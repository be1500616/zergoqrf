"""Order value objects.

This module contains immutable value objects for the order domain,
representing concepts like money, order numbers, and payment references.
"""

import re
from decimal import Decimal
from typing import Dict, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Immutable monetary value representation."""
    
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        """Validate money constraints."""
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """Multiply money by a factor."""
        return Money(self.amount * factor, self.currency)
    
    def __str__(self) -> str:
        """String representation of money."""
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True)
class OrderNumber:
    """Immutable order number value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate order number format."""
        if not self.value:
            raise ValueError("Order number cannot be empty")
        
        # Validate format: ORD-YYYYMMDD-XXXX
        pattern = r'^ORD-\d{8}-\d{4}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid order number format: {self.value}")
    
    def __str__(self) -> str:
        """String representation of order number."""
        return self.value


@dataclass(frozen=True)
class PaymentReference:
    """Immutable payment reference value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate payment reference format."""
        if not self.value:
            raise ValueError("Payment reference cannot be empty")
        
        # Validate format: PAY-YYYYMMDD-HHMMSS-XXX
        pattern = r'^PAY-\d{8}-\d{6}-\d{3}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid payment reference format: {self.value}")
    
    def __str__(self) -> str:
        """String representation of payment reference."""
        return self.value


@dataclass(frozen=True)
class CustomerInfo:
    """Immutable customer information value object."""
    
    name: str
    phone: str
    email: str = None
    
    def __post_init__(self):
        """Validate customer information."""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Customer name must be at least 2 characters")
        
        # Validate Indian phone number format
        phone_pattern = r'^\+91[6-9]\d{9}$'
        if not re.match(phone_pattern, self.phone):
            raise ValueError(f"Invalid Indian phone number format: {self.phone}")
        
        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Invalid email format: {self.email}")
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None


@dataclass(frozen=True)
class GSTCalculation:
    """Immutable GST calculation value object."""
    
    subtotal: Money
    gst_rate: Decimal
    gst_amount: Money
    total_amount: Money
    
    def __post_init__(self):
        """Validate GST calculation."""
        if self.gst_rate < 0 or self.gst_rate > 1:
            raise ValueError("GST rate must be between 0 and 1")
        
        expected_gst = self.subtotal.multiply(self.gst_rate)
        if abs(self.gst_amount.amount - expected_gst.amount) > Decimal('0.01'):
            raise ValueError("GST amount calculation is incorrect")
        
        expected_total = self.subtotal.add(self.gst_amount)
        if abs(self.total_amount.amount - expected_total.amount) > Decimal('0.01'):
            raise ValueError("Total amount calculation is incorrect")
    
    @classmethod
    def calculate(cls, subtotal: Money, gst_rate: Decimal = Decimal('0.05')) -> 'GSTCalculation':
        """Calculate GST for Indian restaurant services (5%)."""
        gst_amount = subtotal.multiply(gst_rate)
        total_amount = subtotal.add(gst_amount)
        
        return cls(
            subtotal=subtotal,
            gst_rate=gst_rate,
            gst_amount=gst_amount,
            total_amount=total_amount
        )


@dataclass(frozen=True)
class OrderCustomizations:
    """Immutable order customizations value object."""
    
    customizations: Dict[str, Any]
    
    def __post_init__(self):
        """Validate customizations."""
        if not isinstance(self.customizations, dict):
            raise ValueError("Customizations must be a dictionary")
        
        # Ensure all keys are strings
        for key in self.customizations.keys():
            if not isinstance(key, str):
                raise ValueError("All customization keys must be strings")
    
    def get(self, key: str, default=None):
        """Get customization value."""
        return self.customizations.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if customization exists."""
        return key in self.customizations
    
    def __len__(self) -> int:
        """Get number of customizations."""
        return len(self.customizations)


@dataclass(frozen=True)
class Quantity:
    """Immutable quantity value object."""
    
    value: int
    
    def __post_init__(self):
        """Validate quantity constraints."""
        if self.value <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.value > 50:  # Business rule: max 50 items per order item
            raise ValueError("Quantity cannot exceed 50 per item")
    
    def add(self, other: 'Quantity') -> 'Quantity':
        """Add two quantities."""
        return Quantity(self.value + other.value)
    
    def multiply_money(self, money: Money) -> Money:
        """Multiply money by quantity."""
        return Money(money.amount * self.value, money.currency)
    
    def __str__(self) -> str:
        """String representation of quantity."""
        return str(self.value)


@dataclass(frozen=True)
class PreparationTime:
    """Immutable preparation time value object."""
    
    minutes: int
    
    def __post_init__(self):
        """Validate preparation time."""
        if self.minutes < 0:
            raise ValueError("Preparation time cannot be negative")
        
        if self.minutes > 480:  # Max 8 hours
            raise ValueError("Preparation time cannot exceed 8 hours")
    
    def add_minutes(self, additional_minutes: int) -> 'PreparationTime':
        """Add additional preparation time."""
        return PreparationTime(self.minutes + additional_minutes)
    
    def __str__(self) -> str:
        """String representation of preparation time."""
        if self.minutes < 60:
            return f"{self.minutes} minutes"
        else:
            hours = self.minutes // 60
            remaining_minutes = self.minutes % 60
            if remaining_minutes == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours}h {remaining_minutes}m"
