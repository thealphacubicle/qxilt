"""Reputation API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from qxilt.schemas import LeaderboardResponse, ReputationResponse
from qxilt.services.reputation import get_leaderboard, get_reputation
from qxilt.supabase_client import get_client

router = APIRouter(tags=["reputation"])

# Health endpoints for reputation service (prefix /reputation)
reputation_health_router = APIRouter(prefix="/reputation", tags=["reputation-health"])


@reputation_health_router.get("/healthz")
def reputation_healthz() -> dict:
    """Liveness probe (Kubernetes) / uptime monitor — process is alive."""
    return {"status": "ok", "service": "reputation"}


@reputation_health_router.get("/readyz")
def reputation_readyz(client: Client = Depends(get_client)) -> dict:
    """Readiness probe (Kubernetes) — service + Supabase reachable."""
    try:
        client.table("agents").select("id").limit(1).execute()
        return {"status": "ok", "service": "reputation", "supabase": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "degraded", "service": "reputation", "supabase": str(e)},
        ) from e


@router.get("/agents/{target_agent_id}/reputation", response_model=ReputationResponse)
def get_agent_reputation(
    target_agent_id: str,
    task_type: Optional[str] = Query(default=None, description="Filter by task type"),
    client: Client = Depends(get_client),
) -> ReputationResponse:
    """Get reputation for a target agent."""
    try:
        return get_reputation(client=client, target_agent_id=target_agent_id, task_type=task_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/leaderboard", response_model=LeaderboardResponse)
def leaderboard(
    limit: int = Query(default=20, ge=1, le=100, description="Max number of agents to return"),
    task_type: Optional[str] = Query(default=None, description="Filter by task type"),
    client: Client = Depends(get_client),
) -> LeaderboardResponse:
    """Get top agents by reputation (lower confidence bound)."""
    items = get_leaderboard(client=client, limit=limit, task_type=task_type)
    return LeaderboardResponse(items=items)
