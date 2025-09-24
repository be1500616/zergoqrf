<!-- Powered by BMAD™ Core -->

# Story 1.5: Menu Creation & Management

## Status
- **Status:** Draft

## Story
**As a** restaurant owner/manager,
**I want to** create, organize, and manage my restaurant's menu,
**so that** customers can browse and order from an attractive, up-to-date menu.

## Acceptance Criteria
1. Menu categories (e.g., Appetizers, Mains) can be created and organized.
2. Nested subcategories are supported.
3. Categories can be scheduled for availability (e.g., breakfast, lunch).
4. Menu items can be added with names, descriptions, and prices.
5. High-quality images can be uploaded for each item.
6. Items can be marked with dietary indicators (e.g., vegetarian, gluten-free).
7. Allergen information can be added to items.
8. Multiple pricing tiers or variants (e.g., small, large) are supported.
9. Customizable add-ons with additional costs can be created.
10. A distinction between draft and live menu versions is maintained.
11. Menu updates can be scheduled for future dates.
12. A history of menu changes is available, with the ability to roll back.
13. Menu changes are published instantly across all QR codes.

## Tasks / Subtasks
- [ ] **Task 1: Menu Structure** (AC: #1, #2, #3)
  - [ ] Subtask 1.1: Develop a UI for creating and reordering menu categories and subcategories.
  - [ ] Subtask 1.2: Implement backend logic to manage the hierarchical structure of the menu.
- [ ] **Task 2: Menu Item Management** (AC: #4, #5, #6, #7)
  - [ ] Subtask 2.1: Build a form for adding and editing menu items, including image uploads.
  - [ ] Subtask 2.2: Enhance the database schema to store all required item details.
- [ ] **Task 3: Pricing and Customization** (AC: #8, #9)
  - [ ] Subtask 3.1: Implement a flexible system for defining item variants and add-ons.
  - [ ] Subtask 3.2: Ensure the pricing logic correctly calculates the total cost with customizations.
- [ ] **Task 4: Versioning and Publishing** (AC: #10, #11, #12, #13)
  - [ ] Subtask 4.1: Design a system for managing different versions of the menu.
  - [ ] Subtask 4.2: Implement a publishing workflow that allows for scheduled updates and rollbacks.

## Dev Notes
The menu is the heart of the restaurant's offering, so the management interface must be both powerful and easy to use. The data model should be flexible enough to handle a wide variety of menu configurations. The versioning system is a key feature that allows restaurants to prepare for seasonal changes or promotions in advance without affecting the live menu.

### Relevant Source Tree Information
- `apps/frontend/lib/features/menu_management/`: Contains the Flutter widgets and controllers for the menu editor.
- `apps-backend/app/features/menu/`: Contains the FastAPI routers for menu-related CRUD operations.
- `infra/supabase/migrations/`: SQL files defining the `menu_categories`, `menu_items`, and related tables.

### Important Notes from Previous Stories
- This story's permissions are managed by the RBAC system from **Story 1.3**.
- The output of this story is directly consumed by **Story 3.1 (Menu Browsing)**.

## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - All menu operations (CRUD, reordering, publishing) must be tested.
  - The pricing calculation for items with variants and add-ons must be thoroughly validated.
- **Testing Frameworks and Patterns:**
  - Backend: Write tests for the menu publishing logic to ensure that draft changes do not affect the live menu until explicitly published.
  - Frontend: Use widget tests for the drag-and-drop reordering of categories and items.
- **Specific Testing Requirements for This Story:**
  - Test that scheduling a menu update for a future date works correctly.
  - Verify that rolling back to a previous menu version restores the correct data.
  - Write a test to confirm that an item marked as "unavailable" does not appear on the public menu.

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
