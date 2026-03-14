.PHONY: dev prod install test dev-setup dev-stop docker-build-dev docker-build-prod docker-run-dev docker-run-prod deploy-prod print-secrets-prod help

help:
	@echo "Qxilt Makefile"
	@echo ""
	@echo "  make dev              Run API with dev env (.env.local, Supabase local)"
	@echo "  make prod             Run API with prod env (.env, hosted Supabase)"
	@echo "  make install          Install package with dev deps"
	@echo "  make test             Run pytest"
	@echo "  make dev-setup        Start Supabase, reset DB, create .env.local"
	@echo "  make dev-stop         Stop dev resources (local Supabase only)"
	@echo "  make docker-build-dev  Build Docker image (dev, hot reload)"
	@echo "  make docker-build-prod Build Docker image (prod)"
	@echo "  make docker-run-dev    Run dev container (local Supabase via host.docker.internal)"
	@echo "  make docker-run-prod  Run prod container"
	@echo "  make deploy-prod      Trigger Koyeb redeploy (requires KOYEB_TOKEN)"
	@echo "  make print-secrets-prod Print env var keys from .env.prod.example"

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

docker-run-dev:
	docker run -p 8000:8000 --env-file .env.local -e SUPABASE_URL=http://host.docker.internal:54321 qxilt:dev

docker-run-prod:
	docker run -p 8000:8000 --env-file .env qxilt:prod

deploy-prod:
	koyeb service redeploy qxilt-api-prod/api

print-secrets-prod:
	@echo "SUPABASE_URL="
	@echo "SUPABASE_SERVICE_ROLE_KEY="
	@echo "QXILT_ALPHA="
	@echo "QXILT_BETA="
	@echo "QXILT_CONFIDENCE_LEVEL="
	@echo "QXILT_API_BASE_URL="
