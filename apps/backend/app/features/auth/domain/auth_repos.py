"""Authentication repository interfaces.

This module defines abstract interfaces for authentication data access.
These interfaces define contracts that must be implemented by the
infrastructure layer without exposing implementation details.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from .auth_entities import User, AuthSession, AnonymousSession, AuthenticationResult
from .auth_vos import Email, Phone, Token, OTPCode, SessionToken


class IAuthRepository(ABC):
    """Abstract interface for authentication operations.
    
    This interface defines the contract for authentication-related
    data access operations without specifying implementation details.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def initiate_phone_auth(self, phone: Phone) -> bool:
        """Initiate phone authentication by sending OTP.
        
        Args:
            phone: User's phone number
            
        Returns:
            True if OTP was sent successfully
            
        Raises:
            AuthenticationError: If OTP sending fails
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def refresh_session(self, refresh_token: Token) -> AuthenticationResult:
        """Refresh user session using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Authentication result with new tokens
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        pass
    
    @abstractmethod
    async def sign_out(self, user_id: str) -> bool:
        """Sign out user and invalidate session.
        
        Args:
            user_id: ID of the user to sign out
            
        Returns:
            True if sign out was successful
        """
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by their ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: Email) -> Optional[User]:
        """Get user by their email address.
        
        Args:
            email: User's email address
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_by_phone(self, phone: Phone) -> Optional[User]:
        """Get user by their phone number.
        
        Args:
            phone: User's phone number
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
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
        pass


class ISessionRepository(ABC):
    """Abstract interface for session management operations.
    
    This interface defines the contract for session-related
    data access operations.
    """
    
    @abstractmethod
    async def create_anonymous_session(
        self,
        restaurant_id: str,
        table_id: Optional[str] = None,
        expires_hours: int = 24,
    ) -> AnonymousSession:
        """Create an anonymous session for QR code users.
        
        Args:
            restaurant_id: Associated restaurant ID
            table_id: Associated table ID (optional)
            expires_hours: Session expiration in hours
            
        Returns:
            Created anonymous session
            
        Raises:
            AuthenticationError: If session creation fails
        """
        pass
    
    @abstractmethod
    async def validate_anonymous_session(self, session_token: SessionToken) -> bool:
        """Validate an anonymous session token.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            True if session is valid
        """
        pass
    
    @abstractmethod
    async def get_anonymous_session(self, session_id: str) -> Optional[AnonymousSession]:
        """Get anonymous session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Anonymous session if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def invalidate_anonymous_session(self, session_id: str) -> bool:
        """Invalidate an anonymous session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if invalidation was successful
        """
        pass
    
    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired anonymous sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        pass


class ITokenRepository(ABC):
    """Abstract interface for token management operations.
    
    This interface defines the contract for token-related
    data access operations.
    """
    
    @abstractmethod
    async def validate_token(self, token: Token) -> Optional[Dict[str, Any]]:
        """Validate a JWT token and extract claims.
        
        Args:
            token: Token to validate
            
        Returns:
            Token claims if valid, None otherwise
        """
        pass
    
    @abstractmethod
    async def extract_user_context(self, token: Token) -> Optional[Dict[str, Any]]:
        """Extract user context from a valid token.
        
        Args:
            token: Valid JWT token
            
        Returns:
            User context data if token is valid, None otherwise
        """
        pass
    
    @abstractmethod
    async def is_token_blacklisted(self, token: Token) -> bool:
        """Check if a token is blacklisted.
        
        Args:
            token: Token to check
            
        Returns:
            True if token is blacklisted
        """
        pass
    
    @abstractmethod
    async def blacklist_token(self, token: Token) -> bool:
        """Add a token to the blacklist.
        
        Args:
            token: Token to blacklist
            
        Returns:
            True if blacklisting was successful
        """
        pass


class IUserRepository(ABC):
    """Abstract interface for user management operations.
    
    This interface defines the contract for user-related
    data access operations beyond authentication.
    """
    
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user.
        
        Args:
            user: User entity to create
            
        Returns:
            Created user entity
            
        Raises:
            AuthenticationError: If user creation fails
        """
        pass
    
    @abstractmethod
    async def update_user(self, user: User) -> User:
        """Update an existing user.
        
        Args:
            user: User entity with updated data
            
        Returns:
            Updated user entity
            
        Raises:
            AuthenticationError: If user update fails
        """
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account.
        
        Args:
            user_id: ID of the user to activate
            
        Returns:
            True if activation was successful
        """
        pass
    
    @abstractmethod
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account.
        
        Args:
            user_id: ID of the user to deactivate
            
        Returns:
            True if deactivation was successful
        """
        pass
