# Simple dev helpers
.PHONY: backend frontend docker-up docker-down test dev

backend:
	lsof -t -i :8000 | xargs kill -9 || true
	cd apps/backend && source .venv/bin/activate && PYTHONPATH=../../ uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd apps/frontend && flutter run -d chrome

docker-up:
	docker compose up --build backend

docker-down:
	docker compose down

test:
	cd apps/backend && pytest -q

# ponytail: one command, one outcome. If supabase CLI is missing, fall back
# to docker compose. Either way, migrations apply automatically.
dev:
	@if command -v supabase >/dev/null 2>&1; then \
		supabase start && supabase migration up; \
	else \
		echo "supabase CLI not found, falling back to docker compose" && \
		docker compose up -d db && \
		for f in infra/supabase/migrations/*.sql; do \
			psql "$$DATABASE_URL" --single-transaction --set ON_ERROR_STOP=on -f $$f; \
		done; \
	fi
