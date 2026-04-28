"""Order status management use cases.

This module contains use cases for managing order status,
including status updates and order retrieval operations.
"""

import logging
from typing import Optional
from uuid import UUID

from ...domain.order_entities import Order
from ...domain.order_enums import OrderStatus
from ...domain.order_vos import OrderNumber, PaymentReference
from ...domain.order_repos import IOrderRepository, IOrderAuditRepository
from ...domain.order_exceptions import (
    OrderNotFoundError, InvalidOrderStatusTransitionError,
    OrderAlreadyCancelledException, OrderAlreadyCompletedException
)
from ..order_dtos import (
    UpdateOrderStatusRequestDTO, OrderResponseDTO, 
    order_entity_to_dto
)

logger = logging.getLogger(__name__)


class UpdateOrderStatusUseCase:
    """Use case for updating order status."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        audit_repository: IOrderAuditRepository,
    ):
        """Initialize update order status use case.
        
        Args:
            order_repository: Order repository
            audit_repository: Order audit repository
        """
        self._order_repository = order_repository
        self._audit_repository = audit_repository
    
    async def execute(
        self,
        order_id: UUID,
        request: UpdateOrderStatusRequestDTO,
        changed_by: Optional[UUID] = None,
    ) -> OrderResponseDTO:
        """Update order status.
        
        Args:
            order_id: Order ID
            request: Status update request
            changed_by: User making the change
            
        Returns:
            Updated order DTO
            
        Raises:
            OrderNotFoundError: If order not found
            InvalidOrderStatusTransitionError: If transition invalid
            OrderAlreadyCancelledException: If order already cancelled
            OrderAlreadyCompletedException: If order already completed
        """
        try:
            logger.info(
                "Updating order status",
                extra={
                    "order_id": str(order_id),
                    "new_status": request.new_status.value,
                    "changed_by": str(changed_by) if changed_by else None,
                }
            )
            
            # Get existing order
            order = await self._order_repository.get_by_id(order_id)
            if not order:
                raise OrderNotFoundError(order_id)
            
            # Store previous status for audit
            previous_status = order.order_status
            
            # Update order status (domain validation will occur)
            order.update_order_status(request.new_status)
            
            # Save updated order
            updated_order = await self._order_repository.update_order(order)
            
            # Create audit entry
            await self._audit_repository.create_audit_entry(
                order_id=order_id,
                previous_order_status=previous_status,
                new_order_status=request.new_status,
                previous_payment_status=order.payment_status,
                new_payment_status=order.payment_status,
                changed_by=changed_by,
                change_reason=request.change_reason,
                change_notes=request.change_notes,
            )
            
            logger.info(
                "Order status updated successfully",
                extra={
                    "order_id": str(order_id),
                    "previous_status": previous_status.value,
                    "new_status": request.new_status.value,
                }
            )
            
            return order_entity_to_dto(updated_order)
            
        except (OrderNotFoundError, InvalidOrderStatusTransitionError, 
                OrderAlreadyCancelledException, OrderAlreadyCompletedException):
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(
                "Order status update failed",
                extra={
                    "order_id": str(order_id),
                    "new_status": request.new_status.value,
                    "error": str(e),
                },
                exc_info=True
            )
            raise


class GetOrderUseCase:
    """Use case for retrieving orders by ID."""
    
    def __init__(self, order_repository: IOrderRepository):
        """Initialize get order use case.
        
        Args:
            order_repository: Order repository
        """
        self._order_repository = order_repository
    
    async def execute(self, order_id: UUID) -> OrderResponseDTO:
        """Get order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order DTO
            
        Raises:
            OrderNotFoundError: If order not found
        """
        try:
            logger.info(
                "Getting order by ID",
                extra={"order_id": str(order_id)}
            )
            
            order = await self._order_repository.get_by_id(order_id)
            if not order:
                raise OrderNotFoundError(order_id)
            
            logger.info(
                "Order retrieved successfully",
                extra={
                    "order_id": str(order_id),
                    "order_number": order.order_number.value,
                }
            )
            
            return order_entity_to_dto(order)
            
        except OrderNotFoundError:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(
                "Get order failed",
                extra={
                    "order_id": str(order_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise


class GetOrderByNumberUseCase:
    """Use case for retrieving orders by order number."""
    
    def __init__(self, order_repository: IOrderRepository):
        """Initialize get order by number use case.
        
        Args:
            order_repository: Order repository
        """
        self._order_repository = order_repository
    
    async def execute(self, order_number: str) -> OrderResponseDTO:
        """Get order by order number.
        
        Args:
            order_number: Order number
            
        Returns:
            Order DTO
            
        Raises:
            OrderNotFoundError: If order not found
        """
        try:
            logger.info(
                "Getting order by number",
                extra={"order_number": order_number}
            )
            
            order_number_vo = OrderNumber(order_number)
            order = await self._order_repository.get_by_order_number(order_number_vo)
            if not order:
                raise OrderNotFoundError(order_number=order_number)
            
            logger.info(
                "Order retrieved successfully",
                extra={
                    "order_id": str(order.id),
                    "order_number": order_number,
                }
            )
            
            return order_entity_to_dto(order)
            
        except OrderNotFoundError:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(
                "Get order by number failed",
                extra={
                    "order_number": order_number,
                    "error": str(e),
                },
                exc_info=True
            )
            raise


class GetOrderByPaymentReferenceUseCase:
    """Use case for retrieving orders by payment reference."""
    
    def __init__(self, order_repository: IOrderRepository):
        """Initialize get order by payment reference use case.
        
        Args:
            order_repository: Order repository
        """
        self._order_repository = order_repository
    
    async def execute(self, payment_reference: str) -> OrderResponseDTO:
        """Get order by payment reference.
        
        Args:
            payment_reference: Payment reference
            
        Returns:
            Order DTO
            
        Raises:
            OrderNotFoundError: If order not found
        """
        try:
            logger.info(
                "Getting order by payment reference",
                extra={"payment_reference": payment_reference}
            )
            
            payment_ref_vo = PaymentReference(payment_reference)
            order = await self._order_repository.get_by_payment_reference(payment_ref_vo)
            if not order:
                raise OrderNotFoundError()
            
            logger.info(
                "Order retrieved successfully",
                extra={
                    "order_id": str(order.id),
                    "payment_reference": payment_reference,
                }
            )
            
            return order_entity_to_dto(order)
            
        except OrderNotFoundError:
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(
                "Get order by payment reference failed",
                extra={
                    "payment_reference": payment_reference,
                    "error": str(e),
                },
                exc_info=True
            )
            raise
