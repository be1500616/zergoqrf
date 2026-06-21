# Ponytail: one target, one outcome. The local stack is the default;
# other profiles only differ by env + which Supabase project they hit.
.PHONY: backend-local backend-dev backend-prod db-migrate db-reset \
        frontend docker-up docker-down test dev health cloud-migrate

# ponytail: APP_PROFILE=local is exported so app/core/config.py resolves
# the local stack. .env.local carries the rest of the keys. Gate on
# `supabase status` so the failure points at the real cause (no stack)
# instead of a downstream asyncpg/connection error.
backend-local:
	@supabase status > /dev/null 2>&1 || { \
		echo "❌ Local Supabase not running. Start it with: supabase start"; \
		exit 1; \
	}
	cd apps/backend && source .venv/bin/activate && \
	APP_PROFILE=local uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-dev:
	cd apps/backend && source .venv/bin/activate && \
	APP_PROFILE=dev uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ponytail: prod requires cloud config. Gate before uvicorn starts.
backend-prod:
	@test -n "$$SUPABASE_URL" || test -f apps/backend/.env.prod || { \
		echo "❌ No cloud config. Set SUPABASE_URL or create apps/backend/.env.prod"; \
		exit 1; \
	}
	cd apps/backend && source .venv/bin/activate && \
	APP_PROFILE=prod uvicorn app.main:app --host 0.0.0.0 --port 8000

# ponytail: apply infra migrations to the cloud DB. Uses the pooler URL
# (port 6543) — direct 5432 is blocked from outside Supabase's network.
# Requires SUPABASE_PROD_DB_URL in env.
cloud-migrate:
	@test -n "$$SUPABASE_PROD_DB_URL" || { \
		echo "❌ SUPABASE_PROD_DB_URL unset. Get it from Supabase dashboard → Database → Connection string (pooler, 6543)"; \
		exit 1; \
	}
	@$(MAKE) db-migrate DATABASE_URL="$$SUPABASE_PROD_DB_URL"

# ponytail: psql is the only sane path — supabase CLI requires `supabase link`
# AND a custom migrations path that config.toml doesn't declare; docker compose
# has no db service. Apply all 24 files in lexical order, single-tx per file.
db-migrate:
	@test -n "$$DATABASE_URL" || (echo "DATABASE_URL unset"; exit 1)
	@for f in infra/supabase/migrations/*.sql; do \
		echo "applying $$f"; \
		psql "$$DATABASE_URL" --single-transaction --set ON_ERROR_STOP=on -f "$$f" || exit 1; \
	done

# ponytail: same path as db-migrate but drops + recreates public schema first.
# Idempotent reset; non-destructive to auth/storage/graphql framework schemas.
db-reset:
	@test -n "$$DATABASE_URL" || (echo "DATABASE_URL unset"; exit 1)
	psql "$$DATABASE_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" && \
	$(MAKE) db-migrate

# ponytail: bring up the local stack + migrations + backend in one shot.
# supabase start already applies supabase/migrations/; infra/supabase/migrations/
# is the parallel set for backend direct-DB ops (function defs, etc.). Re-running
# is safe — CREATE TABLE IF NOT EXISTS, idempotent function defs.
dev:
	supabase start
	@echo "Applying backend migrations..."
	@$(MAKE) db-migrate DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres"
	$(MAKE) backend-local

frontend:
	cd apps/frontend && flutter run -d chrome

docker-up:
	docker compose up --build backend

docker-down:
	docker compose down

test:
	cd apps/backend && pytest -q

# ponytail: one curl, exit code is the truth. -f fails on non-2xx, -s silent.
health:
	@curl -sf http://localhost:8000/healthz > /dev/null \
		&& echo "✅ Backend healthy on :8000" \
		|| { echo "❌ Backend down on :8000"; exit 1; }
