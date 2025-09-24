<!-- Powered by BMAD™ Core -->

# Story 1.3: Staff Management & Role-Based Access

## Status
- **Status:** Draft

## Story
**As a** restaurant owner,
**I want to** manage my staff members and assign appropriate permissions,
**so that** I can control system access and maintain operational security.

## Acceptance Criteria
1. New staff members can be added via an email invitation system.
2. Staff profiles can be created with personal and contact information.
3. Staff roles (Owner, Manager, Kitchen, Service, Cashier) are available.
4. Custom roles with granular permissions can be created.
5. Granular permission control is available for each feature module.
6. Staff shift scheduling with time slots is supported.
7. Attendance tracking and time logs are available.
8. Order processing metrics per staff member can be tracked.
9. Customer feedback and ratings can be associated with staff members.

## Tasks / Subtasks
- [ ] **Task 1: Staff Profile Management** (AC: #1, #2)
  - [ ] Subtask 1.1: Develop a UI for inviting and adding new staff members.
  - [ ] Subtask 1.2: Create backend endpoints for CRUD operations on staff profiles.
  - [ ] Subtask 1.3: Implement the email invitation flow.
- [ ] **Task 2: Role-Based Access Control (RBAC)** (AC: #3, #4, #5)
  - [ ] Subtask 2.1: Define a flexible permissions schema in the database.
  - [ ] Subtask 2.2: Implement a UI for creating and managing roles and their associated permissions.
  - [ ] Subtask 2.3: Enforce permissions in the backend API using middleware or decorators.
- [ ] **Task 3: Schedule and Shift Management** (AC: #6, #7)
  - [ ] Subtask 3.1: Design and build a staff scheduling interface.
  - [ ] Subtask 3.2: Implement logic for shift assignments, swaps, and attendance tracking.
- [ ] **Task 4: Performance Tracking** (AC: #8, #9)
  - [ ] Subtask 4.1: Integrate staff tracking into the order and feedback systems.
  - [ ] Subtask 4.2: Develop a dashboard to display staff performance metrics.

## Dev Notes
The staff management feature is central to the restaurant's operational control. The RBAC system must be robust and flexible enough to accommodate various restaurant structures. Permissions should be enforced at the API level as the primary security measure. The frontend will then use these permissions to conditionally render UI elements, providing a tailored experience for each user role.

### Relevant Source Tree Information
- `apps/frontend/lib/features/staff_management/`: Contains the Flutter widgets and controllers for managing staff.
- `apps/backend/app/features/staff/`: Contains the FastAPI routers for staff and role management.
- `infra/supabase/migrations/`: SQL files defining the `restaurant_staff` and `staff_roles` tables.

### Important Notes from Previous Stories
- This story builds upon the authentication system from **Story 1.0**, associating staff profiles with authenticated users.

## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - Role-based access control must be tested thoroughly to prevent unauthorized access.
- **Testing Frameworks and Patterns:**
  - Backend: Write tests that attempt to access protected endpoints with insufficient permissions and assert that access is denied.
  - Frontend: Use widget tests to verify that UI elements are correctly shown or hidden based on the logged-in user's role.
- **Specific Testing Requirements for This Story:**
  - Test that a 'Kitchen' role user cannot access the 'Reports' page.
  - Verify that a manager can create a new staff member and that the invitation email is sent.
  - Test the shift scheduling logic, including conflict detection.

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
