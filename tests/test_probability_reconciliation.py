"""Tests for ATP probability-table parsing and reconciliation."""

from pathlib import Path

import pytest

from src.parser.statistical_distribution import (
    parse_statistical_distributions,
)
from src.services.probability_reconciliation import (
    reconcile_probability_bin,
)

ATP_TABLE = """
The data case involves NENERG = 5 simulations.
Statistical distribution of peak voltage at node  "T_MANA".  The base
voltage for per unit printout is V-base = 1.12677000E+05
  Interval voltage voltage in Frequency Cumulative Per cent
    number in per unit physical units (density) frequency .GE. current value
        20  1.0000000  1.12677000E+05  0  0  100.000000
        21  1.0500000  1.18310850E+05  1  1   80.000000
        22  1.1000000  1.23944700E+05  2  3   40.000000
Summary of preceding table follows:
"""


def test_parses_atp_bins_with_scope_counts_and_precision() -> None:
    bins = parse_statistical_distributions(ATP_TABLE)

    assert len(bins) == 3
    row = bins[1]
    assert row.terminal == "T_MAN"
    assert row.phase == "A"
    assert row.interval_number == 21
    assert row.threshold == pytest.approx(1.05)
    assert row.unit == "p.u."
    assert row.frequency_count == 1
    assert row.cumulative_frequency == 1
    assert row.denominator == 5
    assert row.source_count == 4
    assert row.source_probability == pytest.approx(0.8)
    assert row.source_percentage == pytest.approx(80.0)
    assert row.comparison_operator == ".GE."
    assert row.printed_precision == 6


def test_parser_accepts_path_without_changing_main_parser(
    tmp_path: Path,
) -> None:
    source = tmp_path / "case.lis"
    source.write_text(ATP_TABLE, encoding="latin-1")

    from_path = parse_statistical_distributions(source)
    from_text = parse_statistical_distributions(ATP_TABLE)

    assert from_path == from_text


def test_parser_requires_declared_denominator() -> None:
    source = ATP_TABLE.replace("NENERG = 5", "no run declaration")

    with pytest.raises(ValueError, match="NENERG declaration not found"):
        parse_statistical_distributions(source)


def test_reconciles_strict_direct_count_with_atp_bin() -> None:
    source_bin = parse_statistical_distributions(ATP_TABLE)[1]

    result = reconcile_probability_bin(
        source_bin,
        [1.0, 1.06, 1.07, 1.08, 1.09],
    )

    assert result.source_count == 4
    assert result.recomputed_count == 4
    assert result.source_probability == pytest.approx(0.8)
    assert result.recomputed_probability == pytest.approx(0.8)
    assert result.source_operator == ".GE."
    assert result.recomputed_operator == ">"
    assert result.probability_tolerance == pytest.approx(0.000000005)
    assert result.validation_status == "valid"
    assert result.reason == "Counts and probabilities agree within tolerance."


def test_threshold_equality_qualifies_boundary_semantics() -> None:
    source_bin = parse_statistical_distributions(ATP_TABLE)[0]

    result = reconcile_probability_bin(
        source_bin,
        [1.0, 1.1, 1.2, 1.3, 1.4],
    )

    assert result.source_count == 5
    assert result.recomputed_count == 4
    assert result.boundary_count == 1
    assert result.validation_status == "qualified"
    assert result.reason == (
        "ATP .GE. includes 1 boundary observation excluded by strict >."
    )


def test_unexplained_count_difference_is_invalid() -> None:
    source_bin = parse_statistical_distributions(ATP_TABLE)[1]

    result = reconcile_probability_bin(
        source_bin,
        [1.0, 1.01, 1.02, 1.08, 1.09],
    )

    assert result.source_count == 4
    assert result.recomputed_count == 2
    assert result.validation_status == "invalid"
    assert result.reason == "Source and recomputed occurrence counts differ."


def test_denominator_difference_is_invalid_and_preserved() -> None:
    source_bin = parse_statistical_distributions(ATP_TABLE)[1]

    result = reconcile_probability_bin(source_bin, [1.0, 1.1, 1.2])

    assert result.source_denominator == 5
    assert result.recomputed_denominator == 3
    assert result.validation_status == "invalid"
    assert result.reason == "Source and recomputed denominators differ."
