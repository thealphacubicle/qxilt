"""HTTP client for Qxilt API."""

from typing import Any, Optional

import httpx

from qxilt.schemas import LeaderboardResponse, ReputationResponse, ReviewResponse


class QxiltClient:
    """Client for the Qxilt HTTP API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the Qxilt API (e.g. http://localhost:8000).
        """
        self.base_url = base_url.rstrip("/")

    def submit_review(
        self,
        reviewer_agent_id: str,
        target_agent_id: str,
        approved: bool,
        task_type: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ReviewResponse:
        """Submit a review event."""
        body: dict[str, Any] = {
            "reviewer_agent_id": reviewer_agent_id,
            "target_agent_id": target_agent_id,
            "approved": approved,
        }
        if task_type is not None:
            body["task_type"] = task_type
        if metadata is not None:
            body["metadata"] = metadata

        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/reviews",
                json=body,
            )
            response.raise_for_status()
            return ReviewResponse.model_validate(response.json())

    def get_reputation(
        self,
        target_agent_id: str,
        task_type: Optional[str] = None,
    ) -> ReputationResponse:
        """Get reputation for a target agent."""
        params: dict[str, str] = {}
        if task_type is not None:
            params["task_type"] = task_type

        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/agents/{target_agent_id}/reputation",
                params=params,
            )
            response.raise_for_status()
            return ReputationResponse.model_validate(response.json())

    def get_leaderboard(
        self,
        limit: int = 20,
        task_type: Optional[str] = None,
    ) -> LeaderboardResponse:
        """Get top agents by reputation."""
        params: dict[str, Any] = {"limit": limit}
        if task_type is not None:
            params["task_type"] = task_type

        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/leaderboard",
                params=params,
            )
            response.raise_for_status()
            return LeaderboardResponse.model_validate(response.json())
