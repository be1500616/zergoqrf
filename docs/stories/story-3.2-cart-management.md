<!-- Powered by BMAD™ Core -->

# Story 3.2: Cart Management & Session Security

## Status

- **Status:** Approved

## Story

**As a** dining customer,
**I want to** add items to my cart and manage my order across both anonymous and authenticated states,
**so that** I can build my meal selection before placing the order, with seamless transition if I choose to sign in.

## Acceptance Criteria

### Core Cart Functionality

1. An "Add to Cart" button creates a cart session if one does not exist (anonymous initially).
2. Items are added to the cart with the selected quantity and customizations.
3. The cart persists as the user navigates through the menu and survives app refreshes.
4. Item quantities can be modified, and items can be removed from the cart.
5. The running total updates automatically with each change.
6. Price calculations accurately reflect the base price, customizations, quantity, and taxes.
7. A mini-cart view is visible during menu browsing showing item count and total.
8. A full cart page is accessible to review the order before placement.

### Session Management & Security

9. Anonymous sessions are valid for 2 hours and extend with cart activity.
10. Cart data is securely isolated per session (anonymous sessions cannot access each other's data).
11. When a user signs in via Supabase Auth, their anonymous cart seamlessly migrates to their authenticated session.
12. Authenticated users can access their cart across devices and sessions.
13. Cart sessions integrate properly with the existing Supabase Auth system (Direct-to-Supabase approach).

### Data Persistence & State Management

14. Cart data is persisted in the backend database, not just frontend state.
15. Cart state synchronizes between frontend and backend for consistency.
16. Expired cart sessions are automatically cleaned up by background processes.

### Business Rules & Constraints (MVP)

17. Maximum 50 items per cart to prevent abuse and ensure reasonable order sizes.
18. Cart auto-expires after 2 hours of inactivity to manage system resources.
19. Real-time price validation ensures cart totals reflect current menu pricing.
20. Clear user feedback for all cart operations (loading states, success/error messages).

### Performance Requirements (MVP)

21. Cart operations (add/remove/update) complete within 3 seconds under normal conditions.
22. System supports 100+ concurrent cart sessions during peak restaurant hours.
23. Cart data loads within 2 seconds when user returns to the application.

## Tasks / Subtasks

- [ ] **Task 1: Database Schema & Migration** (AC: #10, #14, #16)

  - [ ] Subtask 1.1: Create `cart_sessions` table to unify anonymous and authenticated session management.
  - [ ] Subtask 1.2: Create `cart_items` table for persistent cart storage with proper RLS policies.
  - [ ] Subtask 1.3: Implement database functions for cart session creation, validation, and migration.
  - [ ] Subtask 1.4: Create cleanup functions for expired cart sessions and items.

- [ ] **Task 2: Backend Cart API** (AC: #1, #2, #4, #6, #11, #13, #15)

  - [ ] Subtask 2.1: Implement cart session management endpoints (create anonymous, create authenticated, migrate).
  - [ ] Subtask 2.2: Develop cart item CRUD endpoints (add, update quantity, remove, list).
  - [ ] Subtask 2.3: Create cart summary endpoint with real-time totals and item counts.
  - [ ] Subtask 2.4: Implement session validation middleware that works with both anonymous tokens and Supabase JWT.
  - [ ] Subtask 2.5: Build cart migration endpoint for anonymous-to-authenticated transition.

- [ ] **Task 3: Price Calculation Engine** (AC: #6, #8)

  - [ ] Subtask 3.1: Create backend service for accurate cart total calculation including taxes and customizations.
  - [ ] Subtask 3.2: Implement real-time price updates when items or quantities change.
  - [ ] Subtask 3.3: Handle pricing edge cases (item price changes, discontinued items, promotions).

- [ ] **Task 4: Frontend Integration** (AC: #3, #7, #8, #12, #15)

  - [ ] Subtask 4.1: Enhance existing CartController to work with backend API instead of local state only.
  - [ ] Subtask 4.2: Implement session management in Flutter (anonymous session creation, Supabase auth integration).
  - [ ] Subtask 4.3: Build cart synchronization logic to keep frontend and backend in sync.
  - [ ] Subtask 4.4: Handle cart migration during sign-in process seamlessly.

- [ ] **Task 5: UI/UX Implementation** (AC: #7, #8, #20)

  - [ ] Subtask 5.1: Design and implement mini-cart component with item count and total display.
  - [ ] Subtask 5.2: Build full cart page with item management (quantity changes, removal, customization display).
  - [ ] Subtask 5.3: Implement comprehensive loading states, success confirmations, and error messaging.
  - [ ] Subtask 5.4: Add cart persistence indicators and session status display for users.
  - [ ] Subtask 5.5: Implement cart size limits UI (show remaining capacity out of 50 items).

- [ ] **Task 6: Business Rules & Validation** (AC: #17, #18, #19, #21, #22, #23)
  - [ ] Subtask 6.1: Implement cart size validation (maximum 50 items) with user-friendly messaging.
  - [ ] Subtask 6.2: Build session timeout logic with activity tracking and renewal.
  - [ ] Subtask 6.3: Create real-time price validation service to check against current menu prices.
  - [ ] Subtask 6.4: Implement performance monitoring for cart operations (response time tracking).
  - [ ] Subtask 6.5: Add cart operation retry logic with exponential backoff for network failures.

## Dev Notes

This story implements a **hybrid authentication and cart management system** that seamlessly bridges anonymous QR code users with authenticated Supabase users. The key architectural decisions are:

### Authentication Integration Strategy

- **Anonymous Users**: Start with anonymous sessions (existing system) that create cart sessions when first item is added
- **Authenticated Users**: Use Supabase Auth (Direct-to-Supabase approach) with cart sessions linked to `auth.users`
- **Seamless Migration**: When anonymous users sign in, their cart automatically migrates to their authenticated session
- **Session Validation**: Backend supports both anonymous session tokens and Supabase JWT tokens

### Database Design Philosophy

- **Unified Session Management**: `cart_sessions` table handles both anonymous and authenticated sessions
- **Persistent Cart Storage**: `cart_items` table stores cart data in backend, not just frontend state
- **Data Isolation**: RLS policies ensure cart data security across session types
- **Automatic Cleanup**: Background processes remove expired sessions and orphaned cart items

### Technical Integration Points

- **Supabase Auth Integration**: Leverages existing Direct-to-Supabase auth flow without modification
- **Anonymous Session Compatibility**: Works with existing `anonymous_sessions` table and functions
- **Frontend State Sync**: Enhanced CartController synchronizes with backend while maintaining reactive UI
- **Session Migration**: Transparent cart transfer during sign-in process

### MVP Architecture Strategy

- **Security-First Approach**: All database operations protected by RLS policies, input validation on all endpoints
- **Performance Optimization**: Database indexes on critical cart queries, connection pooling for concurrent users
- **Error Handling**: Comprehensive error states with user-friendly messages and automatic retry mechanisms
- **Scalability Foundation**: Clean separation of concerns to support future caching and microservices migration

### Post-MVP Roadmap (Future Phases)

- **Phase 2 Enhancements**: Redis caching layer, advanced analytics, cart abandonment recovery
- **Phase 3 Scale**: API rate limiting, comprehensive monitoring, real-time cross-device sync
- **Phase 4 Advanced**: Machine learning recommendations, dynamic pricing, advanced personalization

### Relevant Source Tree Information

- `infra/supabase/migrations/20250928000001_add_cart_management.sql`: New cart storage schema and functions
- `apps/backend/app/features/cart/`: New cart management API endpoints and services
- `apps/frontend/lib/features/diner/application/controllers/cart_controller.dart`: Enhanced cart controller with backend sync
- `apps/backend/app/features/auth/presentation/supabase_dependencies.py`: Enhanced session validation for cart tokens

### Important Notes from Previous Stories

- This story directly extends **Story 3.1 (Menu Browsing)** by adding cart functionality to menu item interactions
- Integrates with existing anonymous session system from QR code scanning workflow
- Ensure the code follows the vertical clean code architecture and and rules mentioned in the /Users/ashishverma/repos/zergo/zergoqrf/rules for relevant technologies.
- Post Development update the relevant story with the changes follow the template.
- Prepares the foundation for **Story 3.3 (Order Placement)** by providing persistent cart data

## Testing

### Relevant Testing Standards

- **Test File Location:**
  - Backend: `apps/backend/tests/features/cart/`
  - Frontend: `apps/frontend/test/features/diner/cart/`
  - Integration: `apps/backend/tests/integration/cart_auth_integration/`

### Critical Testing Areas

- **Session Security & Isolation:**
  - Backend: Write tests ensuring anonymous session `A` cannot access cart data of session `B`
  - Backend: Verify authenticated users can only access their own cart data via RLS policies
  - Integration: Test that Supabase JWT validation works correctly with cart endpoints
- **Cart Migration Testing:**

  - Backend: Test seamless cart migration from anonymous to authenticated sessions
  - Frontend: Verify cart state remains consistent during sign-in process
  - Integration: Test edge cases (expired sessions, invalid tokens, partial migrations)

- **Data Persistence & Synchronization:**
  - Backend: Test cart data survives server restarts and database reconnections
  - Frontend: Verify cart state synchronizes between frontend and backend correctly
  - Integration: Test cart consistency across multiple device sessions for authenticated users

### Specific Test Scenarios

1. **Anonymous Cart Flow**: QR scan → Menu browse → Add items → Cart persists → Session expires gracefully
2. **Authentication Migration**: Anonymous cart → User signs in → Cart seamlessly migrates → Data preserved
3. **Cross-Device Sync**: User signs in on device A → Adds items → Signs in on device B → Cart appears
4. **Price Calculation Edge Cases**: Complex orders with multiple customizations, promotions, tax variations
5. **Session Security**: Attempt to access cart with invalid tokens, expired sessions, wrong user context
6. **Concurrent Operations**: Multiple users adding items simultaneously, cart updates during price changes
7. **Business Rules Testing**: Attempt to add 51st item → Proper rejection with user-friendly message
8. **Performance Testing**: 100 concurrent users adding items → All operations complete within 3 seconds
9. **Price Validation**: Menu item price changes → Cart automatically updates with notification to user
10. **Error Recovery**: Network failures during cart operations → Automatic retry with user feedback
11. **Session Timeout**: User inactive for 2+ hours → Cart expires with proper cleanup and user notification

### Testing Frameworks and Patterns

- **Backend**: Use FastAPI test client with both anonymous tokens and Supabase JWT mocking
- **Frontend**: Test cart controller with backend API mocking and real Supabase auth integration
- **Database**: Test RLS policies with multiple user contexts and session types
- **Integration**: End-to-end tests covering complete user journeys from QR scan to order placement

## Change Log

| Date       | Version | Description                                                                                     | Author         |
| ---------- | ------- | ----------------------------------------------------------------------------------------------- | -------------- |
| 2025-09-24 | 1.0     | Initial draft of the story.                                                                     | Scrum Master   |
| 2025-09-28 | 2.0     | Enhanced with Supabase Auth integration, hybrid session management, and comprehensive testing.  | Scrum Master   |
| 2025-09-28 | 2.1     | Added MVP business rules, performance requirements, security validations, and post-MVP roadmap. | PM + Architect |

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
