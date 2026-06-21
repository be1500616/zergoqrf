# Capability: Supabase Postgres Runtime

## ADDED Requirements

### Requirement: Profile-aware Postgres connection

The backend MUST resolve a single `database_url` per active profile (`local`, `dev`, `test`, `prod`) and fail fast at startup if it is missing or unparseable for the chosen profile.

#### Scenario: dev profile starts with valid Supabase pooler URL

- **GIVEN** `APP_PROFILE=dev` and `SUPABASE_DEV_DB_URL` is set to a reachable Supabase pooler URL
- **WHEN** `Settings()` is instantiated
- **THEN** `Settings.database_url` is populated, parseable as `postgresql+asyncpg://` or `postgresql://`, and not empty

#### Scenario: profile starts with missing URL

- **GIVEN** `APP_PROFILE=dev` and `SUPABASE_DEV_DB_URL` is empty
- **WHEN** `Settings()` is instantiated
- **THEN** instantiation fails with a single `ValueError` message naming the profile and the missing variable; no module-level import side effects leak partial state

#### Scenario: local profile uses DATABASE_URL directly

- **GIVEN** `APP_PROFILE=local` and `DATABASE_URL=postgresql+asyncpg://localhost:5432/postgres`
- **WHEN** `Settings()` is instantiated
- **THEN** `Settings.database_url` is `postgresql+asyncpg://localhost:5432/postgres` (no fallback to a ghost hostname)

### Requirement: No ghost hostnames in the runtime

The database engine MUST be created with `Settings.database_url` and nothing else. The runtime MUST NOT contain a hardcoded fallback to `db:5432` or any other hostname.

#### Scenario: a developer deletes the env var

- **GIVEN** the developer runs the backend with no `DATABASE_URL` and no `SUPABASE_DEV_DB_URL`
- **WHEN** the backend starts
- **THEN** startup fails loudly with the missing-variable message; no implicit connection to a ghost host is attempted

### Requirement: One durable data plane

The backend MUST use a single Postgres for OLTP. It MUST NOT introduce a second stateful data store in this change.

#### Scenario: a feature needs short-lived state

- **GIVEN** a future feature requires cache or async work
- **WHEN** the developer reaches for a tool
- **THEN** the parked `app-jobs-and-realtime-fanout` change is the right place; this change does not add tables speculatively

### Requirement: Connection lifecycle

The backend MUST warm the connection pool on startup and dispose it on shutdown.

#### Scenario: graceful shutdown

- **GIVEN** the backend is running with active connections
- **WHEN** it receives SIGTERM
- **THEN** the FastAPI shutdown hook calls `engine.dispose()` so in-flight queries finish and the pool is closed cleanly
