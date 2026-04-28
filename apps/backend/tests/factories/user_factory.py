"""User factory for generating test user data.

Provides realistic user data for testing with proper validation
and relationships to other entities.
"""

import uuid
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from tests.config.test_config import TEST_CONFIG
from tests.config.auth_test_data import UserCredentials


@dataclass
class UserData:
    """User data structure for test generation."""
    id: str
    email: str
    password_hash: str
    name: str
    phone: Optional[str]
    role: str
    restaurant_id: Optional[str]
    is_active: bool = True
    email_verified: bool = False
    phone_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_signin_at: Optional[datetime] = None
    permissions: Dict[str, bool] = field(default_factory=dict)


class UserFactory:
    """Factory for generating test user data and entities."""

    def __init__(self):
        self.config = TEST_CONFIG
        self.created_users: List[UserData] = []

    def create_user(
        self,
        email: str = None,
        password: str = None,
        name: str = None,
        phone: str = None,
        role: str = "customer",
        restaurant_id: str = None,
        is_active: bool = True,
        email_verified: bool = False,
        permissions: Dict[str, bool] = None
    ) -> UserData:
        """Create a user with realistic test data."""
        user_id = str(uuid.uuid4())
        unique_id = secrets.token_hex(4)

        # Generate realistic data if not provided
        if not email:
            email = f"test_{unique_id}@{self.config.TEST_EMAIL_DOMAIN}"
        if not password:
            password = self.config.TEST_EMAIL_PASSWORD
        if not name:
            name = f"Test User {unique_id}"
        if not phone:
            phone = f"{self.config.TEST_PHONE_PREFIX}{secrets.choice(string.digits) for _ in range(4)}"

        # Hash password (in real implementation, you'd use proper hashing)
        password_hash = f"hashed_{password}_v1"

        # Set default permissions based on role
        if permissions is None:
            permissions = self._get_default_permissions(role)

        user_data = UserData(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            phone=phone,
            role=role,
            restaurant_id=restaurant_id,
            is_active=is_active,
            email_verified=email_verified,
            permissions=permissions
        )

        self.created_users.append(user_data)
        return user_data

    def create_customer(
        self,
        email: str = None,
        name: str = None,
        phone: str = None,
        email_verified: bool = False
    ) -> UserData:
        """Create a customer user."""
        return self.create_user(
            email=email,
            name=name,
            phone=phone,
            role="customer",
            restaurant_id=None,
            email_verified=email_verified
        )

    def create_manager(
        self,
        restaurant_id: str,
        email: str = None,
        name: str = None,
        phone: str = None
    ) -> UserData:
        """Create a manager user for a restaurant."""
        return self.create_user(
            email=email,
            name=name,
            phone=phone,
            role="manager",
            restaurant_id=restaurant_id,
            email_verified=True  # Managers are typically email verified
        )

    def create_service_staff(
        self,
        restaurant_id: str,
        email: str = None,
        name: str = None,
        phone: str = None
    ) -> UserData:
        """Create a service staff user for a restaurant."""
        return self.create_user(
            email=email,
            name=name,
            phone=phone,
            role="service",
            restaurant_id=restaurant_id,
            email_verified=True
        )

    def create_inactive_user(self, role: str = "customer") -> UserData:
        """Create an inactive user for testing."""
        return self.create_user(
            role=role,
            is_active=False,
            email_verified=False
        )

    def create_user_with_permissions(
        self,
        role: str,
        permissions: Dict[str, bool],
        restaurant_id: str = None
    ) -> UserData:
        """Create a user with specific permissions."""
        return self.create_user(
            role=role,
            permissions=permissions,
            restaurant_id=restaurant_id
        )

    def create_batch_users(
        self,
        count: int,
        role: str = "customer",
        restaurant_id: str = None
    ) -> List[UserData]:
        """Create multiple users of the same role."""
        users = []
        for _ in range(count):
            if role == "customer":
                users.append(self.create_customer())
            elif role in ["manager", "service"]:
                users.append(self.create_user(
                    role=role,
                    restaurant_id=restaurant_id
                ))
            else:
                users.append(self.create_user(role=role))
        return users

    def create_user_from_credentials(self, credentials: UserCredentials) -> UserData:
        """Create user from credentials object."""
        return self.create_user(
            email=credentials.email,
            password=credentials.password,
            name=credentials.name,
            phone=credentials.phone,
            role=credentials.role,
            restaurant_id=credentials.restaurant_id
        )

    def update_user_last_signin(self, user_id: str) -> Optional[UserData]:
        """Update user's last signin time."""
        for user in self.created_users:
            if user.id == user_id:
                user.last_signin_at = datetime.utcnow()
                user.updated_at = datetime.utcnow()
                return user
        return None

    def deactivate_user(self, user_id: str) -> Optional[UserData]:
        """Deactivate a user."""
        for user in self.created_users:
            if user.id == user_id:
                user.is_active = False
                user.updated_at = datetime.utcnow()
                return user
        return None

    def verify_user_email(self, user_id: str) -> Optional[UserData]:
        """Mark user email as verified."""
        for user in self.created_users:
            if user.id == user_id:
                user.email_verified = True
                user.updated_at = datetime.utcnow()
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[UserData]:
        """Find user by email."""
        for user in self.created_users:
            if user.email == email:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[UserData]:
        """Find user by ID."""
        for user in self.created_users:
            if user.id == user_id:
                return user
        return None

    def _get_default_permissions(self, role: str) -> Dict[str, bool]:
        """Get default permissions for a role."""
        permissions = {
            "customer": {
                "view_menu": True,
                "place_orders": True,
                "view_own_orders": True,
                "manage_profile": True
            },
            "service": {
                "view_menu": True,
                "manage_orders": True,
                "view_orders": True,
                "manage_tables": True
            },
            "manager": {
                "view_menu": True,
                "manage_menu": True,
                "manage_orders": True,
                "view_orders": True,
                "manage_staff": True,
                "manage_restaurant": True,
                "view_analytics": True
            },
            "admin": {
                "view_menu": True,
                "manage_menu": True,
                "manage_orders": True,
                "view_orders": True,
                "manage_staff": True,
                "manage_restaurant": True,
                "view_analytics": True,
                "manage_system": True
            }
        }
        return permissions.get(role, {})

    def to_dict(self, user: UserData) -> Dict[str, Any]:
        """Convert user data to dictionary format."""
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
            "restaurant_id": user.restaurant_id,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "phone_verified": user.phone_verified,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "last_signin_at": user.last_signin_at.isoformat() if user.last_signin_at else None,
            "permissions": user.permissions
        }

    def to_api_response(self, user: UserData) -> Dict[str, Any]:
        """Convert user to API response format (excluding sensitive data)."""
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "role": user.role,
            "restaurant_id": user.restaurant_id,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "permissions": user.permissions
        }

    def cleanup_all_users(self):
        """Clear all created users."""
        self.created_users.clear()

    def get_created_users_count(self) -> int:
        """Get count of created users."""
        return len(self.created_users)

    def get_users_by_role(self, role: str) -> List[UserData]:
        """Get all users of a specific role."""
        return [user for user in self.created_users if user.role == role]

    def get_users_by_restaurant(self, restaurant_id: str) -> List[UserData]:
        """Get all users for a specific restaurant."""
        return [user for user in self.created_users if user.restaurant_id == restaurant_id]


# Global factory instance
USER_FACTORY = UserFactory()