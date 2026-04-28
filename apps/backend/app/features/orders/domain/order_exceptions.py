"""Order domain exceptions.

This module contains custom exceptions for the order domain,
providing specific error types for different business rule violations.
"""

from typing import Optional, Any
from uuid import UUID


class OrderDomainError(Exception):
    """Base exception for all order domain errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """Initialize order domain error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


class OrderNotFoundError(OrderDomainError):
    """Raised when an order cannot be found."""
    
    def __init__(self, order_id: UUID = None, order_number: str = None):
        """Initialize order not found error."""
        if order_id:
            message = f"Order with ID {order_id} not found"
            details = {"order_id": str(order_id)}
        elif order_number:
            message = f"Order {order_number} not found"
            details = {"order_number": order_number}
        else:
            message = "Order not found"
            details = {}
        
        super().__init__(message, "ORDER_NOT_FOUND", details)


class OrderAlreadyExistsError(OrderDomainError):
    """Raised when attempting to create a duplicate order."""
    
    def __init__(self, order_number: str):
        """Initialize order already exists error."""
        message = f"Order {order_number} already exists"
        details = {"order_number": order_number}
        super().__init__(message, "ORDER_ALREADY_EXISTS", details)


class InvalidOrderStatusTransitionError(OrderDomainError):
    """Raised when an invalid order status transition is attempted."""
    
    def __init__(self, current_status: str, new_status: str, order_id: UUID = None):
        """Initialize invalid status transition error."""
        message = f"Cannot transition order from {current_status} to {new_status}"
        details = {
            "current_status": current_status,
            "new_status": new_status,
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "INVALID_ORDER_STATUS_TRANSITION", details)


class InvalidPaymentStatusTransitionError(OrderDomainError):
    """Raised when an invalid payment status transition is attempted."""
    
    def __init__(self, current_status: str, new_status: str, order_id: UUID = None):
        """Initialize invalid payment status transition error."""
        message = f"Cannot transition payment from {current_status} to {new_status}"
        details = {
            "current_payment_status": current_status,
            "new_payment_status": new_status,
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "INVALID_PAYMENT_STATUS_TRANSITION", details)


class OrderAlreadyCancelledException(OrderDomainError):
    """Raised when attempting to modify a cancelled order."""
    
    def __init__(self, order_id: UUID, order_number: str = None):
        """Initialize order already cancelled error."""
        message = f"Order {order_number or order_id} is already cancelled"
        details = {"order_id": str(order_id)}
        if order_number:
            details["order_number"] = order_number
        
        super().__init__(message, "ORDER_ALREADY_CANCELLED", details)


class OrderAlreadyCompletedException(OrderDomainError):
    """Raised when attempting to modify a completed order."""
    
    def __init__(self, order_id: UUID, order_number: str = None):
        """Initialize order already completed error."""
        message = f"Order {order_number or order_id} is already completed"
        details = {"order_id": str(order_id)}
        if order_number:
            details["order_number"] = order_number
        
        super().__init__(message, "ORDER_ALREADY_COMPLETED", details)


class PaymentAlreadyCollectedError(OrderDomainError):
    """Raised when attempting to collect payment that's already collected."""
    
    def __init__(self, order_id: UUID, payment_reference: str = None):
        """Initialize payment already collected error."""
        message = f"Payment for order {order_id} is already collected"
        details = {"order_id": str(order_id)}
        if payment_reference:
            details["payment_reference"] = payment_reference
        
        super().__init__(message, "PAYMENT_ALREADY_COLLECTED", details)


class PaymentAmountMismatchError(OrderDomainError):
    """Raised when payment amount doesn't match expected amount."""
    
    def __init__(self, expected_amount: float, received_amount: float, order_id: UUID = None):
        """Initialize payment amount mismatch error."""
        message = f"Payment amount mismatch. Expected: {expected_amount}, Received: {received_amount}"
        details = {
            "expected_amount": expected_amount,
            "received_amount": received_amount,
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "PAYMENT_AMOUNT_MISMATCH", details)


class PaymentReferenceNotFoundError(OrderDomainError):
    """Raised when payment reference is not found or invalid."""
    
    def __init__(self, payment_reference: str):
        """Initialize payment reference not found error."""
        message = f"Payment reference {payment_reference} not found or invalid"
        details = {"payment_reference": payment_reference}
        super().__init__(message, "PAYMENT_REFERENCE_NOT_FOUND", details)


class OrderPreparationNotAllowedError(OrderDomainError):
    """Raised when order preparation is attempted without payment collection."""
    
    def __init__(self, order_id: UUID, payment_status: str):
        """Initialize order preparation not allowed error."""
        message = f"Order preparation not allowed. Payment status: {payment_status}"
        details = {
            "order_id": str(order_id),
            "payment_status": payment_status,
            "required_payment_status": "payment_collected"
        }
        super().__init__(message, "ORDER_PREPARATION_NOT_ALLOWED", details)


class CartSessionExpiredError(OrderDomainError):
    """Raised when cart session has expired during order creation."""
    
    def __init__(self, cart_session_id: UUID):
        """Initialize cart session expired error."""
        message = f"Cart session {cart_session_id} has expired"
        details = {"cart_session_id": str(cart_session_id)}
        super().__init__(message, "CART_SESSION_EXPIRED", details)


class CartSessionNotFoundError(OrderDomainError):
    """Raised when cart session is not found during order creation."""
    
    def __init__(self, cart_session_id: UUID):
        """Initialize cart session not found error."""
        message = f"Cart session {cart_session_id} not found"
        details = {"cart_session_id": str(cart_session_id)}
        super().__init__(message, "CART_SESSION_NOT_FOUND", details)


class EmptyCartError(OrderDomainError):
    """Raised when attempting to create order from empty cart."""
    
    def __init__(self, cart_session_id: UUID):
        """Initialize empty cart error."""
        message = f"Cannot create order from empty cart session {cart_session_id}"
        details = {"cart_session_id": str(cart_session_id)}
        super().__init__(message, "EMPTY_CART", details)


class MinimumOrderAmountError(OrderDomainError):
    """Raised when order doesn't meet minimum amount requirement."""
    
    def __init__(self, current_amount: float, minimum_amount: float):
        """Initialize minimum order amount error."""
        message = f"Order amount {current_amount} is below minimum {minimum_amount}"
        details = {
            "current_amount": current_amount,
            "minimum_amount": minimum_amount,
        }
        super().__init__(message, "MINIMUM_ORDER_AMOUNT_NOT_MET", details)


class InvalidCustomerInfoError(OrderDomainError):
    """Raised when customer information is invalid."""
    
    def __init__(self, field: str, value: Any, reason: str):
        """Initialize invalid customer info error."""
        message = f"Invalid customer {field}: {reason}"
        details = {
            "field": field,
            "value": str(value),
            "reason": reason,
        }
        super().__init__(message, "INVALID_CUSTOMER_INFO", details)


class OrderCreationError(OrderDomainError):
    """Raised when order creation fails due to system issues."""
    
    def __init__(self, reason: str, cart_session_id: UUID = None):
        """Initialize order creation error."""
        message = f"Order creation failed: {reason}"
        details = {"reason": reason}
        if cart_session_id:
            details["cart_session_id"] = str(cart_session_id)
        
        super().__init__(message, "ORDER_CREATION_FAILED", details)


class OrderOperationError(OrderDomainError):
    """Raised when an order operation fails."""
    
    def __init__(self, operation: str, order_id: UUID, reason: str):
        """Initialize order operation error."""
        message = f"Order {operation} failed for {order_id}: {reason}"
        details = {
            "operation": operation,
            "order_id": str(order_id),
            "reason": reason,
        }
        super().__init__(message, "ORDER_OPERATION_FAILED", details)


class UnauthorizedOrderAccessError(OrderDomainError):
    """Raised when user attempts unauthorized access to order."""
    
    def __init__(self, order_id: UUID, user_id: UUID = None):
        """Initialize unauthorized order access error."""
        message = f"Unauthorized access to order {order_id}"
        details = {"order_id": str(order_id)}
        if user_id:
            details["user_id"] = str(user_id)
        
        super().__init__(message, "UNAUTHORIZED_ORDER_ACCESS", details)
