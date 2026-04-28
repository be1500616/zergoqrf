"""Anonymous session use case for QR code authentication.

This module implements the business logic for creating anonymous sessions
for restaurant customers using QR codes, following Clean Architecture principles.
"""

from uuid import uuid4, UUID

from ...domain.auth_entities import AuthSession
from ...domain.auth_repos import IAuthSessionRepository
from ...domain.auth_exceptions import InvalidTokenError
from ..auth_dtos import AnonymousSessionRequestDTO, AnonymousSessionResponseDTO


class AnonymousSessionUseCase:
    """Use case for creating anonymous sessions.
    
    Handles the business logic for creating temporary sessions
    for restaurant customers who scan QR codes.
    """
    
    def __init__(self, session_repository: IAuthSessionRepository):
        """Initialize the AnonymousSessionUseCase.
        
        Args:
            session_repository: Repository for session data operations
        """
        self._session_repository = session_repository
    
    async def execute(
        self, request: AnonymousSessionRequestDTO
    ) -> AnonymousSessionResponseDTO:
        """Execute the anonymous session creation use case.
        
        Args:
            request: Anonymous session request with restaurant and table info
            
        Returns:
            Anonymous session response with session details
            
        Raises:
            InvalidTokenError: If restaurant_id or table_id format is invalid
        """
        # Validate restaurant_id format
        try:
            restaurant_uuid = UUID(request.restaurant_id)
        except ValueError:
            raise InvalidTokenError(f"Invalid restaurant_id format: {request.restaurant_id}")
        
        # Validate table_id format
        try:
            table_uuid = UUID(request.table_id)
        except ValueError:
            raise InvalidTokenError(f"Invalid table_id format: {request.table_id}")
        
        # Create anonymous session
        session = AuthSession(
            id=uuid4(),
            user_id=None,  # Anonymous sessions don't have associated users
            session_type="anonymous",
            restaurant_id=restaurant_uuid,
            table_id=table_uuid,
        )
        
        # Save session to repository
        created_session = await self._session_repository.create_session(session)
        
        return AnonymousSessionResponseDTO(
            session_id=str(created_session.id),
            session_token=created_session.session_token,
            expires_at=created_session.expires_at,
            restaurant_id=str(created_session.restaurant_id),
            table_id=str(created_session.table_id),
        )
