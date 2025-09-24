<!-- Powered by BMAD™ Core -->

# Story 0.1: Development Environment Setup

## Status
- **Status:** Draft

## Story
**As a** developer,
**I want** to quickly set up a complete development environment,
**so that** I can begin implementing ZERGO QR features with all dependencies configured.

## Acceptance Criteria
1. Docker Compose configuration for all services is present.
2. Backend (FastAPI) container runs with hot reload.
3. Database (Supabase local) container is set up with seed data.
4. Redis container for caching and sessions is included.
5. All services can be started with a single `make dev` command.
6. Environment variables are properly configured via `.env`.
7. Flutter development environment setup is documented.
8. Web development server runs on `localhost:3000`.
9. Hot reload is working for Flutter web development.
10. All required Flutter dependencies are installed via `flutter pub get`.
11. Environment is configured for local API endpoints.
12. Supabase local instance or connection to the cloud is established.
13. Database migrations run automatically on startup.
14. Seed data includes test restaurants, tables, and menus.
15. RLS policies are properly configured and tested.
16. Database schema matches architecture documentation.
17. Code formatting is configured (Black for Python, dartfmt for Flutter).
18. Linting is configured (mypy, flake8 for Python; analyzer for Flutter).
19. Pre-commit hooks for code quality are in place.
20. VS Code is configured with recommended extensions.
21. Debug configurations for backend and frontend are available.

## Tasks / Subtasks
- [ ] **Task 1: Docker Environment Setup** (AC: #1, #2, #3, #4, #5, #6)
  - [ ] Subtask 1.1: Create `docker-compose.yml` for backend, database, and Redis.
  - [ ] Subtask 1.2: Configure hot reload for the FastAPI backend container.
  - [ ] Subtask 1.3: Set up Supabase local development environment.
  - [ ] Subtask 1.4: Implement a `make dev` command to orchestrate container startup.
  - [ ] Subtask 1.5: Create and document the `.env.example` file.
- [ ] **Task 2: Frontend Setup** (AC: #7, #8, #9, #10, #11)
  - [ ] Subtask 2.1: Document the Flutter installation and setup process.
  - [ ] Subtask 2.2: Configure the Flutter web server to run on the specified port.
  - [ ] Subtask 2.3: Verify hot reload functionality for frontend changes.
- [ ] **Task 3: Database Configuration** (AC: #12, #13, #14, #15, #16)
  - [ ] Subtask 3.1: Write and apply initial database migrations.
  - [ ] Subtask 3.2: Create a seed script to populate the database with test data.
  - [ ] Subtask 3.3: Implement and test Row Level Security policies for data isolation.
- [ ] **Task 4: Developer Tooling** (AC: #17, #18, #19, #20, #21)
  - [ ] Subtask 4.1: Configure code formatters and linters for Python and Flutter.
  - [ ] Subtask 4.2: Set up pre-commit hooks to enforce code quality standards.
  - [ ] Subtask 4.3: Create a recommended VS Code extensions file and debug configurations.

## Dev Notes
This story is foundational for all subsequent development work. Its completion ensures that any developer can quickly and reliably stand up a local environment that mirrors production, minimizing setup friction and "it works on my machine" issues. The key artifacts produced from this story are the `docker-compose.yml`, the `Makefile`, and the database seeding script.

### Relevant Source Tree Information
- `docker-compose.yml`: Defines the multi-container development environment.
- `Makefile`: Provides convenient commands for managing the development lifecycle (`dev`, `setup`, `test`, `clean`).
- `.env.example`: Template for environment variables required by the application.
- `apps/backend/Dockerfile.dev`: Docker build instructions for the development backend service.
- `infra/supabase/migrations`: Location for database schema migration files.
- `apps/backend/app/scripts/seed_data.py`: Script for populating the database with initial test data.

### Important Notes from Previous Stories
- This is a foundational story (0.1), so there are no preceding stories with relevant notes.

## Testing
### Relevant Testing Standards
- **Test File Location:**
  - Backend: `apps/backend/tests/`
  - Frontend: `apps/frontend/test/`
- **Test Standards:**
  - All new features must be accompanied by corresponding unit and integration tests.
  - Tests should be isolated and not depend on the state of other tests.
- **Testing Frameworks and Patterns:**
  - Backend: `pytest` with `asyncio` support. Use `TestClient` for API endpoint testing and mocking for external services.
  - Frontend: `flutter_test` for unit, widget, and integration testing. Use `mocktail` for mocking dependencies.
- **Specific Testing Requirements for This Story:**
  - Write an environment validation test to confirm all services start correctly with `make dev`.
  - Create a health check endpoint (`/healthz`) for the backend and test it.
  - Verify that the database is seeded correctly on startup.
  - Write a simple integration test where the frontend calls a backend API endpoint.

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
