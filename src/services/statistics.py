"""Statistical distribution fitting and probability estimation.

Fits a Gaussian (Normal) distribution to filtered overvoltage data
and computes exceedance probabilities.
"""

from typing import override

from numpy import isfinite, mean, ndarray, std
from polars import DataFrame
from scipy import stats

from src.services.schemas import StatisticalSummaryRow


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
    df: DataFrame,
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
    values: ndarray = df[value_col].to_numpy()
    mean_value, std_value = float(mean(values)), float(std(values, ddof=1))
    return GaussianFitResult(
        mean=mean_value, std=std_value, n_samples=len(values)
    )


def summarize_statistics(
    df: DataFrame,
    *,
    threshold: float,
    value_col: str = "value_pu",
) -> DataFrame:
    """Summarize exceedance statistics by terminal and phase.

    Non-finite measurements count toward ``n_total`` but are excluded from
    every estimate and from ``n_valid``. Gaussian exceedance is unavailable
    for fewer than two valid samples and for zero-variance samples.

    Returns:
        One row per terminal and phase with empirical and fitted-Gaussian
        evidence and an explicit validation status.
    """
    summary_rows: list[dict[str, str | int | float | None]] = []
    groups = df.partition_by(["terminal", "phase"], maintain_order=True)

    for group in groups:
        valid_values = [
            float(value)
            for value in group[value_col]
            if value is not None and isfinite(value)
        ]
        n_total = group.height
        n_valid = len(valid_values)
        mean_value: float | None = None
        std_value: float | None = None
        empirical_exceedance: float | None = None
        gaussian_exceedance: float | None = None

        if n_valid:
            mean_value = float(mean(valid_values))
            empirical_exceedance = (
                sum(value > threshold for value in valid_values) / n_valid
            )

        if n_valid < 2:
            validation_status = "insufficient_samples"
        else:
            std_value = float(std(valid_values, ddof=1))
            if std_value == 0.0:
                validation_status = "zero_variance"
            else:
                validation_status = "valid"
                if mean_value is not None:
                    gaussian_exceedance = float(
                        stats.norm.sf(
                            threshold, loc=mean_value, scale=std_value
                        )
                    )

        summary_rows.append({
            "terminal": str(group.item(0, "terminal")),
            "phase": str(group.item(0, "phase")),
            "n_total": n_total,
            "n_valid": n_valid,
            "mean": mean_value,
            "std": std_value,
            "empirical_exceedance": empirical_exceedance,
            "gaussian_exceedance": gaussian_exceedance,
            "validation_status": validation_status,
        })

    return StatisticalSummaryRow.validate(
        DataFrame(summary_rows, schema=StatisticalSummaryRow.dtypes)
    )
