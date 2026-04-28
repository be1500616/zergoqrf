"""Transaction Management Domain Exceptions.

This module defines custom exceptions for transaction management domain operations
following the clean architecture principle of domain-specific error handling.
"""

from typing import Any, Dict, Optional
from uuid import UUID


class TransactionManagementError(Exception):
    """Base exception for transaction management domain errors."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        """Initialize transaction management error.

        Args:
            message: Error message
            error_code: Optional error code for categorization
        """
        super().__init__(message)
        self.error_code = error_code


class TransactionError(TransactionManagementError):
    """Base exception for transaction-related errors."""

    def __init__(
        self,
        message: str,
        transaction_id: Optional[UUID] = None,
        error_code: Optional[str] = None,
    ):
        """Initialize transaction error.

        Args:
            message: Error message
            transaction_id: Associated transaction ID
            error_code: Optional error code
        """
        super().__init__(message, error_code)
        self.transaction_id = transaction_id


class TransactionNotFoundError(TransactionError):
    """Exception raised when a transaction is not found."""

    def __init__(self, transaction_id: UUID):
        """Initialize transaction not found error.

        Args:
            transaction_id: Transaction ID that was not found
        """
        super().__init__(
            f"Transaction with ID {transaction_id} not found",
            transaction_id,
            "TRANSACTION_NOT_FOUND",
        )


class TransactionCreationError(TransactionError):
    """Exception raised when transaction creation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize transaction creation error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, error_code="TRANSACTION_CREATION_FAILED")
        self.details = details or {}


class TransactionUpdateError(TransactionError):
    """Exception raised when transaction update fails."""

    def __init__(
        self,
        message: str,
        transaction_id: UUID,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize transaction update error.

        Args:
            message: Error message
            transaction_id: Transaction ID that failed to update
            details: Additional error details
        """
        super().__init__(message, transaction_id, "TRANSACTION_UPDATE_FAILED")
        self.details = details or {}


class InvalidTransactionStatusError(TransactionError):
    """Exception raised when an invalid transaction status transition is attempted."""

    def __init__(
        self,
        current_status: str,
        attempted_status: str,
        transaction_id: Optional[UUID] = None,
    ):
        """Initialize invalid transaction status error.

        Args:
            current_status: Current transaction status
            attempted_status: Attempted new status
            transaction_id: Associated transaction ID
        """
        message = f"Cannot transition from {current_status} to {attempted_status}"
        super().__init__(message, transaction_id, "INVALID_STATUS_TRANSITION")
        self.current_status = current_status
        self.attempted_status = attempted_status


class InsufficientFundsError(TransactionError):
    """Exception raised when there are insufficient funds for an operation."""

    def __init__(
        self,
        available_amount: float,
        requested_amount: float,
        transaction_id: Optional[UUID] = None,
    ):
        """Initialize insufficient funds error.

        Args:
            available_amount: Available amount
            requested_amount: Requested amount
            transaction_id: Associated transaction ID
        """
        message = f"Insufficient funds: available {available_amount}, requested {requested_amount}"
        super().__init__(message, transaction_id, "INSUFFICIENT_FUNDS")
        self.available_amount = available_amount
        self.requested_amount = requested_amount


class RefundError(TransactionManagementError):
    """Base exception for refund-related errors."""

    def __init__(
        self,
        message: str,
        refund_id: Optional[UUID] = None,
        transaction_id: Optional[UUID] = None,
        error_code: Optional[str] = None,
    ):
        """Initialize refund error.

        Args:
            message: Error message
            refund_id: Associated refund ID
            transaction_id: Associated transaction ID
            error_code: Optional error code
        """
        super().__init__(message, error_code)
        self.refund_id = refund_id
        self.transaction_id = transaction_id


class RefundNotFoundError(RefundError):
    """Exception raised when a refund is not found."""

    def __init__(self, refund_id: UUID):
        """Initialize refund not found error.

        Args:
            refund_id: Refund ID that was not found
        """
        super().__init__(
            f"Refund with ID {refund_id} not found",
            refund_id,
            error_code="REFUND_NOT_FOUND",
        )


class RefundCreationError(RefundError):
    """Exception raised when refund creation fails."""

    def __init__(
        self,
        message: str,
        transaction_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize refund creation error.

        Args:
            message: Error message
            transaction_id: Associated transaction ID
            details: Additional error details
        """
        super().__init__(
            message, transaction_id=transaction_id, error_code="REFUND_CREATION_FAILED"
        )
        self.details = details or {}


class RefundAmountExceedsTransactionError(RefundError):
    """Exception raised when refund amount exceeds transaction amount."""

    def __init__(
        self, transaction_amount: float, refund_amount: float, transaction_id: UUID
    ):
        """Initialize refund amount exceeds transaction error.

        Args:
            transaction_amount: Original transaction amount
            refund_amount: Requested refund amount
            transaction_id: Associated transaction ID
        """
        message = f"Refund amount {refund_amount} exceeds transaction amount {transaction_amount}"
        super().__init__(
            message,
            transaction_id=transaction_id,
            error_code="REFUND_AMOUNT_EXCEEDS_TRANSACTION",
        )
        self.transaction_amount = transaction_amount
        self.refund_amount = refund_amount


class RefundUpdateError(RefundError):
    """Exception raised when refund update fails."""

    def __init__(
        self, message: str, refund_id: UUID, details: Optional[Dict[str, Any]] = None
    ):
        """Initialize refund update error.

        Args:
            message: Error message
            refund_id: Refund ID that failed to update
            details: Additional error details
        """
        super().__init__(message, refund_id, error_code="REFUND_UPDATE_FAILED")
        self.details = details or {}


class RefundNotAllowedError(RefundError):
    """Exception raised when a refund is not allowed for a transaction."""

    def __init__(self, transaction_id: UUID, reason: str):
        """Initialize refund not allowed error.

        Args:
            transaction_id: Transaction ID
            reason: Reason why refund is not allowed
        """
        message = f"Refund not allowed for transaction {transaction_id}: {reason}"
        super().__init__(
            message, transaction_id=transaction_id, error_code="REFUND_NOT_ALLOWED"
        )
        self.reason = reason


class PayoutError(TransactionManagementError):
    """Base exception for payout-related errors."""

    def __init__(
        self,
        message: str,
        payout_id: Optional[UUID] = None,
        restaurant_id: Optional[UUID] = None,
        error_code: Optional[str] = None,
    ):
        """Initialize payout error.

        Args:
            message: Error message
            payout_id: Associated payout ID
            restaurant_id: Associated restaurant ID
            error_code: Optional error code
        """
        super().__init__(message, error_code)
        self.payout_id = payout_id
        self.restaurant_id = restaurant_id


class PayoutNotFoundError(PayoutError):
    """Exception raised when a payout is not found."""

    def __init__(self, payout_id: UUID):
        """Initialize payout not found error.

        Args:
            payout_id: Payout ID that was not found
        """
        super().__init__(
            f"Payout with ID {payout_id} not found",
            payout_id,
            error_code="PAYOUT_NOT_FOUND",
        )


class PayoutCreationError(PayoutError):
    """Exception raised when payout creation fails."""

    def __init__(
        self,
        message: str,
        restaurant_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize payout creation error.

        Args:
            message: Error message
            restaurant_id: Associated restaurant ID
            details: Additional error details
        """
        super().__init__(
            message, restaurant_id=restaurant_id, error_code="PAYOUT_CREATION_FAILED"
        )
        self.details = details or {}


class PayoutUpdateError(PayoutError):
    """Exception raised when payout update fails."""

    def __init__(
        self, message: str, payout_id: UUID, details: Optional[Dict[str, Any]] = None
    ):
        """Initialize payout update error.

        Args:
            message: Error message
            payout_id: Payout ID that failed to update
            details: Additional error details
        """
        super().__init__(message, payout_id, error_code="PAYOUT_UPDATE_FAILED")
        self.details = details or {}


class InvalidPayoutAmountError(PayoutError):
    """Exception raised when payout amount calculation is invalid."""

    def __init__(
        self,
        gross_amount: float,
        platform_fee: float,
        tax_amount: float,
        net_amount: float,
        restaurant_id: Optional[UUID] = None,
    ):
        """Initialize invalid payout amount error.

        Args:
            gross_amount: Gross payout amount
            platform_fee: Platform fee amount
            tax_amount: Tax amount
            net_amount: Net payout amount
            restaurant_id: Associated restaurant ID
        """
        expected_net = gross_amount - platform_fee - tax_amount
        message = (
            f"Invalid payout calculation: expected net {expected_net}, got {net_amount}"
        )
        super().__init__(
            message, restaurant_id=restaurant_id, error_code="INVALID_PAYOUT_AMOUNT"
        )
        self.gross_amount = gross_amount
        self.platform_fee = platform_fee
        self.tax_amount = tax_amount
        self.net_amount = net_amount
        self.expected_net = expected_net


class PaymentProcessingError(TransactionError):
    """Exception raised when payment processing fails."""

    def __init__(
        self,
        message: str,
        transaction_id: Optional[UUID] = None,
        gateway_error: Optional[str] = None,
    ):
        """Initialize payment processing error.

        Args:
            message: Error message
            transaction_id: Associated transaction ID
            gateway_error: Gateway-specific error message
        """
        super().__init__(message, transaction_id, "PAYMENT_PROCESSING_FAILED")
        self.gateway_error = gateway_error


class PaymentGatewayError(TransactionManagementError):
    """Exception raised for payment gateway integration errors."""

    def __init__(
        self,
        message: str,
        gateway_name: Optional[str] = None,
        gateway_error_code: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None,
    ):
        """Initialize payment gateway error.

        Args:
            message: Error message
            gateway_name: Name of the payment gateway
            gateway_error_code: Gateway-specific error code
            gateway_response: Full gateway response
        """
        super().__init__(message, "PAYMENT_GATEWAY_ERROR")
        self.gateway_name = gateway_name
        self.gateway_error_code = gateway_error_code
        self.gateway_response = gateway_response or {}


class WebhookVerificationError(TransactionManagementError):
    """Exception raised when webhook signature verification fails."""

    def __init__(self, gateway_name: str, reason: str):
        """Initialize webhook verification error.

        Args:
            gateway_name: Name of the payment gateway
            reason: Reason for verification failure
        """
        message = f"Webhook verification failed for {gateway_name}: {reason}"
        super().__init__(message, "WEBHOOK_VERIFICATION_FAILED")
        self.gateway_name = gateway_name
        self.reason = reason


class AuditLogError(TransactionManagementError):
    """Exception raised for audit logging errors."""

    def __init__(self, message: str, entity_id: Optional[UUID] = None):
        """Initialize audit log error.

        Args:
            message: Error message
            entity_id: Associated entity ID
        """
        super().__init__(message, "AUDIT_LOG_ERROR")
        self.entity_id = entity_id


class ValidationError(TransactionManagementError):
    """Exception raised for domain validation errors."""

    def __init__(self, message: str, field: Optional[str] = None):
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
        """
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class CurrencyMismatchError(ValidationError):
    """Exception raised when currency values don't match."""

    def __init__(self, expected_currency: str, actual_currency: str):
        """Initialize currency mismatch error.

        Args:
            expected_currency: Expected currency code
            actual_currency: Actual currency code
        """
        message = (
            f"Currency mismatch: expected {expected_currency}, got {actual_currency}"
        )
        super().__init__(message)
        self.expected_currency = expected_currency
        self.actual_currency = actual_currency


class UnauthorizedOperationError(TransactionManagementError):
    """Exception raised when user is not authorized for an operation."""

    def __init__(self, operation: str, user_id: Optional[UUID] = None):
        """Initialize unauthorized operation error.

        Args:
            operation: Operation that was attempted
            user_id: User ID that attempted the operation
        """
        message = f"User {user_id} not authorized for operation: {operation}"
        super().__init__(message, "UNAUTHORIZED_OPERATION")
        self.operation = operation
        self.user_id = user_id
