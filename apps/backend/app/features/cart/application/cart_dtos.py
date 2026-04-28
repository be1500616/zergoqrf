"""Cart Data Transfer Objects.

This module contains DTOs for transferring cart data between layers.
DTOs are simple data containers without business logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from ..domain.cart_entities import CartSession, CartItem, SessionType
from ..domain.cart_vos import Money, Quantity, CustomizationOptions


class CartSessionRequestDTO(BaseModel):
    """DTO for cart session creation requests."""
    
    restaurant_id: UUID = Field(..., description="Restaurant ID")
    table_id: Optional[UUID] = Field(None, description="Table ID")
    expires_hours: int = Field(default=2, description="Session expiration in hours")


class CartSessionResponseDTO(BaseModel):
    """DTO for cart session responses."""
    
    id: UUID = Field(..., description="Session ID")
    session_token: str = Field(..., description="Session token")
    session_type: str = Field(..., description="Session type")
    restaurant_id: UUID = Field(..., description="Restaurant ID")
    table_id: Optional[UUID] = Field(None, description="Table ID")
    user_id: Optional[UUID] = Field(None, description="User ID")
    item_count: int = Field(..., description="Number of items in cart")
    total_amount: Decimal = Field(..., description="Total cart amount")
    is_active: bool = Field(..., description="Whether session is active")
    expires_at: datetime = Field(..., description="Session expiration time")
    last_activity_at: datetime = Field(..., description="Last activity time")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class AddCartItemRequestDTO(BaseModel):
    """DTO for adding items to cart."""
    
    menu_item_id: UUID = Field(..., description="Menu item ID")
    quantity: int = Field(..., ge=1, le=50, description="Item quantity")
    customizations: Dict[str, Any] = Field(default_factory=dict, description="Item customizations")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Special instructions")


class UpdateCartItemRequestDTO(BaseModel):
    """DTO for updating cart items."""
    
    quantity: int = Field(..., ge=1, le=50, description="New item quantity")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Special instructions")


class CartItemResponseDTO(BaseModel):
    """DTO for cart item responses."""
    
    id: UUID = Field(..., description="Cart item ID")
    cart_session_id: UUID = Field(..., description="Cart session ID")
    menu_item_id: UUID = Field(..., description="Menu item ID")
    item_name: str = Field(..., description="Item name")
    item_description: Optional[str] = Field(None, description="Item description")
    base_price: Decimal = Field(..., description="Base item price")
    unit_price: Decimal = Field(..., description="Unit price with customizations")
    total_price: Decimal = Field(..., description="Total price")
    quantity: int = Field(..., description="Item quantity")
    customizations: Dict[str, Any] = Field(..., description="Item customizations")
    special_instructions: Optional[str] = Field(None, description="Special instructions")
    is_available: bool = Field(..., description="Whether item is available")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class CartSummaryResponseDTO(BaseModel):
    """DTO for cart summary responses."""
    
    session: CartSessionResponseDTO = Field(..., description="Cart session details")
    items: List[CartItemResponseDTO] = Field(..., description="Cart items")
    subtotal: Decimal = Field(..., description="Subtotal amount")
    tax_amount: Decimal = Field(..., description="Tax amount")
    total_amount: Decimal = Field(..., description="Total amount including tax")
    item_count: int = Field(..., description="Total item count")


class CartMigrationRequestDTO(BaseModel):
    """DTO for cart migration requests."""
    
    anonymous_session_token: str = Field(..., description="Anonymous session token")
    user_id: UUID = Field(..., description="User ID for authenticated session")
    restaurant_id: UUID = Field(..., description="Restaurant ID")


class CartMigrationResponseDTO(BaseModel):
    """DTO for cart migration responses."""
    
    new_session: CartSessionResponseDTO = Field(..., description="New authenticated session")
    migrated_items_count: int = Field(..., description="Number of items migrated")
    migration_successful: bool = Field(..., description="Whether migration was successful")


class PriceValidationRequestDTO(BaseModel):
    """DTO for price validation requests."""
    
    menu_item_id: UUID = Field(..., description="Menu item ID")
    expected_price: Decimal = Field(..., description="Expected price from cart")


class PriceValidationResponseDTO(BaseModel):
    """DTO for price validation responses."""
    
    menu_item_id: UUID = Field(..., description="Menu item ID")
    expected_price: Decimal = Field(..., description="Expected price from cart")
    actual_price: Decimal = Field(..., description="Actual price from menu")
    is_valid: bool = Field(..., description="Whether price is valid")
    price_difference: Decimal = Field(..., description="Price difference")


# Conversion functions between entities and DTOs

def cart_session_entity_to_dto(session: CartSession) -> CartSessionResponseDTO:
    """Convert CartSession entity to DTO.
    
    Args:
        session: Cart session entity
        
    Returns:
        Cart session response DTO
    """
    return CartSessionResponseDTO(
        id=session.id,
        session_token=session.session_token.value,
        session_type=session.session_type.value,
        restaurant_id=session.restaurant_id,
        table_id=session.table_id,
        user_id=session.user_id,
        item_count=session.item_count,
        total_amount=session.total_amount.amount,
        is_active=session.is_active,
        expires_at=session.expires_at,
        last_activity_at=session.last_activity_at,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def cart_item_entity_to_dto(item: CartItem) -> CartItemResponseDTO:
    """Convert CartItem entity to DTO.
    
    Args:
        item: Cart item entity
        
    Returns:
        Cart item response DTO
    """
    return CartItemResponseDTO(
        id=item.id,
        cart_session_id=item.cart_session_id,
        menu_item_id=item.menu_item_id,
        item_name=item.item_name,
        item_description=item.item_description,
        base_price=item.base_price.amount,
        unit_price=item.unit_price.amount,
        total_price=item.total_price.amount,
        quantity=item.quantity.value,
        customizations=item.customizations.options,
        special_instructions=item.special_instructions,
        is_available=item.is_available,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
