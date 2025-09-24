<!-- Powered by BMAD™ Core -->

# Story 3.2: Cart Management & Session Security

## Status
- **Status:** Draft

## Story
**As a** dining customer,
**I want to** add items to my cart and manage my order,
**so that** I can build my meal selection before placing the order.

## Acceptance Criteria
1. An "Add to Cart" button creates a temporary session if one does not exist.
2. Items are added to the cart with the selected quantity and customizations.
3. The cart persists as the user navigates through the menu.
4. Item quantities can be modified, and items can be removed from the cart.
5. The running total updates automatically with each change.
6. The session is valid for a limited time (e.g., 2 hours) and is extended with activity.
7. Cart data is isolated per session.
8. Price calculations accurately reflect the base price, customizations, quantity, and taxes.
9. A mini-cart view is visible during menu browsing.
10. A full cart page is accessible to review the order before placement.

## Tasks / Subtasks
- [ ] **Task 1: Session Management** (AC: #1, #6, #7)
  - [ ] Subtask 1.1: Develop a backend service to create and manage anonymous, temporary user sessions.
  - [ ] Subtask 1.2: Implement logic for session creation, validation, and expiration.
  - [ ] Subtask 1.3: Ensure cart data is securely associated with the session token.
- [ ] **Task 2: Cart Functionality** (AC: #2, #3, #4, #5)
  - [ ] Subtask 2.1: Implement backend endpoints for adding, updating, and removing items from the cart.
  - [ ] Subtask 2.2: Develop frontend state management (e.g., using GetX) to handle the cart state.
- [ ] **Task 3: Price Calculation Engine** (AC: #8)
  - [ ] Subtask 3.1: Create a backend service to accurately calculate the cart total, including all variables.
  - [ ] Subtask 3.2: Ensure the frontend displays the itemized and total prices correctly.
- [ ] **Task 4: UI/UX Implementation** (AC: #9, #10)
  - [ ] Subtask 4.1: Design and build the mini-cart and full-page cart components.
  - [ ] Subtask 4.2: Implement intuitive user interactions, such as quantity selectors and removal gestures.

## Dev Notes
This story introduces a new security and state management layer: the temporary, anonymous session. This is a deliberate design choice to maintain a zero-friction browsing experience while securing the ordering process. The session is only created when a user first adds an item to their cart, not before. This balances user experience with the need for a stateful transaction.

### Relevant Source Tree Information
- `apps/frontend/lib/features/cart/`: Contains the Flutter widgets and controllers for the cart.
- `apps/backend/app/features/sessions/`: Contains the FastAPI routers for session and cart management.
- `infra/supabase/migrations/`: SQL file defining the `customer_sessions` table.

### Important Notes from Previous Stories
- This story is a direct continuation of **Story 3.1 (Menu Browsing)** and acts as the bridge to **Story 3.3 (Order Placement)**.

## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - Session security must be rigorously tested to ensure data isolation.
  - Price calculation logic must be tested with a wide range of scenarios.
- **Testing Frameworks and Patterns:**
  - Backend: Write tests to ensure that a request with `sessionToken_A` cannot access the cart data of `sessionToken_B`.
  - Frontend: Test the cart's state management to ensure it remains consistent across different app screens and after browser refreshes.
- **Specific Testing Requirements for This Story:**
  - Test that a session is created upon the first "Add to Cart" action.
  - Verify that the session expiry and auto-extension logic works as expected.
  - Write a test case with a complex order (multiple items, quantities, and customizations) to validate the final price calculation.

## Change Log
| Date       | Version | Description                 | Author       |
|------------|---------|-----------------------------|--------------|
| 2025-09-24 | 1.0     | Initial draft of the story. | Scrum Master |

## Dev Agent Record
### Agent Model Used
*This section will be populated by the development agent.*

### Debug Log References
*This section will be populated by the development agent.*

### Completion Notes List
*This section will be populated by the development agent.*

### File List
*This section will be populated by the development agent.*

## QA Results
*This section will be populated by the QA agent after review.*
