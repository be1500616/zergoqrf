# Project Context: ZERGO QR

## Purpose
ZERGO QR is a production-ready restaurant management system focused on QR-based ordering and a streamlined restaurant onboarding experience. It aims to provide early-stage restaurant owners with an easy-to-use platform for digital menus, order management, and customer engagement.

## Tech Stack
### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Dependency Management**: `uv` / `pip`
- **Linting/Formatting**: `ruff`, `mypy`
- **Testing**: `pytest`

### Frontend
- **Framework**: Flutter (iOS, Android, Web)
- **State Management**: GetX
- **Navigation**: GoRouter
- **Environment Management**: `flutter_dotenv`
- **Testing**: `flutter test`

### Database & Auth
- **Provider**: Supabase (PostgreSQL)
- **Security**: Row Level Security (RLS)
- **Functions**: Supabase Edge Functions

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Project Conventions

### Code Style
- **Backend**: Follows PEP 8 guidelines, uses Type Hints.
- **Frontend**: Follows standard Flutter style guide, uses PascalCase for classes and camelCase for methods/variables.
- **Commits**: Conventional Commits (`feat`, `fix`, `docs`, `chore`, `test`, `refactor`).

### Architecture Patterns
- **Vertical Slice Architecture**: Each feature is organized into its own slice containing domain, application, infrastructure, and presentation layers.
- **Multi-tenant Isolation**: Enforced via Supabase RLS.

### Testing Strategy
- **Backend**: Unit and integration tests using `pytest`.
- **Frontend**: Widget and unit tests using `flutter test`.
- **Integration**: Full system testing with Docker environments.

### Git Workflow
- **Branching**: Feature-based branching (`feature/scope-description`).
- **Merge Strategy**: Merge to `main` via PRs or `no-ff` merges after testing.

## Domain Context
- **Restaurant Onboarding**: Multi-step registration flow (Info, Owner, Review).
- **QR Management**: Generation and tracking of QR codes for tables.
- **Menu Management**: Categories, items, and pricing.
- **Order Flow**: Diner scans QR, browses menu, places order, tracked by staff.

## Important Constraints
- **Multi-tenancy**: High priority on tenant isolation.
- **Scalability**: Designed for 5-10 concurrent users initially with growth potential.

## External Dependencies
- Supabase (Auth, Database, Edge Functions)
- Docker
- Flutter SDK
- Python 3.12+

