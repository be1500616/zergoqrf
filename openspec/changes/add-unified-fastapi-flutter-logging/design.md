## Context

The current system has no formal logging standard in either backend FastAPI services or the Flutter client. This creates fragmented troubleshooting, weak incident diagnostics, and inconsistent developer/operator experience.

This is a cross-cutting design that affects:

- Backend request handling, service-layer errors, and integration points.
- Frontend UI interaction tracing, API call logging, and runtime error capture.
- Operational workflows for triaging issues in a multi-tenant restaurant environment.

Key constraints:

- Tenant isolation is critical; logging must not leak data across tenants.
- Logs must remain readable by humans while still being machine-queryable.
- The baseline should work locally and in production with minimal divergence.

## Goals / Non-Goals

**Goals:**

- Establish one shared logging contract (fields, levels, event names) across FastAPI and Flutter.
- Require structured logs for backend and structured event logs for frontend.
- Ensure logs are organized by context (request/user/tenant/feature/action/outcome).
- Make logs immediately useful for debugging with request and session correlation IDs.
- Enforce secure logging defaults with PII/secrets redaction.
- Provide predictable environment controls (log level, sink, formatting mode).
- Provide rollout gates and measurable acceptance criteria before production enablement.

**Non-Goals:**

- Choosing a specific commercial observability vendor.
- Replacing metrics, tracing, or crash analytics strategy.
- Capturing 100% of app events (focus is high-value operational events).
- Retrofitting historical data.

## Decisions

1. Shared event schema across backend and frontend

- Decision: Define canonical fields: `timestamp`, `level`, `service`, `platform`, `environment`, `event_name`, `message`, `correlation_id`, `tenant_id` (optional), `user_id` (optional), `feature`, `action`, `outcome`, `error_code` (optional), `request_id` (optional), `route_template` (optional), `client_app_version` (optional), `release_version` (optional), `deployment_id` (optional), and `context` object.
- Rationale: Uniform schema enables intuitive reading and consistent querying.
- Alternatives considered:
  - Separate schemas per platform: simpler short-term, but harder cross-surface diagnosis.
  - Free-form messages only: readable but poor for reliable filtering/aggregation.

1. Backend logs use structured JSON as default

- Decision: FastAPI emits JSON logs in non-local environments; local dev may use pretty formatter with identical fields.
- Rationale: JSON is industry standard for backend ingestion and searchability while preserving local readability.
- Alternatives considered:
  - Plain text only: easier manually, weak for aggregation and automation.

1. Frontend logs use tiered strategy

- Decision: Flutter uses developer-readable console logs in debug builds plus structured event payload logging for key actions/errors; release builds keep high-signal warnings/errors and network/domain failures.
- Rationale: Balance readability, performance, and signal quality on constrained clients.
- Alternatives considered:
  - Verbose production logging: too noisy and may affect performance/privacy.
  - Error-only logging: insufficient context for reproducing user issues.

1. Frontend production sink and delivery guarantees

- Decision: Flutter release/profile logs are delivered to a designated remote sink through a bounded local queue with best-effort delivery semantics.
- Delivery rules:
  - Queue has max entry count and max age; oldest entries are dropped first on overflow.
  - Retry uses capped exponential backoff.
  - Network failures never block UI-critical code paths.
  - Queue persistence across app restart is required for high-severity events.
- Rationale: Without explicit delivery semantics, production frontend logs are not operationally reliable.
- Alternatives considered:
  - Console-only production logging: insufficient for remote incident triage.
  - At-least-once durable delivery for all events: high complexity and overhead for v1.

1. Correlation-first logging

- Decision: Require generation/propagation of `correlation_id` from frontend to backend via `X-Correlation-ID`, with backend validating inbound IDs and creating replacements when missing or malformed.
- Rationale: Enables end-to-end request tracing for user-reported incidents.
- Alternatives considered:
  - Backend-only request IDs: loses linkage to frontend interaction timeline.

1. Secure-by-default redaction rules

- Decision: Use allowlisted safe context fields by default, with denylist redaction as a defense-in-depth fallback.
- Rationale: Prevent accidental leakage while preserving operational utility.
- Alternatives considered:
  - Developer discipline only: too fragile for production systems.

1. Flutter network integration strategy

- Decision: Standardize outbound HTTP calls through a single wrapped transport (`http.BaseClient` wrapper) that injects `X-Correlation-ID`, emits network logs, and enforces sanitization rules.
- Rationale: The current codebase relies on direct `package:http` usage; interceptor-based assumptions are insufficient.
- Alternatives considered:
  - Rely on ad hoc direct `http.`* calls: would fragment logging coverage.
  - Immediate full HTTP stack replacement: excessive scope for this change.

1. Backend correlation migration strategy

- Decision: Adopt one correlation model where `correlation_id` is the canonical cross-surface identifier, and backend `request_id` is mapped to or derived from it for compatibility.
- Rationale: Prevent split identifiers and broken incident timelines.
- Alternatives considered:
  - Dual independent ID systems: ambiguous and operationally fragile.

1. Retention, access control, and integrity controls

- Decision: Production logging policy includes retention windows, deletion/legal-hold process, role-based access controls, audit trails for query/export/delete actions, and tamper-evident/append-only sink expectations.
- Rationale: Logging is part of security and compliance posture, not just debugging.
- Alternatives considered:
  - Tool-default retention/access behavior with no explicit policy: unacceptable for tenant-aware production systems.

1. Performance and volume budgets

- Decision: Define hard budgets and controls:
  - Backend p95 logging overhead budget for request middleware.
  - Client logging must avoid synchronous network/disk writes on UI-critical paths.
  - Max serialized log/event size and truncation policy.
  - Sampling/rate-limit rules for repetitive low-severity events.
- Rationale: Prevent cost/performance regressions after rollout.
- Alternatives considered:
  - Post-hoc tuning only: too risky for first production rollout.

1. Log taxonomy and organization standards

- Decision: Enforce naming pattern `domain.feature.action.outcome` for `event_name`, and severity mapping (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) with clear usage examples.
- Rationale: Predictable naming makes logs self-explanatory and easier to scan.
- Alternatives considered:
  - Ad hoc names by team: inconsistent and harder to search.

## Risks / Trade-offs

- [Risk] Increased implementation effort across two platforms.  
→ Mitigation: Roll out in phases with shared schema package/constants and focused initial event set.
- [Risk] Over-logging creates noise and higher storage cost.  
→ Mitigation: Default level policies per environment and explicit event inclusion criteria.
- [Risk] Missing correlation IDs from older clients.  
→ Mitigation: Backend fallback ID generation and temporary compatibility logging flag.
- [Risk] Sensitive fields slip into contextual payloads.  
→ Mitigation: Centralized sanitizer + tests around representative payloads.
- [Risk] Developer friction from stricter conventions.  
→ Mitigation: Provide helper APIs/wrappers so structured logging is easier than ad hoc logging.
- [Risk] Frontend sink outage causes dropped visibility.  
→ Mitigation: Bounded offline queue, retry/backoff policy, overflow telemetry, and explicit drop metrics.
- [Risk] Correlation ID spoofing or malformed identifiers from clients.  
→ Mitigation: Strict validation and regeneration on backend for invalid IDs.
- [Risk] New logging path causes duplicate backend request logs.  
→ Mitigation: Explicitly harmonize/disable overlapping server access logs during rollout tests.

## Migration Plan

1. Define shared logging schema and severity/event naming guidelines.
2. Implement backend logging configuration, middleware, and exception logging with sanitizer.
3. Implement Flutter logging service abstraction, wrapped HTTP transport, and schema-aligned helpers.
4. Add environment toggles and default levels for local/staging/production.
5. Introduce test coverage for schema compliance, sanitization, correlation propagation, delivery failure handling, and queue overflow behavior.
6. Roll out by high-priority flows first (auth/session, menu fetch, order create/update), then expand behind environment toggles.
7. Apply release gates before production: correlated end-to-end traces visible, redaction tests passing, and no duplicate request logging.

Rollback strategy:

- Keep feature flags/config toggles to reduce verbosity or revert formatter mode per environment.
- Revert wrappers in isolated modules without changing business logic paths.
- Disable frontend remote upload and retain local-only logging mode during incident rollback.
- Lower backend log level and disable request-start logs independently if volume spikes.

## Open Questions

- Should we expose a minimal user-facing error reference code that maps directly to `correlation_id` for support workflows?
- Do we require a shared document enumerating approved event names before implementation starts?