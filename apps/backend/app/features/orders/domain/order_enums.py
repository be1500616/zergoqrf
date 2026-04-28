"""Order domain enumerations.

This module contains enumerations for order and payment status,
payment methods, and other domain-specific constants.
"""

from enum import Enum
from typing import List, Set


class OrderStatus(Enum):
    """Order status enumeration with state transition rules."""
    
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        """Check if transition to new status is valid."""
        valid_transitions = {
            OrderStatus.PLACED: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
            OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
            OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
            OrderStatus.READY: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
            OrderStatus.COMPLETED: set(),  # Terminal state
            OrderStatus.CANCELLED: set(),  # Terminal state
        }
        
        return new_status in valid_transitions.get(self, set())
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal status."""
        return self in {OrderStatus.COMPLETED, OrderStatus.CANCELLED}
    
    def is_active(self) -> bool:
        """Check if order is in active processing state."""
        return self in {
            OrderStatus.PLACED, 
            OrderStatus.CONFIRMED, 
            OrderStatus.PREPARING, 
            OrderStatus.READY
        }
    
    def requires_payment(self) -> bool:
        """Check if status requires payment to proceed."""
        return self == OrderStatus.PLACED
    
    @classmethod
    def get_valid_transitions(cls, current_status: 'OrderStatus') -> Set['OrderStatus']:
        """Get all valid transitions from current status."""
        if current_status == cls.PLACED:
            return {cls.CONFIRMED, cls.CANCELLED}
        elif current_status == cls.CONFIRMED:
            return {cls.PREPARING, cls.CANCELLED}
        elif current_status == cls.PREPARING:
            return {cls.READY, cls.CANCELLED}
        elif current_status == cls.READY:
            return {cls.COMPLETED, cls.CANCELLED}
        else:
            return set()


class PaymentStatus(Enum):
    """Payment status enumeration with validation rules."""
    
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_COLLECTED = "payment_collected"
    PAYMENT_FAILED = "payment_failed"
    
    def can_transition_to(self, new_status: 'PaymentStatus') -> bool:
        """Check if transition to new payment status is valid."""
        valid_transitions = {
            PaymentStatus.PAYMENT_PENDING: {
                PaymentStatus.PAYMENT_COLLECTED, 
                PaymentStatus.PAYMENT_FAILED
            },
            PaymentStatus.PAYMENT_COLLECTED: set(),  # Terminal state for cash payments
            PaymentStatus.PAYMENT_FAILED: {PaymentStatus.PAYMENT_PENDING},  # Can retry
        }
        
        return new_status in valid_transitions.get(self, set())
    
    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self == PaymentStatus.PAYMENT_COLLECTED
    
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self == PaymentStatus.PAYMENT_PENDING
    
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self == PaymentStatus.PAYMENT_FAILED
    
    def allows_order_preparation(self) -> bool:
        """Check if payment status allows order preparation."""
        return self == PaymentStatus.PAYMENT_COLLECTED


class PaymentMethod(Enum):
    """Payment method enumeration (extensible for future digital payments)."""
    
    CASH = "cash"
    RAZORPAY = "razorpay"  # For future Story 6.1
    UPI = "upi"           # For future Story 6.1
    CARD = "card"         # For future Story 6.1
    
    def is_digital(self) -> bool:
        """Check if payment method is digital."""
        return self in {PaymentMethod.RAZORPAY, PaymentMethod.UPI, PaymentMethod.CARD}
    
    def is_cash(self) -> bool:
        """Check if payment method is cash."""
        return self == PaymentMethod.CASH
    
    def requires_gateway(self) -> bool:
        """Check if payment method requires payment gateway."""
        return self.is_digital()
    
    def supports_instant_confirmation(self) -> bool:
        """Check if payment method supports instant confirmation."""
        return self == PaymentMethod.CASH  # Cash is confirmed by staff immediately
    
    @classmethod
    def get_available_methods(cls) -> List['PaymentMethod']:
        """Get currently available payment methods."""
        # For Story 3.3, only cash is available
        return [cls.CASH]
    
    @classmethod
    def get_future_methods(cls) -> List['PaymentMethod']:
        """Get payment methods planned for future releases."""
        return [cls.RAZORPAY, cls.UPI, cls.CARD]


class OrderPriority(Enum):
    """Order priority enumeration for restaurant operations."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    
    def get_preparation_time_multiplier(self) -> float:
        """Get preparation time multiplier based on priority."""
        multipliers = {
            OrderPriority.LOW: 1.2,      # 20% longer
            OrderPriority.NORMAL: 1.0,   # Standard time
            OrderPriority.HIGH: 0.8,     # 20% faster
            OrderPriority.URGENT: 0.6,   # 40% faster
        }
        return multipliers[self]
    
    def get_display_color(self) -> str:
        """Get display color for restaurant console."""
        colors = {
            OrderPriority.LOW: "#6B7280",      # Gray
            OrderPriority.NORMAL: "#3B82F6",   # Blue
            OrderPriority.HIGH: "#F59E0B",     # Amber
            OrderPriority.URGENT: "#EF4444",   # Red
        }
        return colors[self]


class OrderSource(Enum):
    """Order source enumeration for tracking and analytics."""
    
    QR_CODE = "qr_code"           # Customer scanned QR code at table
    STAFF_ASSISTED = "staff_assisted"  # Staff helped customer place order
    PHONE_ORDER = "phone_order"   # Order placed via phone call
    WALK_IN = "walk_in"          # Customer walked in and ordered
    
    def is_self_service(self) -> bool:
        """Check if order source is self-service."""
        return self == OrderSource.QR_CODE
    
    def requires_staff_assistance(self) -> bool:
        """Check if order source requires staff assistance."""
        return self in {OrderSource.STAFF_ASSISTED, OrderSource.PHONE_ORDER}


class CancellationReason(Enum):
    """Order cancellation reason enumeration."""
    
    CUSTOMER_REQUEST = "customer_request"
    ITEM_UNAVAILABLE = "item_unavailable"
    PAYMENT_FAILED = "payment_failed"
    KITCHEN_ISSUE = "kitchen_issue"
    SYSTEM_ERROR = "system_error"
    DUPLICATE_ORDER = "duplicate_order"
    
    def is_customer_initiated(self) -> bool:
        """Check if cancellation was initiated by customer."""
        return self == CancellationReason.CUSTOMER_REQUEST
    
    def is_restaurant_initiated(self) -> bool:
        """Check if cancellation was initiated by restaurant."""
        return self in {
            CancellationReason.ITEM_UNAVAILABLE,
            CancellationReason.KITCHEN_ISSUE,
            CancellationReason.DUPLICATE_ORDER
        }
    
    def is_system_initiated(self) -> bool:
        """Check if cancellation was initiated by system."""
        return self in {
            CancellationReason.PAYMENT_FAILED,
            CancellationReason.SYSTEM_ERROR
        }
    
    def allows_refund(self) -> bool:
        """Check if cancellation reason allows refund."""
        return self in {
            CancellationReason.ITEM_UNAVAILABLE,
            CancellationReason.KITCHEN_ISSUE,
            CancellationReason.SYSTEM_ERROR,
            CancellationReason.DUPLICATE_ORDER
        }
