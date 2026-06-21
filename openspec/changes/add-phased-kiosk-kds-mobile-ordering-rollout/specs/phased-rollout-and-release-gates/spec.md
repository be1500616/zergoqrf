## ADDED Requirements

### Requirement: Phase-gated rollout execution

The rollout process MUST be phase-gated and SHALL require completion criteria for each phase before enabling the next phase in development and pilot environments.

#### Scenario: Advancing from core hardening to pilots

- **WHEN** Phase 1 runtime integration checks pass
- **THEN** the system SHALL permit enabling Phase 2 pilot flags for selected restaurants

### Requirement: Surface-specific enablement flags

The platform MUST provide independent feature flags for each app surface so teams can enable or disable diner PWA, KDS, kiosk, and native mobile independently.

#### Scenario: Disabling only KDS rollout

- **WHEN** a KDS incident requires rollback
- **THEN** operators SHALL be able to disable KDS access without disabling diner ordering or mobile tracking

### Requirement: Release gate evidence

Each phase MUST define objective release gate evidence including functional, reliability, and tenant-isolation checks before promotion.

#### Scenario: Gate verification before promotion

- **WHEN** a team requests phase promotion
- **THEN** release automation SHALL require documented pass results for required gate checks