"""Transaction Management API Router.

This module provides REST API endpoints for transaction management operations.
"""

import logging
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from ...auth.presentation.supabase_dependencies import get_current_user
from ..application.transaction_dtos import (
    FinancialReportDTO,
    MoneyDTO,
    PaymentProcessingDTO,
    PayoutSummaryDTO,
    RefundCreateDTO,
    RefundDTO,
    TransactionCreateDTO,
    TransactionDTO,
    TransactionHistoryRequestDTO,
    TransactionHistoryResponseDTO,
)
from ..application.use_cases.create_transaction import CreateTransactionUseCase
from ..application.use_cases.generate_financial_report import (
    GenerateFinancialReportUseCase,
)
from ..application.use_cases.get_transaction_history import GetTransactionHistoryUseCase
from ..application.use_cases.get_transaction_summary import GetTransactionSummaryUseCase
from ..application.use_cases.process_payment import ProcessPaymentUseCase
from ..application.use_cases.process_refund import ProcessRefundUseCase
from ..domain.transaction_exceptions import (
    InsufficientFundsError,
    InvalidTransactionStatusError,
    PaymentProcessingError,
    TransactionError,
    TransactionNotFoundError,
    UnauthorizedOperationError,
    ValidationError,
)
from ..domain.transaction_vos import PaymentMethod, TransactionStatus
from ..infrastructure.transaction_repos_impl import (
    AuditLogRepositoryImpl,
    PayoutRepositoryImpl,
    RefundRepositoryImpl,
    TransactionRepositoryImpl,
)
from .transaction_schemas import (
    DailyRevenueTrendSchema,
    ErrorResponseSchema,
    MoneySchema,
    PaymentConfirmationSchema,
    PaymentMethodBreakdownSchema,
    RefundCreateSchema,
    RefundResponseSchema,
    TransactionCreateSchema,
    TransactionHistoryRequestSchema,
    TransactionHistoryResponseSchema,
    TransactionResponseSchema,
    TransactionSummarySchema,
    TransactionUpdateSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency injection
def get_transaction_repository() -> TransactionRepositoryImpl:
    """Get transaction repository instance."""
    return TransactionRepositoryImpl()


def get_refund_repository() -> RefundRepositoryImpl:
    """Get refund repository instance."""
    return RefundRepositoryImpl()


def get_payout_repository() -> PayoutRepositoryImpl:
    """Get payout repository instance."""
    return PayoutRepositoryImpl()


def get_audit_log_repository() -> AuditLogRepositoryImpl:
    """Get audit log repository instance."""
    return AuditLogRepositoryImpl()


def get_create_transaction_use_case(
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
    audit_repo: AuditLogRepositoryImpl = Depends(get_audit_log_repository),
) -> CreateTransactionUseCase:
    """Get create transaction use case instance."""
    return CreateTransactionUseCase(transaction_repo, audit_repo)


def get_transaction_summary_use_case(
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
) -> GetTransactionSummaryUseCase:
    """Get transaction summary use case instance."""
    return GetTransactionSummaryUseCase(transaction_repo)


def get_process_refund_use_case(
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
    refund_repo: RefundRepositoryImpl = Depends(get_refund_repository),
    audit_repo: AuditLogRepositoryImpl = Depends(get_audit_log_repository),
) -> ProcessRefundUseCase:
    """Get process refund use case instance."""
    return ProcessRefundUseCase(transaction_repo, refund_repo, audit_repo)


def get_process_payment_use_case(
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
    audit_repo: AuditLogRepositoryImpl = Depends(get_audit_log_repository),
) -> ProcessPaymentUseCase:
    """Get process payment use case instance."""
    return ProcessPaymentUseCase(transaction_repo, audit_repo)


def get_transaction_history_use_case(
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
) -> GetTransactionHistoryUseCase:
    """Get transaction history use case instance."""
    return GetTransactionHistoryUseCase(transaction_repo)


def get_financial_report_use_case(
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
    refund_repo: RefundRepositoryImpl = Depends(get_refund_repository),
    payout_repo: PayoutRepositoryImpl = Depends(get_payout_repository),
) -> GenerateFinancialReportUseCase:
    """Get financial report use case instance."""
    return GenerateFinancialReportUseCase(transaction_repo, refund_repo, payout_repo)


@router.post(
    "/transactions",
    response_model=TransactionResponseSchema,
    status_code=201,
    summary="Create a new transaction",
    description="Create a new transaction for payment processing",
)
async def create_transaction(
    request: TransactionCreateSchema,
    current_user: dict = Depends(get_current_user),
    use_case: CreateTransactionUseCase = Depends(get_create_transaction_use_case),
):
    """Create a new transaction.

    This endpoint creates a new transaction for payment processing.
    Supports both digital payments and cash/pay-at-restaurant scenarios.
    """
    try:
        # Convert schema to DTO
        create_dto = TransactionCreateDTO(
            restaurant_id=request.restaurant_id,
            order_id=request.order_id,
            amount=MoneyDTO(
                amount=request.amount.amount, currency=request.amount.currency
            ),
            payment_method=request.payment_method,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            customer_email=request.customer_email,
            description=request.description,
            reference_number=request.reference_number,
        )

        # Execute use case
        result = await use_case.execute(create_dto, current_user.user_id)

        # Convert DTO to response schema
        return TransactionResponseSchema(
            id=result.id,
            transaction_number=result.transaction_number,
            restaurant_id=result.restaurant_id,
            order_id=result.order_id,
            amount=MoneySchema(
                amount=result.amount.amount, currency=result.amount.currency
            ),
            payment_method=result.payment_method,
            status=result.status,
            customer_name=result.customer_name,
            customer_phone=result.customer_phone,
            customer_email=result.customer_email,
            description=result.description,
            reference_number=result.reference_number,
            gateway_transaction_id=result.gateway_transaction_id,
            gateway_order_id=result.gateway_order_id,
            failure_reason=result.failure_reason,
            created_at=result.created_at,
            updated_at=result.updated_at,
            processed_at=result.processed_at,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=400, detail={"error": str(e), "error_code": "VALIDATION_ERROR"}
        )
    except UnauthorizedOperationError as e:
        raise HTTPException(
            status_code=403, detail={"error": str(e), "error_code": "UNAUTHORIZED"}
        )
    except TransactionError as e:
        raise HTTPException(
            status_code=500, detail={"error": str(e), "error_code": "TRANSACTION_ERROR"}
        )


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponseSchema,
    summary="Get transaction by ID",
    description="Retrieve a specific transaction by its ID",
)
async def get_transaction(
    transaction_id: UUID = Path(..., description="Transaction ID"),
    current_user: dict = Depends(get_current_user),
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
):
    """Get a transaction by ID."""
    try:
        transaction = await transaction_repo.get_transaction_by_id(transaction_id)

        if not transaction:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Transaction not found",
                    "error_code": "TRANSACTION_NOT_FOUND",
                },
            )

        # Convert entity to response schema
        return TransactionResponseSchema(
            id=transaction.id,
            transaction_number=str(transaction.transaction_number),
            restaurant_id=transaction.restaurant_id,
            order_id=transaction.order_id,
            amount=MoneySchema(
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transaction: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})


@router.get(
    "/restaurants/{restaurant_id}/transactions",
    response_model=TransactionHistoryResponseSchema,
    summary="Get restaurant transactions",
    description="Get transaction history for a restaurant with filtering and pagination",
)
async def get_restaurant_transactions(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    status: Optional[str] = Query(None, description="Filter by transaction status"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    search_term: Optional[str] = Query(None, description="Search term"),
    current_user: dict = Depends(get_current_user),
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
):
    """Get transaction history for a restaurant."""
    try:
        # Get transactions from repository
        transactions = await transaction_repo.get_transactions_by_restaurant(
            restaurant_id=restaurant_id,
            limit=limit,
            offset=offset,
            status=status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            search_term=search_term,
        )

        # Convert entities to response schemas
        transaction_schemas = []
        for transaction in transactions:
            transaction_schemas.append(
                TransactionResponseSchema(
                    id=transaction.id,
                    transaction_number=transaction.transaction_number.value,
                    restaurant_id=transaction.restaurant_id,
                    order_id=transaction.order_id,
                    amount=MoneyDTO(
                        amount=transaction.amount.amount,
                        currency=transaction.amount.currency,
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
            )

        return TransactionHistoryResponseSchema(
            transactions=transaction_schemas,
            total_count=len(
                transaction_schemas
            ),  # This should come from the database function
            has_more=len(transaction_schemas) == limit,
        )

    except Exception as e:
        logger.error(f"Failed to get restaurant transactions: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})


@router.get(
    "/restaurants/{restaurant_id}/transactions/summary",
    response_model=TransactionSummarySchema,
    summary="Get transaction summary",
    description="Get transaction summary and analytics for a restaurant",
)
async def get_transaction_summary(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    start_date: Optional[date] = Query(None, description="Summary start date"),
    end_date: Optional[date] = Query(None, description="Summary end date"),
    period: str = Query(
        "monthly", description="Summary period (daily, weekly, monthly)"
    ),
    current_user: dict = Depends(get_current_user),
    use_case: GetTransactionSummaryUseCase = Depends(get_transaction_summary_use_case),
):
    """Get transaction summary for a restaurant."""
    try:
        summary = await use_case.execute(restaurant_id, start_date, end_date, period)

        return TransactionSummarySchema(
            total_transactions=summary.total_transactions,
            total_amount=summary.total_amount,
            completed_transactions=summary.completed_transactions,
            completed_amount=summary.completed_amount,
            pending_transactions=summary.pending_transactions,
            pending_amount=summary.pending_amount,
            failed_transactions=summary.failed_transactions,
            failed_amount=summary.failed_amount,
            refunded_transactions=summary.refunded_transactions,
            refunded_amount=summary.refunded_amount,
            average_transaction_amount=summary.average_transaction_amount,
        )

    except Exception as e:
        logger.error(f"Failed to get transaction summary: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})


@router.post(
    "/transactions/{transaction_id}/confirm-payment",
    response_model=TransactionResponseSchema,
    summary="Confirm cash payment",
    description="Confirm cash payment received at restaurant (staff only)",
)
async def confirm_cash_payment(
    transaction_id: UUID = Path(..., description="Transaction ID"),
    request: PaymentConfirmationSchema = ...,
    current_user: dict = Depends(get_current_user),
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
    audit_repo: AuditLogRepositoryImpl = Depends(get_audit_log_repository),
):
    """Confirm cash payment received at restaurant."""
    try:
        # Get the transaction
        transaction = await transaction_repo.get_transaction_by_id(transaction_id)

        if not transaction:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Transaction not found",
                    "error_code": "TRANSACTION_NOT_FOUND",
                },
            )

        # Validate that this is a cash payment
        if transaction.payment_method.value != "cash":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Only cash payments can be confirmed manually",
                    "error_code": "INVALID_PAYMENT_METHOD",
                },
            )

        # Mark transaction as completed
        transaction.mark_as_completed()

        # Update in database
        updated_transaction = await transaction_repo.update_transaction(transaction)

        # Create audit log
        await audit_repo.create_audit_log(
            entity_id=transaction.id,
            entity_type="transaction",
            action="CONFIRM_PAYMENT",
            previous_status="pending",
            new_status="completed",
            changes={
                "amount_received": float(request.amount_received.amount),
                "payment_method": request.payment_method.value,
                "notes": request.notes,
            },
            reason="Cash payment confirmed by restaurant staff",
            performed_by=UUID(current_user.user_id),
        )

        # Convert to response schema
        return TransactionResponseSchema(
            id=updated_transaction.id,
            transaction_number=updated_transaction.transaction_number.value,
            restaurant_id=updated_transaction.restaurant_id,
            order_id=updated_transaction.order_id,
            amount=MoneyDTO(
                amount=updated_transaction.amount.amount,
                currency=updated_transaction.amount.currency,
            ),
            payment_method=updated_transaction.payment_method,
            status=updated_transaction.status,
            customer_name=updated_transaction.customer_name,
            customer_phone=updated_transaction.customer_phone,
            customer_email=updated_transaction.customer_email,
            description=updated_transaction.description,
            reference_number=updated_transaction.reference_number,
            gateway_transaction_id=updated_transaction.gateway_transaction_id,
            gateway_order_id=updated_transaction.gateway_order_id,
            failure_reason=updated_transaction.failure_reason,
            created_at=updated_transaction.created_at,
            updated_at=updated_transaction.updated_at,
            processed_at=updated_transaction.processed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to confirm cash payment: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})


@router.put(
    "/transactions/{transaction_id}/status",
    response_model=TransactionResponseSchema,
    summary="Update transaction status",
    description="Update transaction status (staff only)",
)
async def update_transaction_status(
    transaction_id: UUID = Path(..., description="Transaction ID"),
    request: TransactionUpdateSchema = ...,
    current_user: dict = Depends(get_current_user),
    transaction_repo: TransactionRepositoryImpl = Depends(get_transaction_repository),
    audit_repo: AuditLogRepositoryImpl = Depends(get_audit_log_repository),
):
    """Update transaction status."""
    try:
        # Get the transaction
        transaction = await transaction_repo.get_transaction_by_id(transaction_id)

        if not transaction:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Transaction not found",
                    "error_code": "TRANSACTION_NOT_FOUND",
                },
            )

        previous_status = transaction.status.value

        # Update transaction fields
        if request.status:
            if request.status.value == "completed":
                transaction.mark_as_completed(
                    gateway_transaction_id=request.gateway_transaction_id,
                    gateway_response=request.gateway_response,
                )
            elif request.status.value == "failed":
                transaction.mark_as_failed(
                    failure_reason=request.failure_reason or "Payment failed",
                    gateway_response=request.gateway_response,
                )
            elif request.status.value == "processing":
                transaction.mark_as_processing(request.gateway_transaction_id)

        # Update in database
        updated_transaction = await transaction_repo.update_transaction(transaction)

        # Create audit log
        await audit_repo.create_audit_log(
            entity_id=transaction.id,
            entity_type="transaction",
            action="UPDATE_STATUS",
            previous_status=previous_status,
            new_status=updated_transaction.status.value,
            changes=request.dict(exclude_unset=True),
            reason="Transaction status updated",
            performed_by=UUID(current_user.user_id),
        )

        # Convert to response schema
        return TransactionResponseSchema(
            id=updated_transaction.id,
            transaction_number=updated_transaction.transaction_number.value,
            restaurant_id=updated_transaction.restaurant_id,
            order_id=updated_transaction.order_id,
            amount=MoneyDTO(
                amount=updated_transaction.amount.amount,
                currency=updated_transaction.amount.currency,
            ),
            payment_method=updated_transaction.payment_method,
            status=updated_transaction.status,
            customer_name=updated_transaction.customer_name,
            customer_phone=updated_transaction.customer_phone,
            customer_email=updated_transaction.customer_email,
            description=updated_transaction.description,
            reference_number=updated_transaction.reference_number,
            gateway_transaction_id=updated_transaction.gateway_transaction_id,
            gateway_order_id=updated_transaction.gateway_order_id,
            failure_reason=updated_transaction.failure_reason,
            created_at=updated_transaction.created_at,
            updated_at=updated_transaction.updated_at,
            processed_at=updated_transaction.processed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update transaction status: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})


@router.post("/{transaction_id}/process-payment", response_model=TransactionDTO)
async def process_payment(
    transaction_id: UUID = Path(..., description="Transaction ID"),
    payment_data: PaymentProcessingDTO = ...,
    process_payment_use_case: ProcessPaymentUseCase = Depends(
        get_process_payment_use_case
    ),
    current_user: dict = Depends(get_current_user),
) -> TransactionDTO:
    """Process payment for a transaction.

    Args:
        transaction_id: Transaction identifier
        payment_data: Payment processing data
        process_payment_use_case: Process payment use case
        current_user: Current authenticated user

    Returns:
        Updated transaction data

    Raises:
        HTTPException: If payment processing fails
    """
    try:
        logger.info(
            "Processing payment for transaction %s",
            transaction_id,
            extra={
                "transaction_id": str(transaction_id),
                "user_id": current_user.get("id"),
            },
        )

        transaction = await process_payment_use_case.execute(
            transaction_id=transaction_id,
            payment_data=payment_data,
            processed_by=UUID(current_user["id"]),
        )

        logger.info(
            "Payment processed successfully",
            extra={
                "transaction_id": str(transaction_id),
                "status": transaction.status.value,
            },
        )

        return transaction

    except (
        TransactionNotFoundError,
        ValidationError,
        InvalidTransactionStatusError,
    ) as e:
        logger.error(
            "Failed to process payment",
            extra={
                "transaction_id": str(transaction_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentProcessingError as e:
        logger.error(
            "Payment processing failed",
            extra={
                "transaction_id": str(transaction_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error processing payment",
            extra={
                "transaction_id": str(transaction_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refunds", response_model=RefundDTO)
async def create_refund(
    refund_request: RefundCreateDTO,
    process_refund_use_case: ProcessRefundUseCase = Depends(
        get_process_refund_use_case
    ),
    current_user: dict = Depends(get_current_user),
) -> RefundDTO:
    """Create a refund for a transaction.

    Args:
        refund_request: Refund creation request
        process_refund_use_case: Process refund use case
        current_user: Current authenticated user

    Returns:
        Created refund data

    Raises:
        HTTPException: If refund creation fails
    """
    try:
        logger.info(
            "Creating refund for transaction %s",
            refund_request.transaction_id,
            extra={
                "transaction_id": str(refund_request.transaction_id),
                "refund_amount": float(refund_request.amount.amount),
                "user_id": current_user.get("id"),
            },
        )

        refund = await process_refund_use_case.execute(
            request=refund_request, processed_by=UUID(current_user["id"])
        )

        logger.info(
            "Refund created successfully",
            extra={
                "refund_id": str(refund.id),
                "transaction_id": str(refund.transaction_id),
                "refund_amount": float(refund.amount.amount),
            },
        )

        return refund

    except (
        TransactionNotFoundError,
        ValidationError,
        InsufficientFundsError,
        InvalidTransactionStatusError,
    ) as e:
        logger.error(
            "Failed to create refund",
            extra={
                "transaction_id": str(refund_request.transaction_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error creating refund",
            extra={
                "transaction_id": str(refund_request.transaction_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history", response_model=TransactionHistoryResponseDTO)
async def get_transaction_history(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    status: Optional[TransactionStatus] = Query(None, description="Filter by status"),
    payment_method: Optional[PaymentMethod] = Query(
        None, description="Filter by payment method"
    ),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    search_term: Optional[str] = Query(None, description="Search term"),
    get_history_use_case: GetTransactionHistoryUseCase = Depends(
        get_transaction_history_use_case
    ),
    current_user: dict = Depends(get_current_user),
) -> TransactionHistoryResponseDTO:
    """Get transaction history for a restaurant.

    Args:
        restaurant_id: Restaurant identifier
        limit: Maximum number of results
        offset: Number of results to skip
        status: Filter by transaction status
        payment_method: Filter by payment method
        start_date: Filter by start date
        end_date: Filter by end date
        search_term: Search term
        get_history_use_case: Get transaction history use case
        current_user: Current authenticated user

    Returns:
        Transaction history data

    Raises:
        HTTPException: If history retrieval fails
    """
    try:
        logger.info(
            "Getting transaction history for restaurant %s",
            restaurant_id,
            extra={
                "restaurant_id": str(restaurant_id),
                "limit": limit,
                "offset": offset,
                "user_id": current_user.get("id"),
            },
        )

        request = TransactionHistoryRequestDTO(
            restaurant_id=restaurant_id,
            limit=limit,
            offset=offset,
            status=status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            search_term=search_term,
        )

        history = await get_history_use_case.execute(
            restaurant_id=restaurant_id, request=request
        )

        logger.info(
            "Transaction history retrieved successfully",
            extra={
                "restaurant_id": str(restaurant_id),
                "transactions_count": len(history.transactions),
                "total_count": history.total_count,
            },
        )

        return history

    except TransactionError as e:
        logger.error(
            "Failed to get transaction history",
            extra={
                "restaurant_id": str(restaurant_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error getting transaction history",
            extra={
                "restaurant_id": str(restaurant_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/reports/financial", response_model=FinancialReportDTO)
async def generate_financial_report(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    start_date: Optional[date] = Query(None, description="Report start date"),
    end_date: Optional[date] = Query(None, description="Report end date"),
    report_type: str = Query("comprehensive", description="Type of report"),
    include_trends: bool = Query(True, description="Include revenue trends"),
    include_breakdowns: bool = Query(
        True, description="Include payment method breakdowns"
    ),
    generate_report_use_case: GenerateFinancialReportUseCase = Depends(
        get_financial_report_use_case
    ),
    current_user: dict = Depends(get_current_user),
) -> FinancialReportDTO:
    """Generate financial report for a restaurant.

    Args:
        restaurant_id: Restaurant identifier
        start_date: Report start date
        end_date: Report end date
        report_type: Type of report
        include_trends: Include revenue trends
        include_breakdowns: Include payment method breakdowns
        generate_report_use_case: Generate financial report use case
        current_user: Current authenticated user

    Returns:
        Financial report data

    Raises:
        HTTPException: If report generation fails
    """
    try:
        logger.info(
            "Generating financial report for restaurant %s",
            restaurant_id,
            extra={
                "restaurant_id": str(restaurant_id),
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "report_type": report_type,
                "user_id": current_user.get("id"),
            },
        )

        report = await generate_report_use_case.execute(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            include_trends=include_trends,
            include_breakdowns=include_breakdowns,
        )

        logger.info(
            "Financial report generated successfully",
            extra={
                "restaurant_id": str(restaurant_id),
                "report_period": f"{report.report_period_start} to {report.report_period_end}",
                "total_transactions": report.transaction_summary.total_transactions,
            },
        )

        return report

    except TransactionError as e:
        logger.error(
            "Failed to generate financial report",
            extra={
                "restaurant_id": str(restaurant_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error generating financial report",
            extra={
                "restaurant_id": str(restaurant_id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/payouts", response_model=List[PayoutSummaryDTO])
async def get_payouts(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    status: Optional[str] = Query(None, description="Filter by payout status"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    payout_repo: PayoutRepositoryImpl = Depends(get_payout_repository),
    current_user: dict = Depends(get_current_user),
) -> List[PayoutSummaryDTO]:
    """Get payouts for a restaurant.

    Args:
        restaurant_id: Restaurant identifier
        limit: Maximum number of results
        offset: Number of results to skip
        status: Filter by payout status
        start_date: Filter by start date
        end_date: Filter by end date
        payout_repo: Payout repository
        current_user: Current authenticated user

    Returns:
        List of payout summaries

    Raises:
        HTTPException: If operation fails
    """
    try:
        # Convert status string to enum if provided
        payout_status = None
        if status:
            try:
                from ..domain.transaction_vos import PayoutStatus

                payout_status = PayoutStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid payout status: {status}"
                )

        # Get payouts from repository
        payouts = await payout_repo.get_payouts_by_restaurant(
            restaurant_id=restaurant_id,
            limit=limit,
            offset=offset,
            status=payout_status,
            start_date=start_date,
            end_date=end_date,
        )

        # Convert to DTOs
        payout_dtos = []
        for payout in payouts:
            payout_dto = PayoutSummaryDTO(
                id=payout.id,
                payout_number=payout.payout_number.value,
                restaurant_id=payout.restaurant_id,
                amount=MoneyDTO(
                    amount=payout.amount.amount, currency=payout.amount.currency.value
                ),
                fees=(
                    MoneyDTO(
                        amount=payout.fees.amount, currency=payout.fees.currency.value
                    )
                    if payout.fees
                    else None
                ),
                net_amount=MoneyDTO(
                    amount=payout.net_amount.amount,
                    currency=payout.net_amount.currency.value,
                ),
                status=payout.status.value,
                gateway_payout_id=payout.gateway_payout_id,
                bank_account_id=payout.bank_account_id,
                description=payout.description,
                processed_by=payout.processed_by,
                created_at=payout.created_at,
                updated_at=payout.updated_at,
                processed_at=payout.processed_at,
            )
            payout_dtos.append(payout_dto)

        logger.info(
            f"Retrieved {len(payout_dtos)} payouts for restaurant {restaurant_id}",
            extra={
                "restaurant_id": str(restaurant_id),
                "payout_count": len(payout_dtos),
                "filters": {
                    "status": status,
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                },
            },
        )

        return payout_dtos

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get payouts for restaurant {restaurant_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/reports/financial/export")
async def export_financial_report(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    start_date: Optional[date] = Query(None, description="Report start date"),
    end_date: Optional[date] = Query(None, description="Report end date"),
    format: str = Query("csv", description="Export format (csv or pdf)"),
    include_trends: bool = Query(True, description="Include revenue trends"),
    include_breakdowns: bool = Query(
        True, description="Include payment method breakdowns"
    ),
    generate_report_use_case: GenerateFinancialReportUseCase = Depends(
        get_financial_report_use_case
    ),
    current_user: dict = Depends(get_current_user),
):
    """Export financial report in CSV or PDF format.

    Args:
        restaurant_id: Restaurant identifier
        start_date: Report start date
        end_date: Report end date
        format: Export format (csv or pdf)
        include_trends: Include revenue trends
        include_breakdowns: Include payment method breakdowns
        generate_report_use_case: Financial report use case
        current_user: Current authenticated user

    Returns:
        File download response

    Raises:
        HTTPException: If operation fails
    """
    try:
        # Validate format
        if format not in ["csv", "pdf"]:
            raise HTTPException(
                status_code=400, detail="Invalid format. Supported formats: csv, pdf"
            )

        # Generate the report data
        report = await generate_report_use_case.execute(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date,
            include_trends=include_trends,
            include_breakdowns=include_breakdowns,
        )

        if format == "csv":
            # Generate CSV content
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(
                [
                    "Report Period",
                    f"{report.report_period_start} to {report.report_period_end}",
                ]
            )
            writer.writerow([])  # Empty row

            # Transaction summary
            writer.writerow(["Transaction Summary"])
            writer.writerow(
                ["Total Transactions", report.transaction_summary.total_transactions]
            )
            writer.writerow(
                [
                    "Total Revenue",
                    f"{report.transaction_summary.total_revenue.amount} {report.transaction_summary.total_revenue.currency}",
                ]
            )
            writer.writerow(
                [
                    "Average Transaction",
                    f"{report.transaction_summary.average_transaction_value.amount} {report.transaction_summary.average_transaction_value.currency}",
                ]
            )
            writer.writerow([])  # Empty row

            # Payment method breakdown
            if report.payment_method_breakdown:
                writer.writerow(["Payment Method Breakdown"])
                writer.writerow(["Method", "Count", "Amount", "Currency"])
                for breakdown in report.payment_method_breakdown:
                    writer.writerow(
                        [
                            breakdown.payment_method,
                            breakdown.transaction_count,
                            breakdown.total_amount.amount,
                            breakdown.total_amount.currency,
                        ]
                    )
                writer.writerow([])  # Empty row

            # Revenue trends
            if report.daily_revenue_trends:
                writer.writerow(["Daily Revenue Trends"])
                writer.writerow(["Date", "Revenue", "Currency", "Transaction Count"])
                for trend in report.daily_revenue_trends:
                    writer.writerow(
                        [
                            trend.date,
                            trend.revenue.amount,
                            trend.revenue.currency,
                            trend.transaction_count,
                        ]
                    )

            # Create response
            from fastapi.responses import StreamingResponse

            def iter_csv():
                output.seek(0)
                yield output.getvalue()

            filename = f"financial_report_{restaurant_id}_{report.report_period_start}_{report.report_period_end}.csv"

            return StreamingResponse(
                iter_csv(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )

        else:  # PDF format
            # For now, return a simple text response indicating PDF export is not yet implemented
            # In a real implementation, you would use a library like reportlab or weasyprint
            raise HTTPException(
                status_code=501,
                detail="PDF export is not yet implemented. Please use CSV format.",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to export financial report for restaurant {restaurant_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")
