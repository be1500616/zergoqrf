"""
Comprehensive tests for the Supabase authentication router.

This module tests all authentication flows including email/password,
phone OTP, anonymous sessions, and JWT validation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.features.auth.presentation.supabase_auth_router import router
from app.features.auth.presentation.supabase_dependencies import UserContext


@pytest.fixture
def app():
    """Create FastAPI app with auth router for testing."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('app.features.auth.presentation.supabase_auth_router.get_supabase_anon') as mock:
        supabase_mock = Mock()
        mock.return_value = supabase_mock
        yield supabase_mock


@pytest.fixture
def mock_user_context():
    """Mock user context for authenticated requests."""
    return UserContext(
        user_id="test-user-id",
        email="test@example.com",
        role="customer",
        restaurant_id="test-restaurant-id",
        permissions={},
        is_anonymous=False,
    )


class TestEmailAuthentication:
    """Test email/password authentication flows."""

    def test_signin_email_success(self, client, mock_supabase):
        """Test successful email sign in."""
        # Mock successful Supabase response
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.phone = None
        mock_user.user_metadata = {"name": "Test User", "role": "customer"}

        mock_session = Mock()
        mock_session.access_token = "test-access-token"
        mock_session.refresh_token = "test-refresh-token"
        mock_session.expires_in = 3600

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/signin/email",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test-access-token"
        assert data["refresh_token"] == "test-refresh-token"
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600
        assert data["user"]["id"] == "test-user-id"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["role"] == "customer"

    def test_signin_email_invalid_credentials(self, client, mock_supabase):
        """Test email sign in with invalid credentials."""
        # Mock failed Supabase response
        mock_auth_response = Mock()
        mock_auth_response.user = None
        mock_auth_response.session = None

        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/signin/email",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )

        # Assertions
        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["error"]["message"]

    def test_signup_email_success(self, client, mock_supabase):
        """Test successful email sign up."""
        # Mock successful Supabase response
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.phone = None

        mock_session = Mock()
        mock_session.access_token = "test-access-token"
        mock_session.refresh_token = "test-refresh-token"
        mock_session.expires_in = 3600

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase.auth.sign_up.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/signup/email",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User",
                "role": "customer"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test-access-token"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"
        assert data["user"]["role"] == "customer"

    def test_signup_email_confirmation_required(self, client, mock_supabase):
        """Test email sign up requiring confirmation."""
        # Mock Supabase response with no session (confirmation required)
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = None

        mock_supabase.auth.sign_up.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/signup/email",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == ""
        assert data["refresh_token"] == ""
        assert data["expires_in"] == 0
        assert data["user"]["is_active"] == False  # Pending confirmation


class TestPhoneAuthentication:
    """Test phone OTP authentication flows."""

    def test_signin_phone_success(self, client, mock_supabase):
        """Test successful phone OTP initiation."""
        # Mock successful Supabase response
        mock_auth_response = Mock()
        mock_supabase.auth.sign_in_with_otp.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/signin/phone",
            json={"phone": "+1234567890"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        assert data["phone"] == "+1234567890"
        assert data["otp_sent"] == True

    def test_verify_phone_otp_success(self, client, mock_supabase):
        """Test successful phone OTP verification."""
        # Mock successful Supabase response
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = None
        mock_user.phone = "+1234567890"
        mock_user.user_metadata = {"name": "Test User"}

        mock_session = Mock()
        mock_session.access_token = "test-access-token"
        mock_session.refresh_token = "test-refresh-token"
        mock_session.expires_in = 3600

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase.auth.verify_otp.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/verify/phone",
            json={
                "phone": "+1234567890",
                "token": "123456",
                "name": "Test User"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test-access-token"
        assert data["user"]["phone"] == "+1234567890"
        assert data["user"]["name"] == "Test User"

    def test_verify_phone_otp_invalid(self, client, mock_supabase):
        """Test phone OTP verification with invalid token."""
        # Mock failed Supabase response
        mock_auth_response = Mock()
        mock_auth_response.user = None
        mock_auth_response.session = None

        mock_supabase.auth.verify_otp.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/verify/phone",
            json={
                "phone": "+1234567890",
                "token": "000000"
            }
        )

        # Assertions
        assert response.status_code == 401
        data = response.json()
        assert "Invalid or expired OTP" in data["error"]["message"]


class TestAnonymousSession:
    """Test anonymous session management."""

    @patch('app.features.auth.presentation.supabase_auth_router.get_supabase')
    def test_create_anonymous_session_success(self, mock_get_supabase, client):
        """Test successful anonymous session creation."""
        # Mock Supabase RPC response
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase

        mock_result = Mock()
        mock_result.data = [{
            "session_id": "test-session-id",
            "session_token": "test-session-token",
            "expires_at": "2024-01-01T12:00:00Z"
        }]

        mock_supabase.rpc.return_value.execute.return_value = mock_result

        # Make request
        response = client.post(
            "/auth/anonymous-session",
            json={
                "restaurant_id": "test-restaurant-id",
                "table_id": "test-table-id"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-id"
        assert data["session_token"] == "test-session-token"
        assert data["restaurant_id"] == "test-restaurant-id"
        assert data["table_id"] == "test-table-id"


class TestUserProfile:
    """Test user profile endpoints."""

    @patch('app.features.auth.presentation.supabase_auth_router.get_current_user')
    def test_get_current_user_profile(self, mock_get_current_user, client, mock_user_context):
        """Test getting current user profile."""
        # Mock authenticated user
        mock_get_current_user.return_value = mock_user_context

        # Make request
        response = client.get("/auth/me")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-id"
        assert data["email"] == "test@example.com"
        assert data["role"] == "customer"
        assert data["restaurant_id"] == "test-restaurant-id"


class TestTokenManagement:
    """Test token refresh and sign out."""

    def test_refresh_token_success(self, client, mock_supabase):
        """Test successful token refresh."""
        # Mock successful Supabase response
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"role": "customer"}

        mock_session = Mock()
        mock_session.access_token = "new-access-token"
        mock_session.refresh_token = "new-refresh-token"
        mock_session.expires_in = 3600

        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase.auth.refresh_session.return_value = mock_auth_response

        # Make request
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "old-refresh-token"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new-access-token"
        assert data["refresh_token"] == "new-refresh-token"

    def test_signout_success(self, client, mock_supabase):
        """Test successful sign out."""
        # Make request
        response = client.post("/auth/signout")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed out successfully"


class TestValidation:
    """Test input validation."""

    def test_invalid_email_format(self, client):
        """Test sign in with invalid email format."""
        response = client.post(
            "/auth/signin/email",
            json={
                "email": "invalid-email",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 422

    def test_invalid_phone_format(self, client):
        """Test phone sign in with invalid phone format."""
        response = client.post(
            "/auth/signin/phone",
            json={"phone": "invalid-phone"}
        )

        assert response.status_code == 422

    def test_short_password(self, client):
        """Test sign up with password too short."""
        response = client.post(
            "/auth/signup/email",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )

        assert response.status_code == 422
