"""Unit tests for the statistical distribution service."""

import polars as pl
import pytest

from src.services.statistics import (
    GaussianFitResult,
    fit_gaussian,
    sigma_summary,
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


def test_sigma_level():
    fit = GaussianFitResult(mean=1.5, std=0.2, n_samples=100)
    assert abs(fit.sigma_level(3) - 2.1) < 1e-9
    assert abs(fit.sigma_level(0) - 1.5) < 1e-9


def test_exceedance_probability_above_mean():
    fit = GaussianFitResult(mean=1.5, std=0.2, n_samples=100)
    # P(X > mean) ~ 0.5
    prob = fit.exceedance_probability(1.5)
    assert abs(prob - 0.5) < 1e-6


def test_exceedance_probability_far_right_tail():
    fit = GaussianFitResult(mean=1.5, std=0.2, n_samples=100)
    # P(X > mean + 3*std) ~ 0.00135
    prob = fit.exceedance_probability(fit.sigma_level(3))
    assert 0.001 < prob < 0.002


def test_sigma_summary_shape():
    fit = GaussianFitResult(mean=2.0, std=0.3, n_samples=200)
    summary = sigma_summary(fit)
    assert summary.shape == (6, 3)
    assert list(summary.columns) == [
        "sigma",
        "threshold_pu",
        "exceedance_prob",
    ]
    # Probability should be monotonically decreasing
    probs = summary["exceedance_prob"].to_list()
    assert all(probs[i] > probs[i + 1] for i in range(len(probs) - 1))


def test_fit_gaussian_raises_on_empty():
    df = _sample_df([])
    with pytest.raises(Exception):
        _ = fit_gaussian(df)
