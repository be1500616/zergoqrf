## 1. Core Runtime Hardening (Phase 1)

- 1.1 Replace placeholder order-tracking router dependency providers with concrete use-case wiring in backend composition.
- 1.2 Enforce backend status transition guards for order/payment lifecycle with explicit validation errors and audit events.
- 1.3 Add idempotency key handling for order creation and retries across PWA, kiosk, and native mobile clients.
- 1.4 Implement tenant- and restaurant-scoped realtime channel naming and payload contracts for customer and kitchen subscribers.
- 1.5 Add backend tests for DI wiring, invalid transition rejection, idempotent order behavior, and cross-tenant isolation.

## 2. Multi-Surface Routing and Access Control (Phase 1)

- 2.1 Introduce surface route namespaces in Flutter for diner ordering, KDS, kiosk, and native mobile modes.
- 2.2 Add role/source-app route guards and backend policy checks aligned to owner/manager/kitchen/service/customer roles.
- 2.3 Wire per-surface feature flags (`enable_kds`, `enable_kiosk`, `enable_mobile_native`) across frontend and backend checks.
- 2.4 Add smoke tests for guarded route access and denied cross-surface navigation paths.

## 3. Diner PWA and KDS Pilot Readiness (Phase 2)

- 3.1 Complete diner/cart/order-tracking route composition so customer flows are reachable in deployed web builds.
- 3.2 Implement offline-aware customer tracking state with stale-status indicator and reconnect refresh behavior.
- 3.3 Harden KDS refresh/reconnect workflow to reconcile latest authoritative order states after disconnect.
- 3.4 Add KDS usability essentials (high-contrast cards, clear next-action cues, and status-update confirmation UX).
- 3.5 Validate pilot readiness with end-to-end tests for status latency, reconnect consistency, and role-scoped data visibility.

## 4. Kiosk and Native Mobile Expansion (Phase 3)

- 4.1 Implement Android kiosk mode baseline configuration and locked-flow navigation behavior for unattended use.
- 4.2 Add kiosk idle timeout/session reset and retry-safe submission handling for interrupted interactions.
- 4.3 Enable native mobile beta capabilities that differ from PWA baseline (deep link entry and notification-ready hooks).
- 4.4 Add phased rollout controls for restaurant cohort allowlists per surface.

## 5. Tenant-Safe Observability and Release Gates (Phase 4)

- 5.1 Emit structured telemetry with tenant, restaurant, source-app, and correlation identifiers on order/status operations.
- 5.2 Build per-surface reliability dashboards for error rate, status update latency, and reconnect success.
- 5.3 Define and codify promotion gates for each phase with required metric thresholds and test evidence artifacts.
- 5.4 Add rollback runbooks using per-surface feature flags and channel-specific release controls.
- 5.5 Run final validation suite (backend, frontend, integration) and document gate outcomes before phase promotion.