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
    plot_overvoltage_scatter,
    plot_pdf_overlay,
)


def _make_df(n_per_terminal: int = 20) -> pl.DataFrame:
    """Build a minimal mock DataFrame with two terminals."""
    import numpy as np

    rng = np.random.default_rng(seed=0)
    rows = []
    for terminal, mean in [("T_MAN", 1.2), ("T_OPO", 1.8)]:
        values = rng.normal(loc=mean, scale=0.1, size=n_per_terminal).tolist()
        for v in values:
            rows.append({"terminal": terminal, "value_pu": v})
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
