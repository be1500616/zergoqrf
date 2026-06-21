# Design: Fix Broken Database Connection

## Context

The repo commits to Supabase in production. The runtime, however, has three concrete bugs that make the backend unstartable. Everything else — the RLS posture gap, the missing migration runner, the missing queue, the speculative `app_jobs` table — is downstream of these three and impossible to evaluate until they are fixed.

This change is the smallest diff that makes the backend runnable. It does not introduce new architecture, new tables, or new infrastructure. It deletes the `db:5432` ghost, wires the URL into `Settings`, and collapses the Supabase client to the version the codebase actually needs.

## Goals / Non-Goals

### Goals

- `Settings.database_url` is populated for every profile and validated at startup.
- `core/database.py` reads only from `Settings`. No ghost hostnames.
- The Supabase client surface is 2 async factories + 1 one-shot helper. No `@lru_cache` on async functions.
- A developer can run `make dev` and have a usable local database with all migrations applied.
- Tier A tests pass with no DB available.

### Non-Goals

- New tables. No `app_cache`, no `app_jobs`, no `refunds`, no anything.
- New tools. No lint scripts, no RLS posture check, no fresh-apply test, no snapshot fixture.
- New infrastructure. No Redis, no broker, no second data store.
- Migration rewrites. The 24 SQL files stay. We just give them a runner.
- Replacing SQLAlchemy. The engine stays. We use it correctly.

## Decisions

### Decision 1: `Settings.database_url` is profile-aware

Resolved at startup, validated, fail-fast. Mirrors the pattern already in `Settings.model_post_init` for the Supabase URL/anon key.

| Profile | Source | Format |
| --- | --- | --- |
| `local` | `DATABASE_URL` (env) | `postgresql+asyncpg://...` direct connection |
| `dev` | `SUPABASE_DEV_DB_URL` | `postgresql+asyncpg://...` Supabase pooler (port 6543) |
| `test` | `SUPABASE_TEST_DB_URL` | `postgresql+asyncpg://...` CI project |
| `prod` | `SUPABASE_PROD_DB_URL` | `postgresql+asyncpg://...` Supabase pooler |

The pooler (transaction mode) is the prod default because Supabase recommends it for serverless and our backend is the only writer in MVP. Direct connection is used for `local` because the Supabase CLI exposes a direct port.

If the URL is missing or unparseable, startup fails with a single message naming the profile and the missing key. No fallback, no `getattr`, no ghost hostname.

### Decision 2: `core/database.py` reads only from `Settings`

```python
# ponytail: single source of truth, no fallback. If the URL is missing,
# startup must fail loudly, not silently route to a ghost host.
engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level.lower() == "debug",
    future=True,
)
```

Pool tuning is left at SQLAlchemy defaults. We add `pool_size`, `max_overflow`, `pool_timeout` only when a profiler says so. The `ponytail:` comment names the upgrade path.

### Decision 3: Supabase client collapse

`supabase_client.py` becomes:

```python
# ponytail: collapse 6 factories to 2 + 1. The long-lived clients are
# held in app.state. User-scoped clients are created on demand at the
# call site (tokens rotate, do not cache).
```

- `get_supabase_service()` — async factory, called once during FastAPI startup, result stored in `app.state.supabase_service`. Uses service role key.
- `get_supabase_anon()` — async factory, called once during startup, result stored in `app.state.supabase_anon`. Uses anon key.
- `user_supabase(access_token: str)` — sync one-shot, returns a fresh async client with the user's JWT. Not cached. Use at the call site when an endpoint needs RLS-enforced reads.

### Decision 4: `make dev` is the one command

```makefile
# ponytail: one command, one outcome. If supabase CLI is missing, fall back
# to docker compose. Either way, migrations apply automatically.
dev:
	@if command -v supabase >/dev/null 2>&1; then \
		supabase start && supabase migration up; \
	else \
		docker compose up -d db && \
		for f in infra/supabase/migrations/*.sql; do \
			psql "$$DATABASE_URL" --single-transaction --set ON_ERROR_STOP=on -f $$f; \
		done; \
	fi
```

No `db-up`, `db-down`, `migrate`, `migrate-reset`, `smoke-db`, `lint-sql`, `test-tier-a`, `test-tier-b`. Those are pre-existing tier names that belong to a future change. Today the only command a developer needs is `make dev`.

### Decision 5: Tier A test is enough

`tests/test_database_config.py` is the only new test. It uses `pytest.MonkeyPatch` to set env vars and asserts:

- For each profile, `Settings()` returns a non-empty `database_url`.
- A missing URL raises `ValueError` with a message naming the profile and the missing key.
- The URL is parsed as `postgresql+asyncpg://` (no other schemes accepted).

No DB connection is required. No Tier B. No fixture for `supabase start`. We do not test the actual database roundtrip in this change — that belongs to the first feature change that needs a real query, where the test cost is justified.

## Tech Choices

- **Engine:** keep `SQLAlchemy[asyncpg]`. The team is already using it. No migration to raw `asyncpg` in this change.
- **Migrations runner:** `supabase migration up` (CLI present) or `psql --single-transaction --set ON_ERROR_STOP=on` in a `for` loop over `infra/supabase/migrations/*.sql`. The `psql` path is only because some hosts may not have the Supabase CLI. Same tracking behaviour: each file applies once, errors stop on the first failure.
- **Config pattern:** extend the existing `Settings.model_post_init` to do `database_url` resolution. No new settings classes, no factory functions.
- **Test framework:** `pytest` with `MonkeyPatch`. No `pytest-postgresql`, no testcontainers, no real DB.

## Risks

- **Risk:** the existing tests that imported the ghost fallback break when the fallback is removed.
  - **Mitigation:** those tests were already broken (they were talking to `db:5432`, which does not resolve). Removing the fallback exposes a known-broken state and gives us a clean baseline.
- **Risk:** `SUPABASE_*_DB_URL` names conflict with the `add-dev-prod-supabase-workflow` change.
  - **Mitigation:** we use the same key naming pattern as that change (`SUPABASE_{PROFILE}_{KEY}`). If it lands first, we consume it. If we land first, it consumes us. Either way, the names match.
- **Risk:** `make dev` runs migrations that were never run before and surface latent schema bugs.
  - **Mitigation:** this is the point. The Tier B fresh-apply test that would have caught this is in the parked `migrations-and-conventions` change. For this change, `make dev` is itself the smoke test: if migrations apply cleanly, we're good; if not, the loop fails loudly with the file and line.

## Open Questions

- None. The change is the minimum diff to make the backend runnable. Anything else is parked.
