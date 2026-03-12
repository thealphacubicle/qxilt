"""Pydantic schemas for Qxilt API."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """Request body for creating a review."""

    reviewer_agent_id: str = Field(..., description="ID of the agent submitting the review")
    target_agent_id: str = Field(..., description="ID of the agent being reviewed")
    approved: bool = Field(..., description="Whether the review is positive (true) or negative (false)")
    task_type: Optional[str] = Field(default=None, description="Optional task type for task-specific reputation")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Optional metadata dict")


class ReviewResponse(BaseModel):
    """Response for a created review."""

    id: str
    reviewer_agent_id: str
    target_agent_id: str
    approved: bool
    task_type: Optional[str] = None
    metadata_json: Optional[dict[str, Any]] = None
    created_at: str


class ReputationResponse(BaseModel):
    """Response for agent reputation."""

    target_agent_id: str
    approvals: int
    rejections: int
    total_reviews: int
    posterior_mean: float
    lower_bound_score: float
    alpha: float
    beta: float


class LeaderboardResponse(BaseModel):
    """Response for leaderboard."""

    items: list[ReputationResponse]
