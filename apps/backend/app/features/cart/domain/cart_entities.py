"""Cart domain entities.

This module contains the core business entities for the cart management system.
Entities have identity and encapsulate business logic and rules.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from .cart_vos import Money, Quantity, CartSessionToken, CustomizationOptions
from .cart_exceptions import CartFullError, InvalidQuantityError


class SessionType(Enum):
    """Enumeration of cart session types."""
    
    ANONYMOUS = "anonymous"
    AUTHENTICATED = "authenticated"


class CartSession:
    """Cart session entity managing session lifecycle and metadata."""
    
    def __init__(
        self,
        id: UUID,
        session_token: CartSessionToken,
        session_type: SessionType,
        restaurant_id: UUID,
        expires_at: datetime,
        table_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        anonymous_session_id: Optional[UUID] = None,
        item_count: int = 0,
        total_amount: Money = None,
        is_active: bool = True,
        last_activity_at: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        """Initialize cart session.
        
        Args:
            id: Session ID
            session_token: Session token
            session_type: Type of session (anonymous/authenticated)
            restaurant_id: Restaurant ID
            expires_at: Session expiration time
            table_id: Optional table ID
            user_id: Optional user ID (for authenticated sessions)
            anonymous_session_id: Optional anonymous session ID
            item_count: Number of items in cart
            total_amount: Total cart amount
            is_active: Whether session is active
            last_activity_at: Last activity timestamp
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.session_token = session_token
        self.session_type = session_type
        self.restaurant_id = restaurant_id
        self.table_id = table_id
        self.user_id = user_id
        self.anonymous_session_id = anonymous_session_id
        self.expires_at = expires_at
        self.item_count = item_count
        self.total_amount = total_amount or Money(0)
        self.is_active = is_active
        self.last_activity_at = last_activity_at or datetime.now(timezone.utc)
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        
        # Validate business rules
        self._validate_session_constraints()
    
    def _validate_session_constraints(self):
        """Validate session business constraints."""
        if self.session_type == SessionType.ANONYMOUS:
            if self.user_id is not None:
                raise ValueError("Anonymous sessions cannot have user_id")
            if self.anonymous_session_id is None:
                raise ValueError("Anonymous sessions must have anonymous_session_id")
        elif self.session_type == SessionType.AUTHENTICATED:
            if self.user_id is None:
                raise ValueError("Authenticated sessions must have user_id")
            if self.anonymous_session_id is not None:
                raise ValueError("Authenticated sessions cannot have anonymous_session_id")
        
        if self.item_count < 0:
            raise ValueError("Item count cannot be negative")
        if self.item_count > 50:
            raise CartFullError(self.item_count)
    
    def is_valid(self) -> bool:
        """Check if session is valid (not expired and active).
        
        Returns:
            True if session is valid, False otherwise
        """
        now = datetime.now(timezone.utc)
        return self.is_active and self.expires_at > now
    
    def is_expired(self) -> bool:
        """Check if session has expired.
        
        Returns:
            True if session is expired, False otherwise
        """
        now = datetime.now(timezone.utc)
        return self.expires_at <= now
    
    def can_add_items(self, quantity: int) -> bool:
        """Check if items can be added to cart.
        
        Args:
            quantity: Number of items to add
            
        Returns:
            True if items can be added, False otherwise
        """
        return (self.item_count + quantity) <= 50
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self):
        """Deactivate the session."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another CartSession."""
        if not isinstance(other, CartSession):
            return False
        return self.id == other.id
    
    def __str__(self) -> str:
        """String representation of cart session."""
        return f"CartSession({self.id}, {self.session_type.value}, items={self.item_count})"
    
    def __repr__(self) -> str:
        """Developer representation of cart session."""
        return (
            f"CartSession(id={self.id}, session_type={self.session_type.value}, "
            f"restaurant_id={self.restaurant_id}, item_count={self.item_count}, "
            f"is_active={self.is_active})"
        )


class CartItem:
    """Cart item entity representing individual items in a cart."""
    
    def __init__(
        self,
        id: UUID,
        cart_session_id: UUID,
        restaurant_id: UUID,
        menu_item_id: UUID,
        item_name: str,
        base_price: Money,
        quantity: Quantity,
        unit_price: Money,
        total_price: Money,
        item_description: Optional[str] = None,
        customizations: CustomizationOptions = None,
        special_instructions: Optional[str] = None,
        is_available: bool = True,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        """Initialize cart item.
        
        Args:
            id: Item ID
            cart_session_id: Cart session ID
            restaurant_id: Restaurant ID
            menu_item_id: Menu item ID
            item_name: Item name
            base_price: Base item price
            quantity: Item quantity
            unit_price: Unit price with customizations
            total_price: Total price (unit_price * quantity)
            item_description: Optional item description
            customizations: Item customizations
            special_instructions: Special instructions
            is_available: Whether item is available
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.cart_session_id = cart_session_id
        self.restaurant_id = restaurant_id
        self.menu_item_id = menu_item_id
        self.item_name = item_name
        self.item_description = item_description
        self.base_price = base_price
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price
        self.customizations = customizations or CustomizationOptions()
        self.special_instructions = special_instructions
        self.is_available = is_available
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        
        # Validate business rules
        self._validate_pricing()
    
    def _validate_pricing(self):
        """Validate pricing consistency."""
        expected_total = Money(self.unit_price.amount * self.quantity.value)
        if self.total_price != expected_total:
            raise ValueError(
                f"Total price {self.total_price} does not match "
                f"unit price {self.unit_price} * quantity {self.quantity}"
            )
    
    def update_quantity(self, new_quantity: Quantity):
        """Update item quantity and recalculate total price.
        
        Args:
            new_quantity: New quantity
        """
        self.quantity = new_quantity
        self.total_price = Money(self.unit_price.amount * new_quantity.value)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_availability(self, is_available: bool):
        """Update item availability status.
        
        Args:
            is_available: New availability status
        """
        self.is_available = is_available
        self.updated_at = datetime.now(timezone.utc)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another CartItem."""
        if not isinstance(other, CartItem):
            return False
        return self.id == other.id
    
    def __str__(self) -> str:
        """String representation of cart item."""
        return f"CartItem({self.item_name}, qty={self.quantity}, total={self.total_price})"
    
    def __repr__(self) -> str:
        """Developer representation of cart item."""
        return (
            f"CartItem(id={self.id}, menu_item_id={self.menu_item_id}, "
            f"quantity={self.quantity}, total_price={self.total_price})"
        )
