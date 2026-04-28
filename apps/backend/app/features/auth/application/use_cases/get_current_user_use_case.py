"""Get current user use case for retrieving authenticated user information.

This module implements the business logic for retrieving current user data
based on authentication tokens, following Clean Architecture principles.
"""

from ...domain.auth_repos import IUserRepository, IAuthSessionRepository
from ...domain.auth_exceptions import (
    InvalidTokenError,
    SessionExpiredError,
    SessionNotFoundError,
    UserNotFoundError,
)
from ..auth_dtos import UserDTO


class GetCurrentUserUseCase:
    """Use case for retrieving current authenticated user.
    
    Handles the business logic for validating authentication tokens
    and returning current user information.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: IAuthSessionRepository,
    ):
        """Initialize the GetCurrentUserUseCase.
        
        Args:
            user_repository: Repository for user data operations
            session_repository: Repository for session data operations
        """
        self._user_repository = user_repository
        self._session_repository = session_repository
    
    async def execute(self, access_token: str) -> UserDTO:
        """Execute the get current user use case.
        
        Args:
            access_token: Access token from authentication header
            
        Returns:
            Current user data transfer object
            
        Raises:
            InvalidTokenError: If access token is invalid
            SessionExpiredError: If session has expired
            SessionNotFoundError: If session doesn't exist
            UserNotFoundError: If associated user doesn't exist
        """
        # Find session by access token
        session = await self._session_repository.get_session_by_token(access_token)
        if not session:
            raise SessionNotFoundError("Session not found for access token")
        
        # Check if session is active
        if not session.is_active:
            raise InvalidTokenError("Session is no longer active")
        
        # Check if session has expired
        if session.is_expired():
            raise SessionExpiredError("Session has expired")
        
        # For anonymous sessions, return limited information
        if session.session_type == "anonymous":
            return UserDTO(
                id="anonymous",
                email="",
                role="customer",
                restaurant_id=str(session.restaurant_id) if session.restaurant_id else None,
                is_active=True,
            )
        
        # Get associated user for authenticated sessions
        if not session.user_id:
            raise UserNotFoundError("No user associated with session")
        
        user = await self._user_repository.get_user_by_id(session.user_id)
        if not user:
            raise UserNotFoundError("User associated with session not found")
        
        # Convert to DTO for response
        return UserDTO(
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
