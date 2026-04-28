"""Process Refund Use Case.

This module implements the use case for processing refunds
with proper validation and business rule enforcement.
"""

import logging
from uuid import uuid4, UUID
from typing import Optional
from decimal import Decimal

from ...domain.transaction_entities import Transaction, Refund
from ...domain.transaction_vos import Money, RefundStatus, TransactionStatus
from ...domain.transaction_repos import ITransactionRepository, IRefundRepository, IAuditLogRepository
from ...domain.transaction_exceptions import (
    TransactionNotFoundError,
    ValidationError,
    InsufficientFundsError,
    InvalidTransactionStatusError,
)
from ..transaction_dtos import RefundCreateDTO, RefundDTO

logger = logging.getLogger(__name__)


class ProcessRefundUseCase:
    """Use case for processing transaction refunds.
    
    This use case handles the creation and processing of refunds with proper
    validation, business rule enforcement, and audit logging.
    """
    
    def __init__(
        self,
        transaction_repository: ITransactionRepository,
        refund_repository: IRefundRepository,
        audit_log_repository: IAuditLogRepository,
    ):
        """Initialize the process refund use case.
        
        Args:
            transaction_repository: Repository for transaction operations
            refund_repository: Repository for refund operations
            audit_log_repository: Repository for audit logging
        """
        self._transaction_repo = transaction_repository
        self._refund_repo = refund_repository
        self._audit_repo = audit_log_repository
    
    async def execute(
        self, 
        request: RefundCreateDTO,
        processed_by: Optional[UUID] = None
    ) -> RefundDTO:
        """Execute the process refund use case.
        
        Args:
            request: Refund creation request data
            processed_by: User processing the refund
            
        Returns:
            Created refund data
            
        Raises:
            TransactionNotFoundError: If transaction is not found
            ValidationError: If request data is invalid
            InsufficientFundsError: If refund amount exceeds available amount
            InvalidTransactionStatusError: If transaction status doesn't allow refunds
        """
        try:
            logger.info(
                "Processing refund for transaction %s",
                request.transaction_id,
                extra={
                    "transaction_id": str(request.transaction_id),
                    "refund_amount": float(request.amount.amount),
                    "reason": request.reason,
                    "processed_by": str(processed_by) if processed_by else None,
                }
            )
            
            # Get the original transaction
            transaction = await self._transaction_repo.get_transaction_by_id(request.transaction_id)
            if not transaction:
                raise TransactionNotFoundError(request.transaction_id)
            
            # Validate transaction status allows refunds
            if transaction.status not in [TransactionStatus.COMPLETED, TransactionStatus.PARTIALLY_REFUNDED]:
                raise InvalidTransactionStatusError(
                    transaction.status.value,
                    "refunded",
                    transaction.id
                )
            
            # Validate request data
            self._validate_request(request, transaction)
            
            # Check if refund amount is valid
            await self._validate_refund_amount(request.transaction_id, request.amount.amount)
            
            # Create money value object
            refund_amount = Money(request.amount.amount, request.amount.currency)
            
            # Create refund entity
            refund = Refund(
                id=uuid4(),
                transaction_id=request.transaction_id,
                restaurant_id=transaction.restaurant_id,
                amount=refund_amount,
                reason=request.reason,
                status=RefundStatus.PENDING,
                processed_by=processed_by,
            )
            
            # Save refund to repository
            created_refund = await self._refund_repo.create_refund(refund)
            
            # Update transaction status if needed
            await self._update_transaction_status_for_refund(transaction, refund_amount.amount)
            
            # Create audit log entry
            await self._audit_repo.create_audit_log(
                entity_id=created_refund.id,
                entity_type="refund",
                action="CREATE",
                new_status=created_refund.status.value,
                changes={
                    "amount": float(created_refund.amount.amount),
                    "currency": created_refund.amount.currency.value,
                    "reason": created_refund.reason,
                    "transaction_id": str(created_refund.transaction_id),
                },
                reason="Refund created",
                performed_by=processed_by
            )
            
            logger.info(
                "Refund created successfully",
                extra={
                    "refund_id": str(created_refund.id),
                    "refund_number": created_refund.refund_number.value,
                    "transaction_id": str(created_refund.transaction_id),
                }
            )
            
            # Convert to DTO and return
            return self._map_to_dto(created_refund)
            
        except (TransactionNotFoundError, ValidationError, InsufficientFundsError, InvalidTransactionStatusError):
            raise
        except Exception as e:
            logger.error(
                "Failed to process refund",
                extra={
                    "transaction_id": str(request.transaction_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise ValidationError(f"Failed to process refund: {str(e)}")
    
    def _validate_request(self, request: RefundCreateDTO, transaction: Transaction) -> None:
        """Validate refund request data.
        
        Args:
            request: Refund request data
            transaction: Original transaction
            
        Raises:
            ValidationError: If validation fails
        """
        if request.amount.amount <= 0:
            raise ValidationError("Refund amount must be greater than zero")
        
        if request.amount.amount > transaction.amount.amount:
            raise ValidationError("Refund amount cannot exceed transaction amount")
        
        if not request.reason or len(request.reason.strip()) == 0:
            raise ValidationError("Refund reason is required")
        
        if request.amount.currency != transaction.amount.currency:
            raise ValidationError("Refund currency must match transaction currency")
    
    async def _validate_refund_amount(self, transaction_id: UUID, refund_amount: Decimal) -> None:
        """Validate that refund amount doesn't exceed available refundable amount.
        
        Args:
            transaction_id: Transaction identifier
            refund_amount: Requested refund amount
            
        Raises:
            InsufficientFundsError: If refund amount exceeds available amount
        """
        # Get existing refunds for this transaction
        existing_refunds = await self._refund_repo.get_refunds_by_transaction(transaction_id)
        
        # Calculate total refunded amount
        total_refunded = sum(
            refund.amount.amount 
            for refund in existing_refunds 
            if refund.status in [RefundStatus.COMPLETED, RefundStatus.PROCESSING]
        )
        
        # Get original transaction amount
        transaction = await self._transaction_repo.get_transaction_by_id(transaction_id)
        available_amount = transaction.amount.amount - total_refunded
        
        if refund_amount > available_amount:
            raise InsufficientFundsError(
                float(available_amount),
                float(refund_amount),
                transaction_id
            )
    
    async def _update_transaction_status_for_refund(
        self, 
        transaction: Transaction, 
        refund_amount: Decimal
    ) -> None:
        """Update transaction status based on refund amount.
        
        Args:
            transaction: Original transaction
            refund_amount: Refund amount
        """
        # Get existing refunds
        existing_refunds = await self._refund_repo.get_refunds_by_transaction(transaction.id)
        
        # Calculate total refunded amount (including this refund)
        total_refunded = refund_amount + sum(
            refund.amount.amount 
            for refund in existing_refunds 
            if refund.status in [RefundStatus.COMPLETED, RefundStatus.PROCESSING]
        )
        
        # Update transaction status
        if total_refunded >= transaction.amount.amount:
            transaction.mark_as_refunded()
        else:
            transaction.mark_as_partially_refunded()
        
        # Save updated transaction
        await self._transaction_repo.update_transaction(transaction)
    
    def _map_to_dto(self, refund: Refund) -> RefundDTO:
        """Map refund entity to DTO.
        
        Args:
            refund: Refund entity
            
        Returns:
            Refund DTO
        """
        from ..transaction_dtos import MoneyDTO
        
        return RefundDTO(
            id=refund.id,
            refund_number=refund.refund_number.value,
            transaction_id=refund.transaction_id,
            restaurant_id=refund.restaurant_id,
            amount=MoneyDTO(
                amount=refund.amount.amount,
                currency=refund.amount.currency
            ),
            reason=refund.reason,
            status=refund.status,
            gateway_refund_id=refund.gateway_refund_id,
            processed_by=refund.processed_by,
            approved_by=refund.approved_by,
            created_at=refund.created_at,
            updated_at=refund.updated_at,
            processed_at=refund.processed_at
        )
