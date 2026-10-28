"""Smoke tests for source-first thesis-defense figures."""

from pathlib import Path

import matplotlib
import polars
import pytest
from PIL import Image

matplotlib.use("Agg")

from matplotlib import pyplot  # noqa: E402

from src.services.defense_visualization import (  # noqa: E402
    OKABE_ITO_PALETTE,
    FigureContext,
    export_publication_figure,
    plot_benchmark,
    plot_cluster_anomalies,
    plot_convergence,
    plot_distribution_qq,
    plot_method_agreement,
    plot_probability_comparison,
    plot_sensitivity,
)


@pytest.fixture
def context() -> FigureContext:
    return FigureContext(
        scenario="SRPI",
        sample_size=200,
        terminal="T_OPO",
        phase="A",
        method="K-Means",
        unit="p.u.",
        threshold=2.3,
        status="aplicável",
    )


def test_distribution_panel_has_histogram_density_and_qq(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "value_pu": [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
        "fitted_mean": [1.15] * 8,
        "fitted_standard_deviation": [0.244949] * 8,
        "adequacy_status": ["não rejeitada"] * 8,
    })

    figure, axes = plot_distribution_qq(source, context)
    try:
        assert len(axes) == 2
        assert axes[0].patches
        assert len(axes[0].lines) >= 2
        assert axes[1].collections
        assert "SRPI" in figure._suptitle.get_text()  # type: ignore[union-attr]
        assert "Adequação: não rejeitada" in axes[1].get_title()
    finally:
        pyplot.close(figure)


def test_probability_plot_shows_curves_ci_threshold_and_adequacy(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "threshold": [1.5, 2.0, 2.5],
        "empirical_probability": [0.4, 0.2, 0.05],
        "gaussian_probability": [0.38, 0.18, 0.03],
        "confidence_interval_lower": [0.3, 0.12, 0.01],
        "confidence_interval_upper": [0.5, 0.30, 0.12],
        "adequacy_status": ["descritiva"] * 3,
        "denominator": [200] * 3,
    })

    figure, axis = plot_probability_comparison(source, context)
    try:
        labels = {line.get_label() for line in axis.lines}
        assert {"Empírica", "Gaussiana", "Limiar: 2.3 p.u."} <= labels
        assert axis.collections
        assert "n = 200" in axis.get_title()
        assert "Adequação: descritiva" in axis.get_title()
        assert axis.get_ylabel() == "Probabilidade de excedência"
    finally:
        pyplot.close(figure)


def test_convergence_uses_common_scale_and_distinct_metrics(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "sample_size": [50, 100, 200, 1_000, 10_000],
        "mean": [1.1, 1.11, 1.12, 1.115, 1.113],
        "percentile_95": [1.3, 1.31, 1.32, 1.315, 1.313],
        "empirical_probability": [0.0] * 5,
        "confidence_interval_lower": [0.0] * 5,
        "confidence_interval_upper": [0.0713, 0.037, 0.019, 0.0038, 0.0004],
        "candidate_rate": [0.08, 0.07, 0.06, 0.055, 0.05],
        "coverage_status": ["present"] * 5,
        "independence_limitation": ["independência não estabelecida"] * 5,
    })
    comparison = source.with_columns(
        (polars.col("candidate_rate") * 2).alias("candidate_rate")
    )
    figure, axes = plot_convergence(
        source, context, comparison_source=polars.concat([source, comparison])
    )
    other, other_axes = plot_convergence(
        comparison,
        context,
        comparison_source=polars.concat([source, comparison]),
    )
    try:
        assert len(axes) == 3
        assert [line.get_ydata().tolist() for line in axes[0].lines] == [
            source["mean"].to_list(),
            source["percentile_95"].to_list(),
        ]
        assert axes[1].lines[0].get_ydata().tolist() == (
            source["candidate_rate"].to_list()
        )
        assert axes[1].get_ylim()[1] < 0.2
        assert axes[2].get_ylim()[1] > 0.0713
        segments = axes[2].collections[0].get_segments()
        assert [segment[:, 1].tolist() for segment in segments] == [
            [0.0, value] for value in source["confidence_interval_upper"]
        ]
        assert [axis.get_ylim() for axis in axes] == [
            axis.get_ylim() for axis in other_axes
        ]
        assert all(axis.get_xscale() == "log" for axis in axes)
        title = str(getattr(figure, "_suptitle").get_text())
        assert "50–10.000" in title
        assert "n=10000" not in title
        assert "convergência" not in title.lower()
    finally:
        pyplot.close(figure)
        pyplot.close(other)


def test_cluster_colors_remain_separate_from_anomaly_marker(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "simulation": [1, 2, 3, 4],
        "value_pu": [1.0, 1.1, 2.0, 2.8],
        "cluster": [0, 0, 1, 1],
        "anomaly_flag": [False, True, False, True],
        "score": [0.1, 0.9, 0.2, 1.2],
        "threshold": [0.8] * 4,
    })

    figure, axis = plot_cluster_anomalies(source, context)
    try:
        legend = axis.get_legend()
        assert legend is not None
        labels = {text.get_text() for text in legend.get_texts()}
        assert {"Cluster 0", "Cluster 1", "Candidato analítico"} <= labels
        assert len(axis.collections) == 3
        assert "cor = cluster descritivo" in axis.get_title()
        assert "marcador = evidência de anomalia" in axis.get_title()
    finally:
        pyplot.close(figure)


def test_method_agreement_keeps_disagreement_na_and_candidates(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "status": ["agreement", "disagreement", "non_applicable"],
        "count": [12, 3, 2],
        "candidate_count": [8, 2, 0],
    })

    figure, axis = plot_method_agreement(source, context)
    try:
        labels = [tick.get_text() for tick in axis.get_xticklabels()]
        assert labels == ["Concordância", "Discordância", "Não aplicável"]
        assert len(axis.patches) == 6
        assert axis.get_legend() is not None
    finally:
        pyplot.close(figure)


def test_benchmark_shows_method_intervention_intensity_and_na(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "intervention_family": ["point", "point", "collective"],
        "intervention_intensity": [1.0, 2.0, 1.0],
        "method": ["kmeans", "kmeans", "dbscan"],
        "recall": [0.6, 0.8, None],
        "benchmark_applicability": [
            "applicable",
            "applicable",
            "non_applicable",
        ],
    })

    figure, axis = plot_benchmark(source, context)
    try:
        assert axis.lines
        assert axis.collections
        assert "Intervenção controlada" in axis.get_title()
        assert "Não aplicável" in {
            text.get_text()
            for text in axis.get_legend().get_texts()  # type: ignore[union-attr]
        }
    finally:
        pyplot.close(figure)


def test_sensitivity_names_varied_parameter_controls_and_jaccard(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "varied_parameter": ["n_clusters"] * 3,
        "varied_value": [2, 3, 4],
        "fixed_controls": ["escala=standard; limiar=p99"] * 3,
        "identity_jaccard": [1.0, 0.85, 0.70],
        "stability_threshold": [0.80] * 3,
        "qualification": ["sensitive"] * 3,
        "applicability": ["applicable"] * 3,
    })

    figure, axis = plot_sensitivity(source, context)
    try:
        assert axis.get_xlabel() == "Parâmetro variado: n_clusters"
        assert axis.get_ylabel() == "Jaccard das identidades candidatas"
        assert "escala=standard; limiar=p99" in axis.get_title()
        assert "Sensível" in axis.get_title()
        assert len(axis.lines) == 2
    finally:
        pyplot.close(figure)


def test_export_writes_svg_and_png_at_publication_resolution(
    tmp_path: Path,
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "status": ["agreement", "disagreement", "non_applicable"],
        "count": [2, 1, 1],
        "candidate_count": [1, 1, 0],
    })
    figure, _axis = plot_method_agreement(source, context)
    try:
        exported = export_publication_figure(figure, tmp_path / "agreement")
    finally:
        pyplot.close(figure)

    assert exported.svg_path.exists()
    assert exported.png_path.exists()
    assert exported.dpi == 300
    assert "<svg" in exported.svg_path.read_text(encoding="utf-8")
    with Image.open(exported.png_path) as image:
        assert image.info["dpi"][0] >= 299


def test_palette_is_colorblind_safe_okabe_ito() -> None:
    assert OKABE_ITO_PALETTE[:4] == (
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
    )


def test_distribution_scenarios_share_bins_and_scales(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "value_pu": [0.8, 0.9, 1.0, 1.1],
        "fitted_mean": [0.95] * 4,
        "fitted_standard_deviation": [0.13] * 4,
        "adequacy_status": ["rejected"] * 4,
    })
    other = polars.DataFrame({
        "value_pu": [1.2, 1.3, 1.4, 1.5],
        "fitted_mean": [1.35] * 4,
        "fitted_standard_deviation": [0.13] * 4,
        "adequacy_status": ["not_rejected"] * 4,
    })
    comparison = polars.concat([source, other])
    first, axes = plot_distribution_qq(
        source, context, comparison_source=comparison
    )
    second, other_axes = plot_distribution_qq(
        other, context, comparison_source=comparison
    )
    try:
        assert [patch.get_x() for patch in axes[0].patches] == [
            patch.get_x() for patch in other_axes[0].patches
        ]
        for axis, other_axis in zip(axes, other_axes, strict=True):
            assert axis.get_xlim() == other_axis.get_xlim()
            assert axis.get_ylim() == other_axis.get_ylim()
        assert context.threshold is not None
        assert axes[0].get_xlim()[1] < context.threshold
        notes = " ".join(text.get_text() for text in getattr(first, "texts"))
        assert "2,3" in notes and "0/4" in notes
        assert "fora da janela" in notes
        assert "Adequação: rejeitada" in axes[1].get_title()
        assert "Adequação: não rejeitada" in other_axes[1].get_title()
        assert "Sobretensão (p.u.)" == axes[0].get_xlabel()
    finally:
        pyplot.close(first)
        pyplot.close(second)


def test_sample_size_candidate_labels_expose_small_rate_differences(
    context: FigureContext,
) -> None:
    source = polars.DataFrame({
        "sample_size": [200, 1_000, 10_000],
        "mean": [1.1] * 3,
        "percentile_95": [1.3] * 3,
        "candidate_rate": [0.01, 0.01, 0.0109],
        "empirical_probability": [0.0] * 3,
        "confidence_interval_lower": [0.0] * 3,
        "confidence_interval_upper": [0.0188, 0.0038, 0.000384],
        "coverage_status": ["present"] * 3,
        "independence_limitation": ["not established"] * 3,
    })
    figure, axes = plot_convergence(source, context)
    try:
        assert [text.get_text() for text in axes[1].texts] == [
            "1,00%",
            "1,00%",
            "1,09%",
        ]
    finally:
        pyplot.close(figure)
