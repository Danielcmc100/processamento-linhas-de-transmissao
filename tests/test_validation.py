"""Unit tests for structured observation validation."""

import polars as pl

from src.services.validation import (
    ValidationIssueCode,
    ValidationStatus,
    validate_observations,
)


def _observations() -> pl.DataFrame:
    return pl.DataFrame({
        "source_file": ["run.lis", "run.lis"],
        "simulation": [1, 2],
        "terminal": ["T_MAN", "T_MAN"],
        "phase": ["A", "A"],
        "value_pu": [1.1, 1.2],
        "time": [0.01, 0.02],
    })


def test_valid_observations_return_clean_status() -> None:
    observations = _observations()

    result = validate_observations(
        observations,
        terminals=("T_MAN",),
        phases=("A",),
    )

    assert result.status is ValidationStatus.VALID
    assert result.is_valid
    assert result.issues == ()
    assert result.cleaned.equals(observations)


def test_non_finite_rows_are_reported_and_excluded() -> None:
    observations = _observations().with_columns(
        pl.Series("value_pu", [float("nan"), 1.2]),
        pl.Series("time", [0.01, float("inf")]),
    )

    result = validate_observations(
        observations,
        terminals=("T_MAN",),
        phases=("A",),
    )

    assert result.status is ValidationStatus.VALID_WITH_ISSUES
    assert result.is_valid
    assert result.cleaned.is_empty()
    assert [issue.code for issue in result.issues] == [
        ValidationIssueCode.NON_FINITE_VALUE,
        ValidationIssueCode.NON_FINITE_TIME,
    ]
    assert result.issues[0].row_index == 0
    assert result.issues[0].source_file == "run.lis"
    assert result.issues[0].simulation == 1
    assert result.issues[0].terminal == "T_MAN"
    assert result.issues[0].phase == "A"


def test_missing_terminal_selection_has_explicit_status() -> None:
    result = validate_observations(
        _observations(),
        terminals=("T_OPO",),
        phases=("A",),
    )

    assert result.status is ValidationStatus.EMPTY_SELECTION
    assert not result.is_valid
    assert result.cleaned.is_empty()
    assert len(result.issues) == 1
    assert result.issues[0].code is ValidationIssueCode.MISSING_TERMINAL
    assert result.issues[0].terminal == "T_OPO"


def test_missing_phase_selection_has_explicit_status() -> None:
    result = validate_observations(
        _observations(),
        terminals=("T_MAN",),
        phases=("B",),
    )

    assert result.status is ValidationStatus.EMPTY_SELECTION
    assert result.cleaned.is_empty()
    assert len(result.issues) == 1
    assert result.issues[0].code is ValidationIssueCode.MISSING_PHASE
    assert result.issues[0].phase == "B"


def test_empty_dataset_has_explicit_status() -> None:
    observations = _observations().clear()

    result = validate_observations(
        observations,
        terminals=("T_MAN",),
        phases=("A",),
    )

    assert result.status is ValidationStatus.EMPTY_DATASET
    assert not result.is_valid
    assert result.cleaned.equals(observations)
    assert len(result.issues) == 1
    assert result.issues[0].code is ValidationIssueCode.EMPTY_DATASET


def test_missing_required_column_is_invalid_without_added_columns() -> None:
    observations = _observations().drop("time")

    result = validate_observations(
        observations,
        terminals=("T_MAN",),
        phases=("A",),
    )

    assert result.status is ValidationStatus.INVALID_INPUT
    assert not result.is_valid
    assert result.cleaned.columns == observations.columns
    assert result.cleaned.is_empty()
    assert len(result.issues) == 1
    assert result.issues[0].code is ValidationIssueCode.MISSING_COLUMN
    assert result.issues[0].field == "time"


def test_incompatible_column_type_is_invalid() -> None:
    observations = _observations().with_columns(
        pl.col("simulation").cast(pl.String)
    )

    result = validate_observations(
        observations,
        terminals=("T_MAN",),
        phases=("A",),
    )

    assert result.status is ValidationStatus.INVALID_INPUT
    assert result.cleaned.is_empty()
    assert len(result.issues) == 1
    assert result.issues[0].code is ValidationIssueCode.INVALID_COLUMN_TYPE
    assert result.issues[0].field == "simulation"


def test_invalid_identity_is_reported_with_available_context() -> None:
    observations = _observations().with_columns(
        pl.Series("terminal", ["", "T_MAN"])
    )

    result = validate_observations(
        observations,
        terminals=("T_MAN",),
        phases=("A",),
    )

    assert result.status is ValidationStatus.INVALID_INPUT
    assert not result.is_valid
    assert result.cleaned["simulation"].to_list() == [2]
    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.code is ValidationIssueCode.INVALID_IDENTITY
    assert issue.field == "terminal"
    assert issue.row_index == 0
    assert issue.source_file == "run.lis"
    assert issue.simulation == 1
    assert issue.phase == "A"
