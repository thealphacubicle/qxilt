"""Reputation and leaderboard services."""

from typing import Optional

from supabase import Client

from qxilt.config import get_settings
from qxilt.schemas import ReputationResponse
from qxilt.scoring.reputation import compute_reputation


def get_reputation(
    client: Client,
    target_agent_id: str,
    task_type: Optional[str] = None,
) -> ReputationResponse:
    """
    Get reputation for a target agent.

    Returns 404-equivalent (raises ValueError) if agent does not exist.
    """
    params: dict = {
        "p_target_agent_id": target_agent_id,
    }
    if task_type is not None:
        params["p_task_type"] = task_type

    response = client.rpc("get_agent_reputation", params).execute()

    if not response.data or (isinstance(response.data, list) and len(response.data) == 0):
        raise ValueError(f"Agent not found: {target_agent_id}")

    data = response.data
    if isinstance(data, list):
        data = data[0]

    approvals = int(data.get("approvals", 0))
    rejections = int(data.get("rejections", 0))
    total_reviews = int(data.get("total_reviews", 0))

    settings = get_settings()
    scores = compute_reputation(
        approvals=approvals,
        rejections=rejections,
        alpha=settings.beta_alpha,
        beta=settings.beta_beta,
        confidence=settings.confidence_level,
    )

    return ReputationResponse(
        target_agent_id=target_agent_id,
        approvals=approvals,
        rejections=rejections,
        total_reviews=total_reviews,
        posterior_mean=scores["posterior_mean"],
        lower_bound_score=scores["lower_bound_score"],
        alpha=scores["alpha"],
        beta=scores["beta"],
    )


def get_leaderboard(
    client: Client,
    limit: int = 20,
    task_type: Optional[str] = None,
) -> list[ReputationResponse]:
    """
    Get top agents by lower confidence bound score.
    """
    params: dict = {
        "p_max_rows": 1000,
    }
    if task_type is not None:
        params["p_task_type"] = task_type

    response = client.rpc("get_leaderboard_counts", params).execute()

    if not response.data:
        return []

    rows = response.data if isinstance(response.data, list) else [response.data]
    settings = get_settings()

    results: list[ReputationResponse] = []
    for row in rows:
        target_agent_id = row.get("target_agent_id", "")
        approvals = int(row.get("approvals", 0))
        rejections = int(row.get("rejections", 0))
        total_reviews = approvals + rejections

        scores = compute_reputation(
            approvals=approvals,
            rejections=rejections,
            alpha=settings.beta_alpha,
            beta=settings.beta_beta,
            confidence=settings.confidence_level,
        )

        results.append(
            ReputationResponse(
                target_agent_id=target_agent_id,
                approvals=approvals,
                rejections=rejections,
                total_reviews=total_reviews,
                posterior_mean=scores["posterior_mean"],
                lower_bound_score=scores["lower_bound_score"],
                alpha=scores["alpha"],
                beta=scores["beta"],
            )
        )

    # Sort by lower_bound_score descending
    results.sort(key=lambda r: r.lower_bound_score, reverse=True)
    return results[:limit]
