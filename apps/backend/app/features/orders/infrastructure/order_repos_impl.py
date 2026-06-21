"""Order repository implementations.

This module contains concrete implementations of order repository interfaces
using Supabase as the data persistence layer.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import AClient

from ..domain.order_entities import Order, OrderItem, PaymentCollection
from ..domain.order_enums import OrderStatus, PaymentMethod, PaymentStatus
from ..domain.order_exceptions import (
    OrderCreationError,
    OrderNotFoundError,
    OrderOperationError,
)
from ..domain.order_repos import (
    IOrderAuditRepository,
    IOrderItemRepository,
    IOrderRepository,
    IPaymentCollectionRepository,
)
from ..domain.order_vos import (
    CustomerInfo,
    GSTCalculation,
    Money,
    OrderCustomizations,
    OrderNumber,
    PaymentReference,
    PreparationTime,
    Quantity,
)

logger = logging.getLogger(__name__)


class SupabaseOrderRepository(IOrderRepository):
    """Supabase implementation of order repository."""

    def __init__(self, supabase_client: AClient):
        """Initialize Supabase order repository.

        Args:
            supabase_client: Async Supabase client for concurrent operations
        """
        self._client = supabase_client

    async def create_order(self, order: Order) -> Order:
        """Create a new order using Supabase database function."""
        try:
            logger.info(
                "Creating order in database",
                extra={
                    "order_id": str(order.id),
                    "order_number": order.order_number.value,
                },
            )

            # Use the database function for atomic order creation
            result = await self._client.rpc(
                "create_order_from_cart",
                {
                    "p_cart_session_id": str(order.cart_session_id),
                    "p_customer_name": order.customer_info.name,
                    "p_customer_phone": order.customer_info.phone,
                    "p_customer_email": order.customer_info.email,
                    "p_special_instructions": order.special_instructions,
                    "p_user_id": str(order.user_id) if order.user_id else None,
                },
            ).execute()

            if not result.data:
                raise OrderCreationError("Database function returned no data")

            created_order_data = result.data[0]

            # Fetch the complete order with items
            order_response = await (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("id", created_order_data["order_id"])
                .execute()
            )

            if not order_response.data:
                raise OrderCreationError("Created order not found")

            created_order = self._map_to_order_entity(order_response.data[0])

            logger.info(
                "Order created successfully",
                extra={
                    "order_id": str(created_order.id),
                    "order_number": created_order.order_number.value,
                },
            )

            return created_order

        except Exception as e:
            logger.error(
                "Order creation failed",
                extra={
                    "order_id": str(order.id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise OrderCreationError(f"Failed to create order: {str(e)}")

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID."""
        try:
            response = await (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("id", str(order_id))
                .execute()
            )

            if not response.data:
                return None

            return self._map_to_order_entity(response.data[0])

        except Exception as e:
            logger.error(
                "Get order by ID failed",
                extra={
                    "order_id": str(order_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_by_order_number(self, order_number: OrderNumber) -> Optional[Order]:
        """Get order by order number."""
        try:
            response = await (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("order_number", order_number.value)
                .execute()
            )

            if not response.data:
                return None

            return self._map_to_order_entity(response.data[0])

        except Exception as e:
            logger.error(
                "Get order by number failed",
                extra={
                    "order_number": order_number.value,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_by_payment_reference(
        self, payment_reference: PaymentReference
    ) -> Optional[Order]:
        """Get order by payment reference."""
        try:
            response = await (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("payment_reference", payment_reference.value)
                .execute()
            )

            if not response.data:
                return None

            return self._map_to_order_entity(response.data[0])

        except Exception as e:
            logger.error(
                "Get order by payment reference failed",
                extra={
                    "payment_reference": payment_reference.value,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def update_order(self, order: Order) -> Order:
        """Update existing order."""
        try:
            logger.info(
                "Updating order",
                extra={
                    "order_id": str(order.id),
                    "order_status": order.order_status.value,
                    "payment_status": order.payment_status.value,
                },
            )

            update_data = {
                "order_status": order.order_status.value,
                "payment_status": order.payment_status.value,
                "payment_method": order.payment_method.value,
                "special_instructions": order.special_instructions,
                "estimated_preparation_time": order.estimated_preparation_time.minutes,
                "confirmed_at": (
                    order.confirmed_at.isoformat() if order.confirmed_at else None
                ),
                "preparing_at": (
                    order.preparing_at.isoformat() if order.preparing_at else None
                ),
                "ready_at": order.ready_at.isoformat() if order.ready_at else None,
                "completed_at": (
                    order.completed_at.isoformat() if order.completed_at else None
                ),
                "cancelled_at": (
                    order.cancelled_at.isoformat() if order.cancelled_at else None
                ),
                "payment_collected_at": (
                    order.payment_collected_at.isoformat()
                    if order.payment_collected_at
                    else None
                ),
                "updated_at": datetime.utcnow().isoformat(),
            }

            response = await (
                self._client.table("orders")
                .update(update_data)
                .eq("id", str(order.id))
                .execute()
            )

            if not response.data:
                raise OrderNotFoundError(order.id)

            # Fetch updated order with relationships
            updated_response = await (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("id", str(order.id))
                .execute()
            )

            return self._map_to_order_entity(updated_response.data[0])

        except OrderNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Order update failed",
                extra={
                    "order_id": str(order.id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise OrderOperationError("update", order.id, str(e))

    async def get_orders_by_restaurant(
        self,
        restaurant_id: UUID,
        order_status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Order]:
        """Get orders by restaurant with optional filters."""
        try:
            query = (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("restaurant_id", str(restaurant_id))
            )

            if order_status:
                query = query.eq("order_status", order_status.value)

            if payment_status:
                query = query.eq("payment_status", payment_status.value)

            response = await (
                query.order("placed_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return [
                self._map_to_order_entity(order_data) for order_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get orders by restaurant failed",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_orders_by_user(
        self,
        user_id: UUID,
        restaurant_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Order]:
        """Get orders by user."""
        try:
            query = (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("user_id", str(user_id))
            )

            if restaurant_id:
                query = query.eq("restaurant_id", str(restaurant_id))

            response = (
                await query.order("placed_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return [
                self._map_to_order_entity(order_data) for order_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get orders by user failed",
                extra={
                    "user_id": str(user_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_orders_by_status(
        self,
        restaurant_id: UUID,
        status: str,
        limit: int = 50,
    ) -> List[Order]:
        """Get orders by restaurant and a single status."""
        try:
            response = await (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("restaurant_id", str(restaurant_id))
                .eq("order_status", status)
                .order("placed_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self._map_to_order_entity(r) for r in response.data]
        except Exception as e:
            logger.error(
                "Get orders by status failed",
                extra={"restaurant_id": str(restaurant_id), "status": status, "error": str(e)},
                exc_info=True,
            )
            raise

    async def get_orders_by_table(
        self,
        table_id: UUID,
        active_only: bool = True,
    ) -> List[Order]:
        """Get orders by table."""
        try:
            query = (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("table_id", str(table_id))
            )

            if active_only:
                query = query.in_(
                    "order_status", ["placed", "confirmed", "preparing", "ready"]
                )

            response = await query.order("placed_at", desc=True).execute()

            return [
                self._map_to_order_entity(order_data) for order_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get orders by table failed",
                extra={
                    "table_id": str(table_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_orders_by_date_range(
        self,
        restaurant_id: UUID,
        start_date: datetime,
        end_date: datetime,
        order_status: Optional[OrderStatus] = None,
    ) -> List[Order]:
        """Get orders by date range."""
        try:
            query = (
                self._client.table("orders")
                .select("*, order_items(*), payment_collections(*)")
                .eq("restaurant_id", str(restaurant_id))
                .gte("placed_at", start_date.isoformat())
                .lte("placed_at", end_date.isoformat())
            )

            if order_status:
                query = query.eq("order_status", order_status.value)

            response = await query.order("placed_at", desc=True).execute()

            return [
                self._map_to_order_entity(order_data) for order_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get orders by date range failed",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def count_orders_by_restaurant(
        self,
        restaurant_id: UUID,
        order_status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
    ) -> int:
        """Count orders by restaurant with optional filters."""
        try:
            query = (
                self._client.table("orders")
                .select("id", count="exact")
                .eq("restaurant_id", str(restaurant_id))
            )

            if order_status:
                query = query.eq("order_status", order_status.value)

            if payment_status:
                query = query.eq("payment_status", payment_status.value)

            response = await query.execute()

            return response.count or 0

        except Exception as e:
            logger.error(
                "Count orders by restaurant failed",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def delete_order(self, order_id: UUID) -> bool:
        """Delete order (soft delete by marking as cancelled)."""
        try:
            response = await (
                self._client.table("orders")
                .update(
                    {
                        "order_status": OrderStatus.CANCELLED.value,
                        "cancelled_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                .eq("id", str(order_id))
                .execute()
            )

            return len(response.data) > 0

        except Exception as e:
            logger.error(
                "Delete order failed",
                extra={
                    "order_id": str(order_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    def _map_to_order_entity(self, order_data: Dict[str, Any]) -> Order:
        """Map database row to order entity."""

        # Parse timestamps
        def parse_timestamp(ts_str):
            if ts_str:
                return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            return None

        # Create customer info
        customer_info = CustomerInfo(
            name=order_data["customer_name"],
            phone=order_data["customer_phone"],
            email=order_data.get("customer_email"),
        )

        # Create GST calculation
        subtotal = Money(Decimal(str(order_data["subtotal"])))
        gst_amount = Money(Decimal(str(order_data["gst_amount"])))
        total_amount = Money(Decimal(str(order_data["total_amount"])))
        gst_rate = Decimal(str(order_data["gst_rate"]))

        gst_calculation = GSTCalculation(
            subtotal=subtotal,
            gst_rate=gst_rate,
            gst_amount=gst_amount,
            total_amount=total_amount,
        )

        # Create order items
        items = []
        for item_data in order_data.get("order_items", []):
            order_item = OrderItem(
                id=UUID(item_data["id"]),
                order_id=UUID(order_data["id"]),
                restaurant_id=UUID(item_data["restaurant_id"]),
                menu_item_id=UUID(item_data["menu_item_id"]),
                item_name=item_data["item_name"],
                item_description=item_data.get("item_description"),
                base_price=Money(Decimal(str(item_data["base_price"]))),
                quantity=Quantity(item_data["quantity"]),
                unit_price=Money(Decimal(str(item_data["unit_price"]))),
                total_price=Money(Decimal(str(item_data["total_price"]))),
                customizations=OrderCustomizations(item_data.get("customizations", {})),
                special_instructions=item_data.get("special_instructions"),
                is_available=item_data.get("is_available", True),
                created_at=parse_timestamp(item_data["created_at"]),
                updated_at=parse_timestamp(item_data["updated_at"]),
            )
            items.append(order_item)

        # Create payment collections
        payment_collections = []
        for pc_data in order_data.get("payment_collections", []):
            payment_collection = PaymentCollection(
                id=UUID(pc_data["id"]),
                order_id=UUID(order_data["id"]),
                payment_reference=PaymentReference(pc_data["payment_reference"]),
                amount=Money(Decimal(str(pc_data["amount"]))),
                payment_method=PaymentMethod(pc_data["payment_method"]),
                collected_by=(
                    UUID(pc_data["collected_by"])
                    if pc_data.get("collected_by")
                    else None
                ),
                collected_at=parse_timestamp(pc_data["collected_at"]),
                collection_notes=pc_data.get("collection_notes"),
                verification_code=pc_data.get("verification_code"),
                created_at=parse_timestamp(pc_data["created_at"]),
                updated_at=parse_timestamp(pc_data["updated_at"]),
            )
            payment_collections.append(payment_collection)

        # Create order entity
        order = Order(
            id=UUID(order_data["id"]),
            order_number=OrderNumber(order_data["order_number"]),
            restaurant_id=UUID(order_data["restaurant_id"]),
            table_id=(
                UUID(order_data["table_id"]) if order_data.get("table_id") else None
            ),
            user_id=UUID(order_data["user_id"]) if order_data.get("user_id") else None,
            cart_session_id=(
                UUID(order_data["cart_session_id"])
                if order_data.get("cart_session_id")
                else None
            ),
            customer_info=customer_info,
            payment_reference=PaymentReference(order_data["payment_reference"]),
            gst_calculation=gst_calculation,
            order_status=OrderStatus(order_data["order_status"]),
            payment_status=PaymentStatus(order_data["payment_status"]),
            payment_method=PaymentMethod(order_data["payment_method"]),
            special_instructions=order_data.get("special_instructions"),
            estimated_preparation_time=PreparationTime(
                order_data.get("estimated_preparation_time", 30)
            ),
            items=items,
            payment_collections=payment_collections,
            placed_at=parse_timestamp(order_data["placed_at"]),
            confirmed_at=parse_timestamp(order_data.get("confirmed_at")),
            preparing_at=parse_timestamp(order_data.get("preparing_at")),
            ready_at=parse_timestamp(order_data.get("ready_at")),
            completed_at=parse_timestamp(order_data.get("completed_at")),
            cancelled_at=parse_timestamp(order_data.get("cancelled_at")),
            payment_collected_at=parse_timestamp(
                order_data.get("payment_collected_at")
            ),
            created_at=parse_timestamp(order_data["created_at"]),
            updated_at=parse_timestamp(order_data["updated_at"]),
        )

        return order


class SupabaseOrderItemRepository(IOrderItemRepository):
    """Supabase implementation of order item repository."""

    def __init__(self, supabase_client: AClient):
        """Initialize Supabase order item repository.

        Args:
            supabase_client: Supabase async client
        """
        self._client = supabase_client

    async def create_item(self, item: OrderItem) -> OrderItem:
        """Create a new order item."""
        # Order items are created as part of order creation
        # This is a placeholder implementation
        return item

    async def get_by_id(self, item_id: UUID) -> Optional[OrderItem]:
        """Get order item by ID."""
        try:
            response = await (
                self._client.table("order_items")
                .select("*")
                .eq("id", str(item_id))
                .execute()
            )

            if not response.data:
                return None

            item_data = response.data[0]
            return self._map_to_order_item_entity(item_data)

        except Exception as e:
            logger.error(f"Get order item by ID failed: {e}")
            raise

    async def get_items_by_order(self, order_id: UUID) -> List[OrderItem]:
        """Get all items for an order."""
        try:
            response = await (
                self._client.table("order_items")
                .select("*")
                .eq("order_id", str(order_id))
                .execute()
            )

            return [
                self._map_to_order_item_entity(item_data) for item_data in response.data
            ]

        except Exception as e:
            logger.error(f"Get order items by order failed: {e}")
            raise

    async def update_item(self, item: OrderItem) -> OrderItem:
        """Update existing order item."""
        # Placeholder implementation
        return item

    async def delete_item(self, item_id: UUID) -> bool:
        """Delete order item."""
        # Placeholder implementation
        return True

    def _map_to_order_item_entity(self, item_data: Dict[str, Any]) -> OrderItem:
        """Map database row to order item entity."""
        return OrderItem(
            id=UUID(item_data["id"]),
            order_id=UUID(item_data["order_id"]),
            restaurant_id=UUID(item_data["restaurant_id"]),
            menu_item_id=UUID(item_data["menu_item_id"]),
            item_name=item_data["item_name"],
            item_description=item_data.get("item_description"),
            base_price=Money(Decimal(str(item_data["base_price"]))),
            quantity=Quantity(item_data["quantity"]),
            unit_price=Money(Decimal(str(item_data["unit_price"]))),
            total_price=Money(Decimal(str(item_data["total_price"]))),
            customizations=OrderCustomizations(item_data.get("customizations", {})),
            special_instructions=item_data.get("special_instructions"),
            is_available=item_data.get("is_available", True),
            created_at=datetime.fromisoformat(
                item_data["created_at"].replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                item_data["updated_at"].replace("Z", "+00:00")
            ),
        )


class SupabasePaymentCollectionRepository(IPaymentCollectionRepository):
    """Supabase implementation of payment collection repository."""

    def __init__(self, supabase_client: AClient):
        """Initialize Supabase payment collection repository.

        Args:
            supabase_client: Supabase async client
        """
        self._client = supabase_client

    async def create_collection(
        self, collection: PaymentCollection
    ) -> PaymentCollection:
        """Create a new payment collection."""
        try:
            collection_data = {
                "id": str(collection.id),
                "order_id": str(collection.order_id),
                "payment_reference": collection.payment_reference.value,
                "amount": float(collection.amount.amount),
                "payment_method": collection.payment_method.value,
                "collected_by": (
                    str(collection.collected_by) if collection.collected_by else None
                ),
                "collected_at": collection.collected_at.isoformat(),
                "collection_notes": collection.collection_notes,
                "verification_code": collection.verification_code,
            }

            response = await (
                self._client.table("payment_collections")
                .insert(collection_data)
                .execute()
            )

            if not response.data:
                raise Exception("Payment collection creation failed")

            return collection

        except Exception as e:
            logger.error(
                "Payment collection creation failed",
                extra={
                    "collection_id": str(collection.id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_by_id(self, collection_id: UUID) -> Optional[PaymentCollection]:
        """Get payment collection by ID."""
        try:
            response = await (
                self._client.table("payment_collections")
                .select("*")
                .eq("id", str(collection_id))
                .execute()
            )

            if not response.data:
                return None

            return self._map_to_payment_collection_entity(response.data[0])

        except Exception as e:
            logger.error(
                "Get payment collection by ID failed",
                extra={
                    "collection_id": str(collection_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_by_order(self, order_id: UUID) -> List[PaymentCollection]:
        """Get all payment collections for an order."""
        try:
            response = (
                await self._client.table("payment_collections")
                .select("*")
                .eq("order_id", str(order_id))
                .order("collected_at", desc=True)
                .execute()
            )

            return [
                self._map_to_payment_collection_entity(pc_data)
                for pc_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get payment collections by order failed",
                extra={
                    "order_id": str(order_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_by_payment_reference(
        self, payment_reference: PaymentReference
    ) -> List[PaymentCollection]:
        """Get payment collections by payment reference."""
        try:
            response = (
                await self._client.table("payment_collections")
                .select("*")
                .eq("payment_reference", payment_reference.value)
                .order("collected_at", desc=True)
                .execute()
            )

            return [
                self._map_to_payment_collection_entity(pc_data)
                for pc_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get payment collections by reference failed",
                extra={
                    "payment_reference": payment_reference.value,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_collections_by_staff(
        self,
        staff_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PaymentCollection]:
        """Get payment collections by staff member."""
        try:
            query = (
                self._client.table("payment_collections")
                .select("*")
                .eq("collected_by", str(staff_id))
            )

            if start_date:
                query = query.gte("collected_at", start_date.isoformat())

            if end_date:
                query = query.lte("collected_at", end_date.isoformat())

            response = await query.order("collected_at", desc=True).execute()

            return [
                self._map_to_payment_collection_entity(pc_data)
                for pc_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get payment collections by staff failed",
                extra={
                    "staff_id": str(staff_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_collections_by_restaurant(
        self,
        restaurant_id: UUID,
        payment_method: Optional[PaymentMethod] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PaymentCollection]:
        """Get payment collections by restaurant."""
        try:
            # Join with orders table to filter by restaurant
            query = (
                self._client.table("payment_collections")
                .select("*, orders!inner(restaurant_id)")
                .eq("orders.restaurant_id", str(restaurant_id))
            )

            if payment_method:
                query = query.eq("payment_method", payment_method.value)

            if start_date:
                query = query.gte("collected_at", start_date.isoformat())

            if end_date:
                query = query.lte("collected_at", end_date.isoformat())

            response = await query.order("collected_at", desc=True).execute()

            return [
                self._map_to_payment_collection_entity(pc_data)
                for pc_data in response.data
            ]

        except Exception as e:
            logger.error(
                "Get payment collections by restaurant failed",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    def _map_to_payment_collection_entity(
        self, pc_data: Dict[str, Any]
    ) -> PaymentCollection:
        """Map database row to payment collection entity."""

        def parse_timestamp(ts_str):
            if ts_str:
                return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            return None

        return PaymentCollection(
            id=UUID(pc_data["id"]),
            order_id=UUID(pc_data["order_id"]),
            payment_reference=PaymentReference(pc_data["payment_reference"]),
            amount=Money(Decimal(str(pc_data["amount"]))),
            payment_method=PaymentMethod(pc_data["payment_method"]),
            collected_by=(
                UUID(pc_data["collected_by"]) if pc_data.get("collected_by") else None
            ),
            collected_at=parse_timestamp(pc_data["collected_at"]),
            collection_notes=pc_data.get("collection_notes"),
            verification_code=pc_data.get("verification_code"),
            created_at=parse_timestamp(pc_data["created_at"]),
            updated_at=parse_timestamp(pc_data["updated_at"]),
        )


class SupabaseOrderAuditRepository(IOrderAuditRepository):
    """Supabase implementation of order audit repository."""

    def __init__(self, supabase_client: AClient):
        """Initialize Supabase order audit repository.

        Args:
            supabase_client: Supabase async client
        """
        self._client = supabase_client

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
        """Create an audit entry for order/payment status changes."""
        try:
            from uuid import uuid4

            audit_id = uuid4()

            audit_data = {
                "id": str(audit_id),
                "order_id": str(order_id),
                "previous_order_status": (
                    previous_order_status.value if previous_order_status else None
                ),
                "new_order_status": (
                    new_order_status.value if new_order_status else None
                ),
                "previous_payment_status": (
                    previous_payment_status.value if previous_payment_status else None
                ),
                "new_payment_status": (
                    new_payment_status.value if new_payment_status else None
                ),
                "changed_by": str(changed_by) if changed_by else None,
                "change_reason": change_reason,
                "change_notes": change_notes,
            }

            response = (
                await self._client.table("order_payment_history")
                .insert(audit_data)
                .execute()
            )

            if not response.data:
                raise Exception("Audit entry creation failed")

            return audit_id

        except Exception as e:
            logger.error(
                "Audit entry creation failed",
                extra={
                    "order_id": str(order_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_audit_history(
        self,
        order_id: UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get audit history for an order."""
        try:
            response = (
                await self._client.table("order_payment_history")
                .select("*")
                .eq("order_id", str(order_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return response.data

        except Exception as e:
            logger.error(
                "Get audit history failed",
                extra={
                    "order_id": str(order_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def get_audit_entries_by_user(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get audit entries by user."""
        try:
            query = (
                self._client.table("order_payment_history")
                .select("*")
                .eq("changed_by", str(user_id))
            )

            if start_date:
                query = query.gte("created_at", start_date.isoformat())

            if end_date:
                query = query.lte("created_at", end_date.isoformat())

            response = await query.order("created_at", desc=True).limit(limit).execute()

            return response.data

        except Exception as e:
            logger.error(
                "Get audit entries by user failed",
                extra={
                    "user_id": str(user_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise
