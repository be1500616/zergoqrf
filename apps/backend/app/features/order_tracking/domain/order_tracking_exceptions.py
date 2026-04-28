"""Order tracking domain exceptions.

This module contains custom exceptions for the order tracking domain,
providing specific error handling for tracking operations and business rules.
"""

from typing import Dict, Any, Optional
from uuid import UUID


class OrderTrackingDomainError(Exception):
    """Base exception for order tracking domain errors."""
    
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        """Initialize domain error with structured information."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class OrderTrackingNotFoundError(OrderTrackingDomainError):
    """Raised when order tracking information is not found."""
    
    def __init__(self, order_id: UUID):
        """Initialize order tracking not found error."""
        message = f"Order tracking information not found for order {order_id}"
        details = {"order_id": str(order_id)}
        super().__init__(message, "ORDER_TRACKING_NOT_FOUND", details)


class InvalidStatusTransitionError(OrderTrackingDomainError):
    """Raised when an invalid status transition is attempted."""
    
    def __init__(self, message: str, error_code: str, details: Dict[str, Any]):
        """Initialize invalid status transition error."""
        super().__init__(message, error_code, details)


class OrderStatusHistoryNotFoundError(OrderTrackingDomainError):
    """Raised when order status history is not found."""
    
    def __init__(self, order_id: UUID):
        """Initialize order status history not found error."""
        message = f"Order status history not found for order {order_id}"
        details = {"order_id": str(order_id)}
        super().__init__(message, "ORDER_STATUS_HISTORY_NOT_FOUND", details)


class NotificationPreferenceNotFoundError(OrderTrackingDomainError):
    """Raised when notification preferences are not found."""
    
    def __init__(self, restaurant_id: UUID, customer_identifier: str):
        """Initialize notification preference not found error."""
        message = f"Notification preferences not found for customer {customer_identifier} in restaurant {restaurant_id}"
        details = {
            "restaurant_id": str(restaurant_id),
            "customer_identifier": customer_identifier
        }
        super().__init__(message, "NOTIFICATION_PREFERENCE_NOT_FOUND", details)


class NotificationDeliveryError(OrderTrackingDomainError):
    """Raised when notification delivery fails."""
    
    def __init__(self, channel: str, recipient: str, reason: str, order_id: UUID = None):
        """Initialize notification delivery error."""
        message = f"Failed to deliver {channel} notification to {recipient}: {reason}"
        details = {
            "channel": channel,
            "recipient": recipient,
            "reason": reason
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "NOTIFICATION_DELIVERY_FAILED", details)


class NotificationChannelNotSupportedError(OrderTrackingDomainError):
    """Raised when notification channel is not supported."""
    
    def __init__(self, channel: str, restaurant_id: UUID = None):
        """Initialize notification channel not supported error."""
        message = f"Notification channel '{channel}' is not supported"
        details = {"channel": channel}
        if restaurant_id:
            details["restaurant_id"] = str(restaurant_id)
        
        super().__init__(message, "NOTIFICATION_CHANNEL_NOT_SUPPORTED", details)


class InvalidTimelineEventError(OrderTrackingDomainError):
    """Raised when timeline event is invalid."""
    
    def __init__(self, event_type: str, reason: str, order_id: UUID = None):
        """Initialize invalid timeline event error."""
        message = f"Invalid timeline event '{event_type}': {reason}"
        details = {
            "event_type": event_type,
            "reason": reason
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "INVALID_TIMELINE_EVENT", details)


class OrderItemTrackingNotFoundError(OrderTrackingDomainError):
    """Raised when order item tracking is not found."""
    
    def __init__(self, order_item_id: UUID, order_id: UUID = None):
        """Initialize order item tracking not found error."""
        message = f"Order item tracking not found for item {order_item_id}"
        details = {"order_item_id": str(order_item_id)}
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "ORDER_ITEM_TRACKING_NOT_FOUND", details)


class KitchenWorkflowError(OrderTrackingDomainError):
    """Raised when kitchen workflow operation fails."""
    
    def __init__(self, operation: str, reason: str, order_id: UUID = None):
        """Initialize kitchen workflow error."""
        message = f"Kitchen workflow operation '{operation}' failed: {reason}"
        details = {
            "operation": operation,
            "reason": reason
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "KITCHEN_WORKFLOW_ERROR", details)


class RealtimeConnectionError(OrderTrackingDomainError):
    """Raised when real-time connection fails."""
    
    def __init__(self, reason: str, channel: str = None):
        """Initialize real-time connection error."""
        message = f"Real-time connection failed: {reason}"
        details = {"reason": reason}
        if channel:
            details["channel"] = channel
        
        super().__init__(message, "REALTIME_CONNECTION_ERROR", details)


class RealtimeBroadcastError(OrderTrackingDomainError):
    """Raised when real-time broadcast fails."""
    
    def __init__(self, event_type: str, reason: str, order_id: UUID = None):
        """Initialize real-time broadcast error."""
        message = f"Failed to broadcast {event_type} event: {reason}"
        details = {
            "event_type": event_type,
            "reason": reason
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "REALTIME_BROADCAST_ERROR", details)


class ETACalculationError(OrderTrackingDomainError):
    """Raised when ETA calculation fails."""
    
    def __init__(self, reason: str, order_id: UUID = None):
        """Initialize ETA calculation error."""
        message = f"ETA calculation failed: {reason}"
        details = {"reason": reason}
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "ETA_CALCULATION_ERROR", details)


class NotificationRateLimitError(OrderTrackingDomainError):
    """Raised when notification rate limit is exceeded."""
    
    def __init__(self, channel: str, recipient: str, limit: int, window_minutes: int):
        """Initialize notification rate limit error."""
        message = f"Rate limit exceeded for {channel} notifications to {recipient}: {limit} per {window_minutes} minutes"
        details = {
            "channel": channel,
            "recipient": recipient,
            "limit": limit,
            "window_minutes": window_minutes
        }
        super().__init__(message, "NOTIFICATION_RATE_LIMIT_EXCEEDED", details)


class OrderTrackingPermissionError(OrderTrackingDomainError):
    """Raised when user lacks permission for order tracking operation."""
    
    def __init__(self, operation: str, user_id: UUID = None, order_id: UUID = None):
        """Initialize order tracking permission error."""
        message = f"Permission denied for operation: {operation}"
        details = {"operation": operation}
        if user_id:
            details["user_id"] = str(user_id)
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "ORDER_TRACKING_PERMISSION_DENIED", details)


class OrderTrackingConfigurationError(OrderTrackingDomainError):
    """Raised when order tracking configuration is invalid."""
    
    def __init__(self, setting: str, reason: str, restaurant_id: UUID = None):
        """Initialize order tracking configuration error."""
        message = f"Invalid configuration for '{setting}': {reason}"
        details = {
            "setting": setting,
            "reason": reason
        }
        if restaurant_id:
            details["restaurant_id"] = str(restaurant_id)
        
        super().__init__(message, "ORDER_TRACKING_CONFIGURATION_ERROR", details)


class NotificationTemplateError(OrderTrackingDomainError):
    """Raised when notification template processing fails."""
    
    def __init__(self, template_type: str, reason: str, order_id: UUID = None):
        """Initialize notification template error."""
        message = f"Notification template error for '{template_type}': {reason}"
        details = {
            "template_type": template_type,
            "reason": reason
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "NOTIFICATION_TEMPLATE_ERROR", details)


class OrderTrackingDataIntegrityError(OrderTrackingDomainError):
    """Raised when order tracking data integrity is compromised."""
    
    def __init__(self, data_type: str, reason: str, order_id: UUID = None):
        """Initialize order tracking data integrity error."""
        message = f"Data integrity error for '{data_type}': {reason}"
        details = {
            "data_type": data_type,
            "reason": reason
        }
        if order_id:
            details["order_id"] = str(order_id)
        
        super().__init__(message, "ORDER_TRACKING_DATA_INTEGRITY_ERROR", details)


class OrderTrackingServiceUnavailableError(OrderTrackingDomainError):
    """Raised when order tracking service is temporarily unavailable."""
    
    def __init__(self, service: str, reason: str):
        """Initialize order tracking service unavailable error."""
        message = f"Order tracking service '{service}' is temporarily unavailable: {reason}"
        details = {
            "service": service,
            "reason": reason
        }
        super().__init__(message, "ORDER_TRACKING_SERVICE_UNAVAILABLE", details)
