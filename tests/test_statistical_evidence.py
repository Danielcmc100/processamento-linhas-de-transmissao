"""Tests for auditable descriptive and empirical probability evidence."""

from collections.abc import Sequence

import pytest
from polars import DataFrame

from src.services.statistical_evidence import summarize_statistical_evidence


def _observations(values: Sequence[float | None]) -> DataFrame:
    return DataFrame({
        "scenario": ["SRPI"] * len(values),
        "sample_size": [200] * len(values),
        "terminal": ["T_OPO"] * len(values),
        "phase": ["A"] * len(values),
        "value_pu": values,
    })


def test_reports_scoped_descriptive_statistics() -> None:
    result = summarize_statistical_evidence(
        _observations([1.0, 2.0, 3.0, 4.0]), threshold=2.0
    )

    row = result.row(0, named=True)
    assert row["scenario"] == "SRPI"
    assert row["sample_size"] == 200
    assert row["terminal"] == "T_OPO"
    assert row["phase"] == "A"
    assert row["unit"] == "p.u."
    assert row["count"] == 4
    assert row["valid_count"] == 4
    assert row["mean"] == pytest.approx(2.5)
    assert row["sample_standard_deviation"] == pytest.approx(1.2909944487)
    assert row["median"] == pytest.approx(2.5)
    assert row["quartile_1"] == pytest.approx(1.75)
    assert row["quartile_3"] == pytest.approx(3.25)
    assert row["percentile_90"] == pytest.approx(3.7)
    assert row["percentile_95"] == pytest.approx(3.85)
    assert row["percentile_99"] == pytest.approx(3.97)
    assert row["minimum"] == 1.0
    assert row["maximum"] == 4.0


def test_uses_strict_exceedance_and_records_event_definition() -> None:
    result = summarize_statistical_evidence(
        _observations([2.0, 2.1, 1.9]), threshold=2.0
    )

    row = result.row(0, named=True)
    assert row["comparison_operator"] == ">"
    assert row["event_definition"] == "value_pu > 2 p.u."
    assert row["occurrence_count"] == 1
    assert row["denominator"] == 3
    assert row["empirical_probability"] == pytest.approx(1 / 3)
    assert row["empirical_percentage"] == pytest.approx(100 / 3)
    assert row["calculation_source"] == "direct_observation_count"


def test_computes_verified_two_sided_wilson_interval() -> None:
    result = summarize_statistical_evidence(
        _observations([1.0, 1.0, 3.0, 3.0]), threshold=2.0
    )

    row = result.row(0, named=True)
    assert row["confidence_level"] == 0.95
    assert row["confidence_interval_method"] == "wilson"
    assert row["confidence_interval_lower"] == pytest.approx(
        0.15003898915214953
    )
    assert row["confidence_interval_upper"] == pytest.approx(
        0.8499610108478505
    )


@pytest.mark.parametrize(
    ("values", "expected_probability", "expected_bound"),
    [
        ([1.0] * 10, 0.0, 0.27753279986288926),
        ([3.0] * 10, 1.0, 0.7224672001371109),
    ],
)
def test_preserves_boundary_probabilities_with_wilson_uncertainty(
    values: list[float],
    expected_probability: float,
    expected_bound: float,
) -> None:
    row = summarize_statistical_evidence(
        _observations(values), threshold=2.0
    ).row(0, named=True)

    assert row["empirical_probability"] == expected_probability
    if expected_probability == 0.0:
        assert row["confidence_interval_lower"] == 0.0
        assert row["confidence_interval_upper"] == pytest.approx(
            expected_bound
        )
    else:
        assert row["confidence_interval_lower"] == pytest.approx(
            expected_bound
        )
        assert row["confidence_interval_upper"] == 1.0
    assert row["probability_applicability"] == "applicable"


def test_excludes_non_finite_values_and_preserves_denominator() -> None:
    row = summarize_statistical_evidence(
        _observations([1.0, None, float("nan"), float("inf"), 3.0]),
        threshold=2.0,
    ).row(0, named=True)

    assert row["count"] == 5
    assert row["valid_count"] == 2
    assert row["excluded_count"] == 3
    assert row["denominator"] == 2
    assert row["occurrence_count"] == 1
    assert row["exclusions"] == "3 null or non-finite observation(s)"
    assert row["validation_status"] == "qualified"


def test_all_invalid_group_is_explicitly_non_applicable() -> None:
    row = summarize_statistical_evidence(
        _observations([None, float("nan")]), threshold=2.0
    ).row(0, named=True)

    assert row["valid_count"] == 0
    assert row["mean"] is None
    assert row["sample_standard_deviation"] is None
    assert row["denominator"] == 0
    assert row["empirical_probability"] is None
    assert row["confidence_interval_lower"] is None
    assert row["confidence_interval_upper"] is None
    assert row["descriptive_applicability"] == "non_applicable"
    assert row["probability_applicability"] == "non_applicable"
    assert row["validation_status"] == "invalid"
    assert row["reason"] == "No valid observations."


def test_single_valid_value_qualifies_only_sample_standard_deviation() -> None:
    row = summarize_statistical_evidence(
        _observations([3.0]), threshold=2.0
    ).row(0, named=True)

    assert row["sample_standard_deviation"] is None
    assert row["empirical_probability"] == 1.0
    assert row["descriptive_applicability"] == "qualified"
    assert row["probability_applicability"] == "applicable"
    assert row["validation_status"] == "qualified"
    assert row["reason"] == (
        "Sample standard deviation requires at least two valid observations."
    )


def test_groups_are_evaluated_independently() -> None:
    observations = DataFrame({
        "scenario": ["SRPI", "SRPI", "CRPI", "CRPI"],
        "sample_size": [50, 50, 100, 100],
        "terminal": ["T_MAN", "T_MAN", "T_OPO", "T_OPO"],
        "phase": ["A", "A", "B", "B"],
        "value_pu": [1.0, 3.0, 3.0, 4.0],
    })

    result = summarize_statistical_evidence(observations, threshold=2.0)

    assert result.height == 2
    assert result["scenario"].to_list() == ["SRPI", "CRPI"]
    assert result["empirical_probability"].to_list() == [0.5, 1.0]


def test_empty_input_returns_declared_empty_schema() -> None:
    result = summarize_statistical_evidence(_observations([]), threshold=2.0)

    assert result.is_empty()
    assert "confidence_interval_lower" in result.columns
    assert result.schema["empirical_probability"].is_float()


@pytest.mark.parametrize("threshold", [float("nan"), float("inf")])
def test_rejects_non_finite_threshold(threshold: float) -> None:
    with pytest.raises(ValueError, match="threshold must be finite"):
        summarize_statistical_evidence(
            _observations([1.0]), threshold=threshold
        )


def test_rejects_missing_scope_columns() -> None:
    observations = _observations([1.0]).drop("scenario")

    with pytest.raises(ValueError, match="Missing required columns: scenario"):
        summarize_statistical_evidence(observations, threshold=2.0)
