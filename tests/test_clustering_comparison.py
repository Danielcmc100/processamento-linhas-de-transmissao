"""Tests for internal clustering comparison metrics."""

from polars import DataFrame

from src.services.clustering_comparison import evaluate_cluster_comparison


def _observations(
    *,
    kmeans_labels: list[int | None],
    dbscan_labels: list[int | None],
    hierarchical_labels: list[int | None],
) -> DataFrame:
    values = [0.0, 0.1, 3.0, 3.1, 3.2]
    return DataFrame({
        "scenario": ["SRPI"] * len(values),
        "source_lineage": ["test"] * len(values),
        "terminal": ["T_MAN"] * len(values),
        "phase": ["A"] * len(values),
        "value_pu": values,
        "kmeans_cluster": kmeans_labels,
        "dbscan_cluster": dbscan_labels,
        "hierarchical_cluster": hierarchical_labels,
    })


def test_comparison_scores_separated_kmeans_and_dbscan_clusters() -> None:
    result = evaluate_cluster_comparison(
        _observations(
            kmeans_labels=[0, 0, 1, 1, 1],
            dbscan_labels=[0, 0, 1, 1, -1],
            hierarchical_labels=[0, 0, 0, 0, 1],
        ),
        grouping_policy=("scenario", "source_lineage", "terminal", "phase"),
    )

    kmeans = result.filter(result["method"] == "kmeans").row(0, named=True)
    dbscan = result.filter(result["method"] == "dbscan").row(0, named=True)
    hierarchical = result.filter(result["method"] == "hierarchical").row(
        0, named=True
    )

    assert kmeans["applicability"] == "applicable"
    assert kmeans["silhouette_score"] is not None
    assert kmeans["silhouette_score"] > 0.9
    assert kmeans["davies_bouldin_score"] is not None
    assert kmeans["davies_bouldin_score"] < 0.1
    assert dbscan["applicability"] == "applicable"
    assert dbscan["evaluated_count"] == 4
    assert dbscan["excluded_noise_count"] == 1
    assert hierarchical["applicability"] == "non_applicable"
    assert hierarchical["reason"] == (
        "Each retained cluster requires at least two observations."
    )


def test_comparison_marks_one_cluster_and_missing_labels_non_applicable() -> (
    None
):
    result = evaluate_cluster_comparison(
        _observations(
            kmeans_labels=[0, 0, 0, 0, 0],
            dbscan_labels=[-1, -1, -1, -1, -1],
            hierarchical_labels=[None, None, None, None, None],
        ),
        grouping_policy=("scenario", "source_lineage", "terminal", "phase"),
    )

    assert result["applicability"].to_list() == [
        "non_applicable",
        "non_applicable",
        "non_applicable",
    ]
    assert result["reason"].to_list() == [
        "At least two retained clusters are required.",
        "At least two retained clusters are required.",
        "At least two retained clusters are required.",
    ]
