import httpx
import uuid
from unittest.mock import Mock, patch

import pytest
from app.main import app
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_staff_signup_and_signin(mock_supabase):
    """Test staff member signup and signin flow."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        restaurant_id = str(uuid.uuid4())

        # Test staff signup
        response = await client.post(
            "/auth/signup/email",
            json={
                "email": "manager@restaurant.com",
                "password": "securepassword123",
                "restaurant_id": restaurant_id,
                "role": "manager",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["role"] == "manager"
        assert data["user"]["restaurant_id"] == restaurant_id

        # Test staff signin
        response = await client.post(
            "/auth/signin/email",
            json={
                "email": "manager@restaurant.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


@pytest.mark.asyncio
async def test_customer_signup_and_signin(mock_supabase):
    """Test customer signup and signin flow."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Test customer signup
        response = await client.post(
            "/auth/signup/email",
            json={"email": "customer@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "customer"
        assert data["user"]["restaurant_id"] is None

        # Test customer signin
        response = await client.post(
            "/auth/signin/email",
            json={"email": "customer@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


@pytest.mark.asyncio
async def test_phone_authentication_flow(mock_supabase):
    """Test phone/OTP authentication flow."""
    # Mock OTP sending
    mock_supabase.auth.sign_in_with_otp.return_value = Mock()

    # Mock OTP verification
    mock_supabase.auth.verify_otp.return_value = Mock(
        session=Mock(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
        ),
        user=Mock(id=str(uuid.uuid4()), phone="+1234567890"),
    )

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Test sending OTP
        response = await client.post(
            "/auth/signin/phone",
            json={"phone": "+1234567890"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        assert data["phone"] == "+1234567890"

        # Test OTP verification
        response = await client.post(
            "/auth/verify/phone",
            json={"phone": "+1234567890", "token": "123456", "name": "John Doe"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


@pytest.mark.asyncio
async def test_anonymous_session_creation(mock_supabase):
    """Test anonymous session creation for QR code users."""
    restaurant_id = str(uuid.uuid4())
    table_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # Mock RPC call for creating anonymous session
    mock_supabase.rpc.return_value.execute.return_value.data = [
        {
            "session_id": session_id,
            "session_token": "anonymous_token_123",
            "expires_at": "2024-01-01T12:00:00Z",
        }
    ]

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/anonymous-session",
            json={"restaurant_id": restaurant_id, "table_id": table_id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "session_token" in data
        assert data["restaurant_id"] == restaurant_id
        assert data["table_id"] == table_id


@pytest.mark.asyncio
async def test_token_refresh(mock_supabase):
    """Test token refresh functionality."""
    # Mock refresh session
    mock_supabase.auth.refresh_session.return_value = Mock(
        session=Mock(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            expires_in=3600,
        ),
        user=Mock(id=str(uuid.uuid4()), email="test@example.com", phone=None),
    )

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": "old_refresh_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access_token"
        assert data["refresh_token"] == "new_refresh_token"


@pytest.mark.asyncio
async def test_get_profile_authenticated(mock_supabase):
    """Test getting user profile with valid token."""
    user_id = str(uuid.uuid4())
    restaurant_id = str(uuid.uuid4())

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/auth/profile",
            headers={"Authorization": "Bearer test_access_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "role" in data
        assert "permissions" in data


@pytest.mark.asyncio
async def test_signout(mock_supabase):
    """Test user signout."""
    mock_supabase.auth.sign_out.return_value = None

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/signout",
            headers={"Authorization": "Bearer test_access_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed out successfully"


@pytest.mark.asyncio
async def test_validate_email_availability(mock_supabase):
    """Test email availability validation."""
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/auth/validate/email",
            params={"email": "test@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test accessing protected endpoints without authentication."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # FastAPI returns 401 for missing Authorization header if token is required
        response = await client.get("/auth/profile")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_credentials(mock_supabase):
    """Test signin with invalid credentials."""
    # Mock failed signin - should raise an error or return something that leads to 401
    mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/signin/email",
            json={"email": "wrong@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
