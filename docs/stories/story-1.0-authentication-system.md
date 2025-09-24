<!-- Powered by BMAD™ Core -->

# Story 1.0: Authentication System Setup

## Status
- **Status:** Draft

## Story
**As a** system architect,
**I want to** implement a comprehensive multi-tenant authentication system,
**so that** restaurant staff, customers, and anonymous users can securely access appropriate features.

## Acceptance Criteria
1. Supabase Auth is configured with JWT tokens.
2. Multi-tenant Row Level Security (RLS) policies are implemented.
3. Custom JWT claims for restaurant context are included.
4. A token refresh mechanism is working correctly.
5. Session management with secure storage is in place.
6. Restaurant staff can authenticate using email/password with role-based permissions.
7. Customers can authenticate using phone/OTP for placing orders.
8. Anonymous users have public menu access without authentication.
9. Restaurant data is isolated via RLS policies.
10. JWT tokens contain a `restaurant_id` for scoping.
11. A permission system with roles (owner, manager, kitchen, service) is implemented.
12. Cross-restaurant data access is prevented.
13. A Flutter authentication service with GetX is created for state management.
14. The frontend service handles automatic token refresh in the background.
15. Tokens are stored securely on the device using Flutter Secure Storage.
16. Authentication state is managed consistently across the app.
17. Role-based UI access control is implemented on the frontend.

## Tasks / Subtasks
- [ ] **Task 1: Database and RLS Setup** (AC: #2, #9, #10, #11, #12)
  - [ ] Subtask 1.1: Create `restaurant_staff` and `customers` tables.
  - [ ] Subtask 1.2: Implement RLS policies to enforce multi-tenancy.
  - [ ] Subtask 1.3: Design a roles and permissions system within the database.
- [ ] **Task 2: Backend Authentication Logic** (AC: #1, #3, #4, #6)
  - [ ] Subtask 2.1: Implement FastAPI middleware to validate Supabase JWTs.
  - [ ] Subtask 2.2: Create a mechanism (e.g., Edge Function) to add custom claims to JWTs.
  - [ ] Subtask 2.3: Develop role-based access control decorators for API endpoints.
- [ ] **Task 3: Frontend Authentication Service** (AC: #5, #13, #14, #15, #16, #17)
  - [ ] Subtask 3.1: Build an `AuthService` in Flutter using GetX.
  - [ ] Subtask 3.2: Implement login flows for staff (email/password) and customers (OTP).
  - [ ] Subtask 3.3: Integrate `flutter_secure_storage` for token persistence.
  - [ ] Subtask 3.4: Implement logic to handle token refresh and session management.
  - [ ] Subtask 3.5: Create UI components that react to authentication state and user roles.
- [ ] **Task 4: Anonymous Session Management** (AC: #8)
  - [ ] Subtask 4.1: Design a system for creating temporary, anonymous sessions for QR code users.
  - [ ] Subtask 4.2: Implement the backend logic to manage these sessions.

## Dev Notes
This story is a critical piece of the application's security and data architecture. The multi-tenant design using Supabase RLS is fundamental to ensuring that data from one restaurant is never exposed to another. The use of custom JWT claims is key to efficiently passing user context (like `restaurant_id` and `role`) to the backend, which simplifies authorization logic in the API layer.

### Relevant Source Tree Information
- `infra/supabase/migrations/`: SQL files defining the authentication-related tables and RLS policies.
- `apps/backend/app/core/auth.py`: Contains the FastAPI authentication middleware and dependency injectors.
- `apps/frontend/lib/core/services/auth_service.dart`: The central Flutter service for managing all authentication logic.

### Important Notes from Previous Stories
- This story depends on the database infrastructure established in **Story 0.1**.

## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - Security-related tests must cover all primary access control scenarios.
  - Mock authentication extensively to test protected endpoints and UI components without requiring live user sessions.
- **Testing Frameworks and Patterns:**
  - Backend: Use `pytest` fixtures to provide mock `AuthContext` objects to protected endpoints.
  - Frontend: Test the `AuthService` logic thoroughly. Use widget tests to verify that UI components correctly show/hide based on authentication state and user roles.
- **Specific Testing Requirements for This Story:**
  - Write a test to ensure an API request with a JWT from `restaurant_A` cannot access data from `restaurant_B`.
  - Test that a user with a 'service' role cannot access an endpoint restricted to 'managers'.
  - On the frontend, test that a login screen is shown when no user is authenticated and that the user is redirected to the dashboard after a successful login.
  - Write a test for the OTP verification flow.

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
