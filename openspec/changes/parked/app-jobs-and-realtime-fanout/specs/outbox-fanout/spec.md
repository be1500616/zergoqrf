# Capability: Outbox Fan-Out

## ADDED Requirements

### Requirement: Row write and job enqueue commit atomically

When a feature needs post-write async work, the caller's write path MUST open a single transaction, write the row, call `enqueue(conn, ...)`, and commit. The row and the job MUST be in the same transaction. There is no two-phase commit and no application-layer queue.

#### Scenario: a successful write enqueues a job

- **GIVEN** a caller is updating `orders.status`
- **WHEN** the caller runs:
  ```
  begin;
  update orders set status = $1, updated_at = now() where id = $2;
  select enqueue('order.status_changed', jsonb_build_object('order_id', $2, 'status', $1));
  commit;
  ```
- **THEN** both the row write and the `app_jobs` insert are visible to other connections only after `commit`; a worker reading after commit sees both

#### Scenario: a failed write does not enqueue a job

- **GIVEN** a caller is updating `orders.status`
- **WHEN** the row write fails (e.g. constraint violation) before `commit`
- **THEN** the `app_jobs` insert is rolled back; no job is queued; no partial state is visible

#### Scenario: a successful enqueue but a failed commit

- **GIVEN** a caller writes the row and enqueues the job
- **WHEN** `commit` fails (e.g. connection drop, deadlock)
- **THEN** both the row write and the `app_jobs` insert are rolled back; the caller sees an error and retries the whole transaction

### Requirement: The worker dispatches after commit

The worker MUST claim jobs whose `run_at <= now()`. After a successful claim, the worker calls the dispatch handler registered for the queue. After a successful handler return, the worker calls `mark_done`. On handler failure, the worker calls `mark_failed` with backoff.

#### Scenario: a happy-path dispatch

- **GIVEN** a job with `queue='order.status_changed'` and a registered handler
- **WHEN** the worker claims the job and calls the handler
- **THEN** the handler runs, the worker calls `mark_done`, the job is removed from the due set

#### Scenario: a handler raises

- **GIVEN** a job with `queue='order.status_changed'` and a registered handler that raises
- **WHEN** the worker calls the handler
- **THEN** the worker catches the exception, calls `mark_failed(conn, job, error, backoff_seconds=2 ** job.attempts)`, the job's `run_at` is set to `now() + backoff`, `attempts` is incremented, and the job is re-claimable after the backoff

### Requirement: No handler is a no-op

A queue name without a registered handler MUST cause the worker to call `mark_failed` with `error = "no handler for queue {queue}"` and `backoff_seconds = 300`. The job is not retried within the backoff window. This prevents a typo in the queue name from spinning the worker.

#### Scenario: a queue name typo

- **GIVEN** a job with `queue='order.status_changedd'` (typo) and no registered handler
- **WHEN** the worker claims the job
- **THEN** the worker calls `mark_failed(conn, job, "no handler for queue order.status_changedd", backoff_seconds=300)`; the job waits 5 minutes before being re-claimable; logs surface the typo

### Requirement: Supabase Realtime is the push channel for client subscribers

When a handler's job is "publish to client subscribers" (e.g. `order.status_changed`), the handler MUST write to the Supabase Realtime channel via the service-role client. The frontend subscribes via `supabase_flutter`. No custom WebSocket gateway.

#### Scenario: order status change reaches the KDS

- **GIVEN** the KDS is subscribed to the `orders` Realtime channel for restaurant X
- **WHEN** the orders API updates `orders.status = 'preparing'` and enqueues `order.status_changed`
- **THEN** the worker claims the job, the handler publishes to the Realtime channel, the KDS receives the update within the lease window

#### Scenario: order status change reaches the diner

- **GIVEN** the diner is subscribed to the `order_tracking` Realtime channel for their order
- **WHEN** the orders API updates `orders.status = 'ready'` and enqueues `order.status_changed`
- **THEN** the worker claims the job, the handler publishes to the Realtime channel, the diner receives the update within the lease window

### Requirement: Handler idempotency is the handler's responsibility

`app_jobs` provides at-least-once delivery. Handlers MUST be idempotent. The outbox pattern does not promise exactly-once.

#### Scenario: a notification is sent twice due to a worker crash

- **GIVEN** a handler that sends a push notification and records "sent" in a `notifications` table
- **WHEN** the worker claims the job, the handler sends the notification, the worker crashes before `mark_done`, the lease expires, another worker re-claims the same job
- **THEN** the handler is called again; the handler checks the `notifications` table, finds the prior "sent" record, and skips the send; `mark_done` is called

### Requirement: Outbox is the only fan-out path

The backend MUST use the outbox pattern for post-write async work. There is no `LISTEN/NOTIFY`-based fan-out, no in-process pub/sub, no message bus. The DB is the queue; the worker is the consumer; Supabase Realtime is the client push.

#### Scenario: a developer reaches for an in-process pub/sub

- **GIVEN** a feature needs to notify a different module after a write
- **WHEN** the developer reaches for an in-process pub/sub or `asyncio.Queue`
- **THEN** the contribution guide and `parked/app-jobs-and-realtime-fanout/proposal.md` redirect them to the outbox pattern; the row write and the job write go in the same transaction
