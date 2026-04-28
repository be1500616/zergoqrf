"""Cart summary and validation use cases.

This module contains use cases for cart summary operations
and price validation functionality.
"""

import logging
from decimal import Decimal
from typing import List
from uuid import UUID

from ...domain.cart_exceptions import (
    CartSessionExpiredError,
    CartSessionNotFoundError,
    PriceValidationError,
)
from ...domain.cart_repos import ICartItemRepository, ICartSessionRepository
from ...domain.cart_vos import CartSessionToken
from ..cart_dtos import (
    CartItemResponseDTO,
    CartSessionResponseDTO,
    CartSummaryResponseDTO,
    PriceValidationRequestDTO,
    PriceValidationResponseDTO,
    cart_item_entity_to_dto,
    cart_session_entity_to_dto,
)

logger = logging.getLogger(__name__)


class ValidateMenuItemPriceUseCase:
    """Use case for validating menu item prices."""

    def __init__(self, menu_item_repository):
        """Initialize the use case.

        Args:
            menu_item_repository: Menu item repository for price lookup
        """
        self._menu_repository = menu_item_repository

    async def execute(
        self, request: PriceValidationRequestDTO
    ) -> PriceValidationResponseDTO:
        """Validate menu item price against current menu.

        Args:
            request: Price validation request

        Returns:
            Price validation response

        Raises:
            PriceValidationError: If price validation fails
        """
        try:
            logger.info(
                "Validating menu item price",
                extra={
                    "menu_item_id": str(request.menu_item_id),
                    "expected_price": float(request.expected_price),
                },
            )

            # Get current menu item price
            menu_item = await self._menu_repository.get_by_id(request.menu_item_id)
            if not menu_item:
                raise PriceValidationError(
                    str(request.menu_item_id), float(request.expected_price), 0.0
                )

            actual_price = Decimal(str(menu_item.base_price))
            price_difference = actual_price - request.expected_price
            is_valid = abs(price_difference) < Decimal("0.01")  # Allow 1 cent tolerance

            logger.info(
                "Price validation completed",
                extra={
                    "menu_item_id": str(request.menu_item_id),
                    "expected_price": float(request.expected_price),
                    "actual_price": float(actual_price),
                    "is_valid": is_valid,
                },
            )

            return PriceValidationResponseDTO(
                menu_item_id=request.menu_item_id,
                expected_price=request.expected_price,
                actual_price=actual_price,
                is_valid=is_valid,
                price_difference=price_difference,
            )

        except Exception as e:
            logger.error(
                "Failed to validate menu item price",
                extra={
                    "error": str(e),
                    "menu_item_id": str(request.menu_item_id),
                },
            )
            raise PriceValidationError(
                str(request.menu_item_id), float(request.expected_price), 0.0
            )


class GetCartSummaryUseCase:
    """Use case for retrieving complete cart summary."""

    def __init__(
        self,
        cart_session_repository: ICartSessionRepository,
        cart_item_repository: ICartItemRepository,
    ):
        """Initialize the use case.

        Args:
            cart_session_repository: Cart session repository
            cart_item_repository: Cart item repository
        """
        self._session_repository = cart_session_repository
        self._item_repository = cart_item_repository

    async def execute(self, session_token: str) -> CartSummaryResponseDTO:
        """Get complete cart summary.

        Args:
            session_token: Cart session token

        Returns:
            Cart summary DTO

        Raises:
            CartSessionNotFoundError: If session not found
            CartSessionExpiredError: If session is expired
        """
        try:
            logger.info(
                "Getting cart summary",
                extra={"session_token": session_token[:8] + "..."},
            )

            # Get and validate cart session
            token = CartSessionToken(session_token)
            session = await self._session_repository.get_by_token(token)

            if not session:
                raise CartSessionNotFoundError(session_token)

            if not session.is_valid():
                raise CartSessionExpiredError(session_token)

            # Get cart items
            items = await self._item_repository.get_items_by_session(session.id)

            # Calculate totals
            subtotal = sum(item.total_price.amount for item in items)
            tax_rate = Decimal("0.10")  # 10% tax rate (should be configurable)
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount

            # Convert to DTOs
            session_dto = cart_session_entity_to_dto(session)
            item_dtos = [cart_item_entity_to_dto(item) for item in items]

            summary = CartSummaryResponseDTO(
                session=session_dto,
                items=item_dtos,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                item_count=len(items),
            )

            logger.info(
                "Cart summary retrieved successfully",
                extra={
                    "session_id": str(session.id),
                    "item_count": len(items),
                    "total_amount": str(total_amount),
                },
            )

            return summary

        except (CartSessionNotFoundError, CartSessionExpiredError):
            raise
        except Exception as e:
            logger.error(
                "Failed to get cart summary",
                extra={
                    "error": str(e),
                    "session_token": session_token[:8] + "...",
                },
            )
            raise


class ValidateCartPricesUseCase:
    """Use case for validating cart item prices against current menu prices."""

    def __init__(
        self,
        cart_session_repository: ICartSessionRepository,
        cart_item_repository: ICartItemRepository,
    ):
        """Initialize the use case.

        Args:
            cart_session_repository: Cart session repository
            cart_item_repository: Cart item repository
        """
        self._session_repository = cart_session_repository
        self._item_repository = cart_item_repository

    async def execute(self, session_token: str) -> List[PriceValidationResponseDTO]:
        """Validate all cart item prices.

        Args:
            session_token: Cart session token

        Returns:
            List of price validation results

        Raises:
            CartSessionNotFoundError: If session not found
            CartSessionExpiredError: If session is expired
        """
        try:
            logger.info(
                "Validating cart prices",
                extra={"session_token": session_token[:8] + "..."},
            )

            # Get and validate cart session
            token = CartSessionToken(session_token)
            session = await self._session_repository.get_by_token(token)

            if not session:
                raise CartSessionNotFoundError(session_token)

            if not session.is_valid():
                raise CartSessionExpiredError(session_token)

            # Get cart items
            items = await self._item_repository.get_items_by_session(session.id)

            validation_results = []

            for item in items:
                # TODO: Get current menu item price from menu service
                # For now, using placeholder validation
                current_base_price = item.base_price.amount  # Placeholder
                calculated_unit_price = current_base_price  # Placeholder

                is_valid = abs(item.base_price.amount - current_base_price) < Decimal(
                    "0.01"
                )
                price_changed = not is_valid

                validation_result = PriceValidationResponseDTO(
                    is_valid=is_valid,
                    current_base_price=current_base_price,
                    calculated_unit_price=calculated_unit_price,
                    price_changed=price_changed,
                    message=(
                        "Price validation completed"
                        if is_valid
                        else "Price has changed"
                    ),
                )

                validation_results.append(validation_result)

            logger.info(
                "Cart price validation completed",
                extra={
                    "session_id": str(session.id),
                    "items_validated": len(validation_results),
                    "price_changes_detected": sum(
                        1 for r in validation_results if r.price_changed
                    ),
                },
            )

            return validation_results

        except (CartSessionNotFoundError, CartSessionExpiredError):
            raise
        except Exception as e:
            logger.error(
                "Failed to validate cart prices",
                extra={
                    "error": str(e),
                    "session_token": session_token[:8] + "...",
                },
            )
            raise


class ValidateMenuItemPriceUseCase:
    """Use case for validating individual menu item prices."""

    def __init__(self):
        """Initialize the use case."""
        pass

    async def execute(
        self, request: PriceValidationRequestDTO
    ) -> PriceValidationResponseDTO:
        """Validate menu item price.

        Args:
            request: Price validation request DTO

        Returns:
            Price validation response DTO
        """
        try:
            logger.info(
                "Validating menu item price",
                extra={
                    "menu_item_id": str(request.menu_item_id),
                    "expected_price": str(request.expected_base_price),
                },
            )

            # TODO: Get current menu item price from menu service
            # For now, using placeholder validation
            current_base_price = request.expected_base_price  # Placeholder
            calculated_unit_price = (
                current_base_price  # Placeholder, should include customizations
            )

            is_valid = abs(request.expected_base_price - current_base_price) < Decimal(
                "0.01"
            )
            price_changed = not is_valid

            validation_result = PriceValidationResponseDTO(
                is_valid=is_valid,
                current_base_price=current_base_price,
                calculated_unit_price=calculated_unit_price,
                price_changed=price_changed,
                message=(
                    "Price validation completed" if is_valid else "Price has changed"
                ),
            )

            logger.info(
                "Menu item price validation completed",
                extra={
                    "menu_item_id": str(request.menu_item_id),
                    "is_valid": is_valid,
                    "price_changed": price_changed,
                },
            )

            return validation_result

        except Exception as e:
            logger.error(
                "Failed to validate menu item price",
                extra={
                    "error": str(e),
                    "menu_item_id": str(request.menu_item_id),
                },
            )
            raise
