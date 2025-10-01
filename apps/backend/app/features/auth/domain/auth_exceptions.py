"""Custom exceptions for authentication domain.

This module defines domain-specific exceptions that represent
business rule violations and error conditions in the authentication system.
"""


class AuthenticationError(Exception):
    """Base exception for authentication-related errors.

    This is the base class for all authentication domain exceptions.
    """

    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        """Initialize an authentication error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when user credentials are invalid.

    This exception is raised when a user provides incorrect
    email/password or phone/OTP combinations.
    """

    def __init__(self, message: str = "Invalid credentials provided"):
        """Initialize an invalid credentials error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "INVALID_CREDENTIALS")


class UserNotFoundError(AuthenticationError):
    """Exception raised when a user cannot be found.

    This exception is raised when attempting to access a user
    that doesn't exist in the system.
    """

    def __init__(self, message: str = "User not found"):
        """Initialize a user not found error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "USER_NOT_FOUND")


class UserAlreadyExistsError(AuthenticationError):
    """Exception raised when attempting to create a duplicate user.

    This exception is raised when trying to create a user with
    an email or phone number that already exists.
    """

    def __init__(self, message: str = "User already exists"):
        """Initialize a user already exists error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "USER_ALREADY_EXISTS")


class TokenExpiredError(AuthenticationError):
    """Exception raised when a token has expired.

    This exception is raised when attempting to use an expired
    JWT token or session token.
    """

    def __init__(self, message: str = "Token has expired"):
        """Initialize a token expired error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "TOKEN_EXPIRED")


class InvalidTokenError(AuthenticationError):
    """Exception raised when a token is invalid or malformed.

    This exception is raised when a token cannot be validated
    or has been tampered with.
    """

    def __init__(self, message: str = "Invalid token"):
        """Initialize an invalid token error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "INVALID_TOKEN")


class InsufficientPermissionsError(AuthenticationError):
    """Exception raised when user lacks required permissions.

    This exception is raised when a user attempts to perform
    an action they don't have permission for.
    """

    def __init__(self, message: str = "Insufficient permissions"):
        """Initialize an insufficient permissions error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "INSUFFICIENT_PERMISSIONS")


class SessionNotFoundError(AuthenticationError):
    """Exception raised when a session cannot be found.

    This exception is raised when attempting to access a session
    that doesn't exist in the system.
    """

    def __init__(self, message: str = "Session not found"):
        """Initialize a session not found error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "SESSION_NOT_FOUND")


class SessionExpiredError(AuthenticationError):
    """Exception raised when a session has expired.

    This exception is raised when attempting to use an expired
    authentication session.
    """

    def __init__(self, message: str = "Session has expired"):
        """Initialize a session expired error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "SESSION_EXPIRED")


class AccountDeactivatedError(AuthenticationError):
    """Exception raised when attempting to use a deactivated account.

    This exception is raised when a user with a deactivated
    account attempts to authenticate.
    """

    def __init__(self, message: str = "Account has been deactivated"):
        """Initialize an account deactivated error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "ACCOUNT_DEACTIVATED")


class MultiTenantViolationError(AuthenticationError):
    """Exception raised when multi-tenant access rules are violated.

    This exception is raised when a user attempts to access
    data from a different restaurant/tenant.
    """

    def __init__(self, message: str = "Access denied: multi-tenant violation"):
        """Initialize a multi-tenant violation error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "MULTI_TENANT_VIOLATION")


class OTPExpiredError(AuthenticationError):
    """Exception raised when an OTP has expired.

    This exception is raised when attempting to verify an
    expired one-time password.
    """

    def __init__(self, message: str = "OTP has expired"):
        """Initialize an OTP expired error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "OTP_EXPIRED")


class InvalidOTPError(AuthenticationError):
    """Exception raised when an OTP is invalid.

    This exception is raised when an incorrect OTP is provided
    for phone number verification.
    """

    def __init__(self, message: str = "Invalid OTP"):
        """Initialize an invalid OTP error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "INVALID_OTP")


class RateLimitExceededError(AuthenticationError):
    """Exception raised when rate limits are exceeded.

    This exception is raised when a user exceeds the allowed
    number of authentication attempts.
    """

    def __init__(self, message: str = "Rate limit exceeded"):
        """Initialize a rate limit exceeded error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "RATE_LIMIT_EXCEEDED")


class InvalidEmailFormatError(AuthenticationError):
    """Exception raised when email format is invalid.

    This exception is raised when an email address doesn't
    match the expected format.
    """

    def __init__(self, message: str = "Invalid email format"):
        """Initialize an invalid email format error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "INVALID_EMAIL_FORMAT")


class WeakPasswordError(AuthenticationError):
    """Exception raised when password is too weak.

    This exception is raised when a password doesn't meet
    the minimum security requirements.
    """

    def __init__(self, message: str = "Password is too weak"):
        """Initialize a weak password error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "WEAK_PASSWORD")


class InvalidPhoneFormatError(AuthenticationError):
    """Exception raised when phone number format is invalid.

    This exception is raised when a phone number doesn't
    match the expected format.
    """

    def __init__(self, message: str = "Invalid phone number format"):
        """Initialize an invalid phone format error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, "INVALID_PHONE_FORMAT")
