<!-- Powered by BMAD™ Core -->

# Story 7.2: Reusable UI Components

## Status
- **Status:** Draft

## Story
**As a** developer,
**I want to** have a library of reusable and responsive UI components,
**so that** I can build new features faster and ensure a consistent user experience across the application.

## Acceptance Criteria
1. A `widgets` directory is created in `apps/frontend/lib/core/theme/`.
2. The directory contains a set of common UI components, such as `PrimaryButton`, `SecondaryButton`, `CustomTextField`, and `InfoCard`.
3. Each component is styled using the `AppTheme` from the design system.
4. The components are responsive and adapt to different screen sizes.
5. The components are well-documented with clear examples of how to use them.
6. The new components are used to replace at least one existing instance of a button, text field, and card in the application.

## Tasks / Subtasks
- [ ] **Task 1: Create Button Components** (AC: #2, #3, #4)
  - [ ] Subtask 1.1: Implement a `PrimaryButton` widget.
  - [ ] Subtask 1.2: Implement a `SecondaryButton` widget.
- [ ] **Task 2: Create Text Field Component** (AC: #2, #3, #4)
  - [ ] Subtask 2.1: Implement a `CustomTextField` widget with support for validation and different input types.
- [ ] **Task 3: Create Card Component** (AC: #2, #3, #4)
  - [ ] Subtask 3.1: Implement an `InfoCard` widget for displaying information in a visually appealing way.
- [ ] **Task 4: Documentation** (AC: #5)
  - [ ] Subtask 4.1: Add comments and examples to each component.
- [ ] **Task 5: Integration** (AC: #6)
  - [ ] Subtask 5.1: Refactor an existing screen to use the new components.

## Dev Notes
The reusable components are the building blocks of the application's UI. They should be designed to be flexible and customizable, while still enforcing the design system's guidelines.

### Relevant Source Tree Information
- `apps/frontend/lib/core/theme/widgets/`: The new directory to be created.
- `apps/frontend/lib/core/theme/design_system.dart`: The file containing the `AppTheme`.

## Testing
### Relevant Testing Standards
- **Test File Location:** `apps/frontend/test/`
- **Test Standards:**
  - Each reusable component must have its own widget test.
  - The tests should cover all possible states of the component (e.g., enabled, disabled, hover, focus).
- **Specific Testing Requirements for This Story:**
  - Write a golden test for each component to ensure that it renders correctly.
  - Test the responsiveness of the components by rendering them on different screen sizes.

## Change Log
| Date       | Version | Description                 | Author       |
|------------|---------|-----------------------------|--------------|
| 2025-09-24 | 1.0     | Initial draft of the story. | Architect    |