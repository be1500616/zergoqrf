"""Cart use cases package.

This package contains all use cases for cart management,
orchestrating business logic and coordinating between domain
and infrastructure layers.
"""

from .cart_item_use_cases import (
    AddCartItemUseCase,
    ClearCartUseCase,
    GetCartItemsUseCase,
    RemoveCartItemUseCase,
    UpdateCartItemUseCase,
)
from .cart_session_use_cases import (
    CreateAnonymousCartSessionUseCase,
    CreateAuthenticatedCartSessionUseCase,
    ExtendCartSessionActivityUseCase,
    GetCartSessionUseCase,
    MigrateCartSessionUseCase,
)
from .cart_summary_use_cases import (
    GetCartSummaryUseCase,
    ValidateCartPricesUseCase,
    ValidateMenuItemPriceUseCase,
)

__all__ = [
    # Cart session use cases
    "CreateAnonymousCartSessionUseCase",
    "CreateAuthenticatedCartSessionUseCase",
    "GetCartSessionUseCase",
    "ExtendCartSessionActivityUseCase",
    "MigrateCartSessionUseCase",
    # Cart item use cases
    "AddCartItemUseCase",
    "UpdateCartItemUseCase",
    "RemoveCartItemUseCase",
    "GetCartItemsUseCase",
    "ClearCartUseCase",
    # Cart summary use cases
    "GetCartSummaryUseCase",
    "ValidateCartPricesUseCase",
    "ValidateMenuItemPriceUseCase",
]
