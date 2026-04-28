"""Cart session management use cases.

This module contains use cases for managing cart sessions,
including creation, validation, and migration operations.
"""

import logging
from typing import Optional
from uuid import UUID

from ...domain.cart_entities import CartSession
from ...domain.cart_repos import ICartSessionRepository
from ...domain.cart_vos import CartSessionToken
from ...domain.cart_exceptions import (
    CartSessionNotFoundError,
    CartSessionExpiredError,
    CartMigrationError,
)
from ..cart_dtos import (
    CartSessionRequestDTO,
    CartSessionResponseDTO,
    CartMigrationRequestDTO,
    CartMigrationResponseDTO,
    cart_session_entity_to_dto,
)

logger = logging.getLogger(__name__)


class CreateAnonymousCartSessionUseCase:
    """Use case for creating anonymous cart sessions."""
    
    def __init__(self, cart_session_repository: ICartSessionRepository):
        """Initialize the use case.
        
        Args:
            cart_session_repository: Cart session repository
        """
        self._repository = cart_session_repository
    
    async def execute(
        self,
        anonymous_session_id: UUID,
        restaurant_id: UUID,
        table_id: Optional[UUID] = None,
    ) -> CartSessionResponseDTO:
        """Create a new anonymous cart session.
        
        Args:
            anonymous_session_id: Anonymous session ID to link to
            restaurant_id: Restaurant ID
            table_id: Optional table ID
            
        Returns:
            Created cart session DTO
            
        Raises:
            CartOperationError: If session creation fails
        """
        try:
            logger.info(
                "Creating anonymous cart session",
                extra={
                    "anonymous_session_id": str(anonymous_session_id),
                    "restaurant_id": str(restaurant_id),
                    "table_id": str(table_id) if table_id else None,
                }
            )
            
            session = await self._repository.create_anonymous_session(
                anonymous_session_id=anonymous_session_id,
                restaurant_id=restaurant_id,
                table_id=table_id,
                expires_hours=2,
            )
            
            logger.info(
                "Anonymous cart session created successfully",
                extra={
                    "session_id": str(session.id),
                    "session_token": session.session_token.value[:8] + "...",
                }
            )
            
            return cart_session_entity_to_dto(session)
            
        except Exception as e:
            logger.error(
                "Failed to create anonymous cart session",
                extra={
                    "error": str(e),
                    "anonymous_session_id": str(anonymous_session_id),
                    "restaurant_id": str(restaurant_id),
                }
            )
            raise


class CreateAuthenticatedCartSessionUseCase:
    """Use case for creating authenticated cart sessions."""
    
    def __init__(self, cart_session_repository: ICartSessionRepository):
        """Initialize the use case.
        
        Args:
            cart_session_repository: Cart session repository
        """
        self._repository = cart_session_repository
    
    async def execute(
        self,
        user_id: UUID,
        restaurant_id: UUID,
        table_id: Optional[UUID] = None,
    ) -> CartSessionResponseDTO:
        """Create a new authenticated cart session.
        
        Args:
            user_id: User ID
            restaurant_id: Restaurant ID
            table_id: Optional table ID
            
        Returns:
            Created cart session DTO
            
        Raises:
            CartOperationError: If session creation fails
        """
        try:
            logger.info(
                "Creating authenticated cart session",
                extra={
                    "user_id": str(user_id),
                    "restaurant_id": str(restaurant_id),
                    "table_id": str(table_id) if table_id else None,
                }
            )
            
            # Check if user already has an active session
            existing_session = await self._repository.get_active_session_for_user(
                user_id=user_id,
                restaurant_id=restaurant_id,
            )
            
            if existing_session and existing_session.is_valid():
                logger.info(
                    "Returning existing active cart session",
                    extra={"session_id": str(existing_session.id)}
                )
                return cart_session_entity_to_dto(existing_session)
            
            session = await self._repository.create_authenticated_session(
                user_id=user_id,
                restaurant_id=restaurant_id,
                table_id=table_id,
                expires_hours=24,
            )
            
            logger.info(
                "Authenticated cart session created successfully",
                extra={
                    "session_id": str(session.id),
                    "session_token": session.session_token.value[:8] + "...",
                }
            )
            
            return cart_session_entity_to_dto(session)
            
        except Exception as e:
            logger.error(
                "Failed to create authenticated cart session",
                extra={
                    "error": str(e),
                    "user_id": str(user_id),
                    "restaurant_id": str(restaurant_id),
                }
            )
            raise


class GetCartSessionUseCase:
    """Use case for retrieving cart sessions."""
    
    def __init__(self, cart_session_repository: ICartSessionRepository):
        """Initialize the use case.
        
        Args:
            cart_session_repository: Cart session repository
        """
        self._repository = cart_session_repository
    
    async def execute(self, session_token: str) -> CartSessionResponseDTO:
        """Get cart session by token.
        
        Args:
            session_token: Session token
            
        Returns:
            Cart session DTO
            
        Raises:
            CartSessionNotFoundError: If session not found
            CartSessionExpiredError: If session is expired
        """
        try:
            token = CartSessionToken(session_token)
            session = await self._repository.get_by_token(token)
            
            if not session:
                raise CartSessionNotFoundError(session_token)
            
            if session.is_expired():
                raise CartSessionExpiredError(session_token)
            
            if not session.is_active:
                raise CartSessionNotFoundError(session_token)
            
            return cart_session_entity_to_dto(session)
            
        except (CartSessionNotFoundError, CartSessionExpiredError):
            raise
        except Exception as e:
            logger.error(
                "Failed to get cart session",
                extra={
                    "error": str(e),
                    "session_token": session_token[:8] + "...",
                }
            )
            raise


class ExtendCartSessionActivityUseCase:
    """Use case for extending cart session activity."""
    
    def __init__(self, cart_session_repository: ICartSessionRepository):
        """Initialize the use case.
        
        Args:
            cart_session_repository: Cart session repository
        """
        self._repository = cart_session_repository
    
    async def execute(self, session_token: str) -> bool:
        """Extend cart session activity.
        
        Args:
            session_token: Session token
            
        Returns:
            True if session was extended, False otherwise
        """
        try:
            token = CartSessionToken(session_token)
            return await self._repository.extend_activity(token)
            
        except Exception as e:
            logger.error(
                "Failed to extend cart session activity",
                extra={
                    "error": str(e),
                    "session_token": session_token[:8] + "...",
                }
            )
            return False


class MigrateCartSessionUseCase:
    """Use case for migrating anonymous cart to authenticated session."""
    
    def __init__(self, cart_session_repository: ICartSessionRepository):
        """Initialize the use case.
        
        Args:
            cart_session_repository: Cart session repository
        """
        self._repository = cart_session_repository
    
    async def execute(self, request: CartMigrationRequestDTO) -> CartMigrationResponseDTO:
        """Migrate anonymous cart session to authenticated.
        
        Args:
            request: Migration request DTO
            
        Returns:
            Migration response DTO
            
        Raises:
            CartMigrationError: If migration fails
        """
        try:
            logger.info(
                "Starting cart migration",
                extra={
                    "anonymous_session_token": request.anonymous_session_token[:8] + "...",
                    "user_id": str(request.user_id),
                    "restaurant_id": str(request.restaurant_id),
                }
            )
            
            token = CartSessionToken(request.anonymous_session_token)
            new_session = await self._repository.migrate_anonymous_to_authenticated(
                anonymous_session_token=token,
                user_id=request.user_id,
                restaurant_id=request.restaurant_id,
            )
            
            logger.info(
                "Cart migration completed successfully",
                extra={
                    "new_session_id": str(new_session.id),
                    "item_count": new_session.item_count,
                }
            )
            
            return CartMigrationResponseDTO(
                new_session=cart_session_entity_to_dto(new_session),
                migrated_items_count=new_session.item_count,
                migration_successful=True,
            )
            
        except Exception as e:
            logger.error(
                "Cart migration failed",
                extra={
                    "error": str(e),
                    "user_id": str(request.user_id),
                    "restaurant_id": str(request.restaurant_id),
                }
            )
            raise CartMigrationError(str(e))
