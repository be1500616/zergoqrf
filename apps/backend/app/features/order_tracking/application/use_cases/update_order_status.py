"""Update order status use case.

This module contains the use case for updating order status with real-time
notifications and comprehensive audit trail management.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from ...domain.order_tracking_entities import OrderStatusHistory
from ...domain.order_tracking_enums import NotificationTrigger, OrderTrackingEventType
from ...domain.order_tracking_repos import (
    IOrderStatusHistoryRepository, IRealtimeEventRepository, IOrderTimelineRepository
)
from ...domain.order_tracking_exceptions import (
    OrderTrackingNotFoundError, InvalidStatusTransitionError,
    RealtimeBroadcastError
)
from ..order_tracking_dtos import (
    UpdateOrderStatusRequestDTO, OrderStatusHistoryDTO,
    order_status_history_entity_to_dto
)

# Import from existing orders feature
from ....orders.domain.order_repos import IOrderRepository
from ....orders.domain.order_enums import OrderStatus
from ....orders.domain.order_exceptions import OrderNotFoundError

logger = logging.getLogger(__name__)


class UpdateOrderStatusUseCase:
    """Use case for updating order status with real-time capabilities."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        status_history_repository: IOrderStatusHistoryRepository,
        realtime_repository: IRealtimeEventRepository,
        timeline_repository: IOrderTimelineRepository,
    ):
        """Initialize update order status use case.
        
        Args:
            order_repository: Repository for order operations
            status_history_repository: Repository for status history operations
            realtime_repository: Repository for real-time event operations
            timeline_repository: Repository for timeline operations
        """
        self._order_repository = order_repository
        self._status_history_repository = status_history_repository
        self._realtime_repository = realtime_repository
        self._timeline_repository = timeline_repository
    
    async def execute(self, request: UpdateOrderStatusRequestDTO) -> OrderStatusHistoryDTO:
        """Execute order status update with comprehensive tracking.
        
        Args:
            request: Update order status request DTO
            
        Returns:
            Order status history DTO
            
        Raises:
            OrderNotFoundError: If order is not found
            InvalidStatusTransitionError: If status transition is invalid
            RealtimeBroadcastError: If real-time broadcast fails
        """
        logger.info(f"Updating order status for order {request.order_id} to {request.new_status}")
        
        try:
            # 1. Validate order exists and get current status
            order = await self._order_repository.get_by_id(request.order_id)
            if not order:
                raise OrderNotFoundError(request.order_id)
            
            current_status = order.order_status.value
            new_status_enum = OrderStatus(request.new_status)
            
            # 2. Validate status transition
            if not order.order_status.can_transition_to(new_status_enum):
                raise InvalidStatusTransitionError(
                    f"Cannot transition order from {current_status} to {request.new_status}",
                    "INVALID_ORDER_STATUS_TRANSITION",
                    {
                        "order_id": str(request.order_id),
                        "current_status": current_status,
                        "new_status": request.new_status
                    }
                )
            
            # 3. Update order status in main orders system
            order.update_order_status(new_status_enum)
            updated_order = await self._order_repository.update_order(order)
            
            # 4. Create status history entry
            status_history = OrderStatusHistory(
                id=uuid4(),
                order_id=request.order_id,
                status=request.new_status,
                previous_status=current_status,
                changed_by=request.changed_by,
                changed_at=datetime.now(timezone.utc),
                estimated_completion_time=request.estimated_completion_time,
                preparation_notes=request.preparation_notes,
                change_reason=request.change_reason,
                system_generated=request.changed_by is None,
            )
            
            created_history = await self._status_history_repository.create_status_history(status_history)
            
            # 5. Add timeline event
            await self._timeline_repository.add_timeline_event(
                order_id=request.order_id,
                event_type="status_change",
                title=f"Order {request.new_status.title()}",
                description=self._get_status_change_description(current_status, request.new_status),
                metadata={
                    "previous_status": current_status,
                    "new_status": request.new_status,
                    "changed_by": str(request.changed_by) if request.changed_by else None,
                    "estimated_completion_time": request.estimated_completion_time.isoformat() if request.estimated_completion_time else None,
                    "preparation_notes": request.preparation_notes,
                }
            )
            
            # 6. Broadcast real-time update
            try:
                await self._realtime_repository.broadcast_order_status_update(
                    order_id=request.order_id,
                    new_status=request.new_status,
                    previous_status=current_status,
                    estimated_completion_time=request.estimated_completion_time,
                    changed_by=request.changed_by
                )
                logger.info(f"Successfully broadcasted status update for order {request.order_id}")
            except Exception as e:
                logger.error(f"Failed to broadcast status update for order {request.order_id}: {e}")
                # Don't fail the entire operation if broadcast fails
                # The status update has already been persisted
            
            # 7. Trigger notifications if requested
            if request.notify_customer:
                await self._trigger_status_notification(
                    order_id=request.order_id,
                    new_status=request.new_status,
                    estimated_completion_time=request.estimated_completion_time
                )
            
            logger.info(f"Successfully updated order {request.order_id} status to {request.new_status}")
            return order_status_history_entity_to_dto(created_history)
            
        except Exception as e:
            logger.error(f"Failed to update order status for order {request.order_id}: {e}")
            raise
    
    def _get_status_change_description(self, from_status: str, to_status: str) -> str:
        """Get human-readable description for status change.
        
        Args:
            from_status: Previous status
            to_status: New status
            
        Returns:
            Human-readable description
        """
        descriptions = {
            ("placed", "confirmed"): "Your order has been confirmed and is being prepared",
            ("confirmed", "preparing"): "Kitchen has started preparing your order",
            ("preparing", "ready"): "Your order is ready for pickup",
            ("ready", "completed"): "Order has been completed successfully",
            ("placed", "cancelled"): "Order has been cancelled",
            ("confirmed", "cancelled"): "Order has been cancelled",
            ("preparing", "cancelled"): "Order has been cancelled during preparation",
        }
        
        key = (from_status, to_status)
        return descriptions.get(key, f"Order status changed from {from_status} to {to_status}")
    
    async def _trigger_status_notification(
        self,
        order_id: UUID,
        new_status: str,
        estimated_completion_time: Optional[datetime] = None
    ) -> None:
        """Trigger notification for status change.
        
        Args:
            order_id: Order ID
            new_status: New order status
            estimated_completion_time: Optional ETA
        """
        try:
            # Map order status to notification trigger
            trigger_mapping = {
                "confirmed": NotificationTrigger.ORDER_CONFIRMED,
                "preparing": NotificationTrigger.ORDER_PREPARING,
                "ready": NotificationTrigger.ORDER_READY,
                "completed": NotificationTrigger.ORDER_COMPLETED,
                "cancelled": NotificationTrigger.ORDER_CANCELLED,
            }
            
            trigger = trigger_mapping.get(new_status)
            if trigger:
                # Import notification use case to avoid circular imports
                from .send_notification import SendNotificationUseCase
                
                # This would be injected in a real implementation
                # For now, we'll log the notification trigger
                logger.info(f"Would trigger {trigger.value} notification for order {order_id}")
                
        except Exception as e:
            logger.error(f"Failed to trigger notification for order {order_id}: {e}")
            # Don't fail the status update if notification fails


class BulkUpdateOrderStatusUseCase:
    """Use case for bulk updating order status for kitchen efficiency."""
    
    def __init__(
        self,
        update_order_status_use_case: UpdateOrderStatusUseCase,
    ):
        """Initialize bulk update order status use case.
        
        Args:
            update_order_status_use_case: Single order status update use case
        """
        self._update_order_status_use_case = update_order_status_use_case
    
    async def execute(
        self,
        order_ids: list[UUID],
        new_status: str,
        changed_by: UUID,
        preparation_notes: Optional[str] = None,
        notify_customers: bool = True
    ) -> list[OrderStatusHistoryDTO]:
        """Execute bulk order status update.
        
        Args:
            order_ids: List of order IDs to update
            new_status: New status for all orders
            changed_by: User making the change
            preparation_notes: Optional preparation notes
            notify_customers: Whether to notify customers
            
        Returns:
            List of order status history DTOs
        """
        logger.info(f"Bulk updating {len(order_ids)} orders to status {new_status}")
        
        results = []
        errors = []
        
        for order_id in order_ids:
            try:
                request = UpdateOrderStatusRequestDTO(
                    order_id=order_id,
                    new_status=new_status,
                    changed_by=changed_by,
                    preparation_notes=preparation_notes,
                    change_reason="Bulk status update",
                    notify_customer=notify_customers
                )
                
                result = await self._update_order_status_use_case.execute(request)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to update order {order_id} in bulk operation: {e}")
                errors.append({"order_id": str(order_id), "error": str(e)})
        
        if errors:
            logger.warning(f"Bulk update completed with {len(errors)} errors: {errors}")
        
        logger.info(f"Successfully updated {len(results)} out of {len(order_ids)} orders")
        return results
