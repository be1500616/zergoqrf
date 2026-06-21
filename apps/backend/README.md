# Backend

FastAPI service for the ZERGO QR ordering platform.

## Local development

```bash
make dev
```

`make dev` brings up a usable local Postgres and applies every migration in
`infra/supabase/migrations/` in lexical order. It prefers the Supabase CLI
(``supabase start`` + ``supabase migration up``) and falls back to
``docker compose up -d db`` plus a ``psql`` loop if the CLI is not on PATH.

The backend reads its `DATABASE_URL` from `DATABASE_URL` (profile `local`) or
`SUPABASE_{PROFILE}_DB_URL` (profile `dev`/`test`/`prod`). Startup fails fast
with a readable error if the URL is missing or unparseable — no ghost
hostnames.
