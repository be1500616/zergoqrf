"""
Error handling helpers for authentication endpoints.

This module provides utilities for creating standardized error responses
across all authentication endpoints.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from ..application.auth_dtos import AuthErrorCode, ErrorDetail, ErrorResponse


def create_error_response(
    error_code: AuthErrorCode,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[List[ErrorDetail]] = None,
) -> HTTPException:
    """
    Create a standardized HTTP exception with structured error response.

    Args:
        error_code: The authentication error code
        message: Human-readable error message
        status_code: HTTP status code (default: 400)
        details: Optional list of detailed error information

    Returns:
        HTTPException with structured error response

    Example:
        >>> raise create_error_response(
        ...     AuthErrorCode.INVALID_CREDENTIALS,
        ...     "Invalid email or password",
        ...     status.HTTP_401_UNAUTHORIZED
        ... )
    """
    error_response = ErrorResponse(
        error=error_code.value,
        error_code=error_code,
        message=message,
        details=details or [],
        timestamp=datetime.utcnow().isoformat(),
    )

    return HTTPException(
        status_code=status_code,
        detail={
            "error": error_response.error,
            "error_code": error_response.error_code.value,
            "message": error_response.message,
            "details": [
                {
                    "code": d.code.value,
                    "message": d.message,
                    "field": d.field,
                    "details": d.details,
                }
                for d in error_response.details
            ],
            "timestamp": error_response.timestamp,
        },
    )


def create_auth_error(message: str = "Authentication failed") -> HTTPException:
    """Create a 401 Unauthorized error."""
    return create_error_response(
        AuthErrorCode.UNAUTHORIZED,
        message,
        status.HTTP_401_UNAUTHORIZED,
    )


def create_invalid_credentials_error() -> HTTPException:
    """Create an invalid credentials error."""
    return create_error_response(
        AuthErrorCode.INVALID_CREDENTIALS,
        "Invalid email or password",
        status.HTTP_401_UNAUTHORIZED,
    )


def create_invalid_token_error() -> HTTPException:
    """Create an invalid token error."""
    return create_error_response(
        AuthErrorCode.INVALID_TOKEN,
        "Invalid or expired token",
        status.HTTP_401_UNAUTHORIZED,
    )


def create_invalid_otp_error() -> HTTPException:
    """Create an invalid OTP error."""
    return create_error_response(
        AuthErrorCode.INVALID_OTP,
        "Invalid or expired OTP code",
        status.HTTP_401_UNAUTHORIZED,
    )


def create_user_exists_error(email: str) -> HTTPException:
    """Create a user already exists error."""
    return create_error_response(
        AuthErrorCode.USER_ALREADY_EXISTS,
        f"User with email {email} already exists",
        status.HTTP_409_CONFLICT,
        details=[
            ErrorDetail(
                code=AuthErrorCode.EMAIL_ALREADY_EXISTS,
                message="This email is already registered",
                field="email",
            )
        ],
    )


def create_invalid_restaurant_code_error() -> HTTPException:
    """Create an invalid restaurant code error."""
    return create_error_response(
        AuthErrorCode.INVALID_RESTAURANT_CODE,
        "Invalid or expired restaurant code",
        status.HTTP_404_NOT_FOUND,
    )


def create_rate_limit_error() -> HTTPException:
    """Create a rate limit exceeded error."""
    return create_error_response(
        AuthErrorCode.RATE_LIMIT_EXCEEDED,
        "Too many requests. Please try again later.",
        status.HTTP_429_TOO_MANY_REQUESTS,
    )


def create_internal_error(
    message: str = "An internal error occurred"
) -> HTTPException:
    """Create a 500 Internal Server Error."""
    return create_error_response(
        AuthErrorCode.INTERNAL_ERROR,
        message,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def create_database_error() -> HTTPException:
    """Create a database error."""
    return create_error_response(
        AuthErrorCode.DATABASE_ERROR,
        "Database operation failed",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def create_session_error(message: str = "Session creation failed") -> HTTPException:
    """Create a session error."""
    return create_error_response(
        AuthErrorCode.ANONYMOUS_SESSION_FAILED,
        message,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

