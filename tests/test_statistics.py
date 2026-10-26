"""Unit tests for the statistical distribution service."""

from math import sqrt

import polars as pl
import pytest

from src.services.schemas import StatisticalSummaryRow
from src.services.statistics import (
    GaussianFitResult,
    fit_gaussian,
    summarize_statistics,
)


def _sample_df(values: list[float]) -> pl.DataFrame:
    return pl.DataFrame({"value_pu": values})


def test_fit_gaussian_mean_std():
    values = [1.0, 1.5, 2.0, 2.5, 3.0]
    df = _sample_df(values)
    fit = fit_gaussian(df)

    assert abs(fit.mean - 2.0) < 1e-9
    assert fit.n_samples == 5
    assert fit.std > 0


def test_gaussian_fit_retains_descriptive_parameters() -> None:
    fit = GaussianFitResult(mean=1.5, std=0.2, n_samples=100)
    assert (fit.mean, fit.std, fit.n_samples) == (1.5, 0.2, 100)
    assert not hasattr(fit, "sigma_level")


def test_exceedance_probability_above_mean():
    fit = GaussianFitResult(mean=1.5, std=0.2, n_samples=100)
    # P(X > mean) ~ 0.5
    prob = fit.exceedance_probability(1.5)
    assert abs(prob - 0.5) < 1e-6


def test_exceedance_probability_far_right_tail():
    fit = GaussianFitResult(mean=1.5, std=0.2, n_samples=100)
    # Retain Gaussian tail evaluation at an independently supplied voltage.
    prob = fit.exceedance_probability(2.1)
    assert 0.001 < prob < 0.002


def test_summary_schema_has_no_voltage_sigma_threshold() -> None:
    assert "sigma_3_threshold" not in StatisticalSummaryRow.dtypes


def test_fit_gaussian_raises_on_empty():
    df = _sample_df([])
    with pytest.raises(Exception):
        _ = fit_gaussian(df)


def test_summarize_statistics_groups_by_terminal_and_phase() -> None:
    observations = pl.DataFrame({
        "terminal": ["T_MAN", "T_MAN", "T_MAN", "T_MAN", "T_OPO"],
        "phase": ["A", "A", "A", "B", "A"],
        "value_pu": [1.0, 2.0, 3.0, 10.0, 2.0],
    })

    summary = summarize_statistics(observations, threshold=3.0).sort(
        "terminal", "phase"
    )

    assert summary["terminal"].to_list() == ["T_MAN", "T_MAN", "T_OPO"]
    assert summary["phase"].to_list() == ["A", "B", "A"]
    first = summary.row(0, named=True)
    assert first["n_total"] == 3
    assert first["n_valid"] == 3
    assert first["mean"] == pytest.approx(2.0)
    assert first["std"] == pytest.approx(1.0)
    assert "sigma_3_threshold" not in summary.columns
    assert first["empirical_exceedance"] == pytest.approx(0.0)
    assert first["gaussian_exceedance"] == pytest.approx(0.15865525393145707)
    assert first["validation_status"] == "valid"

    for row in summary.rows(named=True)[1:]:
        assert row["n_total"] == 1
        assert row["n_valid"] == 1
        assert row["std"] is None
        assert row["gaussian_exceedance"] is None
        assert row["validation_status"] == "insufficient_samples"


def test_summarize_statistics_guards_non_finite_and_zero_variance() -> None:
    observations = pl.DataFrame({
        "terminal": ["T_MAN"] * 4 + ["T_OPO"] * 2,
        "phase": ["A"] * 6,
        "value_pu": [2.0, 2.0, float("nan"), float("inf"), 1.0, 1.0],
    })

    summary = summarize_statistics(observations, threshold=1.5).sort(
        "terminal"
    )

    first = summary.row(0, named=True)
    assert first["n_total"] == 4
    assert first["n_valid"] == 2
    assert first["mean"] == pytest.approx(2.0)
    assert first["std"] == pytest.approx(0.0)
    assert "sigma_3_threshold" not in summary.columns
    assert first["empirical_exceedance"] == pytest.approx(1.0)
    assert first["gaussian_exceedance"] is None
    assert first["validation_status"] == "zero_variance"

    second = summary.row(1, named=True)
    assert second["empirical_exceedance"] == pytest.approx(0.0)
    assert second["validation_status"] == "zero_variance"


def test_summarize_statistics_handles_no_valid_observations() -> None:
    observations = pl.DataFrame({
        "terminal": ["T_MAN", "T_MAN"],
        "phase": ["A", "A"],
        "value_pu": [float("nan"), float("-inf")],
    })

    summary = summarize_statistics(observations, threshold=2.3)

    assert summary.row(0, named=True) == {
        "terminal": "T_MAN",
        "phase": "A",
        "n_total": 2,
        "n_valid": 0,
        "mean": None,
        "std": None,
        "empirical_exceedance": None,
        "gaussian_exceedance": None,
        "validation_status": "insufficient_samples",
    }


def test_empty_summary_preserves_sigma_free_schema() -> None:
    observations = pl.DataFrame(
        schema={
            "terminal": pl.String,
            "phase": pl.String,
            "value_pu": pl.Float64,
        }
    )

    summary = summarize_statistics(observations, threshold=2.3)

    assert summary.is_empty()
    assert summary.schema == StatisticalSummaryRow.dtypes
    assert "sigma_3_threshold" not in summary.columns


def test_summary_uses_finite_sample_standard_deviation() -> None:
    observations = pl.DataFrame({
        "terminal": ["T_MAN"] * 5,
        "phase": ["A"] * 5,
        "value_pu": [1.0, 2.0, None, float("nan"), float("inf")],
    })

    summary = summarize_statistics(observations, threshold=1.5)
    row = summary.row(0, named=True)

    assert row["n_total"] == 5
    assert row["n_valid"] == 2
    assert row["mean"] == pytest.approx(1.5)
    assert row["std"] == pytest.approx(sqrt(0.5))
    assert row["empirical_exceedance"] == pytest.approx(0.5)
    assert row["gaussian_exceedance"] == pytest.approx(0.5)
    assert row["validation_status"] == "valid"
    assert "sigma_3_threshold" not in summary.columns
