"""Cart repository interfaces.

This module contains abstract repository interfaces that define contracts
for data persistence operations in the cart domain.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .cart_entities import CartSession, CartItem
from .cart_vos import CartSessionToken


class ICartSessionRepository(ABC):
    """Abstract interface for cart session repository."""
    
    @abstractmethod
    async def create_anonymous_session(
        self,
        anonymous_session_id: UUID,
        restaurant_id: UUID,
        table_id: Optional[UUID] = None,
        expires_hours: int = 2,
    ) -> CartSession:
        """Create a new anonymous cart session.
        
        Args:
            anonymous_session_id: Anonymous session ID to link to
            restaurant_id: Restaurant ID
            table_id: Optional table ID
            expires_hours: Session expiration in hours
            
        Returns:
            Created cart session
        """
        pass
    
    @abstractmethod
    async def create_authenticated_session(
        self,
        user_id: UUID,
        restaurant_id: UUID,
        table_id: Optional[UUID] = None,
        expires_hours: int = 24,
    ) -> CartSession:
        """Create a new authenticated cart session.
        
        Args:
            user_id: User ID
            restaurant_id: Restaurant ID
            table_id: Optional table ID
            expires_hours: Session expiration in hours
            
        Returns:
            Created cart session
        """
        pass
    
    @abstractmethod
    async def get_by_token(self, session_token: CartSessionToken) -> Optional[CartSession]:
        """Get cart session by token.
        
        Args:
            session_token: Session token
            
        Returns:
            Cart session if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[CartSession]:
        """Get cart session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Cart session if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_active_session_for_user(
        self, 
        user_id: UUID, 
        restaurant_id: UUID
    ) -> Optional[CartSession]:
        """Get active cart session for authenticated user.
        
        Args:
            user_id: User ID
            restaurant_id: Restaurant ID
            
        Returns:
            Active cart session if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def extend_session_activity(self, session_token: CartSessionToken) -> bool:
        """Extend session activity and expiration.
        
        Args:
            session_token: Session token
            
        Returns:
            True if session was extended, False otherwise
        """
        pass
    
    @abstractmethod
    async def migrate_anonymous_to_authenticated(
        self,
        anonymous_session_token: CartSessionToken,
        user_id: UUID,
        restaurant_id: UUID,
    ) -> CartSession:
        """Migrate anonymous cart session to authenticated.
        
        Args:
            anonymous_session_token: Anonymous session token
            user_id: User ID for new authenticated session
            restaurant_id: Restaurant ID
            
        Returns:
            New authenticated cart session
        """
        pass
    
    @abstractmethod
    async def update_session_totals(self, session_id: UUID) -> bool:
        """Update session item count and total amount.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def deactivate_session(self, session_id: UUID) -> bool:
        """Deactivate a cart session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session was deactivated, False otherwise
        """
        pass


class ICartItemRepository(ABC):
    """Abstract interface for cart item repository."""
    
    @abstractmethod
    async def add_item(self, cart_item: CartItem) -> CartItem:
        """Add item to cart.
        
        Args:
            cart_item: Cart item to add
            
        Returns:
            Added cart item
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[CartItem]:
        """Get cart item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Cart item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_items_by_session(self, session_id: UUID) -> List[CartItem]:
        """Get all items in a cart session.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            List of cart items
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def update_item(self, cart_item: CartItem) -> CartItem:
        """Update cart item.
        
        Args:
            cart_item: Cart item to update
            
        Returns:
            Updated cart item
        """
        pass
    
    @abstractmethod
    async def remove_item(self, item_id: UUID) -> bool:
        """Remove item from cart.
        
        Args:
            item_id: Item ID to remove
            
        Returns:
            True if item was removed, False otherwise
        """
        pass
    
    @abstractmethod
    async def clear_cart(self, session_id: UUID) -> int:
        """Clear all items from cart.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            Number of items removed
        """
        pass
    
    @abstractmethod
    async def get_cart_item_count(self, session_id: UUID) -> int:
        """Get total number of items in cart.
        
        Args:
            session_id: Cart session ID
            
        Returns:
            Total item count
        """
        pass
