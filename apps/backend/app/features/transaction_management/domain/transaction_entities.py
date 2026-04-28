"""Transaction Management Domain Entities.

This module defines the core business entities for transaction management
including Transaction, Refund, and Payout entities with their business logic.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from .transaction_vos import (
    Money,
    TransactionNumber,
    PaymentMethod,
    TransactionStatus,
    RefundStatus,
    PayoutStatus,
)


class Transaction:
    """Core transaction entity representing a financial transaction.
    
    This entity encapsulates all transaction-related business logic including
    status transitions, validation, and audit trail management.
    """
    
    def __init__(
        self,
        id: UUID,
        restaurant_id: UUID,
        amount: Money,
        payment_method: PaymentMethod,
        transaction_number: Optional[TransactionNumber] = None,
        order_id: Optional[UUID] = None,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_email: Optional[str] = None,
        description: Optional[str] = None,
        reference_number: Optional[str] = None,
        gateway_transaction_id: Optional[str] = None,
        gateway_order_id: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None,
        status: TransactionStatus = TransactionStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None,
        failure_reason: Optional[str] = None,
    ):
        """Initialize a transaction entity.
        
        Args:
            id: Unique transaction identifier
            restaurant_id: Restaurant this transaction belongs to
            amount: Transaction amount with currency
            payment_method: Method used for payment
            transaction_number: Human-readable transaction number
            order_id: Associated order ID (optional)
            customer_name: Customer name (optional)
            customer_phone: Customer phone (optional)
            customer_email: Customer email (optional)
            description: Transaction description
            reference_number: Internal reference number
            gateway_transaction_id: External gateway transaction ID
            gateway_order_id: External gateway order ID
            gateway_response: Gateway response data
            status: Current transaction status
            created_at: Creation timestamp
            updated_at: Last update timestamp
            processed_at: Processing completion timestamp
            failure_reason: Reason for failure (if applicable)
        """
        self.id = id
        self.restaurant_id = restaurant_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_number = transaction_number or TransactionNumber.generate()
        self.order_id = order_id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.customer_email = customer_email
        self.description = description
        self.reference_number = reference_number
        self.gateway_transaction_id = gateway_transaction_id
        self.gateway_order_id = gateway_order_id
        self.gateway_response = gateway_response or {}
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.processed_at = processed_at
        self.failure_reason = failure_reason
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate transaction business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if self.amount.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        if not self.restaurant_id:
            raise ValueError("Restaurant ID is required")
        
        if self.status == TransactionStatus.FAILED and not self.failure_reason:
            raise ValueError("Failure reason is required for failed transactions")
    
    def mark_as_processing(self, gateway_transaction_id: Optional[str] = None) -> None:
        """Mark transaction as processing.
        
        Args:
            gateway_transaction_id: External gateway transaction ID
            
        Raises:
            ValueError: If status transition is invalid
        """
        if self.status != TransactionStatus.PENDING:
            raise ValueError(f"Cannot mark transaction as processing from status: {self.status}")
        
        self.status = TransactionStatus.PROCESSING
        self.gateway_transaction_id = gateway_transaction_id
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(
        self, 
        gateway_transaction_id: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark transaction as completed.
        
        Args:
            gateway_transaction_id: External gateway transaction ID
            gateway_response: Gateway response data
            
        Raises:
            ValueError: If status transition is invalid
        """
        if self.status not in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]:
            raise ValueError(f"Cannot complete transaction from status: {self.status}")
        
        self.status = TransactionStatus.COMPLETED
        self.gateway_transaction_id = gateway_transaction_id or self.gateway_transaction_id
        self.gateway_response.update(gateway_response or {})
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(
        self, 
        failure_reason: str,
        gateway_response: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark transaction as failed.
        
        Args:
            failure_reason: Reason for failure
            gateway_response: Gateway response data
            
        Raises:
            ValueError: If status transition is invalid
        """
        if self.status == TransactionStatus.COMPLETED:
            raise ValueError("Cannot mark completed transaction as failed")
        
        self.status = TransactionStatus.FAILED
        self.failure_reason = failure_reason
        self.gateway_response.update(gateway_response or {})
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def can_be_refunded(self) -> bool:
        """Check if transaction can be refunded.
        
        Returns:
            True if transaction can be refunded
        """
        return self.status == TransactionStatus.COMPLETED
    
    def initiate_refund(
        self,
        refund_amount: Money,
        reason: str,
        processed_by: UUID
    ) -> 'Refund':
        """Initiate a refund for this transaction.
        
        Args:
            refund_amount: Amount to refund
            reason: Reason for refund
            processed_by: User initiating the refund
            
        Returns:
            Refund entity
            
        Raises:
            ValueError: If refund cannot be initiated
        """
        if not self.can_be_refunded():
            raise ValueError(f"Cannot refund transaction with status: {self.status}")
        
        if refund_amount.amount > self.amount.amount:
            raise ValueError("Refund amount cannot exceed transaction amount")
        
        if refund_amount.currency != self.amount.currency:
            raise ValueError("Refund currency must match transaction currency")
        
        return Refund(
            id=uuid4(),
            transaction_id=self.id,
            restaurant_id=self.restaurant_id,
            amount=refund_amount,
            reason=reason,
            processed_by=processed_by,
        )


class Refund:
    """Refund entity representing a transaction refund.
    
    This entity manages the refund lifecycle and business rules.
    """
    
    def __init__(
        self,
        id: UUID,
        transaction_id: UUID,
        restaurant_id: UUID,
        amount: Money,
        reason: str,
        processed_by: UUID,
        refund_number: Optional[str] = None,
        gateway_refund_id: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None,
        approved_by: Optional[UUID] = None,
        status: RefundStatus = RefundStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None,
    ):
        """Initialize a refund entity.
        
        Args:
            id: Unique refund identifier
            transaction_id: Associated transaction ID
            restaurant_id: Restaurant ID
            amount: Refund amount
            reason: Reason for refund
            processed_by: User who initiated the refund
            refund_number: Human-readable refund number
            gateway_refund_id: External gateway refund ID
            gateway_response: Gateway response data
            approved_by: User who approved the refund
            status: Current refund status
            created_at: Creation timestamp
            updated_at: Last update timestamp
            processed_at: Processing completion timestamp
        """
        self.id = id
        self.transaction_id = transaction_id
        self.restaurant_id = restaurant_id
        self.amount = amount
        self.reason = reason
        self.processed_by = processed_by
        self.refund_number = refund_number
        self.gateway_refund_id = gateway_refund_id
        self.gateway_response = gateway_response or {}
        self.approved_by = approved_by
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.processed_at = processed_at
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate refund business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if self.amount.amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        if not self.reason.strip():
            raise ValueError("Refund reason is required")
    
    def approve(self, approved_by: UUID) -> None:
        """Approve the refund.
        
        Args:
            approved_by: User approving the refund
            
        Raises:
            ValueError: If refund cannot be approved
        """
        if self.status != RefundStatus.PENDING:
            raise ValueError(f"Cannot approve refund with status: {self.status}")
        
        self.approved_by = approved_by
        self.status = RefundStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(
        self,
        gateway_refund_id: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark refund as completed.
        
        Args:
            gateway_refund_id: External gateway refund ID
            gateway_response: Gateway response data
        """
        self.status = RefundStatus.COMPLETED
        self.gateway_refund_id = gateway_refund_id or self.gateway_refund_id
        self.gateway_response.update(gateway_response or {})
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(
        self,
        gateway_response: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark refund as failed.
        
        Args:
            gateway_response: Gateway response data
        """
        self.status = RefundStatus.FAILED
        self.gateway_response.update(gateway_response or {})
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class Payout:
    """Payout entity representing restaurant settlement.
    
    This entity manages restaurant payout lifecycle and calculations.
    """
    
    def __init__(
        self,
        id: UUID,
        restaurant_id: UUID,
        gross_amount: Money,
        platform_fee: Money,
        tax_amount: Money,
        net_amount: Money,
        scheduled_date: datetime,
        period_start_date: datetime,
        period_end_date: datetime,
        payout_number: Optional[str] = None,
        gateway_payout_id: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None,
        bank_account_last4: Optional[str] = None,
        bank_name: Optional[str] = None,
        status: PayoutStatus = PayoutStatus.SCHEDULED,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ):
        """Initialize a payout entity.
        
        Args:
            id: Unique payout identifier
            restaurant_id: Restaurant ID
            gross_amount: Gross payout amount
            platform_fee: Platform fee amount
            tax_amount: Tax amount
            net_amount: Net payout amount
            scheduled_date: Scheduled payout date
            period_start_date: Period start date
            period_end_date: Period end date
            payout_number: Human-readable payout number
            gateway_payout_id: External gateway payout ID
            gateway_response: Gateway response data
            bank_account_last4: Last 4 digits of bank account
            bank_name: Bank name
            status: Current payout status
            created_at: Creation timestamp
            updated_at: Last update timestamp
            completed_at: Completion timestamp
        """
        self.id = id
        self.restaurant_id = restaurant_id
        self.gross_amount = gross_amount
        self.platform_fee = platform_fee
        self.tax_amount = tax_amount
        self.net_amount = net_amount
        self.scheduled_date = scheduled_date
        self.period_start_date = period_start_date
        self.period_end_date = period_end_date
        self.payout_number = payout_number
        self.gateway_payout_id = gateway_payout_id
        self.gateway_response = gateway_response or {}
        self.bank_account_last4 = bank_account_last4
        self.bank_name = bank_name
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.completed_at = completed_at
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate payout business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if self.gross_amount.amount <= 0:
            raise ValueError("Gross amount must be positive")
        
        if self.net_amount.amount <= 0:
            raise ValueError("Net amount must be positive")
        
        expected_net = self.gross_amount.amount - self.platform_fee.amount - self.tax_amount.amount
        if abs(self.net_amount.amount - expected_net) > Decimal('0.01'):
            raise ValueError("Net amount calculation is incorrect")
    
    def mark_as_processing(self, gateway_payout_id: Optional[str] = None) -> None:
        """Mark payout as processing.
        
        Args:
            gateway_payout_id: External gateway payout ID
        """
        if self.status != PayoutStatus.SCHEDULED:
            raise ValueError(f"Cannot process payout with status: {self.status}")
        
        self.status = PayoutStatus.PROCESSING
        self.gateway_payout_id = gateway_payout_id or self.gateway_payout_id
        self.updated_at = datetime.utcnow()
    
    def mark_as_completed(
        self,
        gateway_response: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark payout as completed.
        
        Args:
            gateway_response: Gateway response data
        """
        self.status = PayoutStatus.COMPLETED
        self.gateway_response.update(gateway_response or {})
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(
        self,
        gateway_response: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark payout as failed.
        
        Args:
            gateway_response: Gateway response data
        """
        self.status = PayoutStatus.FAILED
        self.gateway_response.update(gateway_response or {})
        self.updated_at = datetime.utcnow()
