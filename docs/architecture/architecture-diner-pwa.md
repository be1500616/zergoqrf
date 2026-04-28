# Architecture Decision: Diner PWA in Monorepo (Integrated in apps/frontend)

## Decision
Implement the diner-facing Progressive Web App (PWA) as a new feature module inside the existing Flutter app at `apps/frontend` (Clean Architecture, vertical slice under `lib/features/diner/`).

## Rationale
- Speed of delivery: Reuse existing Flutter, routing (go_router), DI (GetX), and API config.
- Shared kernel: Reuse Supabase/bootstrap and common styles as needed.
- Deployment simplicity: Single web build pipeline initially.
- Separation-by-feature: The diner code is fully co-located and isolated under `lib/features/diner/`, enabling future extraction to a dedicated app if required.

## Trade-offs
- Bundle size: Single-app bundle may grow; if Lighthouse audits fail targets from Story 3.1, we will split into a dedicated `apps/diner_pwa` Flutter Web app to minimize payload.
- PWA assets: One manifest/service worker per app; we align branding generically initially and can fork later.

## Foundations Implemented
- Public diner routes: `/diner/:restaurantCode`.
- Feature slice `lib/features/diner/` with domain, application, infrastructure, presentation.
- Backend integration:
  - GET `/restaurants/{restaurant_code}` to resolve restaurant id.
  - GET `/menu/items?restaurant_id=...` for public items.
- Cart controller scaffold for order flow.

## Next Steps (Story 3.1-3.4 alignment)
1. Branding via restaurant settings (logo/colors) on header.
2. Category navigation + search, progressive images.
3. Cart page/sheet and POST `/orders/` integration with table-id when available.
4. PWA optimizations (offline cache strategy, image formats) and performance audits.

## Migration Option
If performance targets require, extract this slice into `apps/diner_pwa` using `flutter create --platforms web` and migrate the diner code with minimal changes.

