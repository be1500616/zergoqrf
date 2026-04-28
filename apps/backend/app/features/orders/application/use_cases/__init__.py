"""Order use cases package.

This package contains all use cases for order management,
orchestrating business logic and coordinating between domain
and infrastructure layers.
"""

from .order_creation_use_cases import CreateOrderFromCartUseCase
from .order_status_use_cases import (
    GetOrderByNumberUseCase,
    GetOrderByPaymentReferenceUseCase,
    GetOrderUseCase,
    UpdateOrderStatusUseCase,
)
from .payment_collection_use_cases import (
    CollectPaymentUseCase,
    GetPaymentCollectionsUseCase,
)
from .restaurant_orders_use_cases import (
    GetOrdersByTableUseCase,
    GetRestaurantOrdersSummaryUseCase,
    GetRestaurantOrdersUseCase,
)

__all__ = [
    # Order creation use cases
    "CreateOrderFromCartUseCase",
    # Order status use cases
    "UpdateOrderStatusUseCase",
    "GetOrderUseCase",
    "GetOrderByNumberUseCase",
    "GetOrderByPaymentReferenceUseCase",
    # Payment collection use cases
    "CollectPaymentUseCase",
    "GetPaymentCollectionsUseCase",
    # Restaurant orders use cases
    "GetRestaurantOrdersUseCase",
    "GetRestaurantOrdersSummaryUseCase",
    "GetOrdersByTableUseCase",
]
