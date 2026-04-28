"""Exception handlers for authentication endpoints.

This module provides FastAPI exception handlers that map domain exceptions
to appropriate HTTP responses, following Clean Architecture principles.
"""

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from ..domain.auth_exceptions import (
    AccountDeactivatedError,
    AuthenticationError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidOTPError,
    InvalidTokenError,
    MultiTenantViolationError,
    OTPExpiredError,
    RateLimitExceededError,
    SessionExpiredError,
    SessionNotFoundError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


def map_auth_exception_to_http(exception: AuthenticationError) -> HTTPException:
    """Map authentication domain exception to HTTP exception.

    Args:
        exception: Domain exception to map

    Returns:
        Appropriate HTTP exception
    """
    # Map specific exceptions to HTTP status codes
    exception_mapping = {
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        UserAlreadyExistsError: status.HTTP_409_CONFLICT,
        UserNotFoundError: status.HTTP_404_NOT_FOUND,
        AccountDeactivatedError: status.HTTP_403_FORBIDDEN,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        TokenExpiredError: status.HTTP_401_UNAUTHORIZED,
        SessionExpiredError: status.HTTP_401_UNAUTHORIZED,
        SessionNotFoundError: status.HTTP_401_UNAUTHORIZED,
        InsufficientPermissionsError: status.HTTP_403_FORBIDDEN,
        RateLimitExceededError: status.HTTP_429_TOO_MANY_REQUESTS,
        MultiTenantViolationError: status.HTTP_403_FORBIDDEN,
        OTPExpiredError: status.HTTP_401_UNAUTHORIZED,
        InvalidOTPError: status.HTTP_401_UNAUTHORIZED,
    }

    # Get the appropriate status code
    status_code = exception_mapping.get(
        type(exception), status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    # Create error response with consistent format
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exception.__class__.__name__,
            "message": str(exception),
            "error_code": exception.error_code,
        },
    )


async def auth_exception_handler(request, exc: AuthenticationError) -> JSONResponse:
    """Global exception handler for authentication errors.

    Args:
        request: FastAPI request object
        exc: Authentication exception

    Returns:
        JSON response with error details
    """
    http_exception = map_auth_exception_to_http(exc)

    return JSONResponse(
        status_code=http_exception.status_code,
        content=http_exception.detail,
    )


# Specific exception handlers for common cases
async def invalid_credentials_handler(
    request, exc: InvalidCredentialsError
) -> JSONResponse:
    """Handle invalid credentials errors.

    Args:
        request: FastAPI request object
        exc: Invalid credentials exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "InvalidCredentials",
            "message": "Invalid email or password",
            "error_code": exc.error_code,
        },
    )


async def user_not_found_handler(request, exc: UserNotFoundError) -> JSONResponse:
    """Handle user not found errors.

    Args:
        request: FastAPI request object
        exc: User not found exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "UserNotFound",
            "message": "User account not found",
            "error_code": exc.error_code,
        },
    )


async def session_expired_handler(request, exc: SessionExpiredError) -> JSONResponse:
    """Handle session expired errors.

    Args:
        request: FastAPI request object
        exc: Session expired exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "SessionExpired",
            "message": "Your session has expired. Please sign in again.",
            "error_code": exc.error_code,
        },
    )


async def permission_denied_handler(
    request, exc: InsufficientPermissionsError
) -> JSONResponse:
    """Handle permission denied errors.

    Args:
        request: FastAPI request object
        exc: Permission denied exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "PermissionDenied",
            "message": "You don't have permission to access this resource",
            "error_code": exc.error_code,
        },
    )
