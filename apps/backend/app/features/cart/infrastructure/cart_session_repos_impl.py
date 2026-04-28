"""Cart session repository implementation using Supabase.

This module provides the concrete implementation of the cart session repository
interface using Supabase as the data store.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from supabase import AClient

from ..domain.cart_entities import CartSession, SessionType
from ..domain.cart_exceptions import (
    CartMigrationError,
    CartOperationError,
    CartSessionNotFoundError,
)
from ..domain.cart_repos import ICartSessionRepository
from ..domain.cart_vos import CartSessionToken, Money

logger = logging.getLogger(__name__)


class CartSessionRepositoryImpl(ICartSessionRepository):
    """Supabase implementation of cart session repository."""

    def __init__(self, supabase_client: AClient):
        """Initialize the repository.

        Args:
            supabase_client: Async Supabase client instance
        """
        self._client = supabase_client

    async def create_anonymous_session(
        self,
        anonymous_session_id: UUID,
        restaurant_id: UUID,
        table_id: Optional[UUID] = None,
        expires_hours: int = 2,
    ) -> CartSession:
        """Create a new anonymous cart session.

        Args:
            anonymous_session_id: Anonymous session ID to link to
            restaurant_id: Restaurant ID
            table_id: Optional table ID
            expires_hours: Session expiration in hours

        Returns:
            Created cart session

        Raises:
            CartOperationError: If session creation fails
        """
        try:
            logger.info(
                "Creating anonymous cart session in database",
                extra={
                    "anonymous_session_id": str(anonymous_session_id),
                    "restaurant_id": str(restaurant_id),
                    "expires_hours": expires_hours,
                },
            )

            # Call database function to create anonymous cart session
            result = await self._client.rpc(
                "create_anonymous_cart_session",
                {
                    "p_anonymous_session_id": str(anonymous_session_id),
                    "p_restaurant_id": str(restaurant_id),
                    "p_table_id": str(table_id) if table_id else None,
                    "p_expires_hours": expires_hours,
                },
            ).execute()

            if not result.data:
                raise CartOperationError(
                    "create_anonymous_session", "Database function returned no data"
                )

            session_data = result.data[0]

            # Create domain entity
            session = CartSession(
                id=UUID(session_data["session_id"]),
                session_token=CartSessionToken(session_data["session_token"]),
                session_type=SessionType.ANONYMOUS,
                restaurant_id=restaurant_id,
                anonymous_session_id=anonymous_session_id,
                table_id=table_id,
                expires_at=datetime.fromisoformat(
                    session_data["expires_at"].replace("Z", "+00:00")
                ),
                item_count=0,
                total_amount=Money(0),
                is_active=True,
                last_activity_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            logger.info(
                "Anonymous cart session created successfully",
                extra={
                    "session_id": str(session.id),
                    "session_token": session.session_token.value[:8] + "...",
                },
            )

            return session

        except Exception as e:
            logger.error(
                "Failed to create anonymous cart session",
                extra={
                    "error": str(e),
                    "anonymous_session_id": str(anonymous_session_id),
                    "restaurant_id": str(restaurant_id),
                },
            )
            raise CartOperationError("create_anonymous_session", str(e))

    async def create_authenticated_session(
        self,
        user_id: UUID,
        restaurant_id: UUID,
        table_id: Optional[UUID] = None,
        expires_hours: int = 24,
    ) -> CartSession:
        """Create a new authenticated cart session.

        Args:
            user_id: User ID
            restaurant_id: Restaurant ID
            table_id: Optional table ID
            expires_hours: Session expiration in hours

        Returns:
            Created cart session

        Raises:
            CartOperationError: If session creation fails
        """
        try:
            logger.info(
                "Creating authenticated cart session in database",
                extra={
                    "user_id": str(user_id),
                    "restaurant_id": str(restaurant_id),
                    "expires_hours": expires_hours,
                },
            )

            # Call database function to create authenticated cart session
            result = await self._client.rpc(
                "create_authenticated_cart_session",
                {
                    "p_user_id": str(user_id),
                    "p_restaurant_id": str(restaurant_id),
                    "p_table_id": str(table_id) if table_id else None,
                    "p_expires_hours": expires_hours,
                },
            ).execute()

            if not result.data:
                raise CartOperationError(
                    "create_authenticated_session", "Database function returned no data"
                )

            session_data = result.data[0]

            # Create domain entity
            session = CartSession(
                id=UUID(session_data["session_id"]),
                session_token=CartSessionToken(session_data["session_token"]),
                session_type=SessionType.AUTHENTICATED,
                restaurant_id=restaurant_id,
                user_id=user_id,
                table_id=table_id,
                expires_at=datetime.fromisoformat(
                    session_data["expires_at"].replace("Z", "+00:00")
                ),
                item_count=0,
                total_amount=Money(0),
                is_active=True,
                last_activity_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            logger.info(
                "Authenticated cart session created successfully",
                extra={
                    "session_id": str(session.id),
                    "session_token": session.session_token.value[:8] + "...",
                },
            )

            return session

        except Exception as e:
            logger.error(
                "Failed to create authenticated cart session",
                extra={
                    "error": str(e),
                    "user_id": str(user_id),
                    "restaurant_id": str(restaurant_id),
                },
            )
            raise CartOperationError("create_authenticated_session", str(e))

    async def get_by_token(
        self, session_token: CartSessionToken
    ) -> Optional[CartSession]:
        """Get cart session by token.

        Args:
            session_token: Session token

        Returns:
            Cart session if found, None otherwise
        """
        try:
            # Call database function to validate cart session
            result = await self._client.rpc(
                "validate_cart_session", {"p_session_token": session_token.value}
            ).execute()

            if not result.data:
                return None

            session_data = result.data[0]

            if not session_data.get("is_valid"):
                return None

            # Determine session type and create appropriate entity
            session_type = SessionType(session_data["session_type"])

            session = CartSession(
                id=UUID(session_data["session_id"]),
                session_token=session_token,
                session_type=session_type,
                restaurant_id=UUID(session_data["restaurant_id"]),
                user_id=(
                    UUID(session_data["user_id"]) if session_data["user_id"] else None
                ),
                table_id=(
                    UUID(session_data["table_id"]) if session_data["table_id"] else None
                ),
                expires_at=datetime.fromisoformat(
                    session_data["expires_at"].replace("Z", "+00:00")
                ),
                # Note: item_count and total_amount will be loaded from database
                # For now using defaults, should be updated with actual values
                item_count=0,
                total_amount=Money(0),
                is_active=True,
                last_activity_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            return session

        except Exception as e:
            logger.error(
                "Failed to get cart session by token",
                extra={
                    "error": str(e),
                    "session_token": session_token.value[:8] + "...",
                },
            )
            return None

    async def get_by_id(self, session_id: UUID) -> Optional[CartSession]:
        """Get cart session by ID.

        Args:
            session_id: Session ID

        Returns:
            Cart session if found, None otherwise
        """
        try:
            result = await (
                self._client.table("cart_sessions")
                .select("*")
                .eq("id", str(session_id))
                .execute()
            )

            if not result.data:
                return None

            session_data = result.data[0]

            # Convert to domain entity
            session_type = SessionType(session_data["session_type"])

            session = CartSession(
                id=UUID(session_data["id"]),
                session_token=CartSessionToken(session_data["session_token"]),
                session_type=session_type,
                restaurant_id=UUID(session_data["restaurant_id"]),
                user_id=(
                    UUID(session_data["user_id"]) if session_data["user_id"] else None
                ),
                anonymous_session_id=(
                    UUID(session_data["anonymous_session_id"])
                    if session_data["anonymous_session_id"]
                    else None
                ),
                table_id=(
                    UUID(session_data["table_id"]) if session_data["table_id"] else None
                ),
                expires_at=datetime.fromisoformat(
                    session_data["expires_at"].replace("Z", "+00:00")
                ),
                item_count=session_data["item_count"],
                total_amount=Money(session_data["total_amount"]),
                is_active=session_data["is_active"],
                last_activity_at=datetime.fromisoformat(
                    session_data["last_activity_at"].replace("Z", "+00:00")
                ),
                created_at=datetime.fromisoformat(
                    session_data["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    session_data["updated_at"].replace("Z", "+00:00")
                ),
            )

            return session

        except Exception as e:
            logger.error(
                "Failed to get cart session by ID",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                },
            )
            return None

    async def get_active_session_for_user(
        self, user_id: UUID, restaurant_id: UUID
    ) -> Optional[CartSession]:
        """Get active cart session for authenticated user.

        Args:
            user_id: User ID
            restaurant_id: Restaurant ID

        Returns:
            Active cart session if found, None otherwise
        """
        try:
            result = await (
                self._client.table("cart_sessions")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("restaurant_id", str(restaurant_id))
                .eq("session_type", "authenticated")
                .eq("is_active", True)
                .gt("expires_at", datetime.now(timezone.utc).isoformat())
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            session_data = result.data[0]

            # Convert to domain entity
            session = CartSession(
                id=UUID(session_data["id"]),
                session_token=CartSessionToken(session_data["session_token"]),
                session_type=SessionType.AUTHENTICATED,
                restaurant_id=UUID(session_data["restaurant_id"]),
                user_id=UUID(session_data["user_id"]),
                table_id=(
                    UUID(session_data["table_id"]) if session_data["table_id"] else None
                ),
                expires_at=datetime.fromisoformat(
                    session_data["expires_at"].replace("Z", "+00:00")
                ),
                item_count=session_data["item_count"],
                total_amount=Money(session_data["total_amount"]),
                is_active=session_data["is_active"],
                last_activity_at=datetime.fromisoformat(
                    session_data["last_activity_at"].replace("Z", "+00:00")
                ),
                created_at=datetime.fromisoformat(
                    session_data["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    session_data["updated_at"].replace("Z", "+00:00")
                ),
            )

            return session

        except Exception as e:
            logger.error(
                "Failed to get active session for user",
                extra={
                    "error": str(e),
                    "user_id": str(user_id),
                    "restaurant_id": str(restaurant_id),
                },
            )
            return None

    async def update(self, session: CartSession) -> CartSession:
        """Update cart session.

        Args:
            session: Cart session to update

        Returns:
            Updated cart session
        """
        try:
            update_data = {
                "item_count": session.item_count,
                "total_amount": float(session.total_amount.amount),
                "is_active": session.is_active,
                "last_activity_at": session.last_activity_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            result = await (
                self._client.table("cart_sessions")
                .update(update_data)
                .eq("id", str(session.id))
                .execute()
            )

            if not result.data:
                raise CartOperationError("update_session", "No session updated")

            return session

        except Exception as e:
            logger.error(
                "Failed to update cart session",
                extra={
                    "error": str(e),
                    "session_id": str(session.id),
                },
            )
            raise CartOperationError("update_session", str(e))

    async def extend_activity(self, session_token: CartSessionToken) -> bool:
        """Extend session activity.

        Args:
            session_token: Session token

        Returns:
            True if session was extended, False otherwise
        """
        try:
            result = await self._client.rpc(
                "extend_cart_session_activity", {"p_session_token": session_token.value}
            ).execute()

            return result.data if result.data is not None else False

        except Exception as e:
            logger.error(
                "Failed to extend session activity",
                extra={
                    "error": str(e),
                    "session_token": session_token.value[:8] + "...",
                },
            )
            return False

    async def migrate_anonymous_to_authenticated(
        self,
        anonymous_session_token: CartSessionToken,
        user_id: UUID,
        restaurant_id: UUID,
    ) -> CartSession:
        """Migrate anonymous cart session to authenticated.

        Args:
            anonymous_session_token: Anonymous session token
            user_id: User ID to migrate to
            restaurant_id: Restaurant ID

        Returns:
            New authenticated cart session

        Raises:
            CartMigrationError: If migration fails
        """
        try:
            result = await self._client.rpc(
                "migrate_cart_to_authenticated",
                {
                    "p_anonymous_session_token": anonymous_session_token.value,
                    "p_user_id": str(user_id),
                    "p_restaurant_id": str(restaurant_id),
                },
            ).execute()

            if not result.data:
                raise CartMigrationError("Database function returned no data")

            migration_data = result.data[0]

            # Get the new session details
            new_session = await self.get_by_token(
                CartSessionToken(migration_data["new_session_token"])
            )

            if not new_session:
                raise CartMigrationError("Failed to retrieve migrated session")

            return new_session

        except Exception as e:
            logger.error(
                "Failed to migrate cart session",
                extra={
                    "error": str(e),
                    "user_id": str(user_id),
                    "restaurant_id": str(restaurant_id),
                },
            )
            raise CartMigrationError(str(e))

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired cart sessions.

        Returns:
            Number of sessions cleaned up
        """
        try:
            result = await self._client.rpc("cleanup_expired_cart_sessions").execute()
            return result.data if result.data is not None else 0

        except Exception as e:
            logger.error("Failed to cleanup expired sessions", extra={"error": str(e)})
            return 0

    async def extend_session_activity(self, session_token: CartSessionToken) -> bool:
        """Extend session activity and expiration.

        Args:
            session_token: Session token

        Returns:
            True if session was extended, False otherwise
        """
        return await self.extend_activity(session_token)

    async def update_session_totals(self, session_id: UUID) -> bool:
        """Update session item count and total amount.

        Args:
            session_id: Session ID

        Returns:
            True if update was successful, False otherwise
        """
        try:
            result = await self._client.rpc(
                "update_cart_session_totals", {"p_cart_session_id": str(session_id)}
            ).execute()

            return True

        except Exception as e:
            logger.error(
                "Failed to update session totals",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                },
            )
            return False

    async def deactivate_session(self, session_id: UUID) -> bool:
        """Deactivate a cart session.

        Args:
            session_id: Session ID

        Returns:
            True if session was deactivated, False otherwise
        """
        try:
            result = await (
                self._client.table("cart_sessions")
                .update(
                    {
                        "is_active": False,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("id", str(session_id))
                .execute()
            )

            return len(result.data) > 0

        except Exception as e:
            logger.error(
                "Failed to deactivate session",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                },
            )
            return False
