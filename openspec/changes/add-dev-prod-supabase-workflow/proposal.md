# Proposal: Golden Path for Local Development and Supabase Production

## Why

Local development currently risks being blocked by live Supabase availability, credentials, and production-only constraints. We need a single team standard that keeps day-to-day development fast while preserving production safety and deployment confidence.

## What Changes

- Standardize a **hybrid environment strategy**:
  - `local`: default developer mode, no dependency on live Supabase for core coding/test loop.
  - `ci`: deterministic automated checks with separated fast and integration tiers.
  - `prod`: real Supabase with strict RLS, validated secrets, and guarded release workflow.
- Introduce a stable backend boundary so application/use-case logic can run with local/mock adapters by default and Supabase adapters in integration/prod paths.
- Define explicit environment variable contracts and startup validation behavior per profile.
- Add tiered test execution model:
  - Tier A (default): fast tests that should run without live Supabase.
  - Tier B (gate): Supabase integration tests for auth/RLS/repository behavior.
- Add promotion gates for production branch deployment:
  - migration order + rollback notes
  - RLS verification
  - auth and critical endpoint smoke checks
  - required env/secret audit.

## Non-Goals

- Replace Supabase in production.
- Re-architect every feature slice in one pass.
- Block feature teams until full migration completes.

## Golden Path Policy (Team Standard)

1. Developers build and test in `local` profile first.
2. Pull requests must pass Tier A checks.
3. Promotion to production branch requires Tier B checks and release gate checklist.
4. Production deployment proceeds only after all gates pass.

## Capabilities

### New Capabilities

- `dev-prod-environment-workflow`: Standardized local/ci/prod profile behavior and switching.
- `supabase-integration-boundary`: Testable abstraction around Supabase-dependent repositories and auth paths.
- `deployment-readiness-gates`: Repeatable checks for migration safety, RLS validation, and release readiness.

## Impact

- `apps/backend`: Environment config, dependency wiring, repository instantiation, test fixtures.
- `apps/frontend`: Environment profile handling and endpoint/base-url alignment per mode.
- `infra/supabase/migrations`: Promotion discipline and verification sequence before production apply.
- `docker-compose.yml` and developer docs: Local workflow and commands for zero-block development.

## Success Criteria

- Developers can run the default local development and test loop without live Supabase credentials.
- CI clearly separates fast checks and Supabase integration checks.
- Production branch promotions use a documented checklist and block on missing migration/RLS/security validations.
- Deployment failures due to missing env configuration are detected at startup (fail-fast), not during runtime traffic.

## Rollout Plan

1. **Phase 1 (foundation):** Introduce profile contract, env validation, and test tier commands.
2. **Phase 2 (high-impact slices):** Apply boundary/adapters to `auth`, `cart`, and `orders`.
3. **Phase 3 (release hardening):** Enforce promotion gates in CI and branch policy for production merges.
4. **Phase 4 (scale-out):** Extend same pattern to remaining slices incrementally.