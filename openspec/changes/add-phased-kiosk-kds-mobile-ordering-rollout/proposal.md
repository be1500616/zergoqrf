## Why

Codebase strong base for diner order, kitchen tracking, multi-platform deploy. But runtime links still missing. Team need phased OPSX plan now, so PWA + kiosk + KDS + native mobile rollout stay stable, each surface ready before scale.

## What Changes

- Make phased rollout plan for 4 surfaces: diner PWA (mobile order), KDS, kiosk, native mobile.
- Add clear capability specs for role-based surfaces, order lifecycle reliability, deployment readiness gates.
- Standardize source-app observability, feature flags, tenant-safe access control for all order/status flows.
- Set build order: backend runtime complete first (DI, routing, realtime, status transitions), kiosk/KDS advanced features after.
- Add non-goals to stop early scope creep into payment rails and heavy analytics.

## Capabilities

### New Capabilities

- `multi-surface-ordering-platform`: Set behavior and boundaries for diner PWA, KDS, kiosk, native mobile with role-scoped access.
- `phased-rollout-and-release-gates`: Set phase-by-phase delivery, validation gates, launch criteria for dev rollout and hardening.
- `order-lifecycle-reliability`: Set idempotent submit, payment/order guardrails, reconnect/offline behavior, realtime consistency.
- `tenant-safe-operations-observability`: Set tenant-safe telemetry, source-app tags, and ops monitoring needs for kitchen/order flows.

### Modified Capabilities

- None. Repo has no existing OpenSpec capability specs under `openspec/specs/`.

## Impact

- Backend: wire order-tracking router deps, kitchen endpoints, realtime channels, idempotency, status transition checks.
- Frontend: compose routes, role-specific shells (PWA/KDS/kiosk/mobile), offline/reconnect UX, phased feature-flag wiring.
- Infra/DevOps: env-specific deploy pipelines, release channels, rollout gates, dashboards/alerts by source app.
- Data/Security: validate multi-tenant RLS, harden role auth for all new surfaces.
- Non-goals (scope control): no full payment-gateway rollout now, no broad loyalty/growth, no advanced BI in initial phased delivery.