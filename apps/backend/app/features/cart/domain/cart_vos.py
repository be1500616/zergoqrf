"""Cart value objects.

This module contains immutable value objects used throughout the cart domain.
Value objects encapsulate data and behavior without identity.
"""

import re
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID

from .cart_exceptions import InvalidQuantityError


class Money:
    """Immutable monetary value representation."""
    
    def __init__(self, amount: Decimal):
        """Initialize money value.
        
        Args:
            amount: Monetary amount
            
        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Money amount cannot be negative")
        self._amount = Decimal(str(amount))
    
    @property
    def amount(self) -> Decimal:
        """Get the monetary amount."""
        return self._amount
    
    def __add__(self, other: 'Money') -> 'Money':
        """Add two money values."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        return Money(self._amount + other._amount)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two money values."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        result = self._amount - other._amount
        if result < 0:
            raise ValueError("Money subtraction cannot result in negative amount")
        return Money(result)
    
    def __mul__(self, multiplier: int) -> 'Money':
        """Multiply money by an integer."""
        if not isinstance(multiplier, int) or multiplier < 0:
            raise TypeError("Money can only be multiplied by non-negative integers")
        return Money(self._amount * multiplier)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another Money object."""
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount
    
    def __str__(self) -> str:
        """String representation of money."""
        return f"${self._amount:.2f}"
    
    def __repr__(self) -> str:
        """Developer representation of money."""
        return f"Money({self._amount})"


class Quantity:
    """Represents item quantities with positive validation."""
    
    def __init__(self, value: int):
        """Initialize quantity.
        
        Args:
            value: Quantity value
            
        Raises:
            InvalidQuantityError: If quantity is not positive
        """
        if not isinstance(value, int) or value <= 0:
            raise InvalidQuantityError(value)
        self._value = value
    
    @property
    def value(self) -> int:
        """Get the quantity value."""
        return self._value
    
    def __add__(self, other: 'Quantity') -> 'Quantity':
        """Add two quantities."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only add Quantity to Quantity")
        return Quantity(self._value + other._value)
    
    def __sub__(self, other: 'Quantity') -> 'Quantity':
        """Subtract two quantities."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only subtract Quantity from Quantity")
        result = self._value - other._value
        if result <= 0:
            raise InvalidQuantityError(result)
        return Quantity(result)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another Quantity object."""
        if not isinstance(other, Quantity):
            return False
        return self._value == other._value
    
    def __lt__(self, other: 'Quantity') -> bool:
        """Check if this quantity is less than another."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only compare Quantity with Quantity")
        return self._value < other._value
    
    def __le__(self, other: 'Quantity') -> bool:
        """Check if this quantity is less than or equal to another."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only compare Quantity with Quantity")
        return self._value <= other._value
    
    def __gt__(self, other: 'Quantity') -> bool:
        """Check if this quantity is greater than another."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only compare Quantity with Quantity")
        return self._value > other._value
    
    def __ge__(self, other: 'Quantity') -> bool:
        """Check if this quantity is greater than or equal to another."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only compare Quantity with Quantity")
        return self._value >= other._value
    
    def __str__(self) -> str:
        """String representation of quantity."""
        return str(self._value)
    
    def __repr__(self) -> str:
        """Developer representation of quantity."""
        return f"Quantity({self._value})"


class CartSessionToken:
    """Represents a cart session token with validation."""
    
    def __init__(self, token: str):
        """Initialize cart session token.
        
        Args:
            token: Session token string
            
        Raises:
            ValueError: If token is invalid
        """
        if not token or not isinstance(token, str):
            raise ValueError("Token must be a non-empty string")
        
        # Basic token validation - should be base64-like string
        if len(token) < 8:
            raise ValueError("Token must be at least 8 characters long")
        
        self._token = token
    
    @property
    def value(self) -> str:
        """Get the token value."""
        return self._token
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another CartSessionToken."""
        if not isinstance(other, CartSessionToken):
            return False
        return self._token == other._token
    
    def __str__(self) -> str:
        """String representation of token (masked for security)."""
        return f"{self._token[:8]}..."
    
    def __repr__(self) -> str:
        """Developer representation of token."""
        return f"CartSessionToken({self._token[:8]}...)"


class CustomizationOptions:
    """Represents menu item customizations."""
    
    def __init__(self, options: Dict[str, Any] = None):
        """Initialize customization options.
        
        Args:
            options: Dictionary of customization options
        """
        self._options = dict(options) if options else {}
    
    @property
    def options(self) -> Dict[str, Any]:
        """Get the customization options."""
        return self._options.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a customization option value.
        
        Args:
            key: Option key
            default: Default value if key not found
            
        Returns:
            Option value or default
        """
        return self._options.get(key, default)
    
    def has_option(self, key: str) -> bool:
        """Check if customization option exists.
        
        Args:
            key: Option key to check
            
        Returns:
            True if option exists, False otherwise
        """
        return key in self._options
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another CustomizationOptions."""
        if not isinstance(other, CustomizationOptions):
            return False
        return self._options == other._options
    
    def __str__(self) -> str:
        """String representation of customizations."""
        if not self._options:
            return "No customizations"
        return f"Customizations: {self._options}"
    
    def __repr__(self) -> str:
        """Developer representation of customizations."""
        return f"CustomizationOptions({self._options})"
