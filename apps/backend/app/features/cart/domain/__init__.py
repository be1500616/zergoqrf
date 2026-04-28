"""Cart domain package.

This package contains the core business logic for cart management,
including entities, value objects, repository interfaces, and exceptions.
"""

from .cart_entities import CartItem, CartSession, SessionType
from .cart_exceptions import (
    CartDomainError,
    CartFullError,
    CartItemNotFoundError,
    CartMigrationError,
    CartOperationError,
    CartSessionExpiredError,
    CartSessionNotFoundError,
    InvalidQuantityError,
    MenuItemUnavailableError,
    PriceValidationError,
)
from .cart_repos import ICartItemRepository, ICartSessionRepository
from .cart_vos import CartSessionToken, CustomizationOptions, Money, Quantity

__all__ = [
    # Entities
    "CartSession",
    "CartItem",
    "SessionType",
    # Value Objects
    "Money",
    "Quantity",
    "CartSessionToken",
    "CustomizationOptions",
    # Repository Interfaces
    "ICartSessionRepository",
    "ICartItemRepository",
    # Exceptions
    "CartDomainError",
    "CartSessionNotFoundError",
    "CartSessionExpiredError",
    "CartItemNotFoundError",
    "CartFullError",
    "CartMigrationError",
    "PriceValidationError",
    "InvalidQuantityError",
    "MenuItemUnavailableError",
    "CartOperationError",
]
