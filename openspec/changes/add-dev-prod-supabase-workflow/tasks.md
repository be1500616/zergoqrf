## 1. Environment Contract
- [ ] 1.1 Define `local`, `ci`, and `prod` profile matrix for backend/frontend config and secrets.
- [ ] 1.2 Add startup validation for required env vars per profile.
- [ ] 1.3 Document profile switching commands and expected behavior.

## 2. Supabase Boundary and Adapters
- [ ] 2.1 Identify high-priority slices (`auth`, `cart`, `orders`) for boundary-first wiring.
- [ ] 2.2 Add/normalize interface-based repository injection at use-case layer.
- [ ] 2.3 Provide local/mock adapters for non-integration test execution.

## 3. Testing Workflow
- [ ] 3.1 Define Tier A test command set (fast local + CI default).
- [ ] 3.2 Define Tier B Supabase integration test command set.
- [ ] 3.3 Add CI job separation and failure policy for each tier.

## 4. Deployment and Promotion
- [ ] 4.1 Define migration promotion checklist (dev -> staging-like -> prod).
- [ ] 4.2 Add RLS verification and auth smoke checks to release gates.
- [ ] 4.3 Define branch/release policy for when Tier B must pass.

## 5. Verification
- [ ] 5.1 Run OpenSpec strict validation for this change.
- [ ] 5.2 Review artifacts with stakeholder and finalize implementation scope.
