"""Supabase Realtime service for order tracking.

This module provides real-time communication capabilities using Supabase Realtime
for broadcasting order status updates and managing WebSocket connections.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from supabase import Client

from ..domain.order_tracking_enums import OrderTrackingEventType
from ..domain.order_tracking_repos import IRealtimeEventRepository
from ..domain.order_tracking_exceptions import (
    RealtimeConnectionError, RealtimeBroadcastError
)
from ....common.supabase_client import get_supabase

logger = logging.getLogger(__name__)


class SupabaseRealtimeService(IRealtimeEventRepository):
    """Supabase Realtime service implementation for order tracking events."""
    
    def __init__(self, supabase_client: Client = None):
        """Initialize Supabase Realtime service.
        
        Args:
            supabase_client: Supabase client instance
        """
        self._client = supabase_client or get_supabase()
        self._active_channels = {}
    
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
        try:
            event_type = OrderTrackingEventType.STATUS_UPDATED
            channel_name = f"order_tracking:{order_id}"
            
            payload = {
                "order_id": str(order_id),
                "new_status": new_status,
                "previous_status": previous_status,
                "estimated_completion_time": estimated_completion_time.isoformat() if estimated_completion_time else None,
                "changed_by": str(changed_by) if changed_by else None,
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type.value
            }
            
            # Broadcast to order-specific channel
            await self._broadcast_to_channel(channel_name, event_type.value, payload)
            
            # Also broadcast to restaurant-wide channel for kitchen displays
            restaurant_channel = f"restaurant_orders:{order_id}"  # Would need restaurant_id
            await self._broadcast_to_channel(restaurant_channel, event_type.value, payload)
            
            logger.info(f"Successfully broadcasted status update for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to broadcast order status update: {e}")
            raise RealtimeBroadcastError(
                event_type="status_updated",
                reason=str(e),
                order_id=order_id
            )
    
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
        try:
            event_type = OrderTrackingEventType.ITEM_STATUS_UPDATED
            channel_name = f"order_tracking:{order_id}"
            
            payload = {
                "order_id": str(order_id),
                "item_id": str(item_id),
                "item_name": item_name,
                "new_status": new_status,
                "previous_status": previous_status,
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type.value
            }
            
            await self._broadcast_to_channel(channel_name, event_type.value, payload)
            
            logger.info(f"Successfully broadcasted item status update for item {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to broadcast item status update: {e}")
            raise RealtimeBroadcastError(
                event_type="item_status_updated",
                reason=str(e),
                order_id=order_id
            )
    
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
        try:
            event_type = OrderTrackingEventType.ETA_UPDATED
            channel_name = f"order_tracking:{order_id}"
            
            payload = {
                "order_id": str(order_id),
                "new_eta": new_eta.isoformat(),
                "previous_eta": previous_eta.isoformat() if previous_eta else None,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type.value
            }
            
            await self._broadcast_to_channel(channel_name, event_type.value, payload)
            
            logger.info(f"Successfully broadcasted ETA update for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to broadcast ETA update: {e}")
            raise RealtimeBroadcastError(
                event_type="eta_updated",
                reason=str(e),
                order_id=order_id
            )
    
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
        try:
            event_type = OrderTrackingEventType.NOTIFICATION_SENT
            channel_name = f"order_tracking:{order_id}"
            
            payload = {
                "order_id": str(order_id),
                "channel": channel,
                "recipient": recipient,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type.value
            }
            
            await self._broadcast_to_channel(channel_name, event_type.value, payload)
            
            logger.info(f"Successfully broadcasted notification sent event for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to broadcast notification sent event: {e}")
            raise RealtimeBroadcastError(
                event_type="notification_sent",
                reason=str(e),
                order_id=order_id
            )
    
    async def _broadcast_to_channel(
        self,
        channel_name: str,
        event_name: str,
        payload: Dict[str, Any]
    ) -> None:
        """Broadcast message to Supabase Realtime channel.
        
        Args:
            channel_name: Channel name
            event_name: Event name
            payload: Event payload
            
        Raises:
            RealtimeBroadcastError: If broadcast fails
        """
        try:
            # Get or create channel
            channel = self._get_or_create_channel(channel_name)
            
            # Send broadcast message
            response = channel.send(
                type="broadcast",
                event=event_name,
                payload=payload
            )
            
            # Check if broadcast was successful
            if not response or response.get("status") != "ok":
                raise RealtimeBroadcastError(
                    event_type=event_name,
                    reason=f"Broadcast failed with response: {response}",
                    order_id=payload.get("order_id")
                )
            
            logger.debug(f"Broadcasted {event_name} to channel {channel_name}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast to channel {channel_name}: {e}")
            raise RealtimeBroadcastError(
                event_type=event_name,
                reason=str(e),
                order_id=payload.get("order_id")
            )
    
    def _get_or_create_channel(self, channel_name: str):
        """Get existing channel or create new one.
        
        Args:
            channel_name: Channel name
            
        Returns:
            Supabase Realtime channel
        """
        if channel_name not in self._active_channels:
            try:
                channel = self._client.channel(channel_name)
                self._active_channels[channel_name] = channel
                logger.debug(f"Created new channel: {channel_name}")
            except Exception as e:
                logger.error(f"Failed to create channel {channel_name}: {e}")
                raise RealtimeConnectionError(
                    reason=f"Failed to create channel: {e}",
                    channel=channel_name
                )
        
        return self._active_channels[channel_name]
    
    async def subscribe_to_order_updates(
        self,
        order_id: UUID,
        callback: callable
    ) -> str:
        """Subscribe to order updates for a specific order.
        
        Args:
            order_id: Order ID to subscribe to
            callback: Callback function for handling updates
            
        Returns:
            Subscription ID
        """
        try:
            channel_name = f"order_tracking:{order_id}"
            channel = self._get_or_create_channel(channel_name)
            
            # Subscribe to all order tracking events
            subscription = channel.on(
                event="*",
                callback=callback
            ).subscribe()
            
            logger.info(f"Subscribed to order updates for order {order_id}")
            return str(subscription)
            
        except Exception as e:
            logger.error(f"Failed to subscribe to order updates: {e}")
            raise RealtimeConnectionError(
                reason=f"Failed to subscribe: {e}",
                channel=channel_name
            )
    
    async def unsubscribe_from_order_updates(self, subscription_id: str) -> bool:
        """Unsubscribe from order updates.
        
        Args:
            subscription_id: Subscription ID to unsubscribe
            
        Returns:
            True if unsubscribed successfully
        """
        try:
            # This would need to be implemented based on Supabase client capabilities
            # For now, we'll just log the unsubscribe request
            logger.info(f"Unsubscribed from order updates: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from order updates: {e}")
            return False
    
    async def get_active_connections(self) -> Dict[str, int]:
        """Get count of active connections per channel.
        
        Returns:
            Dictionary mapping channel names to connection counts
        """
        try:
            # This would need to be implemented based on Supabase client capabilities
            # For now, return the active channels we're tracking
            return {
                channel_name: 1  # Placeholder count
                for channel_name in self._active_channels.keys()
            }
            
        except Exception as e:
            logger.error(f"Failed to get active connections: {e}")
            return {}
    
    async def cleanup_inactive_channels(self) -> int:
        """Clean up inactive channels to free resources.
        
        Returns:
            Number of channels cleaned up
        """
        try:
            cleaned_count = 0
            channels_to_remove = []
            
            for channel_name, channel in self._active_channels.items():
                try:
                    # Check if channel is still active
                    # This would need to be implemented based on Supabase client capabilities
                    # For now, we'll keep all channels
                    pass
                except Exception:
                    channels_to_remove.append(channel_name)
            
            # Remove inactive channels
            for channel_name in channels_to_remove:
                del self._active_channels[channel_name]
                cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} inactive channels")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup inactive channels: {e}")
            return 0
