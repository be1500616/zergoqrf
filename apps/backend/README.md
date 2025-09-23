# ZERGO Backend (FastAPI)

FastAPI 0.110+ app structured using vertical slice clean architecture with Supabase integration.

## Run locally

Prereqs: Python 3.12+, `uv` (optional), `.env` at repo root with Supabase creds.

```
# From repo root one-time
cp .env.example .env  # fill values

# Install deps
cd apps/backend
pip install -U pip
pip install -e .

# Run dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```
pytest -q
```

## Project layout

- `app/core` — settings, logging
- `app/common` — exceptions, supabase client
- `app/features/<feature>` — each has `domain/`, `application/`, `infrastructure/`, `presentation/`
- `tests/` — pytest unit tests

## Env vars

- `SUPABASE_URL` (required)
- `SUPABASE_ANON_KEY` (dev)
- `SUPABASE_SERVICE_ROLE_KEY` (server)
- `SUPABASE_JWT_SECRET` (verify tokens)
- `ALLOWED_ORIGINS` comma-separated list
