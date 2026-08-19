"""Visualization service for ATP simulation overvoltage analysis.

Provides functions to generate:
- Scatter plots mapping P.U. overvoltage to terminal line position.
- Gaussian Probability Density Function (PDF) overlays on scatter data.
- Combined figures merging both visualisations.
"""

from collections.abc import Sequence
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.markers import MarkerStyle
from scipy import stats

from src.services.statistics import GaussianFitResult, fit_gaussian

# Canonical mapping: terminal name → fractional line distance [0, 1].
# 0 = manoeuvre bus (T_MAN), 1 = remote bus (T_OPO).
TERMINAL_DISTANCES: dict[str, float] = {
    "T_MAN": 0.0,
    "1_4LT": 0.25,
    "1_2LT": 0.50,
    "3_4LT": 0.75,
    "T_OPO": 1.0,
}

# Colour palette — one colour per terminal (order matches sorted distances).
_PALETTE: list[str] = [
    "#2196F3",  # T_MAN   – blue
    "#4CAF50",  # 1_4LT   – green
    "#FF9800",  # 1_2LT   – orange
    "#9C27B0",  # 3_4LT   – purple
    "#F44336",  # T_OPO   – red
]


def _terminal_color(terminal: str) -> str:
    """Return a consistent hex colour for *terminal*."""
    terminals_sorted = sorted(
        TERMINAL_DISTANCES,
        key=lambda name: TERMINAL_DISTANCES[name],
    )
    idx = (
        terminals_sorted.index(terminal) if terminal in terminals_sorted else 0
    )
    return _PALETTE[idx % len(_PALETTE)]


def _jitter(n: int, width: float = 0.01) -> np.ndarray:
    """Return an array of *n* small random horizontal offsets."""
    rng = np.random.default_rng(seed=42)
    return rng.uniform(-width, width, size=n)


def plot_overvoltage_scatter(
    df: pl.DataFrame,
    ax: Axes | None = None,
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    cluster_col: str | None = None,
    terminal_distances: dict[str, float] | None = None,
    jitter_width: float = 0.01,
    alpha: float = 0.45,
    marker_size: float = 18.0,
) -> tuple[Figure, Axes]:
    """Plot a scatter of P.U. overvoltage vs fractional line distance.

    Each unique terminal in *df[terminal_col]* is mapped to its fractional
    position on the transmission line using *terminal_distances* (defaults to
    :data:`TERMINAL_DISTANCES`).  A small horizontal jitter is applied so that
    overlapping points remain distinguishable.

    When *cluster_col* is provided, rows whose cluster label equals ``-1``
    (DBSCAN noise / numerical outliers) are rendered in grey with an ``x``
    marker so they remain visible but clearly distinct from valid events.

    Returns:
        A ``(figure, axes)`` tuple.  If *ax* is provided, the same figure that
        owns it is returned.
    """
    distances = terminal_distances or TERMINAL_DISTANCES

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        raw_fig = ax.get_figure()
        if raw_fig is None or not isinstance(raw_fig, Figure):
            fig, ax = plt.subplots(figsize=(10, 6))
        else:
            fig = raw_fig

    terminals: Sequence[str] = df[terminal_col].unique().sort().to_list()

    outlier_legend_added = False
    for terminal in terminals:
        subset = df.filter(pl.col(terminal_col) == terminal)
        dist = distances.get(terminal, 0.0)
        color = _terminal_color(terminal)

        if cluster_col is not None and cluster_col in df.columns:
            valid = subset.filter(pl.col(cluster_col) != -1)
            outliers = subset.filter(pl.col(cluster_col) == -1)
        else:
            valid = subset
            outliers = subset.head(0)  # empty

        # --- valid points ---
        if not valid.is_empty():
            values = valid[value_col].to_numpy()
            x_pos = dist + _jitter(len(values), jitter_width)
            ax.scatter(
                x_pos,
                values,
                label=terminal,
                color=color,
                alpha=alpha,
                s=marker_size,
                edgecolors="none",
                zorder=2,
            )

        # --- outlier points (grey x) ---
        if not outliers.is_empty():
            out_values = outliers[value_col].to_numpy()
            out_x = dist + _jitter(len(out_values), jitter_width)
            outlier_label = (
                "Outlier (DBSCAN)" if not outlier_legend_added else None
            )
            outlier_legend_added = True
            ax.scatter(
                out_x,
                out_values,
                label=outlier_label,
                color="#9E9E9E",
                alpha=0.75,
                s=marker_size * 1.8,
                marker=MarkerStyle("x"),
                linewidths=1.2,
                zorder=3,
            )

    ax.set_xlabel("Fractional line distance (p.u. of total length)")
    ax.set_ylabel("Overvoltage (P.U.)")
    ax.set_title("Phase-to-Ground Overvoltage vs. Line Position")
    ax.legend(title="Terminal", loc="lower left", fontsize=8)
    ax.grid(visible=True, linestyle="--", alpha=0.4, zorder=1)
    ax.set_xlim(-0.08, 1.08)

    return fig, ax


def plot_pdf_overlay(
    df: pl.DataFrame,
    ax: Axes | None = None,
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    terminal_distances: dict[str, float] | None = None,
    pdf_width: float = 0.08,
    n_points: int = 200,
) -> tuple[Figure, Axes]:
    """Overlay a rotated Gaussian PDF for each terminal on a scatter axes.

    The PDF is rendered as a horizontal curve anchored at the terminal's
    fractional distance.  Its width is scaled to *pdf_width* (fractional
    distance units) so it fits neatly between neighbouring terminals.

    Returns:
        A ``(figure, axes)`` tuple.
    """
    distances = terminal_distances or TERMINAL_DISTANCES

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        raw_fig = ax.get_figure()
        if raw_fig is None or not isinstance(raw_fig, Figure):
            fig, ax = plt.subplots(figsize=(10, 6))
        else:
            fig = raw_fig

    terminals: Sequence[str] = df[terminal_col].unique().sort().to_list()

    for terminal in terminals:
        subset = df.filter(pl.col(terminal_col) == terminal)
        if subset.is_empty():
            continue

        fit: GaussianFitResult = fit_gaussian(subset, value_col=value_col)
        dist = distances.get(terminal, 0.0)
        color = _terminal_color(terminal)

        # Generate y values spanning ±4σ around the mean.
        y_min = fit.mean - 4 * fit.std
        y_max = fit.mean + 4 * fit.std
        y_vals = np.linspace(y_min, y_max, n_points)

        # Evaluate PDF and normalise to [0, pdf_width].
        pdf_vals = stats.norm.pdf(y_vals, loc=fit.mean, scale=fit.std)
        if pdf_vals.max() > 0:
            pdf_normalised = pdf_vals / pdf_vals.max() * pdf_width
        else:
            pdf_normalised = pdf_vals

        # Draw PDF as a horizontal curve (x = distance ± normalised pdf).
        ax.fill_betweenx(
            y_vals,
            dist,
            # matplotlib-stubs 0.3.11 incorrectly restricts x2 to a scalar.
            dist + pdf_normalised,  # pyright: ignore[reportArgumentType]
            color=color,
            alpha=0.25,
            zorder=3,
        )
        ax.plot(
            dist + pdf_normalised,
            y_vals,
            color=color,
            linewidth=1.5,
            zorder=4,
        )

        # Mark mean and ±3σ lines.
        line_styles: tuple[tuple[int, Literal["solid", "dashed"]], ...] = (
            (0, "solid"),
            (3, "dashed"),
        )
        for n_sigma, linestyle in line_styles:
            level = fit.mean + n_sigma * fit.std
            ax.hlines(
                level,
                dist - 0.005,
                dist + pdf_width + 0.005,
                colors=[color],
                linestyles=linestyle,
                linewidth=0.9,
                alpha=0.7,
                zorder=5,
            )
            if n_sigma != 0:
                level_neg = fit.mean - n_sigma * fit.std
                ax.hlines(
                    level_neg,
                    dist - 0.005,
                    dist + pdf_width + 0.005,
                    colors=[color],
                    linestyles=linestyle,
                    linewidth=0.9,
                    alpha=0.7,
                    zorder=5,
                )

    return fig, ax


def plot_combined(
    df: pl.DataFrame,
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    cluster_col: str | None = None,
    terminal_distances: dict[str, float] | None = None,
    figsize: tuple[float, float] = (12, 7),
    jitter_width: float = 0.01,
    pdf_width: float = 0.07,
    alpha_scatter: float = 0.40,
    marker_size: float = 16.0,
) -> tuple[Figure, Axes]:
    """Generate one figure with scatter plot and Gaussian PDF overlays.

    Renders scatter points for raw overvoltage data and overlays the fitted
    Gaussian PDF for each terminal on the same axes, combining the outputs
    of :func:`plot_overvoltage_scatter` and :func:`plot_pdf_overlay`.

    When *cluster_col* is provided, DBSCAN outliers are highlighted on the
    scatter in grey rather than removed (see :func:`plot_overvoltage_scatter`).
    The PDF overlay is still fitted only to valid (non-outlier) points.

    Returns:
        A ``(figure, axes)`` tuple ready for ``plt.show()`` or saving.
    """
    fig, ax = plt.subplots(figsize=figsize)

    plot_overvoltage_scatter(
        df=df,
        ax=ax,
        terminal_col=terminal_col,
        value_col=value_col,
        cluster_col=cluster_col,
        terminal_distances=terminal_distances,
        jitter_width=jitter_width,
        alpha=alpha_scatter,
        marker_size=marker_size,
    )

    # PDF fits on valid points only.
    df_for_pdf = (
        df.filter(pl.col(cluster_col) != -1)
        if cluster_col is not None and cluster_col in df.columns
        else df
    )

    plot_pdf_overlay(
        df=df_for_pdf,
        ax=ax,
        terminal_col=terminal_col,
        value_col=value_col,
        terminal_distances=terminal_distances,
        pdf_width=pdf_width,
    )

    ax.set_title(
        "Overvoltage Distribution per Terminal with Gaussian PDF Overlay"
    )
    fig.tight_layout()
    return fig, ax


def plot_exceedance_curve(
    df: pl.DataFrame,
    fits: dict[str, GaussianFitResult],
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    cluster_col: str | None = None,
    figsize: tuple[float, float] = (11, 7),
    n_curve_points: int = 400,
) -> tuple[Figure, Axes]:
    """Plot exceedance probability P(X > x) per terminal.

    For each terminal, renders:
    - **Empirical** complementary CDF (1 - ECDF) as scatter dots,
      computed from all data points (valid + outliers if *cluster_col*
      is given).
    - **Fitted Gaussian** survival function as a smooth curve derived
      from the :class:`GaussianFitResult` in *fits*.
    - Vertical dashed lines at outlier values so their exceedance
      probability can be read directly from the y-axis.

    Args:
        fits: Per-terminal Gaussian fit results, keyed by terminal name.
            Typically the ``fits`` dict built during the pipeline.

    Returns:
        A ``(figure, axes)`` tuple.
    """
    fig, ax = plt.subplots(figsize=figsize)

    terminals: Sequence[str] = df[terminal_col].unique().sort().to_list()

    for terminal in terminals:
        subset = df.filter(pl.col(terminal_col) == terminal)
        fit = fits.get(terminal)
        if fit is None or subset.is_empty():
            continue

        color = _terminal_color(terminal)
        values = np.sort(subset[value_col].to_numpy())
        n = len(values)

        # Empirical exceedance: P(X > x[i]) ≈ (n - rank) / n
        ranks = np.arange(1, n + 1)
        ecdf_exceed = (n - ranks + 1) / n

        ax.scatter(
            values,
            ecdf_exceed,
            color=color,
            alpha=0.35,
            s=12,
            edgecolors="none",
            zorder=2,
            label=f"{terminal} (empirical)",
        )

        # Fitted Gaussian survival function (smooth curve)
        x_min = min(values.min(), fit.mean - 4 * fit.std)
        x_max = max(values.max(), fit.mean + 4 * fit.std)
        x_curve = np.linspace(x_min, x_max, n_curve_points)
        sf_curve = stats.norm.sf(x_curve, loc=fit.mean, scale=fit.std)

        ax.plot(
            x_curve,
            sf_curve,
            color=color,
            linewidth=2.0,
            zorder=3,
            label=f"{terminal} (Gaussian fit)",
        )

        # Vertical markers for outliers
        if cluster_col is not None and cluster_col in df.columns:
            outliers = subset.filter(pl.col(cluster_col) == -1)
            for row in outliers.iter_rows(named=True):
                v: float = row[value_col]
                p_exc = fit.exceedance_probability(v)
                ax.axvline(
                    v,
                    color=color,
                    linestyle=":",
                    linewidth=1.2,
                    alpha=0.8,
                    zorder=4,
                )
                ax.annotate(
                    f"{p_exc:.1e}",
                    xy=(v, p_exc),
                    xytext=(6, 4),
                    textcoords="offset points",
                    fontsize=7,
                    color=color,
                )

    ax.set_xlabel("Overvoltage (P.U.)")
    ax.set_ylabel("P(X > x)")
    ax.set_title(
        "Exceedance Probability per Terminal — Empirical vs. Gaussian Fit"
    )
    ax.legend(fontsize=7, ncols=2, loc="upper right")
    ax.grid(visible=True, linestyle="--", alpha=0.35)
    fig.tight_layout()
    return fig, ax
