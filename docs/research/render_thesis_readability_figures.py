"""Render the thesis benchmark summary from saved experimental evidence."""

from csv import DictReader
from pathlib import Path

from matplotlib import rc_context
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSET_DIRECTORY = PROJECT_ROOT / "doc" / "illustrations"
FAMILIES = (
    ("point", "Pontual"),
    ("contextual", "Contextual"),
    ("collective", "Coletiva"),
)
METHODS = (
    ("kmeans", "K-Means", "#0072B2", "o", "-"),
    ("dbscan_density_novelty", "DBSCAN por novidade", "#D55E00", "s", "--"),
)


def format_decimal(value: float, position: int | None = None) -> str:
    """Format axis values using the manuscript's decimal convention.

    Returns:
        Tick label with a decimal comma.
    """
    return f"{value:g}".replace(".", ",")


def draw_panel(
    axis: Axes,
    rows: list[dict[str, str]],
    family: str,
    title: str,
    metric: str,
) -> None:
    """Plot saved metrics for one intervention family."""
    for method, label, color, marker, style in METHODS:
        selected = sorted(
            (
                row
                for row in rows
                if row["intervention_family"] == family
                and row["method"] == method
            ),
            key=lambda row: float(row["requested_contamination_rate"]),
        )
        axis.plot(
            [
                100 * float(row["requested_contamination_rate"])
                for row in selected
            ],
            [float(row[metric]) for row in selected],
            label=label,
            color=color,
            marker=marker,
            linestyle=style,
            linewidth=1.6,
            markersize=6 if marker == "s" else 4.5,
            markerfacecolor="none" if marker == "s" else color,
        )
    axis.set_title(title, fontsize=11)
    axis.set_xticks([1, 5, 10])
    axis.set_yticks([0, 0.5, 1])
    axis.set_ylim(-0.04, 1.06)
    axis.yaxis.set_major_formatter(FuncFormatter(format_decimal))
    axis.grid(axis="y", alpha=0.25)
    axis.spines[["top", "right"]].set_visible(False)


def main() -> None:
    """Generate the figure without fitting models or rerunning experiments."""
    with (ASSET_DIRECTORY / "benchmark.csv").open(newline="") as source:
        rows = list(DictReader(source))
    with rc_context({"font.family": "DejaVu Sans", "font.size": 10}):
        figure = Figure(figsize=(6.9, 6.2))
        for row_index, (family, family_label) in enumerate(FAMILIES):
            for column_index, (metric, metric_label) in enumerate((
                ("precision", "precisão"),
                ("recall", "revocação"),
            )):
                axis = figure.add_subplot(
                    3, 2, row_index * 2 + column_index + 1
                )
                draw_panel(
                    axis,
                    rows,
                    family,
                    f"{family_label}: {metric_label}",
                    metric,
                )
                if row_index == 2:
                    axis.set_xlabel("Contaminação solicitada (%)")
        handles, labels = figure.axes[0].get_legend_handles_labels()
        figure.legend(
            handles, labels, loc="lower center", ncol=2, frameon=False
        )
        figure.subplots_adjust(
            left=0.08,
            right=0.98,
            top=0.95,
            bottom=0.14,
            hspace=0.55,
            wspace=0.25,
        )
        figure.savefig(
            ASSET_DIRECTORY / "benchmark-precision-recall.pdf",
            metadata={"CreationDate": None, "ModDate": None},
        )


if __name__ == "__main__":
    main()
