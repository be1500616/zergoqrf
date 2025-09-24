<!-- Powered by BMAD™ Core -->

# Story 1.1: Restaurant Registration & Setup

## Status
- **Status:** Draft

## Story
**As a** restaurant owner,
**I want to** register my restaurant and configure basic settings,
**so that** I can start using the ZERGO QR digital ordering system.

## Acceptance Criteria
1. A restaurant owner can create an account with an email and password.
2. The registration process collects basic restaurant information (name, address, contact).
3. A business verification process with document upload is included.
4. A unique, SEO-friendly restaurant slug is generated.
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
- [ ] **Task 1: Registration Flow** (AC: #1, #2, #3, #4, #5)
  - [ ] Subtask 1.1: Create a multi-step registration form on the frontend.
  - [ ] Subtask 1.2: Develop a backend endpoint to handle new restaurant registrations.
  - [ ] Subtask 1.3: Implement logic to generate a unique slug from the restaurant name.
  - [ ] Subtask 1.4: Set up a secure document upload mechanism for business verification.
- [ ] **Task 2: Business Configuration UI** (AC: #6, #7, #8, #9, #10)
  - [ ] Subtask 2.1: Build a settings page for restaurant owners to configure business details.
  - [ ] Subtask 2.2: Create a UI component for setting business hours for each day of the week.
  - [ ] Subtask 2.3: Implement a feature to add and manage closure dates.
- [ ] **Task 3: Branding and Theming** (AC: #11, #12)
  - [ ] Subtask 3.1: Add a logo uploader to the restaurant settings page.
  - [ ] Subtask 3.2: Implement a color picker for theme customization.
- [ ] **Task 4: Financial and Operational Settings** (AC: #13, #14, #15, #16)
  - [ ] Subtask 4.1: Create forms for inputting tax and currency information.
  - [ ] Subtask 4.2: Develop options to configure order processing and service models.

## Dev Notes
This story provides the onboarding experience for new restaurant owners, which is a critical first impression of the platform. The registration process should be as smooth and intuitive as possible. The backend needs to handle the creation of a new tenant, including the restaurant profile and the owner's staff account, in a single atomic transaction to ensure data integrity.

### Relevant Source Tree Information
- `apps/frontend/lib/features/registration/`: Contains the Flutter widgets and controllers for the restaurant registration flow.
- `apps/backend/app/features/restaurants/`: Contains the FastAPI routers and logic for creating and managing restaurant profiles.
- `infra/supabase/migrations/`: SQL files defining the `restaurants` table and related schemas.

### Important Notes from Previous Stories
- This story is dependent on **Story 1.0 (Authentication System)**, as it needs to create a user account for the restaurant owner and associate it with the new restaurant.

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
  - Test the unique slug generation, ensuring it handles duplicate restaurant names correctly (e.g., by appending a number).
  - Verify that uploaded verification documents are stored securely.
  - Write tests for the business hours' configuration to handle various scenarios, such as 24-hour operations or split shifts.

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
