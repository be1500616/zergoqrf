"""Transaction Management Value Objects.

This module defines value objects for transaction management including
Money, TransactionNumber, and various status enums.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
import re


class Currency(str, Enum):
    """Supported currencies."""
    
    INR = "INR"
    USD = "USD"
    EUR = "EUR"


class PaymentMethod(str, Enum):
    """Supported payment methods."""
    
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    RAZORPAY = "razorpay"


class TransactionStatus(str, Enum):
    """Transaction status values."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class RefundStatus(str, Enum):
    """Refund status values."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PayoutStatus(str, Enum):
    """Payout status values."""
    
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Money:
    """Value object representing monetary amount with currency.
    
    This class ensures proper handling of monetary values with currency
    information and provides validation for financial calculations.
    """
    
    def __init__(self, amount: Decimal, currency: Currency = Currency.INR):
        """Initialize money value object.
        
        Args:
            amount: Monetary amount
            currency: Currency code
            
        Raises:
            ValueError: If amount is negative or invalid
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        if amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        # Round to 2 decimal places for currency precision
        self.amount = amount.quantize(Decimal('0.01'))
        self.currency = currency
    
    def __str__(self) -> str:
        """String representation of money."""
        return f"{self.currency.value} {self.amount}"
    
    def __repr__(self) -> str:
        """Detailed representation of money."""
        return f"Money(amount={self.amount}, currency={self.currency.value})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Money object."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other) -> bool:
        """Check if this money is less than another."""
        if not isinstance(other, Money):
            raise TypeError("Cannot compare Money with non-Money object")
        if self.currency != other.currency:
            raise ValueError("Cannot compare money with different currencies")
        return self.amount < other.amount
    
    def __le__(self, other) -> bool:
        """Check if this money is less than or equal to another."""
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        """Check if this money is greater than another."""
        return not self <= other
    
    def __ge__(self, other) -> bool:
        """Check if this money is greater than or equal to another."""
        return not self < other
    
    def add(self, other: 'Money') -> 'Money':
        """Add another money amount.
        
        Args:
            other: Money to add
            
        Returns:
            New Money object with sum
            
        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract another money amount.
        
        Args:
            other: Money to subtract
            
        Returns:
            New Money object with difference
            
        Raises:
            ValueError: If currencies don't match or result is negative
        """
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Cannot subtract more money than available")
        
        return Money(result_amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """Multiply money by a factor.
        
        Args:
            factor: Multiplication factor
            
        Returns:
            New Money object with product
        """
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        
        return Money(self.amount * factor, self.currency)
    
    def divide(self, divisor: Decimal) -> 'Money':
        """Divide money by a divisor.
        
        Args:
            divisor: Division divisor
            
        Returns:
            New Money object with quotient
            
        Raises:
            ValueError: If divisor is zero
        """
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        
        return Money(self.amount / divisor, self.currency)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "amount": float(self.amount),
            "currency": self.currency.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Money':
        """Create Money from dictionary.
        
        Args:
            data: Dictionary with amount and currency
            
        Returns:
            Money object
        """
        return cls(
            amount=Decimal(str(data["amount"])),
            currency=Currency(data["currency"])
        )
    
    @classmethod
    def zero(cls, currency: Currency = Currency.INR) -> 'Money':
        """Create zero money amount.
        
        Args:
            currency: Currency for zero amount
            
        Returns:
            Money object with zero amount
        """
        return cls(Decimal('0'), currency)


class TransactionNumber:
    """Value object for transaction numbers.
    
    Provides validation and generation of human-readable transaction numbers
    following the format: TXN-YYYYMMDD-XXXXXX
    """
    
    PATTERN = re.compile(r'^TXN-\d{8}-\d{6}$')
    
    def __init__(self, value: str):
        """Initialize transaction number.
        
        Args:
            value: Transaction number string
            
        Raises:
            ValueError: If format is invalid
        """
        if not self.PATTERN.match(value):
            raise ValueError(f"Invalid transaction number format: {value}")
        
        self.value = value
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"TransactionNumber('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, TransactionNumber):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.value)
    
    @classmethod
    def generate(cls) -> 'TransactionNumber':
        """Generate a new transaction number.
        
        Returns:
            New TransactionNumber object
            
        Note:
            In production, this should use the database function
            for proper sequence generation.
        """
        import random
        
        date_part = datetime.now().strftime('%Y%m%d')
        sequence_part = f"{random.randint(1, 999999):06d}"
        
        return cls(f"TXN-{date_part}-{sequence_part}")


class RefundNumber:
    """Value object for refund numbers.
    
    Provides validation and generation of human-readable refund numbers
    following the format: REF-YYYYMMDD-XXXXXX
    """
    
    PATTERN = re.compile(r'^REF-\d{8}-\d{6}$')
    
    def __init__(self, value: str):
        """Initialize refund number.
        
        Args:
            value: Refund number string
            
        Raises:
            ValueError: If format is invalid
        """
        if not self.PATTERN.match(value):
            raise ValueError(f"Invalid refund number format: {value}")
        
        self.value = value
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"RefundNumber('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, RefundNumber):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.value)
    
    @classmethod
    def generate(cls) -> 'RefundNumber':
        """Generate a new refund number.
        
        Returns:
            New RefundNumber object
        """
        import random
        
        date_part = datetime.now().strftime('%Y%m%d')
        sequence_part = f"{random.randint(1, 999999):06d}"
        
        return cls(f"REF-{date_part}-{sequence_part}")


class PayoutNumber:
    """Value object for payout numbers.
    
    Provides validation and generation of human-readable payout numbers
    following the format: PAY-YYYYMMDD-XXXXXX
    """
    
    PATTERN = re.compile(r'^PAY-\d{8}-\d{6}$')
    
    def __init__(self, value: str):
        """Initialize payout number.
        
        Args:
            value: Payout number string
            
        Raises:
            ValueError: If format is invalid
        """
        if not self.PATTERN.match(value):
            raise ValueError(f"Invalid payout number format: {value}")
        
        self.value = value
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"PayoutNumber('{self.value}')"
    
    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, PayoutNumber):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.value)
    
    @classmethod
    def generate(cls) -> 'PayoutNumber':
        """Generate a new payout number.
        
        Returns:
            New PayoutNumber object
        """
        import random
        
        date_part = datetime.now().strftime('%Y%m%d')
        sequence_part = f"{random.randint(1, 999999):06d}"
        
        return cls(f"PAY-{date_part}-{sequence_part}")
