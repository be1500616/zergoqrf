"""Supabase authentication repository implementation.

This module provides concrete implementation of authentication repository
interfaces using Supabase as the authentication provider.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from supabase import Client

from ..domain.auth_entities import User, AuthSession, AuthenticationResult
from ..domain.auth_repos import IAuthRepository
from ..domain.auth_vos import Email, Phone, Token, OTPCode
from ..domain.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    InvalidOTPError,
    OTPExpiredError,
    TokenExpiredError,
    InvalidTokenError,
)

logger = logging.getLogger(__name__)


class SupabaseAuthRepository(IAuthRepository):
    """Concrete implementation of authentication repository using Supabase.
    
    This repository handles all authentication operations by delegating
    to Supabase's authentication service.
    """
    
    def __init__(self, supabase_client: Client):
        """Initialize the repository.
        
        Args:
            supabase_client: Supabase client instance
        """
        self._supabase = supabase_client
    
    async def sign_in_with_email(self, email: Email, password: str) -> AuthenticationResult:
        """Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Authentication result with user and session data
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            logger.debug(f"Attempting email sign-in for: {email.value}")
            
            # Use Supabase authentication
            auth_response = self._supabase.auth.sign_in_with_password(
                {"email": email.value, "password": password}
            )
            
            if not auth_response.user or not auth_response.session:
                return AuthenticationResult(
                    success=False,
                    error_message="Invalid email or password"
                )
            
            # Convert Supabase response to domain entities
            user = self._convert_supabase_user_to_entity(auth_response.user)
            session = self._convert_supabase_session_to_entity(auth_response.session, user.user_id)
            
            return AuthenticationResult(
                success=True,
                user=user,
                session=session
            )
            
        except Exception as e:
            logger.error(f"Email sign-in error: {str(e)}")
            return AuthenticationResult(
                success=False,
                error_message=f"Authentication failed: {str(e)}"
            )
    
    async def sign_up_with_email(
        self,
        email: Email,
        password: str,
        name: Optional[str] = None,
        role: str = "customer",
        restaurant_id: Optional[str] = None,
    ) -> AuthenticationResult:
        """Create new user account with email and password.
        
        Args:
            email: User's email address
            password: User's password
            name: User's display name
            role: User's role in the system
            restaurant_id: Associated restaurant ID
            
        Returns:
            Authentication result with user and session data
            
        Raises:
            AuthenticationError: If account creation fails
        """
        try:
            logger.debug(f"Attempting email sign-up for: {email.value}")
            
            # Prepare user metadata
            user_data = {
                "name": name,
                "role": role,
            }
            
            if restaurant_id:
                user_data["restaurant_id"] = restaurant_id
            
            # Use Supabase authentication
            auth_response = self._supabase.auth.sign_up(
                {
                    "email": email.value,
                    "password": password,
                    "options": {"data": user_data},
                }
            )
            
            if not auth_response.user:
                return AuthenticationResult(
                    success=False,
                    error_message="Failed to create user account"
                )
            
            # Convert Supabase response to domain entities
            user = self._convert_supabase_user_to_entity(auth_response.user)
            session = None
            
            # If session exists (no email confirmation required)
            if auth_response.session:
                session = self._convert_supabase_session_to_entity(
                    auth_response.session, user.user_id
                )
            
            return AuthenticationResult(
                success=True,
                user=user,
                session=session,
                requires_verification=session is None
            )
            
        except Exception as e:
            logger.error(f"Email sign-up error: {str(e)}")
            return AuthenticationResult(
                success=False,
                error_message=f"Account creation failed: {str(e)}"
            )
    
    async def initiate_phone_auth(self, phone: Phone) -> bool:
        """Initiate phone authentication by sending OTP.
        
        Args:
            phone: User's phone number
            
        Returns:
            True if OTP was sent successfully
            
        Raises:
            AuthenticationError: If OTP sending fails
        """
        try:
            logger.debug(f"Initiating phone auth for: {phone.value}")
            
            # Use Supabase's phone OTP
            auth_response = self._supabase.auth.sign_in_with_otp({"phone": phone.value})
            
            # Supabase doesn't return a clear success indicator for OTP sending
            # We assume success if no exception is raised
            return True
            
        except Exception as e:
            logger.error(f"Phone OTP initiation error: {str(e)}")
            raise AuthenticationError(f"Failed to send OTP: {str(e)}")
    
    async def verify_phone_otp(
        self,
        phone: Phone,
        otp_code: OTPCode,
        name: Optional[str] = None,
    ) -> AuthenticationResult:
        """Verify phone OTP and complete authentication.
        
        Args:
            phone: User's phone number
            otp_code: OTP code to verify
            name: User's display name (for new users)
            
        Returns:
            Authentication result with user and session data
            
        Raises:
            AuthenticationError: If OTP verification fails
        """
        try:
            logger.debug(f"Verifying OTP for phone: {phone.value}")
            
            # Verify OTP with Supabase
            auth_response = self._supabase.auth.verify_otp(
                {"phone": phone.value, "token": otp_code.value, "type": "sms"}
            )
            
            if not auth_response.user or not auth_response.session:
                return AuthenticationResult(
                    success=False,
                    error_message="Invalid or expired OTP"
                )
            
            # Update user metadata if name provided and not already set
            if name and not auth_response.user.user_metadata.get("name"):
                self._supabase.auth.update_user({"data": {"name": name}})
            
            # Convert Supabase response to domain entities
            user = self._convert_supabase_user_to_entity(auth_response.user)
            session = self._convert_supabase_session_to_entity(
                auth_response.session, user.user_id
            )
            
            return AuthenticationResult(
                success=True,
                user=user,
                session=session
            )
            
        except Exception as e:
            logger.error(f"Phone OTP verification error: {str(e)}")
            return AuthenticationResult(
                success=False,
                error_message=f"OTP verification failed: {str(e)}"
            )
    
    async def refresh_session(self, refresh_token: Token) -> AuthenticationResult:
        """Refresh user session using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Authentication result with new tokens
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        try:
            logger.debug("Attempting token refresh")
            
            # Use Supabase token refresh
            auth_response = self._supabase.auth.refresh_session(refresh_token.value)
            
            if not auth_response.session:
                return AuthenticationResult(
                    success=False,
                    error_message="Invalid refresh token"
                )
            
            # Convert Supabase response to domain entities
            user = None
            if auth_response.user:
                user = self._convert_supabase_user_to_entity(auth_response.user)
            
            session = self._convert_supabase_session_to_entity(
                auth_response.session,
                user.user_id if user else ""
            )
            
            return AuthenticationResult(
                success=True,
                user=user,
                session=session
            )
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return AuthenticationResult(
                success=False,
                error_message=f"Token refresh failed: {str(e)}"
            )
    
    async def sign_out(self, user_id: str) -> bool:
        """Sign out user and invalidate session.
        
        Args:
            user_id: ID of the user to sign out
            
        Returns:
            True if sign out was successful
        """
        try:
            logger.debug(f"Signing out user: {user_id}")
            
            # Use Supabase sign out
            self._supabase.auth.sign_out()
            
            return True
            
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            # Don't fail sign out - it should always succeed from user perspective
            return True
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by their ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User entity if found, None otherwise
        """
        try:
            # This would typically query the users table or use Supabase admin API
            # For now, we'll return None as this requires additional implementation
            logger.debug(f"Getting user by ID: {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Get user by ID error: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: Email) -> Optional[User]:
        """Get user by their email address.
        
        Args:
            email: User's email address
            
        Returns:
            User entity if found, None otherwise
        """
        try:
            # This would typically query the users table
            # For now, we'll return None as this requires additional implementation
            logger.debug(f"Getting user by email: {email.value}")
            return None
            
        except Exception as e:
            logger.error(f"Get user by email error: {str(e)}")
            return None
    
    async def get_user_by_phone(self, phone: Phone) -> Optional[User]:
        """Get user by their phone number.
        
        Args:
            phone: User's phone number
            
        Returns:
            User entity if found, None otherwise
        """
        try:
            # This would typically query the users table
            # For now, we'll return None as this requires additional implementation
            logger.debug(f"Getting user by phone: {phone.value}")
            return None
            
        except Exception as e:
            logger.error(f"Get user by phone error: {str(e)}")
            return None
    
    async def update_user_metadata(
        self,
        user_id: str,
        metadata: Dict[str, Any],
    ) -> bool:
        """Update user metadata.
        
        Args:
            user_id: User's unique identifier
            metadata: Metadata to update
            
        Returns:
            True if update was successful
        """
        try:
            logger.debug(f"Updating metadata for user: {user_id}")
            
            # Use Supabase user update
            self._supabase.auth.update_user({"data": metadata})
            
            return True
            
        except Exception as e:
            logger.error(f"Update user metadata error: {str(e)}")
            return False
    
    def _convert_supabase_user_to_entity(self, supabase_user) -> User:
        """Convert Supabase user to domain User entity.
        
        Args:
            supabase_user: Supabase user object
            
        Returns:
            User domain entity
        """
        user_metadata = supabase_user.user_metadata or {}
        
        # Convert email and phone to value objects if they exist
        email = Email(supabase_user.email) if supabase_user.email else None
        phone = Phone(supabase_user.phone) if supabase_user.phone else None
        
        return User(
            user_id=supabase_user.id,
            email=email,
            phone=phone,
            name=user_metadata.get("name"),
            role=user_metadata.get("role", "customer"),
            restaurant_id=user_metadata.get("restaurant_id"),
            permissions=user_metadata.get("permissions", {}),
            is_active=True,  # Supabase users are active by default
            is_anonymous=False,
            created_at=datetime.fromisoformat(supabase_user.created_at.replace('Z', '+00:00')) if supabase_user.created_at else None,
            updated_at=datetime.fromisoformat(supabase_user.updated_at.replace('Z', '+00:00')) if supabase_user.updated_at else None,
        )
    
    def _convert_supabase_session_to_entity(self, supabase_session, user_id: str) -> AuthSession:
        """Convert Supabase session to domain AuthSession entity.
        
        Args:
            supabase_session: Supabase session object
            user_id: User ID for the session
            
        Returns:
            AuthSession domain entity
        """
        access_token = Token(supabase_session.access_token, token_type="bearer")
        refresh_token = Token(supabase_session.refresh_token, token_type="refresh") if supabase_session.refresh_token else None
        
        return AuthSession(
            session_id=f"session_{user_id}_{datetime.utcnow().timestamp()}",  # Generate session ID
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow().replace(microsecond=0) if supabase_session.expires_in else None,
            is_anonymous=False,
            created_at=datetime.utcnow(),
        )
