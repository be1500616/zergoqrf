# ZERGO QR Monorepo

A production-ready monorepo for ZERGO QR following the PRD and vertical slice clean architecture.

- Frontend: Flutter (iOS, Android, Web) with GetX, GoRouter, Supabase
- Backend: FastAPI (Python 3.12+) with vertical slice modules and Supabase integration
- Database: Supabase Postgres with RLS and realtime
- CI/CD: GitHub Actions
- Dev: Docker (backend), hot reload for both frontend and backend

## Repository Structure

- `apps/frontend/` — Flutter app (feature slices under `lib/features`)
- `apps/backend/` — FastAPI app (feature slices under `app/features`)
- `infra/supabase/` — SQL migrations, RLS policies, and seed data
- `.github/workflows/` — CI pipelines for backend and frontend

## Quick Start

1. Backend (local)

- Copy `.env.example` to `.env` and fill Supabase keys
- Install Python 3.12+ and `uv` or `pip`
- Run dev server:

```
cd apps/backend
# instructions added in backend README once generated
```

2. Frontend (local)

- Install Flutter (stable, latest)
- Copy `apps/frontend/.env.example` to `.env`
- Run:

```
cd apps/frontend
# instructions added in frontend README once generated
```

3. Docker (backend)

```
docker compose up --build backend
```

## Environments

- `.env` (root-level shared defaults and backend)
- `apps/frontend/.env` (Flutter runtime vars via flutter_dotenv or dart-define)

## Notes

- Vertical slice architecture: each feature has domain, application, infrastructure, presentation layers.
- Supabase RLS enforces multi-tenant isolation.
