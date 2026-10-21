"""Check scope identity and unavailable scores in defense summaries."""

from pathlib import Path

from polars import DataFrame, col, read_csv

from src.services.defense_clustering import export_clustering_comparison


def test_summary_preserves_unavailable_scores_and_noise(
    tmp_path: Path,
) -> None:
    for scenario in ("crpi", "srpi"):
        for phase in ("a", "b", "c"):
            run = tmp_path / "runs" / scenario / "50" / phase
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
    assert metrics["sample_size"].unique().to_list() == [50]
    kmeans = summary.filter(col("method") == "kmeans")
    assert kmeans["applicable"].to_list() == [9, 9]
    assert kmeans["median_silhouette"].to_list() == [0.7, 0.7]
    dbscan = summary.filter(col("method") == "dbscan")
    assert dbscan["applicable"].to_list() == [0, 0]
    assert dbscan["median_silhouette"].null_count() == 2
    assert dbscan["excluded_noise_count"].to_list() == [18, 18]
    latex = (tmp_path / "tables" / "clustering_summary.tex").read_text()
    assert "NA & NA" in latex
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
