## Context

The repository already contains a Flutter multi-platform app, backend order and order-tracking modules, and deployment guidance for web and mobile. The current state includes strong domain/application scaffolding but incomplete runtime integration in several critical paths (for example, placeholder use-case dependencies in order tracking router and incomplete route composition for diner/cart/order-tracking surfaces). The business goal is to launch development for a phased rollout across diner PWA, KDS, kiosk, and native mobile while preserving tenant isolation and operational reliability.

Stakeholders include product (phased launch and predictable scope), engineering (deliverable sequencing), restaurant operations (kitchen/front-of-house usability), and platform owners (security, RLS, deployability, and observability).

Constraints include strict multi-tenant boundaries, Supabase RLS correctness, and predictable behavior under intermittent network conditions common in restaurant operations.

## Goals / Non-Goals

**Goals:**

- Define role-scoped multi-surface behavior for PWA ordering, KDS, kiosk, and native mobile.
- Enforce a deployment sequence that hardens backend/runtime fundamentals before advanced surface features.
- Standardize reliability expectations: idempotent order operations, deterministic status transitions, and robust reconnect/offline handling.
- Establish release gates with measurable checks for each phase so teams can proceed without ambiguity.
- Provide tenant-safe observability conventions and operational metrics segmented by app surface.

**Non-Goals:**

- Full digital payment gateway rollout in this change.
- Loyalty/growth campaigns and advanced BI/reporting.
- Re-architecting the entire frontend into separate repositories during initial phase delivery.

## Decisions

1. **Phased rollout with runtime-first sequencing**
  - Decision: Implement in phases where backend DI/routing/realtime/status enforcement lands before kiosk/KDS specialization.
  - Rationale: Prevents feature surface expansion on unstable core workflows.
  - Alternative considered: Build all surfaces in parallel. Rejected due to high integration risk and ambiguous ownership of regressions.
2. **Single backend API with role/source-app segmentation**
  - Decision: Keep one API domain and enforce access by role claims and source app headers (`pwa`, `kds`, `kiosk`, `mobile`).
  - Rationale: Minimizes duplication while maintaining explicit policy boundaries.
  - Alternative considered: Separate APIs per surface. Rejected for initial phases due to operational overhead and duplicated business logic.
3. **PWA-first ordering, Android-first kiosk**
  - Decision: Use PWA as primary mobile ordering channel for low-friction adoption; prioritize Android-native deployment mode for kiosk stability.
  - Rationale: QR-driven traffic favors install-less experiences; unattended kiosk reliability is stronger with Android kiosk capabilities.
  - Alternative considered: Web-only kiosk. Rejected as primary approach due to weaker device/peripheral controls and uptime constraints.
4. **Explicit status and idempotency contracts**
  - Decision: Define normative requirements for idempotent order creation and status transition guardrails (including payment/order coupling rules).
  - Rationale: Restaurant workflows are highly retry-prone; duplicate or invalid transitions create operational incidents.
  - Alternative considered: Rely on best-effort UI prevention. Rejected because clients cannot guarantee consistency under retries/network splits.
5. **Tenant-safe operational telemetry**
  - Decision: Require event/metric tagging by tenant and source app and expose per-surface operational dashboards.
  - Rationale: Enables reliable pilot decisions, faster incident triage, and safe scale-up.
  - Alternative considered: Global aggregate metrics only. Rejected as insufficient for phased rollout decisions.

## Risks / Trade-offs

- **[Risk] Placeholder backend runtime wiring persists into implementation** → Mitigation: Gate Phase 1 completion on non-placeholder DI and endpoint integration tests.
- **[Risk] Surface-specific route conflicts in shared Flutter app** → Mitigation: Introduce explicit route namespaces and role guards with automated route smoke tests.
- **[Risk] Realtime channel leakage across tenants or restaurant contexts** → Mitigation: Use tenant-scoped channel keys and RLS-backed subscriptions, plus negative cross-tenant tests.
- **[Risk] Kiosk hardware and network edge cases delay rollout** → Mitigation: Keep kiosk in controlled pilot phase with strict device matrix and fallback paths.
- **[Trade-off] Faster delivery via shared codebase vs. larger bundle complexity** → Mitigation: Track bundle/perf thresholds and split surface app shells only when thresholds are exceeded.
- **[Trade-off] Single API simplicity vs. policy complexity** → Mitigation: enforce standardized auth middleware and endpoint-level role/source validation checks.

## Migration Plan

1. **Phase 1 (Core hardening)**: complete backend DI wiring, order-tracking runtime integration, route composition, and status/idempotency guards.
2. **Phase 2 (Surface pilots)**: activate PWA ordering pilot and KDS pilot behind feature flags for selected restaurants.
3. **Phase 3 (Kiosk and mobile expansion)**: release Android kiosk pilot and native mobile beta with limited audience.
4. **Phase 4 (Operational scale-up)**: promote features based on gate metrics, with rollback flags for each surface.

Rollback strategy:

- Use per-surface feature flags (`enable_kds`, `enable_kiosk`, `enable_mobile_native`) for immediate disable.
- Preserve backward-compatible API contracts for existing ordering flows during phased introduction.
- Revert deployment channel for affected surface without disabling all ordering endpoints.

## Open Questions

- Should kiosk payment capture in early phases remain strictly cash/at-counter, or include terminal integration pilot?
- What is the minimum acceptable realtime latency target for go-live gates in pilot restaurants (2s vs 3s p95)?
- Which restaurant pilot cohort is approved for each phase and what are explicit exit criteria by cohort?