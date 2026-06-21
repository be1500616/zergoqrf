"""Order tracking value objects.

This module contains immutable value objects for the order tracking domain,
representing concepts like ETA, status transitions, and notification preferences.
"""

import re
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from uuid import UUID

from .order_tracking_enums import (
    NotificationChannel, NotificationStatus, NotificationTrigger,
    OrderItemStatus, KitchenDisplayPriority
)


@dataclass(frozen=True)
class EstimatedTime:
    """Immutable estimated time value object."""
    
    estimated_at: datetime
    estimated_completion: datetime
    confidence_level: float  # 0.0 to 1.0
    
    def __post_init__(self):
        """Validate estimated time constraints."""
        if self.estimated_completion <= self.estimated_at:
            raise ValueError("Estimated completion time must be in the future")
        
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValueError("Confidence level must be between 0.0 and 1.0")
    
    @property
    def duration_minutes(self) -> int:
        """Get estimated duration in minutes."""
        delta = self.estimated_completion - self.estimated_at
        return int(delta.total_seconds() / 60)
    
    @property
    def is_overdue(self) -> bool:
        """Check if estimated time has passed."""
        return datetime.now(timezone.utc) > self.estimated_completion
    
    @property
    def time_remaining_minutes(self) -> int:
        """Get remaining time in minutes (negative if overdue)."""
        delta = self.estimated_completion - datetime.now(timezone.utc)
        return int(delta.total_seconds() / 60)
    
    def update_completion_time(self, new_completion: datetime, reason: str = None) -> 'EstimatedTime':
        """Create new EstimatedTime with updated completion time."""
        return EstimatedTime(
            estimated_at=datetime.now(timezone.utc),
            estimated_completion=new_completion,
            confidence_level=self.confidence_level
        )
    
    def adjust_for_priority(self, priority: KitchenDisplayPriority) -> 'EstimatedTime':
        """Adjust estimated time based on kitchen priority."""
        multiplier = priority.get_preparation_time_multiplier()
        adjusted_duration = timedelta(minutes=int(self.duration_minutes * multiplier))
        new_completion = self.estimated_at + adjusted_duration
        
        return EstimatedTime(
            estimated_at=self.estimated_at,
            estimated_completion=new_completion,
            confidence_level=self.confidence_level * 0.9  # Slightly reduce confidence
        )
    
    def __str__(self) -> str:
        """String representation of estimated time."""
        return f"ETA: {self.estimated_completion.strftime('%H:%M')} ({self.duration_minutes}min)"


@dataclass(frozen=True)
class StatusTransition:
    """Immutable status transition value object."""
    
    from_status: str
    to_status: str
    transition_at: datetime
    changed_by: Optional[UUID]
    reason: Optional[str]
    system_generated: bool = False
    
    def __post_init__(self):
        """Validate status transition constraints."""
        if self.from_status == self.to_status:
            raise ValueError("Status transition must change the status")
        
        if not self.from_status or not self.to_status:
            raise ValueError("Both from_status and to_status are required")
    
    @property
    def is_manual_change(self) -> bool:
        """Check if this was a manual status change."""
        return not self.system_generated and self.changed_by is not None
    
    @property
    def transition_duration_seconds(self) -> int:
        """Get duration since transition in seconds."""
        delta = datetime.now(timezone.utc) - self.transition_at
        return int(delta.total_seconds())
    
    def get_display_message(self) -> str:
        """Get human-readable transition message."""
        if self.system_generated:
            return f"Status automatically changed from {self.from_status} to {self.to_status}"
        elif self.changed_by:
            return f"Status changed from {self.from_status} to {self.to_status} by staff"
        else:
            return f"Status changed from {self.from_status} to {self.to_status}"
    
    def __str__(self) -> str:
        """String representation of status transition."""
        return f"{self.from_status} → {self.to_status} at {self.transition_at.strftime('%H:%M:%S')}"


@dataclass(frozen=True)
class NotificationPreference:
    """Immutable notification preference value object."""
    
    channel: NotificationChannel
    enabled: bool
    recipient: str  # email address or phone number
    immediate_notifications: bool = True
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    
    def __post_init__(self):
        """Validate notification preference constraints."""
        if self.channel.requires_email_address() and not self._is_valid_email(self.recipient):
            raise ValueError(f"Invalid email address for {self.channel.value}: {self.recipient}")
        
        if self.channel.requires_phone_number() and not self._is_valid_phone(self.recipient):
            raise ValueError(f"Invalid phone number for {self.channel.value}: {self.recipient}")
        
        if self.quiet_hours_start and not self._is_valid_time_format(self.quiet_hours_start):
            raise ValueError(f"Invalid quiet hours start time format: {self.quiet_hours_start}")
        
        if self.quiet_hours_end and not self._is_valid_time_format(self.quiet_hours_end):
            raise ValueError(f"Invalid quiet hours end time format: {self.quiet_hours_end}")
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format (Indian +91 format)."""
        pattern = r'^\+91[6-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Validate HH:MM time format."""
        pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        return bool(re.match(pattern, time_str))
    
    def is_in_quiet_hours(self, check_time: datetime = None) -> bool:
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        if check_time is None:
            check_time = datetime.now()
        
        current_time = check_time.strftime('%H:%M')
        
        # Handle quiet hours that span midnight
        if self.quiet_hours_start <= self.quiet_hours_end:
            return self.quiet_hours_start <= current_time <= self.quiet_hours_end
        else:
            return current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end
    
    def should_send_notification(self, trigger: NotificationTrigger, current_time: datetime = None) -> bool:
        """Check if notification should be sent based on preferences."""
        if not self.enabled:
            return False
        
        if not self.immediate_notifications and trigger.should_send_immediately():
            return False
        
        if self.is_in_quiet_hours(current_time):
            return False
        
        return True
    
    def __str__(self) -> str:
        """String representation of notification preference."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.channel.get_display_name()} ({self.recipient}): {status}"


@dataclass(frozen=True)
class OrderTimeline:
    """Immutable order timeline value object."""
    
    order_id: UUID
    events: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime
    
    def __post_init__(self):
        """Validate timeline constraints."""
        if not self.events:
            raise ValueError("Timeline must have at least one event")
        
        if self.last_updated < self.created_at:
            raise ValueError("Last updated time cannot be before creation time")
    
    @classmethod
    def from_partial(
        cls,
        order_id: UUID,
        events: List[Dict[str, Any]],
        created_at: datetime,
        last_updated: datetime,
    ) -> "OrderTimeline":
        """Build a timeline that may be empty (e.g. freshly-created order)."""
        if not events:
            # Synthesize one event so invariants pass; it represents order creation.
            events = [{
                "id": None,
                "event_type": "order_created",
                "title": "Order created",
                "description": "Order placed",
                "metadata": {},
                "created_at": created_at.isoformat(),
            }]
        if last_updated < created_at:
            last_updated = created_at
        return cls(
            order_id=order_id,
            events=events,
            created_at=created_at,
            last_updated=last_updated,
        )

    @property
    def total_events(self) -> int:
        """Get total number of timeline events."""
        return len(self.events)

    @property
    def latest_event(self) -> Dict[str, Any]:
        """Get the most recent timeline event."""
        return max(self.events, key=lambda e: e.get('timestamp', self.created_at))
    
    @property
    def duration_minutes(self) -> int:
        """Get total timeline duration in minutes."""
        delta = self.last_updated - self.created_at
        return int(delta.total_seconds() / 60)
    
    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get all events of a specific type."""
        return [event for event in self.events if event.get('type') == event_type]
    
    def get_status_changes(self) -> List[Dict[str, Any]]:
        """Get all status change events."""
        return self.get_events_by_type('status_change')
    
    def add_event(self, event: Dict[str, Any]) -> 'OrderTimeline':
        """Create new timeline with additional event."""
        new_events = self.events + [event]
        return OrderTimeline(
            order_id=self.order_id,
            events=new_events,
            created_at=self.created_at,
            last_updated=datetime.now(timezone.utc)
        )
    
    def get_formatted_timeline(self) -> List[Dict[str, str]]:
        """Get formatted timeline for display."""
        formatted_events = []
        for event in sorted(self.events, key=lambda e: e.get('timestamp', self.created_at)):
            formatted_events.append({
                'time': event.get('timestamp', self.created_at).strftime('%H:%M:%S'),
                'title': event.get('title', 'Unknown Event'),
                'description': event.get('description', ''),
                'type': event.get('type', 'general'),
                'icon': event.get('icon', 'info')
            })
        return formatted_events
    
    def __str__(self) -> str:
        """String representation of order timeline."""
        return f"Timeline for order {self.order_id}: {self.total_events} events over {self.duration_minutes} minutes"


@dataclass(frozen=True)
class KitchenWorkflowStatus:
    """Immutable kitchen workflow status value object."""
    
    order_id: UUID
    total_items: int
    items_pending: int
    items_preparing: int
    items_ready: int
    items_served: int
    overall_progress: float  # 0.0 to 1.0
    estimated_completion: Optional[datetime]
    assigned_staff: List[UUID]
    priority: KitchenDisplayPriority
    
    def __post_init__(self):
        """Validate kitchen workflow status constraints."""
        total_accounted = self.items_pending + self.items_preparing + self.items_ready + self.items_served
        if self.total_items and total_accounted != self.total_items:
            raise ValueError(
                f"Item counts do not match total items "
                f"(total={self.total_items}, accounted={total_accounted})"
            )

        if not 0.0 <= self.overall_progress <= 1.0:
            raise ValueError("Overall progress must be between 0.0 and 1.0")

    @classmethod
    def from_item_counts(
        cls,
        order_id: UUID,
        items_pending: int,
        items_preparing: int,
        items_ready: int,
        items_served: int = 0,
    ) -> "KitchenWorkflowStatus":
        """Build a kitchen workflow from item counts (no full aggregation needed)."""
        from .order_tracking_enums import KitchenDisplayPriority

        total = items_pending + items_preparing + items_ready + items_served
        if total == 0:
            progress = 0.0
        else:
            progress = (items_ready + items_served) / total
        return cls(
            order_id=order_id,
            total_items=total,
            items_pending=items_pending,
            items_preparing=items_preparing,
            items_ready=items_ready,
            items_served=items_served,
            overall_progress=progress,
            estimated_completion=None,
            assigned_staff=[],
            priority=KitchenDisplayPriority.NORMAL,
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if all items are served."""
        return self.items_served == self.total_items
    
    @property
    def items_in_progress(self) -> int:
        """Get number of items currently being worked on."""
        return self.items_preparing + self.items_ready
    
    @property
    def completion_percentage(self) -> int:
        """Get completion percentage as integer."""
        return int(self.overall_progress * 100)
    
    @property
    def is_overdue(self) -> bool:
        """Check if order is overdue based on estimated completion."""
        if not self.estimated_completion:
            return False
        return datetime.now(timezone.utc) > self.estimated_completion
    
    def get_next_action(self) -> str:
        """Get recommended next action for kitchen staff."""
        if self.items_pending > 0:
            return f"Start preparing {self.items_pending} pending items"
        elif self.items_preparing > 0:
            return f"Continue preparing {self.items_preparing} items"
        elif self.items_ready > 0:
            return f"Serve {self.items_ready} ready items"
        elif self.is_complete:
            return "Order complete"
        else:
            return "Review order status"
    
    def get_status_summary(self) -> str:
        """Get human-readable status summary."""
        if self.is_complete:
            return "All items served"
        
        status_parts = []
        if self.items_preparing > 0:
            status_parts.append(f"{self.items_preparing} preparing")
        if self.items_ready > 0:
            status_parts.append(f"{self.items_ready} ready")
        if self.items_pending > 0:
            status_parts.append(f"{self.items_pending} pending")
        
        return ", ".join(status_parts) if status_parts else "No active items"
    
    def __str__(self) -> str:
        """String representation of kitchen workflow status."""
        return f"Kitchen Status: {self.completion_percentage}% complete ({self.get_status_summary()})"
