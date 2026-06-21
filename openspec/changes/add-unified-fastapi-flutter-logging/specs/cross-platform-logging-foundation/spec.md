## ADDED Requirements

### Requirement: Shared cross-platform log schema

The system SHALL define and enforce a shared logging schema for backend and frontend events containing, at minimum, `timestamp`, `level`, `service`, `platform`, `environment`, `event_name`, `message`, and `correlation_id`.

#### Scenario: Backend and frontend emit compatible fields

- **WHEN** an operational event is logged from either FastAPI or Flutter
- **THEN** the emitted log entry MUST include all required shared schema fields

### Requirement: Canonical severity taxonomy

The system SHALL use a unified severity taxonomy (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) across backend and frontend with consistent semantic meanings.

#### Scenario: Severity values are standardized

- **WHEN** logs are produced by different components
- **THEN** severity values MUST map to the same canonical severity taxonomy

### Requirement: Correlation-first event linking

The system SHALL support end-to-end event correlation by propagating `correlation_id` between Flutter and FastAPI, with backend fallback generation if absent.

#### Scenario: Correlation ID is preserved across request boundary

- **WHEN** Flutter sends a network request with a correlation ID header
- **THEN** FastAPI logs for that request lifecycle MUST use the same correlation ID

#### Scenario: Correlation ID is generated when missing

- **WHEN** FastAPI receives a request without a correlation ID
- **THEN** FastAPI MUST generate one and include it in request lifecycle and error logs

### Requirement: Correlation ID validation

Correlation IDs accepted from clients SHALL be treated as untrusted input.

#### Scenario: Client sends malformed correlation ID

- **WHEN** FastAPI receives an invalid or oversized correlation ID header
- **THEN** FastAPI MUST replace it with a newly generated correlation ID that meets the approved format

#### Scenario: Correlation ID is used for investigation

- **WHEN** logs are queried by correlation ID
- **THEN** correlation ID MUST NOT be treated as proof of tenant, user, or authorization context

### Requirement: Sensitive data sanitization

The logging system SHALL sanitize sensitive values before emission, including auth tokens, passwords, and security credentials.

#### Scenario: Sensitive fields are redacted before write

- **WHEN** a log context payload contains known sensitive keys or values
- **THEN** the logging system MUST redact or remove those values before persisting or printing

### Requirement: Safe log context allowlisting

The logging system SHALL emit only approved context fields and SHALL prohibit raw payload logging by default.

#### Scenario: Request or response payloads are available to logging code

- **WHEN** backend or frontend code logs request, response, exception, or user action context
- **THEN** raw headers, cookies, authorization values, request bodies, response bodies, query strings, and free-form user input MUST NOT be emitted unless explicitly allowlisted and sanitized

### Requirement: Tenant-aware logging safety

The system SHALL include tenant context in logs when available while preventing cross-tenant data leakage in log content.

#### Scenario: Tenant metadata is present without leaking other tenant data

- **WHEN** a request or action is associated with a tenant
- **THEN** logs MUST include that tenant context and MUST NOT include payload data from unrelated tenants

### Requirement: Structured event naming standard

The system SHALL enforce a consistent event naming pattern `domain.feature.action.outcome` for high-value operational logs.

#### Scenario: Events follow approved naming pattern

- **WHEN** developers add new operational log events
- **THEN** event names MUST conform to the `domain.feature.action.outcome` convention

### Requirement: Log retention and deletion governance

Production logging SHALL define retention windows, deletion handling, and legal-hold process for all log sinks.

#### Scenario: Production log retention is configured

- **WHEN** logs are emitted in production
- **THEN** they MUST be stored according to documented retention and deletion policy and MUST NOT be retained indefinitely by default

#### Scenario: Identifiers are present in logs

- **WHEN** logs include `tenant_id`, `user_id`, session references, or correlation identifiers
- **THEN** policy MUST define privacy classification, retention rules, and deletion/anonymization handling

### Requirement: Log access control and tenant-safe querying

Production log access SHALL be role-based, auditable, and constrained to least privilege.

#### Scenario: Operator performs log query

- **WHEN** an operator accesses production logs
- **THEN** access MUST be authorized by role and query activity MUST be auditable

#### Scenario: Cross-tenant access is required

- **WHEN** cross-tenant log access is required for critical support or incident response
- **THEN** access MUST use an explicit break-glass workflow with approval and audit trail

### Requirement: Production log integrity

Production logs SHALL be routed to storage that supports tamper-evident or append-only behavior and auditable export/delete operations.

#### Scenario: Production logs are persisted

- **WHEN** backend or frontend logs are written in production
- **THEN** the sink configuration MUST preserve integrity guarantees for incident investigation

#### Scenario: Log export or deletion occurs

- **WHEN** logs are exported or deleted
- **THEN** the action MUST be auditable with actor and timestamp metadata