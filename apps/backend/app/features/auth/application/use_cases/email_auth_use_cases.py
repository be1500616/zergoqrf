"""Email authentication use cases.

This module contains use cases for email-based authentication operations.
Use cases orchestrate the flow of data and coordinate domain objects to
fulfill specific business requirements.
"""

import logging
from typing import Optional

from ...domain.auth_entities import AuthenticationResult
from ...domain.auth_repos import IAuthRepository
from ...domain.auth_vos import Email
from ...domain.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    InvalidEmailFormatError,
    WeakPasswordError,
)
from ..auth_dtos import (
    EmailSignInRequestDTO,
    EmailSignUpRequestDTO,
    AuthResponseDTO,
    AuthenticationResultDTO,
    UserDTO,
    user_entity_to_dto,
)
from ....core.logging_config import log_auth_event

logger = logging.getLogger(__name__)


class EmailSignInUseCase:
    """Use case for email and password sign-in.
    
    This use case handles the business logic for authenticating users
    with email and password credentials.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, request: EmailSignInRequestDTO) -> AuthResponseDTO:
        """Execute email sign-in use case.
        
        Args:
            request: Sign-in request data
            
        Returns:
            Authentication response with tokens and user data
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            AuthenticationError: If authentication fails
        """
        try:
            logger.debug(f"Email sign in attempt for: {request.email}")
            
            # Validate email format
            try:
                email = Email(request.email)
            except ValueError as e:
                log_auth_event(
                    logger,
                    "signin_failed",
                    email=request.email,
                    details="Invalid email format",
                    level="warning",
                )
                raise InvalidEmailFormatError(str(e))
            
            # Validate password strength (basic check)
            if len(request.password) < 8:
                log_auth_event(
                    logger,
                    "signin_failed",
                    email=request.email,
                    details="Password too short",
                    level="warning",
                )
                raise WeakPasswordError("Password must be at least 8 characters long")
            
            # Attempt authentication
            auth_result = await self._auth_repository.sign_in_with_email(
                email, request.password
            )
            
            if not auth_result.is_successful():
                log_auth_event(
                    logger,
                    "signin_failed",
                    email=request.email,
                    details=auth_result.error_message or "Invalid credentials",
                    level="warning",
                )
                raise InvalidCredentialsError(
                    auth_result.error_message or "Invalid email or password"
                )
            
            # Convert domain entities to DTOs
            user_dto = user_entity_to_dto(auth_result.user)
            
            # Log successful authentication
            log_auth_event(
                logger,
                "signin_success",
                user_id=auth_result.user.user_id,
                email=auth_result.user.email.value if auth_result.user.email else None,
                details=f"Role: {auth_result.user.role}",
            )
            
            # Build response
            return AuthResponseDTO(
                access_token=auth_result.session.access_token.value,
                refresh_token=auth_result.session.refresh_token.value if auth_result.session.refresh_token else "",
                token_type="bearer",
                expires_in=3600,  # Default to 1 hour
                user=user_dto,
            )
            
        except (InvalidCredentialsError, InvalidEmailFormatError, WeakPasswordError):
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "signin_error",
                email=request.email,
                details=str(e),
                level="error"
            )
            logger.error(f"Email sign in error: {str(e)}")
            raise AuthenticationError("Authentication failed")


class EmailSignUpUseCase:
    """Use case for email and password sign-up.
    
    This use case handles the business logic for creating new user
    accounts with email and password credentials.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, request: EmailSignUpRequestDTO) -> AuthResponseDTO:
        """Execute email sign-up use case.
        
        Args:
            request: Sign-up request data
            
        Returns:
            Authentication response with tokens and user data
            
        Raises:
            UserAlreadyExistsError: If user already exists
            InvalidEmailFormatError: If email format is invalid
            WeakPasswordError: If password is too weak
            AuthenticationError: If account creation fails
        """
        try:
            logger.debug(f"Email sign up attempt for: {request.email}")
            
            # Validate email format
            try:
                email = Email(request.email)
            except ValueError as e:
                log_auth_event(
                    logger,
                    "signup_failed",
                    email=request.email,
                    details="Invalid email format",
                    level="warning",
                )
                raise InvalidEmailFormatError(str(e))
            
            # Validate password strength
            if len(request.password) < 8:
                log_auth_event(
                    logger,
                    "signup_failed",
                    email=request.email,
                    details="Password too weak",
                    level="warning",
                )
                raise WeakPasswordError("Password must be at least 8 characters long")
            
            # Check if user already exists
            existing_user = await self._auth_repository.get_user_by_email(email)
            if existing_user:
                log_auth_event(
                    logger,
                    "signup_failed",
                    email=request.email,
                    details="User already exists",
                    level="warning",
                )
                raise UserAlreadyExistsError("User with this email already exists")
            
            # Attempt account creation
            auth_result = await self._auth_repository.sign_up_with_email(
                email=email,
                password=request.password,
                name=request.name,
                role=request.role,
                restaurant_id=request.restaurant_id,
            )
            
            if not auth_result.is_successful():
                log_auth_event(
                    logger,
                    "signup_failed",
                    email=request.email,
                    details=auth_result.error_message or "Account creation failed",
                    level="error",
                )
                raise AuthenticationError(
                    auth_result.error_message or "Failed to create user account"
                )
            
            # Convert domain entities to DTOs
            user_dto = user_entity_to_dto(auth_result.user)
            
            # Log successful account creation
            log_auth_event(
                logger,
                "signup_success",
                user_id=auth_result.user.user_id,
                email=auth_result.user.email.value if auth_result.user.email else None,
                details=f"Role: {auth_result.user.role}",
            )
            
            # Handle case where email confirmation is required (no session)
            if not auth_result.session:
                return AuthResponseDTO(
                    access_token="",
                    refresh_token="",
                    token_type="bearer",
                    expires_in=0,
                    user=UserDTO(
                        id=auth_result.user.user_id,
                        email=auth_result.user.email.value if auth_result.user.email else None,
                        name=request.name,
                        role=request.role,
                        restaurant_id=request.restaurant_id,
                        permissions={},
                        is_active=False,  # Pending email confirmation
                    ),
                )
            
            # Build response with session
            return AuthResponseDTO(
                access_token=auth_result.session.access_token.value,
                refresh_token=auth_result.session.refresh_token.value if auth_result.session.refresh_token else "",
                token_type="bearer",
                expires_in=3600,  # Default to 1 hour
                user=user_dto,
            )
            
        except (UserAlreadyExistsError, InvalidEmailFormatError, WeakPasswordError):
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "signup_error",
                email=request.email,
                details=str(e),
                level="error"
            )
            logger.error(f"Email sign up error: {str(e)}")
            raise AuthenticationError("Account creation failed")


class EmailVerificationUseCase:
    """Use case for email verification.
    
    This use case handles email verification for newly registered users.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, verification_token: str) -> bool:
        """Execute email verification use case.
        
        Args:
            verification_token: Email verification token
            
        Returns:
            True if verification was successful
            
        Raises:
            AuthenticationError: If verification fails
        """
        try:
            # This would typically involve validating the token
            # and activating the user account
            # Implementation depends on Supabase's email verification flow
            
            logger.info(f"Email verification attempted with token: {verification_token[:10]}...")
            
            # For now, return True as Supabase handles this automatically
            return True
            
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            raise AuthenticationError("Email verification failed")
