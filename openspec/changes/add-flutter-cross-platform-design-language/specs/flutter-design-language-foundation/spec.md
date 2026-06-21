## ADDED Requirements

### Requirement: Semantic Token Contract

The Flutter frontend SHALL define and consume a semantic design token contract for color roles, spacing, typography, radius, elevation, and motion so that feature code does not depend on hard-coded raw style values.

#### Scenario: Tokenized styling used in shared components

- **WHEN** a shared component is implemented or updated
- **THEN** its visual styling MUST reference semantic tokens exposed through the design language layer

#### Scenario: Theme mapping remains platform-aware

- **WHEN** the application runs on iOS, Android, or web
- **THEN** token-to-theme mappings MUST preserve semantic meaning while allowing platform-specific value adaptation

### Requirement: Responsive and Adaptive Scale Rules

The Flutter frontend SHALL define deterministic breakpoint and scale behavior for typography and spacing across phone, tablet, and web form factors.

#### Scenario: Consistent typography across device classes

- **WHEN** the same screen is rendered on phone and tablet/web breakpoints
- **THEN** typography levels MUST follow documented scale rules without ad-hoc overrides

#### Scenario: Spacing and layout rhythm follows system rules

- **WHEN** a feature screen introduces new layout structure
- **THEN** spacing MUST use defined scale steps and breakpoint-aware rules from the design language foundation