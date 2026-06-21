## ADDED Requirements

### Requirement: Source-app and tenant telemetry tagging

Operational events and metrics MUST include tenant identity and source-app tags (`pwa`, `kds`, `kiosk`, `mobile`) for all order lifecycle and status update flows.

#### Scenario: Order status event emission

- **WHEN** an order status changes
- **THEN** emitted telemetry SHALL include tenant identifier, restaurant identifier, source-app tag, and correlation identifier

### Requirement: Tenant-safe monitoring views

Monitoring outputs MUST support tenant-safe segmentation and SHALL prevent cross-tenant exposure of operational or business metrics.

#### Scenario: Restaurant-scoped operations dashboard

- **WHEN** an operator opens a restaurant monitoring view
- **THEN** the dashboard SHALL display only metrics authorized for that restaurant or permitted management scope

### Requirement: Phase gate reliability metrics

The platform MUST expose rollout reliability metrics for each surface including error rate, status update latency, and reconnect success so promotion decisions are evidence-based.

#### Scenario: Phase promotion readiness check

- **WHEN** a release manager evaluates phase promotion
- **THEN** the system SHALL provide current and trailing-window reliability metrics per surface for gate validation