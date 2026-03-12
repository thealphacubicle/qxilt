#!/usr/bin/env bash
# Dev setup: start Supabase, reset DB (or apply migrations only if data exists),
# create .env.local from example if missing, inject API URL + service_role key.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_LOCAL="$PROJECT_ROOT/.env.local"
ENV_LOCAL_EXAMPLE="$PROJECT_ROOT/.env.local.example"

cd "$PROJECT_ROOT"

echo "==> Starting Supabase local..."
supabase start

echo ""
# Check if DB already has data — if so, apply migrations only (no seed)
DB_URL=$(supabase status -o env 2>/dev/null | grep -E '^DB_URL=' | cut -d= -f2- | tr -d '"' | head -1)
if [[ -z "$DB_URL" ]]; then
  DB_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres"
fi

AGENT_COUNT=$(psql "$DB_URL" -t -A -c "SELECT COUNT(*) FROM public.agents" 2>/dev/null || echo "0")
if [[ "${AGENT_COUNT:-0}" -gt 0 ]]; then
  echo "==> DB has data — applying migrations only (skipping seed)..."
  supabase migration up
else
  echo "==> Resetting DB (migrations + seed)..."
  supabase db reset
fi

echo ""
if [[ ! -f "$ENV_LOCAL" ]]; then
  echo "==> Creating .env.local from .env.local.example..."
  cp "$ENV_LOCAL_EXAMPLE" "$ENV_LOCAL"
fi

# Try to inject SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from supabase status
STATUS_ENV=$(supabase status -o env 2>/dev/null) || true
if [[ -n "$STATUS_ENV" ]]; then
  API_URL=$(echo "$STATUS_ENV" | grep -E '^API_URL=' | cut -d= -f2- | tr -d '"' | head -1)
  SERVICE_ROLE_KEY=$(echo "$STATUS_ENV" | grep -E '^SERVICE_ROLE_KEY=' | cut -d= -f2- | tr -d '"' | head -1)
    if [[ -n "$API_URL" && -n "$SERVICE_ROLE_KEY" ]]; then
    echo "==> Injecting SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY into .env.local..."
    if [[ "$(uname)" == "Darwin" ]]; then
      sed -i '' "s#^SUPABASE_URL=.*#SUPABASE_URL=$API_URL#" "$ENV_LOCAL"
      sed -i '' "s#^SUPABASE_SERVICE_ROLE_KEY=.*#SUPABASE_SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY#" "$ENV_LOCAL"
    else
      sed -i "s#^SUPABASE_URL=.*#SUPABASE_URL=$API_URL#" "$ENV_LOCAL"
      sed -i "s#^SUPABASE_SERVICE_ROLE_KEY=.*#SUPABASE_SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY#" "$ENV_LOCAL"
    fi
  else
    echo "==> Could not parse API_URL/SERVICE_ROLE_KEY from supabase status."
    echo "    Run 'supabase status' and paste the service_role key into .env.local manually."
  fi
else
  echo "==> Could not run 'supabase status -o env'. Paste the service_role key into .env.local manually."
fi

echo ""
echo "==> Dev setup complete. Run 'make dev' to start the API."
