"""Authentication value objects.

This module defines immutable value objects for the authentication domain.
Value objects represent concepts that are defined by their attributes rather
than their identity.
"""

import re
from datetime import datetime
from typing import Optional


class Email:
    """Email value object representing a validated email address.
    
    This value object ensures email addresses are properly formatted
    and provides email-specific behavior.
    """
    
    def __init__(self, value: str):
        """Initialize an email value object.
        
        Args:
            value: The email address string
            
        Raises:
            ValueError: If the email format is invalid
        """
        if not self._is_valid_email(value):
            raise ValueError(f"Invalid email format: {value}")
        self._value = value.lower().strip()
    
    @property
    def value(self) -> str:
        """Get the email address value.
        
        Returns:
            The email address as a string
        """
        return self._value
    
    @property
    def domain(self) -> str:
        """Get the domain part of the email address.
        
        Returns:
            The domain portion of the email
        """
        return self._value.split("@")[1]
    
    @property
    def local_part(self) -> str:
        """Get the local part of the email address.
        
        Returns:
            The local portion of the email (before @)
        """
        return self._value.split("@")[0]
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex.
        
        Args:
            email: Email string to validate
            
        Returns:
            True if email format is valid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        """String representation of the email."""
        return self._value
    
    def __eq__(self, other) -> bool:
        """Check equality with another email."""
        if not isinstance(other, Email):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Hash function for email."""
        return hash(self._value)


class Phone:
    """Phone number value object representing a validated phone number.
    
    This value object ensures phone numbers are properly formatted
    in international format and provides phone-specific behavior.
    """
    
    def __init__(self, value: str):
        """Initialize a phone value object.
        
        Args:
            value: The phone number string
            
        Raises:
            ValueError: If the phone format is invalid
        """
        if not self._is_valid_phone(value):
            raise ValueError(f"Invalid phone format: {value}")
        self._value = value.strip()
    
    @property
    def value(self) -> str:
        """Get the phone number value.
        
        Returns:
            The phone number as a string
        """
        return self._value
    
    @property
    def country_code(self) -> str:
        """Get the country code from the phone number.
        
        Returns:
            The country code (including +)
        """
        # Simple extraction - in a real system, you'd use a proper phone library
        if self._value.startswith("+1"):
            return "+1"
        elif self._value.startswith("+44"):
            return "+44"
        elif self._value.startswith("+91"):
            return "+91"
        # Add more country codes as needed
        return self._value[:3]  # Default to first 3 characters
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone format using regex.
        
        Args:
            phone: Phone string to validate
            
        Returns:
            True if phone format is valid (international format)
        """
        # International format: +[country code][number]
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))
    
    def __str__(self) -> str:
        """String representation of the phone number."""
        return self._value
    
    def __eq__(self, other) -> bool:
        """Check equality with another phone number."""
        if not isinstance(other, Phone):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Hash function for phone number."""
        return hash(self._value)


class Token:
    """Token value object representing a JWT or session token.
    
    This value object encapsulates token data and provides
    token-specific behavior and validation.
    """
    
    def __init__(
        self,
        value: str,
        token_type: str = "bearer",
        expires_at: Optional[datetime] = None,
    ):
        """Initialize a token value object.
        
        Args:
            value: The token string
            token_type: Type of token (bearer, refresh, etc.)
            expires_at: When the token expires
            
        Raises:
            ValueError: If the token is empty or invalid
        """
        if not value or not value.strip():
            raise ValueError("Token value cannot be empty")
        self._value = value.strip()
        self._token_type = token_type.lower()
        self._expires_at = expires_at
    
    @property
    def value(self) -> str:
        """Get the token value.
        
        Returns:
            The token string
        """
        return self._value
    
    @property
    def token_type(self) -> str:
        """Get the token type.
        
        Returns:
            The token type (bearer, refresh, etc.)
        """
        return self._token_type
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Get the token expiration time.
        
        Returns:
            The expiration datetime or None if no expiration
        """
        return self._expires_at
    
    def is_expired(self) -> bool:
        """Check if the token has expired.
        
        Returns:
            True if the token has expired
        """
        if self._expires_at is None:
            return False
        return datetime.utcnow() > self._expires_at
    
    def is_valid(self) -> bool:
        """Check if the token is valid (not expired).
        
        Returns:
            True if the token is valid
        """
        return not self.is_expired()
    
    def __str__(self) -> str:
        """String representation of the token (masked for security)."""
        if len(self._value) > 10:
            return f"{self._value[:4]}...{self._value[-4:]}"
        return "***"
    
    def __eq__(self, other) -> bool:
        """Check equality with another token."""
        if not isinstance(other, Token):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Hash function for token."""
        return hash(self._value)


class OTPCode:
    """OTP (One-Time Password) value object.
    
    This value object represents a one-time password used for
    phone number verification and other authentication flows.
    """
    
    def __init__(self, value: str):
        """Initialize an OTP code value object.
        
        Args:
            value: The OTP code string
            
        Raises:
            ValueError: If the OTP format is invalid
        """
        if not self._is_valid_otp(value):
            raise ValueError(f"Invalid OTP format: {value}")
        self._value = value.strip()
    
    @property
    def value(self) -> str:
        """Get the OTP code value.
        
        Returns:
            The OTP code as a string
        """
        return self._value
    
    def _is_valid_otp(self, otp: str) -> bool:
        """Validate OTP format.
        
        Args:
            otp: OTP string to validate
            
        Returns:
            True if OTP format is valid (6 digits)
        """
        return bool(re.match(r'^\d{6}$', otp.strip()))
    
    def __str__(self) -> str:
        """String representation of the OTP (masked for security)."""
        return "******"
    
    def __eq__(self, other) -> bool:
        """Check equality with another OTP code."""
        if not isinstance(other, OTPCode):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Hash function for OTP code."""
        return hash(self._value)


class SessionToken:
    """Session token value object for anonymous sessions.
    
    This value object represents session tokens used for
    anonymous user sessions in QR code flows.
    """
    
    def __init__(self, value: str, expires_at: Optional[datetime] = None):
        """Initialize a session token value object.
        
        Args:
            value: The session token string
            expires_at: When the token expires
            
        Raises:
            ValueError: If the token is empty
        """
        if not value or not value.strip():
            raise ValueError("Session token value cannot be empty")
        self._value = value.strip()
        self._expires_at = expires_at
    
    @property
    def value(self) -> str:
        """Get the session token value.
        
        Returns:
            The session token string
        """
        return self._value
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Get the token expiration time.
        
        Returns:
            The expiration datetime or None if no expiration
        """
        return self._expires_at
    
    def is_expired(self) -> bool:
        """Check if the session token has expired.
        
        Returns:
            True if the token has expired
        """
        if self._expires_at is None:
            return False
        return datetime.utcnow() > self._expires_at
    
    def is_valid(self) -> bool:
        """Check if the session token is valid.
        
        Returns:
            True if the token is valid
        """
        return not self.is_expired()
    
    def __str__(self) -> str:
        """String representation of the session token (masked)."""
        if len(self._value) > 8:
            return f"{self._value[:4]}...{self._value[-4:]}"
        return "***"
    
    def __eq__(self, other) -> bool:
        """Check equality with another session token."""
        if not isinstance(other, SessionToken):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Hash function for session token."""
        return hash(self._value)
