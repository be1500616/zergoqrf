"""Order Pydantic schemas.

This module contains Pydantic schemas for order API requests and responses,
providing validation and serialization for the presentation layer.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator

from ..domain.order_enums import OrderStatus, PaymentStatus, PaymentMethod


# Request Schemas
class CustomerInfoSchema(BaseModel):
    """Schema for customer information in order requests."""
    
    name: str = Field(..., min_length=2, max_length=255, description="Customer name")
    phone: str = Field(..., pattern=r'^\+91[6-9]\d{9}$', description="Indian phone number (+91)")
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', description="Email address")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "phone": "+919876543210",
                "email": "john@example.com"
            }
        }


class CreateOrderSchema(BaseModel):
    """Schema for order creation requests."""
    
    cart_session_id: UUID = Field(..., description="Cart session ID to convert to order")
    customer_info: CustomerInfoSchema = Field(..., description="Customer information")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Order-level special instructions")
    table_id: Optional[UUID] = Field(None, description="Table ID if dining in")
    
    class Config:
        schema_extra = {
            "example": {
                "cart_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "customer_info": {
                    "name": "John Doe",
                    "phone": "+919876543210",
                    "email": "john@example.com"
                },
                "special_instructions": "Please make it extra spicy",
                "table_id": "550e8400-e29b-41d4-a716-446655440001"
            }
        }


class UpdateOrderStatusSchema(BaseModel):
    """Schema for order status update requests."""
    
    new_status: OrderStatus = Field(..., description="New order status")
    change_reason: Optional[str] = Field(None, max_length=255, description="Reason for status change")
    change_notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
    class Config:
        schema_extra = {
            "example": {
                "new_status": "preparing",
                "change_reason": "Payment collected, starting preparation",
                "change_notes": "Customer requested extra spicy"
            }
        }


class CollectPaymentSchema(BaseModel):
    """Schema for payment collection requests."""
    
    payment_reference: str = Field(..., description="Payment reference from order")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH, description="Payment method")
    collection_notes: Optional[str] = Field(None, max_length=500, description="Payment collection notes")
    verification_code: Optional[str] = Field(None, max_length=10, description="Customer verification code")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate payment amount precision."""
        if v.as_tuple().exponent < -2:
            raise ValueError('Amount cannot have more than 2 decimal places')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "payment_reference": "PAY-20250928-143022-123",
                "amount": 15.75,
                "payment_method": "cash",
                "collection_notes": "Cash payment collected at counter",
                "verification_code": "1234"
            }
        }


# Response Schemas
class OrderItemSchema(BaseModel):
    """Schema for order item responses."""
    
    id: UUID
    menu_item_id: UUID
    item_name: str
    item_description: Optional[str]
    base_price: Decimal
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    customizations: Dict[str, Any]
    special_instructions: Optional[str]
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "menu_item_id": "550e8400-e29b-41d4-a716-446655440001",
                "item_name": "Chicken Biryani",
                "item_description": "Aromatic basmati rice with tender chicken",
                "base_price": 15.00,
                "quantity": 2,
                "unit_price": 15.00,
                "total_price": 30.00,
                "customizations": {"spice_level": "medium", "size": "large"},
                "special_instructions": "Extra raita",
                "is_available": True,
                "created_at": "2025-09-28T10:30:00Z",
                "updated_at": "2025-09-28T10:30:00Z"
            }
        }


class PaymentCollectionSchema(BaseModel):
    """Schema for payment collection responses."""
    
    id: UUID
    payment_reference: str
    amount: Decimal
    payment_method: PaymentMethod
    collected_by: Optional[UUID]
    collected_at: datetime
    collection_notes: Optional[str]
    verification_code: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "payment_reference": "PAY-20250928-143022-123",
                "amount": 15.75,
                "payment_method": "cash",
                "collected_by": "550e8400-e29b-41d4-a716-446655440001",
                "collected_at": "2025-09-28T14:30:22Z",
                "collection_notes": "Cash payment collected at counter",
                "verification_code": "1234",
                "created_at": "2025-09-28T14:30:22Z"
            }
        }


class OrderSchema(BaseModel):
    """Schema for complete order responses."""
    
    id: UUID
    order_number: str
    restaurant_id: UUID
    table_id: Optional[UUID]
    user_id: Optional[UUID]
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    order_status: OrderStatus
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    payment_reference: str
    special_instructions: Optional[str]
    estimated_preparation_time: int
    subtotal: Decimal
    gst_rate: Decimal
    gst_amount: Decimal
    total_amount: Decimal
    items: List[OrderItemSchema]
    payment_collections: List[PaymentCollectionSchema]
    placed_at: datetime
    confirmed_at: Optional[datetime]
    preparing_at: Optional[datetime]
    ready_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    payment_collected_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "order_number": "ORD-20250928-0001",
                "restaurant_id": "550e8400-e29b-41d4-a716-446655440001",
                "table_id": "550e8400-e29b-41d4-a716-446655440002",
                "user_id": None,
                "customer_name": "John Doe",
                "customer_phone": "+919876543210",
                "customer_email": "john@example.com",
                "order_status": "placed",
                "payment_status": "payment_pending",
                "payment_method": "cash",
                "payment_reference": "PAY-20250928-143022-123",
                "special_instructions": "Please make it extra spicy",
                "estimated_preparation_time": 30,
                "subtotal": 15.00,
                "gst_rate": 0.05,
                "gst_amount": 0.75,
                "total_amount": 15.75,
                "items": [],
                "payment_collections": [],
                "placed_at": "2025-09-28T14:30:00Z",
                "confirmed_at": None,
                "preparing_at": None,
                "ready_at": None,
                "completed_at": None,
                "cancelled_at": None,
                "payment_collected_at": None,
                "created_at": "2025-09-28T14:30:00Z",
                "updated_at": "2025-09-28T14:30:00Z"
            }
        }


class OrderSummarySchema(BaseModel):
    """Schema for order summary responses (lightweight)."""
    
    id: UUID
    order_number: str
    customer_name: str
    customer_phone: str
    order_status: OrderStatus
    payment_status: PaymentStatus
    total_amount: Decimal
    payment_reference: str
    placed_at: datetime
    estimated_preparation_time: int
    items_count: int
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "order_number": "ORD-20250928-0001",
                "customer_name": "John Doe",
                "customer_phone": "+919876543210",
                "order_status": "placed",
                "payment_status": "payment_pending",
                "total_amount": 15.75,
                "payment_reference": "PAY-20250928-143022-123",
                "placed_at": "2025-09-28T14:30:00Z",
                "estimated_preparation_time": 30,
                "items_count": 2
            }
        }


class RestaurantOrdersSchema(BaseModel):
    """Schema for restaurant orders list responses."""
    
    orders: List[OrderSummarySchema]
    total_count: int
    has_more: bool
    
    class Config:
        schema_extra = {
            "example": {
                "orders": [],
                "total_count": 25,
                "has_more": True
            }
        }


class OrdersSummarySchema(BaseModel):
    """Schema for orders summary by status."""
    
    new_orders: int = Field(..., description="Orders with payment pending")
    paid_orders: int = Field(..., description="Orders with payment collected")
    preparing_orders: int = Field(..., description="Orders being prepared")
    ready_orders: int = Field(..., description="Orders ready for pickup/delivery")
    completed_orders_today: int = Field(..., description="Orders completed today")
    total_active_orders: int = Field(..., description="Total active orders")
    
    class Config:
        schema_extra = {
            "example": {
                "new_orders": 5,
                "paid_orders": 12,
                "preparing_orders": 8,
                "ready_orders": 3,
                "completed_orders_today": 45,
                "total_active_orders": 28
            }
        }
