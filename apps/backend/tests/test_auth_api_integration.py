"""API integration tests for authentication endpoints.

This module tests the complete authentication flow through the API endpoints
using Clean Architecture implementation.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.main import app
from app.features.auth.domain.auth_entities import User, AuthSession
from app.features.auth.domain.auth_vos import Email, Password


@pytest.fixture
async def client():
    """Create test client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    return AsyncMock()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User",
        "role": "customer",
    }


@pytest.fixture
def sample_signin_data():
    """Sample signin data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
    }


@pytest.fixture
def sample_anonymous_session_data():
    """Sample anonymous session data for testing."""
    return {
        "restaurant_id": str(uuid4()),
        "table_id": str(uuid4()),
    }


class TestSignUpEndpoint:
    """Test cases for signup endpoint."""
    
    @pytest.mark.asyncio
    async def test_successful_signup(self, client, sample_user_data):
        """Test successful user signup through API."""
        with patch('app.features.auth.application.dependencies.get_supabase') as mock_get_supabase:
            # Mock the use case dependencies
            with patch('app.features.auth.application.use_cases.signup_use_case.SignUpUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                # Mock successful response
                from app.features.auth.application.auth_dtos import AuthTokenResponseDTO, UserDTO
                mock_response = AuthTokenResponseDTO(
                    access_token="test_access_token",
                    refresh_token="test_refresh_token",
                    token_type="bearer",
                    expires_in=3600,
                    user=UserDTO(
                        id=str(uuid4()),
                        email="test@example.com",
                        name="Test User",
                        role="customer",
                        is_active=True,
                    )
                )
                mock_use_case.execute.return_value = mock_response
                
                # Make API request
                response = await client.post("/auth/signup", json=sample_user_data)
                
                # Assert response
                assert response.status_code == 200
                data = response.json()
                assert data["access_token"] == "test_access_token"
                assert data["refresh_token"] == "test_refresh_token"
                assert data["token_type"] == "bearer"
                assert data["user"]["email"] == "test@example.com"
                assert data["user"]["name"] == "Test User"
                assert data["user"]["role"] == "customer"
    
    @pytest.mark.asyncio
    async def test_signup_invalid_email(self, client):
        """Test signup with invalid email format."""
        invalid_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "name": "Test User",
            "role": "customer",
        }
        
        with patch('app.features.auth.application.dependencies.get_supabase'):
            with patch('app.features.auth.application.use_cases.signup_use_case.SignUpUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                from app.features.auth.domain.auth_exceptions import InvalidCredentialsError
                mock_use_case.execute.side_effect = InvalidCredentialsError("Invalid email format")
                
                response = await client.post("/auth/signup", json=invalid_data)
                
                assert response.status_code == 401
                data = response.json()
                assert "error" in data
                assert data["error"] == "InvalidCredentialsError"
    
    @pytest.mark.asyncio
    async def test_signup_user_already_exists(self, client, sample_user_data):
        """Test signup when user already exists."""
        with patch('app.features.auth.application.dependencies.get_supabase'):
            with patch('app.features.auth.application.use_cases.signup_use_case.SignUpUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                from app.features.auth.domain.auth_exceptions import UserAlreadyExistsError
                mock_use_case.execute.side_effect = UserAlreadyExistsError("User already exists")
                
                response = await client.post("/auth/signup", json=sample_user_data)
                
                assert response.status_code == 409
                data = response.json()
                assert "error" in data
                assert data["error"] == "UserAlreadyExistsError"


class TestSignInEndpoint:
    """Test cases for signin endpoint."""
    
    @pytest.mark.asyncio
    async def test_successful_signin(self, client, sample_signin_data):
        """Test successful user signin through API."""
        with patch('app.features.auth.application.dependencies.get_supabase'):
            with patch('app.features.auth.application.use_cases.signin_use_case.SignInUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                # Mock successful response
                from app.features.auth.application.auth_dtos import AuthTokenResponseDTO, UserDTO
                mock_response = AuthTokenResponseDTO(
                    access_token="test_access_token",
                    refresh_token="test_refresh_token",
                    token_type="bearer",
                    expires_in=3600,
                    user=UserDTO(
                        id=str(uuid4()),
                        email="test@example.com",
                        name="Test User",
                        role="customer",
                        is_active=True,
                    )
                )
                mock_use_case.execute.return_value = mock_response
                
                # Make API request
                response = await client.post("/auth/signin", json=sample_signin_data)
                
                # Assert response
                assert response.status_code == 200
                data = response.json()
                assert data["access_token"] == "test_access_token"
                assert data["refresh_token"] == "test_refresh_token"
                assert data["user"]["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_signin_invalid_credentials(self, client, sample_signin_data):
        """Test signin with invalid credentials."""
        with patch('app.features.auth.application.dependencies.get_supabase'):
            with patch('app.features.auth.application.use_cases.signin_use_case.SignInUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                from app.features.auth.domain.auth_exceptions import InvalidCredentialsError
                mock_use_case.execute.side_effect = InvalidCredentialsError("Invalid password")
                
                response = await client.post("/auth/signin", json=sample_signin_data)
                
                assert response.status_code == 401
                data = response.json()
                assert "error" in data
                assert data["error"] == "InvalidCredentialsError"
    
    @pytest.mark.asyncio
    async def test_signin_user_not_found(self, client, sample_signin_data):
        """Test signin when user doesn't exist."""
        with patch('app.features.auth.application.dependencies.get_supabase'):
            with patch('app.features.auth.application.use_cases.signin_use_case.SignInUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                from app.features.auth.domain.auth_exceptions import UserNotFoundError
                mock_use_case.execute.side_effect = UserNotFoundError("User not found")
                
                response = await client.post("/auth/signin", json=sample_signin_data)
                
                assert response.status_code == 404
                data = response.json()
                assert "error" in data
                assert data["error"] == "UserNotFoundError"


class TestAnonymousSessionEndpoint:
    """Test cases for anonymous session endpoint."""
    
    @pytest.mark.asyncio
    async def test_successful_anonymous_session_creation(self, client, sample_anonymous_session_data):
        """Test successful anonymous session creation through API."""
        with patch('app.features.auth.application.dependencies.get_supabase'):
            with patch('app.features.auth.application.use_cases.anonymous_session_use_case.AnonymousSessionUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                # Mock successful response
                from app.features.auth.application.auth_dtos import AnonymousSessionResponseDTO
                from datetime import datetime, timedelta
                
                mock_response = AnonymousSessionResponseDTO(
                    session_id=str(uuid4()),
                    session_token="test_session_token",
                    expires_at=datetime.utcnow() + timedelta(hours=2),
                    restaurant_id=sample_anonymous_session_data["restaurant_id"],
                    table_id=sample_anonymous_session_data["table_id"],
                )
                mock_use_case.execute.return_value = mock_response
                
                # Make API request
                response = await client.post("/auth/anonymous-session", json=sample_anonymous_session_data)
                
                # Assert response
                assert response.status_code == 200
                data = response.json()
                assert data["session_token"] == "test_session_token"
                assert data["restaurant_id"] == sample_anonymous_session_data["restaurant_id"]
                assert data["table_id"] == sample_anonymous_session_data["table_id"]
    
    @pytest.mark.asyncio
    async def test_anonymous_session_invalid_restaurant_id(self, client):
        """Test anonymous session creation with invalid restaurant ID."""
        invalid_data = {
            "restaurant_id": "invalid-uuid",
            "table_id": str(uuid4()),
        }
        
        with patch('app.features.auth.application.dependencies.get_supabase'):
            with patch('app.features.auth.application.use_cases.anonymous_session_use_case.AnonymousSessionUseCase') as mock_use_case_class:
                mock_use_case = AsyncMock()
                mock_use_case_class.return_value = mock_use_case
                
                from app.features.auth.domain.auth_exceptions import InvalidTokenError
                mock_use_case.execute.side_effect = InvalidTokenError("Invalid restaurant_id format")
                
                response = await client.post("/auth/anonymous-session", json=invalid_data)
                
                assert response.status_code == 401
                data = response.json()
                assert "error" in data
                assert data["error"] == "InvalidTokenError"


class TestAuthenticationFlow:
    """Test complete authentication flows."""
    
    @pytest.mark.asyncio
    async def test_complete_signup_signin_flow(self, client):
        """Test complete signup and signin flow."""
        user_data = {
            "email": "flowtest@example.com",
            "password": "SecurePass123!",
            "name": "Flow Test User",
            "role": "customer",
        }
        
        signin_data = {
            "email": "flowtest@example.com",
            "password": "SecurePass123!",
        }
        
        with patch('app.features.auth.application.dependencies.get_supabase'):
            # Mock signup
            with patch('app.features.auth.application.use_cases.signup_use_case.SignUpUseCase') as mock_signup_class:
                mock_signup = AsyncMock()
                mock_signup_class.return_value = mock_signup
                
                from app.features.auth.application.auth_dtos import AuthTokenResponseDTO, UserDTO
                user_id = str(uuid4())
                signup_response = AuthTokenResponseDTO(
                    access_token="signup_access_token",
                    refresh_token="signup_refresh_token",
                    token_type="bearer",
                    expires_in=3600,
                    user=UserDTO(
                        id=user_id,
                        email="flowtest@example.com",
                        name="Flow Test User",
                        role="customer",
                        is_active=True,
                    )
                )
                mock_signup.execute.return_value = signup_response
                
                # Test signup
                signup_resp = await client.post("/auth/signup", json=user_data)
                assert signup_resp.status_code == 200
                signup_data = signup_resp.json()
                assert signup_data["user"]["email"] == "flowtest@example.com"
            
            # Mock signin
            with patch('app.features.auth.application.use_cases.signin_use_case.SignInUseCase') as mock_signin_class:
                mock_signin = AsyncMock()
                mock_signin_class.return_value = mock_signin
                
                signin_response = AuthTokenResponseDTO(
                    access_token="signin_access_token",
                    refresh_token="signin_refresh_token",
                    token_type="bearer",
                    expires_in=3600,
                    user=UserDTO(
                        id=user_id,
                        email="flowtest@example.com",
                        name="Flow Test User",
                        role="customer",
                        is_active=True,
                    )
                )
                mock_signin.execute.return_value = signin_response
                
                # Test signin
                signin_resp = await client.post("/auth/signin", json=signin_data)
                assert signin_resp.status_code == 200
                signin_data = signin_resp.json()
                assert signin_data["user"]["email"] == "flowtest@example.com"
                assert signin_data["access_token"] == "signin_access_token"
