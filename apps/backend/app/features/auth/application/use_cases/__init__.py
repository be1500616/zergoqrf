"""Authentication use cases package.

This package contains all use cases for the authentication feature.
Use cases orchestrate business logic and coordinate between domain
and infrastructure layers.
"""

from .email_auth_use_cases import (
    EmailSignInUseCase,
    EmailSignUpUseCase,
    EmailVerificationUseCase,
)
from .phone_auth_use_cases import (
    PhoneAuthUseCase,
    OTPVerificationUseCase,
    PhoneSignUpUseCase,
    ResendOTPUseCase,
)
from .anonymous_session_use_cases import (
    CreateAnonymousSessionUseCase,
    ValidateAnonymousSessionUseCase,
    GetAnonymousSessionUseCase,
    InvalidateAnonymousSessionUseCase,
    CleanupExpiredSessionsUseCase,
    ExtendAnonymousSessionUseCase,
)
from .token_management_use_cases import (
    TokenRefreshUseCase,
    UserProfileUseCase,
    SignOutUseCase,
    ValidateTokenUseCase,
    BlacklistTokenUseCase,
)

__all__ = [
    # Email authentication use cases
    "EmailSignInUseCase",
    "EmailSignUpUseCase",
    "EmailVerificationUseCase",
    
    # Phone authentication use cases
    "PhoneAuthUseCase",
    "OTPVerificationUseCase",
    "PhoneSignUpUseCase",
    "ResendOTPUseCase",
    
    # Anonymous session use cases
    "CreateAnonymousSessionUseCase",
    "ValidateAnonymousSessionUseCase",
    "GetAnonymousSessionUseCase",
    "InvalidateAnonymousSessionUseCase",
    "CleanupExpiredSessionsUseCase",
    "ExtendAnonymousSessionUseCase",
    
    # Token management use cases
    "TokenRefreshUseCase",
    "UserProfileUseCase",
    "SignOutUseCase",
    "ValidateTokenUseCase",
    "BlacklistTokenUseCase",
]
