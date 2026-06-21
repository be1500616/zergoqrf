# COMPREHENSIVE IMPLEMENTATION PLAN

## Stories 3.3 & 6.1 Multi-Stakeholder Review & Enhancement

**Date:** 28 September 2025  
**Review Team:** Product Manager, Product Owner, Architect, Scrum Master  
**Status:** Implementation Ready

---

## Executive Summary

This document provides a comprehensive multi-stakeholder review of Stories 3.3 (Order Placement) and 6.1 (Payment Gateway Integration) with enhanced alignment, proper subtask organization, and systematic feature development approach. The review addresses the critical requirements for **Order Payment Status Management** and **Razorpay Integration Alignment**.

### Key Deliverables

1. **Enhanced Story 3.3**: Order Placement with comprehensive payment status management
2. **Enhanced Story 6.1**: Payment Gateway integration with restaurant operations
3. **Implementation Plan**: Systematic feature development with proper dependency management
4. **Code Structure**: Clean Architecture compliance with multi-tenant security

---

## Multi-Stakeholder Perspectives

### 🎯 Product Manager Perspective

**Business Value & Market Alignment**

- **Indian Market Focus**: Stories now properly address Indian payment preferences (UPI dominance, cash payments, digital wallets)
- **Revenue Impact**: Clear commission structure and settlement management for sustainable business model
- **Customer Experience**: Seamless payment flow with multiple options reduces cart abandonment
- **Restaurant Operations**: Payment status integration improves kitchen workflow and cash collection efficiency
- **Scalability**: Foundation for advanced features like loyalty programs and promotional discounts

**Key Metrics & KPIs**

- Payment completion rate: Target 95%+
- Order-to-payment cycle time: <5 seconds
- Cash collection efficiency: 90%+ same-day collection
- Customer satisfaction with payment options: 4.5+ rating
- Restaurant payment reconciliation accuracy: 99.9%

### 📋 Product Owner Perspective

**Feature Prioritization & User Stories**

- **Story Dependencies**: Clear dependency chain (3.2 → 3.3 ← 6.1 → 3.4)
- **Acceptance Criteria Enhancement**: Added 25 specific, testable criteria with Indian market considerations
- **User Journey Optimization**: Complete customer flow from cart to confirmation with payment status transparency
- **Restaurant Staff Experience**: Dedicated workflows for cash collection and payment status monitoring
- **Edge Case Coverage**: Payment failures, network issues, webhook processing failures all addressed

**Backlog Management**

- **Critical Path**: Order placement and payment integration must be completed together
- **Risk Mitigation**: Both digital and cash payment paths ensure no customer is left behind
- **Feature Flags**: Progressive rollout capability with fallback to cash-only mode
- **Testing Strategy**: Comprehensive scenarios covering all payment methods and failure modes

### 🏗️ Architect Perspective

**Technical Architecture & System Design**

**Clean Architecture Compliance**

```
Domain Layer (Business Logic)
├── Order (enhanced with payment status)
├── PaymentTransaction (Razorpay integration)
├── PaymentStatus (state machine)
└── Settlement (restaurant payouts)

Application Layer (Use Cases)
├── CreateOrderWithPayment
├── ProcessPaymentWebhook
├── CollectCashPayment
└── UpdatePaymentStatus

Infrastructure Layer (External/Data)
├── RazorpayService (payment gateway)
├── OrderRepository (enhanced schema)
├── PaymentRepository (transaction tracking)
└── NotificationService (alerts)

Presentation Layer (API/UI)
├── OrderController (payment status endpoints)
├── PaymentWebhookController (Razorpay events)
└── RestaurantDashboardController (staff UI)
```

**System Integration Strategy**

- **Database Schema**: Dual status tracking with audit trail
- **API Design**: RESTful endpoints with webhook support
- **Security**: Multi-tenant RLS policies and PCI compliance
- **Performance**: Sub-5 second SLA with caching and optimization
- **Monitoring**: Comprehensive logging and alerting

**Scalability Considerations**

- **Load Balancing**: Payment processing distributed across instances
- **Database Optimization**: Proper indexing and query optimization
- **Caching Strategy**: Payment method and restaurant configuration caching
- **Background Processing**: Webhook handling and settlement processing
- **Error Handling**: Circuit breaker and retry patterns

### 📊 Scrum Master Perspective

**Sprint Planning & Team Coordination**

**Implementation Timeline** (4-5 Sprint Approach)

**Sprint 1: Foundation (5 days)**

- Domain models and value objects
- Database schema migration
- Basic payment status management
- Initial Razorpay integration setup

**Sprint 2: Core Integration (5 days)**

- Order placement with payment integration
- Webhook infrastructure
- Cash payment workflow
- Basic UI enhancements

**Sprint 3: Restaurant Operations (5 days)**

- Staff interfaces for cash collection
- Kitchen display integration
- Payment status reporting
- Settlement basics

**Sprint 4: Advanced Features (5 days)**

- Performance optimization
- Security hardening
- Analytics and reporting
- Comprehensive testing

**Sprint 5: Integration & Polish (5 days)**

- End-to-end testing
- Performance tuning
- Documentation
- Production readiness

**Risk Management**

- **Technical Risks**: Razorpay API changes, webhook reliability
- **Business Risks**: Payment gateway downtime, cash flow impact
- **Mitigation**: Comprehensive testing, fallback mechanisms, monitoring

---

## Detailed Implementation Plan

### Phase 1: Order Payment Status Management

#### 1.1 Database Schema Enhancement

```sql
-- Enhanced orders table with payment tracking
ALTER TABLE orders ADD COLUMN payment_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE orders ADD COLUMN payment_method VARCHAR(50);
ALTER TABLE orders ADD COLUMN payment_id VARCHAR(100);
ALTER TABLE orders ADD COLUMN razorpay_order_id VARCHAR(100);

-- Payment transactions table for audit trail
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    payment_id VARCHAR(100) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(20) NOT NULL,
    gateway_response JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Order payment history for status tracking
CREATE TABLE order_payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    previous_payment_status VARCHAR(20),
    new_payment_status VARCHAR(20) NOT NULL,
    updated_by UUID,
    update_reason VARCHAR(200),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_payment_transactions_order_id ON payment_transactions(order_id);
CREATE INDEX idx_payment_history_order_id ON order_payment_history(order_id);
```

#### 1.2 Domain Models Implementation

```python
# Domain/entities/order.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CASH_PENDING = "cash_pending"
    CASH_COLLECTED = "cash_collected"

class OrderStatus(Enum):
    PAYMENT_PENDING = "payment_pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    RAZORPAY_UPI = "razorpay_upi"
    RAZORPAY_CARD = "razorpay_card"
    RAZORPAY_WALLET = "razorpay_wallet"
    RAZORPAY_NETBANKING = "razorpay_netbanking"
    CASH = "cash"

@dataclass
class PaymentTransaction:
    order_id: str
    payment_id: str
    payment_method: PaymentMethod
    amount: float
    currency: str = "INR"
    status: PaymentStatus = PaymentStatus.PENDING
    gateway_response: Optional[dict] = None
    created_at: datetime = None
    updated_at: datetime = None

class Order:
    def __init__(self, order_data):
        self.id = order_data.get('id')
        self.order_status = OrderStatus(order_data.get('order_status', 'payment_pending'))
        self.payment_status = PaymentStatus(order_data.get('payment_status', 'pending'))
        self.payment_method = PaymentMethod(order_data.get('payment_method')) if order_data.get('payment_method') else None
        # ... other fields

    def can_confirm_order(self) -> bool:
        """Business rule: Order can only be confirmed if payment is secured"""
        return self.payment_status in [PaymentStatus.PAID, PaymentStatus.CASH_PENDING]

    def update_payment_status(self, new_status: PaymentStatus, updated_by: str = None) -> None:
        """Update payment status with validation"""
        if not self._is_valid_payment_transition(self.payment_status, new_status):
            raise ValueError(f"Invalid payment status transition: {self.payment_status} -> {new_status}")

        previous_status = self.payment_status
        self.payment_status = new_status

        # Emit domain event
        self._emit_payment_status_changed_event(previous_status, new_status, updated_by)

        # Auto-update order status based on payment status
        if new_status == PaymentStatus.PAID and self.order_status == OrderStatus.PAYMENT_PENDING:
            self.order_status = OrderStatus.CONFIRMED

    def _is_valid_payment_transition(self, from_status: PaymentStatus, to_status: PaymentStatus) -> bool:
        """Validate payment status state transitions"""
        valid_transitions = {
            PaymentStatus.PENDING: [PaymentStatus.PAID, PaymentStatus.FAILED, PaymentStatus.CASH_PENDING],
            PaymentStatus.CASH_PENDING: [PaymentStatus.CASH_COLLECTED, PaymentStatus.CANCELLED],
            PaymentStatus.PAID: [PaymentStatus.REFUNDED],
            PaymentStatus.FAILED: [PaymentStatus.PAID],  # Retry scenario
            # ... other transitions
        }
        return to_status in valid_transitions.get(from_status, [])
```

#### 1.3 Application Services

```python
# Application/use_cases/create_order_with_payment.py
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class CreateOrderWithPaymentRequest:
    cart_session_id: str
    customer_info: Dict[str, Any]
    payment_method: str
    table_id: str
    restaurant_id: str
    special_instructions: str = ""

class CreateOrderWithPaymentUseCase:
    def __init__(self, order_repo, payment_service, cart_service, notification_service):
        self.order_repo = order_repo
        self.payment_service = payment_service
        self.cart_service = cart_service
        self.notification_service = notification_service

    async def execute(self, request: CreateOrderWithPaymentRequest) -> Dict[str, Any]:
        """Create order with integrated payment processing"""

        # Start database transaction for atomicity
        async with self.order_repo.transaction():
            try:
                # 1. Validate cart session
                cart_session = await self.cart_service.get_cart_session(request.cart_session_id)
                if not cart_session or cart_session.is_expired():
                    raise CartSessionInvalidError("Cart session invalid or expired")

                # 2. Create order from cart data
                order_data = {
                    'cart_session_id': request.cart_session_id,
                    'customer_info': request.customer_info,
                    'payment_method': request.payment_method,
                    'table_id': request.table_id,
                    'restaurant_id': request.restaurant_id,
                    'items': cart_session.items,
                    'subtotal': cart_session.subtotal,
                    'tax_amount': cart_session.tax_amount,
                    'total_amount': cart_session.total_amount,
                    'order_status': OrderStatus.PAYMENT_PENDING,
                    'payment_status': PaymentStatus.PENDING,
                    'special_instructions': request.special_instructions
                }

                order = await self.order_repo.create_order(order_data)

                # 3. Handle payment processing based on method
                if request.payment_method == PaymentMethod.CASH:
                    # Cash orders are immediately confirmed with cash_pending status
                    order.update_payment_status(PaymentStatus.CASH_PENDING)
                    await self.order_repo.update_order(order)

                    # Notify restaurant staff about cash collection
                    await self.notification_service.notify_cash_collection_required(order)

                else:
                    # Digital payments require Razorpay processing
                    payment_response = await self.payment_service.initiate_payment({
                        'order_id': order.id,
                        'amount': order.total_amount,
                        'currency': 'INR',
                        'payment_method': request.payment_method,
                        'customer_info': request.customer_info
                    })

                    # Update order with payment information
                    order.payment_id = payment_response.get('payment_id')
                    order.razorpay_order_id = payment_response.get('razorpay_order_id')
                    await self.order_repo.update_order(order)

                # 4. Clean up cart session
                await self.cart_service.mark_cart_converted(request.cart_session_id)

                # 5. Emit order created event
                await self.notification_service.emit_order_created_event(order)

                return {
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'payment_status': order.payment_status.value,
                    'order_status': order.order_status.value,
                    'payment_details': payment_response if request.payment_method != PaymentMethod.CASH else None,
                    'total_amount': order.total_amount
                }

            except Exception as e:
                # Rollback transaction and cleanup
                await self.order_repo.rollback()
                raise OrderCreationError(f"Failed to create order: {str(e)}")

# Application/use_cases/process_payment_webhook.py
class ProcessPaymentWebhookUseCase:
    def __init__(self, order_repo, payment_repo, notification_service):
        self.order_repo = order_repo
        self.payment_repo = payment_repo
        self.notification_service = notification_service

    async def execute(self, webhook_payload: Dict[str, Any]) -> None:
        """Process Razorpay webhook events"""

        event_type = webhook_payload.get('event')
        payment_data = webhook_payload.get('payload', {}).get('payment', {})

        order_id = self._extract_order_id_from_payment(payment_data)
        if not order_id:
            raise WebhookProcessingError("Could not extract order ID from webhook")

        order = await self.order_repo.get_order_by_id(order_id)
        if not order:
            raise WebhookProcessingError(f"Order not found: {order_id}")

        # Process different webhook events
        if event_type == 'payment.captured':
            await self._handle_payment_success(order, payment_data)
        elif event_type == 'payment.failed':
            await self._handle_payment_failure(order, payment_data)
        elif event_type == 'payment.refunded':
            await self._handle_payment_refund(order, payment_data)

    async def _handle_payment_success(self, order: Order, payment_data: Dict[str, Any]):
        """Handle successful payment confirmation"""

        # Update payment status
        order.update_payment_status(PaymentStatus.PAID)
        await self.order_repo.update_order(order)

        # Create payment transaction record
        payment_transaction = PaymentTransaction(
            order_id=order.id,
            payment_id=payment_data.get('id'),
            payment_method=PaymentMethod(order.payment_method),
            amount=payment_data.get('amount') / 100,  # Razorpay sends amount in paise
            status=PaymentStatus.PAID,
            gateway_response=payment_data
        )
        await self.payment_repo.save_payment_transaction(payment_transaction)

        # Notify restaurant about confirmed order
        await self.notification_service.notify_order_confirmed(order)

        # Notify customer about successful payment
        await self.notification_service.notify_payment_success(order)
```

### Phase 2: Razorpay Integration & Indian Payment Methods

#### 2.1 Razorpay Service Implementation

```python
# Infrastructure/external/razorpay_service.py
import razorpay
from typing import Dict, Any, Optional
import logging
from datetime import datetime

class RazorpayService:
    def __init__(self, key_id: str, key_secret: str):
        self.client = razorpay.Client(auth=(key_id, key_secret))
        self.logger = logging.getLogger(__name__)

    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Razorpay order for payment processing"""

        try:
            razorpay_order = self.client.order.create({
                'amount': int(order_data['amount'] * 100),  # Convert to paise
                'currency': order_data.get('currency', 'INR'),
                'receipt': f"order_{order_data['order_id']}",
                'payment_capture': 1,  # Auto-capture payments
                'notes': {
                    'order_id': order_data['order_id'],
                    'restaurant_id': order_data.get('restaurant_id'),
                    'table_id': order_data.get('table_id')
                }
            })

            self.logger.info(f"Created Razorpay order: {razorpay_order['id']} for order: {order_data['order_id']}")

            return {
                'razorpay_order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': self.client.auth[0],  # Public key for frontend
                'created_at': razorpay_order['created_at']
            }

        except razorpay.errors.RazorpayError as e:
            self.logger.error(f"Razorpay order creation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to create payment order: {str(e)}")

    async def verify_payment_signature(self, payment_data: Dict[str, Any]) -> bool:
        """Verify payment signature for security"""

        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': payment_data['razorpay_order_id'],
                'razorpay_payment_id': payment_data['razorpay_payment_id'],
                'razorpay_signature': payment_data['razorpay_signature']
            })
            return True

        except razorpay.errors.SignatureVerificationError:
            self.logger.warning(f"Invalid payment signature for order: {payment_data.get('razorpay_order_id')}")
            return False

    async def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Fetch payment details from Razorpay"""

        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                'id': payment['id'],
                'amount': payment['amount'] / 100,  # Convert from paise
                'currency': payment['currency'],
                'status': payment['status'],
                'method': payment['method'],
                'description': payment.get('description'),
                'created_at': datetime.fromtimestamp(payment['created_at']),
                'captured_at': datetime.fromtimestamp(payment.get('captured_at', 0)) if payment.get('captured_at') else None
            }

        except razorpay.errors.RazorpayError as e:
            self.logger.error(f"Failed to fetch payment details: {str(e)}")
            raise PaymentGatewayError(f"Failed to get payment details: {str(e)}")

    async def initiate_refund(self, payment_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Initiate refund for a payment"""

        try:
            refund_data = {'payment_id': payment_id}
            if amount:
                refund_data['amount'] = int(amount * 100)  # Convert to paise

            refund = self.client.payment.refund(payment_id, refund_data)

            return {
                'refund_id': refund['id'],
                'amount': refund['amount'] / 100,
                'currency': refund['currency'],
                'status': refund['status'],
                'created_at': datetime.fromtimestamp(refund['created_at'])
            }

        except razorpay.errors.RazorpayError as e:
            self.logger.error(f"Refund initiation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to initiate refund: {str(e)}")

# Infrastructure/external/webhook_handler.py
class RazorpayWebhookHandler:
    def __init__(self, webhook_secret: str, payment_service: RazorpayService):
        self.webhook_secret = webhook_secret
        self.payment_service = payment_service
        self.logger = logging.getLogger(__name__)

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature for security"""

        import hmac
        import hashlib

        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    async def process_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Process incoming webhook from Razorpay"""

        # Verify signature first
        if not self.verify_webhook_signature(payload, signature):
            raise WebhookSecurityError("Invalid webhook signature")

        # Parse payload
        import json
        webhook_data = json.loads(payload.decode('utf-8'))

        event_type = webhook_data.get('event')
        self.logger.info(f"Processing webhook event: {event_type}")

        # Route to appropriate handler
        if event_type.startswith('payment.'):
            return await self._handle_payment_event(webhook_data)
        elif event_type.startswith('refund.'):
            return await self._handle_refund_event(webhook_data)
        else:
            self.logger.warning(f"Unhandled webhook event: {event_type}")
            return {'status': 'ignored', 'event': event_type}

    async def _handle_payment_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment-related webhook events"""

        event_type = webhook_data['event']
        payment_data = webhook_data['payload']['payment']

        # Extract order information
        order_receipt = payment_data.get('notes', {}).get('order_id')
        if not order_receipt:
            raise WebhookProcessingError("No order ID found in webhook payload")

        # Process based on event type
        if event_type == 'payment.captured':
            await self._update_payment_status(order_receipt, 'paid', payment_data)
        elif event_type == 'payment.failed':
            await self._update_payment_status(order_receipt, 'failed', payment_data)
        elif event_type == 'payment.authorized':
            await self._update_payment_status(order_receipt, 'authorized', payment_data)

        return {'status': 'processed', 'event': event_type, 'order_id': order_receipt}
```

### Phase 3: Restaurant Operations Integration

#### 3.1 Kitchen Display Integration

```python
# Infrastructure/services/kitchen_display_service.py
class KitchenDisplayService:
    def __init__(self, websocket_manager, order_repo):
        self.websocket_manager = websocket_manager
        self.order_repo = order_repo

    async def broadcast_order_update(self, order: Order):
        """Broadcast order updates to kitchen displays"""

        kitchen_data = {
            'order_id': order.id,
            'order_number': order.order_number,
            'order_status': order.order_status.value,
            'payment_status': order.payment_status.value,
            'payment_method': order.payment_method.value if order.payment_method else None,
            'items': order.items,
            'total_amount': order.total_amount,
            'special_instructions': order.special_instructions,
            'created_at': order.created_at.isoformat(),
            'payment_indicator': self._get_payment_indicator(order)
        }

        # Broadcast to all kitchen displays for this restaurant
        await self.websocket_manager.broadcast_to_restaurant(
            restaurant_id=order.restaurant_id,
            message_type='order_update',
            data=kitchen_data
        )

    def _get_payment_indicator(self, order: Order) -> Dict[str, Any]:
        """Generate payment status indicator for kitchen display"""

        if order.payment_status == PaymentStatus.PAID:
            return {
                'color': 'green',
                'icon': 'check_circle',
                'text': 'PAID',
                'priority': 'normal'
            }
        elif order.payment_status == PaymentStatus.CASH_PENDING:
            return {
                'color': 'yellow',
                'icon': 'payments',
                'text': 'CASH COLLECTION REQUIRED',
                'priority': 'attention'
            }
        elif order.payment_status == PaymentStatus.FAILED:
            return {
                'color': 'red',
                'icon': 'error',
                'text': 'PAYMENT FAILED',
                'priority': 'hold'
            }
        else:
            return {
                'color': 'blue',
                'icon': 'hourglass_empty',
                'text': 'PAYMENT PENDING',
                'priority': 'hold'
            }

# Presentation/controllers/restaurant_controller.py
class RestaurantController:
    def __init__(self, order_service, payment_service):
        self.order_service = order_service
        self.payment_service = payment_service

    @router.post("/restaurants/{restaurant_id}/orders/{order_id}/collect-cash")
    async def collect_cash_payment(
        self,
        restaurant_id: str,
        order_id: str,
        staff_id: str = Depends(get_current_staff)
    ):
        """Mark cash payment as collected by restaurant staff"""

        try:
            order = await self.order_service.get_order_by_id(order_id)

            # Validate order belongs to restaurant
            if order.restaurant_id != restaurant_id:
                raise HTTPException(status_code=403, detail="Order not found")

            # Validate payment method is cash and status is cash_pending
            if order.payment_method != PaymentMethod.CASH:
                raise HTTPException(status_code=400, detail="Order is not a cash payment")

            if order.payment_status != PaymentStatus.CASH_PENDING:
                raise HTTPException(status_code=400, detail="Cash payment not in pending state")

            # Update payment status
            await self.order_service.mark_cash_payment_collected(
                order_id=order_id,
                collected_by=staff_id
            )

            return {
                'message': 'Cash payment marked as collected',
                'order_id': order_id,
                'payment_status': 'cash_collected',
                'collected_by': staff_id,
                'collected_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/restaurants/{restaurant_id}/payment-dashboard")
    async def get_payment_dashboard(
        self,
        restaurant_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ):
        """Get payment status dashboard for restaurant"""

        dashboard_data = await self.payment_service.get_restaurant_payment_dashboard(
            restaurant_id=restaurant_id,
            date_from=date_from,
            date_to=date_to
        )

        return dashboard_data

# Application/use_cases/collect_cash_payment.py
class CollectCashPaymentUseCase:
    def __init__(self, order_repo, notification_service, kitchen_service):
        self.order_repo = order_repo
        self.notification_service = notification_service
        self.kitchen_service = kitchen_service

    async def execute(self, order_id: str, collected_by: str) -> Dict[str, Any]:
        """Mark cash payment as collected"""

        order = await self.order_repo.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order not found: {order_id}")

        # Validate cash payment can be collected
        if order.payment_method != PaymentMethod.CASH:
            raise InvalidOperationError("Order is not a cash payment")

        if order.payment_status != PaymentStatus.CASH_PENDING:
            raise InvalidOperationError("Cash payment is not in pending state")

        # Update payment status
        order.update_payment_status(PaymentStatus.CASH_COLLECTED, collected_by)
        await self.order_repo.update_order(order)

        # Update kitchen displays
        await self.kitchen_service.broadcast_order_update(order)

        # Notify customer about payment confirmation
        await self.notification_service.notify_payment_confirmed(order)

        return {
            'order_id': order_id,
            'payment_status': PaymentStatus.CASH_COLLECTED.value,
            'collected_by': collected_by,
            'collected_at': datetime.utcnow()
        }
```

---

## Testing Strategy

### Comprehensive Testing Approach

#### Unit Testing

- Domain models and business logic validation
- Payment status state transitions
- Order creation workflows
- Razorpay service integration

#### Integration Testing

- Order-payment synchronization
- Webhook processing end-to-end
- Kitchen display integration
- Restaurant staff workflows

#### Performance Testing

- Payment processing under load
- Webhook handling performance
- Database query optimization
- Concurrent order creation

#### Security Testing

- Payment data encryption
- Webhook signature verification
- Multi-tenant data isolation
- PCI compliance validation

---

## Success Metrics & Monitoring

### Key Performance Indicators

**Technical Metrics**

- Payment processing latency: <5 seconds (95th percentile)
- Order creation success rate: >99.5%
- Webhook processing time: <10 seconds
- Database query performance: <200ms

**Business Metrics**

- Payment completion rate: >95%
- Cash collection efficiency: >90% same-day
- Customer satisfaction: >4.5/5
- Restaurant staff efficiency: 20% improvement in order processing

**Operational Metrics**

- System uptime: >99.9%
- Payment gateway availability: >99.5%
- Error rate: <0.1%
- Support ticket volume: <5% of total orders

### Monitoring & Alerting

```python
# Infrastructure/monitoring/payment_monitor.py
class PaymentSystemMonitor:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerting = AlertingService()

    async def track_payment_processing(self, order_id: str, duration: float, success: bool):
        """Track payment processing metrics"""

        self.metrics.record_histogram('payment_processing_duration', duration)
        self.metrics.increment_counter('payment_attempts_total')

        if success:
            self.metrics.increment_counter('payment_success_total')
        else:
            self.metrics.increment_counter('payment_failure_total')
            # Alert on high failure rate
            await self.alerting.check_failure_rate_threshold()

    async def track_webhook_processing(self, event_type: str, processing_time: float):
        """Track webhook processing performance"""

        self.metrics.record_histogram('webhook_processing_duration', processing_time,
                                    labels={'event_type': event_type})

        # Alert if webhook processing is slow
        if processing_time > 30:  # 30 seconds threshold
            await self.alerting.webhook_processing_slow_alert(event_type, processing_time)
```

---

## Conclusion

This comprehensive implementation plan addresses all requirements for **Order Payment Status Management** and **Razorpay Integration** with proper alignment between Stories 3.3 and 6.1. The enhanced stories now include:

1. **Systematic Feature Development**: Clear task breakdown with proper dependencies
2. **Clean Architecture Compliance**: Domain-driven design with proper layer separation
3. **Multi-tenant Security**: Row Level Security policies and data isolation
4. **Performance Optimization**: Sub-5 second SLA with monitoring and alerting
5. **Restaurant Operations**: Complete staff workflow integration
6. **Comprehensive Testing**: Unit, integration, performance, and security testing

The implementation follows the established patterns from the cart management system while introducing robust payment status management that integrates seamlessly with the existing architecture. The plan ensures scalability, maintainability, and compliance with Indian market requirements while providing a foundation for future enhancements.

**Next Steps:**

1. Review and approve enhanced stories
2. Begin Sprint 1 implementation
3. Set up monitoring and alerting infrastructure
4. Establish testing environments with Razorpay test credentials
5. Coordinate with stakeholders for UAT planning

---

_This document serves as the master plan for implementing comprehensive order payment status management with full stakeholder alignment and technical excellence._
