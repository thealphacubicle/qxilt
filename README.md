# Qxilt

A reputation engine for AI agents. Submit reviews, compute Bayesian trust scores, and query reputation via SDK, API, or CLI.

---

## Why Qxilt?

When AI agents interact with each other, they need a way to build trust. Qxilt enables agent developers to:

- **Submit review events** after one agent interacts with another (approved or rejected)
- **Compute Bayesian trust scores** that handle cold start and avoid naive raw-average ranking
- **Query reputation** for any agent and list top agents by reputation

---

## Architecture

| Component | Technology |
|-----------|------------|
| Data backend | Supabase (Postgres) |
| Schema & migrations | Supabase CLI |
| Data access | `supabase-py` |
| Aggregation | Postgres RPC functions |
| Scoring | Beta-Bernoulli model (Python) |

---

## Quick Start

### Install

```bash
pip install -e .
```

### Development setup

For detailed database setup, environment configuration, and troubleshooting, see **[docs/DEV.md](docs/DEV.md)**.

```bash
make dev-setup   # Start Supabase, reset DB, create .env.local
make dev         # Run the API
```

API docs: http://localhost:8000/docs

---

## Bayesian Scoring

Qxilt uses a Beta-Bernoulli model:

- **Prior**: Beta(α, β) — default α=5, β=5 (weak prior centered at 0.5)
- **Posterior**: Beta(α + approvals, β + rejections)
- **Posterior mean**: Expected approval probability
- **Lower bound score**: (1−confidence)/2 quantile — a conservative score that rewards agents with more reviews

This handles cold start (new agents start at the prior) and avoids ranking by raw averages.

---

## Usage

### CLI

```bash
# Submit a review
qxilt review --reviewer agent_A --target agent_B --approved true --task forecasting

# Get reputation for an agent
qxilt reputation agent_B

# Get leaderboard
qxilt leaderboard --limit 10
```

Use `--api-url` to point at a different API (default: `http://localhost:8000` or `QXILT_API_BASE_URL`).

### SDK

```python
from qxilt.sdk.client import QxiltClient

client = QxiltClient(base_url="http://localhost:8000")

# Submit a review
client.submit_review(
    reviewer_agent_id="agent_A",
    target_agent_id="agent_B",
    approved=True,
    task_type="forecasting",
)

# Get reputation
reputation = client.get_reputation("agent_B")
print(reputation.posterior_mean, reputation.lower_bound_score)

# Get leaderboard
leaderboard = client.get_leaderboard(limit=10)
```

### API

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/reviews` | Submit a review event |
| GET | `/agents/{target_agent_id}/reputation` | Get reputation for an agent |
| GET | `/leaderboard` | Get top agents by reputation |
| GET | `/reviews/healthz` | Liveness (Kubernetes) / uptime monitor — reviews service |
| GET | `/reviews/readyz` | Readiness (Kubernetes) — reviews + Supabase |
| GET | `/reputation/healthz` | Liveness (Kubernetes) / uptime monitor — reputation service |
| GET | `/reputation/readyz` | Readiness (Kubernetes) — reputation + Supabase |

**Example curl:**

```bash
curl -X POST http://localhost:8000/reviews \
  -H "Content-Type: application/json" \
  -d '{"reviewer_agent_id":"agent_A","target_agent_id":"agent_B","approved":true,"task_type":"forecasting"}'
```

---

## Tests

```bash
pytest
```

API tests use a mocked Supabase client; no running instance is required. For integration tests against a real Supabase, set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` and run `supabase start` first.

---

## Docker

```bash
make docker-build-dev   # Dev image (hot reload)
make docker-build-prod # Prod image
docker run -p 8000:8000 --env-file .env qxilt:prod
```

**Local Supabase:** Use `-e SUPABASE_URL=http://host.docker.internal:54321` so the container can reach Supabase on your host. See [docs/DEV.md](docs/DEV.md#docker).

---

## Project Structure

```
qxilt/
├── docs/
│   └── DEV.md              # Developer guide (DB setup, migrations, env)
├── supabase/
│   ├── migrations/         # SQL schema and RPC functions
│   ├── config.toml         # Local Supabase config
│   └── seed.sql            # Dev seed data
├── qxilt/
│   ├── config.py           # Settings (Supabase, Beta prior)
│   ├── supabase_client.py  # Supabase client
│   ├── schemas.py          # Pydantic models
│   ├── scoring/reputation.py
│   ├── services/           # Business logic
│   ├── api/                # FastAPI routes
│   ├── sdk/                # HTTP client
│   └── cli/                # Typer CLI
└── tests/
```

---

## License

MIT
