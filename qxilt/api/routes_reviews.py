"""Review API routes."""

from fastapi import APIRouter, Depends, status
from supabase import Client

from qxilt.schemas import ReviewCreate, ReviewResponse
from qxilt.services.reviews import submit_review
from qxilt.supabase_client import get_client

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    body: ReviewCreate,
    client: Client = Depends(get_client),
) -> ReviewResponse:
    """Submit a review event."""
    return submit_review(
        client=client,
        reviewer_agent_id=body.reviewer_agent_id,
        target_agent_id=body.target_agent_id,
        approved=body.approved,
        task_type=body.task_type,
        metadata=body.metadata,
    )
