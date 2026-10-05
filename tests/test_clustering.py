"""Unit tests for deterministic clustering labels."""

from math import inf, nan
from pathlib import Path

import pytest
from polars import DataFrame, Float64, Int32, String, read_csv

from src.services.clustering import (
    cluster_hierarchical,
    cluster_kmeans,
    detect_outliers_dbscan,
    detect_outliers_dbscan_per_terminal,
)


def _observations(values: list[float]) -> DataFrame:
    return DataFrame({
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
    assert result.schema["dbscan_cluster"] == Int32


def test_dbscan_per_terminal_restores_exact_input_order() -> None:
    observations = DataFrame({
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
    assert dbscan_result.schema["dbscan_cluster"] == Int32
    assert kmeans_result.is_empty()
    assert kmeans_result.schema["kmeans_cluster"] == Int32


def test_kmeans_is_deterministic_with_centroid_ordered_labels() -> None:
    observations = _observations([10.0, 0.0, 10.1, 0.1])

    first = cluster_kmeans(observations, n_clusters=2, random_state=7)
    second = cluster_kmeans(observations, n_clusters=2, random_state=99)

    assert first["simulation"].to_list() == [1, 2, 3, 4]
    assert first["kmeans_cluster"].to_list() == [1, 0, 1, 0]
    assert second["kmeans_cluster"].to_list() == [1, 0, 1, 0]


@pytest.mark.parametrize("eps", [0.0, -0.1, nan, inf])
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


def test_hierarchical_clusters_each_terminal_independently() -> None:
    observations = DataFrame({
        "row_id": list(range(8)),
        "terminal": ["T_MAN", "T_OPO"] * 4,
        "value_pu": [1.0, 2.0, 1.01, 2.01, 2.0, 3.0, 1.02, 2.02],
    })

    result = cluster_hierarchical(observations, max_tail_fraction=0.3)

    assert result["row_id"].to_list() == list(range(8))
    assert result["hierarchical_cluster"].to_list() == [0, 0, 0, 0, 1, 1, 0, 0]
    assert result.schema["hierarchical_cluster"] == Int32


def test_hierarchical_does_not_force_small_or_continuous_groups() -> None:
    for values in ([1.0, 2.0], [1.0] * 20, [1 + i / 20 for i in range(20)]):
        result = cluster_hierarchical(_observations(values))
        assert result["hierarchical_cluster"].to_list() == [0] * len(values)


def test_hierarchical_does_not_select_dense_upper_regime() -> None:
    observations = _observations(
        [1.0, 1.01] + [2 + i / 100 for i in range(18)]
    )

    result = cluster_hierarchical(observations)

    assert result["hierarchical_cluster"].to_list() == [0] * 20


def test_hierarchical_preserves_custom_columns_and_labels() -> None:
    observations = DataFrame({
        "node": ["T_MAN"] * 10,
        "voltage": [1.0] * 9 + [1.5],
        "_clustering_row_index": list(range(10)),
    })
    result = cluster_hierarchical(
        observations,
        terminal_col="node",
        value_col="voltage",
        label_col="upper_group",
    )
    assert result["upper_group"].to_list() == [0] * 9 + [1]
    assert result.drop("upper_group").equals(observations)


def test_hierarchical_empty_input_has_int32_labels() -> None:
    observations = DataFrame(schema={"terminal": String, "value_pu": Float64})
    result = cluster_hierarchical(observations)
    assert result.is_empty()
    assert result.schema["hierarchical_cluster"] == Int32


@pytest.mark.parametrize(
    ("parameter", "value"),
    [
        ("min_gap_pu", 0.0),
        ("min_gap_pu", nan),
        ("gap_factor", 0.5),
        ("gap_factor", inf),
        ("max_tail_fraction", 0.0),
        ("max_tail_fraction", 0.5),
    ],
)
def test_hierarchical_rejects_invalid_parameters(
    parameter: str,
    value: float,
) -> None:
    with pytest.raises(ValueError, match=parameter):
        if parameter == "min_gap_pu":
            cluster_hierarchical(_observations([1.0]), min_gap_pu=value)
        elif parameter == "gap_factor":
            cluster_hierarchical(_observations([1.0]), gap_factor=value)
        else:
            cluster_hierarchical(_observations([1.0]), max_tail_fraction=value)


@pytest.mark.parametrize("algorithm", ["dbscan", "kmeans", "hierarchical"])
@pytest.mark.parametrize("invalid_value", [nan, inf, -inf])
def test_clustering_rejects_non_finite_values(
    algorithm: str,
    invalid_value: float,
) -> None:
    observations = _observations([1.0, invalid_value])

    with pytest.raises(ValueError, match="value_pu must contain only finite"):
        if algorithm == "dbscan":
            detect_outliers_dbscan(observations)
        elif algorithm == "kmeans":
            cluster_kmeans(observations, n_clusters=1)
        else:
            cluster_hierarchical(observations)


def test_hierarchical_matches_marked_fifty_simulation_upper_tails() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "input_files/casos/50-simulacoes/resultados"
        / "annotated_observations.csv"
    )
    observations = read_csv(path).select("terminal", "value_pu")
    result = cluster_hierarchical(observations)
    for terminal, count in {"T_MAN": 1, "1_2LT": 3, "T_OPO": 0}.items():
        subset = result.filter(result["terminal"] == terminal)
        assert subset["hierarchical_cluster"].sum() == count
