## Context

The team prioritizes product delivery speed and wants one default backend workflow with minimal operational overhead. Supabase already provides auth, RLS, storage, and realtime primitives used by the application, so development and testing should remain Supabase-first with strict environment isolation. Local Postgres should remain available as an optional offline path, not the default team dependency.

## Goals / Non-Goals

### Goals

- Make Supabase the default backend for development and testing.
- Separate development and test data using two Supabase projects.
- Keep a lightweight optional local Postgres runtime for offline work.
- Preserve a practical fallback path to self-hosted Postgres without blocking product delivery.

### Non-Goals

- Building full compatibility abstraction before feature delivery.
- Introducing RabbitMQ in the initial delivery phase.
- Re-architecting existing features around provider neutrality now.

## Decisions

### Decision 1: Supabase-First Profile Model

Use three Supabase projects with explicit profile mapping:
- `dev` profile -> Supabase development project
- `test` profile -> Supabase test/CI project
- `prod` profile -> Supabase production project

Rationale: keeps runtime behavior aligned with actual product architecture and maximizes delivery speed.

### Decision 2: Optional Local Postgres Profile

Keep `local-postgres` as optional runtime for:
- offline development
- fast schema work
- selected unit/service tests without cloud dependency

Rationale: preserves developer flexibility without increasing baseline team complexity.

### Decision 3: Environment Isolation and Promotion Gates

Enforce:
- separate credentials and config for each profile
- migration promotion order `dev -> test -> prod`
- release gates for RLS and migration validation before prod apply

Rationale: protects data safety while allowing fast parallel development.

### Decision 4: Queueing Strategy for Current Phase

- Primary queueing mechanism: Postgres-backed jobs/queue tables for application workflows.
- Do not use RabbitMQ in this phase by default.
- Trigger RabbitMQ adoption only when measured load/reliability needs exceed Postgres queue limits.

Rationale: avoids premature infrastructure complexity and keeps team focused on product outcomes.

## Risks / Trade-offs

- Supabase project/config drift between `dev` and `test`.
  - Mitigation: automate env validation and migration sync checks.
- Shared dev data instability from unsafe testing.
  - Mitigation: run destructive/integration tests only on `test`.
- Postgres queue throughput may hit limits.
  - Mitigation: define queue SLO thresholds and revisit RabbitMQ only when thresholds fail.

## Migration Plan

1. Define profile mapping for Supabase `dev`/`test`/`prod` and required env contracts.
2. Add startup validation and CI checks for profile safety.
3. Enforce migration promotion flow and RLS verification gates.
4. Document optional local Postgres runtime bootstrap for offline development.
5. Define Postgres queue usage guidelines and queue SLO-based RabbitMQ trigger criteria.
6. Keep fallback runbook for self-hosted Postgres as contingency.

## Open Questions

- What queue throughput and retry-latency thresholds should trigger RabbitMQ adoption?
- Which workloads must always execute in `test` (never in `dev`)?
