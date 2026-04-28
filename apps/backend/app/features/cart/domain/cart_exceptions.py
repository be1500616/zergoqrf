"""Cart domain exceptions.

This module contains all domain-specific exceptions for the cart management system.
These exceptions represent business rule violations and domain errors.
"""


class CartDomainError(Exception):
    """Base exception for all cart domain errors."""
    
    def __init__(self, message: str, details: dict = None):
        """Initialize cart domain error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CartSessionNotFoundError(CartDomainError):
    """Raised when a cart session is not found."""
    
    def __init__(self, session_token: str):
        """Initialize cart session not found error.
        
        Args:
            session_token: Session token that was not found
        """
        super().__init__(
            f"Cart session not found: {session_token[:8]}...",
            {"session_token": session_token}
        )


class CartSessionExpiredError(CartDomainError):
    """Raised when a cart session has expired."""
    
    def __init__(self, session_token: str):
        """Initialize cart session expired error.
        
        Args:
            session_token: Expired session token
        """
        super().__init__(
            f"Cart session expired: {session_token[:8]}...",
            {"session_token": session_token}
        )


class CartItemNotFoundError(CartDomainError):
    """Raised when a cart item is not found."""
    
    def __init__(self, item_id: str):
        """Initialize cart item not found error.
        
        Args:
            item_id: Cart item ID that was not found
        """
        super().__init__(
            f"Cart item not found: {item_id}",
            {"item_id": item_id}
        )


class CartFullError(CartDomainError):
    """Raised when attempting to add items to a full cart."""
    
    def __init__(self, current_count: int, max_items: int = 50):
        """Initialize cart full error.
        
        Args:
            current_count: Current number of items in cart
            max_items: Maximum allowed items in cart
        """
        super().__init__(
            f"Cart is full. Current items: {current_count}, Maximum: {max_items}",
            {"current_count": current_count, "max_items": max_items}
        )


class CartMigrationError(CartDomainError):
    """Raised when cart migration fails."""
    
    def __init__(self, reason: str, details: dict = None):
        """Initialize cart migration error.
        
        Args:
            reason: Reason for migration failure
            details: Additional error details
        """
        super().__init__(
            f"Cart migration failed: {reason}",
            details or {}
        )


class PriceValidationError(CartDomainError):
    """Raised when price validation fails."""
    
    def __init__(self, item_id: str, expected_price: float, actual_price: float):
        """Initialize price validation error.
        
        Args:
            item_id: Menu item ID with price mismatch
            expected_price: Expected price from cart
            actual_price: Actual price from menu
        """
        super().__init__(
            f"Price validation failed for item {item_id}. Expected: {expected_price}, Actual: {actual_price}",
            {
                "item_id": item_id,
                "expected_price": expected_price,
                "actual_price": actual_price
            }
        )


class InvalidQuantityError(CartDomainError):
    """Raised when an invalid quantity is provided."""
    
    def __init__(self, quantity: int):
        """Initialize invalid quantity error.
        
        Args:
            quantity: Invalid quantity value
        """
        super().__init__(
            f"Invalid quantity: {quantity}. Quantity must be positive.",
            {"quantity": quantity}
        )


class MenuItemUnavailableError(CartDomainError):
    """Raised when attempting to add an unavailable menu item."""
    
    def __init__(self, item_id: str, item_name: str = None):
        """Initialize menu item unavailable error.
        
        Args:
            item_id: Unavailable menu item ID
            item_name: Optional item name for better error message
        """
        item_display = item_name or item_id
        super().__init__(
            f"Menu item is unavailable: {item_display}",
            {"item_id": item_id, "item_name": item_name}
        )


class CartOperationError(CartDomainError):
    """Raised when a cart operation fails at the infrastructure level."""
    
    def __init__(self, operation: str, reason: str, details: dict = None):
        """Initialize cart operation error.
        
        Args:
            operation: Operation that failed (e.g., 'add_item', 'update_quantity')
            reason: Reason for failure
            details: Additional error details
        """
        super().__init__(
            f"Cart operation '{operation}' failed: {reason}",
            {"operation": operation, "reason": reason, **(details or {})}
        )
