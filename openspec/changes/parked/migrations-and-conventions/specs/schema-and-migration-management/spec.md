# Capability: Schema and Migration Management

## ADDED Requirements

### Requirement: One source of truth for schema

The schema MUST be defined by raw SQL files under `infra/supabase/migrations/`. No ORM-managed DDL, no `pg_dump` snapshots, no `Base.metadata.create_all` in production code paths. The SQL files are reviewable in a PR diff, runnable by the same tool on every machine, and the only place a schema change can land.

#### Scenario: a developer tries to alter schema in Python

- **GIVEN** a feature requires adding a column to `orders`
- **WHEN** the developer reaches for `Base.metadata.create_all` or an ORM migration
- **THEN** the contribution guide and `infra/supabase/migrations/README.md` redirect them to a SQL migration under `infra/supabase/migrations/`; the PR template rejects "modified Python ORM models" as the only schema change

### Requirement: One runner, applied uniformly

The Supabase CLI MUST be the migration runner. `supabase db push` is used against a linked project (cloud), `supabase migration up` is used locally, and `supabase_migrations.schema_migrations` is the single applied-set table in every environment.

#### Scenario: local apply

- **GIVEN** `supabase start` is running
- **WHEN** the developer runs `make migrate` (or `make dev` from `fix-broken-database-connection`)
- **THEN** every file under `infra/supabase/migrations/` is applied in lexical order; the applied set is recorded in `supabase_migrations.schema_migrations`; running `make migrate` a second time is a no-op

#### Scenario: cloud apply

- **GIVEN** the project is linked to a Supabase cloud project
- **WHEN** CI runs `supabase db push --linked --password "$SUPABASE_DB_PASSWORD"`
- **THEN** unapplied migrations run, the applied set is updated, and the run is gated by the migration job's other checks (`make lint-sql`, RLS posture check)

### Requirement: Filename and one-convention rules

Every migration filename MUST match `<UTC-timestamp>_<scope>_<verb>.sql`, where the timestamp is `YYYYMMDDHHMMSS` in UTC, the scope is a short table group, and the verb is the action (`create`, `add`, `alter`, `drop`, `seed`). Each migration MUST address one concern. `make lint-sql` is the gate.

#### Scenario: a migration is added with the wrong filename

- **GIVEN** a developer adds `add_priority_column.sql` (no timestamp)
- **WHEN** they run `make lint-sql` or commit with the pre-commit hook
- **THEN** the command exits non-zero with a message naming the offending file and the expected pattern

#### Scenario: a migration bundles two concerns

- **GIVEN** a developer writes a single file that adds a column to `orders` and creates a `refunds` table
- **WHEN** `make lint-sql` runs
- **THEN** the command exits non-zero with a message suggesting two separate files

### Requirement: Idempotency hints

Migrations SHOULD be safe to re-apply. They MUST use `create ... if not exists`, `drop ... if exists`, `create or replace`, and `on conflict do nothing` where supported. Pure data migrations (backfills) MUST be guarded by a `where exists` / `where not exists` clause and a comment explaining the guard. The lint script warns on missing hints; it does not block.

#### Scenario: a migration is re-applied

- **GIVEN** the migrations have been applied once already
- **WHEN** `make migrate` runs again
- **THEN** every statement that uses `if not exists` or `or replace` succeeds; statements without idempotency hints may fail and the failure is reported by the runner with the file and statement number

### Requirement: Additive-first for breaking changes

A breaking schema change MUST be split across at least two PRs: an additive change first (new column nullable or with default; new table), a backfill, then a follow-up PR that enforces the constraint or drops the old column. The follow-up PR MUST cite the preceding additive migration in its description. The PR template and the lint script enforce this.

#### Scenario: a `set not null` ships before the backfill is live

- **GIVEN** PR 1 added `orders.priority text` as nullable and is younger than 30 days
- **WHEN** PR 2 contains `alter table orders alter column priority set not null`
- **THEN** the PR template and the review checklist block the change unless the description cites the additive PR

### Requirement: `down.sql` for destructive changes

A migration that drops a table, drops a column, or renames a column or table MUST be paired with `<same-name>.down.sql` containing the inverse DDL. Additive-only migrations do not need a `down.sql`. The lint script enforces this.

#### Scenario: a column is dropped without a `down.sql`

- **GIVEN** a migration contains `alter table orders drop column legacy_priority`
- **WHEN** `make lint-sql` runs
- **THEN** the command exits non-zero and names the missing `<migration>.down.sql`

### Requirement: RLS in the same file as the table

Any `create table` whose name is in the tenant-scope list MUST be followed in the same migration file by `alter table ... enable row level security` and at least one `create policy` (or a `comment` block explaining why RLS is intentionally off). This is the first line of defense; the RLS posture check in the `multi-tenant-rls-posture` spec is the second.

#### Scenario: a tenant table is added without RLS

- **GIVEN** a developer adds `public.discounts` and forgets `enable row level security`
- **WHEN** `make rls-check` runs
- **THEN** the command exits non-zero and names the table, the missing flag, and the policy that should be added

### Requirement: Seeds are separate from migrations

Seed data lives under `infra/supabase/seeds/` and MUST be idempotent. Seeds MUST NOT run in CI unless `APP_SEED=on`. Seeds MUST NOT contain DDL.

#### Scenario: a developer puts `insert` in a migration

- **GIVEN** a new migration under `infra/supabase/migrations/`
- **WHEN** the file contains `insert into ...`
- **THEN** `make lint-sql` warns and the PR template flags it; the correct location is `infra/supabase/seeds/`

#### Scenario: CI runs migrations

- **GIVEN** `APP_SEED` is not set
- **WHEN** CI runs the migration job
- **THEN** seeds are not applied; tests build their own data via fixtures

### Requirement: No snapshot dumps or `pg_dump` artifacts in migrations

The migrations directory MUST NOT contain `pg_dump --schema-only` output or any file with a name that suggests a snapshot. The convention is forward-only SQL, one concern per file.

#### Scenario: someone checks in `0001_full_schema.sql`

- **GIVEN** a developer regenerates the schema with `pg_dump` and commits the result
- **WHEN** `make lint-sql` runs
- **THEN** the command exits non-zero and points the developer at the `infra/supabase/migrations/README.md` rule against snapshot dumps

### Requirement: Migrations MUST be applied transactionally

Each migration file MUST be wrapped in a single transaction by the runner. A failure MUST roll back the entire file. Cross-file transactions are forbidden.

#### Scenario: a migration has a syntax error in the second statement

- **GIVEN** the file has a valid `create table` followed by an invalid `alter table`
- **WHEN** the runner applies the file
- **THEN** the entire file is rolled back, no tables from that file remain, and the failure is reported with the statement number

### Requirement: Migrations README is the developer-facing contract

`infra/supabase/migrations/README.md` MUST list the 5 enforced conventions with one example per rule, MUST point at `scripts/lint_sql.sh` and `scripts/check_rls.py`, and MUST state the filename format. The README is what a developer reads when they add their second migration.

#### Scenario: a developer adds their second migration

- **GIVEN** `fix-broken-database-connection` has landed
- **WHEN** the developer opens the PR adding a new migration
- **THEN** the PR description includes a link to `infra/supabase/migrations/README.md` and the migration passes `make lint-sql` and `make rls-check`

### Requirement: Config is checked in

`infra/supabase/config.toml` MUST exist and be checked in. It pins the Supabase CLI project config (project id, ports, ignored schemas). The `ignored_schemas` list MUST include `storage`, `auth`, `realtime`, `supabase_migrations`, `graphql`, `vault`, `pgbouncer` — the schemas the CLI should not touch.

#### Scenario: a developer runs `supabase start` on a clean machine

- **GIVEN** `infra/supabase/config.toml` is present
- **WHEN** the developer runs `supabase start`
- **THEN** the CLI reads the checked-in config, ignores the schemas it should not touch, and the local stack starts with the same ports and behavior on every machine
