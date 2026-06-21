## ADDED Requirements

### Requirement: Idempotent order submission

Order creation MUST be idempotent for retried client submissions across PWA, kiosk, and mobile channels to prevent duplicate active orders from network retries or client refreshes.

#### Scenario: Duplicate submission retry

- **WHEN** the client retries the same order request with the same idempotency key after a timeout
- **THEN** the backend SHALL return the original order result instead of creating a second order

### Requirement: Payment-order transition guardrails

The system MUST enforce configured payment and order status transition rules at the backend boundary and SHALL reject invalid transitions regardless of client behavior.

#### Scenario: Preparing before payment collection blocked

- **WHEN** an order status update requests transition to preparing while payment status is pending under pay-before-prep policy
- **THEN** the backend SHALL reject the transition with a validation error and audit record

### Requirement: Realtime consistency with reconnect recovery

Order and kitchen status updates MUST propagate with deterministic ordering guarantees for active sessions and SHALL support reconnect recovery to latest authoritative state.

#### Scenario: KDS reconnect after temporary network loss

- **WHEN** a KDS client disconnects and reconnects
- **THEN** the client SHALL resubscribe and reconcile to the latest server state without losing intermediate terminal statuses

### Requirement: Offline-aware customer tracking

Customer tracking interfaces MUST display last-known authoritative order status while offline and SHALL clearly indicate stale state until connectivity restores.

#### Scenario: Customer loses connectivity during tracking

- **WHEN** a customer device goes offline on the tracking screen
- **THEN** the UI SHALL show last synchronized status and an offline indicator until successful refresh