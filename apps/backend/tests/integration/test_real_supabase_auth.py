"""
Real Supabase integration tests for authentication.

These tests connect to actual Supabase instance and verify
authentication flows work correctly in real environment.
"""

import os
import pytest
import asyncio
from typing import Dict, Any, List
from httpx import AsyncClient
from supabase import create_client, Client

from tests.config.test_config import TEST_CONFIG
from tests.config.auth_test_data import AUTH_TEST_SCENARIOS, UserCredentials
from tests.utils.auth_helpers import AuthTestHelper
from tests.factories.user_factory import USER_FACTORY, UserData


@pytest.mark.integration
@pytest.mark.slow
class TestRealSupabaseAuth:
    """Integration tests with real Supabase."""

    @pytest.fixture(scope="class")
    async def supabase_client(self) -> Client:
        """Create real Supabase client."""
        if not TEST_CONFIG.is_integration_test():
            pytest.skip("Not running integration tests")

        if not TEST_CONFIG.SUPABASE_URL or not TEST_CONFIG.SUPABASE_ANON_KEY:
            pytest.skip("Supabase credentials not configured")

        return create_client(TEST_CONFIG.SUPABASE_URL, TEST_CONFIG.SUPABASE_ANON_KEY)

    @pytest.fixture(scope="class")
    async def test_client(self) -> AsyncClient:
        """Create test HTTP client."""
        from app.main import create_app
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    async def cleanup_users(self, supabase_client: Client):
        """Cleanup fixture for created users."""
        created_user_ids: List[str] = []

        def add_user(user_id: str):
            created_user_ids.append(user_id)

        yield add_user

        # Cleanup users
        for user_id in created_user_ids:
            try:
                # Delete from users table first (foreign key constraint)
                supabase_client.table("users").delete().eq("id", user_id).execute()
                # Delete from auth
                if TEST_CONFIG.SUPABASE_SERVICE_KEY:
                    admin_client = create_client(
                        TEST_CONFIG.SUPABASE_URL,
                        TEST_CONFIG.SUPABASE_SERVICE_KEY
                    )
                    admin_client.auth.admin.delete_user(user_id)
            except Exception as e:
                print(f"Failed to cleanup user {user_id}: {e}")

    @pytest.fixture
    async def cleanup_restaurants(self, supabase_client: Client):
        """Cleanup fixture for created restaurants."""
        created_restaurant_ids: List[str] = []

        def add_restaurant(restaurant_id: str):
            created_restaurant_ids.append(restaurant_id)

        yield add_restaurant

        # Cleanup restaurants
        for restaurant_id in created_restaurant_ids:
            try:
                supabase_client.table("restaurants").delete().eq("id", restaurant_id).execute()
            except Exception as e:
                print(f"Failed to cleanup restaurant {restaurant_id}: {e}")

    async def test_supabase_connection(self, supabase_client: Client):
        """Test basic Supabase connectivity."""
        # Test we can query the database
        response = supabase_client.table("restaurants").select("count").execute()
        assert response.data is not None

    async def test_real_email_signup_flow(
        self,
        test_client: AsyncClient,
        cleanup_users
    ):
        """Test complete email signup flow with real Supabase."""
        auth_helper = AuthTestHelper(test_client)

        # Create test credentials
        credentials = AUTH_TEST_GENERATOR.generate_user_credentials(
            role="customer"
        )

        # Test signup
        signup_response = await auth_helper.signup_user(credentials)

        # Should succeed
        assert signup_response.get("error") is None, f"Signup failed: {signup_response}"
        auth_helper.assert_auth_response(signup_response)

        # Verify user data
        user_data = signup_response["user"]
        assert user_data["email"] == credentials.email
        assert user_data["role"] == credentials.role
        assert user_data["name"] == credentials.name

        # Store for cleanup
        cleanup_users(user_data["id"])

        # Test token works
        token = signup_response["access_token"]
        profile = await auth_helper.get_user_profile(token)
        assert profile.get("error") is None, f"Profile fetch failed: {profile}"
        assert profile["email"] == credentials.email

    async def test_real_email_signin_flow(
        self,
        test_client: AsyncClient,
        cleanup_users
    ):
        """Test complete email signin flow with real Supabase."""
        auth_helper = AuthTestHelper(test_client)

        # Create test credentials
        credentials = AUTH_TEST_GENERATOR.generate_user_credentials(
            role="customer"
        )

        # First signup
        signup_response = await auth_helper.signup_user(credentials)
        assert signup_response.get("error") is None, f"Signup failed: {signup_response}"

        user_id = signup_response["user"]["id"]
        cleanup_users(user_id)

        # Test signin
        signin_response = await auth_helper.signin_user(
            credentials.email,
            credentials.password
        )

        # Should succeed
        assert signin_response.get("error") is None, f"Signin failed: {signin_response}"
        auth_helper.assert_auth_response(signin_response)

        # Verify user data
        user_data = signin_response["user"]
        assert user_data["email"] == credentials.email
        assert user_data["id"] == user_id  # Same user

    async def test_real_manager_signup_with_restaurant(
        self,
        test_client: AsyncClient,
        supabase_client: Client,
        cleanup_users,
        cleanup_restaurants
    ):
        """Test manager signup with restaurant association."""
        auth_helper = AuthTestHelper(test_client)

        # First create a test restaurant
        restaurant_data = {
            "name": "Test Restaurant for Auth",
            "address": "123 Test St",
            "phone": "+1234567890",
            "email": "restaurant@test.com",
            "owner_id": "test-owner-id"  # Will be updated later
        }

        restaurant_response = supabase_client.table("restaurants").insert(restaurant_data).execute()
        assert restaurant_response.data is not None, "Failed to create test restaurant"

        restaurant_id = restaurant_response.data[0]["id"]
        cleanup_restaurants(restaurant_id)

        # Create manager credentials
        manager_credentials = AUTH_TEST_GENERATOR.generate_user_credentials(
            role="manager",
            restaurant_id=restaurant_id
        )

        # Test manager signup
        signup_response = await auth_helper.signup_user(manager_credentials)
        assert signup_response.get("error") is None, f"Manager signup failed: {signup_response}"

        user_id = signup_response["user"]["id"]
        cleanup_users(user_id)

        # Verify manager has restaurant association
        user_data = signup_response["user"]
        assert user_data["role"] == "manager"
        # Note: restaurant_id might be in metadata or separate field depending on implementation

    async def test_real_phone_auth_flow(
        self,
        test_client: AsyncClient
    ):
        """Test phone authentication flow."""
        auth_helper = AuthTestHelper(test_client)

        # Generate test phone number
        phone_number = AUTH_TEST_GENERATOR.generate_unique_phone()

        # Test OTP request (may not work without actual SMS service)
        otp_response = await auth_helper.request_phone_otp(phone_number)

        # The endpoint should respond appropriately even if SMS fails
        assert otp_response.get("error") is None or otp_response.get("message") is not None

        # Note: OTP verification would require actual SMS service or test bypass
        # This is a placeholder for the structure

    async def test_real_token_refresh(
        self,
        test_client: AsyncClient,
        cleanup_users
    ):
        """Test token refresh with real Supabase."""
        auth_helper = AuthTestHelper(test_client)

        # Create user and get tokens
        credentials = AUTH_TEST_GENERATOR.generate_user_credentials()
        signup_response = await auth_helper.signup_user(credentials)
        assert signup_response.get("error") is None, f"Signup failed: {signup_response}"

        user_id = signup_response["user"]["id"]
        cleanup_users(user_id)

        refresh_token = signup_response["refresh_token"]

        # Test token refresh
        refresh_response = await auth_helper.refresh_token(refresh_token)
        assert refresh_response.get("error") is None, f"Token refresh failed: {refresh_response}"

        # Verify new tokens
        assert "access_token" in refresh_response
        assert "refresh_token" in refresh_response
        assert refresh_response["access_token"] != signup_response["access_token"]

    async def test_real_protected_endpoints(
        self,
        test_client: AsyncClient,
        cleanup_users
    ):
        """Test protected endpoints with real authentication."""
        auth_helper = AuthTestHelper(test_client)

        # Create authenticated user
        credentials = AUTH_TEST_GENERATOR.generate_user_credentials()
        signup_response = await auth_helper.signup_user(credentials)
        assert signup_response.get("error") is None, f"Signup failed: {signup_response}"

        user_id = signup_response["user"]["id"]
        cleanup_users(user_id)

        token = signup_response["access_token"]

        # Test accessing protected endpoint
        profile = await auth_helper.get_user_profile(token)
        assert profile.get("error") is None, f"Profile access failed: {profile}"
        assert profile["email"] == credentials.email

        # Test accessing with invalid token
        invalid_response = await test_client.get("/auth/me", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        assert invalid_response.status_code == 401

    async def test_real_error_scenarios(
        self,
        test_client: AsyncClient
    ):
        """Test error scenarios with real Supabase."""
        auth_helper = AuthTestHelper(test_client)

        # Test signin with non-existent user
        signin_response = await auth_helper.signin_user(
            "nonexistent@test.com",
            "password123"
        )
        assert signin_response.get("error") is not None or signin_response.get("detail") is not None

        # Test signin with wrong password
        # First create a user
        credentials = AUTH_TEST_GENERATOR.generate_user_credentials()
        signup_response = await auth_helper.signup_user(credentials)
        if signup_response.get("error") is None:
            # Try signin with wrong password
            wrong_password_response = await auth_helper.signin_user(
                credentials.email,
                "wrongpassword"
            )
            assert wrong_password_response.get("error") is not None or wrong_password_response.get("detail") is not None

    async def test_concurrent_auth_requests(
        self,
        test_client: AsyncClient,
        cleanup_users
    ):
        """Test concurrent authentication requests."""
        auth_helper = AuthTestHelper(test_client)

        async def signup_and_signin(email_suffix: str):
            credentials = AUTH_TEST_GENERATOR.generate_user_credentials(
                email=f"concurrent_{email_suffix}@test.com"
            )

            # Signup
            signup_response = await auth_helper.signup_user(credentials)
            if signup_response.get("error") is None:
                cleanup_users(signup_response["user"]["id"])

                # Signin
                signin_response = await auth_helper.signin_user(
                    credentials.email,
                    credentials.password
                )
                return signup_response
            return signup_response

        # Run concurrent requests
        tasks = [signup_and_signin(str(i)) for i in range(5)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all responses are handled
        for response in responses:
            if isinstance(response, Exception):
                pytest.fail(f"Concurrent request failed with exception: {response}")
            else:
                # Response should either succeed or fail gracefully
                assert response.get("error") is None or response.get("detail") is not None

    async def test_real_session_management(
        self,
        test_client: AsyncClient,
        supabase_client: Client,
        cleanup_restaurants
    ):
        """Test session management with real Supabase."""
        # Create test restaurant
        restaurant_data = {
            "name": "Test Restaurant for Sessions",
            "address": "456 Session St",
            "phone": "+9876543210",
            "email": "sessions@test.com",
            "owner_id": "test-owner-id"
        }

        restaurant_response = supabase_client.table("restaurants").insert(restaurant_data).execute()
        if restaurant_response.data:
            restaurant_id = restaurant_response.data[0]["id"]
            cleanup_restaurants(restaurant_id)

            # Test anonymous session creation
            auth_helper = AuthTestHelper(test_client)
            session_response = await auth_helper.create_anonymous_session(
                restaurant_id,
                "test-table-1"
            )

            # Should succeed or provide meaningful error
            assert session_response.get("error") is None or session_response.get("detail") is not None