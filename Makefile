.PHONY: dev prod install test dev-setup dev-supabase-start dev-db-reset dev-supabase-stop help

help:
	@echo "Qxilt Makefile"
	@echo ""
	@echo "  make dev                 Run API with dev env (.env.local, Supabase local)"
	@echo "  make prod                Run API with prod env (.env, hosted Supabase)"
	@echo "  make install             Install package with dev deps"
	@echo "  make test                Run pytest"
	@echo "  make dev-setup           Full dev setup: start Supabase, reset DB, create .env.local"
	@echo "  make dev-supabase-start  Start Supabase local (Docker)"
	@echo "  make dev-db-reset        Reset DB, run migrations + seed"
	@echo "  make dev-supabase-stop   Stop Supabase local"

dev:
	QXILT_ENV=dev uvicorn qxilt.api.main:app --reload

prod:
	QXILT_ENV=prod uvicorn qxilt.api.main:app --reload

install:
	pip install -e ".[dev]"

test:
	pytest -v

dev-setup:
	./scripts/dev-setup.sh

dev-supabase-start:
	supabase start

dev-db-reset:
	supabase db reset

dev-supabase-stop:
	supabase stop
