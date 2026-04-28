"""Cart item management use cases.

This module contains use cases for managing cart items,
including adding, updating, and removing items from carts.
"""

import logging
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from ...domain.cart_entities import CartItem
from ...domain.cart_repos import ICartItemRepository, ICartSessionRepository
from ...domain.cart_vos import CartSessionToken, CustomizationOptions, Money, Quantity
from ...domain.cart_exceptions import (
    CartSessionNotFoundError,
    CartSessionExpiredError,
    CartItemNotFoundError,
    CartFullError,
    MenuItemUnavailableError,
)
from ..cart_dtos import (
    AddCartItemRequestDTO,
    UpdateCartItemRequestDTO,
    CartItemResponseDTO,
    cart_item_entity_to_dto,
)

logger = logging.getLogger(__name__)


class AddCartItemUseCase:
    """Use case for adding items to cart."""
    
    def __init__(
        self,
        cart_item_repository: ICartItemRepository,
        cart_session_repository: ICartSessionRepository,
    ):
        """Initialize the use case.
        
        Args:
            cart_item_repository: Cart item repository
            cart_session_repository: Cart session repository
        """
        self._item_repository = cart_item_repository
        self._session_repository = cart_session_repository
    
    async def execute(
        self,
        session_token: str,
        request: AddCartItemRequestDTO,
    ) -> CartItemResponseDTO:
        """Add item to cart.
        
        Args:
            session_token: Cart session token
            request: Add item request DTO
            
        Returns:
            Added cart item DTO
            
        Raises:
            CartSessionNotFoundError: If session not found
            CartSessionExpiredError: If session is expired
            CartFullError: If cart is full
            MenuItemUnavailableError: If menu item is unavailable
        """
        try:
            logger.info(
                "Adding item to cart",
                extra={
                    "session_token": session_token[:8] + "...",
                    "menu_item_id": str(request.menu_item_id),
                    "quantity": request.quantity,
                }
            )
            
            # Get and validate cart session
            token = CartSessionToken(session_token)
            session = await self._session_repository.get_by_token(token)
            
            if not session:
                raise CartSessionNotFoundError(session_token)
            
            if not session.is_valid():
                raise CartSessionExpiredError(session_token)
            
            # Check cart capacity
            if session.item_count >= 50:
                raise CartFullError(session.item_count)
            
            # Check if item already exists with same customizations
            existing_item = await self._item_repository.get_item_by_menu_item(
                session_id=session.id,
                menu_item_id=request.menu_item_id,
                customizations=request.customizations,
            )
            
            if existing_item:
                # Update quantity of existing item
                new_quantity = Quantity(existing_item.quantity.value + request.quantity)
                existing_item.update_quantity(new_quantity)
                updated_item = await self._item_repository.update_item(existing_item)
                
                logger.info(
                    "Updated existing cart item quantity",
                    extra={
                        "item_id": str(updated_item.id),
                        "new_quantity": updated_item.quantity.value,
                    }
                )
                
                return cart_item_entity_to_dto(updated_item)
            
            # TODO: Get menu item details from menu service
            # For now, using placeholder values
            item_name = f"Menu Item {request.menu_item_id}"
            item_description = "Menu item description"
            base_price = Money(Decimal("10.00"))  # Placeholder
            unit_price = Money(Decimal("10.00"))  # Placeholder, should include customizations
            
            # Create new cart item
            cart_item = CartItem(
                id=uuid4(),
                cart_session_id=session.id,
                restaurant_id=session.restaurant_id,
                menu_item_id=request.menu_item_id,
                item_name=item_name,
                item_description=item_description,
                base_price=base_price,
                quantity=Quantity(request.quantity),
                unit_price=unit_price,
                total_price=Money(unit_price.amount * request.quantity),
                customizations=CustomizationOptions(request.customizations),
                special_instructions=request.special_instructions,
            )
            
            added_item = await self._item_repository.add_item(cart_item)
            
            logger.info(
                "Cart item added successfully",
                extra={
                    "item_id": str(added_item.id),
                    "session_id": str(session.id),
                    "total_price": str(added_item.total_price.amount),
                }
            )
            
            return cart_item_entity_to_dto(added_item)
            
        except (CartSessionNotFoundError, CartSessionExpiredError, CartFullError):
            raise
        except Exception as e:
            logger.error(
                "Failed to add item to cart",
                extra={
                    "error": str(e),
                    "session_token": session_token[:8] + "...",
                    "menu_item_id": str(request.menu_item_id),
                }
            )
            raise


class UpdateCartItemUseCase:
    """Use case for updating cart items."""
    
    def __init__(self, cart_item_repository: ICartItemRepository):
        """Initialize the use case.
        
        Args:
            cart_item_repository: Cart item repository
        """
        self._repository = cart_item_repository
    
    async def execute(
        self,
        item_id: UUID,
        request: UpdateCartItemRequestDTO,
    ) -> CartItemResponseDTO:
        """Update cart item.
        
        Args:
            item_id: Cart item ID
            request: Update item request DTO
            
        Returns:
            Updated cart item DTO
            
        Raises:
            CartItemNotFoundError: If item not found
        """
        try:
            logger.info(
                "Updating cart item",
                extra={
                    "item_id": str(item_id),
                    "new_quantity": request.quantity,
                }
            )
            
            item = await self._repository.get_by_id(item_id)
            
            if not item:
                raise CartItemNotFoundError(str(item_id))
            
            # Update quantity
            item.update_quantity(Quantity(request.quantity))
            
            # Update customizations if provided
            if request.customizations is not None:
                # TODO: Calculate new unit price based on customizations
                new_unit_price = item.base_price  # Placeholder
                item.update_customizations(
                    CustomizationOptions(request.customizations),
                    new_unit_price,
                )
            
            # Update special instructions
            if request.special_instructions is not None:
                item.special_instructions = request.special_instructions
            
            updated_item = await self._repository.update_item(item)
            
            logger.info(
                "Cart item updated successfully",
                extra={
                    "item_id": str(updated_item.id),
                    "new_total_price": str(updated_item.total_price.amount),
                }
            )
            
            return cart_item_entity_to_dto(updated_item)
            
        except CartItemNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to update cart item",
                extra={
                    "error": str(e),
                    "item_id": str(item_id),
                }
            )
            raise


class RemoveCartItemUseCase:
    """Use case for removing items from cart."""
    
    def __init__(self, cart_item_repository: ICartItemRepository):
        """Initialize the use case.
        
        Args:
            cart_item_repository: Cart item repository
        """
        self._repository = cart_item_repository
    
    async def execute(self, item_id: UUID) -> bool:
        """Remove item from cart.
        
        Args:
            item_id: Cart item ID
            
        Returns:
            True if item was removed, False otherwise
        """
        try:
            logger.info(
                "Removing cart item",
                extra={"item_id": str(item_id)}
            )
            
            removed = await self._repository.remove_item(item_id)
            
            if removed:
                logger.info(
                    "Cart item removed successfully",
                    extra={"item_id": str(item_id)}
                )
            else:
                logger.warning(
                    "Cart item not found for removal",
                    extra={"item_id": str(item_id)}
                )
            
            return removed
            
        except Exception as e:
            logger.error(
                "Failed to remove cart item",
                extra={
                    "error": str(e),
                    "item_id": str(item_id),
                }
            )
            return False


class GetCartItemsUseCase:
    """Use case for retrieving cart items."""
    
    def __init__(self, cart_item_repository: ICartItemRepository):
        """Initialize the use case.
        
        Args:
            cart_item_repository: Cart item repository
        """
        self._repository = cart_item_repository
    
    async def execute(self, session_id: UUID) -> List[CartItemResponseDTO]:
        """Get all items in cart session.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            List of cart item DTOs
        """
        try:
            items = await self._repository.get_items_by_session(session_id)
            return [cart_item_entity_to_dto(item) for item in items]
            
        except Exception as e:
            logger.error(
                "Failed to get cart items",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                }
            )
            return []


class ClearCartUseCase:
    """Use case for clearing all items from cart."""
    
    def __init__(self, cart_item_repository: ICartItemRepository):
        """Initialize the use case.
        
        Args:
            cart_item_repository: Cart item repository
        """
        self._repository = cart_item_repository
    
    async def execute(self, session_id: UUID) -> int:
        """Clear all items from cart.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            Number of items removed
        """
        try:
            logger.info(
                "Clearing cart",
                extra={"session_id": str(session_id)}
            )
            
            removed_count = await self._repository.clear_cart(session_id)
            
            logger.info(
                "Cart cleared successfully",
                extra={
                    "session_id": str(session_id),
                    "removed_count": removed_count,
                }
            )
            
            return removed_count
            
        except Exception as e:
            logger.error(
                "Failed to clear cart",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                }
            )
            return 0
