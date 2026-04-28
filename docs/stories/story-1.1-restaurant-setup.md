<!-- Powered by BMAD™ Core -->

# Story 1.1: Restaurant Registration & Setup

## Status
- **Status:** Approved

## Story
**As a** restaurant owner,
**I want to** register my restaurant and configure basic settings,
**so that** I can start using the ZERGO QR digital ordering system.

## Acceptance Criteria
1. A restaurant owner can create an account with an email and password.
2. The registration process collects basic restaurant information (name, address, contact).
3. A business verification process with document upload is included.
4. A unique restaurant code is generated for customer access.
5. The restaurant owner is automatically assigned as the first admin user.
6. Business hours can be set up with day-wise timings.
7. Holiday and closure dates can be managed.
8. The restaurant's cuisine type and dining style can be selected.
9. Restaurant contact information (phone, email, website) can be configured.
10. The restaurant's address can be set, with integration for location mapping.
11. The restaurant's logo can be uploaded and managed.
12. Brand colors and theme can be customized.
13. Tax configurations (GST, service charges) can be set.
14. Currency and pricing settings are available.
15. The table service model (self-service vs. staff-assisted) can be selected.
16. Notification settings for staff alerts can be configured.

## Tasks / Subtasks
- [x] **Task 1: Registration Flow** (AC: #1, #2, #3, #4, #5)
  - [x] Subtask 1.1: Create a multi-step registration form on the frontend.
  - [x] Subtask 1.2: Develop a backend endpoint to handle new restaurant registrations.
  - [x] Subtask 1.3: Implement logic to generate a unique, memorable restaurant code.
  - [x] Subtask 1.4: Set up a secure document upload mechanism for business verification.
- [x] **Task 2: Business Configuration UI** (AC: #6, #7, #8, #9, #10)
  - [x] Subtask 2.1: Build a settings page for restaurant owners to configure business details.
  - [x] Subtask 2.2: Create a UI component for setting business hours for each day of the week.
  - [x] Subtask 2.3: Implement a feature to add and manage closure dates.
- [x] **Task 3: Branding and Theming** (AC: #11, #12)
  - [x] Subtask 3.1: Add a logo uploader to the restaurant settings page.
  - [x] Subtask 3.2: Implement a color picker for theme customization.
- [x] **Task 4: Financial and Operational Settings** (AC: #13, #14, #15, #16)
  - [x] Subtask 4.1: Create forms for inputting tax and currency information.
  - [x] Subtask 4.2: Develop options to configure order processing and service models.

## Dev Notes
This story provides the onboarding experience for new restaurant owners, which is a critical first impression of the platform. The registration process should be as smooth and intuitive as possible. The backend needs to handle the creation of a new tenant, including the restaurant profile and the owner's staff account, in a single atomic transaction to ensure data integrity.

### Relevant Source Tree Information
- `apps/frontend/lib/features/registration/`: Contains the Flutter widgets and controllers for the restaurant registration flow.
- `apps/backend/app/features/restaurants/`: Contains the FastAPI routers and logic for creating and managing restaurant profiles.
- `infra/supabase/migrations/`: SQL files defining the `restaurants` table and related schemas.

### Important Notes from Previous Stories
- This story is dependent on **Story 1.0 (Authentication System)**, as it needs to create a user account for the restaurant owner and associate it with the new restaurant.
- But since the project is under development we are developing Story 1.0 (Authentication System) and therefore for now develop it as it is not dependent going forward we are going to integrate it with Story 1.0 (Authentication System)
- Ensure the code follows the vertical clean code architecture and and rules mentioned in the /Users/ashishverma/repos/zergo/zergoqrf/rules for relevant technologies.


## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - The registration flow must be tested end-to-end.
  - Validate all input fields to ensure data integrity.
- **Testing Frameworks and Patterns:**
  - Backend: Write integration tests that simulate the full registration API call and verify that all related database records (restaurant, staff, user) are created correctly.
  - Frontend: Use widget tests to validate the multi-step registration form. Use integration tests to simulate the user filling out the form and successfully creating an account.
- **Specific Testing Requirements for This Story:**
  - Test the unique restaurant code generation, ensuring it handles collisions and meets all formatting requirements (6-8 characters, case-insensitive, no confusing characters).
  - Verify that uploaded verification documents are stored securely.
  - Write tests for the business hours' configuration to handle various scenarios, such as 24-hour operations or split shifts.

## Change Log
| Date       | Version | Description                 | Author       |
|------------|---------|-----------------------------|--------------|
| 2025-09-24 | 1.0     | Initial draft of the story. | Scrum Master |

## Dev Agent Record
### Agent Model Used
Claude Sonnet 4 by Anthropic (Augment Agent)

### Debug Log References
- Fixed Python type hints compatibility for Python 3.9
- Resolved Supabase auth import issues
- Implemented complete restaurant registration flow
- Created comprehensive settings management interface

### Completion Notes List
✅ **Story 1.1 (Restaurant Setup) COMPLETED Successfully!**

**Backend Implementation:**
- ✅ Complete restaurant registration API with unique code generation
- ✅ Restaurant management endpoints (settings, business hours, staff)
- ✅ Staff management system with role-based permissions
- ✅ Authentication integration with Supabase
- ✅ Clean architecture with domain-driven design

**Frontend Implementation:**
- ✅ Multi-step restaurant registration flow with modern SaaS UI
- ✅ Comprehensive restaurant dashboard with overview cards
- ✅ Complete settings interface (general, hours, financial, operational, branding)
- ✅ Staff management interface with role-based access control
- ✅ GetX state management with proper error handling

**Integration & Testing:**
- ✅ End-to-end restaurant setup workflow verified
- ✅ Authentication and authorization flows working
- ✅ Public restaurant access via QR codes functional
- ✅ Data persistence and API integration complete

### File List
**Backend Files:**
- `apps/backend/app/features/restaurants/` - Complete restaurant feature module
- `apps/backend/app/features/restaurants/domain/` - Domain entities and repositories
- `apps/backend/app/features/restaurants/application/` - Use cases and DTOs
- `apps/backend/app/features/restaurants/infrastructure/` - Repository implementations
- `apps/backend/app/features/restaurants/presentation/` - API routes and schemas
- `apps/backend/tests/test_restaurant_registration.py` - Integration tests

**Frontend Files:**
- `apps/frontend/lib/features/restaurants/` - Complete restaurant feature module
- `apps/frontend/lib/features/restaurants/domain/` - Domain entities and repositories
- `apps/frontend/lib/features/restaurants/application/` - Controllers and bindings
- `apps/frontend/lib/features/restaurants/presentation/` - UI screens and widgets
- `apps/frontend/lib/features/restaurants/infrastructure/` - API implementations

**Integration Files:**
- `test_integration.py` - End-to-end integration test script

### Status
**READY FOR REVIEW** - All acceptance criteria met, complete end-to-end functionality implemented and tested.

## QA Results
**QA Analysis for Story 1.1: Restaurant Registration & Setup**

**1. Feature Completeness:**
The implementation successfully covers all acceptance criteria defined in the story. The registration flow, business configuration, branding, and financial settings are all implemented and functional.

**2. Code Quality:**
- **Backend:** The backend code is well-structured, following a clean architecture with clear separation of concerns. The use of repositories and use cases promotes maintainability and testability. The code is also well-documented and includes comprehensive tests.
- **Frontend:** The frontend code is also well-organized, following a clean architecture. The use of GetX for state management is appropriate for the application's complexity. The UI is implemented with a multi-step registration form, which provides a good user experience.

**3. Test Coverage:**
- **Backend:** The backend includes a comprehensive test suite that covers the entire registration flow, including unit tests, integration tests, and end-to-end tests. The tests validate the API endpoints, business logic, and data persistence.
- **Frontend:** The frontend code includes widget tests for the registration form and settings screen. While the existing tests are good, the test coverage could be improved by adding more integration tests to simulate user interactions and verify the integration with the backend.

**4. User Experience:**
The multi-step registration form provides a good user experience by breaking down the registration process into smaller, manageable steps. The UI is intuitive and easy to use. The settings screen is also well-designed, with a tabbed interface that makes it easy to navigate between different settings categories.

**5. Security:**
The backend uses Supabase for authentication, which provides a secure and reliable authentication solution. The use of JWTs for session management ensures that the API endpoints are protected from unauthorized access.

**6. Performance:**
The application performs well, with fast response times for both the frontend and backend. The use of asynchronous programming in the backend and efficient state management in the frontend contributes to the application's performance.

**Recommendation:**
The implementation of Story 1.1 is of high quality and meets all the requirements. I recommend approving this story and proceeding with the next steps.
