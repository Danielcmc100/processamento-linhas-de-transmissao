"""Auditable descriptive and empirical probability evidence."""

from collections.abc import Sequence
from math import isfinite
from typing import TypeAlias

from numpy import mean, median, percentile, std
from polars import DataFrame, Float64, Int64, String
from scipy.stats import binomtest

ScopeValue: TypeAlias = str | int
EvidenceValue: TypeAlias = str | int | float | None

_SCOPE_COLUMNS = ("scenario", "sample_size", "terminal", "phase")
_CONFIDENCE_LEVEL = 0.95

_EVIDENCE_SCHEMA = {
    "scenario": String,
    "sample_size": Int64,
    "terminal": String,
    "phase": String,
    "unit": String,
    "event_definition": String,
    "comparison_operator": String,
    "threshold": Float64,
    "count": Int64,
    "valid_count": Int64,
    "excluded_count": Int64,
    "mean": Float64,
    "sample_standard_deviation": Float64,
    "median": Float64,
    "quartile_1": Float64,
    "quartile_3": Float64,
    "percentile_90": Float64,
    "percentile_95": Float64,
    "percentile_99": Float64,
    "minimum": Float64,
    "maximum": Float64,
    "occurrence_count": Int64,
    "denominator": Int64,
    "empirical_probability": Float64,
    "empirical_percentage": Float64,
    "confidence_level": Float64,
    "confidence_interval_method": String,
    "confidence_interval_lower": Float64,
    "confidence_interval_upper": Float64,
    "confidence_interval_applicability": String,
    "calculation_source": String,
    "exclusions": String,
    "descriptive_applicability": String,
    "probability_applicability": String,
    "validation_status": String,
    "reason": String,
}


def summarize_statistical_evidence(
    observations: DataFrame,
    *,
    threshold: float,
    value_col: str = "value_pu",
    unit: str = "p.u.",
) -> DataFrame:
    """Summarize descriptives and strict empirical exceedance by scope.

    Null and non-finite measurements remain in ``count`` and are excluded
    from ``valid_count`` and every calculation. Empirical evidence uses the
    strict event ``value > threshold``. Its two-sided 95% Wilson interval is
    calculated by SciPy from the occurrence count and valid denominator.

    Returns:
        One evidence row per scenario, sample size, terminal, and phase.

    Raises:
        ValueError: If threshold is non-finite or required columns are absent.
    """
    if not isfinite(threshold):
        message = "threshold must be finite."
        raise ValueError(message)

    required_columns = (*_SCOPE_COLUMNS, value_col)
    missing_columns = [
        column
        for column in required_columns
        if column not in observations.columns
    ]
    if missing_columns:
        joined_columns = ", ".join(missing_columns)
        message = f"Missing required columns: {joined_columns}."
        raise ValueError(message)

    if observations.is_empty():
        return DataFrame(schema=_EVIDENCE_SCHEMA)

    rows: list[dict[str, EvidenceValue]] = []
    groups = observations.partition_by(
        list(_SCOPE_COLUMNS), maintain_order=True
    )
    for group in groups:
        values = _valid_values(group[value_col].to_list())
        rows.append(
            _summarize_group(
                group,
                values,
                threshold=threshold,
                value_col=value_col,
                unit=unit,
            )
        )

    return DataFrame(rows, schema=_EVIDENCE_SCHEMA, strict=False)


def _valid_values(values: Sequence[object]) -> list[float]:
    """Return finite numeric values from one observation group."""
    valid_values: list[float] = []
    for value in values:
        if value is None or isinstance(value, bool):
            continue
        if not isinstance(value, (int, float)):
            continue
        numeric_value = float(value)
        if isfinite(numeric_value):
            valid_values.append(numeric_value)
    return valid_values


def _summarize_group(
    group: DataFrame,
    values: list[float],
    *,
    threshold: float,
    value_col: str,
    unit: str,
) -> dict[str, EvidenceValue]:
    """Build one complete evidence row."""
    count = group.height
    valid_count = len(values)
    excluded_count = count - valid_count
    scope = {
        column: _scope_value(group.item(0, column))
        for column in _SCOPE_COLUMNS
    }
    row: dict[str, EvidenceValue] = {
        **scope,
        "unit": unit,
        "event_definition": (f"{value_col} > {threshold:g} {unit}"),
        "comparison_operator": ">",
        "threshold": threshold,
        "count": count,
        "valid_count": valid_count,
        "excluded_count": excluded_count,
        "calculation_source": "direct_observation_count",
        "exclusions": _exclusion_summary(excluded_count),
    }

    if not values:
        row.update(_empty_statistics())
        row.update({
            "occurrence_count": 0,
            "denominator": 0,
            "empirical_probability": None,
            "empirical_percentage": None,
            "confidence_level": _CONFIDENCE_LEVEL,
            "confidence_interval_method": "wilson",
            "confidence_interval_lower": None,
            "confidence_interval_upper": None,
            "confidence_interval_applicability": "non_applicable",
            "descriptive_applicability": "non_applicable",
            "probability_applicability": "non_applicable",
            "validation_status": "invalid",
            "reason": "No valid observations.",
        })
        return row

    row.update(_descriptive_statistics(values))
    occurrence_count = sum(value > threshold for value in values)
    probability = occurrence_count / valid_count
    confidence_interval = binomtest(
        occurrence_count, valid_count
    ).proportion_ci(
        confidence_level=_CONFIDENCE_LEVEL,
        method="wilson",
    )
    reason: str | None = None
    descriptive_applicability = "applicable"
    validation_status = "valid"
    if valid_count == 1:
        reason = (
            "Sample standard deviation requires at least two valid "
            "observations."
        )
        descriptive_applicability = "qualified"
        validation_status = "qualified"
    elif excluded_count:
        validation_status = "qualified"

    row.update({
        "occurrence_count": occurrence_count,
        "denominator": valid_count,
        "empirical_probability": probability,
        "empirical_percentage": probability * 100.0,
        "confidence_level": _CONFIDENCE_LEVEL,
        "confidence_interval_method": "wilson",
        "confidence_interval_lower": float(confidence_interval.low),
        "confidence_interval_upper": float(confidence_interval.high),
        "confidence_interval_applicability": "applicable",
        "descriptive_applicability": descriptive_applicability,
        "probability_applicability": "applicable",
        "validation_status": validation_status,
        "reason": reason,
    })
    return row


def _descriptive_statistics(
    values: list[float],
) -> dict[str, float | None]:
    """Calculate requested descriptive values for finite observations."""
    standard_deviation = (
        float(std(values, ddof=1)) if len(values) >= 2 else None
    )
    return {
        "mean": float(mean(values)),
        "sample_standard_deviation": standard_deviation,
        "median": float(median(values)),
        "quartile_1": float(percentile(values, 25)),
        "quartile_3": float(percentile(values, 75)),
        "percentile_90": float(percentile(values, 90)),
        "percentile_95": float(percentile(values, 95)),
        "percentile_99": float(percentile(values, 99)),
        "minimum": min(values),
        "maximum": max(values),
    }


def _empty_statistics() -> dict[str, None]:
    """Return nullable descriptive fields for an empty valid sample."""
    return {
        "mean": None,
        "sample_standard_deviation": None,
        "median": None,
        "quartile_1": None,
        "quartile_3": None,
        "percentile_90": None,
        "percentile_95": None,
        "percentile_99": None,
        "minimum": None,
        "maximum": None,
    }


def _scope_value(value: object) -> ScopeValue:
    """Normalize Polars scalar scope values for typed row construction."""
    if isinstance(value, int):
        return value
    return str(value)


def _exclusion_summary(excluded_count: int) -> str:
    """Describe exclusions without hiding a changed denominator."""
    if excluded_count == 0:
        return "none"
    return f"{excluded_count} null or non-finite observation(s)"
