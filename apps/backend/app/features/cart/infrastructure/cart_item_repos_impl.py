"""Cart item repository implementation using Supabase.

This module provides the concrete implementation of the cart item repository
interface using Supabase as the data store.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from supabase import AClient

from ..domain.cart_entities import CartItem
from ..domain.cart_repos import ICartItemRepository
from ..domain.cart_vos import CustomizationOptions, Money, Quantity
from ..domain.cart_exceptions import CartOperationError

logger = logging.getLogger(__name__)


class CartItemRepositoryImpl(ICartItemRepository):
    """Supabase implementation of cart item repository."""
    
    def __init__(self, supabase_client: AClient):
        """Initialize the repository.

        Args:
            supabase_client: Async Supabase client instance
        """
        self._client = supabase_client
    
    async def add_item(self, cart_item: CartItem) -> CartItem:
        """Add item to cart.
        
        Args:
            cart_item: Cart item to add
            
        Returns:
            Added cart item
            
        Raises:
            CartOperationError: If item addition fails
        """
        try:
            logger.info(
                "Adding cart item to database",
                extra={
                    "item_id": str(cart_item.id),
                    "cart_session_id": str(cart_item.cart_session_id),
                    "menu_item_id": str(cart_item.menu_item_id),
                    "quantity": cart_item.quantity.value,
                }
            )
            
            item_data = {
                "id": str(cart_item.id),
                "cart_session_id": str(cart_item.cart_session_id),
                "restaurant_id": str(cart_item.restaurant_id),
                "menu_item_id": str(cart_item.menu_item_id),
                "item_name": cart_item.item_name,
                "item_description": cart_item.item_description,
                "base_price": float(cart_item.base_price.amount),
                "quantity": cart_item.quantity.value,
                "customizations": cart_item.customizations.options,
                "special_instructions": cart_item.special_instructions,
                "unit_price": float(cart_item.unit_price.amount),
                "total_price": float(cart_item.total_price.amount),
                "is_available": cart_item.is_available,
                "created_at": cart_item.created_at.isoformat(),
                "updated_at": cart_item.updated_at.isoformat(),
            }
            
            result = await self._client.table("cart_items").insert(item_data).execute()
            
            if not result.data:
                raise CartOperationError("add_item", "No item inserted")
            
            logger.info(
                "Cart item added successfully",
                extra={
                    "item_id": str(cart_item.id),
                    "total_price": str(cart_item.total_price.amount),
                }
            )
            
            return cart_item
            
        except Exception as e:
            logger.error(
                "Failed to add cart item",
                extra={
                    "error": str(e),
                    "item_id": str(cart_item.id),
                    "cart_session_id": str(cart_item.cart_session_id),
                }
            )
            raise CartOperationError("add_item", str(e))
    
    async def get_by_id(self, item_id: UUID) -> Optional[CartItem]:
        """Get cart item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Cart item if found, None otherwise
        """
        try:
            result = await self._client.table("cart_items").select("*").eq("id", str(item_id)).execute()
            
            if not result.data:
                return None
            
            item_data = result.data[0]
            return self._map_to_entity(item_data)
            
        except Exception as e:
            logger.error(
                "Failed to get cart item by ID",
                extra={
                    "error": str(e),
                    "item_id": str(item_id),
                }
            )
            return None
    
    async def get_items_by_session(self, session_id: UUID) -> List[CartItem]:
        """Get all items in a cart session.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            List of cart items
        """
        try:
            result = await self._client.table("cart_items").select("*").eq(
                "cart_session_id", str(session_id)
            ).order("created_at").execute()
            
            if not result.data:
                return []
            
            return [self._map_to_entity(item_data) for item_data in result.data]
            
        except Exception as e:
            logger.error(
                "Failed to get cart items by session",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                }
            )
            return []
    
    async def get_item_by_menu_item(
        self, 
        session_id: UUID, 
        menu_item_id: UUID,
        customizations: dict
    ) -> Optional[CartItem]:
        """Get cart item by menu item and customizations.
        
        Args:
            session_id: Cart session ID
            menu_item_id: Menu item ID
            customizations: Item customizations
            
        Returns:
            Cart item if found, None otherwise
        """
        try:
            result = await self._client.table("cart_items").select("*").eq(
                "cart_session_id", str(session_id)
            ).eq(
                "menu_item_id", str(menu_item_id)
            ).eq(
                "customizations", customizations
            ).limit(1).execute()
            
            if not result.data:
                return None
            
            item_data = result.data[0]
            return self._map_to_entity(item_data)
            
        except Exception as e:
            logger.error(
                "Failed to get cart item by menu item",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                    "menu_item_id": str(menu_item_id),
                }
            )
            return None
    
    async def update_item(self, cart_item: CartItem) -> CartItem:
        """Update cart item.
        
        Args:
            cart_item: Cart item to update
            
        Returns:
            Updated cart item
            
        Raises:
            CartOperationError: If item update fails
        """
        try:
            logger.info(
                "Updating cart item in database",
                extra={
                    "item_id": str(cart_item.id),
                    "new_quantity": cart_item.quantity.value,
                    "new_total_price": str(cart_item.total_price.amount),
                }
            )
            
            update_data = {
                "quantity": cart_item.quantity.value,
                "customizations": cart_item.customizations.options,
                "special_instructions": cart_item.special_instructions,
                "unit_price": float(cart_item.unit_price.amount),
                "total_price": float(cart_item.total_price.amount),
                "is_available": cart_item.is_available,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            result = await self._client.table("cart_items").update(update_data).eq(
                "id", str(cart_item.id)
            ).execute()
            
            if not result.data:
                raise CartOperationError("update_item", "No item updated")
            
            logger.info(
                "Cart item updated successfully",
                extra={
                    "item_id": str(cart_item.id),
                    "new_total_price": str(cart_item.total_price.amount),
                }
            )
            
            return cart_item
            
        except Exception as e:
            logger.error(
                "Failed to update cart item",
                extra={
                    "error": str(e),
                    "item_id": str(cart_item.id),
                }
            )
            raise CartOperationError("update_item", str(e))
    
    async def remove_item(self, item_id: UUID) -> bool:
        """Remove item from cart.
        
        Args:
            item_id: Item ID to remove
            
        Returns:
            True if item was removed, False otherwise
        """
        try:
            logger.info(
                "Removing cart item from database",
                extra={"item_id": str(item_id)}
            )
            
            result = await self._client.table("cart_items").delete().eq("id", str(item_id)).execute()
            
            removed = len(result.data) > 0 if result.data else False
            
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
    
    async def clear_cart(self, session_id: UUID) -> int:
        """Clear all items from cart.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            Number of items removed
        """
        try:
            logger.info(
                "Clearing cart items from database",
                extra={"session_id": str(session_id)}
            )
            
            result = await self._client.table("cart_items").delete().eq(
                "cart_session_id", str(session_id)
            ).execute()
            
            removed_count = len(result.data) if result.data else 0
            
            logger.info(
                "Cart items cleared successfully",
                extra={
                    "session_id": str(session_id),
                    "removed_count": removed_count,
                }
            )
            
            return removed_count
            
        except Exception as e:
            logger.error(
                "Failed to clear cart items",
                extra={
                    "error": str(e),
                    "session_id": str(session_id),
                }
            )
            return 0
    
    def _map_to_entity(self, item_data: dict) -> CartItem:
        """Map database record to domain entity.
        
        Args:
            item_data: Database record
            
        Returns:
            CartItem entity
        """
        return CartItem(
            id=UUID(item_data["id"]),
            cart_session_id=UUID(item_data["cart_session_id"]),
            restaurant_id=UUID(item_data["restaurant_id"]),
            menu_item_id=UUID(item_data["menu_item_id"]),
            item_name=item_data["item_name"],
            item_description=item_data.get("item_description"),
            base_price=Money(Decimal(str(item_data["base_price"]))),
            quantity=Quantity(item_data["quantity"]),
            unit_price=Money(Decimal(str(item_data["unit_price"]))),
            total_price=Money(Decimal(str(item_data["total_price"]))),
            customizations=CustomizationOptions(item_data.get("customizations", {})),
            special_instructions=item_data.get("special_instructions"),
            is_available=item_data.get("is_available", True),
            created_at=datetime.fromisoformat(item_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(item_data["updated_at"].replace("Z", "+00:00")),
        )
