.PHONY: dev prod install test dev-setup dev-stop docker-build-dev docker-build-prod help

help:
	@echo "Qxilt Makefile"
	@echo ""
	@echo "  make dev              Run API with dev env (.env.local, Supabase local)"
	@echo "  make prod             Run API with prod env (.env, hosted Supabase)"
	@echo "  make install          Install package with dev deps"
	@echo "  make test             Run pytest"
	@echo "  make dev-setup        Start Supabase, reset DB, create .env.local"
	@echo "  make dev-stop         Stop dev resources (local Supabase only)"
	@echo "  make docker-build-dev Build Docker image (dev, hot reload)"
	@echo "  make docker-build-prod Build Docker image (prod)"

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

docker-build-dev:
	docker build -f Dockerfile.dev -t qxilt:dev .

docker-build-prod:
	docker build -f Dockerfile.prod -t qxilt:prod .
