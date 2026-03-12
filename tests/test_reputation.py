"""Unit tests for Bayesian reputation scoring."""

import pytest

from qxilt.scoring.reputation import compute_reputation


def test_prior_only_zero_reviews() -> None:
    """With no reviews, posterior equals prior; mean is 0.5 for symmetric prior."""
    result = compute_reputation(
        approvals=0,
        rejections=0,
        alpha=5.0,
        beta=5.0,
        confidence=0.95,
    )
    assert result["posterior_mean"] == 0.5
    assert result["alpha"] == 5.0
    assert result["beta"] == 5.0
    # Lower bound for symmetric prior should be < 0.5
    assert 0 < result["lower_bound_score"] < 0.5


def test_posterior_mean_after_approvals() -> None:
    """Posterior mean increases with approvals."""
    result = compute_reputation(
        approvals=10,
        rejections=0,
        alpha=5.0,
        beta=5.0,
        confidence=0.95,
    )
    # (5+10)/(5+10+5+0) = 15/20 = 0.75
    assert result["posterior_mean"] == 0.75
    assert result["alpha"] == 15.0
    assert result["beta"] == 5.0
    assert result["lower_bound_score"] > 0.5
    assert result["lower_bound_score"] < 0.75


def test_posterior_mean_after_rejections() -> None:
    """Posterior mean decreases with rejections."""
    result = compute_reputation(
        approvals=0,
        rejections=10,
        alpha=5.0,
        beta=5.0,
        confidence=0.95,
    )
    # (5+0)/(5+0+5+10) = 5/20 = 0.25
    assert result["posterior_mean"] == 0.25
    assert result["alpha"] == 5.0
    assert result["beta"] == 15.0
    assert result["lower_bound_score"] < 0.25
    assert result["lower_bound_score"] > 0


def test_lower_bound_decreases_with_confidence() -> None:
    """Higher confidence level yields wider interval, so lower bound is further from mean."""
    r_low = compute_reputation(approvals=10, rejections=5, alpha=5.0, beta=5.0, confidence=0.90)
    r_high = compute_reputation(approvals=10, rejections=5, alpha=5.0, beta=5.0, confidence=0.99)
    # 99% confidence: wider interval -> lower bound is smaller
    assert r_high["lower_bound_score"] < r_low["lower_bound_score"]
    assert r_high["lower_bound_score"] < r_low["posterior_mean"]


def test_mixed_reviews() -> None:
    """Mixed approvals and rejections."""
    result = compute_reputation(
        approvals=8,
        rejections=2,
        alpha=5.0,
        beta=5.0,
        confidence=0.95,
    )
    # (5+8)/(5+8+5+2) = 13/20 = 0.65
    assert result["posterior_mean"] == 0.65
    assert result["alpha"] == 13.0
    assert result["beta"] == 7.0
