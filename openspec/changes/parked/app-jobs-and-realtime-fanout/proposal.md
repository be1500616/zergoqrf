# Proposal: App Jobs and Realtime Fan-Out

**Status:** parked. Not active. Will be promoted to an active OpenSpec change when a feature in the tree actually needs async work (queue, scheduled job, fan-out).

## Why

The MVP needs no queue, no scheduled job runner, and no async fan-out today. There is no `notifications` module, no email sender, no kitchen fan-out code. The only "queue-shaped" comment in the tree is in `phone_auth_use_cases.py` line 338 ("this would typically check a cache/database"). That is a thought, not a need.

When a feature finally calls for async work, the smallest viable implementation is:

- An `app_jobs` table with `FOR UPDATE SKIP LOCKED` claim semantics.
- A thin `queue.py` helper (`enqueue`, `claim_batch`, `mark_done`, `mark_failed`).
- An in-process asyncio worker started during FastAPI `create_app`.
- The caller (the feature) writes the row + enqueues the job in the **same transaction** (transactional outbox).
- A single Tier B integration test that proves the round-trip.

This change captures all of the above as a parked draft so we can promote it in one PR the moment a caller exists.

## What Changes

When promoted, the change lands in the same PR as the caller. The diff contains:

- Migration `2026????000000_<scope>_app_jobs.sql` with `app_jobs(id, queue, payload jsonb, run_at, attempts, locked_until, last_error)` and RLS locked to `service_role`.
- `apps/backend/app/common/queue.py` with `enqueue`, `claim_batch`, `mark_done`, `mark_failed` over `FOR UPDATE SKIP LOCKED`.
- `apps/backend/app/common/worker.py` (in-process asyncio task, started in `create_app`).
- The caller wired to `enqueue` in the same transaction as its write.
- A single Tier B integration test for the caller.

## Non-Goals

- No `app_cache` table. The first cache use-case MUST be a separate promotion with its own justification. The parked draft does not even include `app_cache`; if a future change needs cache, that change is its own OpenSpec.
- No external broker (RabbitMQ, SQS, Kafka). The worker is `asyncpg` + an asyncio loop. ~80 lines total.
- No `procrastinate` or `arq` dependency. Add only if SLOs are measured and missed.
- No SLO numbers. SLOs get written **after** we have one caller's data, not before.
- No multi-process worker. The first worker is in-process. Scale-out is a future change.
- No custom WebSocket gateway. Supabase Realtime channels handle push to clients.
- No Redis. No Memcached. No second data store.
- No fresh-apply snapshot test for the migration. The migration is small and the `migrations-and-conventions` promotion adds the lint.

## Capabilities

### New Capabilities

- `postgres-cache-queue`: Postgres table (`app_jobs`) plus thin Python helpers used for async jobs, in place of any external broker. Includes the worker. (No `app_cache` until a separate use-case.)
- `outbox-fanout`: the outbox pattern. The API write commits the row + inserts an `app_jobs` row in the **same transaction**. The worker dispatches after commit. This gives reliable async work without a broker.

### Modified Capabilities

- None. Both capabilities are new in this change.

## Impact

When promoted:

- `infra/supabase/migrations/2026????000000_<scope>_app_jobs.sql` (new): `app_jobs` table, RLS locked to `service_role`, indexes on `(run_at) WHERE locked_until IS NULL OR locked_until < now()` and on `(queue)`.
- `apps/backend/app/common/queue.py` (new): `enqueue`, `claim_batch`, `mark_done`, `mark_failed`. ~80 lines.
- `apps/backend/app/common/worker.py` (new): in-process asyncio task. Starts in `create_app`, claims due jobs, dispatches by `queue` name, handles lease expiry, retries with backoff.
- The caller (the feature that needs it) calls `enqueue` in the same transaction as its write.
- `tests/test_<caller>_outbox.py` (new, Tier B): one integration test that proves the round-trip.
- `tests/fixtures/rls_tenant_scope.json`: when this change lands, `app_jobs` is added to a special "service-role only" list (not the tenant-scope list). The RLS posture check must allow it.

## Success Criteria

- A caller (the feature) writes a row and enqueues a job in the same transaction.
- The worker claims and dispatches the job within the lease window.
- On worker crash, the job is re-claimed after the lease expires.
- On handler failure, the job's `attempts` is incremented, `run_at` is set with backoff, and another worker (or the same) claims it.
- The Tier B integration test is green.

## Dependencies

- **Hard dependency** on `fix-broken-database-connection`. The worker and the queue helpers both need a working `Settings.database_url` and a runnable local Postgres.
- **Hard dependency** on `migrations-and-conventions` (when promoted). The `app_jobs` migration is subject to the lint, the filename convention, and the RLS posture check. The migration is added to the `service-role` RLS whitelist (a separate, small JSON file).
- **Soft dependency** on `add-phased-kiosk-kds-mobile-ordering-rollout` section 1 ("replace placeholder order-tracking router dependency providers"). If the rollout change lands first and the order-tracking feature becomes the first async-work caller, this change promotes with order-tracking in the same PR.

## Out of Scope (Other Parked Drafts)

- `parked/migrations-and-conventions`: rename, lint, RLS check. Lands before this change (so the `app_jobs` migration passes the lint).

## Why Parked, Not Done Now

Ponytail: YAGNI. The table will be ~30 lines of DDL plus a migration. There is no caller. Adding it now means maintaining a table nobody writes to and a worker nobody feeds. The cost is small but the cost is real: every CI run touches it, every fresh-apply test must account for it, every RLS posture check must allow it.

When the caller lands, the table is 30 minutes of work. Until then, it is dead weight.

## Why Split From `fix-broken-database-connection`

Different justification, different scope, different diff. The broken-thing fix is needed today; the queue is not. Coupling them means the reviewer is asked to sign off on infrastructure with no user-visible benefit.

## Why Split From `migrations-and-conventions`

The migrations-and-conventions parked draft is about how SQL is written. This draft adds SQL that doesn't exist yet. They compose — when this draft is promoted, it lands inside the convention framework that `migrations-and-conventions` set up — but they are not the same change.
