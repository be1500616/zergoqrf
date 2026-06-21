## Context

The codebase relies heavily on Supabase for auth, RLS-protected data access, and feature repositories. Current development can slow down when Supabase access is unavailable, and test scopes are not explicitly segmented across local, integration, and production readiness checks.

## Goals / Non-Goals

### Goals

- Make local development independent from production Supabase uptime and credentials.
- Ensure fast developer feedback via local and mocked tests.
- Keep production behavior strict with RLS and deployment safeguards.
- Enable easy promotion from dev to prod branch with explicit validation gates.

### Non-Goals

- Replacing Supabase in production.
- Rewriting all repositories in one change.
- Introducing a fully separate database stack beyond what is needed for local flow.

## Decisions

### Decision 1: Environment Profiles as First-Class Contract

Adopt explicit profiles (`local`, `ci`, `prod`) with deterministic behavior for:

- API base URLs
- backend datasource adapters
- auth token providers
- secrets loading and required variables

Rationale: Removes ambiguity and prevents accidental production coupling during development.

### Decision 2: Supabase Access Through Injectable Boundaries

Enforce repository and service interfaces at use-case boundaries. Supabase clients remain infrastructure concerns behind adapters.

Rationale: Unit and service tests can run with fakes/mocks; integration tests can target Supabase-specific behavior only where needed.

### Decision 3: Two-Tier Testing Strategy

- Tier A (default local/CI): unit + service + API tests with mocked/fake data layer (fast, deterministic).
- Tier B (integration): controlled Supabase integration tests, run on demand and in selected CI stages.

Rationale: Avoids blocking day-to-day development while still validating real Supabase behavior before release.

### Decision 4: Promotion Gates Before Production Deploy

Require a release checklist including:

- migration ordering and rollback note
- RLS/security verification
- smoke tests against staging-like environment
- explicit environment variable audit

Rationale: Keeps production branch deploys predictable and low risk.

## Risks / Trade-offs

- More configuration surface area across environments.
  - Mitigation: single source docs + `.env.example` contracts + startup validation.
- Partial migration to repository boundaries could be inconsistent.
  - Mitigation: prioritize high-change modules first (auth/cart/orders), then expand.
- Integration tests may drift if run infrequently.
  - Mitigation: minimum schedule in CI and pre-release mandatory run.

## Migration Plan

1. Define environment profile contract and required variables.
2. Introduce adapter/boundary pattern in one or two critical backend feature slices.
3. Add tiered test commands and CI jobs.
4. Add release gate checklist for prod branch.
5. Roll out remaining slices incrementally in follow-up changes.

## Open Questions

- Whether to run local Supabase stack or Postgres+mocked auth as default local mode.
- Which branch policy triggers integration tier (every PR vs pre-merge to prod).
- Preferred staging strategy for production-like validation.

