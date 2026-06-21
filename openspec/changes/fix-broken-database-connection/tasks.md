# Tasks: Fix Broken Database Connection

## 1. Settings

- [x] 1.1 Add `database_url: str = ""` to `Settings`. <!-- id: cfg-1 -->
- [x] 1.2 In `model_post_init`, resolve `database_url` from `SUPABASE_{PROFILE}_DB_URL` (dev/test/prod) or `DATABASE_URL` (local) using the same pattern as the existing `supabase_url` resolution. <!-- id: cfg-2 -->
- [x] 1.3 Validate the URL parses with `sqlalchemy.engine.url.make_url` and uses `postgresql+asyncpg` or `postgresql` scheme. Fail fast with one readable message. <!-- id: cfg-3 -->

## 2. Database Module

- [x] 2.1 Remove the `getattr(settings, "database_url", None)` and the `db:5432` fallback in `core/database.py`. Use `settings.database_url` directly. <!-- id: db-1 -->
- [x] 2.2 Add FastAPI startup hook in `main.create_app` that warms the engine (`await engine.connect()`) and shutdown hook (`await engine.dispose()`). <!-- id: db-2 -->
- [x] 2.3 Add a `ponytail:` comment above `create_async_engine` noting that pool tuning is deferred to load measurement. <!-- id: db-3 -->

## 3. Supabase Client Collapse

- [x] 3.1 Reduce `apps/backend/app/common/supabase_client.py` to: `get_supabase_service` (async, no cache), `get_supabase_anon` (async, no cache), `user_supabase(access_token)` (sync one-shot). <!-- id: sup-1 -->
- [x] 3.2 Hold long-lived clients in FastAPI `app.state.supabase_service` and `app.state.supabase_anon`. Initialize during `create_app()`. <!-- id: sup-2 -->
- [x] 3.3 Remove all `@lru_cache` on async functions. Remove the sync factories that block the event loop. <!-- id: sup-3 -->
- [x] 3.4 Audit existing call sites and replace any usage of the old `get_supabase()` / `get_async_supabase()` patterns. <!-- id: sup-4 -->

## 4. Makefile

- [x] 4.1 Add `dev` target to root `Makefile` that runs `supabase start` and applies migrations in `infra/supabase/migrations/` in lexical order. Fall back to `docker compose up -d db` + `psql` loop if the Supabase CLI is not on PATH. <!-- id: mk-1 -->
- [x] 4.2 Document `make dev` in `apps/backend/README.md` (one paragraph). <!-- id: mk-2 -->

## 5. Seed Script

- [x] 5.1 Update `apps/backend/app/scripts/seed_data.py` to read from `settings.database_url` instead of its own ad-hoc env load. <!-- id: seed-1 -->

## 6. Tests

- [x] 6.1 Add `tests/test_database_config.py` (Tier A) that asserts profile resolution and failure modes using `pytest.MonkeyPatch`. <!-- id: tst-1 -->

## 7. Verification

- [ ] 7.1 `make dev` brings up local Postgres and applies all 24 migrations in lexical order without error. <!-- id: v-1 -->
- [ ] 7.2 Backend starts in `dev` profile with `SUPABASE_DEV_DB_URL` set; `/healthz` returns 200. <!-- id: v-2 -->
- [x] 7.3 Backend fails to start in `dev` profile when `SUPABASE_DEV_DB_URL` is empty; the error message names the missing variable. <!-- id: v-3 -->
- [ ] 7.4 `pytest` (no flags) is green. <!-- id: v-4 -->
- [x] 7.5 `openspec validate fix-broken-database-connection --strict` passes. <!-- id: v-5 -->
