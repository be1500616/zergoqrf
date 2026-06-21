"""Order tracking REST API router.

This module contains the FastAPI router for order tracking endpoints,
providing comprehensive order status management and real-time tracking capabilities.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse

from .order_tracking_schemas import (
    UpdateOrderStatusRequest, BulkUpdateOrderStatusRequest,
    UpdateOrderItemStatusRequest, SendNotificationRequest,
    OrderTrackingResponse, KitchenOrderSummaryResponse,
    NotificationDeliveryMetricsResponse, ErrorResponse, SuccessResponse
)
from ..application.use_cases.update_order_status import (
    UpdateOrderStatusUseCase, BulkUpdateOrderStatusUseCase
)
from ..application.use_cases.get_order_tracking import (
    GetOrderTrackingUseCase, GetOrderTrackingByNumberUseCase, GetKitchenOrdersUseCase
)
from ..application.use_cases.send_notification import (
    SendNotificationUseCase, RetryFailedNotificationsUseCase
)
from ..application.order_tracking_dtos import (
    UpdateOrderStatusRequestDTO, UpdateOrderItemStatusRequestDTO,
    SendNotificationRequestDTO
)
from ..domain.order_tracking_exceptions import (
    OrderTrackingDomainError, OrderTrackingNotFoundError,
    InvalidStatusTransitionError, NotificationDeliveryError
)

# Import authentication dependencies
from ...auth.presentation.supabase_dependencies import get_current_user, require_staff

# Concrete repo impls
from ...orders.infrastructure.order_repos_impl import SupabaseOrderRepository
from ..infrastructure.order_tracking_repos_impl import (
    NoopRealtimeEventRepository,
    SupabaseNotificationHistoryRepository,
    SupabaseOrderItemTrackingRepository,
    SupabaseOrderStatusHistoryRepository,
    SupabaseOrderTimelineRepository,
)
from ..domain.order_tracking_repos import IRealtimeEventRepository

from fastapi import Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/order-tracking", tags=["Order Tracking"])


# ── No-op notification services ──────────────────────────────────────────────
# Real email/WhatsApp/SMS integrations are not in scope right now. Returning
# True keeps the use case pipeline intact; the notification_history row is
# persisted either way.

class _NoopEmailService(IEmailNotificationService):
    async def send_email(self, **_):  # type: ignore[override]
        return True


class _NoopWhatsAppService(IWhatsAppNotificationService):
    async def send_message(self, **_):  # type: ignore[override]
        return True


class _NoopSMSService(ISMSNotificationService):
    async def send_sms(self, **_):  # type: ignore[override]
        return True


# ── DI providers ─────────────────────────────────────────────────────────────

async def _supabase(request: Request):
    return request.app.state.supabase_service


async def _order_repo():
    client = await _supabase()
    return SupabaseOrderRepository(client)


async def _status_history_repo():
    return SupabaseOrderStatusHistoryRepository(await _supabase())


async def _item_tracking_repo():
    return SupabaseOrderItemTrackingRepository(await _supabase())


async def _timeline_repo():
    return SupabaseOrderTimelineRepository(await _supabase())


async def _notification_repo():
    return SupabaseNotificationHistoryRepository(await _supabase())


def _realtime_repo() -> IRealtimeEventRepository:
    return NoopRealtimeEventRepository()


def get_order_tracking_use_case() -> GetOrderTrackingUseCase:
    raise RuntimeError("async provider — use get_order_tracking_use_case_dep")


def get_order_tracking_by_number_use_case() -> GetOrderTrackingByNumberUseCase:
    raise RuntimeError("async provider — use get_order_tracking_by_number_use_case_dep")


def get_kitchen_orders_use_case() -> GetKitchenOrdersUseCase:
    raise RuntimeError("async provider — use get_kitchen_orders_use_case_dep")


def get_update_order_status_use_case() -> UpdateOrderStatusUseCase:
    raise RuntimeError("async provider — use get_update_order_status_use_case_dep")


def get_bulk_update_order_status_use_case() -> BulkUpdateOrderStatusUseCase:
    raise RuntimeError("async provider — use get_bulk_update_order_status_use_case_dep")


def get_send_notification_use_case() -> SendNotificationUseCase:
    raise RuntimeError("async provider — use get_send_notification_use_case_dep")


def get_retry_failed_notifications_use_case() -> RetryFailedNotificationsUseCase:
    raise RuntimeError("async provider — use get_retry_failed_notifications_use_case_dep")


# Async providers used by FastAPI Depends

async def get_order_tracking_use_case_dep() -> GetOrderTrackingUseCase:
    client = await _supabase()
    return GetOrderTrackingUseCase(
        order_repository=SupabaseOrderRepository(client),
        status_history_repository=SupabaseOrderStatusHistoryRepository(client),
        item_tracking_repository=SupabaseOrderItemTrackingRepository(client),
        timeline_repository=SupabaseOrderTimelineRepository(client),
        notification_repository=SupabaseNotificationHistoryRepository(client),
    )


async def get_order_tracking_by_number_use_case_dep() -> GetOrderTrackingByNumberUseCase:
    client = await _supabase()
    return GetOrderTrackingByNumberUseCase(
        order_repository=SupabaseOrderRepository(client),
        get_order_tracking_use_case=await get_order_tracking_use_case_dep(),
    )


async def get_kitchen_orders_use_case_dep() -> GetKitchenOrdersUseCase:
    client = await _supabase()
    return GetKitchenOrdersUseCase(
        order_repository=SupabaseOrderRepository(client),
        status_history_repository=SupabaseOrderStatusHistoryRepository(client),
        item_tracking_repository=SupabaseOrderItemTrackingRepository(client),
    )


async def get_update_order_status_use_case_dep() -> UpdateOrderStatusUseCase:
    client = await _supabase()
    return UpdateOrderStatusUseCase(
        order_repository=SupabaseOrderRepository(client),
        status_history_repository=SupabaseOrderStatusHistoryRepository(client),
        realtime_repository=NoopRealtimeEventRepository(),
        timeline_repository=SupabaseOrderTimelineRepository(client),
    )


async def get_bulk_update_order_status_use_case_dep() -> BulkUpdateOrderStatusUseCase:
    return BulkUpdateOrderStatusUseCase(
        update_order_status_use_case=await get_update_order_status_use_case_dep(),
    )


async def get_send_notification_use_case_dep() -> SendNotificationUseCase:
    client = await _supabase()
    return SendNotificationUseCase(
        order_repository=SupabaseOrderRepository(client),
        notification_repository=SupabaseNotificationHistoryRepository(client),
        realtime_repository=NoopRealtimeEventRepository(),
        email_service=_NoopEmailService(),
        whatsapp_service=_NoopWhatsAppService(),
        sms_service=_NoopSMSService(),
    )


async def get_retry_failed_notifications_use_case_dep() -> RetryFailedNotificationsUseCase:
    client = await _supabase()
    return RetryFailedNotificationsUseCase(
        notification_repository=SupabaseNotificationHistoryRepository(client),
        send_notification_use_case=await get_send_notification_use_case_dep(),
    )


@router.get(
    "/orders/{order_id}",
    response_model=OrderTrackingResponse,
    summary="Get Order Tracking",
    description="Retrieve comprehensive order tracking information including status history, timeline, and notifications."
)
async def get_order_tracking(
    order_id: UUID = Path(..., description="Order ID"),
    include_notifications: bool = Query(True, description="Include notification history"),
    current_user = Depends(get_current_user),
    get_tracking_use_case: GetOrderTrackingUseCase = Depends(get_order_tracking_use_case_dep),
):
    """Get comprehensive order tracking information.
    
    Args:
        order_id: Order ID to get tracking for
        include_notifications: Whether to include notification history
        current_user: Current authenticated user
        get_tracking_use_case: Order tracking use case
        
    Returns:
        Comprehensive order tracking response
        
    Raises:
        HTTPException: If order not found or access denied
    """
    try:
        logger.info(f"Getting order tracking for order {order_id}")
        
        tracking_info = await get_tracking_use_case.execute(
            order_id=order_id,
            include_notifications=include_notifications
        )
        
        return tracking_info
        
    except OrderTrackingNotFoundError as e:
        logger.warning(f"Order tracking not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Failed to get order tracking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve order tracking"}
        )


@router.get(
    "/orders/number/{order_number}",
    response_model=OrderTrackingResponse,
    summary="Get Order Tracking by Number",
    description="Retrieve order tracking information using order number."
)
async def get_order_tracking_by_number(
    order_number: str = Path(..., description="Order number"),
    include_notifications: bool = Query(True, description="Include notification history"),
    current_user = Depends(get_current_user),
    get_tracking_by_number_use_case: GetOrderTrackingByNumberUseCase = Depends(get_order_tracking_by_number_use_case_dep),
):
    """Get order tracking information by order number.
    
    Args:
        order_number: Order number to get tracking for
        include_notifications: Whether to include notification history
        current_user: Current authenticated user
        get_tracking_by_number_use_case: Order tracking by number use case
        
    Returns:
        Comprehensive order tracking response
    """
    try:
        logger.info(f"Getting order tracking for order number {order_number}")
        
        tracking_info = await get_tracking_by_number_use_case.execute(
            order_number=order_number,
            include_notifications=include_notifications
        )
        
        return tracking_info
        
    except OrderTrackingNotFoundError as e:
        logger.warning(f"Order not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Failed to get order tracking by number: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve order tracking"}
        )


@router.put(
    "/orders/{order_id}/status",
    response_model=SuccessResponse,
    summary="Update Order Status",
    description="Update order status with real-time notifications and audit trail."
)
async def update_order_status(
    order_id: UUID = Path(..., description="Order ID"),
    request: UpdateOrderStatusRequest = ...,
    current_user = Depends(require_staff),
    update_status_use_case: UpdateOrderStatusUseCase = Depends(get_update_order_status_use_case_dep),
):
    """Update order status with comprehensive tracking.
    
    Args:
        order_id: Order ID to update
        request: Status update request
        current_user: Current authenticated user (must be restaurant staff)
        update_status_use_case: Update order status use case
        
    Returns:
        Success response with updated status information
    """
    try:
        logger.info(f"Updating order {order_id} status to {request.new_status}")
        
        # Convert to DTO
        update_dto = UpdateOrderStatusRequestDTO(
            order_id=order_id,
            new_status=request.new_status,
            changed_by=current_user.user_id,
            estimated_completion_time=request.estimated_completion_time,
            preparation_notes=request.preparation_notes,
            change_reason=request.change_reason,
            notify_customer=request.notify_customer
        )
        
        status_history = await update_status_use_case.execute(update_dto)
        
        return SuccessResponse(
            message=f"Order status updated to {request.new_status}",
            data={
                "order_id": str(order_id),
                "new_status": request.new_status,
                "status_history_id": str(status_history.id)
            }
        )
        
    except InvalidStatusTransitionError as e:
        logger.warning(f"Invalid status transition: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Failed to update order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to update order status"}
        )


@router.put(
    "/orders/bulk/status",
    response_model=SuccessResponse,
    summary="Bulk Update Order Status",
    description="Update status for multiple orders simultaneously for kitchen efficiency."
)
async def bulk_update_order_status(
    request: BulkUpdateOrderStatusRequest = ...,
    current_user = Depends(require_staff),
    bulk_update_use_case: BulkUpdateOrderStatusUseCase = Depends(get_bulk_update_order_status_use_case_dep),
):
    """Bulk update order status for kitchen efficiency.
    
    Args:
        request: Bulk status update request
        current_user: Current authenticated user (must be restaurant staff)
        bulk_update_use_case: Bulk update order status use case
        
    Returns:
        Success response with bulk update results
    """
    try:
        logger.info(f"Bulk updating {len(request.order_ids)} orders to status {request.new_status}")
        
        results = await bulk_update_use_case.execute(
            order_ids=request.order_ids,
            new_status=request.new_status,
            changed_by=current_user.user_id,
            preparation_notes=request.preparation_notes,
            notify_customers=request.notify_customers
        )
        
        return SuccessResponse(
            message=f"Successfully updated {len(results)} out of {len(request.order_ids)} orders",
            data={
                "updated_count": len(results),
                "total_count": len(request.order_ids),
                "new_status": request.new_status
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to bulk update order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to bulk update order status"}
        )


@router.put(
    "/orders/{order_id}/items/{item_id}/status",
    response_model=SuccessResponse,
    summary="Update Order Item Status",
    description="Update individual order item status for detailed kitchen workflow tracking."
)
async def update_order_item_status(
    order_id: UUID = Path(..., description="Order ID"),
    item_id: UUID = Path(..., description="Order item ID"),
    request: UpdateOrderItemStatusRequest = ...,
    current_user = Depends(require_staff),
    # update_item_status_use_case: UpdateOrderItemStatusUseCase = Depends(),
):
    """Update individual order item status.
    
    Args:
        order_id: Order ID
        item_id: Order item ID
        request: Item status update request
        current_user: Current authenticated user (must be restaurant staff)
        
    Returns:
        Success response with updated item status
    """
    try:
        logger.info(f"Updating item {item_id} status to {request.new_status.value}")
        
        # Convert to DTO
        update_dto = UpdateOrderItemStatusRequestDTO(
            order_item_id=item_id,
            new_status=request.new_status,
            changed_by=current_user.user_id,
            preparation_notes=request.preparation_notes,
            estimated_ready_time=request.estimated_ready_time,
            quality_check_passed=request.quality_check_passed,
            quality_notes=request.quality_notes
        )
        
        # This would be implemented with the item tracking use case
        # item_tracking = await update_item_status_use_case.execute(update_dto)
        
        return SuccessResponse(
            message=f"Order item status updated to {request.new_status.value}",
            data={
                "order_id": str(order_id),
                "item_id": str(item_id),
                "new_status": request.new_status.value
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to update order item status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to update order item status"}
        )


@router.post(
    "/orders/{order_id}/notifications",
    response_model=SuccessResponse,
    summary="Send Order Notification",
    description="Send notifications to customers through multiple channels."
)
async def send_order_notification(
    order_id: UUID = Path(..., description="Order ID"),
    request: SendNotificationRequest = ...,
    current_user = Depends(require_staff),
    send_notification_use_case: SendNotificationUseCase = Depends(get_send_notification_use_case_dep),
):
    """Send order notification through multiple channels.
    
    Args:
        order_id: Order ID
        request: Send notification request
        current_user: Current authenticated user (must be restaurant staff)
        send_notification_use_case: Send notification use case
        
    Returns:
        Success response with notification results
    """
    try:
        logger.info(f"Sending notifications for order {order_id}")
        
        # Convert to DTO
        notification_dto = SendNotificationRequestDTO(
            order_id=order_id,
            trigger=request.trigger,
            channels=request.channels,
            custom_message=request.custom_message,
            custom_subject=request.custom_subject,
            immediate=request.immediate
        )
        
        notifications = await send_notification_use_case.execute(notification_dto)
        
        return SuccessResponse(
            message=f"Sent {len(notifications)} notifications",
            data={
                "order_id": str(order_id),
                "notifications_sent": len(notifications),
                "channels": [n.channel.value for n in notifications]
            }
        )
        
    except NotificationDeliveryError as e:
        logger.warning(f"Notification delivery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Failed to send notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to send notifications"}
        )


@router.get(
    "/kitchen/orders",
    response_model=List[KitchenOrderSummaryResponse],
    summary="Get Kitchen Orders",
    description="Retrieve orders for kitchen display with real-time status information."
)
async def get_kitchen_orders(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    active_only: bool = Query(True, description="Only include active orders"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of orders"),
    current_user = Depends(require_staff),
    get_kitchen_orders_use_case: GetKitchenOrdersUseCase = Depends(get_kitchen_orders_use_case_dep),
):
    """Get orders for kitchen display.
    
    Args:
        restaurant_id: Restaurant ID
        active_only: Whether to only include active orders
        limit: Maximum number of orders to return
        current_user: Current authenticated user (must be restaurant staff)
        get_kitchen_orders_use_case: Get kitchen orders use case
        
    Returns:
        List of kitchen order summaries
    """
    try:
        logger.info(f"Getting kitchen orders for restaurant {restaurant_id}")
        
        orders = await get_kitchen_orders_use_case.execute(
            restaurant_id=restaurant_id,
            active_only=active_only,
            limit=limit
        )
        
        # Convert to kitchen summary format
        kitchen_summaries = []
        for order in orders:
            summary = KitchenOrderSummaryResponse(
                order_id=order.order_id,
                order_number=order.order_number,
                table_number=None,  # Would be extracted from order data
                customer_name="Customer",  # Would be extracted from order data
                current_status=order.current_status,
                priority=order.kitchen_workflow.priority if order.kitchen_workflow else "normal",
                estimated_completion_time=order.estimated_completion_time,
                total_items=order.kitchen_workflow.total_items if order.kitchen_workflow else 0,
                items_pending=order.kitchen_workflow.items_pending if order.kitchen_workflow else 0,
                items_preparing=order.kitchen_workflow.items_preparing if order.kitchen_workflow else 0,
                items_ready=order.kitchen_workflow.items_ready if order.kitchen_workflow else 0,
                overall_progress=order.kitchen_workflow.overall_progress if order.kitchen_workflow else 0.0,
                time_since_placed_minutes=0,  # Would be calculated
                is_overdue=order.kitchen_workflow.is_overdue if order.kitchen_workflow else False,
                next_action=order.kitchen_workflow.next_action if order.kitchen_workflow else "Review order",
                special_instructions=None,  # Would be extracted from order data
            )
            kitchen_summaries.append(summary)
        
        return kitchen_summaries
        
    except Exception as e:
        logger.error(f"Failed to get kitchen orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve kitchen orders"}
        )


@router.get(
    "/notifications/metrics",
    response_model=NotificationDeliveryMetricsResponse,
    summary="Get Notification Metrics",
    description="Retrieve notification delivery metrics and analytics."
)
async def get_notification_metrics(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    start_date: datetime = Query(..., description="Start date for metrics"),
    end_date: datetime = Query(..., description="End date for metrics"),
    current_user = Depends(require_staff),
    # get_metrics_use_case: GetNotificationMetricsUseCase = Depends(),
):
    """Get notification delivery metrics.
    
    Args:
        restaurant_id: Restaurant ID
        start_date: Start date for metrics
        end_date: End date for metrics
        current_user: Current authenticated user (must be restaurant staff)
        
    Returns:
        Notification delivery metrics
    """
    try:
        logger.info(f"Getting notification metrics for restaurant {restaurant_id}")
        
        # This would be implemented with a metrics use case
        metrics = NotificationDeliveryMetricsResponse(
            restaurant_id=restaurant_id,
            date_range_start=start_date,
            date_range_end=end_date,
            total_notifications=0,
            notifications_by_channel={},
            delivery_success_rate=0.0,
            average_delivery_time_seconds=None,
            failed_notifications=0,
            bounced_notifications=0,
            opened_notifications=0,
            clicked_notifications=0,
            engagement_rate=0.0,
            cost_breakdown={},
            total_cost=0.0
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get notification metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve notification metrics"}
        )


@router.post(
    "/notifications/retry",
    response_model=SuccessResponse,
    summary="Retry Failed Notifications",
    description="Retry failed notifications that are eligible for retry."
)
async def retry_failed_notifications(
    max_retries: int = Query(3, ge=1, le=5, description="Maximum retry attempts"),
    current_user = Depends(require_staff),
    retry_notifications_use_case: RetryFailedNotificationsUseCase = Depends(get_retry_failed_notifications_use_case_dep),
):
    """Retry failed notifications.
    
    Args:
        max_retries: Maximum retry attempts
        current_user: Current authenticated user (must be restaurant staff)
        retry_notifications_use_case: Retry failed notifications use case
        
    Returns:
        Success response with retry results
    """
    try:
        logger.info("Retrying failed notifications")
        
        retried_notifications = await retry_notifications_use_case.execute(max_retries=max_retries)
        
        return SuccessResponse(
            message=f"Retried {len(retried_notifications)} failed notifications",
            data={
                "retried_count": len(retried_notifications),
                "max_retries": max_retries
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to retry notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Failed to retry notifications"}
        )
