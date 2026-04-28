"""Create Transaction Use Case.

This module implements the use case for creating new transactions
with proper validation and business rule enforcement.
"""

import logging
from typing import Optional
from uuid import uuid4

from ...domain.transaction_entities import Transaction
from ...domain.transaction_exceptions import TransactionCreationError, ValidationError
from ...domain.transaction_repos import IAuditLogRepository, ITransactionRepository
from ...domain.transaction_vos import (
    Money,
    PaymentMethod,
    TransactionNumber,
    TransactionStatus,
)
from ..transaction_dtos import TransactionCreateDTO, TransactionDTO

logger = logging.getLogger(__name__)


class CreateTransactionUseCase:
    """Use case for creating new transactions.

    This use case handles the creation of new transactions with proper
    validation, business rule enforcement, and audit logging.
    """

    def __init__(
        self,
        transaction_repository: ITransactionRepository,
        audit_log_repository: IAuditLogRepository,
    ):
        """Initialize the create transaction use case.

        Args:
            transaction_repository: Repository for transaction operations
            audit_log_repository: Repository for audit logging
        """
        self._transaction_repo = transaction_repository
        self._audit_repo = audit_log_repository

    async def execute(
        self, request: TransactionCreateDTO, created_by: Optional[str] = None
    ) -> TransactionDTO:
        """Execute the create transaction use case.

        Args:
            request: Transaction creation request data
            created_by: User creating the transaction

        Returns:
            Created transaction data

        Raises:
            TransactionCreationError: If transaction creation fails
            ValidationError: If request data is invalid
        """
        try:
            logger.info(
                "Creating transaction for restaurant %s",
                request.restaurant_id,
                extra={
                    "restaurant_id": str(request.restaurant_id),
                    "amount": float(request.amount.amount),
                    "payment_method": request.payment_method,
                    "created_by": created_by,
                },
            )

            # Validate request data
            self._validate_request(request)

            # Create money value object
            amount = Money(request.amount.amount, request.amount.currency)

            # Create transaction entity
            transaction = Transaction(
                id=uuid4(),
                restaurant_id=request.restaurant_id,
                order_id=request.order_id,
                amount=amount,
                payment_method=PaymentMethod(request.payment_method),
                customer_name=request.customer_name,
                customer_phone=request.customer_phone,
                customer_email=request.customer_email,
                description=request.description,
                reference_number=request.reference_number,
                status=TransactionStatus.PENDING,
            )

            # Save transaction to repository
            created_transaction = await self._transaction_repo.create_transaction(
                transaction
            )

            # Create audit log entry
            # TODO: Implement audit log database functions
            # await self._audit_repo.create_audit_log(
            #     entity_id=created_transaction.id,
            #     entity_type="transaction",
            #     action="CREATE",
            #     new_status=created_transaction.status,
            #     changes={
            #         "amount": float(created_transaction.amount.amount),
            #         "currency": created_transaction.amount.currency,
            #         "payment_method": created_transaction.payment_method,
            #         "restaurant_id": str(created_transaction.restaurant_id),
            #         "order_id": (
            #             str(created_transaction.order_id)
            #             if created_transaction.order_id
            #             else None
            #         ),
            #     },
            #     reason="Transaction created",
            # )

            logger.info(
                "Transaction created successfully",
                extra={
                    "transaction_id": str(created_transaction.id),
                    "transaction_number": created_transaction.transaction_number,
                    "restaurant_id": str(created_transaction.restaurant_id),
                },
            )

            # Convert to DTO and return
            return self._map_to_dto(created_transaction)

        except ValidationError:
            raise
        except Exception as e:
            logger.error(
                "Failed to create transaction",
                extra={
                    "restaurant_id": str(request.restaurant_id),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise TransactionCreationError(f"Failed to create transaction: {str(e)}")

    def _validate_request(self, request: TransactionCreateDTO) -> None:
        """Validate transaction creation request.

        Args:
            request: Transaction creation request

        Raises:
            ValidationError: If validation fails
        """
        # Validate amount
        if request.amount.amount <= 0:
            raise ValidationError("Transaction amount must be positive", "amount")

        # Validate customer information for non-cash payments
        if request.payment_method != PaymentMethod.CASH:
            if not request.customer_name or not request.customer_name.strip():
                raise ValidationError(
                    "Customer name is required for non-cash payments", "customer_name"
                )

            if not request.customer_phone or not request.customer_phone.strip():
                raise ValidationError(
                    "Customer phone is required for non-cash payments", "customer_phone"
                )

        # Validate phone format (basic validation)
        if request.customer_phone:
            phone = request.customer_phone.strip()
            if (
                len(phone) < 10
                or not phone.replace("+", "")
                .replace("-", "")
                .replace(" ", "")
                .isdigit()
            ):
                raise ValidationError("Invalid phone number format", "customer_phone")

        # Validate email format (basic validation)
        if request.customer_email:
            email = request.customer_email.strip()
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValidationError("Invalid email format", "customer_email")

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
            transaction_number=str(transaction.transaction_number),
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
