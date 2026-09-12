"""Adversarial checks of the declared experimental contract."""

from pathlib import Path

from polars import DataFrame, Series, concat
from pytest import mark

from src.services.validation import (
    ValidationIssueCode,
    ValidationStatus,
    load_validation_contract,
    validate_observations,
)


def observations() -> DataFrame:
    """Return a hand-specified, complete two-run study."""
    return DataFrame({
        "source_file": ["case.lis"] * 4,
        "simulation": [1, 1, 2, 2],
        "terminal": ["T_MAN", "T_OPO"] * 2,
        "phase": ["A"] * 4,
        "value_pu": [1.0, 2.0, 3.0, 99.0],
        "time": [0.0, 0.1, 0.2, 0.3],
    })


@mark.parametrize("corruption", ["duplicate", "missing", "run", "source"])
def test_matrix_corruption_blocks_analysis(corruption: str) -> None:
    """Reject changes that would silently alter the sampling unit."""
    frame = observations()
    if corruption == "duplicate":
        frame = concat([frame, frame.head(1)])
    elif corruption == "missing":
        frame = frame.head(3)
    elif corruption == "run":
        frame = frame.with_columns(Series("simulation", [1, 1, 3, 3]))
    else:
        frame = frame.with_columns(Series("source_file", ["other"] * 4))
    result = validate_observations(
        frame,
        terminals=("T_MAN", "T_OPO"),
        phases=("A",),
        expected_runs={"case.lis": 2},
    )
    assert result.status is ValidationStatus.INVALID_INPUT
    assert not result.is_valid


@mark.parametrize("time", [-0.00001, 0.30001, float("nan"), None])
def test_invalid_measurement_excludes_only_affected_row(
    time: float | None,
) -> None:
    """Keep the other observations and identify the excluded source row."""
    frame = observations().with_columns(Series("time", [time, 0.1, 0.2, 0.3]))
    result = validate_observations(
        frame,
        terminals=("T_MAN", "T_OPO"),
        phases=("A",),
        expected_runs={"case.lis": 2},
        time_bounds={"case.lis": (0.0, 0.3)},
    )
    assert result.status is ValidationStatus.VALID_WITH_ISSUES
    assert result.cleaned.equals(frame.slice(1))
    assert result.issues[0].row_index == 0
    assert result.issues[0].source_file == "case.lis"


def test_boundaries_and_finite_extreme_are_retained() -> None:
    """Do not turn measurement integrity into an amplitude cutoff."""
    frame = observations()
    result = validate_observations(
        frame,
        terminals=("T_MAN", "T_OPO"),
        phases=("A",),
        expected_runs={"case.lis": 2},
        time_bounds={"case.lis": (0.0, 0.3)},
    )
    assert result.status is ValidationStatus.VALID
    assert result.cleaned.equals(frame)


def test_missing_cross_combination_is_detected() -> None:
    """Global terminal and phase presence does not imply completeness."""
    frame = observations().with_columns(Series("phase", ["A", "B", "A", "B"]))
    result = validate_observations(
        frame,
        terminals=("T_MAN", "T_OPO"),
        phases=("A", "B"),
        expected_runs={"case.lis": 2},
    )
    assert any(
        issue.code is ValidationIssueCode.INCOMPLETE_MATRIX
        for issue in result.issues
    )


def test_contract_uses_source_declarations(tmp_path: Path) -> None:
    """Read count and simulation interval without consulting observations."""
    (tmp_path / "case.lis").write_text(
        "NENERG = 2\nMisc. data. |   1.E-5      .3\n",
        encoding="utf-8",
    )
    assert load_validation_contract(tmp_path) == (
        {"case.lis": 2},
        {"case.lis": (0.0, 0.3)},
    )
