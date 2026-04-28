<!-- Powered by BMAD™ Core -->

# Story 1.2: Basic Table Management (MVP)

## Status

- **Status:** Approved

## Story

**As a** restaurant manager,
**I want to** create and manage a simple list of my restaurant's tables with basic information,
**so that** I can generate unique QR codes for each table to enable customer ordering.

## Acceptance Criteria

1. Restaurant managers can create tables with unique table numbers/identifiers.
2. Each table can have an optional seating capacity specified.
3. Tables can be listed, viewed, edited, and deleted through a simple interface.
4. Table numbers must be unique within a restaurant.
5. Each table is automatically assigned a unique ID for QR code generation.
6. The system validates that table numbers are not duplicated within the same restaurant.
7. Tables can be bulk created by specifying a count (e.g., "Create 10 tables numbered 1-10").
8. Basic table information (number, capacity, creation date) is stored and retrievable.

## Tasks / Subtasks

- [ ] **Task 1: Basic Table CRUD Operations** (AC: #1, #3, #4, #6)
  - [ ] Subtask 1.1: Create API endpoint to add a new table with number and optional capacity.
  - [ ] Subtask 1.2: Create API endpoint to list all tables for a restaurant.
  - [ ] Subtask 1.3: Create API endpoint to update table information (number, capacity).
  - [ ] Subtask 1.4: Create API endpoint to delete a table.
  - [ ] Subtask 1.5: Implement validation to ensure unique table numbers per restaurant.
- [ ] **Task 2: Table Database Schema** (AC: #5, #8)
  - [ ] Subtask 2.1: Design and create `tables` database table with required fields.
  - [ ] Subtask 2.2: Add foreign key relationship to restaurant.
  - [ ] Subtask 2.3: Create database indexes for optimal query performance.
- [ ] **Task 3: Basic Table Management UI** (AC: #1, #2, #3, #7)
  - [ ] Subtask 3.1: Create simple form to add individual tables.
  - [ ] Subtask 3.2: Create table listing view with edit/delete actions.
  - [ ] Subtask 3.3: Implement bulk table creation functionality.
  - [ ] Subtask 3.4: Add basic validation and error handling in the UI.

## Dev Notes

The table management system for MVP focuses on essential functionality needed to support QR code generation. This simple approach allows restaurant managers to quickly define their table inventory without complex visual interfaces. The system stores the basic table information required for QR code assignment while keeping the implementation straightforward and development time minimal.

### Database Schema Considerations

- Tables require a unique identifier (UUID) for QR code generation
- Table numbers should be unique within each restaurant but can be repeated across different restaurants
- Optional capacity field supports future reservation/ordering features
- Simple schema supports easy querying and maintenance

### Future Enhancements (Post-MVP)

- Visual floor plan editor with drag-and-drop functionality
- Real-time table status tracking
- Multi-floor support
- Table categorization (VIP, outdoor, etc.)
- Advanced table shapes and visual indicators

### Relevant Source Tree Information

- `apps/frontend/lib/features/table_management/`: Contains Flutter widgets for simple table CRUD operations.
- `apps/backend/app/features/tables/`: Contains FastAPI routers for table management endpoints.
- `infra/supabase/migrations/`: SQL files defining the `tables` table with basic schema.

### Important Notes from Previous Stories

- This story depends on **Story 1.1 (Restaurant Registration & Setup)** because a restaurant must exist before its table layout can be configured.
- It is a prerequisite for **Story 2.1 (QR Code Generation)**, as QR codes will be linked to specific tables.
- Ensure the code follows the vertical clean code architecture and and rules mentioned in the /Users/ashishverma/repos/zergo/zergoqrf/rules for relevant technologies.

## Testing

### Relevant Testing Standards

- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - API endpoints must be thoroughly tested for CRUD operations.
  - Database constraints (unique table numbers) must be validated.
  - Error handling for invalid inputs should be tested.
- **Testing Frameworks and Patterns:**
  - Backend: Test API endpoints for creating, reading, updating, and deleting tables.
  - Frontend: Use widget tests for table management forms. Use integration tests for the complete table creation and management workflow.
- **Specific Testing Requirements for This Story:**
  - Test that table numbers are unique within a restaurant but can be duplicated across different restaurants.
  - Verify that bulk table creation works correctly and handles edge cases (e.g., duplicate numbers).
  - Test API validation for required fields and proper error responses.
  - Verify that each table gets a unique identifier suitable for QR code generation.
  - Test the complete workflow from table creation to QR code generation preparation.

## Change Log

| Date       | Version | Description                                                                                                             | Author        |
| ---------- | ------- | ----------------------------------------------------------------------------------------------------------------------- | ------------- |
| 2025-09-24 | 1.0     | Initial draft of the story.                                                                                             | Scrum Master  |
| 2025-09-26 | 2.0     | Simplified to MVP requirements focusing on basic table CRUD operations instead of complex visual floor plan management. | Product Owner |

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
