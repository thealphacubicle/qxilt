.PHONY: dev prod install test dev-setup dev-stop help

help:
	@echo "Qxilt Makefile"
	@echo ""
	@echo "  make dev         Run API with dev env (.env.local, Supabase local)"
	@echo "  make prod        Run API with prod env (.env, hosted Supabase)"
	@echo "  make install     Install package with dev deps"
	@echo "  make test        Run pytest"
	@echo "  make dev-setup   Start Supabase, reset DB, create .env.local"
	@echo "  make dev-stop    Stop dev resources (local Supabase only)"

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

dev-stop:
	supabase stop
