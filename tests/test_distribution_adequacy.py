"""Tests for Gaussian adequacy and robust MAD evidence."""

from collections.abc import Sequence

import pytest
from numpy import concatenate
from numpy.random import default_rng
from polars import DataFrame

from src.services.distribution_adequacy import (
    evaluate_distribution_adequacy,
    evaluate_mad_evidence,
)


def _observations(values: Sequence[float | None]) -> DataFrame:
    return DataFrame({
        "scenario": ["SRPI"] * len(values),
        "sample_size": [len(values)] * len(values),
        "terminal": ["T_OPO"] * len(values),
        "phase": ["A"] * len(values),
        "value_pu": values,
    })


def test_approximately_normal_sample_is_not_rejected() -> None:
    values = default_rng(42).normal(1.8, 0.15, 512).tolist()

    row = evaluate_distribution_adequacy(
        _observations(values), threshold=2.0
    ).row(0, named=True)

    assert row["decision"] == "not_rejected"
    assert row["applicability"] == "applicable"
    assert row["anderson_p_value"] >= 0.05
    assert row["significance_level"] == 0.05
    assert row["reference_method"] == "scipy_anderson_interpolate"
    assert row["fitting_policy"] == "sample_mean_sample_std_ddof_1"
    assert row["qq_correlation"] > 0.99


@pytest.mark.parametrize(
    "values",
    [
        default_rng(7).exponential(1.0, 512).tolist(),
        default_rng(8).standard_t(2.0, 512).tolist(),
        concatenate((
            default_rng(9).normal(-2.0, 0.2, 256),
            default_rng(10).normal(2.0, 0.2, 256),
        )).tolist(),
    ],
    ids=["skewed", "heavy_tailed", "multimodal"],
)
def test_non_gaussian_samples_are_rejected(values: list[float]) -> None:
    row = evaluate_distribution_adequacy(
        _observations(values), threshold=2.0
    ).row(0, named=True)

    assert row["decision"] == "rejected"
    assert row["anderson_p_value"] < 0.05
    assert row["gaussian_inference_status"] == "descriptive_only"
    assert row["skewness"] is not None
    assert row["excess_kurtosis"] is not None


def test_undersized_sample_is_explicitly_non_applicable() -> None:
    row = evaluate_distribution_adequacy(
        _observations([1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]),
        threshold=1.4,
    ).row(0, named=True)

    assert row["decision"] == "undersized"
    assert row["applicability"] == "non_applicable"
    assert row["anderson_statistic"] is None
    assert row["empirical_exceedance"] == pytest.approx(2 / 7)
    assert row["gaussian_exceedance"] is not None


def test_constant_sample_is_explicitly_degenerate() -> None:
    row = evaluate_distribution_adequacy(
        _observations([1.5] * 8), threshold=2.0
    ).row(0, named=True)

    assert row["decision"] == "degenerate"
    assert row["applicability"] == "non_applicable"
    assert row["fitted_standard_deviation"] == 0.0
    assert row["gaussian_exceedance"] is None
    assert row["empirical_exceedance"] == 0.0


def test_reports_empirical_and_gaussian_tail_differences() -> None:
    values = default_rng(21).normal(1.8, 0.15, 512).tolist()
    row = evaluate_distribution_adequacy(
        _observations(values), threshold=2.0
    ).row(0, named=True)

    expected_absolute = abs(
        row["empirical_exceedance"] - row["gaussian_exceedance"]
    )
    assert row["absolute_tail_difference"] == pytest.approx(
        expected_absolute
    )
    assert row["relative_tail_difference"] == pytest.approx(
        expected_absolute / row["empirical_exceedance"]
    )


def test_zero_empirical_probability_has_no_relative_difference() -> None:
    values = default_rng(33).normal(1.0, 0.05, 64).tolist()
    row = evaluate_distribution_adequacy(
        _observations(values), threshold=3.0
    ).row(0, named=True)

    assert row["empirical_exceedance"] == 0.0
    assert row["absolute_tail_difference"] is not None
    assert row["relative_tail_difference"] is None


def test_mad_evidence_flags_only_explicit_robust_extreme() -> None:
    values = [1.0, 1.01, 0.99, 1.02, 0.98, 1.03, 0.97, 3.0]

    result = evaluate_mad_evidence(_observations(values))
    flagged = result.filter(result["mad_flag"])

    assert flagged.height == 1
    assert flagged.item(0, "value_pu") == 3.0
    assert flagged.item(0, "modified_mad_score") > 3.5
    assert set(result["mad_threshold"]) == {3.5}
    assert set(result["mad_applicability"]) == {"applicable"}


def test_mad_evidence_is_non_applicable_for_degenerate_group() -> None:
    result = evaluate_mad_evidence(_observations([1.0] * 8))

    assert result["modified_mad_score"].null_count() == 8
    assert not result["mad_flag"].any()
    assert set(result["mad_applicability"]) == {"non_applicable"}
    assert set(result["mad_reason"]) == {"Median absolute deviation is zero."}


def test_non_finite_values_are_excluded_and_reported() -> None:
    values = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7]
    row = evaluate_distribution_adequacy(
        _observations([*values, None, float("nan")]), threshold=1.5
    ).row(0, named=True)

    assert row["count"] == 10
    assert row["valid_count"] == 8
    assert row["excluded_count"] == 2
    assert row["decision"] in {"not_rejected", "rejected"}
