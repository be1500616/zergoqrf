"""Order tracking domain entities.

This module contains the core business entities for order tracking management,
including OrderStatusHistory, NotificationPreference, and OrderItemTracking entities.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from decimal import Decimal

from .order_tracking_enums import (
    OrderItemStatus, NotificationChannel, NotificationStatus, 
    NotificationTrigger, KitchenDisplayPriority, OrderTrackingEventType
)
from .order_tracking_vos import (
    EstimatedTime, StatusTransition, NotificationPreference, 
    OrderTimeline, KitchenWorkflowStatus
)
from .order_tracking_exceptions import (
    InvalidStatusTransitionError, NotificationDeliveryError,
    OrderTrackingNotFoundError, InvalidTimelineEventError
)


class OrderStatusHistory:
    """Order status history entity for tracking all status changes."""
    
    def __init__(
        self,
        id: UUID,
        order_id: UUID,
        status: str,
        previous_status: Optional[str] = None,
        changed_by: Optional[UUID] = None,
        changed_at: Optional[datetime] = None,
        estimated_completion_time: Optional[datetime] = None,
        actual_completion_time: Optional[datetime] = None,
        preparation_notes: Optional[str] = None,
        item_statuses: Optional[Dict[str, str]] = None,
        change_reason: Optional[str] = None,
        system_generated: bool = False,
        created_at: Optional[datetime] = None,
    ):
        """Initialize order status history entity."""
        self.id = id
        self.order_id = order_id
        self.status = status
        self.previous_status = previous_status
        self.changed_by = changed_by
        self.changed_at = changed_at or datetime.now(timezone.utc)
        self.estimated_completion_time = estimated_completion_time
        self.actual_completion_time = actual_completion_time
        self.preparation_notes = preparation_notes
        self.item_statuses = item_statuses or {}
        self.change_reason = change_reason
        self.system_generated = system_generated
        self.created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
    
    @property
    def updated_at(self) -> datetime:
        """Get last updated timestamp."""
        return self._updated_at
    
    def get_status_transition(self) -> StatusTransition:
        """Get status transition value object."""
        return StatusTransition(
            from_status=self.previous_status or "unknown",
            to_status=self.status,
            transition_at=self.changed_at,
            changed_by=self.changed_by,
            reason=self.change_reason,
            system_generated=self.system_generated
        )
    
    def get_estimated_time(self) -> Optional[EstimatedTime]:
        """Get estimated time value object if available."""
        if not self.estimated_completion_time:
            return None
        
        return EstimatedTime(
            estimated_at=self.changed_at,
            estimated_completion=self.estimated_completion_time,
            confidence_level=0.8  # Default confidence level
        )
    
    def update_preparation_notes(self, notes: str, updated_by: UUID) -> None:
        """Update preparation notes."""
        self.preparation_notes = notes
        self.changed_by = updated_by
        self._updated_at = datetime.now(timezone.utc)
    
    def mark_actual_completion(self, completion_time: datetime = None) -> None:
        """Mark actual completion time."""
        self.actual_completion_time = completion_time or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
    
    def update_item_status(self, item_id: str, status: str) -> None:
        """Update individual item status."""
        self.item_statuses[item_id] = status
        self._updated_at = datetime.now(timezone.utc)
    
    def get_duration_minutes(self) -> Optional[int]:
        """Get duration from status change to completion in minutes."""
        if not self.actual_completion_time:
            return None
        
        delta = self.actual_completion_time - self.changed_at
        return int(delta.total_seconds() / 60)
    
    def is_eta_accurate(self, tolerance_minutes: int = 5) -> Optional[bool]:
        """Check if ETA was accurate within tolerance."""
        if not self.estimated_completion_time or not self.actual_completion_time:
            return None
        
        delta = abs((self.actual_completion_time - self.estimated_completion_time).total_seconds() / 60)
        return delta <= tolerance_minutes
    
    def __str__(self) -> str:
        """String representation of order status history."""
        return f"Order {self.order_id}: {self.previous_status} → {self.status} at {self.changed_at.strftime('%H:%M:%S')}"


class NotificationHistory:
    """Notification history entity for tracking all notifications sent."""
    
    def __init__(
        self,
        id: UUID,
        order_id: UUID,
        restaurant_id: UUID,
        channel: NotificationChannel,
        recipient: str,
        subject: Optional[str] = None,
        message_content: str = "",
        status: NotificationStatus = NotificationStatus.PENDING,
        sent_at: Optional[datetime] = None,
        delivered_at: Optional[datetime] = None,
        opened_at: Optional[datetime] = None,
        clicked_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        max_retries: int = 3,
        external_message_id: Optional[str] = None,
        external_status: Optional[str] = None,
        cost_amount: Optional[Decimal] = None,
        cost_currency: str = "INR",
        created_at: Optional[datetime] = None,
    ):
        """Initialize notification history entity."""
        self.id = id
        self.order_id = order_id
        self.restaurant_id = restaurant_id
        self.channel = channel
        self.recipient = recipient
        self.subject = subject
        self.message_content = message_content
        self.status = status
        self.sent_at = sent_at
        self.delivered_at = delivered_at
        self.opened_at = opened_at
        self.clicked_at = clicked_at
        self.error_message = error_message
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.external_message_id = external_message_id
        self.external_status = external_status
        self.cost_amount = cost_amount
        self.cost_currency = cost_currency
        self.created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
    
    @property
    def updated_at(self) -> datetime:
        """Get last updated timestamp."""
        return self._updated_at
    
    def mark_sent(self, external_message_id: str = None) -> None:
        """Mark notification as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now(timezone.utc)
        if external_message_id:
            self.external_message_id = external_message_id
        self._updated_at = datetime.now(timezone.utc)
    
    def mark_delivered(self, delivered_at: datetime = None) -> None:
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = delivered_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
    
    def mark_opened(self, opened_at: datetime = None) -> None:
        """Mark notification as opened."""
        self.status = NotificationStatus.OPENED
        self.opened_at = opened_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
    
    def mark_clicked(self, clicked_at: datetime = None) -> None:
        """Mark notification as clicked."""
        self.status = NotificationStatus.CLICKED
        self.clicked_at = clicked_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
    
    def mark_failed(self, error_message: str) -> None:
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self._updated_at = datetime.now(timezone.utc)
    
    def mark_bounced(self, error_message: str) -> None:
        """Mark notification as bounced."""
        self.status = NotificationStatus.BOUNCED
        self.error_message = error_message
        self._updated_at = datetime.now(timezone.utc)
    
    def increment_retry_count(self) -> bool:
        """Increment retry count and return if more retries allowed."""
        self.retry_count += 1
        self._updated_at = datetime.now(timezone.utc)
        return self.retry_count < self.max_retries
    
    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return (
            self.status in {NotificationStatus.PENDING, NotificationStatus.FAILED} and
            self.retry_count < self.max_retries
        )
    
    def get_delivery_time_seconds(self) -> Optional[int]:
        """Get delivery time in seconds from sent to delivered."""
        if not self.sent_at or not self.delivered_at:
            return None
        
        delta = self.delivered_at - self.sent_at
        return int(delta.total_seconds())
    
    def get_engagement_metrics(self) -> Dict[str, Any]:
        """Get engagement metrics for the notification."""
        return {
            "sent": self.sent_at is not None,
            "delivered": self.delivered_at is not None,
            "opened": self.opened_at is not None,
            "clicked": self.clicked_at is not None,
            "delivery_time_seconds": self.get_delivery_time_seconds(),
            "open_rate": 1.0 if self.opened_at else 0.0,
            "click_rate": 1.0 if self.clicked_at else 0.0,
        }
    
    def __str__(self) -> str:
        """String representation of notification history."""
        return f"{self.channel.value} to {self.recipient}: {self.status.value}"


class OrderItemTracking:
    """Order item tracking entity for individual item status management."""
    
    def __init__(
        self,
        id: UUID,
        order_id: UUID,
        order_item_id: UUID,
        status: OrderItemStatus = OrderItemStatus.PENDING,
        previous_status: Optional[OrderItemStatus] = None,
        assigned_to: Optional[UUID] = None,
        estimated_ready_time: Optional[datetime] = None,
        actual_ready_time: Optional[datetime] = None,
        preparation_notes: Optional[str] = None,
        quality_check_passed: Optional[bool] = None,
        quality_notes: Optional[str] = None,
        changed_by: Optional[UUID] = None,
        changed_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        """Initialize order item tracking entity."""
        self.id = id
        self.order_id = order_id
        self.order_item_id = order_item_id
        self.status = status
        self.previous_status = previous_status
        self.assigned_to = assigned_to
        self.estimated_ready_time = estimated_ready_time
        self.actual_ready_time = actual_ready_time
        self.preparation_notes = preparation_notes
        self.quality_check_passed = quality_check_passed
        self.quality_notes = quality_notes
        self.changed_by = changed_by
        self.changed_at = changed_at or datetime.now(timezone.utc)
        self.created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
    
    @property
    def updated_at(self) -> datetime:
        """Get last updated timestamp."""
        return self._updated_at
    
    def update_status(self, new_status: OrderItemStatus, changed_by: UUID, reason: str = None) -> None:
        """Update item status with validation."""
        if not self.status.can_transition_to(new_status):
            raise InvalidStatusTransitionError(
                f"Cannot transition item from {self.status.value} to {new_status.value}",
                "INVALID_ITEM_STATUS_TRANSITION",
                {"current_status": self.status.value, "new_status": new_status.value, "item_id": str(self.id)}
            )
        
        self.previous_status = self.status
        self.status = new_status
        self.changed_by = changed_by
        self.changed_at = datetime.now(timezone.utc)
        self._updated_at = datetime.now(timezone.utc)
        
        # Auto-set actual ready time when marked as ready
        if new_status == OrderItemStatus.READY and not self.actual_ready_time:
            self.actual_ready_time = datetime.now(timezone.utc)
    
    def assign_to_staff(self, staff_id: UUID) -> None:
        """Assign item to kitchen staff member."""
        self.assigned_to = staff_id
        self._updated_at = datetime.now(timezone.utc)
    
    def update_estimated_ready_time(self, estimated_time: datetime) -> None:
        """Update estimated ready time."""
        self.estimated_ready_time = estimated_time
        self._updated_at = datetime.now(timezone.utc)
    
    def add_preparation_notes(self, notes: str, added_by: UUID) -> None:
        """Add preparation notes."""
        self.preparation_notes = notes
        self.changed_by = added_by
        self._updated_at = datetime.now(timezone.utc)
    
    def perform_quality_check(self, passed: bool, notes: str = None, checked_by: UUID = None) -> None:
        """Perform quality check on the item."""
        self.quality_check_passed = passed
        self.quality_notes = notes
        if checked_by:
            self.changed_by = checked_by
        self._updated_at = datetime.now(timezone.utc)
    
    def get_preparation_duration_minutes(self) -> Optional[int]:
        """Get preparation duration in minutes."""
        if not self.actual_ready_time:
            return None
        
        # Find when preparation started (status changed to PREPARING)
        start_time = self.created_at  # Fallback to creation time
        if self.status == OrderItemStatus.PREPARING or self.status == OrderItemStatus.READY:
            start_time = self.changed_at
        
        delta = self.actual_ready_time - start_time
        return int(delta.total_seconds() / 60)
    
    def is_overdue(self) -> bool:
        """Check if item is overdue based on estimated ready time."""
        if not self.estimated_ready_time or self.status.is_terminal():
            return False
        
        return datetime.now(timezone.utc) > self.estimated_ready_time
    
    def get_status_display(self) -> str:
        """Get human-readable status display."""
        display = self.status.get_display_name()
        
        if self.is_overdue():
            display += " (Overdue)"
        elif self.assigned_to:
            display += " (Assigned)"
        
        return display
    
    def __str__(self) -> str:
        """String representation of order item tracking."""
        return f"Item {self.order_item_id}: {self.status.get_display_name()}"
