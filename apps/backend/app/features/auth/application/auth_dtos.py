"""Authentication Data Transfer Objects (DTOs).

This module defines DTOs for transferring data between the application
and presentation layers. DTOs provide a clean interface for data exchange
without exposing domain entities directly.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


@dataclass
class EmailSignInRequestDTO:
    """DTO for email sign-in requests."""

    email: str
    password: str


@dataclass
class EmailSignUpRequestDTO:
    """DTO for email sign-up requests."""

    email: str
    password: str
    name: Optional[str] = None
    role: str = "customer"
    restaurant_id: Optional[str] = None


@dataclass
class PhoneAuthRequestDTO:
    """DTO for phone authentication requests."""

    phone: str


@dataclass
class PhoneVerifyRequestDTO:
    """DTO for phone OTP verification requests."""

    phone: str
    token: str
    name: Optional[str] = None


@dataclass
class AnonymousSessionRequestDTO:
    """DTO for anonymous session creation requests."""

    restaurant_id: str
    table_id: Optional[str] = None


@dataclass
class TokenRefreshRequestDTO:
    """DTO for token refresh requests."""

    refresh_token: str


@dataclass
class UserDTO:
    """DTO for user data."""

    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    role: str = "customer"
    restaurant_id: Optional[str] = None
    permissions: Dict[str, Any] = None
    is_active: bool = True
    is_anonymous: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.permissions is None:
            self.permissions = {}


@dataclass
class AuthResponseDTO:
    """DTO for authentication responses."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserDTO = None


@dataclass
class UserProfileResponseDTO:
    """DTO for user profile responses."""

    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    role: str = "customer"
    restaurant_id: Optional[str] = None
    permissions: Dict[str, Any] = None
    is_active: bool = True

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.permissions is None:
            self.permissions = {}


@dataclass
class AnonymousSessionResponseDTO:
    """DTO for anonymous session responses."""

    session_id: str
    session_token: str
    restaurant_id: str
    table_id: Optional[str] = None
    expires_at: str = ""


@dataclass
class PhoneAuthResponseDTO:
    """DTO for phone authentication initiation responses."""

    message: str = "OTP sent successfully"
    phone: str = ""
    otp_sent: bool = True


@dataclass
class SignOutResponseDTO:
    """DTO for sign-out responses."""

    message: str = "Signed out successfully"


@dataclass
class AuthenticationResultDTO:
    """DTO for authentication operation results."""

    success: bool
    user: Optional[UserDTO] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 3600
    error_message: Optional[str] = None
    requires_verification: bool = False


@dataclass
class UserContextDTO:
    """DTO for user context information."""

    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "customer"
    restaurant_id: Optional[str] = None
    permissions: Dict[str, Any] = None
    is_anonymous: bool = False

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.permissions is None:
            self.permissions = {}


@dataclass
class SessionDTO:
    """DTO for session data."""

    session_id: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_anonymous: bool = False
    restaurant_id: Optional[str] = None
    table_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class AnonymousSessionDTO:
    """DTO for anonymous session data."""

    session_id: str
    session_token: str
    restaurant_id: str
    table_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class TokenValidationDTO:
    """DTO for token validation results."""

    is_valid: bool
    user_id: Optional[str] = None
    claims: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.claims is None:
            self.claims = {}


@dataclass
class UserUpdateRequestDTO:
    """DTO for user update requests."""

    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    restaurant_id: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


@dataclass
class PasswordResetRequestDTO:
    """DTO for password reset requests."""

    email: str


@dataclass
class PasswordResetConfirmDTO:
    """DTO for password reset confirmation."""

    token: str
    new_password: str


@dataclass
class EmailVerificationDTO:
    """DTO for email verification."""

    token: str
    email: str


@dataclass
class AuthEventDTO:
    """DTO for authentication events (for logging)."""

    event_type: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# Utility functions for DTO conversions
def user_entity_to_dto(user) -> UserDTO:
    """Convert User entity to UserDTO.

    Args:
        user: User entity from domain layer

    Returns:
        UserDTO for application layer
    """
    return UserDTO(
        id=user.user_id,
        email=user.email.value if user.email else None,
        phone=user.phone.value if user.phone else None,
        name=user.name,
        role=user.role,
        restaurant_id=user.restaurant_id,
        permissions=user.permissions,
        is_active=user.is_active,
        is_anonymous=user.is_anonymous,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def auth_session_to_dto(session) -> SessionDTO:
    """Convert AuthSession entity to SessionDTO.

    Args:
        session: AuthSession entity from domain layer

    Returns:
        SessionDTO for application layer
    """
    return SessionDTO(
        session_id=session.session_id,
        user_id=session.user_id,
        access_token=session.access_token.value,
        refresh_token=session.refresh_token.value if session.refresh_token else None,
        expires_at=session.expires_at,
        is_anonymous=session.is_anonymous,
        restaurant_id=session.restaurant_id,
        table_id=session.table_id,
        created_at=session.created_at,
    )


def anonymous_session_entity_to_dto(session) -> AnonymousSessionDTO:
    """Convert AnonymousSession entity to AnonymousSessionDTO.

    Args:
        session: AnonymousSession entity from domain layer

    Returns:
        AnonymousSessionDTO for application layer
    """
    return AnonymousSessionDTO(
        session_id=session.session_id,
        session_token=session.session_token,
        restaurant_id=session.restaurant_id,
        table_id=session.table_id,
        expires_at=session.expires_at,
        created_at=session.created_at,
    )


# Error Response Models
class AuthErrorCode(str, Enum):
    """Enumeration of authentication error codes."""

    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    UNAUTHORIZED = "UNAUTHORIZED"

    # User errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_INACTIVE = "USER_INACTIVE"

    # Phone auth errors
    INVALID_PHONE = "INVALID_PHONE"
    INVALID_OTP = "INVALID_OTP"
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_SEND_FAILED = "OTP_SEND_FAILED"

    # Email errors
    INVALID_EMAIL = "INVALID_EMAIL"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"

    # Session errors
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    ANONYMOUS_SESSION_FAILED = "ANONYMOUS_SESSION_FAILED"

    # Restaurant code errors
    INVALID_RESTAURANT_CODE = "INVALID_RESTAURANT_CODE"
    RESTAURANT_CODE_EXPIRED = "RESTAURANT_CODE_EXPIRED"
    RESTAURANT_NOT_FOUND = "RESTAURANT_NOT_FOUND"

    # Permission errors
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCESS_DENIED = "ACCESS_DENIED"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Server errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


@dataclass
class ErrorDetail:
    """Detailed error information."""

    code: AuthErrorCode
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ErrorResponse:
    """Standardized error response."""

    error: str
    error_code: AuthErrorCode
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.timestamp is None:
            from datetime import datetime

            self.timestamp = datetime.utcnow().isoformat()
        if self.details is None:
            self.details = []


# Restaurant Code DTOs
@dataclass
class RestaurantCodeRequestDTO:
    """DTO for restaurant code validation requests."""

    code: str


@dataclass
class RestaurantBrandingDTO:
    """DTO for restaurant branding information."""

    restaurant_id: str
    name: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None


@dataclass
class RestaurantCodeResponseDTO:
    """DTO for restaurant code validation responses."""

    valid: bool
    restaurant: Optional[RestaurantBrandingDTO] = None
    session_token: Optional[str] = None
    message: Optional[str] = None
