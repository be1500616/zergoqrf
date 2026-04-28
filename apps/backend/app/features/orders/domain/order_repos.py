"""Order repository interfaces.

This module contains abstract repository interfaces for order management,
defining contracts for data persistence and retrieval operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .order_entities import Order, OrderItem, PaymentCollection
from .order_enums import OrderStatus, PaymentMethod, PaymentStatus
from .order_vos import OrderNumber, PaymentReference


class IOrderRepository(ABC):
    """Abstract repository interface for order operations."""

    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        """Create a new order.

        Args:
            order: Order entity to create

        Returns:
            Created order entity

        Raises:
            OrderAlreadyExistsError: If order already exists
            OrderCreationError: If creation fails
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_order_number(self, order_number: OrderNumber) -> Optional[Order]:
        """Get order by order number.

        Args:
            order_number: Order number

        Returns:
            Order entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_payment_reference(
        self, payment_reference: PaymentReference
    ) -> Optional[Order]:
        """Get order by payment reference.

        Args:
            payment_reference: Payment reference

        Returns:
            Order entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_order(self, order: Order) -> Order:
        """Update existing order.

        Args:
            order: Order entity to update

        Returns:
            Updated order entity

        Raises:
            OrderNotFoundError: If order not found
            OrderOperationError: If update fails
        """
        pass

    @abstractmethod
    async def get_orders_by_restaurant(
        self,
        restaurant_id: UUID,
        order_status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Order]:
        """Get orders by restaurant with optional filters.

        Args:
            restaurant_id: Restaurant ID
            order_status: Optional order status filter
            payment_status: Optional payment status filter
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            List of order entities
        """
        pass

    @abstractmethod
    async def get_orders_by_user(
        self,
        user_id: UUID,
        restaurant_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Order]:
        """Get orders by user.

        Args:
            user_id: User ID
            restaurant_id: Optional restaurant filter
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            List of order entities
        """
        pass

    @abstractmethod
    async def get_orders_by_table(
        self,
        table_id: UUID,
        active_only: bool = True,
    ) -> List[Order]:
        """Get orders by table.

        Args:
            table_id: Table ID
            active_only: Whether to return only active orders

        Returns:
            List of order entities
        """
        pass

    @abstractmethod
    async def get_orders_by_date_range(
        self,
        restaurant_id: UUID,
        start_date: datetime,
        end_date: datetime,
        order_status: Optional[OrderStatus] = None,
    ) -> List[Order]:
        """Get orders by date range.

        Args:
            restaurant_id: Restaurant ID
            start_date: Start date
            end_date: End date
            order_status: Optional order status filter

        Returns:
            List of order entities
        """
        pass

    @abstractmethod
    def count_orders_by_restaurant(
        self,
        restaurant_id: UUID,
        order_status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
    ) -> int:
        """Count orders by restaurant with optional filters.

        Args:
            restaurant_id: Restaurant ID
            order_status: Optional order status filter
            payment_status: Optional payment status filter

        Returns:
            Number of matching orders
        """
        pass

    @abstractmethod
    async def delete_order(self, order_id: UUID) -> bool:
        """Delete order (soft delete).

        Args:
            order_id: Order ID

        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class IOrderItemRepository(ABC):
    """Abstract repository interface for order item operations."""

    @abstractmethod
    async def create_item(self, item: OrderItem) -> OrderItem:
        """Create a new order item.

        Args:
            item: Order item entity to create

        Returns:
            Created order item entity
        """
        pass

    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[OrderItem]:
        """Get order item by ID.

        Args:
            item_id: Order item ID

        Returns:
            Order item entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_items_by_order(self, order_id: UUID) -> List[OrderItem]:
        """Get all items for an order.

        Args:
            order_id: Order ID

        Returns:
            List of order item entities
        """
        pass

    @abstractmethod
    async def update_item(self, item: OrderItem) -> OrderItem:
        """Update existing order item.

        Args:
            item: Order item entity to update

        Returns:
            Updated order item entity
        """
        pass

    @abstractmethod
    async def delete_item(self, item_id: UUID) -> bool:
        """Delete order item.

        Args:
            item_id: Order item ID

        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class IPaymentCollectionRepository(ABC):
    """Abstract repository interface for payment collection operations."""

    @abstractmethod
    async def create_collection(
        self, collection: PaymentCollection
    ) -> PaymentCollection:
        """Create a new payment collection.

        Args:
            collection: Payment collection entity to create

        Returns:
            Created payment collection entity
        """
        pass

    @abstractmethod
    async def get_by_id(self, collection_id: UUID) -> Optional[PaymentCollection]:
        """Get payment collection by ID.

        Args:
            collection_id: Payment collection ID

        Returns:
            Payment collection entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_order(self, order_id: UUID) -> List[PaymentCollection]:
        """Get all payment collections for an order.

        Args:
            order_id: Order ID

        Returns:
            List of payment collection entities
        """
        pass

    @abstractmethod
    async def get_by_payment_reference(
        self, payment_reference: PaymentReference
    ) -> List[PaymentCollection]:
        """Get payment collections by payment reference.

        Args:
            payment_reference: Payment reference

        Returns:
            List of payment collection entities
        """
        pass

    @abstractmethod
    async def get_collections_by_staff(
        self,
        staff_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PaymentCollection]:
        """Get payment collections by staff member.

        Args:
            staff_id: Staff member ID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of payment collection entities
        """
        pass

    @abstractmethod
    async def get_collections_by_restaurant(
        self,
        restaurant_id: UUID,
        payment_method: Optional[PaymentMethod] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PaymentCollection]:
        """Get payment collections by restaurant.

        Args:
            restaurant_id: Restaurant ID
            payment_method: Optional payment method filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of payment collection entities
        """
        pass


class IOrderAuditRepository(ABC):
    """Abstract repository interface for order audit operations."""

    @abstractmethod
    async def create_audit_entry(
        self,
        order_id: UUID,
        previous_order_status: Optional[OrderStatus],
        new_order_status: Optional[OrderStatus],
        previous_payment_status: Optional[PaymentStatus],
        new_payment_status: Optional[PaymentStatus],
        changed_by: Optional[UUID],
        change_reason: Optional[str],
        change_notes: Optional[str],
    ) -> UUID:
        """Create an audit entry for order/payment status changes.

        Args:
            order_id: Order ID
            previous_order_status: Previous order status
            new_order_status: New order status
            previous_payment_status: Previous payment status
            new_payment_status: New payment status
            changed_by: User who made the change
            change_reason: Reason for the change
            change_notes: Additional notes

        Returns:
            Audit entry ID
        """
        pass

    @abstractmethod
    async def get_audit_history(
        self,
        order_id: UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get audit history for an order.

        Args:
            order_id: Order ID
            limit: Maximum number of entries to return

        Returns:
            List of audit entries
        """
        pass

    @abstractmethod
    async def get_audit_entries_by_user(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get audit entries by user.

        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of entries to return

        Returns:
            List of audit entries
        """
        pass
