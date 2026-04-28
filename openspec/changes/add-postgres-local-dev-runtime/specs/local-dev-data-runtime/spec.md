## ADDED Requirements

### Requirement: Supabase-First Development Runtime

The system SHALL use Supabase as the default backend for day-to-day development so product behavior in development stays aligned with production architecture.

#### Scenario: Developer uses default runtime

- **WHEN** a developer starts normal feature development
- **THEN** the backend and frontend use Supabase `dev` configuration by default
- **AND** production credentials are never required for this flow

### Requirement: Isolated Supabase Test Runtime

The system SHALL maintain a separate Supabase `test` project for CI, integration tests, and destructive test workflows.

#### Scenario: CI and destructive tests execute safely

- **WHEN** CI or destructive integration tests run
- **THEN** they target only Supabase `test`
- **AND** development and production data remain isolated

### Requirement: Controlled Promotion Across Environments

The release process SHALL enforce migration and security gates when promoting schema and runtime changes across Supabase environments.

#### Scenario: Migration promotion is validated

- **WHEN** migrations are promoted from `dev` to `test` and then `prod`
- **THEN** migration order and RLS/security checks are validated before each promotion
- **AND** production apply is blocked on failed checks

### Requirement: Optional Local Postgres Runtime

The system SHALL provide an optional local Postgres runtime for offline work and fast local iteration without making it mandatory for the default team workflow.

#### Scenario: Developer works offline

- **WHEN** a developer chooses offline or local-only development
- **THEN** they can run the documented local Postgres profile
- **AND** team delivery flow remains Supabase-first for shared development and testing

### Requirement: Postgres-Backed Queueing Baseline

The system SHALL use Postgres-backed queueing for current product workflows and defer RabbitMQ adoption until explicit throughput/reliability thresholds are exceeded.

#### Scenario: Queueing remains within baseline limits

- **WHEN** queue throughput, processing latency, and retry backlog stay within defined SLO thresholds
- **THEN** Postgres-backed queueing remains the approved default
- **AND** RabbitMQ introduction is not required

### Requirement: RabbitMQ Adoption Trigger Criteria

The system SHALL define measurable trigger criteria for when RabbitMQ (or equivalent broker) becomes necessary.

#### Scenario: Queue demand exceeds baseline

- **WHEN** observed queue metrics exceed agreed SLO thresholds for sustained periods
- **THEN** the platform SHALL initiate a planned broker adoption change
- **AND** this decision is based on measured production-like evidence

