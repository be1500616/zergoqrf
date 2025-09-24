<!-- Powered by BMAD™ Core -->

# Story 1.4: Restaurant Management Dashboard

## Status
- **Status:** Draft

## Story
**As a** restaurant owner/manager,
**I want to** have a comprehensive dashboard to monitor my restaurant's operations,
**so that** I can make informed decisions and manage my business effectively.

## Acceptance Criteria
1. Daily, weekly, and monthly revenue summaries are displayed.
2. Order volume and trends are visualized.
3. Customer count and frequency metrics are available.
4. Average order value is tracked.
5. Live order status can be monitored in real-time.
6. Current table occupancy status is displayed.
7. A list of on-duty staff and their current tasks is available.
8. The kitchen queue and preparation times are visible.
9. Today's earnings and payment statuses are shown.
10. A breakdown of payments by method is provided.
11. Customer feedback and ratings are summarized.
12. The most popular menu items are highlighted.
13. Quick action buttons are available for common tasks (e.g., bulk order updates, disabling menu items).

## Tasks / Subtasks
- [ ] **Task 1: Business Overview Metrics** (AC: #1, #2, #3, #4)
  - [ ] Subtask 1.1: Develop backend endpoints to aggregate and serve dashboard data.
  - [ ] Subtask 1.2: Create UI components to display key business metrics (revenue, orders, etc.).
  - [ ] Subtask 1.3: Implement a date range selector to filter the dashboard view.
- [ ] **Task 2: Real-Time Operations View** (AC: #5, #6, #7, #8)
  - [ ] Subtask 2.1: Set up a WebSocket or use Supabase Realtime to push live updates to the dashboard.
  - [ ] Subtask 2.2: Build UI components to display live orders, table status, and staff activity.
- [ ] **Task 3: Financial and Customer Insights** (AC: #9, #10, #11, #12)
  - [ ] Subtask 3.1: Create widgets for the financial and customer feedback sections.
  - [ ] Subtask 3.2: Implement the logic to calculate and display the most popular menu items.
- [ ] **Task 4: Quick Actions** (AC: #13)
  - [ ] Subtask 4.1: Design and implement a "Quick Actions" panel on the dashboard.
  - [ ] Subtask 4.2: Connect the action buttons to their respective backend functionalities.

## Dev Notes
The dashboard is the central hub for restaurant managers and owners. It needs to provide a high-level overview of the business at a glance, while also offering real-time insights into ongoing operations. The use of real-time data streams is crucial for the "Live Operations" section to be effective. Performance is also key; the dashboard should load quickly and feel responsive, even when displaying a large amount of data.

### Relevant Source Tree Information
- `apps/frontend/lib/features/dashboard/`: Contains the Flutter widgets and controllers for the management dashboard.
- `apps/backend/app/features/dashboard/`: Contains the FastAPI routers for aggregating and serving dashboard data.

### Important Notes from Previous Stories
- This story aggregates data from multiple previous stories, including **Story 1.1 (Restaurant Setup)**, **Story 1.3 (Staff Management)**, and **Story 3.3 (Order Placement)**.

## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - Dashboard data accuracy is critical and must be tested thoroughly.
  - Real-time updates should be tested to ensure they are timely and correct.
- **Testing Frameworks and Patterns:**
  - Backend: Write tests to verify the correctness of the data aggregation queries.
  - Frontend: Use integration tests to simulate real-time updates and verify that the UI reflects the changes correctly.
- **Specific Testing Requirements for This Story:**
  - Test that the revenue summary matches the sum of individual order totals for the selected period.
  - Verify that when an order's status is updated, the change is reflected in the "Live Orders" panel within 2 seconds.
  - Test the "Quick Actions" to ensure they trigger the correct backend operations.

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
