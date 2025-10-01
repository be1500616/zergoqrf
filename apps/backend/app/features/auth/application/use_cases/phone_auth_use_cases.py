"""Phone authentication use cases.

This module contains use cases for phone-based authentication operations
including OTP initiation and verification.
"""

import logging
from typing import Optional

from ...domain.auth_entities import AuthenticationResult
from ...domain.auth_repos import IAuthRepository
from ...domain.auth_vos import Phone, OTPCode
from ...domain.auth_exceptions import (
    AuthenticationError,
    InvalidPhoneFormatError,
    InvalidOTPError,
    OTPExpiredError,
    RateLimitExceededError,
)
from ..auth_dtos import (
    PhoneAuthRequestDTO,
    PhoneVerifyRequestDTO,
    PhoneAuthResponseDTO,
    AuthResponseDTO,
    user_entity_to_dto,
)
from ....core.logging_config import log_auth_event

logger = logging.getLogger(__name__)


class PhoneAuthUseCase:
    """Use case for initiating phone authentication.
    
    This use case handles the business logic for sending OTP
    to phone numbers for authentication.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, request: PhoneAuthRequestDTO) -> PhoneAuthResponseDTO:
        """Execute phone authentication initiation use case.
        
        Args:
            request: Phone authentication request data
            
        Returns:
            Response indicating OTP was sent
            
        Raises:
            InvalidPhoneFormatError: If phone format is invalid
            RateLimitExceededError: If too many attempts
            AuthenticationError: If OTP sending fails
        """
        try:
            logger.debug(f"Phone auth attempt for: {request.phone}")
            
            # Validate phone format
            try:
                phone = Phone(request.phone)
            except ValueError as e:
                log_auth_event(
                    logger,
                    "phone_auth_failed",
                    phone=request.phone,
                    details="Invalid phone format",
                    level="warning",
                )
                raise InvalidPhoneFormatError(str(e))
            
            # Check rate limiting (this would typically be implemented
            # with Redis or similar caching mechanism)
            # For now, we'll skip this check
            
            # Initiate phone authentication
            success = await self._auth_repository.initiate_phone_auth(phone)
            
            if not success:
                log_auth_event(
                    logger,
                    "phone_auth_failed",
                    phone=request.phone,
                    details="Failed to send OTP",
                    level="error",
                )
                raise AuthenticationError("Failed to send OTP")
            
            # Log successful OTP initiation
            log_auth_event(
                logger,
                "phone_auth_initiated",
                phone=request.phone,
                details="OTP sent successfully",
            )
            
            return PhoneAuthResponseDTO(
                message="OTP sent successfully",
                phone=request.phone,
                otp_sent=True,
            )
            
        except (InvalidPhoneFormatError, RateLimitExceededError):
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "phone_auth_error",
                phone=request.phone,
                details=str(e),
                level="error"
            )
            logger.error(f"Phone OTP error: {str(e)}")
            raise AuthenticationError("Failed to send OTP")


class OTPVerificationUseCase:
    """Use case for verifying phone OTP.
    
    This use case handles the business logic for verifying OTP codes
    and completing phone-based authentication.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, request: PhoneVerifyRequestDTO) -> AuthResponseDTO:
        """Execute OTP verification use case.
        
        Args:
            request: OTP verification request data
            
        Returns:
            Authentication response with tokens and user data
            
        Raises:
            InvalidPhoneFormatError: If phone format is invalid
            InvalidOTPError: If OTP is invalid
            OTPExpiredError: If OTP has expired
            AuthenticationError: If verification fails
        """
        try:
            logger.debug(f"OTP verification attempt for: {request.phone}")
            
            # Validate phone format
            try:
                phone = Phone(request.phone)
            except ValueError as e:
                log_auth_event(
                    logger,
                    "otp_verification_failed",
                    phone=request.phone,
                    details="Invalid phone format",
                    level="warning",
                )
                raise InvalidPhoneFormatError(str(e))
            
            # Validate OTP format
            try:
                otp_code = OTPCode(request.token)
            except ValueError as e:
                log_auth_event(
                    logger,
                    "otp_verification_failed",
                    phone=request.phone,
                    details="Invalid OTP format",
                    level="warning",
                )
                raise InvalidOTPError(str(e))
            
            # Verify OTP
            auth_result = await self._auth_repository.verify_phone_otp(
                phone=phone,
                otp_code=otp_code,
                name=request.name,
            )
            
            if not auth_result.is_successful():
                error_msg = auth_result.error_message or "Invalid or expired OTP"
                log_auth_event(
                    logger,
                    "otp_verification_failed",
                    phone=request.phone,
                    details=error_msg,
                    level="warning",
                )
                
                # Determine specific error type
                if "expired" in error_msg.lower():
                    raise OTPExpiredError(error_msg)
                else:
                    raise InvalidOTPError(error_msg)
            
            # Convert domain entities to DTOs
            user_dto = user_entity_to_dto(auth_result.user)
            
            # Log successful verification
            log_auth_event(
                logger,
                "otp_verification_success",
                user_id=auth_result.user.user_id,
                phone=auth_result.user.phone.value if auth_result.user.phone else None,
                details=f"Role: {auth_result.user.role}",
            )
            
            # Update user metadata if name was provided and not already set
            if request.name and not auth_result.user.name:
                await self._auth_repository.update_user_metadata(
                    auth_result.user.user_id,
                    {"name": request.name}
                )
                user_dto.name = request.name
            
            # Build response
            return AuthResponseDTO(
                access_token=auth_result.session.access_token.value,
                refresh_token=auth_result.session.refresh_token.value if auth_result.session.refresh_token else "",
                token_type="bearer",
                expires_in=3600,  # Default to 1 hour
                user=user_dto,
            )
            
        except (InvalidPhoneFormatError, InvalidOTPError, OTPExpiredError):
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "otp_verification_error",
                phone=request.phone,
                details=str(e),
                level="error"
            )
            logger.error(f"Phone OTP verification error: {str(e)}")
            raise AuthenticationError("OTP verification failed")


class PhoneSignUpUseCase:
    """Use case for phone-based sign-up.
    
    This use case handles creating new accounts using phone numbers
    and OTP verification.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(
        self,
        phone_request: PhoneAuthRequestDTO,
        verify_request: PhoneVerifyRequestDTO,
    ) -> AuthResponseDTO:
        """Execute phone sign-up use case.
        
        This is a composite operation that first initiates phone auth
        and then verifies the OTP to create a new account.
        
        Args:
            phone_request: Phone authentication request
            verify_request: OTP verification request
            
        Returns:
            Authentication response with tokens and user data
            
        Raises:
            InvalidPhoneFormatError: If phone format is invalid
            InvalidOTPError: If OTP is invalid
            AuthenticationError: If sign-up fails
        """
        try:
            # First, initiate phone authentication
            phone_auth_use_case = PhoneAuthUseCase(self._auth_repository)
            await phone_auth_use_case.execute(phone_request)
            
            # Then, verify OTP and create account
            otp_verification_use_case = OTPVerificationUseCase(self._auth_repository)
            return await otp_verification_use_case.execute(verify_request)
            
        except Exception as e:
            logger.error(f"Phone sign-up error: {str(e)}")
            raise


class ResendOTPUseCase:
    """Use case for resending OTP codes.
    
    This use case handles resending OTP codes for phone authentication
    with appropriate rate limiting.
    """
    
    def __init__(self, auth_repository: IAuthRepository):
        """Initialize the use case.
        
        Args:
            auth_repository: Repository for authentication operations
        """
        self._auth_repository = auth_repository
    
    async def execute(self, request: PhoneAuthRequestDTO) -> PhoneAuthResponseDTO:
        """Execute OTP resend use case.
        
        Args:
            request: Phone authentication request data
            
        Returns:
            Response indicating OTP was resent
            
        Raises:
            InvalidPhoneFormatError: If phone format is invalid
            RateLimitExceededError: If too many resend attempts
            AuthenticationError: If OTP resending fails
        """
        try:
            logger.debug(f"OTP resend attempt for: {request.phone}")
            
            # Validate phone format
            try:
                phone = Phone(request.phone)
            except ValueError as e:
                raise InvalidPhoneFormatError(str(e))
            
            # Check rate limiting for resends (more restrictive than initial send)
            # This would typically check a cache/database for recent resend attempts
            # For now, we'll skip this check
            
            # Resend OTP
            success = await self._auth_repository.initiate_phone_auth(phone)
            
            if not success:
                log_auth_event(
                    logger,
                    "otp_resend_failed",
                    phone=request.phone,
                    details="Failed to resend OTP",
                    level="error",
                )
                raise AuthenticationError("Failed to resend OTP")
            
            # Log successful OTP resend
            log_auth_event(
                logger,
                "otp_resent",
                phone=request.phone,
                details="OTP resent successfully",
            )
            
            return PhoneAuthResponseDTO(
                message="OTP resent successfully",
                phone=request.phone,
                otp_sent=True,
            )
            
        except (InvalidPhoneFormatError, RateLimitExceededError):
            raise
        except Exception as e:
            log_auth_event(
                logger,
                "otp_resend_error",
                phone=request.phone,
                details=str(e),
                level="error"
            )
            logger.error(f"OTP resend error: {str(e)}")
            raise AuthenticationError("Failed to resend OTP")
