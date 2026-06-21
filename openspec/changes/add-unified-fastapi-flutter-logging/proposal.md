## Why

The backend FastAPI services and Flutter clients currently have no standardized logging setup, which makes debugging and incident response slow and inconsistent. We need an industry-standard, structured logging baseline now so engineers and operators can reliably trace user flows and failures across both surfaces.

## What Changes

- Define a backend logging standard for FastAPI with structured JSON logs, consistent severity levels, request correlation, and environment-specific output modes.
- Define a frontend logging standard for Flutter with readable developer logs, production-safe structured event logging, and shared severity/category conventions.
- Define a mandatory production delivery path for Flutter logs, including offline queue/retry/drop behavior and failure handling.
- Define a shared log schema and naming conventions so backend and frontend logs are easy to understand together.
- Define guardrails for sensitive data redaction, allowlisted log context fields, multi-tenant context tagging, and log volume controls.
- Define retention, deletion, legal-hold, and access-control requirements for production logs.
- Define operator-facing guidance for organization, querying, and troubleshooting workflows using these logs.
- Non-goals:
  - Selecting or mandating a specific paid log aggregation vendor in this change.
  - Replacing metrics/traces/APM; this change establishes logging only.
  - Backfilling historical logs.

## Capabilities

### New Capabilities

- `cross-platform-logging-foundation`: Unified logging architecture, schema, severity taxonomy, correlation strategy, and security guardrails across FastAPI and Flutter.
- `backend-fastapi-structured-logging`: FastAPI-specific requirements for request lifecycle logging, exception logging, tenant-aware context, and production readiness.
- `frontend-flutter-structured-logging`: Flutter-specific requirements for UI/action/network/error logging with user-readable and developer-friendly organization, including client-side delivery semantics.

### Modified Capabilities

- None.

## Impact

- Affected areas:
  - Backend: FastAPI app bootstrap, middleware, exception handlers, HTTP client wrappers, and domain service logging touchpoints.
  - Frontend: Flutter app bootstrap, logging service abstraction, API client/interceptors, and error reporting paths.
  - Infra/ops: Environment configuration for log levels/output targets and operational runbooks for searching logs.
- Data/auth impact:
  - Logs MUST preserve tenant boundaries and include tenant context where available without exposing secrets or PII.
  - Redaction requirements MUST apply to auth tokens, credentials, and customer-sensitive payload fields.
- Operational acceptance criteria:
  - Staging MUST show at least one full correlated flow from Flutter action to FastAPI request/error logs for auth, menu, and order paths.
  - Backend request completion logs MUST include route template, status, duration, environment, service, and correlation ID.
  - Frontend release-mode logs MUST reach the selected production sink with defined retry/drop behavior.
  - Tests MUST prove sensitive values (tokens, auth headers, credentials, contact fields, nested payload values) are not emitted.