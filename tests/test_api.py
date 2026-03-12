"""API integration tests."""

import pytest
from fastapi.testclient import TestClient


def test_submit_review_and_get_reputation(client: TestClient) -> None:
    """POST a review, then GET reputation for the target agent."""
    # Submit review
    response = client.post(
        "/reviews",
        json={
            "reviewer_agent_id": "agent_A",
            "target_agent_id": "agent_B",
            "approved": True,
            "task_type": "forecasting",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reviewer_agent_id"] == "agent_A"
    assert data["target_agent_id"] == "agent_B"
    assert data["approved"] is True
    assert data["task_type"] == "forecasting"

    # Get reputation
    response = client.get("/agents/agent_B/reputation")
    assert response.status_code == 200
    data = response.json()
    assert data["target_agent_id"] == "agent_B"
    assert data["approvals"] == 1
    assert data["rejections"] == 0
    assert data["total_reviews"] == 1
    assert data["posterior_mean"] > 0.5
    assert data["lower_bound_score"] > 0
    assert data["lower_bound_score"] < data["posterior_mean"]


def test_reputation_404_for_unknown_agent(client: TestClient) -> None:
    """GET reputation for non-existent agent returns 404."""
    response = client.get("/agents/nonexistent_agent/reputation")
    assert response.status_code == 404


def test_leaderboard(client: TestClient) -> None:
    """Submit reviews and fetch leaderboard."""
    client.post(
        "/reviews",
        json={
            "reviewer_agent_id": "r1",
            "target_agent_id": "agent_X",
            "approved": True,
        },
    )
    client.post(
        "/reviews",
        json={
            "reviewer_agent_id": "r2",
            "target_agent_id": "agent_Y",
            "approved": False,
        },
    )

    response = client.get("/leaderboard?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    items = data["items"]
    assert len(items) == 2
    # agent_X has 1 approval, agent_Y has 1 rejection - X should rank higher
    assert items[0]["target_agent_id"] == "agent_X"
    assert items[0]["lower_bound_score"] > items[1]["lower_bound_score"]
