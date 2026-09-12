"""Structured data-quality validation for normalized observations."""

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from pathlib import Path
from re import search
from typing import Any

from polars import DataFrame, String, col

REQUIRED_COLUMNS = (
    "source_file",
    "simulation",
    "terminal",
    "phase",
    "value_pu",
    "time",
)


class ValidationStatus(StrEnum):
    """Overall outcome of observation validation."""

    VALID = "valid"
    VALID_WITH_ISSUES = "valid_with_issues"
    EMPTY_DATASET = "empty_dataset"
    EMPTY_SELECTION = "empty_selection"
    INVALID_INPUT = "invalid_input"


class ValidationIssueCode(StrEnum):
    """Machine-readable reason for a validation issue."""

    EMPTY_DATASET = "empty_dataset"
    MISSING_COLUMN = "missing_column"
    INVALID_COLUMN_TYPE = "invalid_column_type"
    INVALID_IDENTITY = "invalid_identity"
    NON_FINITE_VALUE = "non_finite_value"
    NON_FINITE_TIME = "non_finite_time"
    MISSING_TERMINAL = "missing_terminal"
    MISSING_PHASE = "missing_phase"
    DUPLICATE_KEY = "duplicate_key"
    INCOMPLETE_MATRIX = "incomplete_matrix"
    OUT_OF_RANGE_TIME = "out_of_range_time"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One structured observation validation issue."""

    code: ValidationIssueCode
    message: str
    field: str | None = None
    row_index: int | None = None
    source_file: str | None = None
    simulation: int | None = None
    terminal: str | None = None
    phase: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Validation status, issues, and rows safe for analysis."""

    status: ValidationStatus
    issues: tuple[ValidationIssue, ...]
    cleaned: DataFrame

    @property
    def is_valid(self) -> bool:
        """Return whether the cleaned table may feed analysis services."""
        return self.status in {
            ValidationStatus.VALID,
            ValidationStatus.VALID_WITH_ISSUES,
        }


def validate_observations(
    observations: DataFrame,
    *,
    terminals: tuple[str, ...],
    phases: tuple[str, ...],
    expected_runs: dict[str, int] | None = None,
    time_bounds: dict[str, tuple[float, float]] | None = None,
) -> ValidationResult:
    """Validate and select normalized ATP observations.

    Non-finite and out-of-window measurement rows are reported and excluded.
    Optional source declarations define completeness before cleaning.
    Duplicate keys block analysis rather than silently selecting a copy.
    Schema and
    identity inconsistencies make the result invalid, while missing configured
    terminals or phases produce an explicit empty-selection result.

    Returns:
        Structured validation metadata and the rows safe for analysis.
    """
    schema_issues = _validate_schema(observations)
    if schema_issues:
        return ValidationResult(
            status=ValidationStatus.INVALID_INPUT,
            issues=tuple(schema_issues),
            cleaned=observations.clear(),
        )

    if observations.is_empty():
        issue = ValidationIssue(
            code=ValidationIssueCode.EMPTY_DATASET,
            message="The observation dataset is empty.",
        )
        return ValidationResult(
            status=ValidationStatus.EMPTY_DATASET,
            issues=(issue,),
            cleaned=observations.clone(),
        )

    issues: list[ValidationIssue] = []
    invalid_rows: set[int] = set()
    seen: set[tuple[object, ...]] = set()
    for row_index, row in enumerate(observations.to_dicts()):
        row_issues = _validate_row(row, row_index)
        key = tuple(row[field] for field in REQUIRED_COLUMNS[:4])
        if key in seen:
            row_issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.DUPLICATE_KEY,
                    message="Repeated source-run-terminal-phase key.",
                    **_issue_context(row, row_index),
                )
            )
        seen.add(key)
        bounds = (time_bounds or {}).get(row["source_file"])
        time = row["time"]
        if bounds and time is not None and isfinite(time):
            if not bounds[0] <= time <= bounds[1]:
                row_issues.append(
                    ValidationIssue(
                        code=ValidationIssueCode.OUT_OF_RANGE_TIME,
                        message=f"Maximum time outside {bounds} seconds.",
                        field="time",
                        **_issue_context(row, row_index),
                    )
                )
        if row_issues:
            invalid_rows.add(row_index)
            issues.extend(row_issues)

    cleaned = observations.with_row_index("_validation_row")
    if invalid_rows:
        cleaned = cleaned.filter(
            ~col("_validation_row").is_in(sorted(invalid_rows))
        )
    cleaned = cleaned.drop("_validation_row")

    if expected_runs is not None:
        selected_keys = {
            key for key in seen if key[2] in terminals and key[3] in phases
        }
        expected_keys = {
            (source, run, terminal, phase)
            for source, count in expected_runs.items()
            for run in range(1, count + 1)
            for terminal in terminals
            for phase in phases
        }
        if selected_keys != expected_keys:
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.INCOMPLETE_MATRIX,
                    message=(
                        f"Missing {len(expected_keys - selected_keys)} keys; "
                        f"extra {len(selected_keys - expected_keys)} keys."
                    ),
                )
            )

    identity_issue = any(
        issue.code
        in {
            ValidationIssueCode.INVALID_IDENTITY,
            ValidationIssueCode.DUPLICATE_KEY,
            ValidationIssueCode.INCOMPLETE_MATRIX,
        }
        for issue in issues
    )
    if identity_issue:
        return ValidationResult(
            status=ValidationStatus.INVALID_INPUT,
            issues=tuple(issues),
            cleaned=cleaned,
        )

    selection_issues = _validate_selection(
        observations,
        terminals=terminals,
        phases=phases,
    )
    if selection_issues:
        return ValidationResult(
            status=ValidationStatus.EMPTY_SELECTION,
            issues=tuple(issues + selection_issues),
            cleaned=cleaned.clear(),
        )

    cleaned = cleaned.filter(
        col("terminal").is_in(terminals) & col("phase").is_in(phases)
    )
    status = (
        ValidationStatus.VALID_WITH_ISSUES
        if issues
        else ValidationStatus.VALID
    )
    if cleaned.is_empty():
        status = ValidationStatus.EMPTY_SELECTION
    return ValidationResult(
        status=status,
        issues=tuple(issues),
        cleaned=cleaned,
    )


def _validate_schema(observations: DataFrame) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in observations.columns
    ]
    for column in missing_columns:
        issues.append(
            ValidationIssue(
                code=ValidationIssueCode.MISSING_COLUMN,
                message=f"Required column is missing: {column}.",
                field=column,
            )
        )
    if missing_columns:
        return issues

    schema = observations.schema
    expected_kinds = {
        "source_file": "string",
        "simulation": "integer",
        "terminal": "string",
        "phase": "string",
        "value_pu": "float",
        "time": "float",
    }
    for field, expected_kind in expected_kinds.items():
        dtype = schema[field]
        valid = (
            expected_kind == "string"
            and dtype == String
            or expected_kind == "integer"
            and dtype.is_integer()
            or expected_kind == "float"
            and dtype.is_float()
        )
        if not valid:
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.INVALID_COLUMN_TYPE,
                    message=(
                        f"Column {field} must have {expected_kind} data."
                    ),
                    field=field,
                )
            )
    return issues


def _validate_row(
    row: dict[str, Any],
    row_index: int,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    context = _issue_context(row, row_index)
    for field in ("source_file", "terminal", "phase"):
        value = row[field]
        if value is None or not value.strip():
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.INVALID_IDENTITY,
                    message=f"Identity field {field} must not be blank.",
                    field=field,
                    **context,
                )
            )
    if row["simulation"] is None:
        issues.append(
            ValidationIssue(
                code=ValidationIssueCode.INVALID_IDENTITY,
                message="Identity field simulation must not be null.",
                field="simulation",
                **context,
            )
        )
    for field, code in (
        ("value_pu", ValidationIssueCode.NON_FINITE_VALUE),
        ("time", ValidationIssueCode.NON_FINITE_TIME),
    ):
        value = row[field]
        if value is None or not isfinite(value):
            issues.append(
                ValidationIssue(
                    code=code,
                    message=f"Column {field} contains a non-finite value.",
                    field=field,
                    **context,
                )
            )
    return issues


def _issue_context(
    row: dict[str, Any],
    row_index: int,
) -> dict[str, Any]:
    return {
        "row_index": row_index,
        "source_file": row.get("source_file"),
        "simulation": row.get("simulation"),
        "terminal": row.get("terminal"),
        "phase": row.get("phase"),
    }


def _validate_selection(
    observations: DataFrame,
    *,
    terminals: tuple[str, ...],
    phases: tuple[str, ...],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    available_terminals = set(observations["terminal"].drop_nulls())
    available_phases = set(observations["phase"].drop_nulls())
    for terminal in terminals:
        if terminal not in available_terminals:
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.MISSING_TERMINAL,
                    message=f"Selected terminal is absent: {terminal}.",
                    terminal=terminal,
                )
            )
    for phase in phases:
        if phase not in available_phases:
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.MISSING_PHASE,
                    message=f"Selected phase is absent: {phase}.",
                    phase=phase,
                )
            )
    return issues


def load_validation_contract(
    directory: Path,
    encoding: str = "iso-8859-1",
) -> tuple[dict[str, int], dict[str, tuple[float, float]]]:
    """Read declarations from LIS output, independently of extracted rows.

    Returns:
        Declared run counts and available echoed simulation time bounds.
        Simplified LIS fixtures without miscellaneous cards have no bounds.

    Raises:
        ValueError: If an echoed time interval is invalid.
    """
    counts: dict[str, int] = {}
    bounds: dict[str, tuple[float, float]] = {}
    for path in sorted(directory.rglob("*.lis")):
        text = path.read_text(encoding=encoding)
        source = str(path.relative_to(directory))
        match = search(r"NENERG\s*=\s*(\d+)", text)
        counts[source] = int(match[1]) if match else 0
        for line in text.splitlines():
            if line.startswith("Misc. data.") and "|" in line:
                card = line.split("|", 1)[1]
                end = float(card[8:16])
                start = float(card[56:64].strip() or "0")
                if not isfinite(start) or not isfinite(end) or start > end:
                    raise ValueError(f"Invalid time interval in {source}")
                bounds[source] = (start, end)
                break
    return counts, bounds
