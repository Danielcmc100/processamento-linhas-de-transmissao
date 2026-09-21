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
        "empirical_probability": [0.12, 0.10, 0.09, 0.08, 0.075],
        "candidate_rate": [0.08, 0.07, 0.06, 0.055, 0.05],
        "coverage_status": ["present"] * 5,
        "independence_limitation": ["independência não estabelecida"] * 5,
    })

    figure, axis = plot_convergence(source, context)
    try:
        assert len(axis.lines) == 2
        assert {line.get_marker() for line in axis.lines} == {"o", "s"}
        assert "escala comum" in axis.get_title().lower()
        assert "independência não estabelecida" in axis.get_title()
        assert axis.get_xscale() == "log"
    finally:
        pyplot.close(figure)


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
