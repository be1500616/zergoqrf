"""Order creation use cases.

This module contains use cases for creating orders from cart sessions,
implementing the cart-to-order conversion workflow.
"""

import logging
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from ...domain.order_entities import Order, OrderItem
from ...domain.order_enums import OrderStatus, PaymentStatus, PaymentMethod
from ...domain.order_vos import (
    Money, OrderNumber, PaymentReference, CustomerInfo, 
    GSTCalculation, Quantity, PreparationTime, OrderCustomizations
)
from ...domain.order_repos import IOrderRepository, IOrderItemRepository
from ...domain.order_exceptions import (
    CartSessionNotFoundError, CartSessionExpiredError, EmptyCartError,
    OrderCreationError, InvalidCustomerInfoError
)
from ..order_dtos import CreateOrderRequestDTO, OrderResponseDTO, order_entity_to_dto

# Import cart domain for integration
from ....cart.domain.cart_repos import ICartSessionRepository, ICartItemRepository
from ....cart.domain.cart_vos import CartSessionToken

logger = logging.getLogger(__name__)


class CreateOrderFromCartUseCase:
    """Use case for creating orders from cart sessions."""
    
    def __init__(
        self,
        order_repository: IOrderRepository,
        order_item_repository: IOrderItemRepository,
        cart_session_repository: ICartSessionRepository,
        cart_item_repository: ICartItemRepository,
    ):
        """Initialize create order use case.
        
        Args:
            order_repository: Order repository
            order_item_repository: Order item repository
            cart_session_repository: Cart session repository
            cart_item_repository: Cart item repository
        """
        self._order_repository = order_repository
        self._order_item_repository = order_item_repository
        self._cart_session_repository = cart_session_repository
        self._cart_item_repository = cart_item_repository
    
    async def execute(
        self, 
        request: CreateOrderRequestDTO,
        user_id: Optional[UUID] = None
    ) -> OrderResponseDTO:
        """Create order from cart session.
        
        Args:
            request: Order creation request
            user_id: Optional authenticated user ID
            
        Returns:
            Created order DTO
            
        Raises:
            CartSessionNotFoundError: If cart session not found
            CartSessionExpiredError: If cart session expired
            EmptyCartError: If cart is empty
            InvalidCustomerInfoError: If customer info is invalid
            OrderCreationError: If order creation fails
        """
        try:
            logger.info(
                "Creating order from cart session",
                extra={
                    "cart_session_id": str(request.cart_session_id),
                    "customer_name": request.customer_info.name,
                    "user_id": str(user_id) if user_id else None,
                }
            )
            
            # Get and validate cart session
            cart_session = await self._cart_session_repository.get_by_id(request.cart_session_id)
            if not cart_session:
                raise CartSessionNotFoundError(request.cart_session_id)
            
            if not cart_session.is_valid():
                raise CartSessionExpiredError(request.cart_session_id)
            
            # Get cart items
            cart_items = await self._cart_item_repository.get_items_by_session(request.cart_session_id)
            if not cart_items:
                raise EmptyCartError(request.cart_session_id)
            
            # Validate customer information
            customer_info = self._create_customer_info(request.customer_info)
            
            # Calculate order totals
            subtotal = Money(sum(item.total_price.amount for item in cart_items))
            gst_calculation = GSTCalculation.calculate(subtotal)
            
            # Generate order identifiers
            order_id = uuid4()
            order_number = await self._generate_order_number()
            payment_reference = self._generate_payment_reference()
            
            # Create order entity
            order = Order(
                id=order_id,
                order_number=order_number,
                restaurant_id=cart_session.restaurant_id,
                table_id=request.table_id or cart_session.table_id,
                user_id=user_id,
                cart_session_id=request.cart_session_id,
                customer_info=customer_info,
                payment_reference=payment_reference,
                gst_calculation=gst_calculation,
                order_status=OrderStatus.PLACED,
                payment_status=PaymentStatus.PAYMENT_PENDING,
                payment_method=PaymentMethod.CASH,
                special_instructions=request.special_instructions,
                estimated_preparation_time=self._calculate_preparation_time(cart_items),
            )
            
            # Create order items
            order_items = []
            for cart_item in cart_items:
                order_item = OrderItem(
                    id=uuid4(),
                    order_id=order_id,
                    restaurant_id=cart_item.restaurant_id,
                    menu_item_id=cart_item.menu_item_id,
                    item_name=cart_item.item_name,
                    item_description=cart_item.item_description,
                    base_price=cart_item.base_price,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    total_price=cart_item.total_price,
                    customizations=OrderCustomizations(cart_item.customizations.customizations),
                    special_instructions=cart_item.special_instructions,
                )
                order_items.append(order_item)
            
            order.items = order_items
            
            # Save order and items atomically
            created_order = await self._order_repository.create_order(order)
            
            # Mark cart session as converted (deactivate)
            cart_session.is_active = False
            await self._cart_session_repository.update_session(cart_session)
            
            logger.info(
                "Order created successfully",
                extra={
                    "order_id": str(created_order.id),
                    "order_number": created_order.order_number.value,
                    "total_amount": str(created_order.gst_calculation.total_amount.amount),
                    "items_count": len(created_order.items),
                }
            )
            
            return order_entity_to_dto(created_order)
            
        except (CartSessionNotFoundError, CartSessionExpiredError, EmptyCartError, InvalidCustomerInfoError):
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(
                "Order creation failed",
                extra={
                    "cart_session_id": str(request.cart_session_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise OrderCreationError(f"Failed to create order: {str(e)}", request.cart_session_id)
    
    def _create_customer_info(self, customer_request) -> CustomerInfo:
        """Create customer info value object with validation."""
        try:
            return CustomerInfo(
                name=customer_request.name.strip(),
                phone=customer_request.phone,
                email=customer_request.email.strip() if customer_request.email else None,
            )
        except ValueError as e:
            raise InvalidCustomerInfoError("customer_info", customer_request.dict(), str(e))
    
    async def _generate_order_number(self) -> OrderNumber:
        """Generate unique order number."""
        # This would typically call a database function or service
        # For now, we'll use a simple format
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Get count of orders today (simplified)
        # In real implementation, this would be atomic
        counter = 1  # This should be fetched from database
        
        order_number_str = f"ORD-{date_str}-{counter:04d}"
        return OrderNumber(order_number_str)
    
    def _generate_payment_reference(self) -> PaymentReference:
        """Generate unique payment reference."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        import random
        suffix = f"{random.randint(100, 999):03d}"
        
        payment_ref_str = f"PAY-{timestamp}-{suffix}"
        return PaymentReference(payment_ref_str)
    
    def _calculate_preparation_time(self, cart_items) -> PreparationTime:
        """Calculate estimated preparation time based on cart items."""
        # Simple calculation: base time + (items * 5 minutes)
        base_time = 20  # 20 minutes base
        item_time = len(cart_items) * 5  # 5 minutes per item
        
        total_time = min(base_time + item_time, 120)  # Max 2 hours
        return PreparationTime(total_time)
