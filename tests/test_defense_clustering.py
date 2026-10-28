"""Check scope identity and unavailable scores in defense summaries."""

from pathlib import Path

from matplotlib.figure import Figure
from polars import DataFrame, col, read_csv
from pytest import MonkeyPatch

from src.services.defense_clustering import export_clustering_comparison


def test_summary_preserves_unavailable_scores_and_noise(
    tmp_path: Path,
) -> None:
    for scenario in ("crpi", "srpi"):
        for phase in ("a", "b", "c"):
            run = tmp_path / "runs" / scenario / "10000" / phase
            run.mkdir(parents=True)
            records = []
            for terminal in ("T_MAN", "1_2LT", "T_OPO"):
                for method in ("kmeans", "dbscan", "hierarchical"):
                    available = method == "kmeans"
                    records.append({
                        "group_key": f"terminal={terminal};phase={phase}",
                        "method": method,
                        "applicability": (
                            "applicable" if available else "non_applicable"
                        ),
                        "silhouette_score": 0.7 if available else None,
                        "davies_bouldin_score": 0.4 if available else None,
                        "excluded_noise_count": 2 if method == "dbscan" else 0,
                    })
            DataFrame(records).write_csv(run / "clustering_comparison.csv")
    (tmp_path / "sources").mkdir()
    (tmp_path / "tables").mkdir()
    (tmp_path / "figures").mkdir()

    export_clustering_comparison(tmp_path)

    metrics = read_csv(tmp_path / "sources" / "clustering_comparison.csv")
    summary = read_csv(tmp_path / "tables" / "clustering_summary.csv")
    assert metrics.height == 54
    assert set(metrics["phase"]) == {"A", "B", "C"}
    assert set(metrics["terminal"]) == {"T_MAN", "1_2LT", "T_OPO"}
    assert metrics["sample_size"].unique().to_list() == [10000]
    kmeans = summary.filter(col("method") == "kmeans")
    assert kmeans["applicable"].to_list() == [9, 9]
    assert kmeans["median_silhouette"].to_list() == [0.7, 0.7]
    dbscan = summary.filter(col("method") == "dbscan")
    assert dbscan["applicable"].to_list() == [0, 0]
    assert dbscan["median_silhouette"].null_count() == 2
    assert dbscan["excluded_noise_count"].to_list() == [18, 18]
    latex = (tmp_path / "tables" / "clustering_summary.tex").read_text()
    assert "NA & NA" in latex
    assert "10.000" in latex
    assert "0,7000" in latex
    assert (tmp_path / "figures" / "clustering-crpi.png").is_file()


def test_distribution_export_does_not_repeat_three_phase_fits(
    tmp_path: Path,
) -> None:
    from src.services.defense_clustering import export_distribution_comparison

    fits = DataFrame({
        "scenario": ["CRPI", "CRPI", "CRPI"],
        "sample_size": [50, 50, 50],
        "terminal": ["T_MAN", "T_MAN", "T_MAN"],
        "phase": ["A", "B", "C"],
        "model": ["gamma", "normal", "lognormal"],
        "selected": [True, True, True],
    })
    for phase in ("a", "b", "c"):
        run = tmp_path / "runs" / "crpi" / "50" / phase
        run.mkdir(parents=True)
        fits.write_csv(run / "distribution_comparison.csv")
    (tmp_path / "sources").mkdir()
    (tmp_path / "tables").mkdir()

    export_distribution_comparison(tmp_path)

    exported = read_csv(tmp_path / "sources" / "distribution_comparison.csv")
    counts = read_csv(tmp_path / "tables" / "distribution_selection.csv")
    assert exported.height == 3
    assert counts["len"].sum() == 3


def test_reference_figures_share_scales_and_show_missing_scores(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    from src.services.defense_clustering import export_clustering_figures

    records = []
    for scenario, offset in (("SRPI", 0.0), ("CRPI", 0.3)):
        for method in ("kmeans", "dbscan", "hierarchical"):
            for size in (50, 100, 200):
                available = method == "kmeans" and size != 100
                records.append({
                    "scenario": scenario,
                    "terminal": "T_OPO",
                    "phase": "A",
                    "method": method,
                    "sample_size": size,
                    "applicability": (
                        "applicable" if available else "non_applicable"
                    ),
                    "silhouette_score": 0.4 + offset if available else None,
                    "davies_bouldin_score": (
                        0.2 + offset if available else None
                    ),
                })
    # A different group must not affect reference scales or plotted series.
    records.append({
        **records[0],
        "terminal": "T_MAN",
        "silhouette_score": 99.0,
        "davies_bouldin_score": 99.0,
    })
    figures: dict[str, Figure] = {}

    def capture(figure: Figure, output: Path) -> None:
        figures[output.name] = figure

    monkeypatch.setattr(
        "src.services.defense_clustering.export_publication_figure", capture
    )
    export_clustering_figures(DataFrame(records), tmp_path)
    first = figures["clustering-srpi"]
    second = figures["clustering-crpi"]
    for left, right in zip(first.axes, second.axes, strict=True):
        assert left.get_ylim() == right.get_ylim()
        assert left.get_xlim() == right.get_xlim()
        assert left.get_ylim()[1] < 2.0
        assert [line.get_label() for line in left.lines] == ["K-Means"]
        assert left.lines[0].get_color() == right.lines[0].get_color()
        assert left.lines[0].get_marker() == right.lines[0].get_marker()
        assert str(left.lines[0].get_ydata()[1]) == "nan"
        assert "DBSCAN" not in left.get_legend_handles_labels()[1]
        assert "DBSCAN" in " ".join(t.get_text() for t in left.texts)
        assert "não aplicável" in " ".join(t.get_text() for t in left.texts)
    assert "T_OPO" in getattr(first, "texts")[0].get_text()
    assert "fase A" in getattr(first, "texts")[0].get_text()
