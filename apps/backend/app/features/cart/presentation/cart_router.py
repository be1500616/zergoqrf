"""Cart management API router.

This module provides FastAPI endpoints for cart management operations,
including session management, item operations, and cart summary.
"""

import logging
from typing import List
from uuid import UUID

from app.common.supabase_client import get_supabase
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from supabase import Client

from ..application.cart_dtos import (
    AddCartItemRequestDTO,
    CartMigrationRequestDTO,
    PriceValidationRequestDTO,
    UpdateCartItemRequestDTO,
)
from ..application.use_cases import (
    AddCartItemUseCase,
    ClearCartUseCase,
    CreateAnonymousCartSessionUseCase,
    CreateAuthenticatedCartSessionUseCase,
    ExtendCartSessionActivityUseCase,
    GetCartItemsUseCase,
    GetCartSessionUseCase,
    GetCartSummaryUseCase,
    MigrateCartSessionUseCase,
    RemoveCartItemUseCase,
    UpdateCartItemUseCase,
    ValidateCartPricesUseCase,
    ValidateMenuItemPriceUseCase,
)
from ..domain.cart_exceptions import (
    CartDomainError,
    CartFullError,
    CartItemNotFoundError,
    CartMigrationError,
    CartOperationError,
    CartSessionExpiredError,
    CartSessionNotFoundError,
    PriceValidationError,
)
from ..infrastructure.cart_item_repos_impl import CartItemRepositoryImpl
from ..infrastructure.cart_session_repos_impl import CartSessionRepositoryImpl
from .cart_schemas import (
    AddCartItemRequest,
    CartItemResponse,
    CartOperationResponse,
    CartSessionResponse,
    CartSummaryResponse,
    CreateAnonymousCartSessionRequest,
    CreateAuthenticatedCartSessionRequest,
    ErrorResponse,
    MigrateCartRequest,
    MigrateCartResponse,
    UpdateCartItemRequest,
    ValidatePriceRequest,
    ValidatePriceResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cart", tags=["Cart Management"])


# Dependency injection functions
def get_cart_session_repository(
    supabase: Client = Depends(get_supabase),
) -> CartSessionRepositoryImpl:
    """Get cart session repository instance."""
    return CartSessionRepositoryImpl(supabase)


def get_cart_item_repository(
    supabase: Client = Depends(get_supabase),
) -> CartItemRepositoryImpl:
    """Get cart item repository instance."""
    return CartItemRepositoryImpl(supabase)


def get_create_anonymous_cart_session_use_case(
    repository: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> CreateAnonymousCartSessionUseCase:
    """Get create anonymous cart session use case."""
    return CreateAnonymousCartSessionUseCase(repository)


def get_create_authenticated_cart_session_use_case(
    repository: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> CreateAuthenticatedCartSessionUseCase:
    """Get create authenticated cart session use case."""
    return CreateAuthenticatedCartSessionUseCase(repository)


def get_cart_session_use_case(
    repository: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> GetCartSessionUseCase:
    """Get cart session use case."""
    return GetCartSessionUseCase(repository)


def get_extend_cart_session_activity_use_case(
    repository: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> ExtendCartSessionActivityUseCase:
    """Get extend cart session activity use case."""
    return ExtendCartSessionActivityUseCase(repository)


def get_migrate_cart_session_use_case(
    cart_session_repo: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
    cart_item_repo: CartItemRepositoryImpl = Depends(get_cart_item_repository),
) -> MigrateCartSessionUseCase:
    """Get migrate cart session use case."""
    return MigrateCartSessionUseCase(cart_session_repo, cart_item_repo)


def get_add_cart_item_use_case(
    cart_item_repo: CartItemRepositoryImpl = Depends(get_cart_item_repository),
    cart_session_repo: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> AddCartItemUseCase:
    """Get add cart item use case."""
    return AddCartItemUseCase(cart_item_repo, cart_session_repo)


def get_update_cart_item_use_case(
    cart_item_repo: CartItemRepositoryImpl = Depends(get_cart_item_repository),
    cart_session_repo: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> UpdateCartItemUseCase:
    """Get update cart item use case."""
    return UpdateCartItemUseCase(cart_item_repo, cart_session_repo)


def get_remove_cart_item_use_case(
    cart_item_repo: CartItemRepositoryImpl = Depends(get_cart_item_repository),
    cart_session_repo: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> RemoveCartItemUseCase:
    """Get remove cart item use case."""
    return RemoveCartItemUseCase(cart_item_repo, cart_session_repo)


def get_cart_items_use_case(
    repository: CartItemRepositoryImpl = Depends(get_cart_item_repository),
) -> GetCartItemsUseCase:
    """Get cart items use case."""
    return GetCartItemsUseCase(repository)


def get_clear_cart_use_case(
    cart_item_repo: CartItemRepositoryImpl = Depends(get_cart_item_repository),
    cart_session_repo: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
) -> ClearCartUseCase:
    """Get clear cart use case."""
    return ClearCartUseCase(cart_item_repo, cart_session_repo)


def get_cart_summary_use_case(
    cart_session_repo: CartSessionRepositoryImpl = Depends(get_cart_session_repository),
    cart_item_repo: CartItemRepositoryImpl = Depends(get_cart_item_repository),
) -> GetCartSummaryUseCase:
    """Get cart summary use case."""
    return GetCartSummaryUseCase(cart_session_repo, cart_item_repo)


def get_validate_cart_prices_use_case(
    cart_item_repo: CartItemRepositoryImpl = Depends(get_cart_item_repository),
) -> ValidateCartPricesUseCase:
    """Get validate cart prices use case."""
    return ValidateCartPricesUseCase(cart_item_repo)


def get_validate_menu_item_price_use_case() -> ValidateMenuItemPriceUseCase:
    """Get validate menu item price use case."""
    return ValidateMenuItemPriceUseCase()


# Error handlers
def handle_cart_error(error: Exception) -> JSONResponse:
    """Handle cart-related errors and return appropriate HTTP responses.

    Args:
        error: The exception that occurred

    Returns:
        JSONResponse with appropriate status code and error details
    """
    if isinstance(error, CartSessionNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error="CART_SESSION_NOT_FOUND",
                message=error.message,
                details={"session_token": error.session_token[:8] + "..."},
            ).dict(),
        )

    elif isinstance(error, CartSessionExpiredError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(
                error="CART_SESSION_EXPIRED",
                message=error.message,
                details={"session_token": error.session_token[:8] + "..."},
            ).dict(),
        )

    elif isinstance(error, CartItemNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error="CART_ITEM_NOT_FOUND",
                message=error.message,
                details={"item_id": error.item_id},
            ).dict(),
        )

    elif isinstance(error, CartFullError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="CART_FULL",
                message=error.message,
                details={
                    "current_count": error.current_count,
                    "max_items": error.max_items,
                },
            ).dict(),
        )

    elif isinstance(error, CartMigrationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="CART_MIGRATION_ERROR",
                message=error.message,
                details={"reason": error.reason},
            ).dict(),
        )

    elif isinstance(error, PriceValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="PRICE_VALIDATION_ERROR",
                message=error.message,
                details={
                    "item_name": error.item_name,
                    "expected_price": error.expected_price,
                    "actual_price": error.actual_price,
                },
            ).dict(),
        )

    elif isinstance(error, CartOperationError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="CART_OPERATION_ERROR",
                message=error.message,
                details=error.details,
            ).dict(),
        )

    elif isinstance(error, CartDomainError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="CART_DOMAIN_ERROR",
                message=error.message,
                details=error.details,
            ).dict(),
        )

    else:
        logger.error(f"Unhandled cart error: {error}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="INTERNAL_SERVER_ERROR", message="An unexpected error occurred"
            ).dict(),
        )


# Cart Session Endpoints


@router.post("/sessions/anonymous", response_model=CartSessionResponse)
async def create_anonymous_cart_session(
    request: CreateAnonymousCartSessionRequest,
    use_case: CreateAnonymousCartSessionUseCase = Depends(
        get_create_anonymous_cart_session_use_case
    ),
) -> CartSessionResponse:
    """Create a new anonymous cart session.

    Creates a cart session for anonymous users that expires after 2 hours.
    The session is linked to an anonymous session ID for tracking.

    Args:
        request: Anonymous cart session creation request
        use_case: Create anonymous cart session use case

    Returns:
        Created cart session details

    Raises:
        HTTPException: If session creation fails
    """
    try:
        logger.info(
            "Creating anonymous cart session",
            extra={
                "anonymous_session_id": str(request.anonymous_session_id),
                "restaurant_id": str(request.restaurant_id),
            },
        )

        session_dto = await use_case.execute(
            anonymous_session_id=request.anonymous_session_id,
            restaurant_id=request.restaurant_id,
            table_id=request.table_id,
        )

        return CartSessionResponse(**session_dto.dict())

    except Exception as e:
        return handle_cart_error(e)


@router.post("/sessions/authenticated", response_model=CartSessionResponse)
async def create_authenticated_cart_session(
    request: CreateAuthenticatedCartSessionRequest,
    user_id: UUID = Depends(),  # TODO: Get from authentication
    use_case: CreateAuthenticatedCartSessionUseCase = Depends(
        get_create_authenticated_cart_session_use_case
    ),
) -> CartSessionResponse:
    """Create a new authenticated cart session.

    Creates a cart session for authenticated users that expires after 24 hours.
    If the user already has an active session for the restaurant, returns the existing session.

    Args:
        request: Authenticated cart session creation request
        user_id: Authenticated user ID
        use_case: Create authenticated cart session use case

    Returns:
        Created or existing cart session details

    Raises:
        HTTPException: If session creation fails
    """
    try:
        logger.info(
            "Creating authenticated cart session",
            extra={
                "user_id": str(user_id),
                "restaurant_id": str(request.restaurant_id),
            },
        )

        session_dto = await use_case.execute(
            user_id=user_id,
            restaurant_id=request.restaurant_id,
            table_id=request.table_id,
        )

        return CartSessionResponse(**session_dto.dict())

    except Exception as e:
        return handle_cart_error(e)


@router.get("/sessions/{session_token}", response_model=CartSessionResponse)
async def get_cart_session(
    session_token: str,
    use_case: GetCartSessionUseCase = Depends(get_cart_session_use_case),
) -> CartSessionResponse:
    """Get cart session by token.

    Retrieves cart session details and validates that the session is active and not expired.

    Args:
        session_token: Cart session token
        use_case: Get cart session use case

    Returns:
        Cart session details

    Raises:
        HTTPException: If session not found or expired
    """
    try:
        session_dto = await use_case.execute(session_token)
        return CartSessionResponse(**session_dto.dict())

    except Exception as e:
        return handle_cart_error(e)


@router.post("/sessions/{session_token}/extend", response_model=CartOperationResponse)
async def extend_cart_session_activity(
    session_token: str,
    use_case: ExtendCartSessionActivityUseCase = Depends(
        get_extend_cart_session_activity_use_case
    ),
) -> CartOperationResponse:
    """Extend cart session activity.

    Extends the expiration time for anonymous sessions and updates last activity timestamp.
    Authenticated sessions are not automatically extended.

    Args:
        session_token: Cart session token
        use_case: Extend cart session activity use case

    Returns:
        Operation result
    """
    try:
        extended = await use_case.execute(session_token)

        return CartOperationResponse(
            success=extended,
            message=(
                "Session activity extended successfully"
                if extended
                else "Session not found or expired"
            ),
        )

    except Exception as e:
        return handle_cart_error(e)


@router.post("/sessions/migrate", response_model=MigrateCartResponse)
async def migrate_cart_session(
    request: MigrateCartRequest,
    user_id: UUID = Depends(),  # TODO: Get from authentication
    use_case: MigrateCartSessionUseCase = Depends(get_migrate_cart_session_use_case),
) -> MigrateCartResponse:
    """Migrate anonymous cart session to authenticated.

    Transfers all items from an anonymous cart session to a new authenticated session.
    The anonymous session is deactivated after successful migration.

    Args:
        request: Cart migration request
        user_id: Authenticated user ID
        use_case: Migrate cart session use case

    Returns:
        Migration result with new session details

    Raises:
        HTTPException: If migration fails
    """
    try:
        logger.info(
            "Migrating cart session",
            extra={
                "anonymous_session_token": request.anonymous_session_token[:8] + "...",
                "user_id": str(user_id),
                "restaurant_id": str(request.restaurant_id),
            },
        )

        migration_request_dto = CartMigrationRequestDTO(
            anonymous_session_token=request.anonymous_session_token,
            user_id=user_id,
            restaurant_id=request.restaurant_id,
        )

        migration_dto = await use_case.execute(migration_request_dto)

        return MigrateCartResponse(**migration_dto.dict())

    except Exception as e:
        return handle_cart_error(e)


# Cart Item Endpoints


@router.post("/sessions/{session_token}/items", response_model=CartItemResponse)
async def add_cart_item(
    session_token: str,
    request: AddCartItemRequest,
    use_case: AddCartItemUseCase = Depends(get_add_cart_item_use_case),
) -> CartItemResponse:
    """Add item to cart.

    Adds a menu item to the cart with specified quantity and customizations.
    If the same item with identical customizations already exists, the quantities are combined.

    Args:
        session_token: Cart session token
        request: Add item request
        use_case: Add cart item use case

    Returns:
        Added cart item details

    Raises:
        HTTPException: If operation fails
    """
    try:
        logger.info(
            "Adding item to cart",
            extra={
                "session_token": session_token[:8] + "...",
                "menu_item_id": str(request.menu_item_id),
                "quantity": request.quantity,
            },
        )

        add_request_dto = AddCartItemRequestDTO(
            menu_item_id=request.menu_item_id,
            quantity=request.quantity,
            customizations=request.customizations,
            special_instructions=request.special_instructions,
        )

        item_dto = await use_case.execute(session_token, add_request_dto)

        return CartItemResponse(**item_dto.dict())

    except Exception as e:
        return handle_cart_error(e)


@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: UUID,
    request: UpdateCartItemRequest,
    use_case: UpdateCartItemUseCase = Depends(get_update_cart_item_use_case),
) -> CartItemResponse:
    """Update cart item.

    Updates the quantity, customizations, or special instructions for a cart item.
    Pricing is recalculated based on the new configuration.

    Args:
        item_id: Cart item ID
        request: Update item request
        use_case: Update cart item use case

    Returns:
        Updated cart item details

    Raises:
        HTTPException: If item not found or update fails
    """
    try:
        logger.info(
            "Updating cart item",
            extra={
                "item_id": str(item_id),
                "new_quantity": request.quantity,
            },
        )

        update_request_dto = UpdateCartItemRequestDTO(
            quantity=request.quantity,
            customizations=request.customizations,
            special_instructions=request.special_instructions,
        )

        item_dto = await use_case.execute(item_id, update_request_dto)

        return CartItemResponse(**item_dto.dict())

    except Exception as e:
        return handle_cart_error(e)


@router.delete("/items/{item_id}", response_model=CartOperationResponse)
async def remove_cart_item(
    item_id: UUID,
    use_case: RemoveCartItemUseCase = Depends(get_remove_cart_item_use_case),
) -> CartOperationResponse:
    """Remove item from cart.

    Removes a specific item from the cart. Cart totals are automatically updated.

    Args:
        item_id: Cart item ID
        use_case: Remove cart item use case

    Returns:
        Operation result
    """
    try:
        logger.info("Removing cart item", extra={"item_id": str(item_id)})

        removed = await use_case.execute(item_id)

        return CartOperationResponse(
            success=removed,
            message="Item removed successfully" if removed else "Item not found",
        )

    except Exception as e:
        return handle_cart_error(e)


@router.get("/sessions/{session_token}/items", response_model=List[CartItemResponse])
async def get_cart_items(
    session_token: str,
    use_case: GetCartItemsUseCase = Depends(get_cart_items_use_case),
) -> List[CartItemResponse]:
    """Get all items in cart.

    Retrieves all items in the specified cart session.

    Args:
        session_token: Cart session token
        use_case: Get cart items use case

    Returns:
        List of cart items

    Raises:
        HTTPException: If session not found or expired
    """
    try:
        # First validate session exists
        session_use_case = get_cart_session_use_case()
        session_dto = await session_use_case.execute(session_token)

        # Get items for the session
        item_dtos = await use_case.execute(session_dto.id)

        return [CartItemResponse(**item_dto.dict()) for item_dto in item_dtos]

    except Exception as e:
        return handle_cart_error(e)


@router.delete("/sessions/{session_token}/items", response_model=CartOperationResponse)
async def clear_cart(
    session_token: str,
    use_case: ClearCartUseCase = Depends(get_clear_cart_use_case),
) -> CartOperationResponse:
    """Clear all items from cart.

    Removes all items from the cart. Cart totals are reset to zero.

    Args:
        session_token: Cart session token
        use_case: Clear cart use case

    Returns:
        Operation result with count of removed items
    """
    try:
        logger.info("Clearing cart", extra={"session_token": session_token[:8] + "..."})

        # First validate session exists
        session_use_case = get_cart_session_use_case()
        session_dto = await session_use_case.execute(session_token)

        # Clear items from the session
        removed_count = await use_case.execute(session_dto.id)

        return CartOperationResponse(
            success=True,
            message=f"Cart cleared successfully. {removed_count} items removed.",
            data={"removed_count": removed_count},
        )

    except Exception as e:
        return handle_cart_error(e)


# Cart Summary and Validation Endpoints


@router.get("/sessions/{session_token}/summary", response_model=CartSummaryResponse)
async def get_cart_summary(
    session_token: str,
    use_case: GetCartSummaryUseCase = Depends(get_cart_summary_use_case),
) -> CartSummaryResponse:
    """Get complete cart summary.

    Retrieves the complete cart summary including session details, all items,
    and calculated totals with tax.

    Args:
        session_token: Cart session token
        use_case: Get cart summary use case

    Returns:
        Complete cart summary

    Raises:
        HTTPException: If session not found or expired
    """
    try:
        logger.info(
            "Getting cart summary", extra={"session_token": session_token[:8] + "..."}
        )

        summary_dto = await use_case.execute(session_token)

        return CartSummaryResponse(**summary_dto.dict())

    except Exception as e:
        return handle_cart_error(e)


@router.post(
    "/sessions/{session_token}/validate-prices",
    response_model=List[ValidatePriceResponse],
)
async def validate_cart_prices(
    session_token: str,
    use_case: ValidateCartPricesUseCase = Depends(get_validate_cart_prices_use_case),
) -> List[ValidatePriceResponse]:
    """Validate all cart item prices.

    Validates that all items in the cart have current pricing.
    Returns validation results for each item.

    Args:
        session_token: Cart session token
        use_case: Validate cart prices use case

    Returns:
        List of price validation results

    Raises:
        HTTPException: If session not found or expired
    """
    try:
        logger.info(
            "Validating cart prices", extra={"session_token": session_token[:8] + "..."}
        )

        validation_dtos = await use_case.execute(session_token)

        return [
            ValidatePriceResponse(**validation_dto.dict())
            for validation_dto in validation_dtos
        ]

    except Exception as e:
        return handle_cart_error(e)


@router.post("/validate-price", response_model=ValidatePriceResponse)
async def validate_menu_item_price(
    request: ValidatePriceRequest,
    use_case: ValidateMenuItemPriceUseCase = Depends(
        get_validate_menu_item_price_use_case
    ),
) -> ValidatePriceResponse:
    """Validate menu item price.

    Validates the price of a specific menu item with customizations
    before adding to cart.

    Args:
        request: Price validation request
        use_case: Validate menu item price use case

    Returns:
        Price validation result
    """
    try:
        logger.info(
            "Validating menu item price",
            extra={
                "menu_item_id": str(request.menu_item_id),
                "expected_price": str(request.expected_base_price),
            },
        )

        validation_request_dto = PriceValidationRequestDTO(
            menu_item_id=request.menu_item_id,
            expected_base_price=request.expected_base_price,
            customizations=request.customizations,
        )

        validation_dto = await use_case.execute(validation_request_dto)

        return ValidatePriceResponse(**validation_dto.dict())

    except Exception as e:
        return handle_cart_error(e)
