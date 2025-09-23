# ZERGO Frontend (Flutter)

Flutter app with GetX, GoRouter, and Supabase; feature-based vertical slices.

## Run locally

Prereqs: Flutter (stable), `.env` in this folder with Supabase keys.

```
cp .env.example .env
flutter pub get
flutter run -d chrome  # or iOS/Android
```

## Structure

- `lib/core/` — Supabase init, API clients, themes
- `lib/shared/` — widgets, utils, constants
- `lib/features/{auth,menu,orders,admin}` — feature slices
