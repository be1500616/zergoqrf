## ADDED Requirements

### Requirement: Profile-Based Runtime Modes

The system MUST support explicit runtime profiles (`local`, `ci`, `prod`) that control data, auth, and configuration behavior predictably across backend and frontend.

#### Scenario: Local profile avoids production dependency

- **WHEN** a developer runs the app in `local` profile
- **THEN** the app uses local-safe datasource/auth configuration
- **AND** no production Supabase credential is required to start core development flow

#### Scenario: Production profile enforces strict configuration

- **WHEN** the app runs in `prod` profile
- **THEN** all required Supabase configuration and secrets are validated on startup
- **AND** startup fails fast with actionable error messages if required values are missing

### Requirement: Tiered Test Execution

The project MUST provide separate test tiers so normal development remains fast and non-blocking while still validating real Supabase behavior before production deployment.

#### Scenario: Fast tests run without live Supabase

- **WHEN** a developer runs the default local/CI test command
- **THEN** tests execute using mocked or local adapters
- **AND** they do not require live Supabase network access

#### Scenario: Integration tests validate real Supabase paths

- **WHEN** the integration test tier is triggered
- **THEN** Supabase-dependent auth, RLS, and repository flows are executed against configured integration infrastructure
- **AND** failures block promotion to production branch

### Requirement: Production Promotion Gates

The release process MUST define explicit gates for migration safety and security verification before production deployment.

#### Scenario: Migration and security checklist is enforced

- **WHEN** a change includes database/auth impacts
- **THEN** migration order, rollback notes, and RLS verification are required artifacts
- **AND** deployment cannot proceed until required gates pass