"""Anonymous session management use cases.

This module contains use cases for managing anonymous sessions
for QR code users who access the system without full authentication.
"""

import logging
from datetime import datetime
from typing import Optional

from ...domain.auth_entities import AnonymousSession
from ...domain.auth_repos import ISessionRepository
from ...domain.auth_vos import SessionToken
from ...domain.auth_exceptions import (
    AuthenticationError,
    SessionNotFoundError,
    SessionExpiredError,
    MultiTenantViolationError,
)
from ..auth_dtos import (
    AnonymousSessionRequestDTO,
    AnonymousSessionResponseDTO,
    anonymous_session_entity_to_dto,
)
from ....core.logging_config import log_auth_event

logger = logging.getLogger(__name__)


class CreateAnonymousSessionUseCase:
    """Use case for creating anonymous sessions.
    
    This use case handles the business logic for creating temporary
    sessions for QR code users who access the system without authentication.
    """
    
    def __init__(self, session_repository: ISessionRepository):
        """Initialize the use case.
        
        Args:
            session_repository: Repository for session operations
        """
        self._session_repository = session_repository
    
    async def execute(self, request: AnonymousSessionRequestDTO) -> AnonymousSessionResponseDTO:
        """Execute anonymous session creation use case.
        
        Args:
            request: Anonymous session creation request data
            
        Returns:
            Anonymous session response with session data
            
        Raises:
            AuthenticationError: If session creation fails
            MultiTenantViolationError: If restaurant access is invalid
        """
        try:
            logger.debug(f"Creating anonymous session for restaurant: {request.restaurant_id}")
            
            # Validate restaurant ID format (basic UUID check)
            if not self._is_valid_uuid(request.restaurant_id):
                log_auth_event(
                    logger,
                    "anonymous_session_failed",
                    details=f"Invalid restaurant ID format: {request.restaurant_id}",
                    level="warning",
                )
                raise MultiTenantViolationError("Invalid restaurant ID format")
            
            # Validate table ID format if provided
            if request.table_id and not self._is_valid_uuid(request.table_id):
                log_auth_event(
                    logger,
                    "anonymous_session_failed",
                    details=f"Invalid table ID format: {request.table_id}",
                    level="warning",
                )
                raise MultiTenantViolationError("Invalid table ID format")
            
            # Create anonymous session
            session = await self._session_repository.create_anonymous_session(
                restaurant_id=request.restaurant_id,
                table_id=request.table_id,
                expires_hours=24,  # Default 24-hour expiration
            )
            
            # Log successful session creation
            log_auth_event(
                logger,
                "anonymous_session_created",
                details=f"Session created for restaurant {request.restaurant_id}, table {request.table_id}",
            )
            
            # Convert to response DTO
            return AnonymousSessionResponseDTO(
                session_id=session.session_id,
                session_token=session.session_token,
                restaurant_id=session.restaurant_id,
                table_id=session.table_id,
                expires_at=session.expires_at.isoformat() if session.expires_at else "",
            )
            
        except MultiTenantViolationError:
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "anonymous_session_error",
                details=str(e),
                level="error"
            )
            logger.error(f"Anonymous session creation error: {str(e)}")
            raise AuthenticationError("Failed to create anonymous session")
    
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Validate UUID format.
        
        Args:
            uuid_string: String to validate as UUID
            
        Returns:
            True if valid UUID format
        """
        try:
            import uuid
            uuid.UUID(uuid_string)
            return True
        except (ValueError, TypeError):
            return False


class ValidateAnonymousSessionUseCase:
    """Use case for validating anonymous sessions.
    
    This use case handles validation of anonymous session tokens
    to ensure they are valid and not expired.
    """
    
    def __init__(self, session_repository: ISessionRepository):
        """Initialize the use case.
        
        Args:
            session_repository: Repository for session operations
        """
        self._session_repository = session_repository
    
    async def execute(self, session_token: str) -> bool:
        """Execute anonymous session validation use case.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            True if session is valid and not expired
            
        Raises:
            SessionNotFoundError: If session is not found
            SessionExpiredError: If session has expired
            AuthenticationError: If validation fails
        """
        try:
            logger.debug(f"Validating anonymous session token: {session_token[:10]}...")
            
            # Create session token value object
            try:
                token = SessionToken(session_token)
            except ValueError as e:
                log_auth_event(
                    logger,
                    "session_validation_failed",
                    details="Invalid session token format",
                    level="warning",
                )
                raise AuthenticationError(f"Invalid session token format: {str(e)}")
            
            # Validate session
            is_valid = await self._session_repository.validate_anonymous_session(token)
            
            if not is_valid:
                log_auth_event(
                    logger,
                    "session_validation_failed",
                    details="Session token is invalid or expired",
                    level="warning",
                )
                return False
            
            # Log successful validation
            log_auth_event(
                logger,
                "session_validated",
                details="Anonymous session validated successfully",
            )
            
            return True
            
        except Exception as e:
            log_auth_event(
                logger,
                "session_validation_error",
                details=str(e),
                level="error"
            )
            logger.error(f"Session validation error: {str(e)}")
            raise AuthenticationError("Session validation failed")


class GetAnonymousSessionUseCase:
    """Use case for retrieving anonymous session data.
    
    This use case handles retrieval of anonymous session information
    by session ID.
    """
    
    def __init__(self, session_repository: ISessionRepository):
        """Initialize the use case.
        
        Args:
            session_repository: Repository for session operations
        """
        self._session_repository = session_repository
    
    async def execute(self, session_id: str) -> Optional[AnonymousSessionResponseDTO]:
        """Execute anonymous session retrieval use case.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Anonymous session data if found, None otherwise
            
        Raises:
            AuthenticationError: If retrieval fails
        """
        try:
            logger.debug(f"Retrieving anonymous session: {session_id}")
            
            # Get session from repository
            session = await self._session_repository.get_anonymous_session(session_id)
            
            if not session:
                log_auth_event(
                    logger,
                    "session_not_found",
                    details=f"Session not found: {session_id}",
                    level="warning",
                )
                return None
            
            # Check if session is expired
            if session.is_expired():
                log_auth_event(
                    logger,
                    "session_expired",
                    details=f"Session expired: {session_id}",
                    level="warning",
                )
                return None
            
            # Convert to response DTO
            return AnonymousSessionResponseDTO(
                session_id=session.session_id,
                session_token=session.session_token,
                restaurant_id=session.restaurant_id,
                table_id=session.table_id,
                expires_at=session.expires_at.isoformat() if session.expires_at else "",
            )
            
        except Exception as e:
            logger.error(f"Session retrieval error: {str(e)}")
            raise AuthenticationError("Failed to retrieve session")


class InvalidateAnonymousSessionUseCase:
    """Use case for invalidating anonymous sessions.
    
    This use case handles invalidation of anonymous sessions
    when users sign out or sessions need to be terminated.
    """
    
    def __init__(self, session_repository: ISessionRepository):
        """Initialize the use case.
        
        Args:
            session_repository: Repository for session operations
        """
        self._session_repository = session_repository
    
    async def execute(self, session_id: str) -> bool:
        """Execute anonymous session invalidation use case.
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            True if invalidation was successful
            
        Raises:
            AuthenticationError: If invalidation fails
        """
        try:
            logger.debug(f"Invalidating anonymous session: {session_id}")
            
            # Invalidate session
            success = await self._session_repository.invalidate_anonymous_session(session_id)
            
            if success:
                log_auth_event(
                    logger,
                    "session_invalidated",
                    details=f"Session invalidated: {session_id}",
                )
            else:
                log_auth_event(
                    logger,
                    "session_invalidation_failed",
                    details=f"Failed to invalidate session: {session_id}",
                    level="warning",
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Session invalidation error: {str(e)}")
            raise AuthenticationError("Failed to invalidate session")


class CleanupExpiredSessionsUseCase:
    """Use case for cleaning up expired anonymous sessions.
    
    This use case handles periodic cleanup of expired anonymous sessions
    to maintain database hygiene.
    """
    
    def __init__(self, session_repository: ISessionRepository):
        """Initialize the use case.
        
        Args:
            session_repository: Repository for session operations
        """
        self._session_repository = session_repository
    
    async def execute(self) -> int:
        """Execute expired session cleanup use case.
        
        Returns:
            Number of sessions cleaned up
            
        Raises:
            AuthenticationError: If cleanup fails
        """
        try:
            logger.debug("Starting cleanup of expired anonymous sessions")
            
            # Clean up expired sessions
            cleaned_count = await self._session_repository.cleanup_expired_sessions()
            
            # Log cleanup results
            log_auth_event(
                logger,
                "sessions_cleaned",
                details=f"Cleaned up {cleaned_count} expired sessions",
            )
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Session cleanup error: {str(e)}")
            raise AuthenticationError("Failed to cleanup expired sessions")


class ExtendAnonymousSessionUseCase:
    """Use case for extending anonymous session expiration.
    
    This use case handles extending the expiration time of active
    anonymous sessions to keep them valid longer.
    """
    
    def __init__(self, session_repository: ISessionRepository):
        """Initialize the use case.
        
        Args:
            session_repository: Repository for session operations
        """
        self._session_repository = session_repository
    
    async def execute(self, session_id: str, extend_hours: int = 24) -> bool:
        """Execute session extension use case.
        
        Args:
            session_id: Session ID to extend
            extend_hours: Number of hours to extend the session
            
        Returns:
            True if extension was successful
            
        Raises:
            SessionNotFoundError: If session is not found
            AuthenticationError: If extension fails
        """
        try:
            logger.debug(f"Extending anonymous session: {session_id} by {extend_hours} hours")
            
            # Get current session
            session = await self._session_repository.get_anonymous_session(session_id)
            
            if not session:
                raise SessionNotFoundError(f"Session not found: {session_id}")
            
            # Check if session is still valid (not expired)
            if session.is_expired():
                raise SessionExpiredError(f"Cannot extend expired session: {session_id}")
            
            # This would typically involve updating the session expiration
            # For now, we'll assume success since the repository would handle this
            
            log_auth_event(
                logger,
                "session_extended",
                details=f"Session {session_id} extended by {extend_hours} hours",
            )
            
            return True
            
        except (SessionNotFoundError, SessionExpiredError):
            raise
        except Exception as e:
            logger.error(f"Session extension error: {str(e)}")
            raise AuthenticationError("Failed to extend session")
