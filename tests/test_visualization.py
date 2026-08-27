"""Unit tests for the visualization service.

These are smoke tests — they verify function signatures and return types
without rendering any GUI window (using the ``Agg`` non-interactive backend).
"""

import matplotlib
import polars as pl

matplotlib.use("Agg")  # Must be set before importing pyplot

from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from src.services.visualization import (  # noqa: E402
    TERMINAL_DISTANCES,
    plot_combined,
    plot_overvoltage_histogram,
    plot_overvoltage_scatter,
    plot_pdf_overlay,
    plot_switching_time_curve,
)


def _make_df(n_per_terminal: int = 20) -> pl.DataFrame:
    """Build a minimal mock DataFrame with two terminals."""
    import numpy as np

    rng = np.random.default_rng(seed=0)
    rows = []
    for terminal, mean in [("T_MAN", 1.2), ("T_OPO", 1.8)]:
        values = rng.normal(loc=mean, scale=0.1, size=n_per_terminal).tolist()
        for index, v in enumerate(values):
            rows.append({
                "terminal": terminal,
                "value_pu": v,
                "time": 0.01 + index * 0.0001,
            })
    return pl.DataFrame(rows)


def test_plot_scatter_returns_figure_and_axes():
    df = _make_df()
    fig, ax = plot_overvoltage_scatter(df)
    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_plot_scatter_with_all_terminals():
    import numpy as np

    rng = np.random.default_rng(seed=1)
    rows = []
    for terminal in TERMINAL_DISTANCES:
        for v in rng.normal(1.5, 0.15, 10).tolist():
            rows.append({"terminal": terminal, "value_pu": v})
    df = pl.DataFrame(rows)
    fig, ax = plot_overvoltage_scatter(df)
    assert isinstance(fig, Figure)


def test_plot_pdf_overlay_returns_figure_and_axes():
    df = _make_df()
    fig, ax = plot_pdf_overlay(df)
    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_plot_combined_returns_figure_and_axes():
    df = _make_df()
    fig, ax = plot_combined(df)
    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_plot_overvoltage_histogram_groups_frequencies_by_terminal():
    df = _make_df()

    fig, ax = plot_overvoltage_histogram(df, bins=8)

    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)
    assert ax.get_ylabel() == "Frequency"
    legend = ax.get_legend()
    assert legend is not None
    assert {text.get_text() for text in legend.get_texts()} == {
        "T_MAN",
        "T_OPO",
    }


def test_plot_switching_time_returns_figure_and_axes():
    df = pl.DataFrame({
        "switch_number": [1, 1, 2, 2],
        "opening_time": [0.019, 0.0205, 0.011, 0.013],
        "mean_time": [0.02, 0.02, 0.012, 0.012],
        "std_dev": [0.000833, 0.000833, 0.001, 0.001],
    })
    fig, ax = plot_switching_time_curve(df)
    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)


def test_plot_scatter_empty_terminal_subset_no_crash():
    """Scatter with only one terminal should not raise."""
    df = pl.DataFrame([
        {"terminal": "T_MAN", "value_pu": 1.2},
        {"terminal": "T_MAN", "value_pu": 1.3},
    ])
    fig, ax = plot_overvoltage_scatter(df)
    assert isinstance(fig, Figure)


def test_plot_pdf_single_terminal_no_crash():
    """PDF overlay with a single terminal and enough points must not crash."""
    import numpy as np

    rng = np.random.default_rng(seed=2)
    df = pl.DataFrame({
        "terminal": ["T_OPO"] * 30,
        "value_pu": rng.normal(1.8, 0.1, 30).tolist(),
    })
    fig, ax = plot_pdf_overlay(df)
    assert isinstance(fig, Figure)


def test_terminal_distances_coverage():
    """All canonical terminals must be present in TERMINAL_DISTANCES."""
    expected = {"T_MAN", "1_4LT", "1_2LT", "3_4LT", "T_OPO"}
    assert expected == set(TERMINAL_DISTANCES)
