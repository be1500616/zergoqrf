# Capability: Postgres Cache and Queue

This capability covers the `app_jobs` table, the worker, and the queue helpers. It does **not** include `app_cache`; the first cache use-case MUST be a separate promotion with its own justification.

## ADDED Requirements

### Requirement: Postgres-backed queue

The backend MUST provide an `app_jobs` table and Python helpers (`enqueue`, `claim_batch`, `mark_done`, `mark_failed`) for asynchronous work. The worker MUST claim jobs using `SELECT ... FOR UPDATE SKIP LOCKED` so multiple workers do not double-claim.

#### Scenario: enqueue then claim by a single worker

- **GIVEN** an empty `app_jobs` table
- **WHEN** `enqueue("order.status_changed", {...})` is called inside a transaction that is committed
- **THEN** a subsequent `claim_batch(worker="w1", limit=10)` returns exactly that job and locks its `locked_until` to `now() + lease_seconds`

#### Scenario: a second worker cannot claim a locked job

- **GIVEN** worker `w1` has claimed a job with `locked_until` in the future
- **WHEN** worker `w2` calls `claim_batch` before `locked_until` elapses
- **THEN** it returns an empty list

#### Scenario: failed job retries with backoff

- **GIVEN** a job has been claimed and `mark_failed(..., backoff_seconds=30)` is called
- **WHEN** the worker commits the failure
- **THEN** the job's `run_at` is set to `now() + 30s`, `attempts` is incremented, and `locked_until` is cleared so another worker (or the same) can claim it after the backoff

### Requirement: Worker is in-process and starts during FastAPI startup

The worker MUST run in the backend process and be started as an `asyncio.create_task` in `create_app`. The worker MUST be cancelled on FastAPI shutdown.

#### Scenario: backend starts and stops cleanly

- **GIVEN** the backend is starting
- **WHEN** `create_app` runs
- **THEN** the worker task is created and the asyncio loop continues; the worker is ready to claim jobs

#### Scenario: backend shuts down

- **GIVEN** the worker is running with active jobs in flight
- **WHEN** the backend receives SIGTERM
- **THEN** the FastAPI shutdown hook cancels the worker task; in-flight jobs are released (their lease expires) and re-claimed by the next worker

### Requirement: Queue and worker are service-role only

The `app_jobs` table MUST be locked to the `service_role` Postgres role via RLS. The `anon` and `authenticated` roles MUST NOT read or write to it. The table is added to the `service_role` whitelist in the RLS posture check, not the tenant-scope list.

#### Scenario: anon role denied

- **GIVEN** `app_jobs` has `rowsecurity = true` and a policy restricted to `service_role`
- **WHEN** a request executes `SELECT * FROM app_jobs` with an `anon` JWT
- **THEN** Postgres returns zero rows (or denies) and the worker logic is unaffected because it uses the service-role connection

### Requirement: SLOs are measured, not declared

The original monolithic proposal declared SLOs ("95p claim-to-dispatch < 250 ms at 100 jobs/s/worker") as a release gate. This requirement rejects that approach: SLOs MUST be written **after** we have one caller's data, not before. A real broker is added only after we measure a sustained SLO miss, and the decision is recorded in a new OpenSpec change with measured numbers.

#### Scenario: SLO regression is a documented decision, not a silent retry

- **GIVEN** production metrics show a sustained SLO miss for 7 days
- **WHEN** the team considers adding a broker
- **THEN** the decision is recorded in a new OpenSpec change with measured numbers, not done as a one-off PR

#### Scenario: no SLO numbers in the spec

- **GIVEN** this capability is being added
- **WHEN** a reader looks for SLO numbers
- **THEN** the spec says "measure first, gate after"; no numbers are declared

### Requirement: Lease is configurable per claim

`claim_batch` MUST accept a `lease_seconds` parameter (default 30). Lease expiry MUST be tunable per queue in a future change; for now, all queues share the default.

#### Scenario: short lease for fast handlers

- **GIVEN** a fast handler that completes in <1s
- **WHEN** `claim_batch(worker="w1", lease_seconds=10)` is called
- **THEN** the job is locked for 10s; if the worker crashes, the job is re-claimable after 10s

### Requirement: Idempotency is the handler's responsibility

`app_jobs` does not provide at-least-once or exactly-once delivery semantics. Handlers MUST be idempotent. The spec explicitly does not promise exactly-once.

#### Scenario: a handler is called twice for the same job

- **GIVEN** a handler that sends a notification
- **WHEN** the worker claims the job, the worker crashes mid-handler, the lease expires, another worker claims the same job
- **THEN** the notification is sent twice; the handler is responsible for de-duplication (e.g. by job id, or by a per-recipient "already sent" flag)

### Requirement: `app_cache` is NOT in this capability

This capability explicitly excludes `app_cache`. The first cache use-case MUST be a separate promotion with its own justification. A reader of this spec MUST NOT assume `app_cache` exists.

#### Scenario: a developer assumes `app_cache` exists

- **GIVEN** this capability is in `openspec/specs/`
- **WHEN** a developer looks for a cache table
- **THEN** they find `app_jobs` but no `app_cache`; the parked `app-jobs-and-realtime-fanout/proposal.md` "Out of Scope" section is the source of truth, and the next change author writes a new promotion with the cache use-case
