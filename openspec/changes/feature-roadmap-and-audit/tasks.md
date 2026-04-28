# Tasks: Feature Roadmap and Audit

## Infrastructure
- [ ] Audit `infra/supabase/migrations/` <!-- id: i1 -->
- [ ] Verify `seed.sql` consistency <!-- id: i2 -->
- [ ] Test DB connection and migrations <!-- id: i3 -->

## Backend
- [ ] Audit `apps/backend/app/features/auth/` <!-- id: b1 -->
- [ ] Verify JWT logic and middleware <!-- id: b2 -->
- [ ] Audit `apps/backend/app/features/restaurants/` <!-- id: b3 -->
- [ ] Audit `apps/backend/app/features/menu/` and `apps/backend/app/features/orders/` <!-- id: b4 -->
- [ ] Verify backend test coverage with `pytest` <!-- id: b5 -->

## Frontend
- [ ] Audit `apps/frontend/lib/shared/onboarding/` <!-- id: f1 -->
- [ ] Audit `apps/frontend/lib/features/restaurants/` (registration screen) <!-- id: f2 -->
- [ ] Verify frontend test coverage with `flutter test` <!-- id: f3 -->

## Git Organization
- [ ] Create logical commits for validated infrastructure <!-- id: g1 -->
- [ ] Create logical commits for validated backend features <!-- id: g2 -->
- [ ] Create logical commits for validated frontend features <!-- id: g3 -->
