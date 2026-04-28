"""Transaction Repository Implementation.

This module implements the transaction repository using Supabase as the data store.
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import Client

from ....common.supabase_client import get_supabase
from ..domain.transaction_entities import Payout, Refund, Transaction
from ..domain.transaction_exceptions import (
    PayoutCreationError,
    PayoutNotFoundError,
    PayoutUpdateError,
    RefundCreationError,
    RefundNotFoundError,
    RefundUpdateError,
    TransactionCreationError,
    TransactionNotFoundError,
    TransactionUpdateError,
)
from ..domain.transaction_repos import (
    IAuditLogRepository,
    IPayoutRepository,
    IRefundRepository,
    ITransactionRepository,
)
from ..domain.transaction_vos import (
    Currency,
    Money,
    PaymentMethod,
    PayoutStatus,
    RefundStatus,
    TransactionNumber,
    TransactionStatus,
)

logger = logging.getLogger(__name__)


class TransactionRepositoryImpl(ITransactionRepository):
    """Supabase implementation of transaction repository."""

    def __init__(self, client: Optional[Client] = None):
        """Initialize transaction repository.

        Args:
            client: Supabase client instance
        """
        self._client = client or get_supabase()

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """Create a new transaction."""
        try:
            # Prepare transaction data
            transaction_data = {
                "id": str(transaction.id),
                "restaurant_id": str(transaction.restaurant_id),
                "order_id": str(transaction.order_id) if transaction.order_id else None,
                "amount": float(transaction.amount.amount),
                "currency": transaction.amount.currency,
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "customer_name": transaction.customer_name,
                "customer_phone": transaction.customer_phone,
                "customer_email": transaction.customer_email,
                "description": transaction.description,
                "reference_number": transaction.reference_number,
                "gateway_transaction_id": transaction.gateway_transaction_id,
                "gateway_order_id": transaction.gateway_order_id,
                "gateway_response": transaction.gateway_response,
                "failure_reason": transaction.failure_reason,
            }

            # Insert transaction
            result = (
                self._client.table("transactions").insert(transaction_data).execute()
            )

            if not result.data:
                raise TransactionCreationError("Failed to create transaction")

            # Return created transaction
            return self._map_to_transaction_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to create transaction: {str(e)}")
            raise TransactionCreationError(f"Database error: {str(e)}")

    async def get_transaction_by_id(
        self, transaction_id: UUID
    ) -> Optional[Transaction]:
        """Get transaction by ID."""
        try:
            result = (
                self._client.table("transactions")
                .select("*")
                .eq("id", str(transaction_id))
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_transaction_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to get transaction by ID: {str(e)}")
            return None

    async def get_transaction_by_number(
        self, transaction_number: str
    ) -> Optional[Transaction]:
        """Get transaction by transaction number."""
        try:
            result = (
                self._client.table("transactions")
                .select("*")
                .eq("transaction_number", transaction_number)
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_transaction_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to get transaction by number: {str(e)}")
            return None

    async def get_transactions_by_restaurant(
        self,
        restaurant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[TransactionStatus] = None,
        payment_method: Optional[PaymentMethod] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search_term: Optional[str] = None,
    ) -> List[Transaction]:
        """Get transactions for a restaurant with filtering."""
        try:
            # Use the database function for complex filtering
            params = {
                "p_restaurant_id": str(restaurant_id),
                "p_limit": limit,
                "p_offset": offset,
                "p_status": status if status else None,
                "p_payment_method": payment_method if payment_method else None,
                "p_start_date": start_date.isoformat() if start_date else None,
                "p_end_date": end_date.isoformat() if end_date else None,
                "p_search_term": search_term,
            }

            result = self._client.rpc("get_transaction_history", params).execute()

            if not result.data:
                return []

            return [self._map_to_transaction_entity(row) for row in result.data]

        except Exception as e:
            logger.error(f"Failed to get transactions by restaurant: {str(e)}")
            return []

    async def count_transactions_by_restaurant(
        self,
        restaurant_id: UUID,
        status: Optional[TransactionStatus] = None,
        payment_method: Optional[PaymentMethod] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search_term: Optional[str] = None,
    ) -> int:
        """Count transactions for a restaurant with filtering."""
        try:
            # Use the database function for complex filtering
            params = {
                "p_restaurant_id": str(restaurant_id),
                "p_status": status if status else None,
                "p_payment_method": payment_method if payment_method else None,
                "p_start_date": start_date.isoformat() if start_date else None,
                "p_end_date": end_date.isoformat() if end_date else None,
                "p_search_term": search_term,
            }

            result = self._client.rpc("count_transaction_history", params).execute()

            if not result.data:
                return 0

            return result.data[0].get("count", 0)

        except Exception as e:
            logger.error(f"Failed to count transactions by restaurant: {str(e)}")
            return 0

    async def get_transaction_by_number(
        self, restaurant_id: UUID, transaction_number: str
    ) -> Optional[Transaction]:
        """Get transaction by number for a specific restaurant."""
        try:
            result = (
                self._client.table("transactions")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
                .eq("transaction_number", transaction_number)
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_transaction_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to get transaction by number: {str(e)}")
            return None

    async def update_transaction(self, transaction: Transaction) -> Transaction:
        """Update an existing transaction."""
        try:
            # Prepare update data
            update_data = {
                "status": transaction.status,
                "gateway_transaction_id": transaction.gateway_transaction_id,
                "gateway_order_id": transaction.gateway_order_id,
                "gateway_response": transaction.gateway_response,
                "failure_reason": transaction.failure_reason,
                "processed_at": (
                    transaction.processed_at.isoformat()
                    if transaction.processed_at
                    else None
                ),
                "updated_at": datetime.utcnow().replace(tzinfo=None).isoformat() + "Z",
            }

            # Update transaction
            result = (
                self._client.table("transactions")
                .update(update_data)
                .eq("id", str(transaction.id))
                .execute()
            )

            if not result.data:
                raise TransactionUpdateError("Transaction not found", transaction.id)

            return self._map_to_transaction_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to update transaction: {str(e)}")
            raise TransactionUpdateError(f"Database error: {str(e)}", transaction.id)

    async def get_transaction_summary(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get transaction summary for a restaurant."""
        try:
            params = {
                "p_restaurant_id": str(restaurant_id),
                "p_start_date": start_date.isoformat() if start_date else None,
                "p_end_date": end_date.isoformat() if end_date else None,
            }

            result = self._client.rpc("get_transaction_summary", params).execute()

            if not result.data:
                return {}

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to get transaction summary: {str(e)}")
            return {}

    async def get_payment_method_breakdown(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """Get payment method breakdown for a restaurant."""
        try:
            params = {
                "p_restaurant_id": str(restaurant_id),
                "p_start_date": start_date.isoformat() if start_date else None,
                "p_end_date": end_date.isoformat() if end_date else None,
            }

            result = self._client.rpc("get_payment_method_breakdown", params).execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get payment method breakdown: {str(e)}")
            return []

    async def get_daily_revenue_trends(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """Get daily revenue trends for a restaurant."""
        try:
            params = {
                "p_restaurant_id": str(restaurant_id),
                "p_start_date": start_date.isoformat() if start_date else None,
                "p_end_date": end_date.isoformat() if end_date else None,
            }

            result = self._client.rpc("get_daily_revenue_trends", params).execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get daily revenue trends: {str(e)}")
            return []

    def _map_to_transaction_entity(self, data: Dict[str, Any]) -> Transaction:
        """Map database row to transaction entity."""
        return Transaction(
            id=UUID(data["id"]),
            restaurant_id=UUID(data["restaurant_id"]),
            order_id=UUID(data["order_id"]) if data.get("order_id") else None,
            amount=Money(Decimal(str(data["amount"])), Currency(data["currency"])),
            payment_method=PaymentMethod(data["payment_method"]),
            transaction_number=TransactionNumber(data["transaction_number"]),
            customer_name=data.get("customer_name"),
            customer_phone=data.get("customer_phone"),
            customer_email=data.get("customer_email"),
            description=data.get("description"),
            reference_number=data.get("reference_number"),
            gateway_transaction_id=data.get("gateway_transaction_id"),
            gateway_order_id=data.get("gateway_order_id"),
            gateway_response=data.get("gateway_response", {}),
            status=TransactionStatus(data["status"]),
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                data["updated_at"].replace("Z", "+00:00")
            ),
            processed_at=(
                datetime.fromisoformat(data["processed_at"].replace("Z", "+00:00"))
                if data.get("processed_at")
                else None
            ),
            failure_reason=data.get("failure_reason"),
        )


class AuditLogRepositoryImpl(IAuditLogRepository):
    """Supabase implementation of audit log repository."""

    def __init__(self, client: Optional[Client] = None):
        """Initialize audit log repository.

        Args:
            client: Supabase client instance
        """
        self._client = client or get_supabase()

    async def create_audit_log(
        self,
        entity_id: UUID,
        entity_type: str,
        action: str,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        performed_by: Optional[UUID] = None,
    ) -> UUID:
        """Create an audit log entry."""
        try:
            # Use the database function for audit log creation
            params = {
                f"p_{entity_type}_id": str(entity_id),
                "p_action": action,
                "p_entity_type": entity_type,
                "p_previous_status": previous_status,
                "p_new_status": new_status,
                "p_changes": changes or {},
                "p_reason": reason,
            }

            result = self._client.rpc("create_transaction_audit_log", params).execute()

            if not result.data:
                raise Exception("Failed to create audit log")

            return UUID(result.data[0])

        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            raise

    async def get_audit_logs_for_entity(
        self, entity_id: UUID, entity_type: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit logs for a specific entity."""
        try:
            query = self._client.table("transaction_audit_logs").select("*")

            if entity_type == "transaction":
                query = query.eq("transaction_id", str(entity_id))
            elif entity_type == "refund":
                query = query.eq("refund_id", str(entity_id))
            elif entity_type == "payout":
                query = query.eq("payout_id", str(entity_id))

            result = (
                query.order("created_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get audit logs: {str(e)}")
            return []


class RefundRepositoryImpl(IRefundRepository):
    """Supabase implementation of refund repository."""

    def __init__(self, client: Optional[Client] = None):
        """Initialize refund repository.

        Args:
            client: Supabase client instance
        """
        self._client = client or get_supabase()

    async def create_refund(self, refund: Refund) -> Refund:
        """Create a new refund."""
        try:
            # Prepare refund data
            refund_data = {
                "id": str(refund.id),
                "refund_number": refund.refund_number.value,
                "transaction_id": str(refund.transaction_id),
                "restaurant_id": str(refund.restaurant_id),
                "amount": float(refund.amount.amount),
                "currency": refund.amount.currency.value,
                "reason": refund.reason,
                "status": refund.status.value,
                "gateway_refund_id": refund.gateway_refund_id,
                "processed_by": (
                    str(refund.processed_by) if refund.processed_by else None
                ),
                "approved_by": str(refund.approved_by) if refund.approved_by else None,
                "processed_at": (
                    refund.processed_at.isoformat() if refund.processed_at else None
                ),
            }

            # Insert refund
            result = self._client.table("refunds").insert(refund_data).execute()

            if not result.data:
                raise RefundCreationError("Failed to create refund")

            # Return created refund
            return self._map_to_refund_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to create refund: {str(e)}")
            raise RefundCreationError(f"Database error: {str(e)}")

    async def get_refund_by_id(self, refund_id: UUID) -> Optional[Refund]:
        """Get refund by ID."""
        try:
            result = (
                self._client.table("refunds")
                .select("*")
                .eq("id", str(refund_id))
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_refund_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to get refund by ID: {str(e)}")
            return None

    async def get_refunds_by_transaction(self, transaction_id: UUID) -> List[Refund]:
        """Get refunds for a transaction."""
        try:
            result = (
                self._client.table("refunds")
                .select("*")
                .eq("transaction_id", str(transaction_id))
                .order("created_at", desc=True)
                .execute()
            )

            if not result.data:
                return []

            return [self._map_to_refund_entity(row) for row in result.data]

        except Exception as e:
            logger.error(f"Failed to get refunds by transaction: {str(e)}")
            return []

    async def update_refund(self, refund: Refund) -> Refund:
        """Update an existing refund."""
        try:
            # Prepare update data
            update_data = {
                "status": refund.status.value,
                "gateway_refund_id": refund.gateway_refund_id,
                "approved_by": str(refund.approved_by) if refund.approved_by else None,
                "processed_at": (
                    refund.processed_at.isoformat() if refund.processed_at else None
                ),
                "updated_at": datetime.utcnow().replace(tzinfo=None).isoformat() + "Z",
            }

            # Update refund
            result = (
                self._client.table("refunds")
                .update(update_data)
                .eq("id", str(refund.id))
                .execute()
            )

            if not result.data:
                raise RefundNotFoundError(refund.id)

            # Return updated refund
            return self._map_to_refund_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to update refund: {str(e)}")
            raise RefundUpdateError(f"Database error: {str(e)}", refund.id)

    async def get_refund_summary(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get refund summary for a restaurant."""
        try:
            params = {
                "p_restaurant_id": str(restaurant_id),
                "p_start_date": start_date.isoformat() if start_date else None,
                "p_end_date": end_date.isoformat() if end_date else None,
            }

            result = self._client.rpc("get_refund_summary", params).execute()

            if not result.data:
                return {}

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to get refund summary: {str(e)}")
            return {}

    def _map_to_refund_entity(self, data: Dict[str, Any]) -> Refund:
        """Map database row to refund entity."""
        return Refund(
            id=UUID(data["id"]),
            transaction_id=UUID(data["transaction_id"]),
            restaurant_id=UUID(data["restaurant_id"]),
            amount=Money(Decimal(str(data["amount"])), Currency(data["currency"])),
            reason=data["reason"],
            status=RefundStatus(data["status"]),
            gateway_refund_id=data.get("gateway_refund_id"),
            processed_by=(
                UUID(data["processed_by"]) if data.get("processed_by") else None
            ),
            approved_by=UUID(data["approved_by"]) if data.get("approved_by") else None,
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                data["updated_at"].replace("Z", "+00:00")
            ),
            processed_at=(
                datetime.fromisoformat(data["processed_at"].replace("Z", "+00:00"))
                if data.get("processed_at")
                else None
            ),
        )


class PayoutRepositoryImpl(IPayoutRepository):
    """Supabase implementation of payout repository."""

    def __init__(self, client: Optional[Client] = None):
        """Initialize payout repository.

        Args:
            client: Supabase client instance
        """
        self._client = client or get_supabase()

    async def create_payout(self, payout: Payout) -> Payout:
        """Create a new payout."""
        try:
            # Prepare payout data
            payout_data = {
                "id": str(payout.id),
                "payout_number": payout.payout_number.value,
                "restaurant_id": str(payout.restaurant_id),
                "amount": float(payout.amount.amount),
                "currency": payout.amount.currency.value,
                "fees": float(payout.fees.amount) if payout.fees else 0,
                "net_amount": float(payout.net_amount.amount),
                "status": payout.status.value,
                "gateway_payout_id": payout.gateway_payout_id,
                "bank_account_id": payout.bank_account_id,
                "description": payout.description,
                "processed_by": (
                    str(payout.processed_by) if payout.processed_by else None
                ),
                "processed_at": (
                    payout.processed_at.isoformat() if payout.processed_at else None
                ),
            }

            # Insert payout
            result = self._client.table("payouts").insert(payout_data).execute()

            if not result.data:
                raise PayoutCreationError("Failed to create payout")

            # Return created payout
            return self._map_to_payout_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to create payout: {str(e)}")
            raise PayoutCreationError(f"Database error: {str(e)}")

    async def get_payout_by_id(self, payout_id: UUID) -> Optional[Payout]:
        """Get payout by ID."""
        try:
            result = (
                self._client.table("payouts")
                .select("*")
                .eq("id", str(payout_id))
                .execute()
            )

            if not result.data:
                return None

            return self._map_to_payout_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to get payout by ID: {str(e)}")
            return None

    async def get_payouts_by_restaurant(
        self,
        restaurant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[PayoutStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Payout]:
        """Get payouts for a restaurant."""
        try:
            query = (
                self._client.table("payouts")
                .select("*")
                .eq("restaurant_id", str(restaurant_id))
            )

            if status:
                query = query.eq("status", status.value)

            if start_date:
                query = query.gte("created_at", start_date.isoformat())

            if end_date:
                query = query.lte("created_at", end_date.isoformat())

            result = (
                query.order("created_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )

            if not result.data:
                return []

            return [self._map_to_payout_entity(row) for row in result.data]

        except Exception as e:
            logger.error(f"Failed to get payouts by restaurant: {str(e)}")
            return []

    async def update_payout(self, payout: Payout) -> Payout:
        """Update an existing payout."""
        try:
            # Prepare update data
            update_data = {
                "status": payout.status.value,
                "gateway_payout_id": payout.gateway_payout_id,
                "processed_at": (
                    payout.processed_at.isoformat() if payout.processed_at else None
                ),
                "updated_at": datetime.utcnow().replace(tzinfo=None).isoformat() + "Z",
            }

            # Update payout
            result = (
                self._client.table("payouts")
                .update(update_data)
                .eq("id", str(payout.id))
                .execute()
            )

            if not result.data:
                raise PayoutNotFoundError(payout.id)

            # Return updated payout
            return self._map_to_payout_entity(result.data[0])

        except Exception as e:
            logger.error(f"Failed to update payout: {str(e)}")
            raise PayoutUpdateError(f"Database error: {str(e)}", payout.id)

    async def get_payout_summary(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Get payout summary for a restaurant."""
        try:
            params = {
                "p_restaurant_id": str(restaurant_id),
                "p_start_date": start_date.isoformat() if start_date else None,
                "p_end_date": end_date.isoformat() if end_date else None,
            }

            result = self._client.rpc("get_payout_summary", params).execute()

            if not result.data:
                return {}

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to get payout summary: {str(e)}")
            return {}

    def _map_to_payout_entity(self, data: Dict[str, Any]) -> Payout:
        """Map database row to payout entity."""
        return Payout(
            id=UUID(data["id"]),
            restaurant_id=UUID(data["restaurant_id"]),
            amount=Money(Decimal(str(data["amount"])), Currency(data["currency"])),
            fees=(
                Money(Decimal(str(data["fees"])), Currency(data["currency"]))
                if data.get("fees")
                else None
            ),
            net_amount=Money(
                Decimal(str(data["net_amount"])), Currency(data["currency"])
            ),
            status=PayoutStatus(data["status"]),
            gateway_payout_id=data.get("gateway_payout_id"),
            bank_account_id=data.get("bank_account_id"),
            description=data.get("description"),
            processed_by=(
                UUID(data["processed_by"]) if data.get("processed_by") else None
            ),
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                data["updated_at"].replace("Z", "+00:00")
            ),
            processed_at=(
                datetime.fromisoformat(data["processed_at"].replace("Z", "+00:00"))
                if data.get("processed_at")
                else None
            ),
        )
