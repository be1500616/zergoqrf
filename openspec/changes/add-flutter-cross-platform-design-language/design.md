## Context

ZERGO QR is expanding Flutter surfaces across phone, tablet, and web usage contexts for restaurant operators and guests. UI work currently depends on local implementation decisions, which increases drift in spacing, color semantics, typography scale, and interaction behavior. Because onboarding, menu, QR, and order operations are cross-cutting journeys, inconsistent components create measurable UX and maintenance costs.

The project needs one design language that is strict enough to keep brand and usability consistent, while allowing platform-appropriate affordances (e.g., Cupertino conventions, Android interactions, desktop/web focus behavior). This design must work with the existing Flutter stack (GetX, GoRouter) and support iterative rollout without a big-bang rewrite.

## Goals / Non-Goals

**Goals:**

- Define a canonical token system and theming contract for Flutter applications.
- Define shared component requirements (states, behavior, accessibility, and adaptation rules) for core UI primitives and business-critical composites.
- Establish contribution governance so designers and engineers can evolve the design language safely.
- Add lightweight quality gates to prevent regressions in visual consistency and accessibility.
- Enable phased adoption in existing features without blocking product delivery.

**Non-Goals:**

- Re-implement every existing screen in this change.
- Replace Flutter's Material/Cupertino systems with a fully custom rendering stack.
- Introduce backend, API, or RLS behavior changes.

## Decisions

### Decision 1: Use semantic design tokens as the single source of visual truth

- **Choice:** Introduce semantic tokens (color roles, spacing scale, type scale, radius, elevation, motion durations/curves) mapped to Flutter theme extensions.
- **Rationale:** Semantic tokens decouple intent from hard-coded values and allow platform adaptation without changing feature code.
- **Alternatives considered:**
  - Direct per-widget styling: rejected because drift and duplication increase rapidly.
  - Pure brand-token-only system without semantic layer: rejected because feature teams need stable intent-based API surface.

### Decision 2: Create a component standards catalog with explicit state and behavior contracts

- **Choice:** Define a standards set for foundational widgets (buttons, inputs, cards, chips, dialogs, navigation, feedback surfaces) and key composites for restaurant operations.
- **Rationale:** Shared requirements reduce implementation variance and make acceptance criteria testable.
- **Alternatives considered:**
  - Only publish design mocks and rely on interpretation: rejected due to ambiguous implementation and inconsistent accessibility.
  - Standardize only primitive widgets: rejected because user flows depend heavily on repeated composites.

### Decision 3: Establish a platform adaptation matrix

- **Choice:** Define per-platform adaptation boundaries (must-match brand elements vs may-adapt interaction details) for iOS, Android, web, and large-screen contexts.
- **Rationale:** Preserves coherence while respecting native expectations and input models.
- **Alternatives considered:**
  - Fully identical UI on all platforms: rejected due to poor platform ergonomics.
  - Fully platform-native divergence: rejected because brand and workflow consistency would degrade.

### Decision 4: Adopt governance with versioning and deprecation lifecycle

- **Choice:** Require design-system change proposals, version bumping, migration notes, and deprecation windows for tokens/components.
- **Rationale:** Prevents uncontrolled breaking UI changes and keeps teams aligned during parallel delivery.
- **Alternatives considered:**
  - Informal Slack/PR-only governance: rejected because it is hard to audit and enforce at scale.

### Decision 5: Add quality gates in CI and review checklists

- **Choice:** Introduce required checks for contrast, touch target size, focus/keyboard behavior (web), and representative golden/screenshot tests for core components.
- **Rationale:** Early detection of UI drift is lower cost than manual cleanup.
- **Alternatives considered:**
  - Manual QA only: rejected because results are inconsistent and late.

## Risks / Trade-offs

- **[Risk] Increased initial process overhead for feature teams** -> **Mitigation:** Start with a minimal component baseline and phase in stricter gates over time.
- **[Risk] Token abstraction may feel complex early on** -> **Mitigation:** Provide usage examples, migration guide snippets, and lint/checklist support.
- **[Risk] Platform adaptation disagreements** -> **Mitigation:** Encode adaptation decisions in a published matrix with design+engineering sign-off.
- **[Risk] Legacy screens remain inconsistent during migration** -> **Mitigation:** Prioritize high-traffic flows first and track adoption progress as a defined roadmap.

## Migration Plan

1. Define and publish v1 token contract and theme extension mappings.
2. Standardize core components and provide implementation usage guidance.
3. Apply quality gates to newly changed UI first; do not block untouched legacy screens.
4. Migrate critical flows in phases (onboarding, menu operations, order lifecycle surfaces).
5. Deprecate non-compliant legacy patterns with migration windows and owner assignment.
6. Roll back by disabling strict enforcement gates if release risk is detected, while keeping non-breaking token/component docs intact.

## Open Questions

- Which feature area should be the first migration pilot for the fastest confidence gain?
- What baseline device matrix (phone/tablet/web breakpoints) should be mandatory for UI verification?
- Should Figma token exports be automated in this phase or introduced after v1 stabilization?