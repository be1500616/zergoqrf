"""Token management and user profile use cases.

This module contains use cases for token refresh, user profile management,
and session operations.
"""

import logging
from typing import Optional

from ...domain.auth_entities import AuthenticationResult
from ...domain.auth_repos import IAuthRepository, ITokenRepository, IUserRepository
from ...domain.auth_vos import Token
from ...domain.auth_exceptions import (
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
    UserNotFoundError,
)
from ..auth_dtos import (
    TokenRefreshRequestDTO,
    AuthResponseDTO,
    UserProfileResponseDTO,
    UserContextDTO,
    SignOutResponseDTO,
    user_entity_to_dto,
)
from ....core.logging_config import log_auth_event

logger = logging.getLogger(__name__)


class TokenRefreshUseCase:
    """Use case for refreshing authentication tokens.
    
    This use case handles the business logic for refreshing expired
    access tokens using valid refresh tokens.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, request: TokenRefreshRequestDTO) -> AuthResponseDTO:
        """Execute token refresh use case.
        
        Args:
            request: Token refresh request data
            
        Returns:
            Authentication response with new tokens
            
        Raises:
            InvalidTokenError: If refresh token is invalid
            TokenExpiredError: If refresh token has expired
            AuthenticationError: If token refresh fails
        """
        try:
            logger.debug("Token refresh attempt")
            
            # Validate refresh token format
            if not request.refresh_token or not request.refresh_token.strip():
                log_auth_event(
                    logger,
                    "token_refresh_failed",
                    details="Empty refresh token",
                    level="warning",
                )
                raise InvalidTokenError("Refresh token is required")
            
            # Create token value object
            try:
                refresh_token = Token(request.refresh_token, token_type="refresh")
            except ValueError as e:
                log_auth_event(
                    logger,
                    "token_refresh_failed",
                    details="Invalid refresh token format",
                    level="warning",
                )
                raise InvalidTokenError(f"Invalid refresh token format: {str(e)}")
            
            # Attempt token refresh
            auth_result = await self._auth_repository.refresh_session(refresh_token)
            
            if not auth_result.is_successful():
                error_msg = auth_result.error_message or "Invalid refresh token"
                log_auth_event(
                    logger,
                    "token_refresh_failed",
                    details=error_msg,
                    level="warning",
                )
                
                # Determine specific error type
                if "expired" in error_msg.lower():
                    raise TokenExpiredError(error_msg)
                else:
                    raise InvalidTokenError(error_msg)
            
            # Convert domain entities to DTOs
            user_dto = user_entity_to_dto(auth_result.user)
            
            # Log successful token refresh
            log_auth_event(
                logger,
                "token_refresh_success",
                user_id=auth_result.user.user_id,
                details="Token refreshed successfully",
            )
            
            # Build response
            return AuthResponseDTO(
                access_token=auth_result.session.access_token.value,
                refresh_token=auth_result.session.refresh_token.value if auth_result.session.refresh_token else "",
                token_type="bearer",
                expires_in=3600,  # Default to 1 hour
                user=user_dto,
            )
            
        except (InvalidTokenError, TokenExpiredError):
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "token_refresh_error",
                details=str(e),
                level="error"
            )
            logger.error(f"Token refresh error: {str(e)}")
            raise AuthenticationError("Token refresh failed")


class UserProfileUseCase:
    """Use case for retrieving user profile information.
    
    This use case handles the business logic for getting current
    user profile data from the authentication context.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, user_context: UserContextDTO) -> UserProfileResponseDTO:
        """Execute user profile retrieval use case.
        
        Args:
            user_context: Current user context from authentication
            
        Returns:
            User profile response data
            
        Raises:
            UserNotFoundError: If user is not found
            AuthenticationError: If profile retrieval fails
        """
        try:
            logger.debug(f"Retrieving profile for user: {user_context.user_id}")
            
            # Get full user data from repository
            user = await self._auth_repository.get_user_by_id(user_context.user_id)
            
            if not user:
                log_auth_event(
                    logger,
                    "profile_retrieval_failed",
                    user_id=user_context.user_id,
                    details="User not found",
                    level="warning",
                )
                raise UserNotFoundError(f"User not found: {user_context.user_id}")
            
            # Log successful profile retrieval
            log_auth_event(
                logger,
                "profile_retrieved",
                user_id=user.user_id,
                details="Profile retrieved successfully",
            )
            
            # Build response from user context (which already has the needed data)
            return UserProfileResponseDTO(
                id=user_context.user_id,
                email=user_context.email,
                phone=user_context.phone,
                name=user.name,  # Get actual name from user entity
                role=user_context.role,
                restaurant_id=user_context.restaurant_id,
                permissions=user_context.permissions,
                is_active=user.is_active,
            )
            
        except UserNotFoundError:
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "profile_retrieval_error",
                user_id=user_context.user_id,
                details=str(e),
                level="error"
            )
            logger.error(f"Profile retrieval error: {str(e)}")
            raise AuthenticationError("Failed to retrieve user profile")


class SignOutUseCase:
    """Use case for user sign-out.
    
    This use case handles the business logic for signing out users
    and invalidating their sessions.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, user_context: Optional[UserContextDTO] = None) -> SignOutResponseDTO:
        """Execute user sign-out use case.
        
        Args:
            user_context: Current user context (optional for anonymous users)
            
        Returns:
            Sign-out response
        """
        try:
            if user_context and not user_context.is_anonymous:
                logger.debug(f"Signing out user: {user_context.user_id}")
                
                # Sign out from authentication system
                success = await self._auth_repository.sign_out(user_context.user_id)
                
                if success:
                    log_auth_event(
                        logger,
                        "signout_success",
                        user_id=user_context.user_id,
                        details="User signed out successfully",
                    )
                else:
                    log_auth_event(
                        logger,
                        "signout_warning",
                        user_id=user_context.user_id,
                        details="Sign out completed with warnings",
                        level="warning",
                    )
            else:
                logger.debug("Anonymous user sign-out or no user context")
            
            # Always return success for sign-out operations
            return SignOutResponseDTO(message="Signed out successfully")
            
        except Exception as e:
            # Log error but don't fail sign-out
            log_auth_event(
                logger,
                "signout_error",
                user_id=user_context.user_id if user_context else None,
                details=str(e),
                level="error"
            )
            logger.error(f"Sign out error: {str(e)}")
            
            # Still return success - sign out should always succeed from user perspective
            return SignOutResponseDTO(message="Signed out successfully")


class ValidateTokenUseCase:
    """Use case for validating authentication tokens.
    
    This use case handles validation of JWT tokens and extraction
    of user context information.
    """
    
    def __init__(self, token_repository: ITokenRepository):
        """Initialize the use case.
        
        Args:
            token_repository: Repository for token operations
        """
        self._token_repository = token_repository
    
    async def execute(self, token_value: str) -> Optional[UserContextDTO]:
        """Execute token validation use case.
        
        Args:
            token_value: JWT token to validate
            
        Returns:
            User context if token is valid, None otherwise
            
        Raises:
            InvalidTokenError: If token format is invalid
            TokenExpiredError: If token has expired
            AuthenticationError: If validation fails
        """
        try:
            logger.debug(f"Validating token: {token_value[:10]}...")
            
            # Create token value object
            try:
                token = Token(token_value, token_type="bearer")
            except ValueError as e:
                raise InvalidTokenError(f"Invalid token format: {str(e)}")
            
            # Check if token is blacklisted
            is_blacklisted = await self._token_repository.is_token_blacklisted(token)
            if is_blacklisted:
                log_auth_event(
                    logger,
                    "token_validation_failed",
                    details="Token is blacklisted",
                    level="warning",
                )
                raise InvalidTokenError("Token has been revoked")
            
            # Validate token and extract claims
            claims = await self._token_repository.validate_token(token)
            
            if not claims:
                log_auth_event(
                    logger,
                    "token_validation_failed",
                    details="Token validation failed",
                    level="warning",
                )
                return None
            
            # Extract user context from token claims
            user_context_data = await self._token_repository.extract_user_context(token)
            
            if not user_context_data:
                log_auth_event(
                    logger,
                    "token_validation_failed",
                    details="Failed to extract user context",
                    level="warning",
                )
                return None
            
            # Build user context DTO
            user_context = UserContextDTO(
                user_id=user_context_data.get("user_id", ""),
                email=user_context_data.get("email"),
                phone=user_context_data.get("phone"),
                role=user_context_data.get("role", "customer"),
                restaurant_id=user_context_data.get("restaurant_id"),
                permissions=user_context_data.get("permissions", {}),
                is_anonymous=user_context_data.get("is_anonymous", False),
            )
            
            # Log successful validation
            log_auth_event(
                logger,
                "token_validated",
                user_id=user_context.user_id,
                details="Token validated successfully",
            )
            
            return user_context
            
        except (InvalidTokenError, TokenExpiredError):
            raise
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise AuthenticationError("Token validation failed")


class BlacklistTokenUseCase:
    """Use case for blacklisting tokens.
    
    This use case handles adding tokens to a blacklist to prevent
    their further use after sign-out or security incidents.
    """
    
    def __init__(self, token_repository: ITokenRepository):
        """Initialize the use case.
        
        Args:
            token_repository: Repository for token operations
        """
        self._token_repository = token_repository
    
    async def execute(self, token_value: str) -> bool:
        """Execute token blacklisting use case.
        
        Args:
            token_value: Token to blacklist
            
        Returns:
            True if blacklisting was successful
            
        Raises:
            InvalidTokenError: If token format is invalid
            AuthenticationError: If blacklisting fails
        """
        try:
            logger.debug(f"Blacklisting token: {token_value[:10]}...")
            
            # Create token value object
            try:
                token = Token(token_value, token_type="bearer")
            except ValueError as e:
                raise InvalidTokenError(f"Invalid token format: {str(e)}")
            
            # Add token to blacklist
            success = await self._token_repository.blacklist_token(token)
            
            if success:
                log_auth_event(
                    logger,
                    "token_blacklisted",
                    details="Token added to blacklist",
                )
            else:
                log_auth_event(
                    logger,
                    "token_blacklist_failed",
                    details="Failed to blacklist token",
                    level="warning",
                )
            
            return success
            
        except InvalidTokenError:
            raise
        except Exception as e:
            logger.error(f"Token blacklisting error: {str(e)}")
            raise AuthenticationError("Failed to blacklist token")
