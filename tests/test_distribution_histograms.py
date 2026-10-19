"""Scientific contracts for density panels and model comparisons."""

from matplotlib.pyplot import close
from numpy.random import default_rng
from polars import DataFrame, col, concat, lit
from pytest import approx, raises
from scipy.stats import norm

from src.services.distribution_histograms import (
    compare_distributions,
    plot_distribution_histograms,
)


def _observations(values: list[float]) -> DataFrame:
    """Return a single declared experimental group."""
    return DataFrame({"value_pu": values}).with_columns(
        lit("SRPI").alias("scenario"),
        lit(len(values)).alias("sample_size"),
        lit("test-source").alias("source_lineage"),
        lit("T_MAN").alias("terminal"),
        lit("A").alias("phase"),
    )


def test_comparison_preserves_groups_and_mle_aic() -> None:
    values = default_rng(42).normal(1.5, 0.1, 100).tolist()
    first = _observations(values)
    second = first.with_columns(
        lit("B").alias("phase"), (col("value_pu") + 1).alias("value_pu")
    )
    comparison = compare_distributions(concat([first, second]))
    normal = comparison.filter(
        (col("model") == "normal") & (col("phase") == "A")
    )
    location, scale = norm.fit(values)
    expected = 4 - 2 * norm.logpdf(values, location, scale).sum()
    assert normal.item(0, "aic") == approx(expected)
    assert comparison.height == 6
    assert comparison.filter(col("selected")).height == 2
    assert set(comparison["n"]) == {100}
    for group in comparison.partition_by("phase"):
        winner = group.filter(col("selected"))
        assert winner.item(0, "aic") == group["aic"].min()


def test_degenerate_groups_have_no_selected_fit() -> None:
    comparison = compare_distributions(_observations([1.0] * 5))
    assert set(comparison["status"]) == {"unavailable"}
    assert comparison["selected"].sum() == 0
    assert set(comparison["reason"]) == {"Constant observations."}


def test_density_integrates_to_one_in_separate_phase_panels() -> None:
    first = _observations([1.0, 1.1, 1.2, 1.4, 1.9])
    observations = concat([
        first.with_columns(lit(phase).alias("phase"))
        for phase in ("A", "B", "C")
    ])
    figure, axes = plot_distribution_histograms(
        observations, compare_distributions(observations), ("T_MAN",)
    )
    try:
        assert len(axes) == 3
        for axis in axes:
            area = sum(
                bar.get_width() * bar.get_height() for bar in axis.patches
            )
            assert area == approx(1.0)
            assert "n = 5" in axis.texts[0].get_text()
    finally:
        close(figure)


def test_plot_rejects_pooled_scenarios() -> None:
    first = _observations([1.0, 1.1, 1.2, 1.4])
    observations = concat([
        first,
        first.with_columns(lit("CRPI").alias("scenario")),
    ])
    with raises(ValueError, match="one nonempty source scope"):
        plot_distribution_histograms(
            observations, compare_distributions(observations), ("T_MAN",)
        )
