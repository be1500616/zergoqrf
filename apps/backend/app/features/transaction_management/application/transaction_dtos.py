"""Transaction Management Data Transfer Objects.

This module defines DTOs for transferring data between application layers
while maintaining clean architecture boundaries.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ..domain.transaction_vos import (
    Currency,
    PaymentMethod,
    PayoutStatus,
    RefundStatus,
    TransactionStatus,
)


class MoneyDTO(BaseModel):
    """Data transfer object for money values."""

    amount: Decimal = Field(..., ge=0, description="Monetary amount")
    currency: Currency = Field(default=Currency.INR, description="Currency code")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class TransactionCreateDTO(BaseModel):
    """DTO for creating a new transaction."""

    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    order_id: Optional[UUID] = Field(None, description="Associated order ID")
    amount: MoneyDTO = Field(..., description="Transaction amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    customer_name: Optional[str] = Field(
        None, max_length=255, description="Customer name"
    )
    customer_phone: Optional[str] = Field(
        None, max_length=20, description="Customer phone"
    )
    customer_email: Optional[str] = Field(
        None, max_length=255, description="Customer email"
    )
    description: Optional[str] = Field(None, description="Transaction description")
    reference_number: Optional[str] = Field(
        None, max_length=100, description="Internal reference"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class TransactionUpdateDTO(BaseModel):
    """DTO for updating a transaction."""

    status: Optional[TransactionStatus] = Field(None, description="Transaction status")
    gateway_transaction_id: Optional[str] = Field(
        None, description="Gateway transaction ID"
    )
    gateway_order_id: Optional[str] = Field(None, description="Gateway order ID")
    gateway_response: Optional[Dict[str, Any]] = Field(
        None, description="Gateway response data"
    )
    failure_reason: Optional[str] = Field(None, description="Failure reason")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class TransactionDTO(BaseModel):
    """DTO for transaction data."""

    id: UUID = Field(..., description="Transaction identifier")
    transaction_number: str = Field(
        ..., description="Human-readable transaction number"
    )
    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    order_id: Optional[UUID] = Field(None, description="Associated order ID")
    amount: MoneyDTO = Field(..., description="Transaction amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    status: TransactionStatus = Field(..., description="Transaction status")
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    customer_email: Optional[str] = Field(None, description="Customer email")
    description: Optional[str] = Field(None, description="Transaction description")
    reference_number: Optional[str] = Field(None, description="Internal reference")
    gateway_transaction_id: Optional[str] = Field(
        None, description="Gateway transaction ID"
    )
    gateway_order_id: Optional[str] = Field(None, description="Gateway order ID")
    failure_reason: Optional[str] = Field(None, description="Failure reason")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class RefundCreateDTO(BaseModel):
    """DTO for creating a new refund."""

    transaction_id: UUID = Field(..., description="Transaction identifier")
    amount: MoneyDTO = Field(..., description="Refund amount")
    reason: str = Field(..., min_length=1, max_length=1000, description="Refund reason")
    processed_by: UUID = Field(..., description="User initiating the refund")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("reason")
    def validate_reason(cls, v):
        """Validate refund reason is not empty."""
        if not v.strip():
            raise ValueError("Refund reason cannot be empty")
        return v.strip()


class RefundUpdateDTO(BaseModel):
    """DTO for updating a refund."""

    status: Optional[RefundStatus] = Field(None, description="Refund status")
    gateway_refund_id: Optional[str] = Field(None, description="Gateway refund ID")
    gateway_response: Optional[Dict[str, Any]] = Field(
        None, description="Gateway response data"
    )
    approved_by: Optional[UUID] = Field(
        None, description="User who approved the refund"
    )
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class RefundDTO(BaseModel):
    """DTO for refund data."""

    id: UUID = Field(..., description="Refund identifier")
    refund_number: str = Field(..., description="Human-readable refund number")
    transaction_id: UUID = Field(..., description="Transaction identifier")
    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    amount: MoneyDTO = Field(..., description="Refund amount")
    reason: str = Field(..., description="Refund reason")
    status: RefundStatus = Field(..., description="Refund status")
    processed_by: UUID = Field(..., description="User who initiated the refund")
    approved_by: Optional[UUID] = Field(
        None, description="User who approved the refund"
    )
    gateway_refund_id: Optional[str] = Field(None, description="Gateway refund ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class PayoutCreateDTO(BaseModel):
    """DTO for creating a new payout."""

    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    gross_amount: MoneyDTO = Field(..., description="Gross payout amount")
    platform_fee: MoneyDTO = Field(..., description="Platform fee amount")
    tax_amount: MoneyDTO = Field(..., description="Tax amount")
    net_amount: MoneyDTO = Field(..., description="Net payout amount")
    scheduled_date: date = Field(..., description="Scheduled payout date")
    period_start_date: date = Field(..., description="Period start date")
    period_end_date: date = Field(..., description="Period end date")
    bank_account_last4: Optional[str] = Field(
        None, max_length=4, description="Last 4 digits of bank account"
    )
    bank_name: Optional[str] = Field(None, max_length=100, description="Bank name")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class PayoutDTO(BaseModel):
    """DTO for payout data."""

    id: UUID = Field(..., description="Payout identifier")
    payout_number: str = Field(..., description="Human-readable payout number")
    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    gross_amount: MoneyDTO = Field(..., description="Gross payout amount")
    platform_fee: MoneyDTO = Field(..., description="Platform fee amount")
    tax_amount: MoneyDTO = Field(..., description="Tax amount")
    net_amount: MoneyDTO = Field(..., description="Net payout amount")
    status: PayoutStatus = Field(..., description="Payout status")
    scheduled_date: date = Field(..., description="Scheduled payout date")
    period_start_date: date = Field(..., description="Period start date")
    period_end_date: date = Field(..., description="Period end date")
    bank_account_last4: Optional[str] = Field(
        None, description="Last 4 digits of bank account"
    )
    bank_name: Optional[str] = Field(None, description="Bank name")
    gateway_payout_id: Optional[str] = Field(None, description="Gateway payout ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class TransactionSummaryDTO(BaseModel):
    """DTO for transaction summary data."""

    total_transactions: int = Field(..., description="Total number of transactions")
    total_amount: Decimal = Field(..., description="Total transaction amount")
    completed_transactions: int = Field(
        ..., description="Number of completed transactions"
    )
    completed_amount: Decimal = Field(..., description="Total completed amount")
    pending_transactions: int = Field(..., description="Number of pending transactions")
    pending_amount: Decimal = Field(..., description="Total pending amount")
    failed_transactions: int = Field(..., description="Number of failed transactions")
    failed_amount: Decimal = Field(..., description="Total failed amount")
    refunded_transactions: int = Field(
        ..., description="Number of refunded transactions"
    )
    refunded_amount: Decimal = Field(..., description="Total refunded amount")
    average_transaction_amount: Decimal = Field(
        ..., description="Average transaction amount"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class PaymentProcessingDTO(BaseModel):
    """DTO for payment processing data."""

    payment_method: Optional[PaymentMethod] = Field(None, description="Payment method")
    gateway_data: Optional[Dict[str, Any]] = Field(
        None, description="Gateway-specific data"
    )
    notes: Optional[str] = Field(None, description="Processing notes")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class RefundSummaryDTO(BaseModel):
    """DTO for refund summary data."""

    total_refunds: int = Field(..., description="Total number of refunds")
    total_refunded_amount: Decimal = Field(..., description="Total refunded amount")
    completed_refunds: int = Field(..., description="Number of completed refunds")
    completed_refunded_amount: Decimal = Field(
        ..., description="Total completed refund amount"
    )
    pending_refunds: int = Field(..., description="Number of pending refunds")
    pending_refunded_amount: Decimal = Field(
        ..., description="Total pending refund amount"
    )
    average_refund_amount: Decimal = Field(..., description="Average refund amount")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class PayoutSummaryDTO(BaseModel):
    """DTO for payout summary data."""

    total_payouts: int = Field(..., description="Total number of payouts")
    total_payout_amount: Decimal = Field(..., description="Total payout amount")
    completed_payouts: int = Field(..., description="Number of completed payouts")
    completed_payout_amount: Decimal = Field(
        ..., description="Total completed payout amount"
    )
    pending_payouts: int = Field(..., description="Number of pending payouts")
    pending_payout_amount: Decimal = Field(
        ..., description="Total pending payout amount"
    )
    total_fees: Decimal = Field(..., description="Total fees deducted")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class FinancialReportDTO(BaseModel):
    """DTO for comprehensive financial reports."""

    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    report_period_start: date = Field(..., description="Report period start date")
    report_period_end: date = Field(..., description="Report period end date")
    report_type: str = Field(..., description="Type of report")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    transaction_summary: TransactionSummaryDTO = Field(
        ..., description="Transaction summary"
    )
    refund_summary: RefundSummaryDTO = Field(..., description="Refund summary")
    payout_summary: PayoutSummaryDTO = Field(..., description="Payout summary")
    payment_method_breakdown: Optional[List["PaymentMethodBreakdownDTO"]] = Field(
        None, description="Payment method breakdown"
    )
    revenue_trends: Optional[List["DailyRevenueTrendDTO"]] = Field(
        None, description="Daily revenue trends"
    )
    key_metrics: Dict[str, float] = Field(..., description="Key financial metrics")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class PaymentMethodBreakdownDTO(BaseModel):
    """DTO for payment method breakdown data."""

    payment_method: PaymentMethod = Field(..., description="Payment method")
    transaction_count: int = Field(..., description="Number of transactions")
    total_amount: Decimal = Field(..., description="Total amount for this method")
    percentage: Decimal = Field(..., description="Percentage of total volume")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class DailyRevenueTrendDTO(BaseModel):
    """DTO for daily revenue trend data."""

    transaction_date: date = Field(..., description="Transaction date")
    transaction_count: int = Field(..., description="Number of transactions")
    total_revenue: Decimal = Field(..., description="Total revenue")
    completed_revenue: Decimal = Field(..., description="Completed revenue")
    refunded_amount: Decimal = Field(..., description="Refunded amount")
    net_revenue: Decimal = Field(..., description="Net revenue")


class TransactionHistoryRequestDTO(BaseModel):
    """DTO for transaction history request parameters."""

    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    limit: int = Field(
        default=50, ge=1, le=100, description="Maximum number of results"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    status: Optional[TransactionStatus] = Field(None, description="Filter by status")
    payment_method: Optional[PaymentMethod] = Field(
        None, description="Filter by payment method"
    )
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")
    search_term: Optional[str] = Field(None, max_length=100, description="Search term")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class TransactionHistoryResponseDTO(BaseModel):
    """DTO for transaction history response."""

    transactions: List[TransactionDTO] = Field(..., description="List of transactions")
    total_count: int = Field(..., description="Total number of transactions")
    has_more: bool = Field(..., description="Whether there are more results")


class FinancialReportRequestDTO(BaseModel):
    """DTO for financial report request parameters."""

    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    start_date: date = Field(..., description="Report start date")
    end_date: date = Field(..., description="Report end date")
    report_type: str = Field(..., description="Type of report")
    format: str = Field(default="json", description="Report format (json, csv, pdf)")
    include_details: bool = Field(
        default=False, description="Include detailed transactions"
    )

    @validator("end_date")
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date."""
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class FinancialReportDTO(BaseModel):
    """DTO for financial report data."""

    restaurant_id: UUID = Field(..., description="Restaurant identifier")
    report_type: str = Field(..., description="Type of report")
    period_start: date = Field(..., description="Report period start")
    period_end: date = Field(..., description="Report period end")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    summary: TransactionSummaryDTO = Field(..., description="Transaction summary")
    payment_method_breakdown: List["PaymentMethodBreakdownDTO"] = Field(
        ..., description="Payment method breakdown"
    )
    daily_trends: List["DailyRevenueTrendDTO"] = Field(
        ..., description="Daily revenue trends"
    )
    transactions: Optional[List[TransactionDTO]] = Field(
        None, description="Detailed transactions"
    )
    refunds: Optional[List[RefundDTO]] = Field(None, description="Refund details")
    payouts: Optional[List[PayoutDTO]] = Field(None, description="Payout details")
