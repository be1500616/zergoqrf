"""Order management FastAPI router.

This module contains FastAPI routes for order management operations,
including order creation, status updates, and payment collection.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from supabase import AClient

from ....common.supabase_client import get_async_supabase
from ...cart.infrastructure.cart_item_repos_impl import CartItemRepositoryImpl
from ...cart.infrastructure.cart_session_repos_impl import CartSessionRepositoryImpl
from ..application.order_dtos import (
    CollectPaymentRequestDTO,
    CreateOrderRequestDTO,
    UpdateOrderStatusRequestDTO,
)
from ..application.use_cases import (
    CollectPaymentUseCase,
    CreateOrderFromCartUseCase,
    GetOrderByNumberUseCase,
    GetOrderByPaymentReferenceUseCase,
    GetOrdersByTableUseCase,
    GetOrderUseCase,
    GetPaymentCollectionsUseCase,
    GetRestaurantOrdersSummaryUseCase,
    GetRestaurantOrdersUseCase,
    UpdateOrderStatusUseCase,
)
from ..domain.order_enums import OrderStatus, PaymentStatus
from ..domain.order_exceptions import (
    CartSessionExpiredError,
    CartSessionNotFoundError,
    EmptyCartError,
    InvalidCustomerInfoError,
    InvalidOrderStatusTransitionError,
    InvalidPaymentStatusTransitionError,
    OrderAlreadyCancelledException,
    OrderAlreadyCompletedException,
    OrderAlreadyExistsError,
    OrderCreationError,
    OrderNotFoundError,
    OrderOperationError,
    PaymentAlreadyCollectedError,
    PaymentAmountMismatchError,
    PaymentReferenceNotFoundError,
    UnauthorizedOrderAccessError,
)
from ..infrastructure.order_repos_impl import (
    SupabaseOrderAuditRepository,
    SupabaseOrderItemRepository,
    SupabaseOrderRepository,
    SupabasePaymentCollectionRepository,
)
from .order_schemas import (
    CollectPaymentSchema,
    CreateOrderSchema,
    OrderSchema,
    OrdersSummarySchema,
    OrderSummarySchema,
    PaymentCollectionSchema,
    RestaurantOrdersSchema,
    UpdateOrderStatusSchema,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/orders", tags=["Orders"])


# Dependency injection functions
async def get_order_repository(
    supabase: AClient = Depends(get_async_supabase),
) -> SupabaseOrderRepository:
    """Get order repository instance."""
    return SupabaseOrderRepository(supabase)


async def get_order_item_repository(
    supabase: AClient = Depends(get_async_supabase),
) -> SupabaseOrderItemRepository:
    """Get order item repository instance."""
    return SupabaseOrderItemRepository(supabase)


async def get_payment_collection_repository(
    supabase: AClient = Depends(get_async_supabase),
) -> SupabasePaymentCollectionRepository:
    """Get payment collection repository instance."""
    return SupabasePaymentCollectionRepository(supabase)


async def get_order_audit_repository(
    supabase: AClient = Depends(get_async_supabase),
) -> SupabaseOrderAuditRepository:
    """Get order audit repository instance."""
    return SupabaseOrderAuditRepository(supabase)


async def get_cart_session_repository(
    supabase: AClient = Depends(get_async_supabase),
) -> CartSessionRepositoryImpl:
    """Get cart session repository instance."""
    return CartSessionRepositoryImpl(supabase)


async def get_cart_item_repository(
    supabase: AClient = Depends(get_async_supabase),
) -> CartItemRepositoryImpl:
    """Get cart item repository instance."""
    return CartItemRepositoryImpl(supabase)


def get_create_order_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
    order_item_repository: SupabaseOrderItemRepository = Depends(
        get_order_item_repository
    ),
    cart_session_repository: CartSessionRepositoryImpl = Depends(
        get_cart_session_repository
    ),
    cart_item_repository: CartItemRepositoryImpl = Depends(get_cart_item_repository),
) -> CreateOrderFromCartUseCase:
    """Get create order use case instance."""
    return CreateOrderFromCartUseCase(
        order_repository,
        order_item_repository,
        cart_session_repository,
        cart_item_repository,
    )


def get_update_order_status_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
    order_audit_repository: SupabaseOrderAuditRepository = Depends(
        get_order_audit_repository
    ),
) -> UpdateOrderStatusUseCase:
    """Get update order status use case instance."""
    return UpdateOrderStatusUseCase(order_repository, order_audit_repository)


def get_get_order_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
) -> GetOrderUseCase:
    """Get order use case instance."""
    return GetOrderUseCase(order_repository)


def get_get_order_by_number_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
) -> GetOrderByNumberUseCase:
    """Get order by number use case instance."""
    return GetOrderByNumberUseCase(order_repository)


def get_get_order_by_payment_reference_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
) -> GetOrderByPaymentReferenceUseCase:
    """Get order by payment reference use case instance."""
    return GetOrderByPaymentReferenceUseCase(order_repository)


def get_collect_payment_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
    payment_collection_repository: SupabasePaymentCollectionRepository = Depends(
        get_payment_collection_repository
    ),
    order_audit_repository: SupabaseOrderAuditRepository = Depends(
        get_order_audit_repository
    ),
) -> CollectPaymentUseCase:
    """Get collect payment use case instance."""
    return CollectPaymentUseCase(
        order_repository, payment_collection_repository, order_audit_repository
    )


def get_get_payment_collections_use_case(
    payment_collection_repository: SupabasePaymentCollectionRepository = Depends(
        get_payment_collection_repository
    ),
) -> GetPaymentCollectionsUseCase:
    """Get payment collections use case instance."""
    return GetPaymentCollectionsUseCase(payment_collection_repository)


def get_get_restaurant_orders_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
) -> GetRestaurantOrdersUseCase:
    """Get restaurant orders use case instance."""
    return GetRestaurantOrdersUseCase(order_repository)


def get_get_restaurant_orders_summary_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
) -> GetRestaurantOrdersSummaryUseCase:
    """Get restaurant orders summary use case instance."""
    return GetRestaurantOrdersSummaryUseCase(order_repository)


def get_get_orders_by_table_use_case(
    order_repository: SupabaseOrderRepository = Depends(get_order_repository),
) -> GetOrdersByTableUseCase:
    """Get orders by table use case instance."""
    return GetOrdersByTableUseCase(order_repository)


# Order Creation Endpoints
@router.post(
    "/",
    response_model=OrderSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create order from cart",
    description="Convert a cart session to an order with customer information and payment tracking.",
)
async def create_order(
    request: CreateOrderSchema,
    create_order_use_case: CreateOrderFromCartUseCase = Depends(
        get_create_order_use_case
    ),
    current_user_id: Optional[UUID] = Depends(),  # From auth dependency
) -> OrderSchema:
    """Create order from cart session."""
    try:
        # Convert schema to DTO
        create_request = CreateOrderRequestDTO(
            cart_session_id=request.cart_session_id,
            customer_info=request.customer_info,
            special_instructions=request.special_instructions,
            table_id=request.table_id,
        )

        # Execute use case
        order_dto = await create_order_use_case.execute(create_request, current_user_id)

        # Convert DTO to schema
        return OrderSchema(**order_dto.dict())

    except CartSessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "CART_SESSION_NOT_FOUND",
                "message": str(e),
                "details": e.details,
            },
        )
    except CartSessionExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "CART_SESSION_EXPIRED",
                "message": str(e),
                "details": e.details,
            },
        )
    except EmptyCartError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "EMPTY_CART",
                "message": str(e),
                "details": e.details,
            },
        )
    except InvalidCustomerInfoError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "INVALID_CUSTOMER_INFO",
                "message": str(e),
                "details": e.details,
            },
        )
    except OrderCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ORDER_CREATION_FAILED",
                "message": str(e),
                "details": e.details,
            },
        )


# Order Retrieval Endpoints
@router.get(
    "/{order_id}",
    response_model=OrderSchema,
    summary="Get order by ID",
    description="Retrieve complete order details including items and payment collections.",
)
async def get_order(
    order_id: UUID,
    get_order_use_case: GetOrderUseCase = Depends(get_get_order_use_case),
) -> OrderSchema:
    """Get order by ID."""
    try:
        order_dto = await get_order_use_case.execute(order_id)
        return OrderSchema(**order_dto.dict())

    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ORDER_NOT_FOUND",
                "message": str(e),
                "details": e.details,
            },
        )


@router.get(
    "/number/{order_number}",
    response_model=OrderSchema,
    summary="Get order by order number",
    description="Retrieve order details using the human-readable order number.",
)
async def get_order_by_number(
    order_number: str,
    get_order_by_number_use_case: GetOrderByNumberUseCase = Depends(
        get_get_order_by_number_use_case
    ),
) -> OrderSchema:
    """Get order by order number."""
    try:
        order_dto = await get_order_by_number_use_case.execute(order_number)
        return OrderSchema(**order_dto.dict())

    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ORDER_NOT_FOUND",
                "message": str(e),
                "details": e.details,
            },
        )


@router.get(
    "/payment-reference/{payment_reference}",
    response_model=OrderSchema,
    summary="Get order by payment reference",
    description="Retrieve order details using the payment reference for staff operations.",
)
async def get_order_by_payment_reference(
    payment_reference: str,
    get_order_by_payment_reference_use_case: GetOrderByPaymentReferenceUseCase = Depends(
        get_get_order_by_payment_reference_use_case
    ),
) -> OrderSchema:
    """Get order by payment reference."""
    try:
        order_dto = await get_order_by_payment_reference_use_case.execute(
            payment_reference
        )
        return OrderSchema(**order_dto.dict())

    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ORDER_NOT_FOUND",
                "message": str(e),
                "details": e.details,
            },
        )


# Order Status Management Endpoints
@router.patch(
    "/{order_id}/status",
    response_model=OrderSchema,
    summary="Update order status",
    description="Update order status with validation and audit trail.",
)
async def update_order_status(
    order_id: UUID,
    request: UpdateOrderStatusSchema,
    update_order_status_use_case: UpdateOrderStatusUseCase = Depends(
        get_update_order_status_use_case
    ),
    current_user_id: Optional[UUID] = Depends(),  # From auth dependency
) -> OrderSchema:
    """Update order status."""
    try:
        # Convert schema to DTO
        update_request = UpdateOrderStatusRequestDTO(
            new_status=request.new_status,
            change_reason=request.change_reason,
            change_notes=request.change_notes,
        )

        # Execute use case
        order_dto = await update_order_status_use_case.execute(
            order_id, update_request, current_user_id
        )

        return OrderSchema(**order_dto.dict())

    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ORDER_NOT_FOUND",
                "message": str(e),
                "details": e.details,
            },
        )
    except InvalidOrderStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_STATUS_TRANSITION",
                "message": str(e),
                "details": e.details,
            },
        )
    except (OrderAlreadyCancelledException, OrderAlreadyCompletedException) as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": e.error_code,
                "message": str(e),
                "details": e.details,
            },
        )


# Payment Collection Endpoints
@router.post(
    "/{order_id}/collect-payment",
    response_model=OrderSchema,
    summary="Collect payment for order",
    description="Collect cash payment and update order status automatically.",
)
async def collect_payment(
    order_id: UUID,
    request: CollectPaymentSchema,
    collect_payment_use_case: CollectPaymentUseCase = Depends(
        get_collect_payment_use_case
    ),
    current_user_id: Optional[UUID] = Depends(),  # Staff member collecting payment
) -> OrderSchema:
    """Collect payment for order."""
    try:
        # Convert schema to DTO
        collect_request = CollectPaymentRequestDTO(
            payment_reference=request.payment_reference,
            amount=request.amount,
            payment_method=request.payment_method,
            collection_notes=request.collection_notes,
            verification_code=request.verification_code,
        )

        # Execute use case
        order_dto = await collect_payment_use_case.execute(
            order_id, collect_request, current_user_id
        )

        return OrderSchema(**order_dto.dict())

    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ORDER_NOT_FOUND",
                "message": str(e),
                "details": e.details,
            },
        )
    except PaymentReferenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "PAYMENT_REFERENCE_NOT_FOUND",
                "message": str(e),
                "details": e.details,
            },
        )
    except PaymentAlreadyCollectedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "PAYMENT_ALREADY_COLLECTED",
                "message": str(e),
                "details": e.details,
            },
        )
    except PaymentAmountMismatchError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "PAYMENT_AMOUNT_MISMATCH",
                "message": str(e),
                "details": e.details,
            },
        )


@router.get(
    "/{order_id}/payment-collections",
    response_model=List[PaymentCollectionSchema],
    summary="Get payment collections for order",
    description="Retrieve all payment collections for a specific order.",
)
async def get_payment_collections(
    order_id: UUID,
    get_payment_collections_use_case: GetPaymentCollectionsUseCase = Depends(
        get_get_payment_collections_use_case
    ),
) -> List[PaymentCollectionSchema]:
    """Get payment collections for order."""
    try:
        collections_dto = await get_payment_collections_use_case.execute_by_order(
            order_id
        )
        return [
            PaymentCollectionSchema(**collection.dict())
            for collection in collections_dto
        ]

    except Exception as e:
        logger.error(f"Get payment collections failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment collections",
        )


# Restaurant Orders Management Endpoints
@router.get(
    "/restaurant/{restaurant_id}",
    response_model=RestaurantOrdersSchema,
    summary="Get restaurant orders",
    description="Retrieve orders for a restaurant with optional status filters.",
)
async def get_restaurant_orders(
    restaurant_id: UUID,
    order_status: Optional[OrderStatus] = Query(
        None, description="Filter by order status"
    ),
    payment_status: Optional[PaymentStatus] = Query(
        None, description="Filter by payment status"
    ),
    limit: int = Query(
        50, ge=1, le=100, description="Maximum number of orders to return"
    ),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    get_restaurant_orders_use_case: GetRestaurantOrdersUseCase = Depends(
        get_get_restaurant_orders_use_case
    ),
) -> RestaurantOrdersSchema:
    """Get restaurant orders with filters."""
    try:
        orders_dto = await get_restaurant_orders_use_case.execute(
            restaurant_id=restaurant_id,
            order_status=order_status,
            payment_status=payment_status,
            limit=limit,
            offset=offset,
        )

        return RestaurantOrdersSchema(**orders_dto.dict())

    except Exception as e:
        logger.error(f"Get restaurant orders failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve restaurant orders",
        )


@router.get(
    "/restaurant/{restaurant_id}/summary",
    response_model=OrdersSummarySchema,
    summary="Get restaurant orders summary",
    description="Get order counts by status for restaurant dashboard.",
)
async def get_restaurant_orders_summary(
    restaurant_id: UUID,
    get_restaurant_orders_summary_use_case: GetRestaurantOrdersSummaryUseCase = Depends(
        get_get_restaurant_orders_summary_use_case
    ),
) -> OrdersSummarySchema:
    """Get restaurant orders summary."""
    try:
        summary = await get_restaurant_orders_summary_use_case.execute(restaurant_id)
        return OrdersSummarySchema(**summary)

    except Exception as e:
        logger.error(f"Get restaurant orders summary failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders summary",
        )


@router.get(
    "/table/{table_id}",
    response_model=List[OrderSchema],
    summary="Get orders by table",
    description="Retrieve orders for a specific table.",
)
async def get_orders_by_table(
    table_id: UUID,
    active_only: bool = Query(True, description="Return only active orders"),
    get_orders_by_table_use_case: GetOrdersByTableUseCase = Depends(
        get_get_orders_by_table_use_case
    ),
) -> List[OrderSchema]:
    """Get orders by table."""
    try:
        orders_dto = await get_orders_by_table_use_case.execute(table_id, active_only)
        return [OrderSchema(**order.dict()) for order in orders_dto]

    except Exception as e:
        logger.error(f"Get orders by table failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders by table",
        )
