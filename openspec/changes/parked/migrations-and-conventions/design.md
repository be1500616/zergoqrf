# Design: Migrations and Conventions

## Context

`fix-broken-database-connection` makes the 24 existing migrations runnable. It does not, however, enforce that the next 24 are written consistently. This change captures the conventions the team wants to enforce when migrations become a regular activity, plus the small tooling (lint, RLS posture check) that turns the conventions into something a CI job can run.

This change is parked because the conventions are not load-bearing until the second real migration is added. Promoting this draft early is a 5-PR change with no immediate user-visible benefit; promoting it the moment the second migration lands is a 1-PR change because the conventions document what the developer is about to do anyway.

## Goals / Non-Goals

### Goals

- One canonical source of truth for schema: raw SQL files under `infra/supabase/migrations/`.
- One runner: Supabase CLI (`supabase db push` against a linked project, `supabase migration up` locally).
- Five conventions enforced by a small lint script: filename, one-concern, idempotency hints, additive-first, RLS-in-same-file, seeds split.
- A 30-line RLS posture check that fails the build if a tenant table is added without RLS.
- A migrations README that a developer reads before adding a second migration.

### Non-Goals

- New tables. No `app_jobs`, no `app_cache`, no anything that needs a caller.
- New infrastructure. No Redis, no broker, no second data store.
- Migration rewrites. The 24 SQL files stay. We rename the legacy one and document the rest.
- Alembic, Prisma, Drizzle, snapshot dumps.
- Fresh-apply snapshot test, idempotency replay test, `_zergo_migrations` shim table.
- CI workflow `migrations` job. Local-run only.
- `Base.metadata.create_all` removal. That belongs to a follow-up, when the test paths' dependency on it is known.

## Decisions

### Decision 1: Supabase CLI is the runner

The repo has 24 hand-written SQL files. The choice is between (a) keeping that, with the Supabase CLI as the runner, and (b) switching to Alembic / Prisma / Drizzle / an ORM-managed DDL. We pick (a).

- **Runner:** Supabase CLI (`supabase db push` against a linked project, `supabase migration up` against local). It understands the standard layout, writes to `supabase_migrations.schema_migrations` in every environment (local Supabase, cloud project, CI), and is what Supabase Cloud itself uses for production migrations. One tool, one tracking table, one workflow on every machine.
- **Schema source of truth:** raw `.sql` files under `infra/supabase/migrations/`. No model definitions, no DDL in Python, no snapshot dumps. The files already in the tree are the format we keep.
- **Why not Alembic:** the team is shipping SQL, not Python-ORM DDL. Adding Alembic would create a second source of truth (Python model + SQL migration) and a parallel tracking table. The drift would be silent and catastrophic. Skip.
- **Why not Prisma/Drizzle:** same reason — they generate SQL from a non-SQL source. We want SQL to be readable in the PR diff and reviewable by anyone who knows Postgres, not only people who know our ORM.
- **Why not snapshot dumps:** a `pg_dump --schema-only` checked into git is a derived artifact, not a source. It hides the intent of each change, makes diffs unreadable, and is impossible to cherry-pick or revert per-change.

### Decision 2: Five conventions, not ten

The original monolithic proposal listed 10 numbered rules. Five is the right size for the codebase as it stands today. The other five are correct but not enforced.

| # | Convention | Enforced? | Why |
|---|---|---|---|
| 1 | Filename `<UTC-timestamp>_<scope>_<verb>.sql` | Yes (lint) | Catches `add_priority_column.sql`-style breakage immediately. |
| 2 | One concern per file | Yes (lint) | The legacy `0001_init.sql` is the one exception; the rename acknowledges it. |
| 3 | Idempotency hints (`if not exists`, `or replace`) | Yes (lint warn) | Encouraged but not blocking. Pure data migrations MUST have a `where exists` guard. |
| 4 | Additive-first for breaking changes | Yes (lint warn + PR template) | A `drop column` or `set not null` requires the PR description to cite the preceding additive migration. |
| 5 | RLS for tenant tables in the same file | Yes (lint + RLS posture) | A new `create table` in the tenant-scope list MUST be followed in the same file by `enable row level security` and a `create policy`. The RLS posture check is the second line of defense. |
| 6 | Indexes with the table | No (humans catch in review) | The lint is not smart enough to read query plans. |
| 7 | `down.sql` for destructive changes | Yes (lint warn) | If a file contains `drop column` or `drop table`, it MUST have a paired `<same-name>.down.sql`. |
| 8 | Seeds in `seeds/`, not `migrations/` | Yes (lint) | An `insert` in a migration is a warning. |
| 9 | No transactions across files | Yes (runner behavior) | The Supabase CLI wraps each file in a transaction. |
| 10 | No `select *` in policy definitions | No (warn only) | Listed for completeness; not enforced in this change. |

### Decision 3: RLS posture check is a 30-line script, not a spec

The check is:

```python
# scripts/check_rls.py — ponytail: 30 lines, prints the first violation, exits 1.
# Reads tenant scope from tests/fixtures/rls_tenant_scope.json.
# Connects with service role, runs:
#   select tablename from pg_tables where schemaname='public'
#   intersect select tablename from <tenant_scope_list>
#   except
#   select tablename from pg_tables where schemaname='public' and rowsecurity = true
```

`make rls-check` runs it. The test is `tests/test_rls_tenant_isolation.py` (Tier A — pure-Python checks of the script's argument parsing, scope loading, and query construction; no DB required).

### Decision 4: Migrations README is the developer-facing contract

`infra/supabase/migrations/README.md` lists the 5 enforced conventions with one example per rule, points at `scripts/lint_sql.sh` and `scripts/check_rls.py`, and states the filename format. The README is what a developer reads when they add their second migration. It is not a tutorial.

### Decision 5: Local loop extension is two Makefile targets

The base local loop is `make dev` from `fix-broken-database-connection`. This change adds:

- `make lint-sql` — runs `scripts/lint_sql.sh` over the migrations directory.
- `make rls-check` — runs `scripts/check_rls.py` against the local Postgres.

Both are local-run by default. CI integration is a separate small change.

## Tech Choices

- **Lint script:** `bash` + `grep` + `awk`. ~50 lines. No Python, no new dependency.
- **RLS posture check:** Python 3.12, `psycopg` (already a transitive dep via `sqlalchemy`). ~30 lines.
- **Pre-commit hook:** existing `.pre-commit-config.yaml` pattern (already configured in the repo for other linters).
- **Migrations runner:** Supabase CLI (already the runner from `fix-broken-database-connection`). No change.
- **Migrations tracking table:** `supabase_migrations.schema_migrations`. Owned by the CLI. No `_zergo_migrations` shim — that YAGNI shim is gone.

## Risks

- **Risk:** the lint script's heuristics give false positives on the 24 existing migrations.
  - **Mitigation:** the promotion commit includes a one-time pass that adds `if not exists` and `or replace` to the 24 files where they are missing. The diff is large but mechanical.
- **Risk:** the RLS posture check fails on the 24 existing migrations because they were written before the RLS-in-same-file rule existed.
  - **Mitigation:** the check prints the offending table names; the promotion commit includes a follow-up PR that adds `enable row level security` and the matching policies to the legacy tables.
- **Risk:** the README's "5 rules" become 10 rules within 3 months as the team adds migrations.
  - **Mitigation:** the rules are reviewable. If the team needs a 6th rule, the change is a one-paragraph addition to the README + one line in the lint script.

## Open Questions

- Where do the legacy `2025-09-*` migration files land relative to the renamed `20250101000000_init_legacy.sql`? Lexical order: `20250101000000_init_legacy.sql` < `20250924000000_initial_schema.sql` < `20250924000001_add_rls_policies.sql` < ... The rename preserves the apply order. ✅
- Do we add the RLS posture check as its own small change (one PR) before promoting this draft, or roll it in here? Both are fine. The check is a 30-line script. The PR split is the team's call.
