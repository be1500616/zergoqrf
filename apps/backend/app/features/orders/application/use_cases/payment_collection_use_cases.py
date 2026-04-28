"""Payment collection use cases.

This module contains use cases for collecting payments and managing
payment collection operations for cash payments.
"""

import logging
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from ...domain.order_entities import Order, PaymentCollection
from ...domain.order_enums import PaymentStatus
from ...domain.order_vos import Money, PaymentReference
from ...domain.order_repos import IOrderRepository, IPaymentCollectionRepository, IOrderAuditRepository
from ...domain.order_exceptions import (
    OrderNotFoundError, PaymentReferenceNotFoundError, PaymentAlreadyCollectedError,
    PaymentAmountMismatchError
)
from ..order_dtos import (
    CollectPaymentRequestDTO, OrderResponseDTO, PaymentCollectionResponseDTO,
    order_entity_to_dto, payment_collection_entity_to_dto
)

logger = logging.getLogger(__name__)


class CollectPaymentUseCase:
    """Use case for collecting cash payments."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        payment_collection_repository: IPaymentCollectionRepository,
        audit_repository: IOrderAuditRepository,
    ):
        """Initialize collect payment use case.
        
        Args:
            order_repository: Order repository
            payment_collection_repository: Payment collection repository
            audit_repository: Order audit repository
        """
        self._order_repository = order_repository
        self._payment_collection_repository = payment_collection_repository
        self._audit_repository = audit_repository
    
    async def execute(
        self,
        order_id: UUID,
        request: CollectPaymentRequestDTO,
        collected_by: Optional[UUID] = None,
    ) -> OrderResponseDTO:
        """Collect payment for an order.
        
        Args:
            order_id: Order ID
            request: Payment collection request
            collected_by: Staff member collecting payment
            
        Returns:
            Updated order DTO
            
        Raises:
            OrderNotFoundError: If order not found
            PaymentReferenceNotFoundError: If payment reference doesn't match
            PaymentAlreadyCollectedError: If payment already collected
            PaymentAmountMismatchError: If payment amount doesn't match
        """
        try:
            logger.info(
                "Collecting payment",
                extra={
                    "order_id": str(order_id),
                    "payment_reference": request.payment_reference,
                    "amount": str(request.amount),
                    "collected_by": str(collected_by) if collected_by else None,
                }
            )
            
            # Get order and validate payment reference
            order = await self._order_repository.get_by_id(order_id)
            if not order:
                raise OrderNotFoundError(order_id)
            
            if order.payment_reference.value != request.payment_reference:
                raise PaymentReferenceNotFoundError(request.payment_reference)
            
            # Check if payment already collected
            if order.payment_status == PaymentStatus.PAYMENT_COLLECTED:
                raise PaymentAlreadyCollectedError(order_id, request.payment_reference)
            
            # Validate payment amount
            expected_amount = order.gst_calculation.total_amount.amount
            if abs(request.amount - expected_amount) > Decimal('0.01'):
                raise PaymentAmountMismatchError(
                    float(expected_amount), 
                    float(request.amount), 
                    order_id
                )
            
            # Store previous payment status for audit
            previous_payment_status = order.payment_status
            previous_order_status = order.order_status
            
            # Collect payment (domain logic handles status transitions)
            payment_amount = Money(request.amount)
            payment_collection = order.collect_payment(
                amount=payment_amount,
                collected_by=collected_by,
                collection_notes=request.collection_notes,
                verification_code=request.verification_code,
            )
            
            # Save payment collection
            await self._payment_collection_repository.create_collection(payment_collection)
            
            # Update order
            updated_order = await self._order_repository.update_order(order)
            
            # Create audit entry
            await self._audit_repository.create_audit_entry(
                order_id=order_id,
                previous_order_status=previous_order_status,
                new_order_status=order.order_status,
                previous_payment_status=previous_payment_status,
                new_payment_status=order.payment_status,
                changed_by=collected_by,
                change_reason="Payment collected",
                change_notes=request.collection_notes,
            )
            
            logger.info(
                "Payment collected successfully",
                extra={
                    "order_id": str(order_id),
                    "payment_collection_id": str(payment_collection.id),
                    "amount": str(request.amount),
                    "new_order_status": order.order_status.value,
                    "new_payment_status": order.payment_status.value,
                }
            )
            
            return order_entity_to_dto(updated_order)
            
        except (OrderNotFoundError, PaymentReferenceNotFoundError, 
                PaymentAlreadyCollectedError, PaymentAmountMismatchError):
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(
                "Payment collection failed",
                extra={
                    "order_id": str(order_id),
                    "payment_reference": request.payment_reference,
                    "error": str(e),
                },
                exc_info=True
            )
            raise


class GetPaymentCollectionsUseCase:
    """Use case for retrieving payment collections."""
    
    def __init__(self, payment_collection_repository: IPaymentCollectionRepository):
        """Initialize get payment collections use case.
        
        Args:
            payment_collection_repository: Payment collection repository
        """
        self._payment_collection_repository = payment_collection_repository
    
    async def execute_by_order(self, order_id: UUID) -> List[PaymentCollectionResponseDTO]:
        """Get payment collections for an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            List of payment collection DTOs
        """
        try:
            logger.info(
                "Getting payment collections for order",
                extra={"order_id": str(order_id)}
            )
            
            collections = await self._payment_collection_repository.get_by_order(order_id)
            
            logger.info(
                "Payment collections retrieved successfully",
                extra={
                    "order_id": str(order_id),
                    "collections_count": len(collections),
                }
            )
            
            return [payment_collection_entity_to_dto(collection) for collection in collections]
            
        except Exception as e:
            logger.error(
                "Get payment collections failed",
                extra={
                    "order_id": str(order_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise
    
    async def execute_by_payment_reference(
        self, 
        payment_reference: str
    ) -> List[PaymentCollectionResponseDTO]:
        """Get payment collections by payment reference.
        
        Args:
            payment_reference: Payment reference
            
        Returns:
            List of payment collection DTOs
        """
        try:
            logger.info(
                "Getting payment collections by reference",
                extra={"payment_reference": payment_reference}
            )
            
            payment_ref_vo = PaymentReference(payment_reference)
            collections = await self._payment_collection_repository.get_by_payment_reference(payment_ref_vo)
            
            logger.info(
                "Payment collections retrieved successfully",
                extra={
                    "payment_reference": payment_reference,
                    "collections_count": len(collections),
                }
            )
            
            return [payment_collection_entity_to_dto(collection) for collection in collections]
            
        except Exception as e:
            logger.error(
                "Get payment collections by reference failed",
                extra={
                    "payment_reference": payment_reference,
                    "error": str(e),
                },
                exc_info=True
            )
            raise
    
    async def execute_by_staff(
        self, 
        staff_id: UUID,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[PaymentCollectionResponseDTO]:
        """Get payment collections by staff member.
        
        Args:
            staff_id: Staff member ID
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            
        Returns:
            List of payment collection DTOs
        """
        try:
            logger.info(
                "Getting payment collections by staff",
                extra={
                    "staff_id": str(staff_id),
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
            
            # Parse dates if provided
            start_datetime = None
            end_datetime = None
            
            if start_date:
                from datetime import datetime
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            
            if end_date:
                from datetime import datetime
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            collections = await self._payment_collection_repository.get_collections_by_staff(
                staff_id=staff_id,
                start_date=start_datetime,
                end_date=end_datetime,
            )
            
            logger.info(
                "Payment collections retrieved successfully",
                extra={
                    "staff_id": str(staff_id),
                    "collections_count": len(collections),
                }
            )
            
            return [payment_collection_entity_to_dto(collection) for collection in collections]
            
        except Exception as e:
            logger.error(
                "Get payment collections by staff failed",
                extra={
                    "staff_id": str(staff_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise
