"""Repository implementations for authentication infrastructure layer.

This module contains concrete implementations of the repository interfaces
defined in the domain layer, using Supabase as the data persistence layer.
"""

from typing import List, Optional
from uuid import UUID

from supabase import Client

from ..domain.auth_entities import AuthSession, User
from ..domain.auth_exceptions import (
    SessionNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from ..domain.auth_repos import IAuthSessionRepository, IUserRepository
from ..domain.auth_vos import Email, Password, PhoneNumber


class UserRepositoryImpl(IUserRepository):
    """Concrete implementation of IUserRepository using Supabase.

    This class implements all user data access operations using
    the Supabase client for database interactions.
    """

    def __init__(self, supabase_client: Client):
        """Initialize the UserRepositoryImpl.

        Args:
            supabase_client: Supabase client for database operations
        """
        self._client = supabase_client

    async def create_user(self, user: User) -> User:
        """Create a new user in the database.

        Args:
            user: The user entity to create

        Returns:
            The created user entity with updated metadata

        Raises:
            UserAlreadyExistsError: If user with same email exists
        """
        try:
            # Check if user already exists
            existing = await self.get_user_by_email(user.email)
            if existing:
                raise UserAlreadyExistsError(
                    f"User with email {user.email.value} already exists"
                )

            # Create user via Supabase Auth
            auth_response = self._client.auth.sign_up(
                {
                    "email": user.email.value,
                    "password": "temp_password",  # This will be handled by Supabase
                    "options": {
                        "data": {
                            "name": user.name,
                            "role": user.role,
                            "restaurant_id": (
                                str(user.restaurant_id) if user.restaurant_id else None
                            ),
                            "phone": user.phone.value if user.phone else None,
                        }
                    },
                }
            )

            if not auth_response.user:
                raise Exception("Failed to create user in Supabase Auth")

            # Update user with Supabase-generated ID
            user._id = UUID(auth_response.user.id)

            return user

        except Exception as e:
            if "already exists" in str(e).lower():
                raise UserAlreadyExistsError(str(e))
            raise

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user

        Returns:
            The user entity if found, None otherwise
        """
        try:
            # Get user from Supabase Auth
            auth_response = self._client.auth.get_user()
            if not auth_response.user or auth_response.user.id != str(user_id):
                return None

            # Convert Supabase user to domain entity
            return self._convert_supabase_user_to_entity(auth_response.user)

        except Exception:
            return None

    async def get_user_by_email(self, email: Email) -> Optional[User]:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for

        Returns:
            The user entity if found, None otherwise
        """
        try:
            # Query users table for email
            result = (
                self._client.table("auth.users")
                .select("*")
                .eq("email", email.value)
                .execute()
            )

            if not result.data:
                return None

            user_data = result.data[0]
            return self._convert_db_user_to_entity(user_data)

        except Exception:
            return None

    async def get_user_by_phone(self, phone: PhoneNumber) -> Optional[User]:
        """Retrieve a user by their phone number.

        Args:
            phone: The phone number to search for

        Returns:
            The user entity if found, None otherwise
        """
        try:
            # Query users table for phone
            result = (
                self._client.table("auth.users")
                .select("*")
                .eq("phone", phone.value)
                .execute()
            )

            if not result.data:
                return None

            user_data = result.data[0]
            return self._convert_db_user_to_entity(user_data)

        except Exception:
            return None

    async def update_user(self, user: User) -> User:
        """Update an existing user in the database.

        Args:
            user: The user entity with updated data

        Returns:
            The updated user entity

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        try:
            # Update user in Supabase Auth
            update_data = {
                "data": {
                    "name": user.name,
                    "role": user.role,
                    "restaurant_id": (
                        str(user.restaurant_id) if user.restaurant_id else None
                    ),
                    "phone": user.phone.value if user.phone else None,
                }
            }

            auth_response = self._client.auth.update_user(update_data)
            if not auth_response.user:
                raise UserNotFoundError(f"User with id {user.id} not found")

            return user

        except Exception as e:
            if "not found" in str(e).lower():
                raise UserNotFoundError(str(e))
            raise

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user from the database.

        Args:
            user_id: The unique identifier of the user to delete

        Returns:
            True if user was deleted, False if not found
        """
        try:
            # Note: Supabase doesn't provide direct user deletion via client
            # This would typically be handled via admin API or RLS policies
            # For now, we'll deactivate the user instead
            user = await self.get_user_by_id(user_id)
            if not user:
                return False

            user.deactivate()
            await self.update_user(user)
            return True

        except Exception:
            return False

    async def get_users_by_restaurant(self, restaurant_id: UUID) -> List[User]:
        """Retrieve all users associated with a restaurant.

        Args:
            restaurant_id: The restaurant identifier

        Returns:
            List of user entities associated with the restaurant
        """
        try:
            # Query restaurant_staff table for users
            result = (
                self._client.table("restaurant_staff")
                .select("user_id")
                .eq("restaurant_id", str(restaurant_id))
                .execute()
            )

            users = []
            for staff_record in result.data:
                user = await self.get_user_by_id(UUID(staff_record["user_id"]))
                if user:
                    users.append(user)

            return users

        except Exception:
            return []

    def _convert_supabase_user_to_entity(self, supabase_user) -> User:
        """Convert Supabase user object to domain entity.

        Args:
            supabase_user: Supabase user object

        Returns:
            User domain entity
        """
        metadata = supabase_user.user_metadata or {}

        return User(
            id=UUID(supabase_user.id),
            email=Email(supabase_user.email),
            password=Password("", is_hashed=True),  # Password not accessible
            phone=PhoneNumber(metadata.get("phone")) if metadata.get("phone") else None,
            name=metadata.get("name"),
            role=metadata.get("role", "customer"),
            restaurant_id=(
                UUID(metadata["restaurant_id"])
                if metadata.get("restaurant_id")
                else None
            ),
            is_active=True,  # Assume active if in Supabase
        )

    def _convert_db_user_to_entity(self, user_data: dict) -> User:
        """Convert database user record to domain entity.

        Args:
            user_data: User data from database

        Returns:
            User domain entity
        """
        metadata = user_data.get("user_metadata", {}) or {}

        return User(
            id=UUID(user_data["id"]),
            email=Email(user_data["email"]),
            password=Password("", is_hashed=True),  # Password not accessible
            phone=PhoneNumber(metadata.get("phone")) if metadata.get("phone") else None,
            name=metadata.get("name"),
            role=metadata.get("role", "customer"),
            restaurant_id=(
                UUID(metadata["restaurant_id"])
                if metadata.get("restaurant_id")
                else None
            ),
            is_active=True,  # Assume active if in database
        )


class AuthSessionRepositoryImpl(IAuthSessionRepository):
    """Concrete implementation of IAuthSessionRepository using Supabase.

    This class implements all session data access operations using
    the Supabase client for database interactions.
    """

    def __init__(self, supabase_client: Client):
        """Initialize the AuthSessionRepositoryImpl.

        Args:
            supabase_client: Supabase client for database operations
        """
        self._client = supabase_client

    async def create_session(self, session: AuthSession) -> AuthSession:
        """Create a new authentication session.

        Args:
            session: The session entity to create

        Returns:
            The created session entity with updated metadata
        """
        try:
            # Insert session into custom sessions table
            session_data = {
                "id": str(session.id),
                "user_id": str(session.user_id) if session.user_id else None,
                "session_token": session.session_token,
                "session_type": session.session_type,
                "restaurant_id": (
                    str(session.restaurant_id) if session.restaurant_id else None
                ),
                "table_id": str(session.table_id) if session.table_id else None,
                "expires_at": (
                    session.expires_at.isoformat() if session.expires_at else None
                ),
                "is_active": session.is_active,
                "created_at": (
                    session.created_at.isoformat() if session.created_at else None
                ),
            }

            result = self._client.table("auth_sessions").insert(session_data).execute()

            if not result.data:
                raise Exception("Failed to create session")

            return session

        except Exception as e:
            raise Exception(f"Failed to create session: {str(e)}")

    async def get_session_by_id(self, session_id: UUID) -> Optional[AuthSession]:
        """Retrieve a session by its ID.

        Args:
            session_id: The unique identifier of the session

        Returns:
            The session entity if found, None otherwise
        """
        try:
            result = (
                self._client.table("auth_sessions")
                .select("*")
                .eq("id", str(session_id))
                .execute()
            )

            if not result.data:
                return None

            return self._convert_db_session_to_entity(result.data[0])

        except Exception:
            return None

    async def get_session_by_token(self, session_token: str) -> Optional[AuthSession]:
        """Retrieve a session by its token.

        Args:
            session_token: The session token to search for

        Returns:
            The session entity if found, None otherwise
        """
        try:
            result = (
                self._client.table("auth_sessions")
                .select("*")
                .eq("session_token", session_token)
                .execute()
            )

            if not result.data:
                return None

            return self._convert_db_session_to_entity(result.data[0])

        except Exception:
            return None

    def _convert_db_session_to_entity(self, session_data: dict) -> AuthSession:
        """Convert database session record to domain entity.

        Args:
            session_data: Session data from database

        Returns:
            AuthSession domain entity
        """
        from datetime import datetime

        return AuthSession(
            id=UUID(session_data["id"]),
            user_id=(
                UUID(session_data["user_id"]) if session_data.get("user_id") else None
            ),
            session_token=session_data["session_token"],
            session_type=session_data["session_type"],
            restaurant_id=(
                UUID(session_data["restaurant_id"])
                if session_data.get("restaurant_id")
                else None
            ),
            table_id=(
                UUID(session_data["table_id"]) if session_data.get("table_id") else None
            ),
            expires_at=(
                datetime.fromisoformat(session_data["expires_at"])
                if session_data.get("expires_at")
                else None
            ),
            is_active=session_data.get("is_active", True),
            created_at=(
                datetime.fromisoformat(session_data["created_at"])
                if session_data.get("created_at")
                else None
            ),
        )
