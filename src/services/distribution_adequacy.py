"""Gaussian distribution adequacy and robust MAD evidence."""

from collections.abc import Callable, Sequence
from math import isfinite
from typing import Protocol, TypeAlias, TypeGuard, cast

from numpy import median
from polars import Boolean, DataFrame, Float64, Int64, Series, String
from scipy.stats import anderson, kurtosis, norm, probplot, skew

from src.services.statistics import fit_gaussian

EvidenceValue: TypeAlias = str | int | float | None


class _AndersonPValueResult(Protocol):
    """Typed subset returned by SciPy's p-value Anderson API."""

    statistic: float
    pvalue: float


_SCOPE_COLUMNS = ("scenario", "sample_size", "terminal", "phase")
_MINIMUM_SAMPLE_SIZE = 8
_SIGNIFICANCE_LEVEL = 0.05
_MAD_THRESHOLD = 3.5
_MAD_SCALE = 0.6744897501960817

_ADEQUACY_SCHEMA = {
    "scenario": String,
    "sample_size": Int64,
    "terminal": String,
    "phase": String,
    "count": Int64,
    "valid_count": Int64,
    "excluded_count": Int64,
    "fitted_mean": Float64,
    "fitted_standard_deviation": Float64,
    "fitting_policy": String,
    "comparison_operator": String,
    "threshold": Float64,
    "empirical_exceedance": Float64,
    "gaussian_exceedance": Float64,
    "absolute_tail_difference": Float64,
    "relative_tail_difference": Float64,
    "anderson_statistic": Float64,
    "anderson_p_value": Float64,
    "significance_level": Float64,
    "reference_method": String,
    "skewness": Float64,
    "excess_kurtosis": Float64,
    "qq_correlation": Float64,
    "decision": String,
    "applicability": String,
    "gaussian_inference_status": String,
    "limitations": String,
    "reason": String,
}


def evaluate_distribution_adequacy(
    observations: DataFrame,
    *,
    threshold: float,
    value_col: str = "value_pu",
) -> DataFrame:
    """Evaluate fitted-Gaussian adequacy within comparable groups.

    Finite observations are fitted with sample mean and sample standard
    deviation. Anderson-Darling uses SciPy's interpolated normal-reference
    p-value and a predeclared 5% significance level. Groups with fewer than
    eight finite values or zero variance remain valid for empirical boundary
    evidence but are non-applicable for adequacy inference.

    Returns:
        One adequacy and tail-comparison row per scenario, sample size,
        terminal, and phase.

    Raises:
        ValueError: If threshold is non-finite or required columns are absent.
    """
    if not isfinite(threshold):
        message = "threshold must be finite."
        raise ValueError(message)
    _require_columns(observations, value_col)

    if observations.is_empty():
        return DataFrame(schema=_ADEQUACY_SCHEMA)

    rows: list[dict[str, EvidenceValue]] = []
    groups = observations.partition_by(
        list(_SCOPE_COLUMNS), maintain_order=True
    )
    for group in groups:
        values = _valid_values(group[value_col].to_list())
        rows.append(_evaluate_group(group, values, threshold, value_col))

    return DataFrame(rows, schema=_ADEQUACY_SCHEMA, strict=False)


def evaluate_mad_evidence(
    observations: DataFrame,
    *,
    value_col: str = "value_pu",
    threshold: float = _MAD_THRESHOLD,
) -> DataFrame:
    """Append group-local modified MAD scores and explicit flags.

    The score is ``0.6744897501960817 * (value - median) / MAD`` and a
    candidate requires ``abs(score) > threshold``. Groups with fewer than
    eight finite observations or zero MAD are non-applicable and never flag.

    Returns:
        Input observations with robust score, threshold, flag,
        applicability, group median, MAD, and reason columns.

    Raises:
        ValueError: If threshold is invalid or required columns are absent.
    """
    if not isfinite(threshold) or threshold <= 0.0:
        message = "threshold must be finite and greater than zero."
        raise ValueError(message)
    _require_columns(observations, value_col)

    row_count = observations.height
    scores: list[float | None] = [None] * row_count
    flags = [False] * row_count
    medians: list[float | None] = [None] * row_count
    deviations: list[float | None] = [None] * row_count
    applicability = ["non_applicable"] * row_count
    reasons: list[str | None] = [None] * row_count

    indexed = observations.with_row_index("_row_index")
    groups = indexed.partition_by(list(_SCOPE_COLUMNS), maintain_order=True)
    for group in groups:
        _score_mad_group(
            group,
            value_col=value_col,
            threshold=threshold,
            scores=scores,
            flags=flags,
            medians=medians,
            deviations=deviations,
            applicability=applicability,
            reasons=reasons,
        )

    return observations.with_columns(
        Series("mad_median", medians, dtype=Float64),
        Series("median_absolute_deviation", deviations, dtype=Float64),
        Series("modified_mad_score", scores, dtype=Float64),
        Series("mad_threshold", [threshold] * row_count, dtype=Float64),
        Series("mad_flag", flags, dtype=Boolean),
        Series("mad_applicability", applicability, dtype=String),
        Series("mad_reason", reasons, dtype=String),
    )


def _evaluate_group(
    group: DataFrame,
    values: list[float],
    threshold: float,
    value_col: str,
) -> dict[str, EvidenceValue]:
    """Build one group-level adequacy record."""
    valid_count = len(values)
    empirical = (
        sum(value > threshold for value in values) / valid_count
        if valid_count
        else None
    )
    row: dict[str, EvidenceValue] = {
        **{
            column: _scope_value(group.item(0, column))
            for column in _SCOPE_COLUMNS
        },
        "count": group.height,
        "valid_count": valid_count,
        "excluded_count": group.height - valid_count,
        "fitted_mean": None,
        "fitted_standard_deviation": None,
        "fitting_policy": "sample_mean_sample_std_ddof_1",
        "comparison_operator": ">",
        "threshold": threshold,
        "empirical_exceedance": empirical,
        "gaussian_exceedance": None,
        "absolute_tail_difference": None,
        "relative_tail_difference": None,
        "anderson_statistic": None,
        "anderson_p_value": None,
        "significance_level": _SIGNIFICANCE_LEVEL,
        "reference_method": "scipy_anderson_interpolate",
        "skewness": None,
        "excess_kurtosis": None,
        "qq_correlation": None,
        "decision": "undersized",
        "applicability": "non_applicable",
        "gaussian_inference_status": "descriptive_only",
        "limitations": (
            "Interpolated p-values are bounded by SciPy reference tables; "
            "formal tests are sensitive at large sample sizes."
        ),
        "reason": (
            f"At least {_MINIMUM_SAMPLE_SIZE} finite observations are "
            "required."
        ),
    }
    if valid_count < 2:
        return row

    fit = fit_gaussian(DataFrame({value_col: values}), value_col=value_col)
    row["fitted_mean"] = fit.mean
    row["fitted_standard_deviation"] = fit.std
    if fit.std == 0.0:
        row["decision"] = "degenerate"
        row["gaussian_inference_status"] = "unavailable"
        row["reason"] = "Gaussian adequacy is undefined for zero variance."
        return row

    gaussian = fit.exceedance_probability(threshold)
    row["gaussian_exceedance"] = gaussian
    if empirical is not None:
        absolute_difference = abs(empirical - gaussian)
        row["absolute_tail_difference"] = absolute_difference
        if empirical > 0.0:
            row["relative_tail_difference"] = (
                absolute_difference / empirical
            )

    row["skewness"] = float(skew(values, bias=False))
    row["excess_kurtosis"] = float(
        kurtosis(values, fisher=True, bias=False)
    )
    probability_plot = probplot(values, dist=norm, fit=True)
    row["qq_correlation"] = float(probability_plot[1][2])

    if valid_count < _MINIMUM_SAMPLE_SIZE:
        return row

    anderson_with_p_value = cast(
        Callable[..., _AndersonPValueResult], anderson
    )
    result = anderson_with_p_value(
        values, dist="norm", method="interpolate"
    )
    statistic = float(result.statistic)
    p_value = float(result.pvalue)
    row["anderson_statistic"] = statistic
    row["anderson_p_value"] = p_value
    row["applicability"] = "applicable"
    if p_value < _SIGNIFICANCE_LEVEL:
        row["decision"] = "rejected"
        row["gaussian_inference_status"] = "descriptive_only"
        row["reason"] = "Anderson-Darling rejects normality at 5%."
    else:
        row["decision"] = "not_rejected"
        row["gaussian_inference_status"] = "qualified"
        row["reason"] = "Anderson-Darling does not reject normality at 5%."
    return row


def _score_mad_group(
    group: DataFrame,
    *,
    value_col: str,
    threshold: float,
    scores: list[float | None],
    flags: list[bool],
    medians: list[float | None],
    deviations: list[float | None],
    applicability: list[str],
    reasons: list[str | None],
) -> None:
    """Populate row-aligned MAD evidence for one comparable group."""
    valid_rows = [
        (int(index), float(value))
        for index, value in zip(
            group["_row_index"].to_list(),
            group[value_col].to_list(),
            strict=True,
        )
        if _is_finite_number(value)
    ]
    group_indices = [int(index) for index in group["_row_index"]]
    if len(valid_rows) < _MINIMUM_SAMPLE_SIZE:
        reason = (
            f"At least {_MINIMUM_SAMPLE_SIZE} finite observations are "
            "required."
        )
        for index in group_indices:
            reasons[index] = reason
        return

    values = [value for _, value in valid_rows]
    median_value = float(median(values))
    mad = float(median([abs(value - median_value) for value in values]))
    for index in group_indices:
        medians[index] = median_value
        deviations[index] = mad
    if mad == 0.0:
        for index in group_indices:
            reasons[index] = "Median absolute deviation is zero."
        return

    valid_indices = {index for index, _ in valid_rows}
    for index, value in valid_rows:
        score = _MAD_SCALE * (value - median_value) / mad
        scores[index] = score
        flags[index] = abs(score) > threshold
        applicability[index] = "applicable"
    for index in group_indices:
        if index not in valid_indices:
            reasons[index] = "Observation is null or non-finite."


def _valid_values(values: Sequence[object]) -> list[float]:
    """Return finite numeric values."""
    return [float(value) for value in values if _is_finite_number(value)]


def _is_finite_number(value: object) -> TypeGuard[int | float]:
    """Return whether value is a finite non-Boolean number."""
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and isfinite(float(value))
    )


def _require_columns(observations: DataFrame, value_col: str) -> None:
    """Reject observations missing scope or value columns."""
    required = (*_SCOPE_COLUMNS, value_col)
    missing = [column for column in required if column not in observations]
    if missing:
        message = f"Missing required columns: {', '.join(missing)}."
        raise ValueError(message)


def _scope_value(value: object) -> str | int:
    """Normalize a scope scalar for evidence serialization."""
    if isinstance(value, int):
        return value
    return str(value)
