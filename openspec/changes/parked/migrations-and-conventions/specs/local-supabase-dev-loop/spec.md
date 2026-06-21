# Capability: Local Supabase Dev Loop

This capability extends the base `make dev` workflow established in `fix-broken-database-connection`. The base workflow is the broken-thing fix; this capability is the conventions and guardrails layered on top of it.

## ADDED Requirements

### Requirement: One-command local database (base)

The base local loop is `make dev` from `fix-broken-database-connection`. It brings up `supabase start` (preferred) or `docker compose up -d db` (fallback) and applies all migrations in `infra/supabase/migrations/` in lexical order. This requirement is satisfied by `fix-broken-database-connection` and is restated here only as a reference point for the extensions.

#### Scenario: clean laptop, no Supabase CLI

- **GIVEN** Docker is installed and the developer has no Supabase CLI
- **WHEN** they run `make dev`
- **THEN** a Postgres 15 container starts on a documented port, migrations apply, and the backend can connect

#### Scenario: Supabase CLI is available

- **GIVEN** the Supabase CLI is installed
- **WHEN** they run `make dev`
- **THEN** `supabase start` runs and migrations apply, including the `studio`, `auth`, `realtime`, and `storage` services provided by the CLI

### Requirement: `make lint-sql` is a developer-local guardrail

A developer MUST be able to run `make lint-sql` locally and have it pass on a clean checkout. The target runs `scripts/lint_sql.sh` over the migrations directory. The script enforces the 5 conventions from `infra/supabase/migrations/README.md`.

#### Scenario: a developer adds a migration that violates the filename rule

- **GIVEN** the developer adds `add_priority_column.sql` (no timestamp)
- **WHEN** they run `make lint-sql`
- **THEN** the command exits non-zero with a message naming the offending file and the expected pattern

#### Scenario: a developer adds a migration that bundles two concerns

- **GIVEN** the developer writes a single file that touches `orders` and `cart`
- **WHEN** they run `make lint-sql`
- **THEN** the command exits non-zero with a message suggesting two separate files

### Requirement: `make rls-check` is a developer-local guardrail

A developer MUST be able to run `make rls-check` locally and have it pass on a fresh `supabase start`. The target runs `scripts/check_rls.py` against the local Postgres. The script asserts RLS posture on the tenant-scope list.

#### Scenario: a developer adds a tenant table without RLS

- **GIVEN** the developer adds `public.discounts` and forgets `enable row level security`
- **WHEN** they run `make rls-check`
- **THEN** the command exits non-zero, names the table, and points at the missing `enable row level security` line

### Requirement: Pre-commit hook runs the lint

`pre-commit run --all-files` MUST run `scripts/lint_sql.sh --staged` on changed `.sql` files and block the commit on a violation. The hook is a local-run guardrail; CI integration is a separate small change.

#### Scenario: a developer commits a migration that violates the filename rule

- **GIVEN** the developer has `add_priority_column.sql` staged
- **WHEN** they run `git commit`
- **THEN** the pre-commit hook runs the lint, the lint fails, and the commit is blocked with a single readable message

### Requirement: `infra/supabase/README.md` is the developer-facing entry point

`infra/supabase/README.md` MUST document the local loop end-to-end: `make dev` boots + applies migrations; `make lint-sql` checks conventions; `make rls-check` asserts RLS on tenant tables. The README is what a developer reads when they set up the project for the first time.

#### Scenario: a new developer joins the project

- **GIVEN** the new developer has Docker and the Supabase CLI installed
- **WHEN** they read `infra/supabase/README.md` and run the documented commands
- **THEN** they have a usable local database, a green lint, and a green RLS posture check within 5 minutes

### Requirement: Smoke check before any feature work

`make smoke-db` (carried over from the original proposal) MUST open a connection, run `select 1`, count tables in `public`, and assert RLS is enabled on every tenant-scope table. The command MUST exit non-zero on any failure with a single readable message. This is the broader smoke check; `make rls-check` is the focused RLS subset.

#### Scenario: a missing migration

- **GIVEN** a developer added a tenant table in a new migration but forgot to enable RLS
- **WHEN** they run `make smoke-db`
- **THEN** the command exits non-zero, names the table, and points at the missing `enable row level security` line

### Requirement: Tier A vs Tier B split (deferred)

The original proposal included a Tier A vs Tier B test split. This requirement is **deferred** to a follow-up change once we have a real Tier B test. The local loop in this change is local-run only; CI integration is a separate, smaller change.

#### Scenario: a developer runs `pytest` offline (deferred)

- **GIVEN** the developer is offline and `DATABASE_URL` is unreachable
- **WHEN** they run `pytest`
- **THEN** (future) Tier A tests run and pass; Tier B tests are reported as skipped with the reason "tier_b requires DATABASE_URL"

This scenario is parked. The Tier A / Tier B split is not load-bearing until we have a Tier B test that depends on a live DB.
