"""Qxilt CLI."""

import os
from typing import Optional

import typer
from qxilt.sdk.client import QxiltClient

app = typer.Typer(
    name="qxilt",
    help="Qxilt - Reputation engine for AI agents",
)


def _get_client(api_url: Optional[str] = None) -> QxiltClient:
    """Get SDK client with API URL from env or argument."""
    url = api_url or os.environ.get("QXILT_API_BASE_URL", "http://localhost:8000")
    return QxiltClient(base_url=url)


def _parse_bool(value: str) -> bool:
    """Parse 'true'/'false' string to bool."""
    return value.lower() in ("true", "1", "yes")


@app.command()
def review(
    reviewer: str = typer.Option(..., "--reviewer", "-r", help="Reviewer agent ID"),
    target: str = typer.Option(..., "--target", "-t", help="Target agent ID"),
    approved: str = typer.Option(..., "--approved", "-a", help="Whether approved (true/false)"),
    task: Optional[str] = typer.Option(None, "--task", help="Task type (optional)"),
    api_url: Optional[str] = typer.Option(None, "--api-url", help="Qxilt API base URL"),
) -> None:
    """Submit a review event."""
    client = _get_client(api_url)
    result = client.submit_review(
        reviewer_agent_id=reviewer,
        target_agent_id=target,
        approved=_parse_bool(approved),
        task_type=task,
    )
    typer.echo(f"Review submitted: id={result.id}")


@app.command()
def reputation(
    agent_id: str = typer.Argument(..., help="Target agent ID"),
    task_type: Optional[str] = typer.Option(None, "--task", help="Filter by task type"),
    api_url: Optional[str] = typer.Option(None, "--api-url", help="Qxilt API base URL"),
) -> None:
    """Get reputation for an agent."""
    client = _get_client(api_url)
    try:
        result = client.get_reputation(target_agent_id=agent_id, task_type=task_type)
        typer.echo(f"Agent: {result.target_agent_id}")
        typer.echo(f"  Approvals: {result.approvals}")
        typer.echo(f"  Rejections: {result.rejections}")
        typer.echo(f"  Total reviews: {result.total_reviews}")
        typer.echo(f"  Posterior mean: {result.posterior_mean:.4f}")
        typer.echo(f"  Lower bound score: {result.lower_bound_score:.4f}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def leaderboard(
    limit: int = typer.Option(20, "--limit", "-n", help="Max number of agents"),
    task_type: Optional[str] = typer.Option(None, "--task", help="Filter by task type"),
    api_url: Optional[str] = typer.Option(None, "--api-url", help="Qxilt API base URL"),
) -> None:
    """Get top agents by reputation."""
    client = _get_client(api_url)
    result = client.get_leaderboard(limit=limit, task_type=task_type)
    if not result.items:
        typer.echo("No agents with reviews found.")
        return
    for i, item in enumerate(result.items, 1):
        typer.echo(f"{i}. {item.target_agent_id}: score={item.lower_bound_score:.4f} (n={item.total_reviews})")


if __name__ == "__main__":
    app()
