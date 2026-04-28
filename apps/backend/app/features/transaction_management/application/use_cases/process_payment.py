"""Process Payment Use Case.

This module implements the use case for processing payments
with proper validation and business rule enforcement.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from ...domain.payment_gateway_interfaces import (
    IPaymentGateway,
    PaymentRequest,
    PaymentResponse,
)
from ...domain.transaction_entities import Transaction
from ...domain.transaction_exceptions import (
    InvalidTransactionStatusError,
    PaymentProcessingError,
    TransactionNotFoundError,
    ValidationError,
)
from ...domain.transaction_repos import IAuditLogRepository, ITransactionRepository
from ...domain.transaction_vos import PaymentMethod, TransactionStatus
from ..transaction_dtos import PaymentProcessingDTO, TransactionDTO

logger = logging.getLogger(__name__)


class ProcessPaymentUseCase:
    """Use case for processing payments.

    This use case handles payment processing through various payment gateways
    with proper validation, business rule enforcement, and audit logging.
    """

    def __init__(
        self,
        transaction_repository: ITransactionRepository,
        audit_log_repository: IAuditLogRepository,
        payment_gateway: Optional[IPaymentGateway] = None,
    ):
        """Initialize the process payment use case.

        Args:
            transaction_repository: Repository for transaction operations
            audit_log_repository: Repository for audit logging
            payment_gateway: Payment gateway for processing payments
        """
        self._transaction_repo = transaction_repository
        self._audit_repo = audit_log_repository
        self._payment_gateway = payment_gateway

    async def execute(
        self,
        transaction_id: UUID,
        payment_data: PaymentProcessingDTO,
        processed_by: Optional[UUID] = None,
    ) -> TransactionDTO:
        """Execute the process payment use case.

        Args:
            transaction_id: Transaction identifier
            payment_data: Payment processing data
            processed_by: User processing the payment

        Returns:
            Updated transaction data

        Raises:
            TransactionNotFoundError: If transaction is not found
            ValidationError: If request data is invalid
            InvalidTransactionStatusError: If transaction status doesn't allow payment
            PaymentProcessingError: If payment processing fails
        """
        try:
            logger.info(
                "Processing payment for transaction %s",
                transaction_id,
                extra={
                    "transaction_id": str(transaction_id),
                    "payment_method": (
                        payment_data.payment_method.value
                        if payment_data.payment_method
                        else None
                    ),
                    "processed_by": str(processed_by) if processed_by else None,
                },
            )

            # Get the transaction
            transaction = await self._transaction_repo.get_transaction_by_id(
                transaction_id
            )
            if not transaction:
                raise TransactionNotFoundError(transaction_id)

            # Validate transaction status allows payment processing
            if transaction.status not in [
                TransactionStatus.PENDING,
                TransactionStatus.PROCESSING,
            ]:
                raise InvalidTransactionStatusError(
                    transaction.status.value, "processing", transaction.id
                )

            # Validate payment data
            self._validate_payment_data(payment_data, transaction)

            # Process payment based on method
            if transaction.payment_method == PaymentMethod.CASH:
                # Handle cash payment confirmation
                updated_transaction = await self._process_cash_payment(
                    transaction, payment_data, processed_by
                )
            else:
                # Handle digital payment processing
                updated_transaction = await self._process_digital_payment(
                    transaction, payment_data, processed_by
                )

            logger.info(
                "Payment processed successfully",
                extra={
                    "transaction_id": str(updated_transaction.id),
                    "transaction_number": updated_transaction.transaction_number.value,
                    "status": updated_transaction.status.value,
                },
            )

            # Convert to DTO and return
            return self._map_to_dto(updated_transaction)

        except (
            TransactionNotFoundError,
            ValidationError,
            InvalidTransactionStatusError,
            PaymentProcessingError,
        ):
            raise
        except Exception as e:
            logger.error(
                "Failed to process payment",
                extra={
                    "transaction_id": str(transaction_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise PaymentProcessingError(f"Failed to process payment: {str(e)}")

    async def _process_cash_payment(
        self,
        transaction: Transaction,
        payment_data: PaymentProcessingDTO,
        processed_by: Optional[UUID],
    ) -> Transaction:
        """Process cash payment confirmation.

        Args:
            transaction: Transaction entity
            payment_data: Payment processing data
            processed_by: User processing the payment

        Returns:
            Updated transaction
        """
        # Mark transaction as completed for cash payments
        transaction.mark_as_completed()

        # Update transaction in repository
        updated_transaction = await self._transaction_repo.update_transaction(
            transaction
        )

        # Create audit log entry
        await self._audit_repo.create_audit_log(
            entity_id=transaction.id,
            entity_type="transaction",
            action="CONFIRM_CASH_PAYMENT",
            previous_status="pending",
            new_status="completed",
            changes={
                "payment_method": "cash",
                "confirmed_by": str(processed_by) if processed_by else None,
                "notes": payment_data.notes,
            },
            reason="Cash payment confirmed by restaurant staff",
            performed_by=processed_by,
        )

        return updated_transaction

    async def _process_digital_payment(
        self,
        transaction: Transaction,
        payment_data: PaymentProcessingDTO,
        processed_by: Optional[UUID],
    ) -> Transaction:
        """Process digital payment through payment gateway.

        Args:
            transaction: Transaction entity
            payment_data: Payment processing data
            processed_by: User processing the payment

        Returns:
            Updated transaction
        """
        if not self._payment_gateway:
            raise PaymentProcessingError(
                "Payment gateway not configured for digital payments"
            )

        try:
            # Mark transaction as processing
            transaction.mark_as_processing()
            await self._transaction_repo.update_transaction(transaction)

            # Create payment request
            payment_request = PaymentRequest(
                amount=transaction.amount,
                payment_method=transaction.payment_method,
                customer_name=transaction.customer_name,
                customer_email=transaction.customer_email,
                customer_phone=transaction.customer_phone,
                description=transaction.description,
                order_id=str(transaction.order_id) if transaction.order_id else None,
                metadata={
                    "transaction_id": str(transaction.id),
                    "restaurant_id": str(transaction.restaurant_id),
                    "reference_number": transaction.reference_number,
                },
            )

            # Process payment through gateway
            payment_response = await self._payment_gateway.create_payment_intent(
                payment_request
            )

            # Update transaction with gateway response
            if payment_response.success and payment_response.status:
                if payment_response.status == TransactionStatus.COMPLETED:
                    transaction.mark_as_completed(
                        gateway_transaction_id=payment_response.gateway_transaction_id,
                        gateway_response=payment_response.gateway_response,
                    )
                elif payment_response.status == TransactionStatus.FAILED:
                    transaction.mark_as_failed(
                        failure_reason=payment_response.error_message
                        or "Payment failed",
                        gateway_response=payment_response.gateway_response,
                    )
                else:
                    # Payment is still processing
                    transaction.gateway_transaction_id = (
                        payment_response.gateway_transaction_id
                    )
                    transaction.gateway_response = payment_response.gateway_response
            else:
                # Payment failed
                transaction.mark_as_failed(
                    failure_reason=payment_response.error_message
                    or "Payment processing failed",
                    gateway_response=payment_response.gateway_response,
                )

            # Update transaction in repository
            updated_transaction = await self._transaction_repo.update_transaction(
                transaction
            )

            # Create audit log entry
            await self._audit_repo.create_audit_log(
                entity_id=transaction.id,
                entity_type="transaction",
                action="PROCESS_DIGITAL_PAYMENT",
                previous_status="processing",
                new_status=updated_transaction.status.value,
                changes={
                    "gateway_transaction_id": payment_response.gateway_transaction_id,
                    "gateway_status": payment_response.status,
                    "payment_method": transaction.payment_method.value,
                },
                reason="Digital payment processed through gateway",
                performed_by=processed_by,
            )

            return updated_transaction

        except Exception as e:
            # Mark transaction as failed
            transaction.mark_as_failed(
                failure_reason=f"Payment processing failed: {str(e)}"
            )
            await self._transaction_repo.update_transaction(transaction)

            # Create audit log entry for failure
            await self._audit_repo.create_audit_log(
                entity_id=transaction.id,
                entity_type="transaction",
                action="PAYMENT_FAILED",
                previous_status="processing",
                new_status="failed",
                changes={
                    "failure_reason": str(e),
                    "payment_method": transaction.payment_method.value,
                },
                reason="Payment processing failed",
                performed_by=processed_by,
            )

            raise PaymentProcessingError(f"Payment processing failed: {str(e)}")

    def _validate_payment_data(
        self, payment_data: PaymentProcessingDTO, transaction: Transaction
    ) -> None:
        """Validate payment processing data.

        Args:
            payment_data: Payment processing data
            transaction: Transaction entity

        Raises:
            ValidationError: If validation fails
        """
        if (
            payment_data.payment_method
            and payment_data.payment_method != transaction.payment_method
        ):
            raise ValidationError("Payment method mismatch")

        if (
            transaction.payment_method != PaymentMethod.CASH
            and not self._payment_gateway
        ):
            raise ValidationError("Payment gateway required for non-cash payments")

    def _map_to_dto(self, transaction: Transaction) -> TransactionDTO:
        """Map transaction entity to DTO.

        Args:
            transaction: Transaction entity

        Returns:
            Transaction DTO
        """
        from ..transaction_dtos import MoneyDTO

        return TransactionDTO(
            id=transaction.id,
            transaction_number=transaction.transaction_number.value,
            restaurant_id=transaction.restaurant_id,
            order_id=transaction.order_id,
            amount=MoneyDTO(
                amount=transaction.amount.amount, currency=transaction.amount.currency
            ),
            payment_method=transaction.payment_method,
            status=transaction.status,
            customer_name=transaction.customer_name,
            customer_phone=transaction.customer_phone,
            customer_email=transaction.customer_email,
            description=transaction.description,
            reference_number=transaction.reference_number,
            gateway_transaction_id=transaction.gateway_transaction_id,
            gateway_order_id=transaction.gateway_order_id,
            failure_reason=transaction.failure_reason,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            processed_at=transaction.processed_at,
        )
