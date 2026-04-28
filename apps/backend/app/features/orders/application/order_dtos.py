"""Order Data Transfer Objects.

This module contains DTOs for transferring order data between layers.
DTOs are simple data containers without business logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator

from ..domain.order_entities import Order, OrderItem, PaymentCollection
from ..domain.order_enums import OrderStatus, PaymentStatus, PaymentMethod
from ..domain.order_vos import Money, OrderNumber, PaymentReference, CustomerInfo, GSTCalculation


# Request DTOs
class CustomerInfoRequestDTO(BaseModel):
    """DTO for customer information in order requests."""
    
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


class CreateOrderRequestDTO(BaseModel):
    """DTO for order creation requests."""
    
    cart_session_id: UUID = Field(..., description="Cart session ID to convert to order")
    customer_info: CustomerInfoRequestDTO = Field(..., description="Customer information")
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


class UpdateOrderStatusRequestDTO(BaseModel):
    """DTO for order status update requests."""
    
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


class CollectPaymentRequestDTO(BaseModel):
    """DTO for payment collection requests."""
    
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


# Response DTOs
class OrderItemResponseDTO(BaseModel):
    """DTO for order item responses."""
    
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


class PaymentCollectionResponseDTO(BaseModel):
    """DTO for payment collection responses."""
    
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


class OrderResponseDTO(BaseModel):
    """DTO for order responses."""
    
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
    items: List[OrderItemResponseDTO]
    payment_collections: List[PaymentCollectionResponseDTO]
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


class OrderSummaryResponseDTO(BaseModel):
    """DTO for order summary responses (lightweight)."""
    
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


class RestaurantOrdersResponseDTO(BaseModel):
    """DTO for restaurant orders list responses."""
    
    orders: List[OrderSummaryResponseDTO]
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


# Conversion functions
def order_entity_to_dto(order: Order) -> OrderResponseDTO:
    """Convert order entity to response DTO."""
    return OrderResponseDTO(
        id=order.id,
        order_number=order.order_number.value,
        restaurant_id=order.restaurant_id,
        table_id=order.table_id,
        user_id=order.user_id,
        customer_name=order.customer_info.name,
        customer_phone=order.customer_info.phone,
        customer_email=order.customer_info.email,
        order_status=order.order_status,
        payment_status=order.payment_status,
        payment_method=order.payment_method,
        payment_reference=order.payment_reference.value,
        special_instructions=order.special_instructions,
        estimated_preparation_time=order.estimated_preparation_time.minutes,
        subtotal=order.gst_calculation.subtotal.amount,
        gst_rate=order.gst_calculation.gst_rate,
        gst_amount=order.gst_calculation.gst_amount.amount,
        total_amount=order.gst_calculation.total_amount.amount,
        items=[order_item_entity_to_dto(item) for item in order.items],
        payment_collections=[payment_collection_entity_to_dto(pc) for pc in order.payment_collections],
        placed_at=order.placed_at,
        confirmed_at=order.confirmed_at,
        preparing_at=order.preparing_at,
        ready_at=order.ready_at,
        completed_at=order.completed_at,
        cancelled_at=order.cancelled_at,
        payment_collected_at=order.payment_collected_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def order_item_entity_to_dto(item: OrderItem) -> OrderItemResponseDTO:
    """Convert order item entity to response DTO."""
    return OrderItemResponseDTO(
        id=item.id,
        menu_item_id=item.menu_item_id,
        item_name=item.item_name,
        item_description=item.item_description,
        base_price=item.base_price.amount,
        quantity=item.quantity.value,
        unit_price=item.unit_price.amount,
        total_price=item.total_price.amount,
        customizations=item.customizations.customizations,
        special_instructions=item.special_instructions,
        is_available=item.is_available,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def payment_collection_entity_to_dto(collection: PaymentCollection) -> PaymentCollectionResponseDTO:
    """Convert payment collection entity to response DTO."""
    return PaymentCollectionResponseDTO(
        id=collection.id,
        payment_reference=collection.payment_reference.value,
        amount=collection.amount.amount,
        payment_method=collection.payment_method,
        collected_by=collection.collected_by,
        collected_at=collection.collected_at,
        collection_notes=collection.collection_notes,
        verification_code=collection.verification_code,
        created_at=collection.created_at,
    )
