"""Unit tests for deterministic clustering labels."""

import math

import polars as pl
import pytest

from src.services.clustering import (
    cluster_kmeans,
    detect_outliers_dbscan,
    detect_outliers_dbscan_per_terminal,
)


def _observations(values: list[float]) -> pl.DataFrame:
    return pl.DataFrame({
        "source_file": ["run.lis"] * len(values),
        "simulation": list(range(1, len(values) + 1)),
        "terminal": ["T_MAN"] * len(values),
        "phase": ["A"] * len(values),
        "value_pu": values,
        "time": [index / 100 for index in range(len(values))],
    })


def test_dbscan_labels_separated_cluster_and_noise() -> None:
    observations = _observations([1.0, 1.01, 1.02, 8.0])

    result = detect_outliers_dbscan(
        observations,
        eps=0.1,
        min_samples=2,
    )

    assert result.columns == [*observations.columns, "dbscan_cluster"]
    assert result["simulation"].to_list() == [1, 2, 3, 4]
    assert result["dbscan_cluster"].to_list() == [0, 0, 0, -1]
    assert result.schema["dbscan_cluster"] == pl.Int32


def test_dbscan_per_terminal_restores_exact_input_order() -> None:
    observations = pl.DataFrame({
        "row_id": [10, 20, 30, 40, 50],
        "terminal": ["T_MAN", "T_OPO", "T_MAN", "T_OPO", "T_MAN"],
        "value_pu": [1.0, 100.0, 1.01, 100.01, 8.0],
    })

    result = detect_outliers_dbscan_per_terminal(
        observations,
        eps=0.1,
        min_samples=2,
    )

    assert result["row_id"].to_list() == [10, 20, 30, 40, 50]
    assert result["dbscan_cluster"].to_list() == [0, 0, 0, 0, -1]


def test_dbscan_small_group_has_defined_noise_labels() -> None:
    observations = _observations([1.0, 1.1])

    result = detect_outliers_dbscan(
        observations,
        min_samples=3,
    )

    assert result["dbscan_cluster"].to_list() == [-1, -1]


def test_empty_inputs_return_declared_algorithm_columns() -> None:
    observations = _observations([])

    dbscan_result = detect_outliers_dbscan_per_terminal(observations)
    kmeans_result = cluster_kmeans(observations)

    assert dbscan_result.is_empty()
    assert dbscan_result.schema["dbscan_cluster"] == pl.Int32
    assert kmeans_result.is_empty()
    assert kmeans_result.schema["kmeans_cluster"] == pl.Int32


def test_kmeans_is_deterministic_with_centroid_ordered_labels() -> None:
    observations = _observations([10.0, 0.0, 10.1, 0.1])

    first = cluster_kmeans(observations, n_clusters=2, random_state=7)
    second = cluster_kmeans(observations, n_clusters=2, random_state=99)

    assert first["simulation"].to_list() == [1, 2, 3, 4]
    assert first["kmeans_cluster"].to_list() == [1, 0, 1, 0]
    assert second["kmeans_cluster"].to_list() == [1, 0, 1, 0]


@pytest.mark.parametrize("eps", [0.0, -0.1, math.nan, math.inf])
def test_dbscan_rejects_invalid_eps(eps: float) -> None:
    with pytest.raises(ValueError, match="eps must be finite and greater"):
        detect_outliers_dbscan(_observations([1.0]), eps=eps)


@pytest.mark.parametrize("min_samples", [0, -1, 1.5])
def test_dbscan_rejects_invalid_min_samples(
    min_samples: int | float,
) -> None:
    with pytest.raises(ValueError, match="min_samples must be an integer"):
        detect_outliers_dbscan(
            _observations([1.0]),
            min_samples=min_samples,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("n_clusters", [0, -1, 1.5])
def test_kmeans_rejects_invalid_cluster_count(
    n_clusters: int | float,
) -> None:
    with pytest.raises(ValueError, match="n_clusters must be an integer"):
        cluster_kmeans(
            _observations([1.0]),
            n_clusters=n_clusters,  # type: ignore[arg-type]
        )


def test_kmeans_rejects_cluster_count_above_row_count() -> None:
    with pytest.raises(ValueError, match="must not exceed the row count"):
        cluster_kmeans(_observations([1.0]), n_clusters=2)


@pytest.mark.parametrize("algorithm", ["dbscan", "kmeans"])
@pytest.mark.parametrize("invalid_value", [math.nan, math.inf, -math.inf])
def test_clustering_rejects_non_finite_values(
    algorithm: str,
    invalid_value: float,
) -> None:
    observations = _observations([1.0, invalid_value])

    with pytest.raises(ValueError, match="value_pu must contain only finite"):
        if algorithm == "dbscan":
            detect_outliers_dbscan(observations)
        else:
            cluster_kmeans(observations, n_clusters=1)
