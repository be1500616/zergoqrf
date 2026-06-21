# Proposal: Fix Broken Database Connection

## Why

The backend cannot connect to a database today. Three concrete bugs, all in the runtime:

1. `apps/backend/app/core/config.py` has no `database_url` field on `Settings`. It also has no `database_url` env var resolution.
2. `apps/backend/app/core/database.py` reads `settings.database_url` via `getattr(settings, "database_url", None)` (always returns `None`) and silently falls back to `postgresql+asyncpg://postgres:postgres@db:5432/postgres`. There is no `db` service in `docker-compose.yml`. Any code path that hits `get_db_session()` either fails to start or talks to a hostname that does not resolve.
3. `apps/backend/app/common/supabase_client.py` ships six near-duplicate factories (sync/async × service/anon/user). The async ones are wrapped in `@lru_cache`, which FastAPI cannot await. The sync ones block the event loop on every Supabase REST call.

Until these three are fixed, the backend cannot run locally, tests cannot hit a real DB, and every downstream concern (RLS posture, migration runner, queue/cache tables) is a guess because we have no working query to measure.

## What Changes

- Add `database_url` to `Settings`, resolved per active profile from `SUPABASE_{PROFILE}_DB_URL` (dev/test/prod) or `DATABASE_URL` (local). Validate the URL parses and is reachable at startup. Fail fast with a single readable error.
- Remove the ghost `db:5432` fallback in `core/database.py`. Use only the URL from `Settings`.
- Collapse `supabase_client.py` to one async service-role factory + one async anon factory. User-scoped clients are created on demand at the call site (no cache, tokens rotate). Hold the long-lived async clients in FastAPI `app.state`, not in module globals.
- Add `make dev` that runs `supabase start` (preferred) or `docker compose up -d db` (fallback) and applies the migrations in `infra/supabase/migrations/`. One command, one outcome: a working local DB.
- Add a Tier A unit test that asserts `Settings.database_url` is populated for each profile and that startup fails when it isn't.

## Non-Goals

- No new tables (`app_cache`, `app_jobs`, or anything else). Tables are added when a feature needs them, in a separate OpenSpec change.
- No RLS posture check, no migration lint, no fresh-apply test, no snapshot fixture. Those belong to the parked `migrations-and-conventions` change.
- No new env-isolation contract. We use the profile contract that `add-dev-prod-supabase-workflow` already defines. If that change lands first, this one consumes it. If this lands first, we adopt the same key names (`SUPABASE_{PROFILE}_DB_URL`) and `add-dev-prod-supabase-workflow` is updated to reference them.
- No Redis, no broker, no cache module, no queue module. Postgres only.
- No replacing `Base` / SQLAlchemy. The engine stays. We just stop pretending `db:5432` exists.
- No changes to the 24 existing SQL migrations. They stay as-is and become runnable by `make dev`.

## Capabilities

### New Capabilities

- `supabase-postgres-runtime`: profile-aware Postgres connection management for backend, validated at startup, used uniformly for OLTP. The first and only capability in this change.

### Modified Capabilities

- None. `openspec/specs/` is empty; this introduces the first baseline capability.

## Impact

- `apps/backend/app/core/config.py`: add `database_url` field. Resolve from per-profile env in `model_post_init` with fail-fast validation.
- `apps/backend/app/core/database.py`: remove ghost fallback. Use `settings.database_url` only. Add FastAPI startup/shutdown hooks for engine warmup and `engine.dispose()`.
- `apps/backend/app/common/supabase_client.py`: collapse to 2 factories. Remove `@lru_cache` on async functions. Provide a one-shot helper for user-scoped clients.
- `apps/backend/app/main.py`: initialize Supabase clients in `app.state` during `create_app()`.
- `apps/backend/app/scripts/seed_data.py`: update URL source to `settings.database_url` so the seed script stops reading its own ad-hoc env.
- `Makefile` (root): add `dev` target that runs `supabase start` and applies migrations in one shot.
- `tests/test_database_config.py` (new, Tier A): asserts profile resolution and failure modes. No DB required.

## Success Criteria

- `make dev` brings up a usable local Postgres and applies every migration in `infra/supabase/migrations/` in lexical order. On a clean machine with the Supabase CLI, the loop finishes in under 5 minutes.
- Backend starts in `dev` profile using only `SUPABASE_DEV_DB_URL` (or the appropriate profile key). No `db:5432` ghost. No `REDIS_URL` requirement. No `getattr` warning.
- `pytest` (Tier A) passes with no DB available. `test_database_config.py` is green.
- `apps/backend/app/common/supabase_client.py` is reduced from 6 factories to 2 async factories + 1 one-shot helper. No `@lru_cache` on async functions.
- The backend can be imported and `/healthz` returns 200 in all four profiles (`local`, `dev`, `test`, `prod`) with appropriate env vars set.

## Dependencies

- Soft dependency on the env-isolation contract from `add-dev-prod-supabase-workflow`. If that lands first, this change consumes it. If this lands first, the key names (`SUPABASE_{PROFILE}_DB_URL`) match so the two changes compose without conflict.
- Blocks every other runtime-touching OpenSpec change (`add-phased-kiosk-kds-mobile-ordering-rollout`, parked `migrations-and-conventions`, parked `app-jobs-and-realtime-fanout`).

## Out of Scope (Parked Changes)

The proposal we previously drafted (`unify-supabase-postgres-runtime`) covered five capabilities. This change lifts one of them — the one that fixes a concrete bug today — and parks the rest as separate drafts:

- `parked/migrations-and-conventions`: rename `0001_init.sql`, add `scripts/lint_sql.sh` and pre-commit hook, add RLS posture check, write `infra/supabase/migrations/README.md`. Lands after this change, when the team is adding the second or third real schema change.
- `parked/app-jobs-and-realtime-fanout`: `app_jobs` table, `app_cache` table, queue worker, outbox-style status fan-out. Lands when a feature in the tree actually needs async work, in the same PR as the caller.

Both parked drafts are intentional YAGNI. We do not build the table or the worker until a caller exists.
