# Tasks: App Jobs and Realtime Fan-Out

## 1. Migration

- [ ] 1.1 Add migration `2026????000000_<scope>_app_jobs.sql` with `app_jobs(id, queue, payload jsonb, run_at, attempts, locked_until, last_error, created_at)` table. <!-- id: mig-1 -->
- [ ] 1.2 Add indexes: `(run_at) WHERE locked_until IS NULL OR locked_until < now()` and `(queue)`. <!-- id: mig-2 -->
- [ ] 1.3 Add RLS locked to `service_role`: `create policy app_jobs_service_role_all ...`. <!-- id: mig-3 -->
- [ ] 1.4 Add `tests/fixtures/rls_service_role_tables.json` with `["app_jobs"]` so `make rls-check` allows it. <!-- id: mig-4 -->

## 2. Queue Helper

- [ ] 2.1 Write `apps/backend/app/common/queue.py` with `enqueue(conn, queue, payload, run_at=None) -> int`. <!-- id: q-1 -->
- [ ] 2.2 Add `claim_batch(conn, worker_id, lease_seconds=30, limit=10) -> list[Job]` over `FOR UPDATE SKIP LOCKED`. <!-- id: q-2 -->
- [ ] 2.3 Add `mark_done(conn, job) -> None` and `mark_failed(conn, job, error, backoff_seconds=None) -> None`. <!-- id: q-3 -->
- [ ] 2.4 Add a `Job` dataclass with `id`, `queue`, `payload`, `attempts`, `worker_id`, and `from_row(row, worker_id)` classmethod. <!-- id: q-4 -->

## 3. Worker

- [ ] 3.1 Write `apps/backend/app/common/worker.py` with `worker_loop(pool, worker_id, dispatch) -> None`. <!-- id: w-1 -->
- [ ] 3.2 Start the worker as `asyncio.create_task(worker_loop(...))` in `create_app`. Cancel on shutdown. <!-- id: w-2 -->
- [ ] 3.3 Register dispatch handlers per queue (e.g. `order.status_changed -> handler`). The first caller's handler is wired in its own task. <!-- id: w-3 -->

## 4. Caller (Landing in Same PR)

- [ ] 4.1 In the caller's write path, open a transaction. Write the row. Call `enqueue(conn, ...)`. Commit. <!-- id: c-1 -->
- [ ] 4.2 Add a handler in the worker that dispatches the job (e.g. publishes to Supabase Realtime, sends a notification). <!-- id: c-2 -->
- [ ] 4.3 (Optional) For order-tracking status fan-out, the handler writes to the Supabase Realtime channel via the service-role client. The frontend subscribes via `supabase_flutter`. <!-- id: c-3 -->

## 5. Test

- [ ] 5.1 Add `tests/test_<caller>_outbox.py` (Tier B): start a real Postgres, write a row + enqueue a job in a transaction, run the worker once, assert the handler was called and the job is marked done. <!-- id: t-1 -->
- [ ] 5.2 (Optional) Add a lease-expiry test: claim a job, do not mark it done, simulate lease expiry, claim again from a different worker, assert the same job is re-claimed. <!-- id: t-2 -->

## 6. Out of Scope (Other Parked Drafts)

- `app_cache` table. Lands in a separate promotion when a real cache use-case exists.
- `apps/backend/app/common/cache.py`. Same.
- SLO numbers. Written after this change lands and we have one caller's data.
- Multi-process worker. Scale-out is a future change.
- External broker. Added only after SLO miss.
- Custom WebSocket gateway. Supabase Realtime handles push.

## 7. Verification

- [ ] 7.1 `make lint-sql` is green on the new migration. <!-- id: v-1 -->
- [ ] 7.2 `make rls-check` is green with `app_jobs` in the service-role whitelist. <!-- id: v-2 -->
- [ ] 7.3 The Tier B integration test is green against the local Supabase Postgres. <!-- id: v-3 -->
- [ ] 7.4 The caller ships in the same PR; the row write and the job write commit atomically. <!-- id: v-4 -->
- [ ] 7.5 `pytest` (Tier A) is green; no DB required for the default run. <!-- id: v-5 -->
- [ ] 7.6 `openspec validate app-jobs-and-realtime-fanout --strict` passes after promotion. <!-- id: v-6 -->
