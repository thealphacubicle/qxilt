"""Pytest fixtures for Qxilt tests."""

import os
from typing import Any
from unittest.mock import MagicMock

import pytest

# Set required env vars for config before any qxilt imports
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
from fastapi.testclient import TestClient

from qxilt.api.main import app
from qxilt.supabase_client import get_client


class MockSupabaseClient:
    """Mock Supabase client for API tests without a real Supabase instance."""

    def __init__(self) -> None:
        self._reviews: list[dict[str, Any]] = []
        self._agents: set[str] = set()

    def rpc(self, name: str, params: dict[str, Any]) -> MagicMock:
        """Mock RPC calls."""
        result = MagicMock()

        if name == "submit_review":
            reviewer = params.get("p_reviewer_agent_id", "")
            target = params.get("p_target_agent_id", "")
            approved = params.get("p_approved", False)
            task_type = params.get("p_task_type")
            metadata = params.get("p_metadata")
            self._agents.add(reviewer)
            self._agents.add(target)
            review = {
                "id": f"review-{len(self._reviews)}",
                "reviewer_agent_id": reviewer,
                "target_agent_id": target,
                "approved": approved,
                "task_type": task_type,
                "metadata_json": metadata,
                "created_at": "2024-01-01T00:00:00Z",
            }
            self._reviews.append(review)
            result.data = review
        elif name == "get_agent_reputation":
            target = params.get("p_target_agent_id", "")
            task_type = params.get("p_task_type")
            agent_exists = target in self._agents
            if not agent_exists:
                result.data = []
            else:
                matching = [
                    r
                    for r in self._reviews
                    if r["target_agent_id"] == target and (task_type is None or r.get("task_type") == task_type)
                ]
                approvals = sum(1 for r in matching if r["approved"])
                rejections = len(matching) - approvals
                result.data = [
                    {
                        "target_agent_id": target,
                        "approvals": approvals,
                        "rejections": rejections,
                        "total_reviews": len(matching),
                    }
                ]
        elif name == "get_leaderboard_counts":
            task_type = params.get("p_task_type")
            max_rows = params.get("p_max_rows", 1000)
            by_target: dict[str, tuple[int, int]] = {}
            for r in self._reviews:
                if task_type is not None and r.get("task_type") != task_type:
                    continue
                t = r["target_agent_id"]
                if t not in by_target:
                    by_target[t] = (0, 0)
                a, rej = by_target[t]
                if r["approved"]:
                    by_target[t] = (a + 1, rej)
                else:
                    by_target[t] = (a, rej + 1)
            result.data = [
                {"target_agent_id": t, "approvals": a, "rejections": rej}
                for t, (a, rej) in by_target.items()
            ][:max_rows]
        else:
            result.data = []

        result.execute = lambda: result
        return result


@pytest.fixture
def mock_supabase_client() -> MockSupabaseClient:
    """Create a fresh mock Supabase client."""
    return MockSupabaseClient()


@pytest.fixture
def client(mock_supabase_client: MockSupabaseClient) -> TestClient:
    """Create TestClient with mocked Supabase."""
    def override_get_client():
        return mock_supabase_client

    app.dependency_overrides[get_client] = override_get_client
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
