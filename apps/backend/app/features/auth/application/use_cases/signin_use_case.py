"""Sign in use case for user authentication.

This module implements the business logic for user authentication,
following Clean Architecture principles.
"""

from uuid import uuid4

from ...domain.auth_entities import User, AuthSession
from ...domain.auth_repos import IUserRepository, IAuthSessionRepository
from ...domain.auth_vos import Email
from ...domain.auth_exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    AccountDeactivatedError,
)
from ..auth_dtos import SignInRequestDTO, AuthTokenResponseDTO, UserDTO


class SignInUseCase:
    """Use case for user authentication.
    
    Handles the business logic for authenticating existing users,
    including credential validation and session creation.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: IAuthSessionRepository,
    ):
        """Initialize the SignInUseCase.
        
        Args:
            user_repository: Repository for user data operations
            session_repository: Repository for session data operations
        """
        self._user_repository = user_repository
        self._session_repository = session_repository
    
    async def execute(
        self, request: SignInRequestDTO
    ) -> AuthTokenResponseDTO:
        """Execute the sign in use case.
        
        Args:
            request: Sign in request containing credentials
            
        Returns:
            Authentication token response with user data
            
        Raises:
            UserNotFoundError: If user with email doesn't exist
            InvalidCredentialsError: If password is incorrect
            AccountDeactivatedError: If user account is deactivated
        """
        # Validate email format
        try:
            email = Email(request.email)
        except ValueError as e:
            raise InvalidCredentialsError(f"Invalid email format: {str(e)}")
        
        # Find user by email
        user = await self._user_repository.get_user_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {request.email} not found")
        
        # Check if account is active
        if not user.is_active:
            raise AccountDeactivatedError(
                "Account has been deactivated. Please contact support."
            )
        
        # Verify password
        if not user.password.verify(request.password):
            raise InvalidCredentialsError("Invalid password")
        
        # Create authentication session
        session = AuthSession(
            id=uuid4(),
            user_id=user.id,
            session_type="authenticated",
            restaurant_id=user.restaurant_id,
        )
        
        # Save session to repository
        created_session = await self._session_repository.create_session(session)
        
        # Convert to DTOs for response
        user_dto = UserDTO(
            id=str(user.id),
            email=user.email.value,
            phone=user.phone.value if user.phone else None,
            name=user.name,
            role=user.role,
            restaurant_id=str(user.restaurant_id) if user.restaurant_id else None,
            permissions=user.permissions,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        
        return AuthTokenResponseDTO(
            access_token=created_session.session_token,
            refresh_token=created_session.session_token,  # Simplified for now
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user=user_dto,
        )
