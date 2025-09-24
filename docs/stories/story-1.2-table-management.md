<!-- Powered by BMAD™ Core -->

# Story 1.2: Table Management System

## Status
- **Status:** Draft

## Story
**As a** restaurant manager,
**I want to** define and organize my restaurant's table layout and capacity,
**so that** I can manage seating efficiently and prepare for QR code assignment.

## Acceptance Criteria
1. A drag-and-drop interface for arranging tables is available.
2. The interface provides a visual representation of the restaurant floor plan.
3. Table positioning is based on a grid layout.
4. Different table shapes (round, square, rectangular) are supported.
5. Visual indicators for table status and capacity are displayed.
6. Floor plan configurations can be saved and loaded.
7. Table capacity (number of seats) can be set.
8. Unique table numbers or identifiers can be assigned.
9. Tables can be categorized (e.g., regular, VIP, outdoor).
10. Multiple floor plans can be created (e.g., ground floor, terrace).
11. Real-time table status (Available, Occupied, Reserved, Cleaning) is displayed.
12. Table occupancy duration is tracked.
13. Table status can be updated automatically based on order completion.
14. Staff can manually override table status.

## Tasks / Subtasks
- [ ] **Task 1: Visual Table Editor** (AC: #1, #2, #3, #4, #5, #6)
  - [ ] Subtask 1.1: Develop a drag-and-drop canvas for the floor plan.
  - [ ] Subtask 1.2: Create visual components for different table shapes and statuses.
  - [ ] Subtask 1.3: Implement the backend logic to save and retrieve table coordinates.
- [ ] **Task 2: Table Configuration** (AC: #7, #8, #9)
  - [ ] Subtask 2.1: Build a properties panel to edit the details of a selected table.
  - [ ] Subtask 2.2: Enhance the `tables` database schema to store capacity, shape, and type.
- [ ] **Task 3: Multi-Floor Support** (AC: #10)
  - [ ] Subtask 3.1: Implement UI for creating and switching between multiple floors.
  - [ ] Subtask 3.2: Add a `floor_id` to the `tables` table to associate tables with a specific floor.
- [ ] **Task 4: Real-Time Status Management** (AC: #11, #12, #13, #14)
  - [ ] Subtask 4.1: Use Supabase Realtime to broadcast table status changes to all connected clients.
  - [ ] Subtask 4.2: Develop backend logic to update table status based on order events.
  - [ ] Subtask 4.3: Create API endpoints for staff to manually update table statuses.

## Dev Notes
The table management system is a core operational tool for restaurant staff. The visual layout editor should be highly interactive and intuitive. The real-time status updates are a key feature, requiring a reliable WebSocket or similar connection to ensure that all staff members have a synchronized view of the floor plan. This will be achieved using Supabase's real-time capabilities.

### Relevant Source Tree Information
- `apps/frontend/lib/features/table_management/`: Contains the Flutter widgets and controllers for the table layout editor and status dashboard.
- `apps/backend/app/features/tables/`: Contains the FastAPI routers for managing tables and their statuses.
- `infra/supabase/migrations/`: SQL files defining the `tables` and `restaurant_floors` tables.

### Important Notes from Previous Stories
- This story depends on **Story 1.1 (Restaurant Registration & Setup)** because a restaurant must exist before its table layout can be configured.
- It is a prerequisite for **Story 2.1 (QR Code Generation)**, as QR codes will be linked to specific tables.

## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - The drag-and-drop functionality should be tested to ensure positions are saved correctly.
  - Real-time updates must be tested to verify synchronization across multiple clients.
- **Testing Frameworks and Patterns:**
  - Backend: Test API endpoints for creating, updating, and deleting tables and floors.
  - Frontend: Use widget tests for the table editor components. Use integration tests to simulate a user arranging tables on the floor plan and saving the layout.
- **Specific Testing Requirements for This Story:**
  - Write a test to confirm that when a table's status is updated, the change is immediately reflected on a second client.
  - Test the constraints on table creation, such as unique table numbers per restaurant.
  - Verify that a user can create and manage tables across multiple floors.

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
