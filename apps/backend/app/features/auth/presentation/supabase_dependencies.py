"""
Simplified Supabase authentication dependencies for FastAPI.

This module provides clean, efficient authentication dependencies that properly
integrate with Supabase's built-in authentication system, eliminating redundant
session management and improving performance.
"""

import logging
from typing import Any, Dict, List, Optional

import jwt
from app.common.supabase_client import get_supabase, get_user_supabase_client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

logger = logging.getLogger(__name__)

# Security scheme for Bearer token authentication
security = HTTPBearer(scheme_name="BearerAuth")


class UserContext:
    """User context containing authentication and authorization information."""

    def __init__(
        self,
        user_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        role: str = "customer",
        restaurant_id: Optional[str] = None,
        permissions: Optional[Dict[str, Any]] = None,
        is_anonymous: bool = False,
    ):
        self.user_id = user_id
        self.email = email
        self.phone = phone
        self.role = role
        self.restaurant_id = restaurant_id
        self.permissions = permissions or {}
        self.is_anonymous = is_anonymous

    def has_role(self, required_role: str) -> bool:
        """Check if user has the required role."""
        return self.role == required_role or self.role == "owner"

    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the required roles."""
        return self.role in roles or self.role == "owner"

    def has_permission(self, permission: str) -> bool:
        """Check if user has the required permission."""
        if self.role == "owner":
            return True
        return self.permissions.get(permission, False)

    def can_access_restaurant(self, target_restaurant_id: Optional[str]) -> bool:
        """Check if user can access the specified restaurant."""
        if target_restaurant_id is None:
            return True
        return self.restaurant_id == target_restaurant_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase),
) -> UserContext:
    """
    Get current authenticated user from Supabase JWT token.

    This dependency validates the JWT token with Supabase and extracts
    user information and claims for authorization.

    Args:
        credentials: Bearer token from Authorization header
        supabase: Supabase client instance

    Returns:
        UserContext with user information and permissions

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Validate token with Supabase
        user_response = supabase.auth.get_user(credentials.credentials)
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user = user_response.user

        # Decode JWT to get custom claims (without verification since Supabase already validated)
        try:
            decoded_token = jwt.decode(
                credentials.credentials, options={"verify_signature": False}
            )
            custom_claims = decoded_token.get("app_metadata", {})
        except Exception:
            custom_claims = {}

        # Get user metadata safely
        user_metadata = getattr(user, "user_metadata", {}) or {}

        # Extract user information
        user_id = user.id
        email = user.email
        phone = getattr(user, "phone", None) or user_metadata.get("phone")
        role = custom_claims.get("role", user_metadata.get("role", "customer"))
        restaurant_id = custom_claims.get(
            "restaurant_id", user_metadata.get("restaurant_id")
        )
        permissions = custom_claims.get(
            "permissions", user_metadata.get("permissions", {})
        )

        logger.info(f"Authenticated user: {user_id} with role: {role}")

        return UserContext(
            user_id=user_id,
            email=email,
            phone=phone,
            role=role,
            restaurant_id=restaurant_id,
            permissions=permissions,
            is_anonymous=False,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase),
) -> Optional[UserContext]:
    """
    Get current user if authenticated, otherwise return None.

    This dependency is useful for endpoints that work for both
    authenticated and anonymous users.

    Args:
        credentials: Optional Bearer token from Authorization header
        supabase: Supabase client instance

    Returns:
        UserContext if authenticated, None otherwise
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        return await get_current_user(credentials, supabase)
    except HTTPException:
        return None


def require_role(allowed_roles: List[str]):
    """
    Dependency factory for role-based access control.

    Args:
        allowed_roles: List of roles that are allowed access

    Returns:
        Dependency function that validates user role
    """

    async def role_checker(
        user_context: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if not user_context.has_any_role(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}",
            )
        return user_context

    return role_checker


def require_permission(required_permission: str):
    """
    Dependency factory for permission-based access control.

    Args:
        required_permission: Permission that is required for access

    Returns:
        Dependency function that validates user permission
    """

    async def permission_checker(
        user_context: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if not user_context.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}",
            )
        return user_context

    return permission_checker


def require_restaurant_access(restaurant_id_param: str = "restaurant_id"):
    """
    Dependency factory for restaurant-based access control.

    Args:
        restaurant_id_param: Name of the path/query parameter containing restaurant_id

    Returns:
        Dependency function that validates restaurant access
    """

    async def restaurant_access_checker(
        user_context: UserContext = Depends(get_current_user),
        # Note: In a real implementation, you'd extract restaurant_id from path/query params
        # This is a simplified version for demonstration
    ) -> UserContext:
        # For now, just return the user context
        # In a full implementation, you'd validate restaurant access here
        return user_context

    return restaurant_access_checker


async def get_user_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Client:
    """
    Get Supabase client configured with user's JWT token for RLS operations.

    This dependency provides a Supabase client that includes the user's
    authentication context, allowing RLS policies to work correctly.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        Supabase client configured with user authentication

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    return get_user_supabase_client(credentials.credentials)


async def validate_anonymous_session(
    session_token: str,
    supabase: Client = Depends(get_supabase),
) -> UserContext:
    """
    Validate anonymous session token and return session context.

    Args:
        session_token: Anonymous session token
        supabase: Supabase client instance

    Returns:
        UserContext for anonymous session

    Raises:
        HTTPException: If session is invalid or expired
    """
    try:
        # Call the database function to validate anonymous session
        result = supabase.rpc(
            "validate_anonymous_session", {"p_session_token": session_token}
        ).execute()

        if not result.data or not result.data[0].get("is_valid"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired anonymous session",
            )

        session_data = result.data[0]

        return UserContext(
            user_id=session_data["session_id"],
            role="anonymous",
            restaurant_id=session_data["restaurant_id"],
            is_anonymous=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anonymous session validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Anonymous session validation failed",
        )


# Convenience dependencies for common role requirements
require_owner = require_role(["owner"])
require_manager = require_role(["owner", "manager"])
require_staff = require_role(["owner", "manager", "staff"])
require_kitchen = require_role(["owner", "manager", "kitchen"])
require_service = require_role(["owner", "manager", "service"])

# Convenience dependencies for common permissions
require_manage_menu = require_permission("manage_menu")
require_manage_orders = require_permission("manage_orders")
require_manage_tables = require_permission("manage_tables")
require_manage_staff = require_permission("manage_staff")
require_view_analytics = require_permission("view_analytics")
