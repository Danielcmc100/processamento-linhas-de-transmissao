"""Controlled anomaly benchmark confusion counts and safe metrics."""

from math import isfinite

from polars import (
    Boolean,
    DataFrame,
    Float64,
    Int64,
    String,
    col,
)

_GROUP_COLUMNS = (
    "intervention_family",
    "intervention_intensity",
    "method",
)
_REQUIRED_COLUMNS = (
    *_GROUP_COLUMNS,
    "controlled_label",
    "flag",
    "applicability",
)
_SCHEMA = {
    "intervention_family": String,
    "intervention_intensity": Float64,
    "method": String,
    "row_count": Int64,
    "applicable_count": Int64,
    "excluded_count": Int64,
    "true_positive": Int64,
    "false_positive": Int64,
    "true_negative": Int64,
    "false_negative": Int64,
    "precision": Float64,
    "recall": Float64,
    "f1": Float64,
    "false_positive_rate": Float64,
    "benchmark_applicability": String,
    "benchmark_reason": String,
    "precision_applicability": String,
    "precision_reason": String,
    "recall_applicability": String,
    "recall_reason": String,
    "f1_applicability": String,
    "f1_reason": String,
    "false_positive_rate_applicability": String,
    "false_positive_rate_reason": String,
}


def summarize_controlled_benchmark(evidence: DataFrame) -> DataFrame:
    """Aggregate controlled labels and method flags into safe metrics.

    Results are grouped by intervention family, intensity, and method.
    Non-applicable method rows are excluded from confusion counts. Undefined
    metric denominators produce null values with explicit reasons.

    Returns:
        Deterministically sorted confusion counts and derived metrics.

    Raises:
        ValueError: If required columns, types, or evidence states are invalid.
    """
    _validate_evidence(evidence)
    if evidence.is_empty():
        return DataFrame(schema=_SCHEMA)

    rows: list[dict[str, object]] = []
    sorted_evidence = evidence.sort(list(_GROUP_COLUMNS))
    groups = sorted_evidence.partition_by(
        list(_GROUP_COLUMNS),
        maintain_order=True,
    )
    for group in groups:
        rows.append(_summarize_group(group))
    return DataFrame(rows, schema=_SCHEMA, strict=False)


def _summarize_group(group: DataFrame) -> dict[str, object]:
    """Summarize one intervention-family, intensity, and method group."""
    applicable = group.filter(col("applicability") == "applicable")
    pairs = applicable.select("controlled_label", "flag").iter_rows()
    pair_values = [(bool(truth), bool(flag)) for truth, flag in pairs]
    true_positive = sum(truth and flag for truth, flag in pair_values)
    false_positive = sum(not truth and flag for truth, flag in pair_values)
    true_negative = sum(not truth and not flag for truth, flag in pair_values)
    false_negative = sum(truth and not flag for truth, flag in pair_values)

    precision = _safe_metric(
        true_positive,
        true_positive + false_positive,
        "No predicted positive observations.",
    )
    recall = _safe_metric(
        true_positive,
        true_positive + false_negative,
        "No positive controlled observations.",
    )
    f1 = _safe_metric(
        2 * true_positive,
        2 * true_positive + false_positive + false_negative,
        "No true or predicted positive observations.",
    )
    false_positive_rate = _safe_metric(
        false_positive,
        false_positive + true_negative,
        "No negative controlled observations.",
    )
    metrics = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": false_positive_rate,
    }
    applicable_count = applicable.height

    row: dict[str, object] = {
        "intervention_family": str(group.item(0, "intervention_family")),
        "intervention_intensity": float(
            group.item(0, "intervention_intensity")
        ),
        "method": str(group.item(0, "method")),
        "row_count": group.height,
        "applicable_count": applicable_count,
        "excluded_count": group.height - applicable_count,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "false_negative": false_negative,
        **{name: value for name, (value, _) in metrics.items()},
        "benchmark_applicability": (
            "applicable" if applicable_count else "non_applicable"
        ),
        "benchmark_reason": (
            None if applicable_count else "No applicable method results."
        ),
    }
    for name, (value, reason) in metrics.items():
        row[f"{name}_applicability"] = (
            "applicable" if value is not None else "non_applicable"
        )
        row[f"{name}_reason"] = reason
    return row


def _safe_metric(
    numerator: int,
    denominator: int,
    undefined_reason: str,
) -> tuple[float | None, str | None]:
    """Return ratio and explicit reason when denominator is zero."""
    if denominator == 0:
        return None, undefined_reason
    return numerator / denominator, None


def _validate_evidence(evidence: DataFrame) -> None:
    """Validate benchmark schema and applicable evidence states."""
    for column in _REQUIRED_COLUMNS:
        if column not in evidence.columns:
            raise ValueError(
                f"Required benchmark column is missing: {column}."
            )

    for column in ("intervention_family", "method", "applicability"):
        if evidence.schema[column] != String:
            raise ValueError(f"{column} must be String.")
        if evidence[column].null_count():
            raise ValueError(f"{column} must not contain null values.")
    if not evidence.schema["intervention_intensity"].is_numeric():
        raise ValueError("intervention_intensity must be numeric.")
    intensities = evidence["intervention_intensity"].to_list()
    if any(
        value is None or not isfinite(float(value)) for value in intensities
    ):
        message = "intervention_intensity must contain finite values."
        raise ValueError(message)
    for column in ("controlled_label", "flag"):
        if evidence.schema[column] != Boolean:
            raise ValueError(f"{column} must be Boolean.")
    if evidence["controlled_label"].null_count():
        raise ValueError("controlled_label must not contain null values.")

    statuses = set(evidence["applicability"].to_list())
    if not statuses.issubset({"applicable", "non_applicable"}):
        message = (
            "applicability must contain only applicable or non_applicable."
        )
        raise ValueError(message)
    if not evidence.filter(
        (col("applicability") == "applicable") & col("flag").is_null()
    ).is_empty():
        message = "flag must be Boolean when applicability is applicable."
        raise ValueError(message)
    if not evidence.filter(
        (col("applicability") == "non_applicable")
        & col("flag").fill_null(False)
    ).is_empty():
        message = "flag must not be true when applicability is non_applicable."
        raise ValueError(message)
