"""Order tracking Pydantic schemas.

This module contains Pydantic schemas for order tracking API requests
and responses, ensuring proper data validation and serialization.
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


class UpdateOrderStatusRequest(BaseModel):
    """Request schema for updating order status."""
    
    new_status: str = Field(..., description="New order status")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")
    preparation_notes: Optional[str] = Field(None, description="Preparation notes")
    change_reason: Optional[str] = Field(None, description="Reason for status change")
    notify_customer: bool = Field(True, description="Whether to notify customer")
    
    @validator('new_status')
    def validate_status(cls, v):
        """Validate order status."""
        valid_statuses = ['placed', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Invalid status: {v}. Must be one of {valid_statuses}')
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "new_status": "preparing",
                "estimated_completion_time": "2024-01-15T14:30:00Z",
                "preparation_notes": "Started cooking",
                "change_reason": "Kitchen ready to prepare",
                "notify_customer": True
            }
        }


class BulkUpdateOrderStatusRequest(BaseModel):
    """Request schema for bulk updating order status."""
    
    order_ids: List[UUID] = Field(..., description="List of order IDs to update")
    new_status: str = Field(..., description="New status for all orders")
    preparation_notes: Optional[str] = Field(None, description="Preparation notes")
    notify_customers: bool = Field(True, description="Whether to notify customers")
    
    @validator('order_ids')
    def validate_order_ids(cls, v):
        """Validate order IDs list."""
        if not v:
            raise ValueError('At least one order ID is required')
        if len(v) > 50:
            raise ValueError('Cannot update more than 50 orders at once')
        return v
    
    @validator('new_status')
    def validate_status(cls, v):
        """Validate order status."""
        valid_statuses = ['placed', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Invalid status: {v}. Must be one of {valid_statuses}')
        return v


class UpdateOrderItemStatusRequest(BaseModel):
    """Request schema for updating order item status."""
    
    new_status: OrderItemStatus = Field(..., description="New item status")
    preparation_notes: Optional[str] = Field(None, description="Preparation notes")
    estimated_ready_time: Optional[datetime] = Field(None, description="Estimated ready time")
    quality_check_passed: Optional[bool] = Field(None, description="Quality check result")
    quality_notes: Optional[str] = Field(None, description="Quality check notes")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "new_status": "preparing",
                "preparation_notes": "Started grilling",
                "estimated_ready_time": "2024-01-15T14:25:00Z",
                "quality_check_passed": None,
                "quality_notes": None
            }
        }


class SendNotificationRequest(BaseModel):
    """Request schema for sending notifications."""
    
    trigger: NotificationTrigger = Field(..., description="Notification trigger")
    channels: List[NotificationChannel] = Field(default_factory=list, description="Notification channels")
    custom_message: Optional[str] = Field(None, description="Custom message content")
    custom_subject: Optional[str] = Field(None, description="Custom subject")
    immediate: bool = Field(False, description="Send immediately regardless of preferences")
    
    @validator('channels')
    def validate_channels(cls, v):
        """Validate notification channels."""
        if not v:
            # Default to email if no channels specified
            return [NotificationChannel.EMAIL]
        return v
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "trigger": "order_ready",
                "channels": ["email", "whatsapp"],
                "custom_message": "Your delicious meal is ready!",
                "custom_subject": "Order Ready - Come and get it!",
                "immediate": False
            }
        }


class OrderStatusHistoryResponse(BaseModel):
    """Response schema for order status history."""
    
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


class NotificationHistoryResponse(BaseModel):
    """Response schema for notification history."""
    
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


class OrderItemTrackingResponse(BaseModel):
    """Response schema for order item tracking."""
    
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


class OrderTimelineResponse(BaseModel):
    """Response schema for order timeline."""
    
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


class KitchenWorkflowStatusResponse(BaseModel):
    """Response schema for kitchen workflow status."""
    
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


class OrderTrackingResponse(BaseModel):
    """Response schema for comprehensive order tracking."""
    
    order_id: UUID
    order_number: str
    restaurant_id: UUID
    current_status: str
    estimated_completion_time: Optional[datetime] = None
    status_history: List[OrderStatusHistoryResponse] = Field(default_factory=list)
    item_tracking: List[OrderItemTrackingResponse] = Field(default_factory=list)
    timeline: Optional[OrderTimelineResponse] = None
    kitchen_workflow: Optional[KitchenWorkflowStatusResponse] = None
    notifications_sent: List[NotificationHistoryResponse] = Field(default_factory=list)
    last_updated: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class KitchenOrderSummaryResponse(BaseModel):
    """Response schema for kitchen order summary."""
    
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


class NotificationDeliveryMetricsResponse(BaseModel):
    """Response schema for notification delivery metrics."""
    
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


class RealtimeEventResponse(BaseModel):
    """Response schema for real-time events."""
    
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


class ErrorResponse(BaseModel):
    """Response schema for API errors."""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Error details")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="Error timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "error": "ORDER_NOT_FOUND",
                "message": "Order not found with ID: 123e4567-e89b-12d3-a456-426614174000",
                "details": {
                    "order_id": "123e4567-e89b-12d3-a456-426614174000"
                },
                "timestamp": "2024-01-15T14:30:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """Response schema for successful operations."""
    
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional response data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="Response timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "success": True,
                "message": "Order status updated successfully",
                "data": {
                    "order_id": "123e4567-e89b-12d3-a456-426614174000",
                    "new_status": "preparing"
                },
                "timestamp": "2024-01-15T14:30:00Z"
            }
        }
