"""Statistical distribution fitting and probability estimation.

Fits a Gaussian (Normal) distribution to filtered overvoltage data
and computes sigma levels and exceedance probabilities.
"""

from typing import override

import numpy as np
import polars as pl
from scipy import stats


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
