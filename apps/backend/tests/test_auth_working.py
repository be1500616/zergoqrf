import uuid
from unittest.mock import Mock, patch

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    mock_client = Mock()
    mock_auth = Mock()
    mock_client.auth = mock_auth

    # Mock successful signup
    mock_auth.sign_up.return_value = Mock(
        session=Mock(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
        ),
        user=Mock(id=uuid.uuid4(), email="test@example.com"),
    )

    # Mock successful signin
    mock_auth.sign_in_with_password.return_value = Mock(
        session=Mock(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
        ),
        user=Mock(id=uuid.uuid4(), email="test@example.com"),
    )

    # Mock get_user for token validation
    mock_auth.get_user.return_value = Mock(
        user=Mock(
            id=str(uuid.uuid4()),
            email="test@example.com",
            user_metadata={"role": "customer"},
        )
    )

    # Mock table operations
    mock_table = Mock()
    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = Mock(data=[])

    return mock_client


@pytest.mark.asyncio
async def test_staff_signup_and_signin(mock_supabase):
    """Test staff member signup and signin flow."""
    with patch(
        "app.common.supabase_client.get_supabase",
        return_value=mock_supabase,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            restaurant_id = str(uuid.uuid4())

            # Test staff signup
            response = await client.post(
                "/auth/signup",
                json={
                    "email": "manager@restaurant.com",
                    "password": "securepassword123",
                    "restaurant_id": restaurant_id,
                    "role": "manager",
                },
            )
            if response.status_code != 200:
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["user"]["role"] == "manager"
            assert data["user"]["restaurant_id"] == restaurant_id

            # Test staff signin
            response = await client.post(
                "/auth/signin",
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
    with patch(
        "app.common.supabase_client.get_supabase",
        return_value=mock_supabase,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test customer signup
            response = await client.post(
                "/auth/signup",
                json={"email": "customer@example.com", "password": "password123"},
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["role"] == "customer"
            assert data["user"]["restaurant_id"] is None

            # Test customer signin
            response = await client.post(
                "/auth/signin",
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

    with patch(
        "app.common.supabase_client.get_supabase",
        return_value=mock_supabase,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test sending OTP
            response = await client.post(
                "/auth/phone/signin",
                json={"phone": "+1234567890"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "OTP sent successfully"
            assert data["phone"] == "+1234567890"

            # Test OTP verification
            response = await client.post(
                "/auth/phone/verify",
                json={"phone": "+1234567890", "otp": "123456", "name": "John Doe"},
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["role"] == "customer"


@pytest.mark.asyncio
async def test_anonymous_session_creation(mock_supabase):
    """Test anonymous session creation for QR code users."""
    restaurant_id = str(uuid.uuid4())
    table_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # Mock RPC call for creating anonymous session
    mock_supabase.rpc.return_value = Mock(
        execute=Mock(
            return_value=Mock(
                data=[
                    {
                        "session_id": session_id,
                        "session_token": "anonymous_token_123",
                        "expires_at": "2024-01-01T12:00:00Z",
                    }
                ]
            )
        )
    )

    with patch(
        "app.common.supabase_client.get_supabase",
        return_value=mock_supabase,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/anonymous",
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
        )
    )

    with patch(
        "app.common.supabase_client.get_supabase",
        return_value=mock_supabase,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/refresh",
                json={"refresh_token": "old_refresh_token"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "new_access_token"
            assert data["refresh_token"] == "new_refresh_token"


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test accessing protected endpoints without authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/auth/profile")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_credentials(mock_supabase):
    """Test signin with invalid credentials."""
    # Mock failed signin
    mock_supabase.auth.sign_in_with_password.return_value = Mock(session=None)

    with patch(
        "app.common.supabase_client.get_supabase",
        return_value=mock_supabase,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/signin",
                json={"email": "wrong@example.com", "password": "wrongpassword"},
            )
            assert response.status_code == 400
