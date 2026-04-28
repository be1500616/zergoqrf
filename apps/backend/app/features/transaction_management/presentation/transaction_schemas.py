"""Transaction Management API Schemas.

This module defines Pydantic schemas for transaction management API endpoints.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ..domain.transaction_vos import (
    Currency,
    PaymentMethod,
    TransactionStatus,
    RefundStatus,
    PayoutStatus
)


class MoneySchema(BaseModel):
    """Schema for money values."""
    
    amount: Decimal = Field(..., ge=0, description="Monetary amount")
    currency: Currency = Field(default=Currency.INR, description="Currency code")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class TransactionCreateSchema(BaseModel):
    """Schema for creating a new transaction."""
    
    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    order_id: Optional[UUID] = Field(None, description="Associated order ID")
    amount: MoneySchema = Field(..., description="Transaction amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    customer_name: Optional[str] = Field(None, max_length=255, description="Customer name")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer phone")
    customer_email: Optional[str] = Field(None, max_length=255, description="Customer email")
    description: Optional[str] = Field(None, description="Transaction description")
    reference_number: Optional[str] = Field(None, max_length=100, description="Internal reference")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        schema_extra = {
            "example": {
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "order_id": "123e4567-e89b-12d3-a456-426614174001",
                "amount": {
                    "amount": 250.00,
                    "currency": "INR"
                },
                "payment_method": "cash",
                "customer_name": "John Doe",
                "customer_phone": "+91-9876543210",
                "customer_email": "john@example.com",
                "description": "Order payment",
                "reference_number": "REF-001"
            }
        }


class TransactionUpdateSchema(BaseModel):
    """Schema for updating a transaction."""
    
    status: Optional[TransactionStatus] = Field(None, description="Transaction status")
    gateway_transaction_id: Optional[str] = Field(None, description="Gateway transaction ID")
    gateway_order_id: Optional[str] = Field(None, description="Gateway order ID")
    gateway_response: Optional[Dict[str, Any]] = Field(None, description="Gateway response data")
    failure_reason: Optional[str] = Field(None, description="Failure reason")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class TransactionResponseSchema(BaseModel):
    """Schema for transaction response."""
    
    id: UUID = Field(..., description="Transaction identifier")
    transaction_number: str = Field(..., description="Human-readable transaction number")
    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    order_id: Optional[UUID] = Field(None, description="Associated order ID")
    amount: MoneySchema = Field(..., description="Transaction amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    status: TransactionStatus = Field(..., description="Transaction status")
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    customer_email: Optional[str] = Field(None, description="Customer email")
    description: Optional[str] = Field(None, description="Transaction description")
    reference_number: Optional[str] = Field(None, description="Internal reference")
    gateway_transaction_id: Optional[str] = Field(None, description="Gateway transaction ID")
    gateway_order_id: Optional[str] = Field(None, description="Gateway order ID")
    failure_reason: Optional[str] = Field(None, description="Failure reason")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class TransactionHistoryRequestSchema(BaseModel):
    """Schema for transaction history request."""
    
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    status: Optional[TransactionStatus] = Field(None, description="Filter by status")
    payment_method: Optional[PaymentMethod] = Field(None, description="Filter by payment method")
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")
    search_term: Optional[str] = Field(None, max_length=100, description="Search term")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class TransactionHistoryResponseSchema(BaseModel):
    """Schema for transaction history response."""
    
    transactions: List[TransactionResponseSchema] = Field(..., description="List of transactions")
    total_count: int = Field(..., description="Total number of transactions")
    has_more: bool = Field(..., description="Whether there are more results")


class TransactionSummarySchema(BaseModel):
    """Schema for transaction summary."""
    
    total_transactions: int = Field(..., description="Total number of transactions")
    total_amount: Decimal = Field(..., description="Total transaction amount")
    completed_transactions: int = Field(..., description="Number of completed transactions")
    completed_amount: Decimal = Field(..., description="Total completed amount")
    pending_transactions: int = Field(..., description="Number of pending transactions")
    pending_amount: Decimal = Field(..., description="Total pending amount")
    failed_transactions: int = Field(..., description="Number of failed transactions")
    failed_amount: Decimal = Field(..., description="Total failed amount")
    refunded_transactions: int = Field(..., description="Number of refunded transactions")
    refunded_amount: Decimal = Field(..., description="Total refunded amount")
    average_transaction_amount: Decimal = Field(..., description="Average transaction amount")


class PaymentMethodBreakdownSchema(BaseModel):
    """Schema for payment method breakdown."""
    
    payment_method: PaymentMethod = Field(..., description="Payment method")
    transaction_count: int = Field(..., description="Number of transactions")
    total_amount: Decimal = Field(..., description="Total amount for this method")
    percentage: Decimal = Field(..., description="Percentage of total volume")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class DailyRevenueTrendSchema(BaseModel):
    """Schema for daily revenue trend."""
    
    transaction_date: date = Field(..., description="Transaction date")
    transaction_count: int = Field(..., description="Number of transactions")
    total_revenue: Decimal = Field(..., description="Total revenue")
    completed_revenue: Decimal = Field(..., description="Completed revenue")
    refunded_amount: Decimal = Field(..., description="Refunded amount")
    net_revenue: Decimal = Field(..., description="Net revenue")


class RefundCreateSchema(BaseModel):
    """Schema for creating a refund."""
    
    amount: MoneySchema = Field(..., description="Refund amount")
    reason: str = Field(..., min_length=1, max_length=1000, description="Refund reason")
    
    @validator('reason')
    def validate_reason(cls, v):
        """Validate refund reason is not empty."""
        if not v.strip():
            raise ValueError('Refund reason cannot be empty')
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "amount": {
                    "amount": 100.00,
                    "currency": "INR"
                },
                "reason": "Customer requested refund due to order cancellation"
            }
        }


class RefundResponseSchema(BaseModel):
    """Schema for refund response."""
    
    id: UUID = Field(..., description="Refund identifier")
    refund_number: str = Field(..., description="Human-readable refund number")
    transaction_id: UUID = Field(..., description="Transaction identifier")
    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    amount: MoneySchema = Field(..., description="Refund amount")
    reason: str = Field(..., description="Refund reason")
    status: RefundStatus = Field(..., description="Refund status")
    processed_by: UUID = Field(..., description="User who initiated the refund")
    approved_by: Optional[UUID] = Field(None, description="User who approved the refund")
    gateway_refund_id: Optional[str] = Field(None, description="Gateway refund ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class PaymentConfirmationSchema(BaseModel):
    """Schema for payment confirmation (cash payments)."""
    
    amount_received: MoneySchema = Field(..., description="Amount received")
    payment_method: PaymentMethod = Field(..., description="Payment method used")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        schema_extra = {
            "example": {
                "amount_received": {
                    "amount": 250.00,
                    "currency": "INR"
                },
                "payment_method": "cash",
                "notes": "Exact amount received"
            }
        }


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error": "Transaction not found",
                "error_code": "TRANSACTION_NOT_FOUND",
                "details": {
                    "transaction_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
