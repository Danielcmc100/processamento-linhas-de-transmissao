"""Structured data-quality validation for normalized observations."""

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Any

import polars as pl

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
    cleaned: pl.DataFrame

    @property
    def is_valid(self) -> bool:
        """Return whether the cleaned table may feed analysis services."""
        return self.status in {
            ValidationStatus.VALID,
            ValidationStatus.VALID_WITH_ISSUES,
        }


def validate_observations(
    observations: pl.DataFrame,
    *,
    terminals: tuple[str, ...],
    phases: tuple[str, ...],
) -> ValidationResult:
    """Validate and select normalized ATP observations.

    Non-finite measurement rows are reported and excluded. Schema and
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
    for row_index, row in enumerate(observations.to_dicts()):
        row_issues = _validate_row(row, row_index)
        if row_issues:
            invalid_rows.add(row_index)
            issues.extend(row_issues)

    cleaned = observations.with_row_index("_validation_row")
    if invalid_rows:
        cleaned = cleaned.filter(
            ~pl.col("_validation_row").is_in(sorted(invalid_rows))
        )
    cleaned = cleaned.drop("_validation_row")

    identity_issue = any(
        issue.code is ValidationIssueCode.INVALID_IDENTITY for issue in issues
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
        pl.col("terminal").is_in(terminals) & pl.col("phase").is_in(phases)
    )
    status = (
        ValidationStatus.VALID_WITH_ISSUES
        if issues
        else ValidationStatus.VALID
    )
    return ValidationResult(
        status=status,
        issues=tuple(issues),
        cleaned=cleaned,
    )


def _validate_schema(observations: pl.DataFrame) -> list[ValidationIssue]:
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
            and dtype == pl.String
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
    observations: pl.DataFrame,
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
