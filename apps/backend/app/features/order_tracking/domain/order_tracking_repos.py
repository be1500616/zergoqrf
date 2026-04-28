"""Order tracking repository interfaces.

This module contains abstract repository interfaces for order tracking management,
defining contracts for data persistence and retrieval operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .order_tracking_entities import (
    OrderStatusHistory, NotificationHistory, OrderItemTracking
)
from .order_tracking_enums import (
    OrderItemStatus, NotificationChannel, NotificationStatus, 
    NotificationTrigger, KitchenDisplayPriority
)
from .order_tracking_vos import OrderTimeline, KitchenWorkflowStatus


class IOrderStatusHistoryRepository(ABC):
    """Abstract repository interface for order status history operations."""

    @abstractmethod
    async def create_status_history(self, status_history: OrderStatusHistory) -> OrderStatusHistory:
        """Create a new order status history entry.

        Args:
            status_history: Order status history entity to create

        Returns:
            Created order status history entity

        Raises:
            OrderTrackingDataIntegrityError: If creation fails due to data issues
        """
        pass

    @abstractmethod
    async def get_by_id(self, history_id: UUID) -> Optional[OrderStatusHistory]:
        """Get order status history by ID.

        Args:
            history_id: Status history ID

        Returns:
            Order status history entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: UUID) -> List[OrderStatusHistory]:
        """Get all status history for an order.

        Args:
            order_id: Order ID

        Returns:
            List of order status history entities ordered by changed_at DESC
        """
        pass

    @abstractmethod
    async def get_latest_by_order_id(self, order_id: UUID) -> Optional[OrderStatusHistory]:
        """Get latest status history for an order.

        Args:
            order_id: Order ID

        Returns:
            Latest order status history entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_status(
        self, 
        status: str, 
        restaurant_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[OrderStatusHistory]:
        """Get status history entries by status.

        Args:
            status: Order status to filter by
            restaurant_id: Optional restaurant ID filter
            limit: Maximum number of entries to return

        Returns:
            List of order status history entities
        """
        pass

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        restaurant_id: Optional[UUID] = None
    ) -> List[OrderStatusHistory]:
        """Get status history entries within date range.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            restaurant_id: Optional restaurant ID filter

        Returns:
            List of order status history entities
        """
        pass

    @abstractmethod
    async def update_status_history(self, status_history: OrderStatusHistory) -> OrderStatusHistory:
        """Update order status history entry.

        Args:
            status_history: Order status history entity to update

        Returns:
            Updated order status history entity

        Raises:
            OrderStatusHistoryNotFoundError: If status history not found
        """
        pass

    @abstractmethod
    async def delete_status_history(self, history_id: UUID) -> bool:
        """Delete order status history entry.

        Args:
            history_id: Status history ID

        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class INotificationHistoryRepository(ABC):
    """Abstract repository interface for notification history operations."""

    @abstractmethod
    async def create_notification_history(self, notification: NotificationHistory) -> NotificationHistory:
        """Create a new notification history entry.

        Args:
            notification: Notification history entity to create

        Returns:
            Created notification history entity
        """
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Optional[NotificationHistory]:
        """Get notification history by ID.

        Args:
            notification_id: Notification history ID

        Returns:
            Notification history entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: UUID) -> List[NotificationHistory]:
        """Get all notifications for an order.

        Args:
            order_id: Order ID

        Returns:
            List of notification history entities ordered by created_at DESC
        """
        pass

    @abstractmethod
    async def get_by_channel_and_recipient(
        self,
        channel: NotificationChannel,
        recipient: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[NotificationHistory]:
        """Get notifications by channel and recipient.

        Args:
            channel: Notification channel
            recipient: Recipient identifier
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of notification history entities
        """
        pass

    @abstractmethod
    async def get_pending_notifications(self, max_retries: int = 3) -> List[NotificationHistory]:
        """Get pending notifications that need to be sent.

        Args:
            max_retries: Maximum retry count to include

        Returns:
            List of pending notification history entities
        """
        pass

    @abstractmethod
    async def get_failed_notifications(
        self,
        retry_eligible_only: bool = True
    ) -> List[NotificationHistory]:
        """Get failed notifications.

        Args:
            retry_eligible_only: Only return notifications eligible for retry

        Returns:
            List of failed notification history entities
        """
        pass

    @abstractmethod
    async def update_notification_history(self, notification: NotificationHistory) -> NotificationHistory:
        """Update notification history entry.

        Args:
            notification: Notification history entity to update

        Returns:
            Updated notification history entity
        """
        pass

    @abstractmethod
    async def get_delivery_metrics(
        self,
        restaurant_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get notification delivery metrics for a restaurant.

        Args:
            restaurant_id: Restaurant ID
            start_date: Start date for metrics
            end_date: End date for metrics

        Returns:
            Dictionary containing delivery metrics
        """
        pass


class IOrderItemTrackingRepository(ABC):
    """Abstract repository interface for order item tracking operations."""

    @abstractmethod
    async def create_item_tracking(self, item_tracking: OrderItemTracking) -> OrderItemTracking:
        """Create a new order item tracking entry.

        Args:
            item_tracking: Order item tracking entity to create

        Returns:
            Created order item tracking entity
        """
        pass

    @abstractmethod
    async def get_by_id(self, tracking_id: UUID) -> Optional[OrderItemTracking]:
        """Get order item tracking by ID.

        Args:
            tracking_id: Item tracking ID

        Returns:
            Order item tracking entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: UUID) -> List[OrderItemTracking]:
        """Get all item tracking for an order.

        Args:
            order_id: Order ID

        Returns:
            List of order item tracking entities
        """
        pass

    @abstractmethod
    async def get_by_order_item_id(self, order_item_id: UUID) -> List[OrderItemTracking]:
        """Get tracking history for a specific order item.

        Args:
            order_item_id: Order item ID

        Returns:
            List of order item tracking entities ordered by changed_at DESC
        """
        pass

    @abstractmethod
    async def get_by_status(
        self,
        status: OrderItemStatus,
        restaurant_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None
    ) -> List[OrderItemTracking]:
        """Get item tracking entries by status.

        Args:
            status: Item status to filter by
            restaurant_id: Optional restaurant ID filter
            assigned_to: Optional staff assignment filter

        Returns:
            List of order item tracking entities
        """
        pass

    @abstractmethod
    async def get_assigned_to_staff(self, staff_id: UUID) -> List[OrderItemTracking]:
        """Get items assigned to specific staff member.

        Args:
            staff_id: Staff member ID

        Returns:
            List of order item tracking entities assigned to staff
        """
        pass

    @abstractmethod
    async def update_item_tracking(self, item_tracking: OrderItemTracking) -> OrderItemTracking:
        """Update order item tracking entry.

        Args:
            item_tracking: Order item tracking entity to update

        Returns:
            Updated order item tracking entity
        """
        pass

    @abstractmethod
    async def get_kitchen_workflow_status(self, order_id: UUID) -> Optional[KitchenWorkflowStatus]:
        """Get kitchen workflow status for an order.

        Args:
            order_id: Order ID

        Returns:
            Kitchen workflow status value object if found, None otherwise
        """
        pass


class IOrderTimelineRepository(ABC):
    """Abstract repository interface for order timeline operations."""

    @abstractmethod
    async def get_order_timeline(self, order_id: UUID) -> Optional[OrderTimeline]:
        """Get complete order timeline.

        Args:
            order_id: Order ID

        Returns:
            Order timeline value object if found, None otherwise
        """
        pass

    @abstractmethod
    async def add_timeline_event(
        self,
        order_id: UUID,
        event_type: str,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OrderTimeline:
        """Add event to order timeline.

        Args:
            order_id: Order ID
            event_type: Type of timeline event
            title: Event title
            description: Event description
            metadata: Optional event metadata

        Returns:
            Updated order timeline value object
        """
        pass

    @abstractmethod
    async def get_timeline_events_by_type(
        self,
        order_id: UUID,
        event_type: str
    ) -> List[Dict[str, Any]]:
        """Get timeline events by type.

        Args:
            order_id: Order ID
            event_type: Event type to filter by

        Returns:
            List of timeline events
        """
        pass


class IRealtimeEventRepository(ABC):
    """Abstract repository interface for real-time event operations."""

    @abstractmethod
    async def broadcast_order_status_update(
        self,
        order_id: UUID,
        new_status: str,
        previous_status: str,
        estimated_completion_time: Optional[datetime] = None,
        changed_by: Optional[UUID] = None
    ) -> bool:
        """Broadcast order status update event.

        Args:
            order_id: Order ID
            new_status: New order status
            previous_status: Previous order status
            estimated_completion_time: Optional ETA
            changed_by: Optional user who made the change

        Returns:
            True if broadcast successful, False otherwise
        """
        pass

    @abstractmethod
    async def broadcast_item_status_update(
        self,
        order_id: UUID,
        item_id: UUID,
        item_name: str,
        new_status: str,
        previous_status: str
    ) -> bool:
        """Broadcast item status update event.

        Args:
            order_id: Order ID
            item_id: Order item ID
            item_name: Item name
            new_status: New item status
            previous_status: Previous item status

        Returns:
            True if broadcast successful, False otherwise
        """
        pass

    @abstractmethod
    async def broadcast_eta_update(
        self,
        order_id: UUID,
        new_eta: datetime,
        previous_eta: Optional[datetime] = None,
        reason: Optional[str] = None
    ) -> bool:
        """Broadcast ETA update event.

        Args:
            order_id: Order ID
            new_eta: New estimated completion time
            previous_eta: Previous estimated completion time
            reason: Optional reason for ETA change

        Returns:
            True if broadcast successful, False otherwise
        """
        pass

    @abstractmethod
    async def broadcast_notification_sent(
        self,
        order_id: UUID,
        channel: str,
        recipient: str,
        status: str
    ) -> bool:
        """Broadcast notification sent event.

        Args:
            order_id: Order ID
            channel: Notification channel
            recipient: Notification recipient
            status: Notification status

        Returns:
            True if broadcast successful, False otherwise
        """
        pass
