"""Cross-sample convergence and explicit method-comparison evidence."""

from collections.abc import Sequence
from math import isclose
from pathlib import Path
from typing import Literal, TypeAlias

from polars import (
    DataFrame,
    Float64,
    Int64,
    String,
    concat,
    lit,
    read_csv,
    read_json,
    read_parquet,
)

from src.services.dataset_manifest import (
    ACCEPTED_BASE_VOLTAGE,
    SAMPLE_SIZES,
)

EvidenceSource: TypeAlias = DataFrame | Path | str
AnalysisMode: TypeAlias = Literal[
    "descriptive",
    "exploratory",
    "inferential",
]

_GROUP_COLUMNS = ("scenario", "terminal", "phase")
_COMPATIBILITY_COLUMNS = (
    "base_voltage",
    "event_definition",
    "comparison_operator",
    "threshold",
    "grouping_policy",
    "method_policy",
)
_METRIC_COLUMNS = (
    "mean",
    "sample_standard_deviation",
    "median",
    "percentile_90",
    "percentile_95",
    "percentile_99",
    "empirical_probability",
    "confidence_interval_width",
    "candidate_count",
    "candidate_rate",
)
_INPUT_COLUMNS = (
    *_GROUP_COLUMNS,
    "sample_size",
    *_COMPATIBILITY_COLUMNS,
    "relationship_status",
    "mean",
    "sample_standard_deviation",
    "median",
    "percentile_90",
    "percentile_95",
    "percentile_99",
    "empirical_probability",
    "confidence_interval_lower",
    "confidence_interval_upper",
    "fitted_model_status",
    "candidate_count",
    "candidate_rate",
)
_METHOD_COLUMNS = (
    "scenario",
    "sample_size",
    "source_lineage",
    "simulation",
    "terminal",
    "terminal_position_km",
    "phase",
    "event_definition",
    "sigma_flag",
    "sigma_applicability",
    "sigma_reason",
    "mad_flag",
    "mad_applicability",
    "mad_reason",
    "flag",
    "applicability",
    "reason",
    "dbscan_flag",
    "dbscan_applicability",
    "dbscan_reason",
    "method_agreement",
    "applicable_method_count",
    "method_disagreement",
    "anomaly_candidate",
    "anomaly_reasons",
)
_INDEPENDENCE_LIMITATION = (
    "Dataset independence is not established; comparisons describe "
    "sampling consistency only."
)
_REFERENCE_LIMITATION = "High-sample empirical reference; not ground truth."

_BASE_SCHEMA = {
    "scenario": String,
    "sample_size": Int64,
    "base_voltage": Float64,
    "terminal": String,
    "phase": String,
    "event_definition": String,
    "comparison_operator": String,
    "threshold": Float64,
    "grouping_policy": String,
    "method_policy": String,
    "relationship_status": String,
    "mean": Float64,
    "sample_standard_deviation": Float64,
    "median": Float64,
    "percentile_90": Float64,
    "percentile_95": Float64,
    "percentile_99": Float64,
    "empirical_probability": Float64,
    "confidence_interval_lower": Float64,
    "confidence_interval_upper": Float64,
    "fitted_model_status": String,
    "candidate_count": Int64,
    "candidate_rate": Float64,
    "confidence_interval_width": Float64,
    "coverage_status": String,
    "comparison_status": String,
    "coverage_reason": String,
    "previous_sample_size": Int64,
    "reference_role": String,
    "reference_limitation": String,
    "independence_limitation": String,
}
_DELTA_SCHEMA = {
    name: Float64
    for metric in _METRIC_COLUMNS
    for name in (
        f"previous_{metric}",
        f"{metric}_absolute_delta",
        f"{metric}_relative_delta",
    )
}
_DELTA_REASON_SCHEMA = {
    f"{metric}_relative_delta_reason": String for metric in _METRIC_COLUMNS
}
_OUTPUT_SCHEMA = {
    **_BASE_SCHEMA,
    **_DELTA_SCHEMA,
    **_DELTA_REASON_SCHEMA,
}


def build_convergence_table(
    evidence: EvidenceSource | Sequence[EvidenceSource],
) -> DataFrame:
    """Build compatible five-size convergence evidence.

    Inputs may be assembled DataFrames or saved CSV, JSON, or Parquet tables.
    Each scenario-terminal-phase series must use one accepted base, event,
    threshold, grouping policy, and method policy. Missing canonical sizes are
    materialized rather than silently omitted.

    Returns:
        One ordered row per required size and compatible scope, including
        confidence width, consecutive deltas, coverage, and limitations.

    Raises:
        ValueError: If evidence is missing, duplicated, or incompatible.
    """
    table = _load_tables(evidence)
    _require_columns(table, _INPUT_COLUMNS, "convergence")
    if table.is_empty():
        return DataFrame(schema=_OUTPUT_SCHEMA)
    _validate_sample_sizes(table)

    output_rows: list[dict[str, object]] = []
    groups = table.partition_by(list(_GROUP_COLUMNS), maintain_order=True)
    for group in groups:
        _validate_compatibility(group)
        output_rows.extend(_build_group_rows(group))

    return DataFrame(
        output_rows,
        schema=_OUTPUT_SCHEMA,
        strict=False,
    ).sort(*_GROUP_COLUMNS, "sample_size")


def build_method_comparison_matrix(
    evidence: EvidenceSource | Sequence[EvidenceSource],
    *,
    analysis_mode: AnalysisMode = "descriptive",
    multiplicity_qualification: str = (
        "No inferential multiplicity claim is made."
    ),
) -> DataFrame:
    """Preserve row identity and every explicit method status and reason.

    Returns:
        Input evidence with declared analysis mode, multiplicity statement,
        and stable method identities.

    Raises:
        ValueError: If required method evidence or inferential qualification
            is absent.
    """
    table = _load_tables(evidence)
    _require_columns(table, _METHOD_COLUMNS, "method comparison")
    valid_modes = {"descriptive", "exploratory", "inferential"}
    if analysis_mode not in valid_modes:
        raise ValueError(
            "analysis_mode must be descriptive, exploratory, or inferential."
        )
    if analysis_mode == "inferential" and not multiplicity_qualification:
        raise ValueError(
            "Inferential analysis requires a multiplicity qualification."
        )
    if not multiplicity_qualification:
        raise ValueError("multiplicity_qualification must not be empty.")

    return table.with_columns(
        lit(analysis_mode, dtype=String).alias("analysis_mode"),
        lit(multiplicity_qualification, dtype=String).alias(
            "multiplicity_qualification"
        ),
        lit(
            "sigma_3;mad_modified_z;kmeans_distance;dbscan_noise",
            dtype=String,
        ).alias("compared_methods"),
    )


def _load_tables(
    evidence: EvidenceSource | Sequence[EvidenceSource],
) -> DataFrame:
    """Load one or more machine-readable evidence tables."""
    if isinstance(evidence, (DataFrame, Path, str)):
        sources = [evidence]
    else:
        sources = list(evidence)
    if not sources:
        raise ValueError("At least one evidence table is required.")
    tables = [_load_table(source) for source in sources]
    return tables[0] if len(tables) == 1 else concat(tables, how="diagonal")


def _load_table(source: EvidenceSource) -> DataFrame:
    """Load one DataFrame or supported saved evidence table."""
    if isinstance(source, DataFrame):
        return source
    path = Path(source)
    if path.suffix == ".csv":
        return read_csv(path)
    if path.suffix in {".json", ".jsonl", ".ndjson"}:
        return read_json(path)
    if path.suffix == ".parquet":
        return read_parquet(path)
    raise ValueError(
        f"Unsupported evidence table format: {path.suffix or '<none>'}."
    )


def _require_columns(
    table: DataFrame,
    required: Sequence[str],
    label: str,
) -> None:
    """Reject incomplete evidence contracts with exact missing fields."""
    missing = [column for column in required if column not in table]
    if missing:
        raise ValueError(f"Missing {label} columns: {', '.join(missing)}.")


def _validate_sample_sizes(table: DataFrame) -> None:
    """Reject sample sizes outside declared comparison scope."""
    observed = set(table["sample_size"].to_list())
    unexpected = sorted(observed - set(SAMPLE_SIZES))
    if unexpected:
        values = ", ".join(str(value) for value in unexpected)
        raise ValueError(f"Unsupported sample sizes: {values}.")


def _validate_compatibility(group: DataFrame) -> None:
    """Require frozen policy values within one electrical scope."""
    if group["sample_size"].n_unique() != group.height:
        raise ValueError(
            "Duplicate sample size within scenario, terminal, and phase."
        )
    bases = group["base_voltage"].drop_nulls().unique().to_list()
    if len(bases) != 1 or not isclose(
        float(bases[0]),
        ACCEPTED_BASE_VOLTAGE,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError(
            f"All rows must use accepted base voltage "
            f"{ACCEPTED_BASE_VOLTAGE:g}."
        )
    for column in _COMPATIBILITY_COLUMNS[1:]:
        if group[column].null_count() or group[column].n_unique() != 1:
            raise ValueError(
                f"Incompatible {column} within convergence scope."
            )


def _build_group_rows(group: DataFrame) -> list[dict[str, object]]:
    """Complete canonical sizes and calculate consecutive differences."""
    indexed = {
        _required_int(row["sample_size"], "sample_size"): row
        for row in group.iter_rows(named=True)
    }
    exemplar = group.row(0, named=True)
    rows: list[dict[str, object]] = []
    previous: dict[str, object] | None = None
    for sample_size in SAMPLE_SIZES:
        source = indexed.get(sample_size)
        if source is None:
            row = _missing_row(exemplar, sample_size)
        else:
            row = _observed_row(source)
        _add_deltas(row, previous)
        rows.append(row)
        previous = row
    return rows


def _observed_row(source: dict[str, object]) -> dict[str, object]:
    """Add convergence metadata to one observed source row."""
    sample_size = _required_int(source["sample_size"], "sample_size")
    lower = _optional_float(source["confidence_interval_lower"])
    upper = _optional_float(source["confidence_interval_upper"])
    width = upper - lower if lower is not None and upper is not None else None
    relationship = str(source["relationship_status"])
    return {
        **source,
        "confidence_interval_width": width,
        "coverage_status": "present",
        "comparison_status": "comparable",
        "coverage_reason": None,
        "previous_sample_size": None,
        "reference_role": (
            "high_sample_empirical_reference"
            if sample_size == 10_000
            else "comparison_sample"
        ),
        "reference_limitation": _REFERENCE_LIMITATION,
        "independence_limitation": _independence_limitation(relationship),
    }


def _missing_row(
    exemplar: dict[str, object],
    sample_size: int,
) -> dict[str, object]:
    """Materialize one explicit missing-coverage row."""
    row: dict[str, object] = {
        column: exemplar[column]
        for column in (
            *_GROUP_COLUMNS,
            *_COMPATIBILITY_COLUMNS,
            "relationship_status",
        )
    }
    for metric in (
        "mean",
        "sample_standard_deviation",
        "median",
        "percentile_90",
        "percentile_95",
        "percentile_99",
        "empirical_probability",
        "confidence_interval_lower",
        "confidence_interval_upper",
        "fitted_model_status",
        "candidate_count",
        "candidate_rate",
    ):
        row[metric] = None
    row.update({
        "sample_size": sample_size,
        "confidence_interval_width": None,
        "coverage_status": "missing",
        "comparison_status": "incomplete",
        "coverage_reason": f"Required sample size {sample_size} is missing.",
        "previous_sample_size": None,
        "reference_role": (
            "high_sample_empirical_reference"
            if sample_size == 10_000
            else "comparison_sample"
        ),
        "reference_limitation": _REFERENCE_LIMITATION,
        "independence_limitation": _independence_limitation(
            str(exemplar["relationship_status"])
        ),
    })
    return row


def _add_deltas(
    row: dict[str, object],
    previous: dict[str, object] | None,
) -> None:
    """Append safe consecutive absolute and relative metric changes."""
    comparable = (
        previous is not None
        and previous["coverage_status"] == "present"
        and row["coverage_status"] == "present"
    )
    row["previous_sample_size"] = (
        previous["sample_size"] if comparable and previous else None
    )
    for metric in _METRIC_COLUMNS:
        previous_value = (
            _optional_float(previous.get(metric))
            if comparable and previous
            else None
        )
        current_value = _optional_float(row.get(metric))
        row[f"previous_{metric}"] = previous_value
        row[f"{metric}_absolute_delta"] = None
        row[f"{metric}_relative_delta"] = None
        reason_column = f"{metric}_relative_delta_reason"
        if current_value is None or previous_value is None:
            row[reason_column] = "No consecutive comparable value."
            continue
        delta = current_value - previous_value
        row[f"{metric}_absolute_delta"] = delta
        if previous_value == 0.0:
            row[reason_column] = "Previous value is zero."
            continue
        row[f"{metric}_relative_delta"] = delta / abs(previous_value)
        row[reason_column] = None


def _independence_limitation(relationship_status: str) -> str:
    """Return explicit interpretation limit for source relationships."""
    if relationship_status == "independent":
        return "Datasets are declared independently generated."
    if relationship_status == "nested":
        return (
            "Datasets are nested; comparisons describe sampling consistency "
            "without independent-sample inference."
        )
    return _INDEPENDENCE_LIMITATION


def _optional_float(value: object) -> float | None:
    """Convert numeric table value while preserving nulls."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _required_int(value: object, field: str) -> int:
    """Return required integer evidence value."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise ValueError(f"{field} must be an integer.")
