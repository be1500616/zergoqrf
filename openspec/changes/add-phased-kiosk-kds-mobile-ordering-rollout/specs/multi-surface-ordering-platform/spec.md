## ADDED Requirements

### Requirement: Role-scoped surface access

The system MUST provide explicit, role-scoped access boundaries for diner PWA, KDS, kiosk, and native mobile surfaces so that users can only access workflows authorized for their role and tenant context.

#### Scenario: Customer accesses diner PWA

- **WHEN** an unauthenticated diner opens a QR entry route for a restaurant
- **THEN** the system SHALL allow menu/cart/order-tracking workflows limited to that restaurant context

#### Scenario: Kitchen user accesses KDS

- **WHEN** a user with kitchen role signs into KDS
- **THEN** the system SHALL grant kitchen workflow actions and deny customer and owner-only management actions

### Requirement: Surface-specific route namespaces

The frontend MUST expose surface-specific route namespaces and guards to prevent route collision and accidental cross-surface navigation in shared Flutter deployments.

#### Scenario: Shared deployment route resolution

- **WHEN** the app initializes routes for web or mobile targets
- **THEN** route matching SHALL resolve to a surface namespace with guard checks before rendering any protected screen

### Requirement: Surface mode configuration

The platform MUST support runtime surface mode configuration through feature flags and environment-aware settings so the same codebase can safely run phased rollouts.

#### Scenario: Kiosk disabled for restaurant

- **WHEN** a restaurant is not enabled for kiosk mode
- **THEN** kiosk routes and actions SHALL remain unavailable even if the client build contains kiosk UI code