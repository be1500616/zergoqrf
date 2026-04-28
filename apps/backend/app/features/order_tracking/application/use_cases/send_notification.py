"""Send notification use case.

This module contains the use case for sending order tracking notifications
through multiple channels with comprehensive delivery tracking.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from ...domain.order_tracking_entities import NotificationHistory
from ...domain.order_tracking_enums import (
    NotificationChannel, NotificationStatus, NotificationTrigger
)
from ...domain.order_tracking_repos import (
    INotificationHistoryRepository, IRealtimeEventRepository
)
from ...domain.order_tracking_exceptions import (
    NotificationDeliveryError, NotificationChannelNotSupportedError,
    NotificationRateLimitError
)
from ..order_tracking_dtos import (
    SendNotificationRequestDTO, NotificationHistoryDTO,
    notification_history_entity_to_dto
)

# Import from existing orders feature
from ....orders.domain.order_repos import IOrderRepository
from ....orders.domain.order_exceptions import OrderNotFoundError

logger = logging.getLogger(__name__)


class SendNotificationUseCase:
    """Use case for sending order tracking notifications."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        notification_repository: INotificationHistoryRepository,
        realtime_repository: IRealtimeEventRepository,
        email_service: 'IEmailNotificationService',
        whatsapp_service: 'IWhatsAppNotificationService',
        sms_service: 'ISMSNotificationService',
    ):
        """Initialize send notification use case.
        
        Args:
            order_repository: Repository for order operations
            notification_repository: Repository for notification operations
            realtime_repository: Repository for real-time events
            email_service: Email notification service
            whatsapp_service: WhatsApp notification service
            sms_service: SMS notification service
        """
        self._order_repository = order_repository
        self._notification_repository = notification_repository
        self._realtime_repository = realtime_repository
        self._email_service = email_service
        self._whatsapp_service = whatsapp_service
        self._sms_service = sms_service
    
    async def execute(self, request: SendNotificationRequestDTO) -> List[NotificationHistoryDTO]:
        """Execute notification sending across multiple channels.
        
        Args:
            request: Send notification request DTO
            
        Returns:
            List of notification history DTOs
            
        Raises:
            OrderNotFoundError: If order is not found
            NotificationChannelNotSupportedError: If channel is not supported
        """
        logger.info(f"Sending notifications for order {request.order_id} with trigger {request.trigger.value}")
        
        try:
            # 1. Validate order exists
            order = await self._order_repository.get_by_id(request.order_id)
            if not order:
                raise OrderNotFoundError(request.order_id)
            
            # 2. Get customer contact information
            customer_email = order.customer_info.email if hasattr(order.customer_info, 'email') else None
            customer_phone = order.customer_info.phone if hasattr(order.customer_info, 'phone') else None
            customer_name = order.customer_info.name if hasattr(order.customer_info, 'name') else "Customer"
            
            # 3. Prepare notification content
            message_content = self._build_message_content(
                trigger=request.trigger,
                order=order,
                custom_message=request.custom_message
            )
            
            subject = self._build_subject(
                trigger=request.trigger,
                order=order,
                custom_subject=request.custom_subject
            )
            
            # 4. Send notifications through each requested channel
            notification_results = []
            
            for channel in request.channels:
                try:
                    # Check rate limits
                    recipient = self._get_recipient_for_channel(channel, customer_email, customer_phone)
                    if not recipient:
                        logger.warning(f"No recipient available for channel {channel.value}")
                        continue
                    
                    await self._check_rate_limits(channel, recipient)
                    
                    # Create notification history entry
                    notification = NotificationHistory(
                        id=uuid4(),
                        order_id=request.order_id,
                        restaurant_id=order.restaurant_id,
                        channel=channel,
                        recipient=recipient,
                        subject=subject,
                        message_content=message_content,
                        status=NotificationStatus.PENDING,
                        created_at=datetime.now(timezone.utc),
                    )
                    
                    # Save notification history
                    created_notification = await self._notification_repository.create_notification_history(notification)
                    
                    # Send notification through appropriate service
                    success = await self._send_through_channel(
                        channel=channel,
                        recipient=recipient,
                        subject=subject,
                        message=message_content,
                        notification=created_notification,
                        order=order
                    )
                    
                    if success:
                        created_notification.mark_sent()
                        await self._notification_repository.update_notification_history(created_notification)
                        
                        # Broadcast notification sent event
                        await self._realtime_repository.broadcast_notification_sent(
                            order_id=request.order_id,
                            channel=channel.value,
                            recipient=recipient,
                            status="sent"
                        )
                    
                    notification_results.append(notification_history_entity_to_dto(created_notification))
                    
                except Exception as e:
                    logger.error(f"Failed to send {channel.value} notification for order {request.order_id}: {e}")
                    # Continue with other channels even if one fails
                    continue
            
            logger.info(f"Successfully processed {len(notification_results)} notifications for order {request.order_id}")
            return notification_results
            
        except Exception as e:
            logger.error(f"Failed to send notifications for order {request.order_id}: {e}")
            raise
    
    def _build_message_content(
        self,
        trigger: NotificationTrigger,
        order,
        custom_message: Optional[str] = None
    ) -> str:
        """Build notification message content.
        
        Args:
            trigger: Notification trigger
            order: Order entity
            custom_message: Optional custom message
            
        Returns:
            Formatted message content
        """
        if custom_message:
            template = trigger.get_default_message_template()
            return template.format(
                order_number=order.order_number.value,
                custom_message=custom_message,
                restaurant_name=getattr(order, 'restaurant_name', 'Restaurant'),
                customer_name=getattr(order.customer_info, 'name', 'Customer'),
                eta=self._format_eta(order)
            )
        
        template = trigger.get_default_message_template()
        return template.format(
            order_number=order.order_number.value,
            restaurant_name=getattr(order, 'restaurant_name', 'Restaurant'),
            customer_name=getattr(order.customer_info, 'name', 'Customer'),
            eta=self._format_eta(order)
        )
    
    def _build_subject(
        self,
        trigger: NotificationTrigger,
        order,
        custom_subject: Optional[str] = None
    ) -> str:
        """Build notification subject.
        
        Args:
            trigger: Notification trigger
            order: Order entity
            custom_subject: Optional custom subject
            
        Returns:
            Formatted subject
        """
        if custom_subject:
            return custom_subject.format(
                order_number=order.order_number.value,
                restaurant_name=getattr(order, 'restaurant_name', 'Restaurant')
            )
        
        template = trigger.get_subject_template()
        return template.format(
            order_number=order.order_number.value,
            restaurant_name=getattr(order, 'restaurant_name', 'Restaurant')
        )
    
    def _get_recipient_for_channel(
        self,
        channel: NotificationChannel,
        customer_email: Optional[str],
        customer_phone: Optional[str]
    ) -> Optional[str]:
        """Get recipient for notification channel.
        
        Args:
            channel: Notification channel
            customer_email: Customer email address
            customer_phone: Customer phone number
            
        Returns:
            Recipient identifier for the channel
        """
        if channel == NotificationChannel.EMAIL:
            return customer_email
        elif channel in [NotificationChannel.WHATSAPP, NotificationChannel.SMS]:
            return customer_phone
        else:
            return None
    
    def _format_eta(self, order) -> str:
        """Format estimated completion time for display.
        
        Args:
            order: Order entity
            
        Returns:
            Formatted ETA string
        """
        if hasattr(order, 'estimated_preparation_time') and order.estimated_preparation_time:
            return f"{order.estimated_preparation_time} minutes"
        return "soon"
    
    async def _check_rate_limits(self, channel: NotificationChannel, recipient: str) -> None:
        """Check notification rate limits.
        
        Args:
            channel: Notification channel
            recipient: Recipient identifier
            
        Raises:
            NotificationRateLimitError: If rate limit is exceeded
        """
        # Get recent notifications for this recipient and channel
        recent_notifications = await self._notification_repository.get_by_channel_and_recipient(
            channel=channel,
            recipient=recipient,
            start_date=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        )
        
        # Define rate limits per channel
        rate_limits = {
            NotificationChannel.EMAIL: 10,  # 10 emails per day
            NotificationChannel.WHATSAPP: 5,  # 5 WhatsApp messages per day
            NotificationChannel.SMS: 3,  # 3 SMS per day
        }
        
        limit = rate_limits.get(channel, 10)
        if len(recent_notifications) >= limit:
            raise NotificationRateLimitError(
                channel=channel.value,
                recipient=recipient,
                limit=limit,
                window_minutes=1440  # 24 hours
            )
    
    async def _send_through_channel(
        self,
        channel: NotificationChannel,
        recipient: str,
        subject: str,
        message: str,
        notification: NotificationHistory,
        order
    ) -> bool:
        """Send notification through specific channel.
        
        Args:
            channel: Notification channel
            recipient: Recipient identifier
            subject: Message subject
            message: Message content
            notification: Notification history entity
            order: Order entity
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._email_service.send_email(
                    to=recipient,
                    subject=subject,
                    body=message,
                    order_id=str(order.id),
                    notification_id=str(notification.id)
                )
            elif channel == NotificationChannel.WHATSAPP:
                return await self._whatsapp_service.send_message(
                    to=recipient,
                    message=message,
                    order_id=str(order.id),
                    notification_id=str(notification.id)
                )
            elif channel == NotificationChannel.SMS:
                return await self._sms_service.send_sms(
                    to=recipient,
                    message=message,
                    order_id=str(order.id),
                    notification_id=str(notification.id)
                )
            else:
                raise NotificationChannelNotSupportedError(channel.value)
                
        except Exception as e:
            logger.error(f"Failed to send {channel.value} notification: {e}")
            notification.mark_failed(str(e))
            await self._notification_repository.update_notification_history(notification)
            return False


class RetryFailedNotificationsUseCase:
    """Use case for retrying failed notifications."""
    
    def __init__(
        self,
        notification_repository: INotificationHistoryRepository,
        send_notification_use_case: SendNotificationUseCase,
    ):
        """Initialize retry failed notifications use case.
        
        Args:
            notification_repository: Repository for notification operations
            send_notification_use_case: Main notification sending use case
        """
        self._notification_repository = notification_repository
        self._send_notification_use_case = send_notification_use_case
    
    async def execute(self, max_retries: int = 3) -> List[NotificationHistoryDTO]:
        """Execute retry of failed notifications.
        
        Args:
            max_retries: Maximum number of retries to attempt
            
        Returns:
            List of notification history DTOs for retried notifications
        """
        logger.info("Retrying failed notifications")
        
        try:
            # Get failed notifications eligible for retry
            failed_notifications = await self._notification_repository.get_failed_notifications(
                retry_eligible_only=True
            )
            
            retried_notifications = []
            
            for notification in failed_notifications:
                try:
                    if notification.can_retry():
                        # Increment retry count
                        notification.increment_retry_count()
                        
                        # Attempt to resend
                        success = await self._send_notification_use_case._send_through_channel(
                            channel=notification.channel,
                            recipient=notification.recipient,
                            subject=notification.subject,
                            message=notification.message_content,
                            notification=notification,
                            order=None  # Would need to fetch order if needed
                        )
                        
                        if success:
                            notification.mark_sent()
                        
                        # Update notification history
                        updated_notification = await self._notification_repository.update_notification_history(notification)
                        retried_notifications.append(notification_history_entity_to_dto(updated_notification))
                        
                except Exception as e:
                    logger.error(f"Failed to retry notification {notification.id}: {e}")
                    continue
            
            logger.info(f"Successfully retried {len(retried_notifications)} notifications")
            return retried_notifications
            
        except Exception as e:
            logger.error(f"Failed to retry failed notifications: {e}")
            raise
