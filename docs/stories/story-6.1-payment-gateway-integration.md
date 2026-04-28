<!-- Powered by BMAD™ Core -->

# Story 6.1: Indian Payment Gateway Integration (Razorpay)

## Status

- **Status:** Draft - Updated for Indian Market Integration

## Story

**As a** system administrator for an Indian restaurant tech platform,
**I want to** integrate Razorpay payment gateway with comprehensive Indian payment method support,
**so that** customers can pay using UPI, cards, wallets, netbanking, and cash while restaurants receive funds safely with proper GST compliance.

## Acceptance Criteria

### Razorpay Core Integration

1. The system is integrated with Razorpay payment gateway for Indian market operations.
2. Webhook endpoints are set up to handle payment events from Razorpay (payment.captured, payment.failed, etc.).
3. Razorpay API keys and secrets are securely managed for both test and live environments.
4. Razorpay SDK is properly integrated in both backend (Node.js/Python) and frontend (Flutter).

### Indian Payment Methods Support

5. UPI payments are supported with major UPI apps (Google Pay, PhonePe, Paytm, BHIM).
6. Credit and debit card payments support all major Indian banks and international cards.
7. Digital wallet payments support Paytm, Mobikwik, FreeCharge, Ola Money, and Amazon Pay.
8. Net banking integration covers 50+ major Indian banks.
9. Buy Now Pay Later (BNPL) options like Simpl, LazyPay, and ePayLater are available.
10. Cash payment option is integrated as a non-gateway payment method.

### Security & Compliance

11. PCI DSS compliance measures are implemented through Razorpay's secure infrastructure.
12. 3D Secure authentication is enabled for card payments as per RBI guidelines.
13. Payment authorization and capture are handled correctly for Indian regulations.
14. GST compliance features are integrated for proper tax handling and invoicing.

### Business Operations

15. Refunds and partial refunds can be processed through Razorpay dashboard and API.
16. Razorpay Route accounts are set up for restaurants to manage payouts and settlements.
17. Platform fee and commission structure is implemented with proper GST calculations.
18. Multi-currency support for international cards with INR as base currency.
19. Payment retry mechanism is implemented for failed transactions.
20. Razorpay Smart Collect is configured for automated payment reconciliation.

## Tasks / Subtasks

- [ ] **Task 1: Razorpay Core Integration & Security** (AC: #1, #2, #3, #4, #11, #12)

  - [ ] Subtask 1.1: Set up Razorpay API keys and configure backend service with proper environment separation.
  - [ ] Subtask 1.2: Implement comprehensive webhook handler for all Razorpay events (payment, refund, settlement).
  - [ ] Subtask 1.3: Integrate Razorpay SDK in Flutter app with proper error handling and security measures.
  - [ ] Subtask 1.4: Implement 3D Secure authentication flow compliant with RBI guidelines.
  - [ ] Subtask 1.5: Set up secure key management and rotation policies for Razorpay credentials.

- [ ] **Task 2: Comprehensive Indian Payment Methods** (AC: #5, #6, #7, #8, #9, #10)

  - [ ] Subtask 2.1: Integrate UPI payments with support for all major UPI apps and QR code generation.
  - [ ] Subtask 2.2: Configure card payments supporting all Indian banks and international cards.
  - [ ] Subtask 2.3: Set up digital wallet integrations (Paytm, PhonePe, Google Pay, Amazon Pay, etc.).
  - [ ] Subtask 2.4: Implement net banking integration covering 50+ major Indian banks.
  - [ ] Subtask 2.5: Configure BNPL options (Simpl, LazyPay, ePayLater) with proper risk assessment.
  - [ ] Subtask 2.6: Implement cash payment workflow as parallel non-gateway payment method.

- [ ] **Task 3: Payment Processing & Transaction Management** (AC: #13, #15, #18, #19, #20)

  - [ ] Subtask 3.1: Implement payment authorization, capture, and settlement logic.
  - [ ] Subtask 3.2: Build comprehensive refund processing system with partial refund support.
  - [ ] Subtask 3.3: Set up multi-currency support with INR as base currency for international cards.
  - [ ] Subtask 3.4: Implement intelligent payment retry mechanism for failed transactions.
  - [ ] Subtask 3.5: Configure Razorpay Smart Collect for automated payment reconciliation.

- [ ] **Task 4: Restaurant Account Management & Settlements** (AC: #16, #17)

  - [ ] Subtask 4.1: Integrate Razorpay Route for restaurant account management and payouts.
  - [ ] Subtask 4.2: Implement restaurant onboarding flow with KYC compliance for payouts.
  - [ ] Subtask 4.3: Build platform fee calculation system with proper commission structure.
  - [ ] Subtask 4.4: Set up automated settlement schedules and payout management.
  - [ ] Subtask 4.5: Create restaurant dashboard for payment analytics and settlement tracking.

- [ ] **Task 5: GST Compliance & Indian Tax Integration** (AC: #14, #17)
  - [ ] Subtask 5.1: Implement GST calculation engine compliant with Indian tax regulations.
  - [ ] Subtask 5.2: Build GST invoice generation system with proper tax breakdowns.
  - [ ] Subtask 5.3: Integrate platform fee GST calculations with proper tax treatment.
  - [ ] Subtask 5.4: Set up tax reporting and compliance tracking systems.
  - [ ] Subtask 5.5: Create GST-compliant receipt generation for customers and restaurants.

## Dev Notes

This story implements **Razorpay integration for the Indian restaurant tech market**, providing comprehensive payment method support that caters to Indian customer preferences and regulatory requirements. The integration must be **highly secure, compliant, and performant** while supporting the diverse payment ecosystem in India.

### Indian Payment Ecosystem Integration

- **Razorpay Gateway**: Complete integration with India's leading payment gateway supporting 100+ payment methods
- **UPI Dominance**: Special focus on UPI payments which account for 60%+ of digital transactions in India
- **Digital Wallets**: Support for popular Indian wallets with seamless integration
- **Traditional Banking**: Net banking support for customers preferring bank-to-bank transfers
- **BNPL Growth**: Integration with popular Buy Now Pay Later services gaining traction in India
- **Cash Integration**: Parallel cash payment system for customers preferring offline payments

### Security & Compliance Framework

- **RBI Compliance**: Adherence to Reserve Bank of India guidelines for digital payments
- **PCI DSS**: Leveraging Razorpay's PCI DSS Level 1 compliance for secure card processing
- **3D Secure**: Mandatory 3D Secure authentication as per RBI guidelines for card payments
- **Data Localization**: Ensuring payment data storage complies with Indian data protection laws
- **KYC Integration**: Restaurant onboarding with proper Know Your Customer processes
- **Fraud Prevention**: Razorpay's AI-powered fraud detection tailored for Indian market patterns

### Technical Architecture Strategy

- **SDK Integration**: Razorpay SDK integration in both backend APIs and Flutter frontend
- **Webhook Architecture**: Comprehensive webhook handling for all payment lifecycle events
- **State Management**: Proper payment state handling across order lifecycle
- **Error Handling**: Robust error handling for network issues common in Indian infrastructure
- **Retry Logic**: Intelligent retry mechanisms for failed transactions
- **Performance Optimization**: Optimized for varying network conditions across India

### GST & Tax Compliance Integration

- **GST Engine**: Automated GST calculation following Indian tax slabs (5% for restaurant services)
- **Invoice Generation**: GST-compliant invoice generation for B2B and B2C transactions
- **Tax Reporting**: Automated tax reporting and compliance tracking
- **Platform Fee Tax**: Proper GST treatment of platform fees and commissions
- **GSTIN Integration**: Support for restaurant GSTIN registration and validation

### Business Model Implementation

- **Platform Economics**: Commission and platform fee calculation with proper tax treatment
- **Settlement Management**: Automated settlement cycles with configurable payout schedules
- **Multi-tier Pricing**: Support for different commission structures for different restaurant tiers
- **Revenue Sharing**: Transparent revenue sharing between platform, restaurants, and payment gateway
- **Analytics Integration**: Payment analytics for business intelligence and decision making

### Relevant Source Tree Information

- `apps/backend/app/features/payments/razorpay/`: Razorpay API integration and webhook handlers
- `apps/backend/app/features/payments/cash/`: Cash payment workflow integration
- `apps/backend/app/services/gst/`: GST calculation and tax compliance engine
- `apps/frontend/lib/features/payments/razorpay/`: Razorpay Flutter SDK integration
- `apps/frontend/lib/features/payments/cash/`: Cash payment UI and workflow
- `infra/supabase/migrations/`: Payment tables with Indian compliance fields
- `apps/backend/app/features/settlements/`: Restaurant payout and settlement management

### Important Notes from Previous Stories

- **Foundation for Story 6.2**: Customer payment flow will leverage this Razorpay integration
- **Integration with Story 3.3**: Order placement story uses these payment methods
- **Dependency for Story 6.4**: Transaction management builds on this payment infrastructure
- **Restaurant Onboarding**: Integrates with Story 1.1 restaurant setup for payment account creation

### Performance & Scalability Considerations

- **Payment SLA**: Sub-5 second payment processing for optimal user experience
- **Webhook Processing**: Asynchronous webhook processing to handle high transaction volumes
- **Database Optimization**: Efficient payment transaction storage and querying
- **Caching Strategy**: Payment method and fee structure caching for performance
- **Load Balancing**: Proper load distribution for payment processing during peak hours

## Testing

### Relevant Testing Standards

- **Test File Location:**
  - Backend: `apps/backend/tests/features/payments/razorpay/`, `apps/backend/tests/features/payments/gst/`
  - Frontend: `apps/frontend/test/features/payments/razorpay/`
  - Integration: `apps/backend/tests/integration/razorpay_webhooks/`

### Critical Testing Areas

- **Razorpay Payment Methods Testing:**

  - Backend: Test all Indian payment methods (UPI, cards, wallets, netbanking, BNPL)
  - Frontend: Validate payment method selection UI and Razorpay SDK integration
  - Integration: Test end-to-end payment flows for each payment method
  - Performance: Validate payment processing completes within 5-second SLA

- **Webhook & Event Processing:**

  - Backend: Test comprehensive webhook handling for all Razorpay events
  - Integration: Verify payment status synchronization and order updates
  - Security: Test webhook signature verification and replay attack prevention
  - Performance: Validate webhook processing within 10-second SLA

- **GST & Tax Compliance:**

  - Backend: Test GST calculation accuracy for various scenarios
  - Integration: Verify tax-compliant invoice generation
  - Compliance: Test adherence to Indian tax regulations and reporting
  - Database: Validate proper GST record keeping for audits

- **Settlement & Restaurant Payouts:**
  - Backend: Test Razorpay Route integration for restaurant settlements
  - Integration: Verify automated settlement calculations and platform fee deductions
  - Financial: Test payout schedules and reconciliation processes
  - Compliance: Validate KYC and settlement compliance requirements

### Specific Test Scenarios (Indian Market)

1. **UPI Payment Flow**: Customer selects UPI → Razorpay UPI interface → Payment confirmation → Order update
2. **Card Payment with 3D Secure**: Card selection → 3D Secure authentication → Payment success → Settlement
3. **Digital Wallet Payment**: Paytm/PhonePe selection → Wallet authentication → Payment completion → Notification
4. **Net Banking Flow**: Bank selection → Internet banking authentication → Payment confirmation → Order processing
5. **BNPL Payment**: Simpl/LazyPay selection → Credit approval → Deferred payment setup → Order confirmation
6. **Cash Payment Integration**: Cash selection → Order confirmation → Kitchen notification with payment status
7. **Failed Payment Retry**: Payment failure → Error handling → Retry with different method → Success
8. **Webhook Payment Status Update**: Razorpay webhook → Payment status change → Order update → Customer notification
9. **GST Calculation Accuracy**: Various order amounts → Correct 5% GST calculation → Proper invoice generation
10. **International Card Processing**: Foreign card → Currency conversion → INR processing → Settlement in INR
11. **Platform Fee Calculation**: Order completion → Commission calculation → GST on fees → Restaurant payout calculation
12. **Settlement Reconciliation**: Daily settlement → Platform fee deduction → GST compliance → Restaurant account credit
13. **Refund Processing**: Customer refund request → Razorpay refund API → Customer account credit → Tax adjustment
14. **Multi-payment Method Orders**: Customer switches payment methods → Previous attempts handled → Successful completion

### Testing Frameworks and Patterns

- **Backend**: FastAPI test client with Razorpay test API and webhook simulation
- **Frontend**: Flutter widget tests with Razorpay SDK mocking
- **Integration**: End-to-end tests using Razorpay test environment
- **Performance**: Load testing with realistic Indian payment method distribution
- **Security**: Payment security testing including webhook verification and fraud prevention
- **Compliance**: GST calculation verification and Indian tax regulation compliance testing

### Performance Test Requirements (Indian Market)

- **Payment Processing Speed**: 95% of payments complete within 5 seconds
- **UPI Transaction Time**: UPI payments complete within 3 seconds (UPI standard)
- **Webhook Processing**: All webhooks processed within 10 seconds
- **GST Calculation**: Tax computation completes in < 50ms
- **Settlement Processing**: Daily settlements complete within 2 hours
- **High Volume Testing**: System handles 1000+ concurrent payments during festival seasons
- **Network Resilience**: Payment processing works with 2G/3G network conditions common in India

## Change Log

| Date       | Version | Description                                                                                                | Author                   |
| ---------- | ------- | ---------------------------------------------------------------------------------------------------------- | ------------------------ |
| 2025-09-24 | 1.0     | Initial draft of the story.                                                                                | Scrum Master             |
| 2025-09-28 | 2.0     | Complete overhaul for Indian market - Razorpay integration, comprehensive payment methods, GST compliance. | PM + PO + Architect + SM |

## Dev Agent Record

### Agent Model Used

_This section will be populated by the development agent._

### Debug Log References

_This section will be populated by the development agent._

### Completion Notes List

_This section will be populated by the development agent._

### File List

_This section will be populated by the development agent._

## QA Results

_This section will be populated by the QA agent after review._
