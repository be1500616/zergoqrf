# Design: App Jobs and Realtime Fan-Out

## Context

The MVP needs no queue, no scheduled job runner, and no async fan-out today. This draft captures the minimum viable implementation when a feature finally calls for it: an `app_jobs` table, a worker over `FOR UPDATE SKIP LOCKED`, and an outbox-style write path that commits the row and the job in the same transaction.

The design is parked because there is no caller. The moment a caller exists (an endpoint that needs to send a notification, do post-write work, or fan out), this draft is promoted in the same PR. The diff is one reviewable unit.

## Goals / Non-Goals

### Goals

- One durable queue: `app_jobs` table.
- One worker: in-process asyncio task started in `create_app`.
- One outbox pattern: row write + `enqueue` in the same transaction.
- Lease-based claim with `FOR UPDATE SKIP LOCKED`.
- Backoff on failure.
- RLS locked to `service_role`.

### Non-Goals

- No `app_cache`. The first cache use-case is a separate promotion.
- No external broker. The worker is `asyncpg` + an asyncio loop.
- No `procrastinate` or `arq`. Add only if SLOs are measured and missed.
- No SLO numbers. SLOs get written **after** we have one caller's data.
- No multi-process worker. In-process is the MVP. Scale-out is a future change.
- No custom WebSocket gateway. Supabase Realtime channels handle push.
- No Redis. No Memcached. No second data store.

## Decisions

### Decision 1: `app_jobs` table

```sql
-- ponytail: one queue table, no separate "scheduled" table. run_at covers both.
create table if not exists public.app_jobs (
    id bigserial primary key,
    queue text not null,
    payload jsonb not null,
    run_at timestamptz not null default now(),
    attempts int not null default 0,
    locked_until timestamptz,
    last_error text,
    created_at timestamptz not null default now()
);

create index if not exists app_jobs_due_idx
    on public.app_jobs (run_at)
    where locked_until is null or locked_until < now();

create index if not exists app_jobs_queue_idx
    on public.app_jobs (queue);

alter table public.app_jobs enable row level security;

-- ponytail: only service_role can read or write app_jobs. anon/authenticated
-- roles cannot enqueue or claim.
create policy app_jobs_service_role_all on public.app_jobs
    for all
    to service_role
    using (true)
    with check (true);
```

The migration is added to a `service_role` whitelist in the RLS posture check (separate from the tenant-scope list), so `make rls-check` allows it.

### Decision 2: `enqueue` is a single INSERT

```python
# ponytail: enqueue is one insert. Call it inside the caller's transaction
# so the row write and the job write commit atomically. The worker dispatches
# after commit; if the worker is down, the job waits.
async def enqueue(conn, queue: str, payload: dict, run_at: datetime | None = None) -> int:
    row = await conn.fetchrow(
        "insert into app_jobs (queue, payload, run_at) values ($1, $2, $3) returning id",
        queue, json.dumps(payload), run_at or datetime.utcnow(),
    )
    return row["id"]
```

### Decision 3: `claim_batch` uses `FOR UPDATE SKIP LOCKED`

```python
# ponytail: skip locked, lease for N seconds. Lease expiry lets crashed
# workers' jobs be re-claimed without a separate "stuck" sweeper.
async def claim_batch(conn, worker_id: str, lease_seconds: int = 30, limit: int = 10) -> list[Job]:
    rows = await conn.fetch(
        """
        update app_jobs
        set locked_until = now() + ($3 || ' seconds')::interval
        where id in (
            select id from app_jobs
            where run_at <= now()
              and (locked_until is null or locked_until < now())
            order by run_at
            for update skip locked
            limit $4
        )
        returning id, queue, payload, attempts
        """,
        worker_id, queue, lease_seconds, limit,
    )
    return [Job.from_row(r, worker_id) for r in rows]
```

### Decision 4: Worker is in-process

```python
# ponytail: in-process worker. ~80 lines. Started in create_app.
# One process per backend instance. Scale-out is a future change.
async def worker_loop(pool, worker_id: str, dispatch: dict[str, Callable]):
    while True:
        async with pool.acquire() as conn:
            jobs = await claim_batch(conn, worker_id)
            for job in jobs:
                handler = dispatch.get(job.queue)
                if not handler:
                    await mark_failed(conn, job, f"no handler for queue {job.queue}")
                    continue
                try:
                    await handler(job.payload)
                    await mark_done(conn, job)
                except Exception as e:
                    backoff = min(300, 2 ** job.attempts)
                    await mark_failed(conn, job, str(e), backoff_seconds=backoff)
        await asyncio.sleep(0.1)
```

Started as an `asyncio.create_task(worker_loop(...))` in `create_app`. Cancelled on shutdown.

### Decision 5: Outbox pattern in the caller

The caller writes the row and enqueues the job in the **same transaction**:

```python
# ponytail: outbox. Row write and job write commit atomically. If the
# commit fails, neither ships. If the commit succeeds, the worker
# dispatches the job eventually.
async def update_order_status(order_id: str, new_status: str):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "update orders set status = $1, updated_at = now() where id = $2",
                new_status, order_id,
            )
            await enqueue(conn, "order.status_changed", {"order_id": order_id, "status": new_status})
```

No two-phase commit. No application-layer queue. The DB is the queue.

### Decision 6: No SLO numbers yet

SLOs ("95p claim-to-dispatch < 250 ms at 100 jobs/s/worker") get written **after** we have one caller's data. The original monolithic proposal listed SLOs as a release gate; that was speculative. The rule is: measure first, gate after.

## Tech Choices

- **Driver:** `asyncpg` directly. The worker and the queue helpers do not need SQLAlchemy.
- **Worker framework:** none. The worker is ~80 lines of `asyncpg` + `asyncio`.
- **Outbox pattern:** implicit in the caller's transaction. No library.
- **Supabase Realtime:** the worker handler for `order.status_changed` writes to the Supabase Realtime channel via the service-role client. The frontend subscribes via `supabase_flutter`.
- **Test framework:** the Tier B integration test uses `pytest-asyncio` + the local Supabase Postgres from `make dev`.

## Risks

- **Risk:** `app_jobs` is too slow for kitchen fan-out under load.
  - **Mitigation:** no SLOs to miss yet. When the first caller's data lands, measure. If the worker is the bottleneck, scale out (multiple processes), then shard by queue, then — only then — consider an external broker.
- **Risk:** the in-process worker means jobs do not survive a backend restart.
  - **Mitigation:** the lease expires, the next backend instance picks up the job. Lease seconds are tuned to backend restart time (default 30s, configurable).
- **Risk:** the outbox pattern couples the caller to `asyncpg` directly.
  - **Mitigation:** `enqueue` is one INSERT. The caller already has a connection. No coupling beyond what already exists.
- **Risk:** the `service_role` whitelist in the RLS posture check is a special case.
  - **Mitigation:** it lives in `tests/fixtures/rls_service_role_tables.json`, separate from `rls_tenant_scope.json`. The RLS posture script reads both and applies different rules.

## Open Questions

- Do we want `procrastinate` (Python-native, Postgres-backed) as a future upgrade path, or roll our own 80-line worker? Ponytail: roll our own. Add `procrastinate` only if SLOs demand it.
- Lease seconds default: 30s. Tunable per queue. The first caller (likely order-tracking status fan-out) sets the value.
