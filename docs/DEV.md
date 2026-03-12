# Qxilt Developer Guide

This document provides detailed technical instructions for setting up the Qxilt database and development environment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Architecture](#database-architecture)
3. [Schema Overview](#schema-overview)
4. [Migrations](#migrations)
5. [RPC Functions](#rpc-functions)
6. [Local Development Setup](#local-development-setup)
7. [Hosted Supabase (Production) Setup](#hosted-supabase-production-setup)
8. [Environment Variables](#environment-variables)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Purpose |
|-------------|---------|
| **Python 3.10+** | Runtime for the Qxilt API, SDK, and CLI |
| **Supabase CLI** | Local Supabase instance, migrations, and DB management |
| **Docker** | Required by `supabase start` to run Postgres, Auth, etc. |

### Installing Supabase CLI

```bash
# macOS (Homebrew)
brew install supabase/tap/supabase

# npm
npm install -g supabase

# Or see: https://supabase.com/docs/guides/local-development/cli/getting-started
```

---

## Database Architecture

Qxilt uses **Supabase** (Postgres) as its data backend:

- **Schema & migrations** — Managed via Supabase CLI (`supabase/migrations/`)
- **Data access** — Via `supabase-py` client with service role key
- **Aggregation logic** — Postgres RPC functions for review counts
- **Scoring** — Bayesian (Beta-Bernoulli) computed in Python

---

## Schema Overview

### `public.agents`

| Column | Type | Description |
|--------|------|-------------|
| `id` | `uuid` | Primary key (auto-generated) |
| `agent_id` | `text` | Unique agent identifier |
| `created_at` | `timestamptz` | Auto-set on insert |

Agents are created implicitly when they submit or receive their first review.

### `public.reviews`

| Column | Type | Description |
|--------|------|-------------|
| `id` | `uuid` | Primary key (auto-generated) |
| `reviewer_agent_id` | `text` | Agent who submitted the review |
| `target_agent_id` | `text` | Agent being reviewed |
| `approved` | `boolean` | Whether the interaction was approved |
| `task_type` | `text` | Optional task category (e.g. `forecasting`, `summarization`) |
| `metadata_json` | `jsonb` | Optional arbitrary metadata |
| `created_at` | `timestamptz` | Auto-set on insert |

---

## Migrations

Migrations live in `supabase/migrations/` and run in order:

| File | Purpose |
|------|---------|
| `0001_init.sql` | Creates `agents` and `reviews` tables |
| `0002_reputation_functions.sql` | Adds RPC functions: `submit_review`, `get_agent_reputation`, `get_leaderboard_counts` |
| `0003_indexes.sql` | Adds indexes on `target_agent_id` and `task_type` for query performance |

### Applying migrations

```bash
# Local: migrations run automatically on `supabase db reset`
supabase db reset

# Hosted: link project and push
supabase link --project-ref <your-project-ref>
supabase db push
```

---

## RPC Functions

### `public.submit_review(p_reviewer_agent_id, p_target_agent_id, p_approved, p_task_type?, p_metadata?)`

- Inserts reviewer and target into `agents` (upsert if exists)
- Inserts a new row into `reviews`
- Returns the inserted review as JSONB
- **Security**: `SECURITY DEFINER` with `search_path = ''` for safe execution

### `public.get_agent_reputation(p_target_agent_id, p_task_type?)`

- Returns `(target_agent_id, approvals, rejections, total_reviews)` for the given agent
- Optional `task_type` filter
- Returns empty if agent does not exist

### `public.get_leaderboard_counts(p_task_type?, p_max_rows?)`

- Returns `(target_agent_id, approvals, rejections)` for all agents with reviews
- Optional `task_type` filter
- `p_max_rows` defaults to 1000

---

## Local Development Setup

### 1. Supabase configuration

`supabase/config.toml` configures the local instance:

- **API port**: 54321
- **DB port**: 54322
- **Studio port**: 54323
- **Postgres**: v15
- **Seed**: `supabase/seed.sql` runs after migrations on `db reset`

### 2. Quick setup (recommended)

```bash
make dev-setup
```

This script:

1. Starts Supabase local (`supabase start`)
2. Resets the DB (runs migrations + seed)
3. Creates `.env.local` from `.env.local.example` if missing
4. Injects `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from `supabase status`

### 3. Manual setup

```bash
# Start Supabase
supabase start

# Reset DB (migrations + seed)
supabase db reset

# Create env file
cp .env.local.example .env.local

# Get credentials from supabase status
supabase status

# Paste API_URL and SERVICE_ROLE_KEY into .env.local
# Or use: supabase status -o env
```

### 4. Seed data

`supabase/seed.sql` inserts sample agents and reviews for local testing:

- Agents: `agent_A`, `agent_B`, `agent_C`
- Sample reviews across forecasting and summarization tasks

---

## Hosted Supabase (Production) Setup

### 1. Create a project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Note the **Project URL** and **Service Role Key** (Project Settings → API)

### 2. Run migrations

```bash
# Link your project
supabase link --project-ref <your-project-ref>

# Push migrations
supabase db push
```

### 3. Configure environment

```bash
cp .env.prod.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
```

### 4. Run the API

```bash
make prod
# Or: QXILT_ENV=prod uvicorn qxilt.api.main:app --reload
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase API URL (e.g. `http://localhost:54321` or `https://xxx.supabase.co`) |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key for server-side operations |
| `QXILT_ALPHA` | No | Beta prior α (default: 5) |
| `QXILT_BETA` | No | Beta prior β (default: 5) |
| `QXILT_CONFIDENCE_LEVEL` | No | Confidence for lower-bound score (default: 0.95) |
| `QXILT_API_BASE_URL` | No | Base URL for API (used by CLI/SDK, default: `http://localhost:8000`) |
| `QXILT_ENV` | No | `dev` uses `.env.local`, `prod` uses `.env` (default: `prod`) |

### Config loading

- **`QXILT_ENV=dev`** → loads `.env.local` (Supabase local)
- **`QXILT_ENV=prod`** (default) → loads `.env` (hosted Supabase)

---

## Troubleshooting

### Port conflicts

If ports 54321–54323 are in use, edit `supabase/config.toml` to change `api.port`, `db.port`, and `studio.port`.

### "Could not parse API_URL/SERVICE_ROLE_KEY"

Run `supabase status` and manually copy the values into `.env.local`:

```
API URL: http://127.0.0.1:54321
service_role key: eyJ...
```

### Migration failures

```bash
# Reset local DB from scratch
supabase db reset

# For hosted: check migration history
supabase migration list
```

### Docker not running

`supabase start` requires Docker. Ensure Docker Desktop (or equivalent) is running before starting Supabase.

### Database connection refused

- Ensure `supabase start` has completed successfully
- Verify `SUPABASE_URL` in `.env.local` matches the output of `supabase status`
