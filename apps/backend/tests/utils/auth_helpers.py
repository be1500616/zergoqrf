"""Authentication test helpers.

Provides utility functions for testing authentication flows,
token management, and user session handling.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import pytest
from httpx import AsyncClient, Response

from tests.config.test_config import TEST_CONFIG
from tests.config.auth_test_data import (
    AUTH_TEST_GENERATOR,
    AUTH_TEST_SCENARIOS,
    UserCredentials,
    AuthTestCase,
    VALID_TEST_TOKEN,
    INVALID_TEST_TOKEN
)
from tests.factories.user_factory import USER_FACTORY, UserData


class AuthTestHelper:
    """Helper class for authentication testing."""

    def __init__(self, client: AsyncClient):
        self.client = client
        self.config = TEST_CONFIG
        self.user_factory = USER_FACTORY
        self.test_generator = AUTH_TEST_GENERATOR
        self.test_scenarios = AUTH_TEST_SCENARIOS

        # Track created entities for cleanup
        self.created_users: List[str] = []
        self.created_sessions: List[str] = []
        self.created_restaurants: List[str] = []

    async def signup_user(self, credentials: UserCredentials) -> Dict[str, Any]:
        """Signup a user and return response."""
        response = await self.client.post("/auth/signup/email", json={
            "email": credentials.email,
            "password": credentials.password,
            "name": credentials.name,
            "role": credentials.role,
            "restaurant_id": credentials.restaurant_id
        })

        if response.status_code in [200, 201] and "user" in response.json():
            user_id = response.json()["user"].get("id")
            if user_id:
                self.created_users.append(user_id)

        return response.json()

    async def signin_user(self, email: str, password: str) -> Dict[str, Any]:
        """Signin a user and return response."""
        response = await self.client.post("/auth/signin/email", json={
            "email": email,
            "password": password
        })

        return response.json()

    async def get_user_profile(self, token: str) -> Dict[str, Any]:
        """Get user profile using token."""
        response = await self.client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        return response.json()

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        response = await self.client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        return response.json()

    async def signout(self, token: str) -> Dict[str, Any]:
        """Sign out user."""
        response = await self.client.post("/auth/signout", headers={
            "Authorization": f"Bearer {token}"
        })
        return response.json()

    async def request_phone_otp(self, phone: str) -> Dict[str, Any]:
        """Request OTP for phone authentication."""
        response = await self.client.post("/auth/signin/phone", json={
            "phone": phone
        })
        return response.json()

    async def verify_phone_otp(self, phone: str, otp: str, name: str = None) -> Dict[str, Any]:
        """Verify OTP for phone authentication."""
        payload = {"phone": phone, "token": otp}
        if name:
            payload["name"] = name

        response = await self.client.post("/auth/verify/phone", json=payload)
        return response.json()

    async def create_anonymous_session(self, restaurant_id: str, table_id: str) -> Dict[str, Any]:
        """Create anonymous session."""
        response = await self.client.post("/auth/anonymous-session", json={
            "restaurant_id": restaurant_id,
            "table_id": table_id
        })

        if response.status_code == 200:
            session_id = response.json().get("session_id")
            if session_id:
                self.created_sessions.append(session_id)

        return response.json()

    def assert_auth_response(self, response: Dict[str, Any], expected_keys: List[str] = None):
        """Assert authentication response has expected structure."""
        default_keys = ["access_token", "refresh_token", "user"]
        if expected_keys:
            default_keys = expected_keys

        for key in default_keys:
            assert key in response, f"Missing key '{key}' in auth response"

        # Assert user structure
        if "user" in response:
            user = response["user"]
            assert "id" in user
            assert "email" in user
            assert "role" in user

    def assert_error_response(self, response: Dict[str, Any], expected_error_type: str = None):
        """Assert error response has expected structure."""
        assert "error" in response or "detail" in response, "Response should contain error information"

        if expected_error_type and "error" in response:
            error = response["error"]
            if isinstance(error, dict) and "type" in error:
                assert error["type"] == expected_error_type

    async def run_auth_test_scenario(self, scenario: AuthTestCase) -> Dict[str, Any]:
        """Run a complete authentication test scenario."""
        if "signup" in scenario.name:
            response = await self.signup_user(scenario.credentials)
        elif "signin" in scenario.name:
            response = await self.signin_user(scenario.credentials.email, scenario.credentials.password)
        else:
            raise ValueError(f"Unknown scenario type: {scenario.name}")

        # Validate response
        if scenario.should_succeed:
            assert response.get("error") is None, f"Expected success but got error: {response}"
            self.assert_auth_response(response)
        else:
            assert response.get("error") is not None or response.get("detail") is not None, \
                f"Expected error but got success: {response}"

        return response

    async def create_authenticated_user(self, role: str = "customer", restaurant_id: str = None) -> Tuple[Dict[str, Any], str]:
        """Create a user and authenticate them, return user data and token."""
        # Create user credentials
        credentials = self.test_generator.generate_user_credentials(
            role=role,
            restaurant_id=restaurant_id
        )

        # Signup user
        signup_response = await self.signup_user(credentials)
        assert signup_response.get("error") is None, f"Signup failed: {signup_response}"

        # Extract token
        token = signup_response.get("access_token")
        assert token is not None, "No access token in signup response"

        # Get user profile
        profile = await self.get_user_profile(token)
        assert profile.get("error") is None, f"Profile fetch failed: {profile}"

        return profile, token

    async def create_test_session(self, user_data: UserData) -> Dict[str, Any]:
        """Create a test session for user."""
        # For now, return mock session data
        # In real implementation, this would call your session creation endpoint
        return {
            "session_id": f"session_{user_data.id}",
            "user_id": user_data.id,
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "is_active": True
        }

    def get_mock_auth_response(self, user_data: UserData, include_token: bool = True) -> Dict[str, Any]:
        """Get mock authentication response for testing."""
        response = {
            "user": self.user_factory.to_api_response(user_data)
        }

        if include_token:
            response.update({
                "access_token": VALID_TEST_TOKEN,
                "refresh_token": f"refresh_{user_data.id}",
                "expires_in": self.config.AUTH_TOKEN_EXPIRY_SECONDS,
                "token_type": "bearer"
            })

        return response

    def get_mock_error_response(self, error_type: str, message: str) -> Dict[str, Any]:
        """Get mock error response for testing."""
        return {
            "error": {
                "type": error_type,
                "message": message
            }
        }

    async def cleanup_created_resources(self):
        """Cleanup all resources created during testing."""
        # Note: In real implementation, you'd call actual cleanup endpoints
        # This is a placeholder for the cleanup logic

        # Clear tracking lists
        self.created_users.clear()
        self.created_sessions.clear()
        self.created_restaurants.clear()

        # Clear factory data
        self.user_factory.cleanup_all_users()


class TokenTestHelper:
    """Helper for token-related testing."""

    def __init__(self):
        self.config = TEST_CONFIG

    def generate_test_token(self, user_data: UserData, expires_in: int = None) -> str:
        """Generate test JWT token."""
        # In real implementation, you'd use actual JWT generation
        # For now, return a mock token
        return f"test_token_{user_data.id}_{expires_in or self.config.AUTH_TOKEN_EXPIRY_SECONDS}"

    def generate_expired_token(self, user_data: UserData) -> str:
        """Generate expired test token."""
        return f"expired_token_{user_data.id}"

    def parse_token_payload(self, token: str) -> Dict[str, Any]:
        """Parse token payload for testing."""
        # In real implementation, you'd decode actual JWT
        # For now, return mock payload
        if "test_token_" in token:
            parts = token.split("_")
            return {
                "sub": parts[2],
                "exp": int(parts[3]) if len(parts) > 3 else None,
                "iat": int(datetime.utcnow().timestamp())
            }
        return {}

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired."""
        payload = self.parse_token_payload(token)
        if "exp" in payload and payload["exp"]:
            return payload["exp"] < datetime.utcnow().timestamp()
        return False


class MockSupabaseHelper:
    """Helper for creating mock Supabase clients."""

    def __init__(self):
        self.config = TEST_CONFIG

    def create_mock_client(self) -> Mock:
        """Create mock Supabase client."""
        mock_client = Mock()
        mock_client.auth = Mock()

        # Setup auth methods
        mock_client.auth.sign_up = AsyncMock()
        mock_client.auth.sign_in_with_password = AsyncMock()
        mock_client.auth.sign_in_with_otp = AsyncMock()
        mock_client.auth.verify_otp = AsyncMock()
        mock_client.auth.get_user = AsyncMock()
        mock_client.auth.refresh_session = AsyncMock()
        mock_client.auth.sign_out = AsyncMock()

        # Setup database methods
        mock_client.table = Mock()
        mock_client.rpc = AsyncMock()

        return mock_client

    def setup_signup_success(self, mock_client: Mock, user_data: UserData):
        """Setup mock client for successful signup."""
        mock_user = Mock()
        mock_user.id = user_data.id
        mock_user.email = user_data.email
        mock_user.user_metadata = {
            "role": user_data.role,
            "restaurant_id": user_data.restaurant_id,
            "name": user_data.name
        }

        mock_session = Mock()
        mock_session.access_token = VALID_TEST_TOKEN
        mock_session.refresh_token = f"refresh_{user_data.id}"
        mock_session.expires_in = self.config.AUTH_TOKEN_EXPIRY_SECONDS

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_client.auth.sign_up.return_value = mock_auth_response

    def setup_signin_success(self, mock_client: Mock, user_data: UserData):
        """Setup mock client for successful signin."""
        mock_user = Mock()
        mock_user.id = user_data.id
        mock_user.email = user_data.email
        mock_user.user_metadata = {
            "role": user_data.role,
            "restaurant_id": user_data.restaurant_id
        }

        mock_session = Mock()
        mock_session.access_token = VALID_TEST_TOKEN
        mock_session.refresh_token = f"refresh_{user_data.id}"
        mock_session.expires_in = self.config.AUTH_TOKEN_EXPIRY_SECONDS

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_client.auth.sign_in_with_password.return_value = mock_auth_response

    def setup_get_user_success(self, mock_client: Mock, user_data: UserData):
        """Setup mock client for successful get_user."""
        mock_user = Mock()
        mock_user.id = user_data.id
        mock_user.email = user_data.email
        mock_user.user_metadata = {
            "role": user_data.role,
            "restaurant_id": user_data.restaurant_id,
            "permissions": user_data.permissions
        }

        mock_user_response = Mock()
        mock_user_response.user = mock_user

        mock_client.auth.get_user.return_value = mock_user_response


# Pytest fixtures for easy use
@pytest.fixture
async def auth_helper(client: AsyncClient) -> AuthTestHelper:
    """Create auth test helper."""
    helper = AuthTestHelper(client)
    yield helper
    await helper.cleanup_created_resources()


@pytest.fixture
def token_helper() -> TokenTestHelper:
    """Create token test helper."""
    return TokenTestHelper()


@pytest.fixture
def mock_supabase_helper() -> MockSupabaseHelper:
    """Create mock Supabase helper."""
    return MockSupabaseHelper()