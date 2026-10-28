"""Aggregate fitted partitions without mixing phases or refitting labels."""

from math import isfinite
from pathlib import Path

from matplotlib import pyplot
from polars import DataFrame, col, concat, lit, read_csv

from src.services.defense_visualization import (
    OKABE_ITO_PALETTE,
    export_publication_figure,
)


def export_clustering_comparison(output: Path) -> None:
    """Export all scope metrics, applicability counts and reference plots."""
    frames = []
    paths = (output / "runs").glob("*/*/*/clustering_comparison.csv")
    for path in sorted(paths):
        scenario, size, phase = path.parts[-4:-1]
        frames.append(
            read_csv(path).with_columns(
                lit(scenario.upper()).alias("scenario"),
                lit(int(size)).alias("sample_size"),
                lit(phase.upper()).alias("phase"),
                col("group_key")
                .str.extract(r"terminal=([^;]+)")
                .alias("terminal"),
            )
        )
    metrics = concat(frames).sort(
        "scenario", "sample_size", "terminal", "phase", "method"
    )
    metrics.write_csv(output / "sources" / "clustering_comparison.csv")
    summary = (
        metrics
        .group_by("scenario", "sample_size", "method")
        .agg(
            (col("applicability") == "applicable").sum().alias("applicable"),
            col("silhouette_score").median().alias("median_silhouette"),
            col("davies_bouldin_score")
            .median()
            .alias("median_davies_bouldin"),
            col("excluded_noise_count").sum().alias("excluded_noise_count"),
        )
        .sort("scenario", "sample_size", "method")
    )
    summary.write_csv(output / "tables" / "clustering_summary.csv")
    lines = [
        r"\begingroup\small",
        r"\setlength{\LTpre}{0pt}",
        r"\begin{longtable}{llrrrr}",
        r"\caption{Comparação geométrica por cenário e tamanho amostral. "
        r"Medianas somente entre grupos aplicáveis; A indica quantos dos "
        r"nove grupos terminal--fase são aplicáveis. NA: não aplicável. "
        r"Fonte: elaboração própria.}\label{tab:cluster-summary}\\",
        r"\hline Cenário & Método & $N$ & A/9 & Silhouette & DB \\",
        r"\hline\endfirsthead",
        r"\hline Cenário & Método & $N$ & A/9 & Silhouette & DB \\",
        r"\hline\endhead",
    ]
    names = {
        "kmeans": "K-Means",
        "dbscan": "DBSCAN",
        "hierarchical": "Hierárquico",
    }
    for row in summary.iter_rows(named=True):
        scores = [
            "NA" if row[key] is None else f"{row[key]:.4f}".replace(".", ",")
            for key in ("median_silhouette", "median_davies_bouldin")
        ]
        lines.append(
            f"{row['scenario']} & {names[row['method']]} & "
            f"{row['sample_size']:,} & {row['applicable']} & ".replace(
                ",", "."
            )
            + " & ".join(scores)
            + r" \\"
        )
    lines.extend([r"\hline", r"\end{longtable}", r"\endgroup"])
    (output / "tables" / "clustering_summary.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    export_clustering_figures(metrics, output / "figures")


def export_clustering_figures(metrics: DataFrame, output: Path) -> None:
    """Plot saved reference-group indices on shared scenario scales."""
    reference = metrics.filter(
        (col("terminal") == "T_OPO") & (col("phase") == "A")
    )
    methods = (
        ("kmeans", "K-Means", "o", "-", OKABE_ITO_PALETTE[4]),
        ("dbscan", "DBSCAN", "s", "--", OKABE_ITO_PALETTE[0]),
        ("hierarchical", "Hierárquico", "^", "-.", OKABE_ITO_PALETTE[2]),
    )
    specifications = (
        ("silhouette_score", "Silhouette (maior é melhor)"),
        ("davies_bouldin_score", "Davies–Bouldin (menor é melhor)"),
    )
    limits = []
    for key, _ in specifications:
        values = reference.filter(col("applicability") == "applicable")[key]
        finite = [float(v) for v in values if v is not None and isfinite(v)]
        low, high = (min(finite), max(finite)) if finite else (0.0, 1.0)
        margin = max((high - low) * 0.1, 0.025)
        limits.append((low - margin, high + margin))
    sizes = sorted(reference["sample_size"].unique().to_list())
    for scenario in ("SRPI", "CRPI"):
        figure, axes = pyplot.subplots(1, 2, figsize=(9, 4.6))
        for axis, (key, title), limit in zip(
            axes, specifications, limits, strict=True
        ):
            unavailable = []
            for method, name, marker, style, color in methods:
                selected = reference.filter(
                    (col("scenario") == scenario) & (col("method") == method)
                ).sort("sample_size")
                scores = [
                    float(value)
                    if applicable == "applicable"
                    and value is not None
                    and isfinite(value)
                    else float("nan")
                    for value, applicable in zip(
                        selected[key], selected["applicability"], strict=True
                    )
                ]
                missing = sum(not isfinite(value) for value in scores)
                if any(isfinite(value) for value in scores):
                    axis.plot(
                        selected["sample_size"],
                        scores,
                        marker=marker,
                        linestyle=style,
                        color=color,
                        label=name,
                    )
                if missing:
                    unavailable.append(
                        f"{name}: não aplicável em {missing}/{len(scores)} N"
                    )
            axis.set_xscale("log")
            axis.set_xticks(
                sizes, [f"{size:,}".replace(",", ".") for size in sizes]
            )
            axis.set_xlim(min(sizes) / 1.2, max(sizes) * 1.2)
            axis.set_ylim(limit)
            axis.set_xlabel("Número de simulações (N)", fontsize=11)
            axis.tick_params(labelsize=10)
            axis.set_title(title, fontsize=11)
            axis.grid(alpha=0.3)
            if axis.lines:
                axis.legend(fontsize=10)
            axis.text(
                0.0,
                -0.27,
                "\n".join(unavailable),
                transform=axis.transAxes,
                fontsize=10,
                va="top",
            )
        figure.suptitle(f"{scenario} — T_OPO, fase A")
        figure.tight_layout(rect=(0, 0.11, 1, 0.95))
        export_publication_figure(
            figure, output / f"clustering-{scenario.lower()}"
        )
        pyplot.close(figure)


def export_distribution_comparison(output: Path) -> None:
    """Collect each source's three-phase fits once, without duplicate runs."""
    paths = sorted((output / "runs").glob("*/*/a/distribution_comparison.csv"))
    fits = concat([read_csv(path) for path in paths]).sort(
        "scenario", "sample_size", "terminal", "phase", "model"
    )
    fits.write_csv(output / "sources" / "distribution_comparison.csv")
    selected = fits.filter(col("selected"))
    selected.group_by("scenario", "sample_size", "model").len().sort(
        "scenario", "sample_size", "model"
    ).write_csv(output / "tables" / "distribution_selection.csv")
