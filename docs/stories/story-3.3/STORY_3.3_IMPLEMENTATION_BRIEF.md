# Story 3.3 Implementation Brief

## Pay at Restaurant Mode - State Sync & Transition Analysis

**Date:** 28 September 2025  
**Status:** ✅ Ready for Implementation - Restaurant Console Focused  
**Priority:** Critical - MBP Feature  
**Focus:** Pay at Restaurant with Payment-Dependent Order Preparation

---

## 🔄 **STATE TRANSITION ANALYSIS** (Updated Requirements)

### **Key Clarifications from User:**

1. **No Kitchen Concept**: Only restaurant console (kitchen may be added in future)
2. **Payment Dependency**: Order preparation can ONLY start after payment is collected
3. **Bidirectional Sync**: Status changes must reflect to both customer and restaurant
4. **Console-Based Management**: Restaurant manages everything through one interface

---

## 📊 **ORDER & PAYMENT STATUS STATE MACHINES**

### **Order Status Transitions:**

```
placed → [payment_collected] → preparing → ready → completed
   ↓                                          ↓
cancelled ← [anytime before preparing] ← [payment_pending]
```

### **Payment Status Transitions:**

```
payment_pending → payment_collected → [triggers order preparation]
       ↓
payment_failed → [order auto-cancelled]
```

### **Critical State Sync Rules:**

1. **Order Creation**: `order_status = 'placed'` + `payment_status = 'payment_pending'`
2. **Payment Collection**: `payment_status = 'payment_collected'` → Auto-trigger `order_status = 'preparing'`
3. **Preparation Start**: ONLY when `payment_status = 'payment_collected'`
4. **Status Visibility**: Real-time sync to both customer and restaurant console
5. **Cancellation Rules**: Can cancel if `order_status IN ('placed', 'confirmed')` regardless of payment

---

## 🔧 **STATE SYNCHRONIZATION REQUIREMENTS**

### **1. Payment Collection Triggers Order Preparation**

```python
# When restaurant marks payment as collected
if payment_status_change == 'payment_collected':
    order.status = 'preparing'  # Auto-transition
    notify_customer("Payment received, order is being prepared")
    notify_restaurant("Order #123 moved to preparation")
```

### **2. Bidirectional Notification System**

```
Payment Collected → Customer: "Payment confirmed, order preparing"
                 → Restaurant: "Payment received for Order #123"

Order Status Change → Customer: "Order is ready for pickup"
                   → Restaurant: "Order #123 marked as ready"
```

### **3. Restaurant Console State Management**

```
Restaurant Console Shows:
- NEW ORDERS (placed + payment_pending) - Yellow indicator
- PAID ORDERS (placed + payment_collected) - Green indicator
- IN PREPARATION (preparing + payment_collected)
- READY (ready + payment_collected)
- COMPLETED (completed + payment_collected)
```

### **4. Customer-Facing State Visibility**

```
Customer Sees:
- "Order placed, please pay at restaurant" (placed + payment_pending)
- "Payment received, preparing your order" (preparing + payment_collected)
- "Order ready for pickup" (ready + payment_collected)
- "Order completed" (completed + payment_collected)
```

---

## 🚨 **GAPS & ISSUES IDENTIFIED**

### **Critical Gaps to Address:**

1. **State Transition Validation**

   - ❌ Missing: Automatic order status change when payment collected
   - ❌ Missing: Prevention of preparation start without payment
   - ❌ Missing: Bidirectional notification system

2. **Restaurant Console Requirements**

   - ❌ Missing: Single unified interface (no separate kitchen/front-of-house)
   - ❌ Missing: Payment collection + order management in same view
   - ❌ Missing: Real-time status sync between customer and restaurant

3. **Data Consistency Issues**
   - ❌ Missing: Transaction-level state sync (payment + order status)
   - ❌ Missing: Event-driven status propagation
   - ❌ Missing: Rollback mechanisms for failed state transitions

### **Implementation Risks:**

1. **Race Conditions**: Multiple staff marking payment simultaneously
2. **State Inconsistency**: Order status not updating when payment collected
3. **Notification Failures**: Customer/restaurant not getting status updates
4. **Performance Issues**: Real-time sync for 50+ concurrent orders

---

## 🏗️ **REVISED IMPLEMENTATION STRUCTURE**

### **Database Schema Changes Required:**

```sql
-- Add trigger for automatic state transition
CREATE OR REPLACE FUNCTION update_order_status_on_payment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.payment_status = 'payment_collected' AND OLD.payment_status = 'payment_pending' THEN
        UPDATE orders
        SET order_status = 'preparing',
            updated_at = NOW()
        WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payment_collected_trigger
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_order_status_on_payment();
```

### **State Sync Service (New Requirement):**

```python
class OrderPaymentSyncService:
    async def mark_payment_collected(self, order_id: str, staff_id: str):
        async with self.db.transaction():
            # 1. Update payment status
            await self.update_payment_status(order_id, 'payment_collected')

            # 2. Auto-transition order status
            await self.update_order_status(order_id, 'preparing')

            # 3. Notify both customer and restaurant
            await self.notify_customer(order_id, "payment_confirmed")
            await self.notify_restaurant(order_id, "order_ready_for_prep")

            # 4. Update restaurant console in real-time
            await self.broadcast_restaurant_update(order_id)
```

### **Restaurant Console Architecture:**

```
Single Restaurant Console Interface:
├── New Orders Section (payment_pending orders)
├── Payment Collection Interface
├── Orders in Preparation (payment_collected + preparing)
├── Ready Orders (ready status)
└── Completed Orders History
```

---

## 📋 **UPDATED TASK PRIORITIES**

### **Phase 1: Core State Management (Days 1-3)**

1. **Database Schema**: Add payment→order status triggers
2. **State Sync Service**: Bidirectional notification system
3. **Restaurant Console**: Unified interface design

### **Phase 2: Payment-Order Integration (Days 4-6)**

4. **Payment Collection**: Auto-trigger order preparation
5. **Status Validation**: Prevent preparation without payment
6. **Real-time Sync**: Customer ↔ Restaurant status updates

### **Phase 3: Testing & Polish (Days 7-8)**

7. **State Transition Testing**: All status change scenarios
8. **Concurrency Testing**: Multiple staff, multiple orders
9. **Performance Testing**: Real-time sync at scale

---

## ✅ **SUCCESS CRITERIA (Updated)**

### **State Sync Requirements:**

- [ ] Payment collection auto-triggers order preparation
- [ ] Status changes visible to both customer and restaurant within 2 seconds
- [ ] Single restaurant console manages payment + order workflow
- [ ] No order preparation possible without payment collection
- [ ] Bidirectional notifications working for all status changes
- [ ] Transaction-level consistency for payment + order status updates

### **Restaurant Console Features:**

- [ ] Unified interface showing payment status + order status
- [ ] One-click payment collection with automatic order progression
- [ ] Real-time updates without page refresh
- [ ] Clear visual indicators for payment status (yellow/green)
- [ ] Order management from placement to completion

### **Performance & Reliability:**

- [ ] State transitions complete within 200ms
- [ ] Real-time updates handle 50+ concurrent orders
- [ ] Zero data inconsistency in payment/order status
- [ ] Proper error handling and rollback mechanisms

---

## 🎯 **KEY DELIVERABLE SUMMARY**

**A unified restaurant console** where staff can:

1. **See new orders** (with payment pending status)
2. **Collect payments** (one-click mark as collected)
3. **Auto-start preparation** (when payment confirmed)
4. **Track order progress** (through to completion)
5. **Maintain real-time sync** with customer status

**State synchronization ensures:**

- Payment collection immediately enables order preparation
- Customer sees live updates of order status
- Restaurant console reflects all changes in real-time
- No manual coordination needed between payment and preparation

---

**The AI agent now has complete clarity on state transitions and restaurant workflow!** 🎉

_All gaps identified, state sync requirements defined, implementation path clarified._
