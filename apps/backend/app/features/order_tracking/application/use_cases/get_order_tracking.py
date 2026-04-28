"""Get order tracking use case.

This module contains the use case for retrieving comprehensive order tracking
information including status history, timeline, and real-time updates.
"""

import logging
from typing import Optional
from uuid import UUID

from ...domain.order_tracking_repos import (
    IOrderStatusHistoryRepository, IOrderItemTrackingRepository,
    IOrderTimelineRepository, INotificationHistoryRepository
)
from ...domain.order_tracking_exceptions import OrderTrackingNotFoundError
from ..order_tracking_dtos import (
    OrderTrackingResponseDTO, OrderStatusHistoryDTO, OrderItemTrackingDTO,
    OrderTimelineDTO, KitchenWorkflowStatusDTO, NotificationHistoryDTO,
    order_status_history_entity_to_dto, order_item_tracking_entity_to_dto,
    notification_history_entity_to_dto
)

# Import from existing orders feature
from ....orders.domain.order_repos import IOrderRepository
from ....orders.domain.order_exceptions import OrderNotFoundError

logger = logging.getLogger(__name__)


class GetOrderTrackingUseCase:
    """Use case for retrieving comprehensive order tracking information."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        status_history_repository: IOrderStatusHistoryRepository,
        item_tracking_repository: IOrderItemTrackingRepository,
        timeline_repository: IOrderTimelineRepository,
        notification_repository: INotificationHistoryRepository,
    ):
        """Initialize get order tracking use case.
        
        Args:
            order_repository: Repository for order operations
            status_history_repository: Repository for status history operations
            item_tracking_repository: Repository for item tracking operations
            timeline_repository: Repository for timeline operations
            notification_repository: Repository for notification operations
        """
        self._order_repository = order_repository
        self._status_history_repository = status_history_repository
        self._item_tracking_repository = item_tracking_repository
        self._timeline_repository = timeline_repository
        self._notification_repository = notification_repository
    
    async def execute(self, order_id: UUID, include_notifications: bool = True) -> OrderTrackingResponseDTO:
        """Execute order tracking retrieval.
        
        Args:
            order_id: Order ID to get tracking for
            include_notifications: Whether to include notification history
            
        Returns:
            Comprehensive order tracking response DTO
            
        Raises:
            OrderNotFoundError: If order is not found
        """
        logger.info(f"Retrieving order tracking for order {order_id}")
        
        try:
            # 1. Get base order information
            order = await self._order_repository.get_by_id(order_id)
            if not order:
                raise OrderNotFoundError(order_id)
            
            # 2. Get status history
            status_history_entities = await self._status_history_repository.get_by_order_id(order_id)
            status_history = [
                order_status_history_entity_to_dto(entity) 
                for entity in status_history_entities
            ]
            
            # 3. Get item tracking
            item_tracking_entities = await self._item_tracking_repository.get_by_order_id(order_id)
            item_tracking = [
                order_item_tracking_entity_to_dto(entity) 
                for entity in item_tracking_entities
            ]
            
            # 4. Get order timeline
            timeline_vo = await self._timeline_repository.get_order_timeline(order_id)
            timeline = None
            if timeline_vo:
                timeline = OrderTimelineDTO(
                    order_id=timeline_vo.order_id,
                    events=timeline_vo.events,
                    created_at=timeline_vo.created_at,
                    last_updated=timeline_vo.last_updated,
                    total_events=timeline_vo.total_events,
                    duration_minutes=timeline_vo.duration_minutes,
                )
            
            # 5. Get kitchen workflow status
            kitchen_workflow_vo = await self._item_tracking_repository.get_kitchen_workflow_status(order_id)
            kitchen_workflow = None
            if kitchen_workflow_vo:
                kitchen_workflow = KitchenWorkflowStatusDTO(
                    order_id=kitchen_workflow_vo.order_id,
                    total_items=kitchen_workflow_vo.total_items,
                    items_pending=kitchen_workflow_vo.items_pending,
                    items_preparing=kitchen_workflow_vo.items_preparing,
                    items_ready=kitchen_workflow_vo.items_ready,
                    items_served=kitchen_workflow_vo.items_served,
                    overall_progress=kitchen_workflow_vo.overall_progress,
                    estimated_completion=kitchen_workflow_vo.estimated_completion,
                    assigned_staff=kitchen_workflow_vo.assigned_staff,
                    priority=kitchen_workflow_vo.priority,
                    is_complete=kitchen_workflow_vo.is_complete,
                    items_in_progress=kitchen_workflow_vo.items_in_progress,
                    completion_percentage=kitchen_workflow_vo.completion_percentage,
                    is_overdue=kitchen_workflow_vo.is_overdue,
                    next_action=kitchen_workflow_vo.get_next_action(),
                    status_summary=kitchen_workflow_vo.get_status_summary(),
                )
            
            # 6. Get notification history if requested
            notifications_sent = []
            if include_notifications:
                notification_entities = await self._notification_repository.get_by_order_id(order_id)
                notifications_sent = [
                    notification_history_entity_to_dto(entity) 
                    for entity in notification_entities
                ]
            
            # 7. Build comprehensive response
            response = OrderTrackingResponseDTO(
                order_id=order.id,
                order_number=order.order_number.value,
                restaurant_id=order.restaurant_id,
                current_status=order.order_status.value,
                estimated_completion_time=self._get_latest_eta(status_history),
                status_history=status_history,
                item_tracking=item_tracking,
                timeline=timeline,
                kitchen_workflow=kitchen_workflow,
                notifications_sent=notifications_sent,
                last_updated=max(
                    order.updated_at,
                    max([h.updated_at for h in status_history_entities], default=order.updated_at),
                    max([t.updated_at for t in item_tracking_entities], default=order.updated_at),
                )
            )
            
            logger.info(f"Successfully retrieved order tracking for order {order_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to retrieve order tracking for order {order_id}: {e}")
            raise
    
    def _get_latest_eta(self, status_history: list[OrderStatusHistoryDTO]) -> Optional[str]:
        """Get latest estimated completion time from status history.
        
        Args:
            status_history: List of status history DTOs
            
        Returns:
            Latest ETA as ISO string if available
        """
        for history in sorted(status_history, key=lambda h: h.changed_at, reverse=True):
            if history.estimated_completion_time:
                return history.estimated_completion_time.isoformat()
        return None


class GetOrderTrackingByNumberUseCase:
    """Use case for retrieving order tracking by order number."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        get_order_tracking_use_case: GetOrderTrackingUseCase,
    ):
        """Initialize get order tracking by number use case.
        
        Args:
            order_repository: Repository for order operations
            get_order_tracking_use_case: Main order tracking use case
        """
        self._order_repository = order_repository
        self._get_order_tracking_use_case = get_order_tracking_use_case
    
    async def execute(self, order_number: str, include_notifications: bool = True) -> OrderTrackingResponseDTO:
        """Execute order tracking retrieval by order number.
        
        Args:
            order_number: Order number to get tracking for
            include_notifications: Whether to include notification history
            
        Returns:
            Comprehensive order tracking response DTO
            
        Raises:
            OrderNotFoundError: If order is not found
        """
        logger.info(f"Retrieving order tracking for order number {order_number}")
        
        # Import order number value object
        from ....orders.domain.order_vos import OrderNumber
        
        try:
            order_number_vo = OrderNumber(order_number)
            order = await self._order_repository.get_by_order_number(order_number_vo)
            
            if not order:
                raise OrderNotFoundError(f"Order not found with number: {order_number}")
            
            return await self._get_order_tracking_use_case.execute(
                order_id=order.id,
                include_notifications=include_notifications
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve order tracking for order number {order_number}: {e}")
            raise


class GetKitchenOrdersUseCase:
    """Use case for retrieving orders for kitchen display."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        status_history_repository: IOrderStatusHistoryRepository,
        item_tracking_repository: IOrderItemTrackingRepository,
    ):
        """Initialize get kitchen orders use case.
        
        Args:
            order_repository: Repository for order operations
            status_history_repository: Repository for status history operations
            item_tracking_repository: Repository for item tracking operations
        """
        self._order_repository = order_repository
        self._status_history_repository = status_history_repository
        self._item_tracking_repository = item_tracking_repository
    
    async def execute(
        self,
        restaurant_id: UUID,
        active_only: bool = True,
        limit: int = 50
    ) -> list[OrderTrackingResponseDTO]:
        """Execute kitchen orders retrieval.
        
        Args:
            restaurant_id: Restaurant ID to get orders for
            active_only: Whether to only include active orders
            limit: Maximum number of orders to return
            
        Returns:
            List of order tracking response DTOs for kitchen display
        """
        logger.info(f"Retrieving kitchen orders for restaurant {restaurant_id}")
        
        try:
            # Get orders for restaurant
            if active_only:
                # Get orders that are not completed or cancelled
                active_statuses = ["placed", "confirmed", "preparing", "ready"]
                orders = []
                for status in active_statuses:
                    status_orders = await self._order_repository.get_orders_by_status(
                        restaurant_id=restaurant_id,
                        status=status,
                        limit=limit // len(active_statuses)
                    )
                    orders.extend(status_orders)
            else:
                orders = await self._order_repository.get_orders_by_restaurant(
                    restaurant_id=restaurant_id,
                    limit=limit
                )
            
            # Build tracking responses for each order
            tracking_responses = []
            for order in orders:
                try:
                    # Get basic tracking info (without full timeline for performance)
                    status_history = await self._status_history_repository.get_by_order_id(order.id)
                    item_tracking = await self._item_tracking_repository.get_by_order_id(order.id)
                    kitchen_workflow = await self._item_tracking_repository.get_kitchen_workflow_status(order.id)
                    
                    response = OrderTrackingResponseDTO(
                        order_id=order.id,
                        order_number=order.order_number.value,
                        restaurant_id=order.restaurant_id,
                        current_status=order.order_status.value,
                        estimated_completion_time=self._get_latest_eta_from_entities(status_history),
                        status_history=[order_status_history_entity_to_dto(h) for h in status_history],
                        item_tracking=[order_item_tracking_entity_to_dto(t) for t in item_tracking],
                        timeline=None,  # Skip timeline for performance
                        kitchen_workflow=self._build_kitchen_workflow_dto(kitchen_workflow) if kitchen_workflow else None,
                        notifications_sent=[],  # Skip notifications for kitchen view
                        last_updated=order.updated_at,
                    )
                    
                    tracking_responses.append(response)
                    
                except Exception as e:
                    logger.error(f"Failed to build tracking response for order {order.id}: {e}")
                    continue
            
            # Sort by priority and time
            tracking_responses.sort(key=lambda r: (
                r.kitchen_workflow.priority.get_sort_order() if r.kitchen_workflow else 999,
                r.last_updated
            ))
            
            logger.info(f"Successfully retrieved {len(tracking_responses)} kitchen orders")
            return tracking_responses
            
        except Exception as e:
            logger.error(f"Failed to retrieve kitchen orders for restaurant {restaurant_id}: {e}")
            raise
    
    def _get_latest_eta_from_entities(self, status_history: list) -> Optional[str]:
        """Get latest ETA from status history entities."""
        for history in sorted(status_history, key=lambda h: h.changed_at, reverse=True):
            if history.estimated_completion_time:
                return history.estimated_completion_time.isoformat()
        return None
    
    def _build_kitchen_workflow_dto(self, workflow_vo) -> KitchenWorkflowStatusDTO:
        """Build kitchen workflow DTO from value object."""
        return KitchenWorkflowStatusDTO(
            order_id=workflow_vo.order_id,
            total_items=workflow_vo.total_items,
            items_pending=workflow_vo.items_pending,
            items_preparing=workflow_vo.items_preparing,
            items_ready=workflow_vo.items_ready,
            items_served=workflow_vo.items_served,
            overall_progress=workflow_vo.overall_progress,
            estimated_completion=workflow_vo.estimated_completion,
            assigned_staff=workflow_vo.assigned_staff,
            priority=workflow_vo.priority,
            is_complete=workflow_vo.is_complete,
            items_in_progress=workflow_vo.items_in_progress,
            completion_percentage=workflow_vo.completion_percentage,
            is_overdue=workflow_vo.is_overdue,
            next_action=workflow_vo.get_next_action(),
            status_summary=workflow_vo.get_status_summary(),
        )
