"""Bayesian Beta-Bernoulli reputation scoring."""

from scipy import stats


def compute_reputation(
    approvals: int,
    rejections: int,
    alpha: float,
    beta: float,
    confidence: float,
) -> dict[str, float]:
    """
    Compute reputation metrics using a Beta-Bernoulli model.

    Prior: Beta(alpha, beta)
    Posterior: Beta(alpha + approvals, beta + rejections)
    Returns posterior mean, lower confidence bound, and posterior params.

    Args:
        approvals: Number of approved reviews.
        rejections: Number of rejected reviews.
        alpha: Prior alpha parameter.
        beta: Prior beta parameter.
        confidence: Confidence level for lower bound (e.g. 0.95 for 95%).

    Returns:
        Dict with keys: posterior_mean, lower_bound_score, alpha, beta
        (alpha and beta are the posterior parameters).
    """
    post_alpha = alpha + approvals
    post_beta = beta + rejections

    # Posterior mean: E[p] = alpha / (alpha + beta)
    posterior_mean = post_alpha / (post_alpha + post_beta)

    # Lower confidence bound: (1 - confidence) / 2 quantile of Beta distribution
    # e.g. for 95% confidence, use 2.5th percentile
    quantile = (1 - confidence) / 2
    lower_bound_score = float(stats.beta.ppf(quantile, post_alpha, post_beta))

    return {
        "posterior_mean": posterior_mean,
        "lower_bound_score": lower_bound_score,
        "alpha": post_alpha,
        "beta": post_beta,
    }
