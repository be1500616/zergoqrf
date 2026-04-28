"""Order tracking data transfer objects.

This module contains DTOs for transferring order tracking data between
application layers, ensuring clean separation of concerns.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator

from ..domain.order_tracking_enums import (
    OrderItemStatus, NotificationChannel, NotificationStatus,
    NotificationTrigger, KitchenDisplayPriority
)


class OrderStatusHistoryDTO(BaseModel):
    """Data transfer object for order status history."""
    
    id: UUID
    order_id: UUID
    status: str
    previous_status: Optional[str] = None
    changed_by: Optional[UUID] = None
    changed_at: datetime
    estimated_completion_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None
    preparation_notes: Optional[str] = None
    item_statuses: Dict[str, str] = Field(default_factory=dict)
    change_reason: Optional[str] = None
    system_generated: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class NotificationHistoryDTO(BaseModel):
    """Data transfer object for notification history."""
    
    id: UUID
    order_id: UUID
    restaurant_id: UUID
    channel: NotificationChannel
    recipient: str
    subject: Optional[str] = None
    message_content: str
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    external_message_id: Optional[str] = None
    external_status: Optional[str] = None
    cost_amount: Optional[Decimal] = None
    cost_currency: str = "INR"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: float(v),
        }


class OrderItemTrackingDTO(BaseModel):
    """Data transfer object for order item tracking."""
    
    id: UUID
    order_id: UUID
    order_item_id: UUID
    status: OrderItemStatus
    previous_status: Optional[OrderItemStatus] = None
    assigned_to: Optional[UUID] = None
    estimated_ready_time: Optional[datetime] = None
    actual_ready_time: Optional[datetime] = None
    preparation_notes: Optional[str] = None
    quality_check_passed: Optional[bool] = None
    quality_notes: Optional[str] = None
    changed_by: Optional[UUID] = None
    changed_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class OrderTimelineDTO(BaseModel):
    """Data transfer object for order timeline."""
    
    order_id: UUID
    events: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime
    total_events: int
    duration_minutes: int
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class KitchenWorkflowStatusDTO(BaseModel):
    """Data transfer object for kitchen workflow status."""
    
    order_id: UUID
    total_items: int
    items_pending: int
    items_preparing: int
    items_ready: int
    items_served: int
    overall_progress: float = Field(ge=0.0, le=1.0)
    estimated_completion: Optional[datetime] = None
    assigned_staff: List[UUID] = Field(default_factory=list)
    priority: KitchenDisplayPriority
    is_complete: bool
    items_in_progress: int
    completion_percentage: int
    is_overdue: bool
    next_action: str
    status_summary: str
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class UpdateOrderStatusRequestDTO(BaseModel):
    """Request DTO for updating order status."""
    
    order_id: UUID
    new_status: str
    changed_by: Optional[UUID] = None
    estimated_completion_time: Optional[datetime] = None
    preparation_notes: Optional[str] = None
    change_reason: Optional[str] = None
    notify_customer: bool = True
    
    @validator('new_status')
    def validate_status(cls, v):
        """Validate order status."""
        valid_statuses = ['placed', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Invalid status: {v}. Must be one of {valid_statuses}')
        return v


class UpdateOrderItemStatusRequestDTO(BaseModel):
    """Request DTO for updating order item status."""
    
    order_item_id: UUID
    new_status: OrderItemStatus
    changed_by: UUID
    preparation_notes: Optional[str] = None
    estimated_ready_time: Optional[datetime] = None
    quality_check_passed: Optional[bool] = None
    quality_notes: Optional[str] = None


class SendNotificationRequestDTO(BaseModel):
    """Request DTO for sending notifications."""
    
    order_id: UUID
    trigger: NotificationTrigger
    channels: List[NotificationChannel] = Field(default_factory=list)
    custom_message: Optional[str] = None
    custom_subject: Optional[str] = None
    immediate: bool = False
    
    @validator('channels')
    def validate_channels(cls, v):
        """Validate notification channels."""
        if not v:
            # Default to email if no channels specified
            return [NotificationChannel.EMAIL]
        return v


class NotificationPreferenceDTO(BaseModel):
    """Data transfer object for notification preferences."""
    
    id: UUID
    restaurant_id: UUID
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    email_enabled: bool = True
    whatsapp_enabled: bool = False
    sms_enabled: bool = False
    immediate_notifications: bool = True
    status_change_notifications: bool = True
    eta_update_notifications: bool = True
    completion_notifications: bool = True
    business_hours_only: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    opt_out_all: bool = False
    privacy_consent: bool = False
    created_at: datetime
    updated_at: datetime
    
    @validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        """Validate time format (HH:MM)."""
        if v is not None:
            try:
                datetime.strptime(v, '%H:%M')
            except ValueError:
                raise ValueError('Time must be in HH:MM format')
        return v


class OrderTrackingResponseDTO(BaseModel):
    """Response DTO for order tracking information."""
    
    order_id: UUID
    order_number: str
    restaurant_id: UUID
    current_status: str
    estimated_completion_time: Optional[datetime] = None
    status_history: List[OrderStatusHistoryDTO] = Field(default_factory=list)
    item_tracking: List[OrderItemTrackingDTO] = Field(default_factory=list)
    timeline: Optional[OrderTimelineDTO] = None
    kitchen_workflow: Optional[KitchenWorkflowStatusDTO] = None
    notifications_sent: List[NotificationHistoryDTO] = Field(default_factory=list)
    last_updated: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class KitchenOrderSummaryDTO(BaseModel):
    """Summary DTO for kitchen order display."""
    
    order_id: UUID
    order_number: str
    table_number: Optional[str] = None
    customer_name: str
    current_status: str
    priority: KitchenDisplayPriority
    estimated_completion_time: Optional[datetime] = None
    total_items: int
    items_pending: int
    items_preparing: int
    items_ready: int
    overall_progress: float
    time_since_placed_minutes: int
    is_overdue: bool
    next_action: str
    special_instructions: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class NotificationDeliveryMetricsDTO(BaseModel):
    """DTO for notification delivery metrics."""
    
    restaurant_id: UUID
    date_range_start: datetime
    date_range_end: datetime
    total_notifications: int
    notifications_by_channel: Dict[str, int] = Field(default_factory=dict)
    delivery_success_rate: float
    average_delivery_time_seconds: Optional[float] = None
    failed_notifications: int
    bounced_notifications: int
    opened_notifications: int
    clicked_notifications: int
    engagement_rate: float
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)
    total_cost: float
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class RealtimeEventDTO(BaseModel):
    """DTO for real-time events."""
    
    event_type: str
    order_id: UUID
    timestamp: datetime
    payload: Dict[str, Any]
    channel: str
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


# Utility functions for DTO conversions
def order_status_history_entity_to_dto(entity) -> OrderStatusHistoryDTO:
    """Convert OrderStatusHistory entity to DTO."""
    return OrderStatusHistoryDTO(
        id=entity.id,
        order_id=entity.order_id,
        status=entity.status,
        previous_status=entity.previous_status,
        changed_by=entity.changed_by,
        changed_at=entity.changed_at,
        estimated_completion_time=entity.estimated_completion_time,
        actual_completion_time=entity.actual_completion_time,
        preparation_notes=entity.preparation_notes,
        item_statuses=entity.item_statuses,
        change_reason=entity.change_reason,
        system_generated=entity.system_generated,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def notification_history_entity_to_dto(entity) -> NotificationHistoryDTO:
    """Convert NotificationHistory entity to DTO."""
    return NotificationHistoryDTO(
        id=entity.id,
        order_id=entity.order_id,
        restaurant_id=entity.restaurant_id,
        channel=entity.channel,
        recipient=entity.recipient,
        subject=entity.subject,
        message_content=entity.message_content,
        status=entity.status,
        sent_at=entity.sent_at,
        delivered_at=entity.delivered_at,
        opened_at=entity.opened_at,
        clicked_at=entity.clicked_at,
        error_message=entity.error_message,
        retry_count=entity.retry_count,
        max_retries=entity.max_retries,
        external_message_id=entity.external_message_id,
        external_status=entity.external_status,
        cost_amount=entity.cost_amount,
        cost_currency=entity.cost_currency,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def order_item_tracking_entity_to_dto(entity) -> OrderItemTrackingDTO:
    """Convert OrderItemTracking entity to DTO."""
    return OrderItemTrackingDTO(
        id=entity.id,
        order_id=entity.order_id,
        order_item_id=entity.order_item_id,
        status=entity.status,
        previous_status=entity.previous_status,
        assigned_to=entity.assigned_to,
        estimated_ready_time=entity.estimated_ready_time,
        actual_ready_time=entity.actual_ready_time,
        preparation_notes=entity.preparation_notes,
        quality_check_passed=entity.quality_check_passed,
        quality_notes=entity.quality_notes,
        changed_by=entity.changed_by,
        changed_at=entity.changed_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
