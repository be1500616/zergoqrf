<!-- Powered by BMAD™ Core -->

# Story 7.3: UI Refactoring

## Status
- **Status:** Draft

## Story
**As a** developer,
**I want to** refactor the existing UI to use the new design system and reusable components,
**so that** the entire application has a consistent look and feel, and is easier to maintain and update.

## Acceptance Criteria
1. All screens in the application are refactored to use the `AppTheme` and reusable components from the design system.
2. All inline styles and hardcoded values (colors, font sizes, etc.) are removed from the UI code.
3. The application's UI is fully responsive and adapts to different screen sizes and orientations.
4. The refactored code is cleaner, more readable, and easier to maintain.
5. The application's functionality remains unchanged after the refactoring.

## Tasks / Subtasks
- [ ] **Task 1: Refactor Authentication Screens** (AC: #1, #2, #3, #4)
  - [ ] Subtask 1.1: Refactor the `AuthScreen`.
- [ ] **Task 2: Refactor Restaurant Screens** (AC: #1, #2, #3, #4)
  - [ ] Subtask 2.1: Refactor the `RestaurantRegistrationScreen`.
  - [ ] Subtask 2.2: Refactor the `RestaurantDashboardScreen`.
  - [ ] Subtask 2.3: Refactor the `RestaurantSettingsScreen`.
  - [ ] Subtask 2.4: Refactor the `StaffManagementScreen`.
- [ ] **Task 3: Refactor Home Screen** (AC: #1, #2, #3, #4)
  - [ ] Subtask 3.1: Refactor the `HomeScreen`.
- [ ] **Task 4: Verification** (AC: #5)
  - [ ] Subtask 4.1: Perform a full regression test of the application to ensure that all functionality is working as expected.

## Dev Notes
This story is a significant undertaking that will touch a large portion of the codebase. It is important to approach it systematically, refactoring one screen at a time and thoroughly testing each one before moving on to the next.

### Relevant Source Tree Information
- `apps/frontend/lib/features/`: The directory containing the application's feature screens.
- `apps/frontend/lib/core/theme/`: The directory containing the design system.

## Testing
### Relevant Testing Standards
- **Test File Location:** `apps/frontend/test/`
- **Test Standards:**
  - All existing widget tests should be updated to reflect the changes made during the refactoring.
  - New widget tests should be added for any screens that do not have them.
- **Specific Testing Requirements for This Story:**
  - Write golden tests for each refactored screen to ensure that the UI remains consistent.
  - Perform manual testing on a variety of devices and screen sizes to verify the responsiveness of the UI.

## Change Log
| Date       | Version | Description                 | Author       |
|------------|---------|-----------------------------|--------------|
| 2025-09-24 | 1.0     | Initial draft of the story. | Architect    |