"""Cart API schemas.

This module contains Pydantic schemas for cart management API endpoints,
providing request/response validation and documentation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class CreateAnonymousCartSessionRequest(BaseModel):
    """Request schema for creating anonymous cart sessions."""
    
    anonymous_session_id: UUID = Field(..., description="Anonymous session ID to link to")
    restaurant_id: UUID = Field(..., description="Restaurant ID")
    table_id: Optional[UUID] = Field(None, description="Table ID")


class CreateAuthenticatedCartSessionRequest(BaseModel):
    """Request schema for creating authenticated cart sessions."""
    
    restaurant_id: UUID = Field(..., description="Restaurant ID")
    table_id: Optional[UUID] = Field(None, description="Table ID")


class CartSessionResponse(BaseModel):
    """Response schema for cart sessions."""
    
    id: UUID = Field(..., description="Cart session ID")
    session_token: str = Field(..., description="Session token")
    session_type: str = Field(..., description="Session type (anonymous/authenticated)")
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


class AddCartItemRequest(BaseModel):
    """Request schema for adding items to cart."""
    
    menu_item_id: UUID = Field(..., description="Menu item ID")
    quantity: int = Field(..., ge=1, le=50, description="Item quantity")
    customizations: Dict[str, Any] = Field(default_factory=dict, description="Item customizations")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Special instructions")


class UpdateCartItemRequest(BaseModel):
    """Request schema for updating cart items."""
    
    quantity: int = Field(..., ge=1, le=50, description="New item quantity")
    customizations: Optional[Dict[str, Any]] = Field(None, description="Updated customizations")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Updated special instructions")


class CartItemResponse(BaseModel):
    """Response schema for cart items."""
    
    id: UUID = Field(..., description="Cart item ID")
    cart_session_id: UUID = Field(..., description="Cart session ID")
    menu_item_id: UUID = Field(..., description="Menu item ID")
    item_name: str = Field(..., description="Item name")
    item_description: Optional[str] = Field(None, description="Item description")
    base_price: Decimal = Field(..., description="Base item price")
    unit_price: Decimal = Field(..., description="Unit price with customizations")
    total_price: Decimal = Field(..., description="Total price (unit_price * quantity)")
    quantity: int = Field(..., description="Item quantity")
    customizations: Dict[str, Any] = Field(..., description="Item customizations")
    special_instructions: Optional[str] = Field(None, description="Special instructions")
    is_available: bool = Field(..., description="Whether item is available")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class CartSummaryResponse(BaseModel):
    """Response schema for cart summary."""
    
    session: CartSessionResponse = Field(..., description="Cart session details")
    items: List[CartItemResponse] = Field(..., description="Cart items")
    subtotal: Decimal = Field(..., description="Subtotal amount")
    tax_amount: Decimal = Field(..., description="Tax amount")
    total_amount: Decimal = Field(..., description="Total amount including tax")
    item_count: int = Field(..., description="Total item count")


class MigrateCartRequest(BaseModel):
    """Request schema for cart migration."""
    
    anonymous_session_token: str = Field(..., description="Anonymous session token")
    restaurant_id: UUID = Field(..., description="Restaurant ID")


class MigrateCartResponse(BaseModel):
    """Response schema for cart migration."""
    
    new_session: CartSessionResponse = Field(..., description="New authenticated session")
    migrated_items_count: int = Field(..., description="Number of items migrated")
    migration_successful: bool = Field(..., description="Whether migration was successful")


class ValidatePriceRequest(BaseModel):
    """Request schema for price validation."""
    
    menu_item_id: UUID = Field(..., description="Menu item ID")
    expected_base_price: Decimal = Field(..., description="Expected base price")
    customizations: Dict[str, Any] = Field(default_factory=dict, description="Item customizations")


class ValidatePriceResponse(BaseModel):
    """Response schema for price validation."""
    
    is_valid: bool = Field(..., description="Whether price is valid")
    current_base_price: Decimal = Field(..., description="Current base price")
    calculated_unit_price: Decimal = Field(..., description="Calculated unit price with customizations")
    price_changed: bool = Field(..., description="Whether price has changed")
    message: Optional[str] = Field(None, description="Validation message")


class CartOperationResponse(BaseModel):
    """Generic response schema for cart operations."""
    
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Operation message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Configuration
class Config:
    """Pydantic configuration."""
    
    json_encoders = {
        datetime: lambda v: v.isoformat(),
        Decimal: lambda v: float(v),
    }
    use_enum_values = True
    validate_assignment = True
