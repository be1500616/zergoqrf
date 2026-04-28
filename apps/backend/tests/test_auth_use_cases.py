"""Integration tests for authentication use cases.

This module tests the application layer use cases with mocked repositories.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from app.features.auth.application.auth_dtos import (
    AnonymousSessionRequestDTO,
    SignInRequestDTO,
    SignUpRequestDTO,
    TokenRefreshRequestDTO,
)
from app.features.auth.application.use_cases import (
    AnonymousSessionUseCase,
    GetCurrentUserUseCase,
    RefreshTokenUseCase,
    SignInUseCase,
    SignUpUseCase,
)
from app.features.auth.domain.auth_entities import AuthSession, User
from app.features.auth.domain.auth_exceptions import (
    InvalidCredentialsError,
    InvalidEmailFormatError,
    SessionNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
    WeakPasswordError,
)
from app.features.auth.domain.auth_vos import Email, Password, PhoneNumber


@pytest.fixture
def mock_user_repository():
    """Mock user repository for testing."""
    return AsyncMock()


@pytest.fixture
def mock_session_repository():
    """Mock session repository for testing."""
    return AsyncMock()


@pytest.fixture
def sample_user():
    """Sample user entity for testing."""
    return User(
        id=uuid4(),
        email=Email("test@example.com"),
        name="Test User",
        role="customer",
    )


@pytest.fixture
def sample_session():
    """Sample session entity for testing."""
    return AuthSession(
        id=uuid4(),
        user_id=uuid4(),
        session_type="authenticated",
    )


class TestSignUpUseCase:
    """Test cases for SignUpUseCase."""

    @pytest.mark.asyncio
    async def test_successful_signup(
        self, mock_user_repository, mock_session_repository
    ):
        """Test successful user signup."""
        # Arrange
        mock_user_repository.get_user_by_email.return_value = None  # User doesn't exist
        mock_user_repository.create_user.return_value = User(
            id=uuid4(),
            email=Email("test@example.com"),
            name="Test User",
            role="customer",
        )
        mock_session_repository.create_session.return_value = AuthSession(
            id=uuid4(),
            user_id=uuid4(),
            session_type="authenticated",
        )

        use_case = SignUpUseCase(mock_user_repository, mock_session_repository)
        request = SignUpRequestDTO(
            email="test@example.com",
            password="SecurePass123!",
            name="Test User",
            role="customer",
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.user.email == "test@example.com"
        assert response.user.name == "Test User"
        assert response.user.role == "customer"
        assert response.access_token is not None
        assert response.token_type == "bearer"

        mock_user_repository.get_user_by_email.assert_called_once()
        mock_user_repository.create_user.assert_called_once()
        mock_session_repository.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_signup_user_already_exists(
        self, mock_user_repository, mock_session_repository, sample_user
    ):
        """Test signup when user already exists."""
        # Arrange
        mock_user_repository.get_user_by_email.return_value = sample_user

        use_case = SignUpUseCase(mock_user_repository, mock_session_repository)
        request = SignUpRequestDTO(
            email="test@example.com",
            password="SecurePass123!",
            name="Test User",
            role="customer",
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(request)

        mock_user_repository.get_user_by_email.assert_called_once()
        mock_user_repository.create_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_signup_invalid_email(
        self, mock_user_repository, mock_session_repository
    ):
        """Test signup with invalid email format."""
        # Arrange
        use_case = SignUpUseCase(mock_user_repository, mock_session_repository)
        request = SignUpRequestDTO(
            email="invalid-email",
            password="SecurePass123!",
            name="Test User",
            role="customer",
        )

        # Act & Assert
        with pytest.raises(InvalidEmailFormatError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_signup_weak_password(
        self, mock_user_repository, mock_session_repository
    ):
        """Test signup with weak password."""
        # Arrange
        use_case = SignUpUseCase(mock_user_repository, mock_session_repository)
        request = SignUpRequestDTO(
            email="test@example.com",
            password="weak",
            name="Test User",
            role="customer",
        )

        # Act & Assert
        with pytest.raises(WeakPasswordError):
            await use_case.execute(request)


class TestSignInUseCase:
    """Test cases for SignInUseCase."""

    @pytest.mark.asyncio
    async def test_successful_signin(
        self, mock_user_repository, mock_session_repository, sample_user
    ):
        """Test successful user signin."""
        # Arrange
        mock_user_repository.get_user_by_email.return_value = sample_user
        mock_session_repository.create_session.return_value = AuthSession(
            id=uuid4(),
            user_id=sample_user.id,
            session_type="authenticated",
        )

        use_case = SignInUseCase(mock_user_repository, mock_session_repository)
        request = SignInRequestDTO(
            email="test@example.com",
            password="SecurePass123!",
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.user.email == "test@example.com"
        assert response.access_token is not None
        assert response.token_type == "bearer"

        mock_user_repository.get_user_by_email.assert_called_once()
        mock_session_repository.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_signin_user_not_found(
        self, mock_user_repository, mock_session_repository
    ):
        """Test signin when user doesn't exist."""
        # Arrange
        mock_user_repository.get_user_by_email.return_value = None

        use_case = SignInUseCase(mock_user_repository, mock_session_repository)
        request = SignInRequestDTO(
            email="nonexistent@example.com",
            password="SecurePass123!",
        )

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await use_case.execute(request)

        mock_user_repository.get_user_by_email.assert_called_once()
        mock_session_repository.create_session.assert_not_called()

    @pytest.mark.asyncio
    async def test_signin_invalid_password(
        self, mock_user_repository, mock_session_repository, sample_user
    ):
        """Test signin with invalid password."""
        # Arrange
        mock_user_repository.get_user_by_email.return_value = sample_user

        use_case = SignInUseCase(mock_user_repository, mock_session_repository)
        request = SignInRequestDTO(
            email="test@example.com",
            password="WrongPassword123!",
        )

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(request)

        mock_user_repository.get_user_by_email.assert_called_once()
        mock_session_repository.create_session.assert_not_called()


class TestAnonymousSessionUseCase:
    """Test cases for AnonymousSessionUseCase."""

    @pytest.mark.asyncio
    async def test_successful_anonymous_session_creation(self, mock_session_repository):
        """Test successful anonymous session creation."""
        # Arrange
        restaurant_id = uuid4()
        table_id = uuid4()

        mock_session_repository.create_session.return_value = AuthSession(
            id=uuid4(),
            session_token="anon_token",
            expires_at=datetime.utcnow() + timedelta(hours=2),
            user_id=None,
            restaurant_id=restaurant_id,
            table_id=table_id,
            is_anonymous=True,
        )

        use_case = AnonymousSessionUseCase(mock_session_repository)
        request = AnonymousSessionRequestDTO(
            restaurant_id=str(restaurant_id),
            table_id=str(table_id),
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.restaurant_id == str(restaurant_id)
        assert response.table_id == str(table_id)
        assert response.session_token is not None

        mock_session_repository.create_session.assert_called_once()


class TestRefreshTokenUseCase:
    """Test cases for RefreshTokenUseCase."""

    @pytest.mark.asyncio
    async def test_successful_token_refresh(
        self, mock_user_repository, mock_session_repository, sample_user, sample_session
    ):
        """Test successful token refresh."""
        # Arrange
        mock_session_repository.get_session_by_token.return_value = sample_session
        mock_user_repository.get_user_by_id.return_value = sample_user
        mock_session_repository.create_session.return_value = AuthSession(
            id=uuid4(),
            user_id=sample_user.id,
            session_type="authenticated",
        )
        mock_session_repository.update_session.return_value = sample_session

        use_case = RefreshTokenUseCase(mock_user_repository, mock_session_repository)
        request = TokenRefreshRequestDTO(refresh_token="valid_refresh_token")

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.user.email == "test@example.com"
        assert response.access_token is not None
        assert response.token_type == "bearer"

        mock_session_repository.get_session_by_token.assert_called_once()
        mock_user_repository.get_user_by_id.assert_called_once()
        mock_session_repository.create_session.assert_called_once()
        mock_session_repository.update_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_token_session_not_found(
        self, mock_user_repository, mock_session_repository
    ):
        """Test token refresh when session doesn't exist."""
        # Arrange
        mock_session_repository.get_session_by_token.return_value = None

        use_case = RefreshTokenUseCase(mock_user_repository, mock_session_repository)
        request = TokenRefreshRequestDTO(refresh_token="invalid_refresh_token")

        # Act & Assert
        with pytest.raises(SessionNotFoundError):
            await use_case.execute(request)

        mock_session_repository.get_session_by_token.assert_called_once()
        mock_user_repository.get_user_by_id.assert_not_called()
