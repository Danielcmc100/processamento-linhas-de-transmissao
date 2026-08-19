"""Statistical distribution fitting and probability estimation.

Fits a Gaussian (Normal) distribution to filtered overvoltage data
and computes sigma levels and exceedance probabilities.
"""

from typing import override

import numpy as np
import polars as pl
from scipy import stats

STATISTICAL_SUMMARY_SCHEMA = {
    "terminal": pl.String,
    "phase": pl.String,
    "n_total": pl.Int64,
    "n_valid": pl.Int64,
    "mean": pl.Float64,
    "std": pl.Float64,
    "sigma_3_threshold": pl.Float64,
    "empirical_exceedance": pl.Float64,
    "gaussian_exceedance": pl.Float64,
    "validation_status": pl.String,
}


class GaussianFitResult:
    """Results of fitting a Gaussian distribution to a voltage sample.

    Attributes:
        mean: Sample mean (P.U.).
        std: Sample standard deviation (P.U.).
        n_samples: Number of data points used in the fit.
    """

    def __init__(self, mean: float, std: float, n_samples: int) -> None:
        self.mean: float = mean
        self.std: float = std
        self.n_samples: int = n_samples

    def sigma_level(self, n: float) -> float:
        """Return the voltage threshold at *n* standard deviations above mean.

        Returns:
            Threshold value in P.U.
        """
        return self.mean + n * self.std

    def exceedance_probability(self, threshold: float) -> float:
        """Probability that a single event exceeds *threshold* (P.U.).

        Uses the survival function (1 - CDF) of the fitted normal.

        Returns:
            Probability in [0, 1].
        """
        return float(stats.norm.sf(threshold, loc=self.mean, scale=self.std))

    @override
    def __repr__(self) -> str:
        return (
            f"GaussianFitResult("
            f"mean={self.mean:.4f}, "
            f"std={self.std:.4f}, n={self.n_samples})"
        )


def fit_gaussian(
    df: pl.DataFrame,
    value_col: str = "value_pu",
) -> GaussianFitResult:
    """Fit a Gaussian distribution to the *value_col* column.

    Returns:
        :class:`GaussianFitResult` with mean, std and sample count.

    Raises:
        ValueError: If the DataFrame has no rows.
    """
    if df.is_empty():
        message = "Cannot fit Gaussian to an empty DataFrame."
        raise ValueError(message)
    values: np.ndarray = df[value_col].to_numpy()
    mean, std = float(np.mean(values)), float(np.std(values, ddof=1))
    return GaussianFitResult(mean=mean, std=std, n_samples=len(values))


def sigma_summary(fit: GaussianFitResult) -> pl.DataFrame:
    """Return a summary table of sigma levels (1σ to 6σ).

    Returns:
        DataFrame with columns ``sigma``, ``threshold_pu``,
        ``exceedance_prob``.
    """
    sigmas = [1, 2, 3, 4, 5, 6]
    thresholds = [fit.sigma_level(s) for s in sigmas]
    probs = [fit.exceedance_probability(t) for t in thresholds]

    return pl.DataFrame({
        "sigma": sigmas,
        "threshold_pu": thresholds,
        "exceedance_prob": probs,
    })


def summarize_statistics(
    df: pl.DataFrame,
    *,
    threshold: float,
    value_col: str = "value_pu",
) -> pl.DataFrame:
    """Summarize exceedance statistics by terminal and phase.

    Non-finite measurements count toward ``n_total`` but are excluded from
    every estimate and from ``n_valid``. Gaussian exceedance is unavailable
    for fewer than two valid samples and for zero-variance samples.

    Returns:
        One row per terminal and phase with empirical and fitted-Gaussian
        evidence, sigma threshold, and an explicit validation status.
    """
    summary_rows: list[dict[str, str | int | float | None]] = []
    groups = df.partition_by(["terminal", "phase"], maintain_order=True)

    for group in groups:
        valid_values = [
            float(value)
            for value in group[value_col]
            if value is not None and np.isfinite(value)
        ]
        n_total = group.height
        n_valid = len(valid_values)
        mean: float | None = None
        std: float | None = None
        sigma_3_threshold: float | None = None
        empirical_exceedance: float | None = None
        gaussian_exceedance: float | None = None

        if n_valid:
            mean = float(np.mean(valid_values))
            empirical_exceedance = (
                sum(value > threshold for value in valid_values) / n_valid
            )

        if n_valid < 2:
            validation_status = "insufficient_samples"
        else:
            std = float(np.std(valid_values, ddof=1))
            sigma_3_threshold = mean + 3 * std if mean is not None else None
            if std == 0.0:
                validation_status = "zero_variance"
            else:
                validation_status = "valid"
                gaussian_exceedance = float(
                    stats.norm.sf(threshold, loc=mean, scale=std)
                )

        summary_rows.append({
            "terminal": str(group.item(0, "terminal")),
            "phase": str(group.item(0, "phase")),
            "n_total": n_total,
            "n_valid": n_valid,
            "mean": mean,
            "std": std,
            "sigma_3_threshold": sigma_3_threshold,
            "empirical_exceedance": empirical_exceedance,
            "gaussian_exceedance": gaussian_exceedance,
            "validation_status": validation_status,
        })

    return pl.DataFrame(summary_rows, schema=STATISTICAL_SUMMARY_SCHEMA)
