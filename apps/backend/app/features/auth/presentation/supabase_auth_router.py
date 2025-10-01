"""
Simplified Supabase authentication router for FastAPI.

This router provides clean authentication endpoints that properly integrate
with Supabase's built-in authentication system, eliminating redundant
session management and improving security.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from app.common.supabase_client import get_supabase, get_supabase_anon
from app.core.logging_config import log_auth_event, log_security_event
from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from supabase import Client

from ..application.auth_dtos import (
    RestaurantBrandingDTO,
    RestaurantCodeRequestDTO,
    RestaurantCodeResponseDTO,
)
from .error_helpers import (
    create_auth_error,
    create_database_error,
    create_internal_error,
    create_invalid_credentials_error,
    create_invalid_otp_error,
    create_invalid_token_error,
    create_session_error,
)
from .supabase_dependencies import (
    UserContext,
    get_current_user,
    get_current_user_optional,
    validate_anonymous_session,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Pydantic models for request/response
class EmailSignInRequest(BaseModel):
    """Request model for email/password sign in."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class EmailSignUpRequest(BaseModel):
    """Request model for email/password sign up."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None
    role: str = Field(default="customer")
    restaurant_id: Optional[str] = None


class PhoneAuthRequest(BaseModel):
    """Request model for phone authentication."""

    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")


class PhoneVerifyRequest(BaseModel):
    """Request model for phone OTP verification."""

    phone: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")
    token: str = Field(..., min_length=6, max_length=6)
    name: Optional[str] = None


class AnonymousSessionRequest(BaseModel):
    """Request model for anonymous session creation."""

    restaurant_id: str = Field(..., description="Restaurant UUID")
    table_id: Optional[str] = Field(None, description="Table UUID")


class AuthResponse(BaseModel):
    """Standard authentication response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class UserProfileResponse(BaseModel):
    """User profile response."""

    id: str
    email: Optional[str]
    phone: Optional[str]
    name: Optional[str]
    role: str
    restaurant_id: Optional[str]
    permissions: Dict[str, Any]
    is_active: bool


class AnonymousSessionResponse(BaseModel):
    """Anonymous session response."""

    session_id: str
    session_token: str
    restaurant_id: str
    table_id: Optional[str]
    expires_at: str


@router.post("/signin/email", response_model=AuthResponse)
async def sign_in_with_email(
    request: EmailSignInRequest,
    supabase: Client = Depends(get_supabase_anon),
):
    """
    Sign in with email and password using Supabase authentication.

    This endpoint uses Supabase's built-in authentication system
    and returns standard JWT tokens.
    """
    try:
        logger.debug(f"Email sign in attempt for: {request.email}")

        # Use anonymous client for sign in to avoid service role permissions
        auth_response = supabase.auth.sign_in_with_password(
            {"email": request.email, "password": request.password}
        )

        if not auth_response.user or not auth_response.session:
            log_auth_event(
                logger,
                "signin_failed",
                email=request.email,
                details="Invalid credentials",
                level="warning",
            )
            raise create_invalid_credentials_error()

        user = auth_response.user
        session = auth_response.session

        # Get user claims for response
        user_metadata = user.user_metadata or {}

        log_auth_event(
            logger,
            "signin_success",
            user_id=user.id,
            email=user.email,
            details=f"Role: {user_metadata.get('role', 'customer')}",
        )

        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token or "",
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user={
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": user_metadata.get("name"),
                "role": user_metadata.get("role", "customer"),
                "restaurant_id": user_metadata.get("restaurant_id"),
                "permissions": user_metadata.get("permissions", {}),
                "is_active": True,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        log_auth_event(
            logger,
            "signin_error",
            email=request.email,
            details=str(e),
            level="error",
        )
        logger.error(f"Email sign in error: {str(e)}")
        raise create_internal_error("Authentication failed")


@router.post("/signup/email", response_model=AuthResponse)
async def sign_up_with_email(
    request: EmailSignUpRequest,
    supabase: Client = Depends(get_supabase_anon),
):
    """
    Sign up with email and password using Supabase authentication.

    This endpoint creates a new user account and automatically
    creates associated customer/staff records via database triggers.
    """
    try:
        # Prepare user metadata
        user_data = {
            "name": request.name,
            "role": request.role,
        }

        if request.restaurant_id:
            user_data["restaurant_id"] = request.restaurant_id

        # Use anonymous client for sign up
        auth_response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {"data": user_data},
            }
        )

        if not auth_response.user:
            raise create_internal_error("Failed to create user account")

        user = auth_response.user
        session = auth_response.session

        # If no session (email confirmation required), return user info without tokens
        if not session:
            return AuthResponse(
                access_token="",
                refresh_token="",
                token_type="bearer",
                expires_in=0,
                user={
                    "id": user.id,
                    "email": user.email,
                    "name": request.name,
                    "role": request.role,
                    "restaurant_id": request.restaurant_id,
                    "permissions": {},
                    "is_active": False,  # Pending email confirmation
                },
            )

        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token or "",
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user={
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": request.name,
                "role": request.role,
                "restaurant_id": request.restaurant_id,
                "permissions": {},
                "is_active": True,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email sign up error: {str(e)}")
        raise create_internal_error("Account creation failed")


@router.post("/signin/phone")
async def sign_in_with_phone(
    request: PhoneAuthRequest,
    supabase: Client = Depends(get_supabase_anon),
):
    """
    Initiate phone authentication by sending OTP.

    This endpoint uses Supabase's built-in phone authentication
    to send an OTP to the provided phone number.
    """
    try:
        # Use Supabase's phone OTP
        supabase.auth.sign_in_with_otp({"phone": request.phone})

        return {
            "message": "OTP sent successfully",
            "phone": request.phone,
            "otp_sent": True,
        }

    except Exception as e:
        logger.error(f"Phone OTP error: {str(e)}")
        raise create_internal_error("Failed to send OTP")


@router.post("/verify/phone", response_model=AuthResponse)
async def verify_phone_otp(
    request: PhoneVerifyRequest,
    supabase: Client = Depends(get_supabase_anon),
):
    """
    Verify phone OTP and complete authentication.

    This endpoint verifies the OTP and returns JWT tokens
    for the authenticated user.
    """
    try:
        # Verify OTP with Supabase
        auth_response = supabase.auth.verify_otp(
            {"phone": request.phone, "token": request.token, "type": "sms"}
        )

        if not auth_response.user or not auth_response.session:
            raise create_invalid_otp_error()

        user = auth_response.user
        session = auth_response.session

        # Update user metadata if name provided
        if request.name and not user.user_metadata.get("name"):
            supabase.auth.update_user({"data": {"name": request.name}})

        user_metadata = user.user_metadata or {}

        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token or "",
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user={
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "name": user_metadata.get("name") or request.name,
                "role": user_metadata.get("role", "customer"),
                "restaurant_id": user_metadata.get("restaurant_id"),
                "permissions": user_metadata.get("permissions", {}),
                "is_active": True,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone OTP verification error: {str(e)}")
        raise create_internal_error("OTP verification failed")


@router.post("/anonymous-session", response_model=AnonymousSessionResponse)
async def create_anonymous_session(
    request: AnonymousSessionRequest,
    supabase: Client = Depends(get_supabase),
):
    """
    Create an anonymous session for QR code users.

    This endpoint creates a temporary session for users
    who access the menu via QR code without authentication.
    """
    try:
        # Call the database function to create anonymous session
        result = supabase.rpc(
            "create_anonymous_session",
            {
                "p_restaurant_id": request.restaurant_id,
                "p_table_id": request.table_id,
                "p_expires_hours": 24,
            },
        ).execute()

        if not result.data:
            raise create_session_error("Failed to create anonymous session")

        session_data = result.data[0]

        return AnonymousSessionResponse(
            session_id=session_data["session_id"],
            session_token=session_data["session_token"],
            restaurant_id=request.restaurant_id,
            table_id=request.table_id or "",
            expires_at=session_data["expires_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anonymous session creation error: {str(e)}")
        raise create_session_error("Failed to create anonymous session")


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    user_context: UserContext = Depends(get_current_user),
):
    """
    Get current user profile information.

    This endpoint returns the authenticated user's profile
    including role, permissions, and restaurant access.
    """
    return UserProfileResponse(
        id=user_context.user_id,
        email=user_context.email,
        phone=user_context.phone,
        name=user_context.email,  # TODO: Get actual name from user metadata
        role=user_context.role,
        restaurant_id=user_context.restaurant_id,
        permissions=user_context.permissions,
        is_active=True,
    )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_context: UserContext = Depends(get_current_user),
):
    """
    Get user profile information (alias for /me endpoint).

    This endpoint provides the same functionality as /me but with
    a different path for frontend compatibility.
    """
    return UserProfileResponse(
        id=user_context.user_id,
        email=user_context.email,
        phone=user_context.phone,
        name=user_context.email,  # TODO: Get actual name from user metadata
        role=user_context.role,
        restaurant_id=user_context.restaurant_id,
        permissions=user_context.permissions,
        is_active=True,
    )


@router.post("/signout")
async def sign_out(
    user_context: UserContext = Depends(get_current_user_optional),
    supabase: Client = Depends(get_supabase_anon),
):
    """
    Sign out the current user.

    This endpoint invalidates the user's session and tokens.
    """
    try:
        if user_context and not user_context.is_anonymous:
            # Sign out from Supabase
            supabase.auth.sign_out()

        return {"message": "Signed out successfully"}

    except Exception as e:
        logger.error(f"Sign out error: {str(e)}")
        # Don't fail sign out even if there's an error
        return {"message": "Signed out successfully"}


@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    supabase: Client = Depends(get_supabase_anon),
):
    """
    Refresh access token using refresh token.

    This endpoint uses Supabase's built-in token refresh
    to get a new access token.
    """
    try:
        auth_response = supabase.auth.refresh_session(refresh_token)

        if not auth_response.session:
            raise create_invalid_token_error()

        session = auth_response.session
        user = auth_response.user

        user_metadata = user.user_metadata or {} if user else {}

        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token or "",
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user={
                "id": user.id if user else "",
                "email": user.email if user else None,
                "phone": user.phone if user else None,
                "name": user_metadata.get("name"),
                "role": user_metadata.get("role", "customer"),
                "restaurant_id": user_metadata.get("restaurant_id"),
                "permissions": user_metadata.get("permissions", {}),
                "is_active": True,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise create_invalid_token_error()


@router.post("/validate-restaurant-code", response_model=Dict[str, Any])
async def validate_restaurant_code(
    request: RestaurantCodeRequestDTO = Body(...),
    supabase: Client = Depends(get_supabase_anon),
) -> Dict[str, Any]:
    """
    Validate a restaurant code and return restaurant branding information.

    This endpoint allows diners to access a restaurant's menu by entering
    a restaurant code without full authentication. It creates an anonymous
    session for the user.

    Args:
        request: Restaurant code request containing the code to validate
        supabase: Supabase client instance

    Returns:
        Restaurant branding information and session token if valid

    Raises:
        HTTPException: If code is invalid or database error occurs
    """
    try:
        code = request.code.upper().strip()

        # Validate code format (6-8 alphanumeric characters)
        if not code or len(code) < 6 or len(code) > 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid restaurant code format",
            )

        # Query restaurant by code
        response = (
            supabase.table("restaurants")
            .select("id, name, settings")
            .eq("code", code)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            log_security_event(
                "invalid_restaurant_code",
                {"code": code},
                "warning",
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant code not found",
            )

        restaurant = response.data[0]
        restaurant_id = restaurant["id"]
        restaurant_name = restaurant["name"]
        settings = restaurant.get("settings", {})

        # Extract branding information from settings
        branding = settings.get("branding", {})

        # Create anonymous session
        import secrets
        from datetime import datetime, timedelta, timezone

        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        session_response = (
            supabase.table("anonymous_sessions")
            .insert(
                {
                    "restaurant_id": restaurant_id,
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat(),
                }
            )
            .execute()
        )

        if not session_response.data:
            raise create_database_error()

        log_auth_event(
            "restaurant_code_validated",
            {
                "restaurant_id": restaurant_id,
                "code": code,
            },
        )

        # Return restaurant branding and session token
        return {
            "valid": True,
            "restaurant": {
                "restaurant_id": restaurant_id,
                "name": restaurant_name,
                "logo_url": branding.get("logo_url"),
                "primary_color": branding.get("primary_color"),
                "secondary_color": branding.get("secondary_color"),
            },
            "session_token": session_token,
            "message": f"Welcome to {restaurant_name}!",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restaurant code validation error: {str(e)}")
        raise create_internal_error()
