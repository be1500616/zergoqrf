"""Authentication domain entities.

This module defines the core business entities for the authentication system.
These entities represent the fundamental business objects and their behavior.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from .auth_vos import Email, Phone, Token


class User:
    """Core user entity representing an authenticated user in the system.
    
    This entity encapsulates user identity, authentication status, and
    authorization information including roles and permissions.
    """
    
    def __init__(
        self,
        user_id: str,
        email: Optional[Email] = None,
        phone: Optional[Phone] = None,
        name: Optional[str] = None,
        role: str = "customer",
        restaurant_id: Optional[str] = None,
        permissions: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
        is_anonymous: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize a user entity.
        
        Args:
            user_id: Unique identifier for the user
            email: User's email address (if provided)
            phone: User's phone number (if provided)
            name: User's display name
            role: User's role in the system
            restaurant_id: Associated restaurant ID (for staff/owners)
            permissions: User's specific permissions
            is_active: Whether the user account is active
            is_anonymous: Whether this is an anonymous user
            created_at: When the user was created
            updated_at: When the user was last updated
        """
        self.user_id = user_id
        self.email = email
        self.phone = phone
        self.name = name
        self.role = role
        self.restaurant_id = restaurant_id
        self.permissions = permissions or {}
        self.is_active = is_active
        self.is_anonymous = is_anonymous
        self.created_at = created_at
        self.updated_at = updated_at
    
    def has_role(self, required_role: str) -> bool:
        """Check if user has the required role.
        
        Args:
            required_role: The role to check for
            
        Returns:
            True if user has the role or is an owner
        """
        return self.role == required_role or self.role == "owner"
    
    def has_any_role(self, allowed_roles: list[str]) -> bool:
        """Check if user has any of the allowed roles.
        
        Args:
            allowed_roles: List of roles to check against
            
        Returns:
            True if user has any of the allowed roles
        """
        return self.role in allowed_roles or self.role == "owner"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission.
        
        Args:
            permission: The permission to check for
            
        Returns:
            True if user has the permission or is an owner
        """
        if self.role == "owner":
            return True
        return self.permissions.get(permission, False)
    
    def can_access_restaurant(self, target_restaurant_id: Optional[str]) -> bool:
        """Check if user can access a specific restaurant.
        
        Args:
            target_restaurant_id: The restaurant ID to check access for
            
        Returns:
            True if user can access the restaurant
        """
        if target_restaurant_id is None:
            return True
        return self.restaurant_id == target_restaurant_id
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_profile(
        self,
        name: Optional[str] = None,
        email: Optional[Email] = None,
        phone: Optional[Phone] = None,
    ) -> None:
        """Update user profile information.
        
        Args:
            name: New display name
            email: New email address
            phone: New phone number
        """
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        self.updated_at = datetime.utcnow()


class AuthSession:
    """Authentication session entity representing a user's active session.
    
    This entity manages session state, tokens, and expiration for
    authenticated users.
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: str,
        access_token: Token,
        refresh_token: Optional[Token] = None,
        expires_at: Optional[datetime] = None,
        is_anonymous: bool = False,
        restaurant_id: Optional[str] = None,
        table_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        """Initialize an authentication session.
        
        Args:
            session_id: Unique identifier for the session
            user_id: ID of the user this session belongs to
            access_token: JWT access token
            refresh_token: Refresh token for token renewal
            expires_at: When the session expires
            is_anonymous: Whether this is an anonymous session
            restaurant_id: Associated restaurant (for anonymous sessions)
            table_id: Associated table (for anonymous sessions)
            created_at: When the session was created
        """
        self.session_id = session_id
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.is_anonymous = is_anonymous
        self.restaurant_id = restaurant_id
        self.table_id = table_id
        self.created_at = created_at or datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if the session has expired.
        
        Returns:
            True if the session has expired
        """
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the session is valid (not expired).
        
        Returns:
            True if the session is valid
        """
        return not self.is_expired()
    
    def refresh(self, new_access_token: Token, new_refresh_token: Optional[Token] = None) -> None:
        """Refresh the session with new tokens.
        
        Args:
            new_access_token: New JWT access token
            new_refresh_token: New refresh token (optional)
        """
        self.access_token = new_access_token
        if new_refresh_token:
            self.refresh_token = new_refresh_token


class AnonymousSession:
    """Anonymous session entity for QR code users.
    
    This entity represents temporary sessions for users who access
    the system via QR codes without full authentication.
    """
    
    def __init__(
        self,
        session_id: str,
        session_token: str,
        restaurant_id: str,
        table_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        """Initialize an anonymous session.
        
        Args:
            session_id: Unique identifier for the session
            session_token: Token for session validation
            restaurant_id: Associated restaurant ID
            table_id: Associated table ID (optional)
            expires_at: When the session expires
            created_at: When the session was created
        """
        self.session_id = session_id
        self.session_token = session_token
        self.restaurant_id = restaurant_id
        self.table_id = table_id
        self.expires_at = expires_at
        self.created_at = created_at or datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if the anonymous session has expired.
        
        Returns:
            True if the session has expired
        """
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the anonymous session is valid.
        
        Returns:
            True if the session is valid
        """
        return not self.is_expired()


class AuthenticationResult:
    """Result entity for authentication operations.
    
    This entity encapsulates the result of authentication attempts,
    including success/failure status and associated data.
    """
    
    def __init__(
        self,
        success: bool,
        user: Optional[User] = None,
        session: Optional[AuthSession] = None,
        error_message: Optional[str] = None,
        requires_verification: bool = False,
    ):
        """Initialize an authentication result.
        
        Args:
            success: Whether the authentication was successful
            user: The authenticated user (if successful)
            session: The created session (if successful)
            error_message: Error message (if failed)
            requires_verification: Whether additional verification is needed
        """
        self.success = success
        self.user = user
        self.session = session
        self.error_message = error_message
        self.requires_verification = requires_verification
    
    def is_successful(self) -> bool:
        """Check if the authentication was successful.
        
        Returns:
            True if authentication succeeded
        """
        return self.success
    
    def needs_verification(self) -> bool:
        """Check if additional verification is required.
        
        Returns:
            True if verification is needed
        """
        return self.requires_verification
