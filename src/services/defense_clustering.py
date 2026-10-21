"""Aggregate fitted partitions without mixing phases or refitting labels."""

from pathlib import Path

from matplotlib import pyplot
from polars import col, concat, lit, read_csv

from src.services.defense_visualization import export_publication_figure


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
            f"{row['sample_size']} & {row['applicable']} & "
            + " & ".join(scores)
            + r" \\"
        )
    lines.extend([r"\hline", r"\end{longtable}", r"\endgroup"])
    (output / "tables" / "clustering_summary.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    for scenario in ("SRPI", "CRPI"):
        figure, axes = pyplot.subplots(1, 2, figsize=(10, 4))
        for method, name in names.items():
            selected = metrics.filter(
                (col("scenario") == scenario)
                & (col("terminal") == "T_OPO")
                & (col("phase") == "A")
                & (col("method") == method)
            ).sort("sample_size")
            for axis, key, title in zip(
                axes,
                ("silhouette_score", "davies_bouldin_score"),
                (
                    "Silhouette (maior é melhor)",
                    "Davies–Bouldin (menor é melhor)",
                ),
                strict=True,
            ):
                axis.plot(
                    selected["sample_size"],
                    [float("nan") if v is None else v for v in selected[key]],
                    marker="o",
                    label=name,
                )
                axis.set_xscale("log")
                axis.set_xlabel("Número de simulações")
                axis.set_title(title)
                axis.grid(alpha=0.3)
        axes[0].legend()
        figure.suptitle(
            f"{scenario} — T_OPO, fase A — máximos em p.u.\n"
            "Ausência de ponto: métrica não aplicável"
        )
        figure.tight_layout()
        export_publication_figure(
            figure, output / "figures" / f"clustering-{scenario.lower()}"
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
