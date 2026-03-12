"""Review submission service."""

from typing import Any, Optional

from supabase import Client

from qxilt.schemas import ReviewCreate, ReviewResponse


def submit_review(
    client: Client,
    reviewer_agent_id: str,
    target_agent_id: str,
    approved: bool,
    task_type: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> ReviewResponse:
    """
    Submit a review event via RPC.

    Creates agent rows if they don't exist, then inserts the review.
    """
    params: dict[str, Any] = {
        "p_reviewer_agent_id": reviewer_agent_id,
        "p_target_agent_id": target_agent_id,
        "p_approved": approved,
    }
    if task_type is not None:
        params["p_task_type"] = task_type
    if metadata is not None:
        params["p_metadata"] = metadata

    response = client.rpc("submit_review", params).execute()

    if not response.data:
        raise RuntimeError("submit_review RPC returned no data")

    data = response.data
    if isinstance(data, list):
        data = data[0] if data else {}

    return ReviewResponse(
        id=str(data.get("id", "")),
        reviewer_agent_id=data.get("reviewer_agent_id", reviewer_agent_id),
        target_agent_id=data.get("target_agent_id", target_agent_id),
        approved=data.get("approved", approved),
        task_type=data.get("task_type"),
        metadata_json=data.get("metadata_json"),
        created_at=data.get("created_at", ""),
    )
