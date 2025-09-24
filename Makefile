# Simple dev helpers
.PHONY: backend frontend docker-up docker-down test

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
