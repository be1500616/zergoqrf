# Proposal: Supabase-First Development Runtime with Isolated Dev/Test and Optional Local Postgres

## Why

Product delivery speed is the primary goal. The team needs one default path that keeps auth, RLS, storage, and realtime behavior consistent during development and testing. We will use Supabase as the primary development backend with strict environment separation, while keeping local Postgres as an optional runtime for offline work and contingency.

## What Changes

- Standardize a Supabase-first profile strategy:
  - `dev`: primary day-to-day development Supabase project.
  - `test`: isolated Supabase project for CI/integration and destructive test runs.
  - `prod`: production Supabase project with strict promotion gates.
- Enforce environment isolation and safe promotion:
  - separate secrets/config per profile.
  - migration flow `dev -> test -> prod`.
  - startup validation for required env vars by profile.
- Keep local Postgres as an optional profile:
  - for offline development and rapid local iteration.
  - not required for the default team loop.
- Define queueing guidance for this phase:
  - use Postgres-backed queue patterns for product workflows where needed.
  - do not introduce RabbitMQ in this phase unless explicit throughput/reliability thresholds are exceeded.

## Non-Goals

- Building a provider-agnostic compatibility framework before core product delivery.
- Introducing RabbitMQ as mandatory infrastructure in this phase.
- Re-platforming production away from Supabase now.

## Capabilities

### New Capabilities

- `supabase-dev-test-runtime`: standardized Supabase-first environment workflow for development and testing.
- `optional-local-postgres-runtime`: optional local Postgres path for offline/fast local work.

## Impact

- `apps/backend` and `apps/frontend`: profile-based Supabase project selection and startup validation.
- CI and release workflows: test project gating and migration promotion sequence.
- local tooling/docs: optional Postgres runtime bootstrap for offline development.

## Success Criteria

- Developers use Supabase `dev` by default with no production credential usage.
- CI and integration use only Supabase `test`, keeping development data isolated.
- Promotion to `prod` is gated by migration and RLS checks.
- Local Postgres remains available as an optional, documented fallback path.

