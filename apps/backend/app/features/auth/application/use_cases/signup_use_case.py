"""Sign up use case for user registration.

This module implements the business logic for user registration,
following Clean Architecture principles.
"""

from typing import Optional
from uuid import uuid4

from ...domain.auth_entities import User, AuthSession
from ...domain.auth_repos import IUserRepository, IAuthSessionRepository
from ...domain.auth_vos import Email, Password, PhoneNumber
from ...domain.auth_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
)
from ..auth_dtos import SignUpRequestDTO, AuthTokenResponseDTO, UserDTO


class SignUpUseCase:
    """Use case for user registration.
    
    Handles the business logic for creating new user accounts,
    including validation, password hashing, and session creation.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: IAuthSessionRepository,
    ):
        """Initialize the SignUpUseCase.
        
        Args:
            user_repository: Repository for user data operations
            session_repository: Repository for session data operations
        """
        self._user_repository = user_repository
        self._session_repository = session_repository
    
    async def execute(
        self, request: SignUpRequestDTO
    ) -> AuthTokenResponseDTO:
        """Execute the sign up use case.
        
        Args:
            request: Sign up request containing user data
            
        Returns:
            Authentication token response with user data
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            InvalidCredentialsError: If email or password format is invalid
        """
        # Validate email format
        try:
            email = Email(request.email)
        except ValueError as e:
            raise InvalidCredentialsError(f"Invalid email format: {str(e)}")
        
        # Validate password strength
        try:
            password = Password(request.password)
        except ValueError as e:
            raise InvalidCredentialsError(f"Invalid password: {str(e)}")
        
        # Validate phone number if provided
        phone = None
        if request.phone:
            try:
                phone = PhoneNumber(request.phone)
            except ValueError as e:
                raise InvalidCredentialsError(f"Invalid phone: {str(e)}")
        
        # Check if user already exists
        existing_user = await self._user_repository.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with email {request.email} already exists"
            )
        
        # Create new user entity
        user = User(
            id=uuid4(),
            email=email,
            password=password,
            phone=phone,
            name=request.name,
            role=request.role or "customer",
            restaurant_id=request.restaurant_id,
            is_active=True,
        )
        
        # Save user to repository
        created_user = await self._user_repository.create_user(user)
        
        # Create authentication session
        session = AuthSession(
            id=uuid4(),
            user_id=created_user.id,
            session_type="authenticated",
            restaurant_id=created_user.restaurant_id,
        )
        
        # Save session to repository
        created_session = await self._session_repository.create_session(session)
        
        # Convert to DTOs for response
        user_dto = UserDTO(
            id=str(created_user.id),
            email=created_user.email.value,
            phone=created_user.phone.value if created_user.phone else None,
            name=created_user.name,
            role=created_user.role,
            restaurant_id=(
                str(created_user.restaurant_id) 
                if created_user.restaurant_id else None
            ),
            permissions=created_user.permissions,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )
        
        return AuthTokenResponseDTO(
            access_token=created_session.session_token,
            refresh_token=created_session.session_token,  # Simplified for now
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user=user_dto,
        )
