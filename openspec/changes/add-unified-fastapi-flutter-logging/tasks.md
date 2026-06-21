## 1. Logging Contract and Governance

- 1.1 Create shared logging contract document (schema fields, severity taxonomy, event naming pattern, and message style guidance).
- 1.2 Define approved high-value event catalog for onboarding, menu, and order lifecycle flows.
- 1.3 Add environment-level logging configuration matrix (local, staging, production) for backend and frontend.
- 1.4 Define log retention, deletion, legal-hold, and privacy classification policy for all environments.
- 1.5 Define approved context allowlist and prohibited raw payload fields (headers, cookies, auth values, request/response bodies, query strings, free-form user input).
- 1.6 Define incident-response field policy (`request_id`, `route_template`, app version, deployment identifier) and classify each as required, optional, pseudonymous, or forbidden.

## 2. Backend Domain and Application Logging Requirements

- 2.1 Identify critical backend domain/application workflows that require structured operational logs.
- 2.2 Define standard backend log contexts for request, user, tenant, feature, action, outcome, and error code.
- 2.3 Define canonical `X-Correlation-ID` propagation and validation rules from inbound request through service execution and response.
- 2.4 Define mapping/migration rules between existing `request_id` usage and canonical `correlation_id`.

## 3. Backend Infrastructure Implementation (FastAPI)

- 3.1 Implement centralized FastAPI logger configuration with JSON output for non-local and readable formatter for local.
- 3.2 Implement request middleware for request start/completion logging with route template, latency, status, and correlation ID.
- 3.3 Implement exception handling integration for structured error logs with safe contextual metadata.
- 3.4 Implement allowlist-first sanitizer/redactor for sensitive fields before log emission.
- 3.5 Add backend config controls for log-level thresholds, verbosity, and sink controls by environment.
- 3.6 Validate inbound `X-Correlation-ID` headers and test missing, empty, malformed, and oversized values.
- 3.7 Add backend rate-limit/sampling and payload-size controls for repetitive low-severity logs.

## 4. Frontend Domain and Application Logging Requirements

- 4.1 Identify key Flutter user journeys/actions that require standardized operational logs.
- 4.2 Define frontend log context model aligned to shared schema (feature, action, outcome, correlation ID, error category).
- 4.3 Define rules for user-readable log messages and severity selection in client code.
- 4.4 Define production sink, delivery semantics, and queue/drop policy for release/profile logs.

## 5. Frontend Infrastructure Implementation (Flutter)

- 5.1 Implement centralized Flutter logging service abstraction used by feature modules.
- 5.2 Implement build-mode aware behavior (debug-readable output, release high-signal structured logs).
- 5.3 Implement a wrapped HTTP transport for all backend API calls that injects `X-Correlation-ID` and emits standardized network logs.
- 5.4 Migrate direct `http.*` backend calls to the wrapped transport and add guardrails to prevent bypass.
- 5.5 Implement runtime error logging with structured context and sensitive data sanitization.
- 5.6 Implement bounded offline queue, retry/backoff, and overflow telemetry for frontend log delivery.

## 6. Verification, Quality Gates, and Rollout

- 6.1 Add backend tests for schema compliance, correlation propagation, and sensitive data redaction (including nested payload structures).
- 6.2 Add backend tests for exception-path logging and duplicate request-log prevention.
- 6.3 Add Flutter tests for logging behavior across debug/profile/release modes.
- 6.4 Add Flutter tests for sink failures, offline queue retry, queue overflow/drop policy, and restart persistence behavior.
- 6.5 Add negative tests proving prohibited raw fields are never logged.
- 6.6 Perform staging validation for correlated end-to-end flows (auth, menu, order) and confirm production acceptance criteria.
- 6.7 Document production log access roles, tenant-scoped query rules, break-glass workflow, and audit expectations.
- 6.8 Update backend/frontend runbooks with troubleshooting examples, rollback switches, and integrity/retention guidance.