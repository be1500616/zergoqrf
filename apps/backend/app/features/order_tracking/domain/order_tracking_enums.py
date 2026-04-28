"""Order tracking domain enumerations.

This module contains enumerations for order tracking status, notification
channels, and other domain-specific constants that extend the base order system.
"""

from enum import Enum
from typing import List, Set


class OrderItemStatus(Enum):
    """Individual order item status enumeration for kitchen workflow."""
    
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    CANCELLED = "cancelled"
    
    def can_transition_to(self, new_status: 'OrderItemStatus') -> bool:
        """Check if transition to new status is valid."""
        valid_transitions = {
            OrderItemStatus.PENDING: {OrderItemStatus.PREPARING, OrderItemStatus.CANCELLED},
            OrderItemStatus.PREPARING: {OrderItemStatus.READY, OrderItemStatus.CANCELLED},
            OrderItemStatus.READY: {OrderItemStatus.SERVED, OrderItemStatus.CANCELLED},
            OrderItemStatus.SERVED: set(),  # Terminal state
            OrderItemStatus.CANCELLED: set(),  # Terminal state
        }
        return new_status in valid_transitions.get(self, set())
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal status."""
        return self in {OrderItemStatus.SERVED, OrderItemStatus.CANCELLED}
    
    def get_display_name(self) -> str:
        """Get human-readable display name."""
        display_names = {
            OrderItemStatus.PENDING: "Pending",
            OrderItemStatus.PREPARING: "Preparing",
            OrderItemStatus.READY: "Ready",
            OrderItemStatus.SERVED: "Served",
            OrderItemStatus.CANCELLED: "Cancelled",
        }
        return display_names[self]
    
    def get_display_color(self) -> str:
        """Get display color for UI components."""
        colors = {
            OrderItemStatus.PENDING: "#6B7280",      # Gray
            OrderItemStatus.PREPARING: "#F59E0B",    # Amber
            OrderItemStatus.READY: "#10B981",        # Emerald
            OrderItemStatus.SERVED: "#059669",       # Green
            OrderItemStatus.CANCELLED: "#EF4444",    # Red
        }
        return colors[self]


class NotificationChannel(Enum):
    """Notification channel enumeration for extensible messaging."""
    
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    PUSH = "push"
    
    def get_display_name(self) -> str:
        """Get human-readable display name."""
        display_names = {
            NotificationChannel.EMAIL: "Email",
            NotificationChannel.WHATSAPP: "WhatsApp",
            NotificationChannel.SMS: "SMS",
            NotificationChannel.PUSH: "Push Notification",
        }
        return display_names[self]
    
    def is_enabled_by_default(self) -> bool:
        """Check if channel is enabled by default for new customers."""
        return self == NotificationChannel.EMAIL
    
    def requires_phone_number(self) -> bool:
        """Check if channel requires phone number."""
        return self in {NotificationChannel.WHATSAPP, NotificationChannel.SMS}
    
    def requires_email_address(self) -> bool:
        """Check if channel requires email address."""
        return self == NotificationChannel.EMAIL
    
    def supports_rich_content(self) -> bool:
        """Check if channel supports rich content (HTML, images, etc.)."""
        return self in {NotificationChannel.EMAIL, NotificationChannel.PUSH}


class NotificationStatus(Enum):
    """Notification delivery status enumeration."""
    
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal status."""
        return self in {
            NotificationStatus.DELIVERED,
            NotificationStatus.FAILED,
            NotificationStatus.BOUNCED,
            NotificationStatus.OPENED,
            NotificationStatus.CLICKED,
        }
    
    def is_successful(self) -> bool:
        """Check if notification was successfully delivered."""
        return self in {
            NotificationStatus.DELIVERED,
            NotificationStatus.OPENED,
            NotificationStatus.CLICKED,
        }
    
    def get_display_name(self) -> str:
        """Get human-readable display name."""
        display_names = {
            NotificationStatus.PENDING: "Pending",
            NotificationStatus.SENT: "Sent",
            NotificationStatus.DELIVERED: "Delivered",
            NotificationStatus.FAILED: "Failed",
            NotificationStatus.BOUNCED: "Bounced",
            NotificationStatus.OPENED: "Opened",
            NotificationStatus.CLICKED: "Clicked",
        }
        return display_names[self]


class NotificationTrigger(Enum):
    """Notification trigger events for order tracking."""
    
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_PREPARING = "order_preparing"
    ORDER_READY = "order_ready"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    ETA_UPDATED = "eta_updated"
    ITEM_READY = "item_ready"
    CUSTOM = "custom"
    
    def get_default_message_template(self) -> str:
        """Get default message template for trigger."""
        templates = {
            NotificationTrigger.ORDER_CONFIRMED: "Your order #{order_number} has been confirmed! Estimated preparation time: {eta}",
            NotificationTrigger.ORDER_PREPARING: "Great news! Your order #{order_number} is now being prepared by our kitchen team.",
            NotificationTrigger.ORDER_READY: "Your order #{order_number} is ready for pickup! Please collect it from the counter.",
            NotificationTrigger.ORDER_COMPLETED: "Thank you! Your order #{order_number} has been completed. We hope you enjoyed your meal!",
            NotificationTrigger.ORDER_CANCELLED: "We're sorry, but your order #{order_number} has been cancelled. Please contact us for assistance.",
            NotificationTrigger.ETA_UPDATED: "Update: Your order #{order_number} estimated completion time has been updated to {eta}",
            NotificationTrigger.ITEM_READY: "One of your items from order #{order_number} is ready: {item_name}",
            NotificationTrigger.CUSTOM: "Order #{order_number}: {custom_message}",
        }
        return templates[self]
    
    def get_subject_template(self) -> str:
        """Get email subject template for trigger."""
        subjects = {
            NotificationTrigger.ORDER_CONFIRMED: "Order Confirmed - #{order_number}",
            NotificationTrigger.ORDER_PREPARING: "Order Being Prepared - #{order_number}",
            NotificationTrigger.ORDER_READY: "Order Ready for Pickup - #{order_number}",
            NotificationTrigger.ORDER_COMPLETED: "Order Completed - #{order_number}",
            NotificationTrigger.ORDER_CANCELLED: "Order Cancelled - #{order_number}",
            NotificationTrigger.ETA_UPDATED: "Order ETA Updated - #{order_number}",
            NotificationTrigger.ITEM_READY: "Item Ready - #{order_number}",
            NotificationTrigger.CUSTOM: "Order Update - #{order_number}",
        }
        return subjects[self]
    
    def should_send_immediately(self) -> bool:
        """Check if notification should be sent immediately."""
        immediate_triggers = {
            NotificationTrigger.ORDER_CONFIRMED,
            NotificationTrigger.ORDER_READY,
            NotificationTrigger.ORDER_CANCELLED,
        }
        return self in immediate_triggers


class OrderTrackingEventType(Enum):
    """Real-time event types for order tracking."""
    
    STATUS_UPDATED = "status_updated"
    ITEM_STATUS_UPDATED = "item_status_updated"
    ETA_UPDATED = "eta_updated"
    NOTIFICATION_SENT = "notification_sent"
    TIMELINE_UPDATED = "timeline_updated"
    
    def get_channel_name(self, order_id: str) -> str:
        """Get Supabase Realtime channel name for event."""
        return f"order_tracking:{order_id}:{self.value}"
    
    def get_broadcast_payload_schema(self) -> dict:
        """Get expected payload schema for broadcast."""
        schemas = {
            OrderTrackingEventType.STATUS_UPDATED: {
                "order_id": "string",
                "new_status": "string",
                "previous_status": "string",
                "estimated_completion_time": "string|null",
                "changed_by": "string|null",
                "timestamp": "string"
            },
            OrderTrackingEventType.ITEM_STATUS_UPDATED: {
                "order_id": "string",
                "item_id": "string",
                "item_name": "string",
                "new_status": "string",
                "previous_status": "string",
                "timestamp": "string"
            },
            OrderTrackingEventType.ETA_UPDATED: {
                "order_id": "string",
                "new_eta": "string",
                "previous_eta": "string|null",
                "reason": "string|null",
                "timestamp": "string"
            },
            OrderTrackingEventType.NOTIFICATION_SENT: {
                "order_id": "string",
                "channel": "string",
                "recipient": "string",
                "status": "string",
                "timestamp": "string"
            },
            OrderTrackingEventType.TIMELINE_UPDATED: {
                "order_id": "string",
                "timeline_events": "array",
                "timestamp": "string"
            }
        }
        return schemas[self]


class KitchenDisplayPriority(Enum):
    """Kitchen display priority for order management."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    
    def get_sort_order(self) -> int:
        """Get sort order for kitchen display (lower = higher priority)."""
        sort_orders = {
            KitchenDisplayPriority.URGENT: 1,
            KitchenDisplayPriority.HIGH: 2,
            KitchenDisplayPriority.NORMAL: 3,
            KitchenDisplayPriority.LOW: 4,
        }
        return sort_orders[self]
    
    def get_display_color(self) -> str:
        """Get display color for kitchen interface."""
        colors = {
            KitchenDisplayPriority.LOW: "#6B7280",      # Gray
            KitchenDisplayPriority.NORMAL: "#3B82F6",   # Blue
            KitchenDisplayPriority.HIGH: "#F59E0B",     # Amber
            KitchenDisplayPriority.URGENT: "#EF4444",   # Red
        }
        return colors[self]
    
    def get_preparation_time_multiplier(self) -> float:
        """Get preparation time multiplier based on priority."""
        multipliers = {
            KitchenDisplayPriority.LOW: 1.2,      # 20% longer
            KitchenDisplayPriority.NORMAL: 1.0,   # Standard time
            KitchenDisplayPriority.HIGH: 0.8,     # 20% faster
            KitchenDisplayPriority.URGENT: 0.6,   # 40% faster
        }
        return multipliers[self]
