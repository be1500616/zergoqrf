"""Restaurant orders management use cases.

This module contains use cases for restaurant staff to manage orders,
including viewing orders by status and getting order summaries.
"""

import logging
from typing import List, Optional
from uuid import UUID

from ...domain.order_entities import Order
from ...domain.order_enums import OrderStatus, PaymentStatus
from ...domain.order_repos import IOrderRepository
from ..order_dtos import (
    OrderResponseDTO,
    OrderSummaryResponseDTO,
    RestaurantOrdersResponseDTO,
    order_entity_to_dto,
)

logger = logging.getLogger(__name__)


class GetRestaurantOrdersUseCase:
    """Use case for getting restaurant orders with filters."""

    def __init__(self, order_repository: IOrderRepository):
        """Initialize get restaurant orders use case.

        Args:
            order_repository: Order repository
        """
        self._order_repository = order_repository

    async def execute(
        self,
        restaurant_id: UUID,
        order_status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> RestaurantOrdersResponseDTO:
        """Get restaurant orders with optional filters.

        Args:
            restaurant_id: Restaurant ID
            order_status: Optional order status filter
            payment_status: Optional payment status filter
            limit: Maximum number of orders to return
            offset: Number of orders to skip

        Returns:
            Restaurant orders response DTO
        """
        try:
            logger.info(
                "Getting restaurant orders",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "order_status": order_status.value if order_status else None,
                    "payment_status": payment_status.value if payment_status else None,
                    "limit": limit,
                    "offset": offset,
                },
            )

            # Get orders
            orders = await self._order_repository.get_orders_by_restaurant(
                restaurant_id=restaurant_id,
                order_status=order_status,
                payment_status=payment_status,
                limit=limit + 1,  # Get one extra to check if there are more
                offset=offset,
            )

            # Check if there are more orders
            has_more = len(orders) > limit
            if has_more:
                orders = orders[:limit]  # Remove the extra order

            # Get total count
            total_count = self._order_repository.count_orders_by_restaurant(
                restaurant_id=restaurant_id,
                order_status=order_status,
                payment_status=payment_status,
            )

            # Convert to summary DTOs
            order_summaries = [self._order_to_summary_dto(order) for order in orders]

            logger.info(
                "Restaurant orders retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "orders_count": len(order_summaries),
                    "total_count": total_count,
                    "has_more": has_more,
                },
            )

            return RestaurantOrdersResponseDTO(
                orders=order_summaries,
                total_count=total_count,
                has_more=has_more,
            )

        except Exception as e:
            logger.error(
                "Get restaurant orders failed",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    def _order_to_summary_dto(self, order: Order) -> OrderSummaryResponseDTO:
        """Convert order entity to summary DTO."""
        return OrderSummaryResponseDTO(
            id=order.id,
            order_number=order.order_number.value,
            customer_name=order.customer_info.name,
            customer_phone=order.customer_info.phone,
            order_status=order.order_status,
            payment_status=order.payment_status,
            total_amount=order.gst_calculation.total_amount.amount,
            payment_reference=order.payment_reference.value,
            placed_at=order.placed_at,
            estimated_preparation_time=order.estimated_preparation_time.minutes,
            items_count=order.get_total_items_count(),
        )


class GetRestaurantOrdersSummaryUseCase:
    """Use case for getting restaurant orders summary by status."""

    def __init__(self, order_repository: IOrderRepository):
        """Initialize get restaurant orders summary use case.

        Args:
            order_repository: Order repository
        """
        self._order_repository = order_repository

    async def execute(self, restaurant_id: UUID) -> dict:
        """Get restaurant orders summary by status.

        Args:
            restaurant_id: Restaurant ID

        Returns:
            Dictionary with order counts by status
        """
        try:
            logger.info(
                "Getting restaurant orders summary",
                extra={"restaurant_id": str(restaurant_id)},
            )

            # Get counts for each status combination
            summary = {}

            # New orders (placed + payment_pending)
            new_orders_count = self._order_repository.count_orders_by_restaurant(
                restaurant_id=restaurant_id,
                order_status=OrderStatus.PLACED,
                payment_status=PaymentStatus.PAYMENT_PENDING,
            )
            summary["new_orders"] = new_orders_count

            # Paid orders (placed/confirmed + payment_collected)
            paid_orders_count = self._order_repository.count_orders_by_restaurant(
                restaurant_id=restaurant_id,
                payment_status=PaymentStatus.PAYMENT_COLLECTED,
            )
            summary["paid_orders"] = paid_orders_count

            # Orders in preparation
            preparing_orders_count = self._order_repository.count_orders_by_restaurant(
                restaurant_id=restaurant_id,
                order_status=OrderStatus.PREPARING,
            )
            summary["preparing_orders"] = preparing_orders_count

            # Ready orders
            ready_orders_count = self._order_repository.count_orders_by_restaurant(
                restaurant_id=restaurant_id,
                order_status=OrderStatus.READY,
            )
            summary["ready_orders"] = ready_orders_count

            # Completed orders (today)
            from datetime import datetime, timezone

            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = datetime.now(timezone.utc).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            completed_orders = await self._order_repository.get_orders_by_date_range(
                restaurant_id=restaurant_id,
                start_date=today_start,
                end_date=today_end,
                order_status=OrderStatus.COMPLETED,
            )
            summary["completed_orders_today"] = len(completed_orders)

            # Total active orders
            active_statuses = [
                OrderStatus.PLACED,
                OrderStatus.CONFIRMED,
                OrderStatus.PREPARING,
                OrderStatus.READY,
            ]
            total_active = 0
            for status in active_statuses:
                count = self._order_repository.count_orders_by_restaurant(
                    restaurant_id=restaurant_id,
                    order_status=status,
                )
                total_active += count

            summary["total_active_orders"] = total_active

            logger.info(
                "Restaurant orders summary retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "summary": summary,
                },
            )

            return summary

        except Exception as e:
            logger.error(
                "Get restaurant orders summary failed",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise


class GetOrdersByTableUseCase:
    """Use case for getting orders by table."""

    def __init__(self, order_repository: IOrderRepository):
        """Initialize get orders by table use case.

        Args:
            order_repository: Order repository
        """
        self._order_repository = order_repository

    async def execute(
        self, table_id: UUID, active_only: bool = True
    ) -> List[OrderResponseDTO]:
        """Get orders by table.

        Args:
            table_id: Table ID
            active_only: Whether to return only active orders

        Returns:
            List of order DTOs
        """
        try:
            logger.info(
                "Getting orders by table",
                extra={
                    "table_id": str(table_id),
                    "active_only": active_only,
                },
            )

            orders = await self._order_repository.get_orders_by_table(
                table_id=table_id,
                active_only=active_only,
            )

            logger.info(
                "Orders by table retrieved successfully",
                extra={
                    "table_id": str(table_id),
                    "orders_count": len(orders),
                },
            )

            return [order_entity_to_dto(order) for order in orders]

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
