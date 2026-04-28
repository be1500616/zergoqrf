"""Order domain entities.

This module contains the core business entities for order management,
including Order, OrderItem, and PaymentCollection entities.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from decimal import Decimal

from .order_enums import OrderStatus, PaymentStatus, PaymentMethod, CancellationReason
from .order_vos import (
    Money, OrderNumber, PaymentReference, CustomerInfo, 
    GSTCalculation, Quantity, PreparationTime, OrderCustomizations
)
from .order_exceptions import (
    InvalidOrderStatusTransitionError, InvalidPaymentStatusTransitionError,
    OrderAlreadyCancelledException, OrderAlreadyCompletedException,
    PaymentAlreadyCollectedError, OrderPreparationNotAllowedError
)


class OrderItem:
    """Order item entity representing individual items in an order."""
    
    def __init__(
        self,
        id: UUID,
        order_id: UUID,
        restaurant_id: UUID,
        menu_item_id: UUID,
        item_name: str,
        base_price: Money,
        quantity: Quantity,
        unit_price: Money,
        total_price: Money,
        item_description: str = None,
        customizations: OrderCustomizations = None,
        special_instructions: str = None,
        is_available: bool = True,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        """Initialize order item.
        
        Args:
            id: Order item ID
            order_id: Parent order ID
            restaurant_id: Restaurant ID
            menu_item_id: Menu item ID
            item_name: Item name (snapshot)
            base_price: Base price of the item
            quantity: Item quantity
            unit_price: Unit price including customizations
            total_price: Total price (unit_price * quantity)
            item_description: Item description
            customizations: Item customizations
            special_instructions: Special instructions for this item
            is_available: Whether item is available
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.order_id = order_id
        self.restaurant_id = restaurant_id
        self.menu_item_id = menu_item_id
        self.item_name = item_name
        self.item_description = item_description
        self.base_price = base_price
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price
        self.customizations = customizations or OrderCustomizations({})
        self.special_instructions = special_instructions
        self.is_available = is_available
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        
        # Validate pricing consistency
        expected_total = self.quantity.multiply_money(self.unit_price)
        if abs(self.total_price.amount - expected_total.amount) > Decimal('0.01'):
            raise ValueError("Total price must equal unit price * quantity")
    
    def update_quantity(self, new_quantity: Quantity) -> None:
        """Update item quantity and recalculate total price."""
        self.quantity = new_quantity
        self.total_price = self.quantity.multiply_money(self.unit_price)
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_unavailable(self) -> None:
        """Mark item as unavailable."""
        self.is_available = False
        self.updated_at = datetime.now(timezone.utc)
    
    def get_customization_summary(self) -> str:
        """Get human-readable customization summary."""
        if not self.customizations or len(self.customizations) == 0:
            return "No customizations"
        
        items = []
        for key, value in self.customizations.customizations.items():
            items.append(f"{key}: {value}")
        
        return ", ".join(items)
    
    def __repr__(self) -> str:
        """Developer representation of order item."""
        return (
            f"OrderItem(id={self.id}, item_name='{self.item_name}', "
            f"quantity={self.quantity.value}, total_price={self.total_price})"
        )


class PaymentCollection:
    """Payment collection entity for tracking cash payments."""
    
    def __init__(
        self,
        id: UUID,
        order_id: UUID,
        payment_reference: PaymentReference,
        amount: Money,
        payment_method: PaymentMethod,
        collected_by: UUID = None,
        collected_at: datetime = None,
        collection_notes: str = None,
        verification_code: str = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        """Initialize payment collection.
        
        Args:
            id: Payment collection ID
            order_id: Order ID
            payment_reference: Payment reference
            amount: Payment amount
            payment_method: Payment method used
            collected_by: Staff member who collected payment
            collected_at: Payment collection timestamp
            collection_notes: Notes about payment collection
            verification_code: Verification code for customer
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.order_id = order_id
        self.payment_reference = payment_reference
        self.amount = amount
        self.payment_method = payment_method
        self.collected_by = collected_by
        self.collected_at = collected_at or datetime.now(timezone.utc)
        self.collection_notes = collection_notes
        self.verification_code = verification_code
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def is_cash_payment(self) -> bool:
        """Check if this is a cash payment."""
        return self.payment_method == PaymentMethod.CASH
    
    def is_digital_payment(self) -> bool:
        """Check if this is a digital payment."""
        return self.payment_method.is_digital()
    
    def get_collection_summary(self) -> str:
        """Get human-readable collection summary."""
        method = self.payment_method.value.title()
        amount = str(self.amount)
        time = self.collected_at.strftime("%Y-%m-%d %H:%M:%S")
        
        return f"{method} payment of {amount} collected at {time}"
    
    def __repr__(self) -> str:
        """Developer representation of payment collection."""
        return (
            f"PaymentCollection(id={self.id}, amount={self.amount}, "
            f"method={self.payment_method.value}, collected_at={self.collected_at})"
        )


class Order:
    """Order aggregate root managing order lifecycle and business rules."""
    
    def __init__(
        self,
        id: UUID,
        order_number: OrderNumber,
        restaurant_id: UUID,
        customer_info: CustomerInfo,
        payment_reference: PaymentReference,
        gst_calculation: GSTCalculation,
        table_id: UUID = None,
        user_id: UUID = None,
        cart_session_id: UUID = None,
        order_status: OrderStatus = OrderStatus.PLACED,
        payment_status: PaymentStatus = PaymentStatus.PAYMENT_PENDING,
        payment_method: PaymentMethod = PaymentMethod.CASH,
        special_instructions: str = None,
        estimated_preparation_time: PreparationTime = None,
        items: List[OrderItem] = None,
        payment_collections: List[PaymentCollection] = None,
        placed_at: datetime = None,
        confirmed_at: datetime = None,
        preparing_at: datetime = None,
        ready_at: datetime = None,
        completed_at: datetime = None,
        cancelled_at: datetime = None,
        payment_collected_at: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        """Initialize order aggregate.
        
        Args:
            id: Order ID
            order_number: Unique order number
            restaurant_id: Restaurant ID
            customer_info: Customer information
            payment_reference: Payment reference for staff
            gst_calculation: GST calculation details
            table_id: Optional table ID
            user_id: Optional user ID (for authenticated customers)
            cart_session_id: Cart session ID (for traceability)
            order_status: Current order status
            payment_status: Current payment status
            payment_method: Payment method
            special_instructions: Order-level special instructions
            estimated_preparation_time: Estimated preparation time
            items: Order items
            payment_collections: Payment collections
            placed_at: Order placement timestamp
            confirmed_at: Order confirmation timestamp
            preparing_at: Preparation start timestamp
            ready_at: Order ready timestamp
            completed_at: Order completion timestamp
            cancelled_at: Order cancellation timestamp
            payment_collected_at: Payment collection timestamp
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = id
        self.order_number = order_number
        self.restaurant_id = restaurant_id
        self.table_id = table_id
        self.user_id = user_id
        self.cart_session_id = cart_session_id
        self.customer_info = customer_info
        self.payment_reference = payment_reference
        self.gst_calculation = gst_calculation
        self.order_status = order_status
        self.payment_status = payment_status
        self.payment_method = payment_method
        self.special_instructions = special_instructions
        self.estimated_preparation_time = estimated_preparation_time or PreparationTime(30)
        self.items = items or []
        self.payment_collections = payment_collections or []
        
        # Status timestamps
        self.placed_at = placed_at or datetime.now(timezone.utc)
        self.confirmed_at = confirmed_at
        self.preparing_at = preparing_at
        self.ready_at = ready_at
        self.completed_at = completed_at
        self.cancelled_at = cancelled_at
        self.payment_collected_at = payment_collected_at
        
        # Audit timestamps
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def add_item(self, item: OrderItem) -> None:
        """Add item to order."""
        if self.is_cancelled():
            raise OrderAlreadyCancelledException(self.id, self.order_number.value)
        
        if self.is_completed():
            raise OrderAlreadyCompletedException(self.id, self.order_number.value)
        
        self.items.append(item)
        self._update_timestamp()
    
    def update_order_status(self, new_status: OrderStatus) -> None:
        """Update order status with validation."""
        if not self.order_status.can_transition_to(new_status):
            raise InvalidOrderStatusTransitionError(
                self.order_status.value, new_status.value, self.id
            )
        
        # Check payment dependency for preparation
        if new_status == OrderStatus.PREPARING and not self.payment_status.allows_order_preparation():
            raise OrderPreparationNotAllowedError(self.id, self.payment_status.value)
        
        self.order_status = new_status
        self._update_status_timestamp(new_status)
        self._update_timestamp()
    
    def update_payment_status(self, new_status: PaymentStatus) -> None:
        """Update payment status with validation."""
        if not self.payment_status.can_transition_to(new_status):
            raise InvalidPaymentStatusTransitionError(
                self.payment_status.value, new_status.value, self.id
            )
        
        self.payment_status = new_status
        
        if new_status == PaymentStatus.PAYMENT_COLLECTED:
            self.payment_collected_at = datetime.now(timezone.utc)
            
            # Auto-transition order to confirmed if still placed
            if self.order_status == OrderStatus.PLACED:
                self.order_status = OrderStatus.CONFIRMED
                self.confirmed_at = datetime.now(timezone.utc)
        
        self._update_timestamp()
    
    def collect_payment(
        self, 
        amount: Money, 
        collected_by: UUID = None, 
        collection_notes: str = None,
        verification_code: str = None
    ) -> PaymentCollection:
        """Collect payment for the order."""
        if self.payment_status == PaymentStatus.PAYMENT_COLLECTED:
            raise PaymentAlreadyCollectedError(self.id, self.payment_reference.value)
        
        # Validate payment amount
        if abs(amount.amount - self.gst_calculation.total_amount.amount) > Decimal('0.01'):
            raise ValueError(f"Payment amount mismatch. Expected: {self.gst_calculation.total_amount}, Received: {amount}")
        
        # Create payment collection record
        payment_collection = PaymentCollection(
            id=uuid4(),
            order_id=self.id,
            payment_reference=self.payment_reference,
            amount=amount,
            payment_method=self.payment_method,
            collected_by=collected_by,
            collection_notes=collection_notes,
            verification_code=verification_code,
        )
        
        self.payment_collections.append(payment_collection)
        self.update_payment_status(PaymentStatus.PAYMENT_COLLECTED)
        
        return payment_collection
    
    def cancel_order(self, reason: CancellationReason, cancelled_by: UUID = None) -> None:
        """Cancel the order."""
        if self.is_cancelled():
            raise OrderAlreadyCancelledException(self.id, self.order_number.value)
        
        if self.is_completed():
            raise OrderAlreadyCompletedException(self.id, self.order_number.value)
        
        self.order_status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now(timezone.utc)
        self._update_timestamp()
    
    def is_active(self) -> bool:
        """Check if order is in active processing state."""
        return self.order_status.is_active()
    
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.order_status == OrderStatus.CANCELLED
    
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return self.order_status == OrderStatus.COMPLETED
    
    def is_payment_pending(self) -> bool:
        """Check if payment is pending."""
        return self.payment_status == PaymentStatus.PAYMENT_PENDING
    
    def is_payment_collected(self) -> bool:
        """Check if payment is collected."""
        return self.payment_status == PaymentStatus.PAYMENT_COLLECTED
    
    def can_start_preparation(self) -> bool:
        """Check if order can start preparation."""
        return (
            self.payment_status.allows_order_preparation() and
            self.order_status in {OrderStatus.CONFIRMED, OrderStatus.PLACED}
        )
    
    def get_total_items_count(self) -> int:
        """Get total number of items in order."""
        return sum(item.quantity.value for item in self.items)
    
    def get_order_summary(self) -> str:
        """Get human-readable order summary."""
        items_count = self.get_total_items_count()
        total_amount = self.gst_calculation.total_amount
        
        return (
            f"Order {self.order_number.value}: {items_count} items, "
            f"Total: {total_amount}, Status: {self.order_status.value.title()}, "
            f"Payment: {self.payment_status.value.replace('_', ' ').title()}"
        )
    
    def _update_status_timestamp(self, status: OrderStatus) -> None:
        """Update appropriate timestamp based on status."""
        now = datetime.now(timezone.utc)
        
        if status == OrderStatus.CONFIRMED:
            self.confirmed_at = now
        elif status == OrderStatus.PREPARING:
            self.preparing_at = now
        elif status == OrderStatus.READY:
            self.ready_at = now
        elif status == OrderStatus.COMPLETED:
            self.completed_at = now
        elif status == OrderStatus.CANCELLED:
            self.cancelled_at = now
    
    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        """Developer representation of order."""
        return (
            f"Order(id={self.id}, order_number={self.order_number.value}, "
            f"status={self.order_status.value}, payment_status={self.payment_status.value}, "
            f"total={self.gst_calculation.total_amount})"
        )
