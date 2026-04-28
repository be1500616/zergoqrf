"""Refresh token use case for token renewal.

This module implements the business logic for refreshing authentication tokens,
following Clean Architecture principles.
"""

from uuid import uuid4

from ...domain.auth_entities import AuthSession
from ...domain.auth_repos import IUserRepository, IAuthSessionRepository
from ...domain.auth_exceptions import (
    InvalidTokenError,
    SessionExpiredError,
    SessionNotFoundError,
    UserNotFoundError,
)
from ..auth_dtos import TokenRefreshRequestDTO, AuthTokenResponseDTO, UserDTO


class RefreshTokenUseCase:
    """Use case for refreshing authentication tokens.
    
    Handles the business logic for validating refresh tokens
    and generating new access tokens.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: IAuthSessionRepository,
    ):
        """Initialize the RefreshTokenUseCase.
        
        Args:
            user_repository: Repository for user data operations
            session_repository: Repository for session data operations
        """
        self._user_repository = user_repository
        self._session_repository = session_repository
    
    async def execute(
        self, request: TokenRefreshRequestDTO
    ) -> AuthTokenResponseDTO:
        """Execute the refresh token use case.
        
        Args:
            request: Token refresh request containing refresh token
            
        Returns:
            New authentication token response
            
        Raises:
            InvalidTokenError: If refresh token is invalid
            SessionExpiredError: If session has expired
            SessionNotFoundError: If session doesn't exist
            UserNotFoundError: If associated user doesn't exist
        """
        # Find session by refresh token
        session = await self._session_repository.get_session_by_token(
            request.refresh_token
        )
        if not session:
            raise SessionNotFoundError("Session not found for refresh token")
        
        # Check if session is active
        if not session.is_active:
            raise InvalidTokenError("Session is no longer active")
        
        # Check if session has expired
        if session.is_expired():
            raise SessionExpiredError("Session has expired")
        
        # Get associated user
        user = await self._user_repository.get_user_by_id(session.user_id)
        if not user:
            raise UserNotFoundError("User associated with session not found")
        
        # Create new session (invalidate old one)
        new_session = AuthSession(
            id=uuid4(),
            user_id=user.id,
            session_type=session.session_type,
            restaurant_id=session.restaurant_id,
            table_id=session.table_id,
        )
        
        # Save new session and deactivate old one
        session.deactivate()
        await self._session_repository.update_session(session)
        created_session = await self._session_repository.create_session(new_session)
        
        # Convert user to DTO for response
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
