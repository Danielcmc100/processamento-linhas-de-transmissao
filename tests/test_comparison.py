"""Unit tests for statistical-versus-clustering comparison."""

import polars as pl
import pytest

from src.services.comparison import compare_anomaly_methods


def _annotated_observations() -> pl.DataFrame:
    return pl.DataFrame({
        "source_file": ["run.lis"] * 4,
        "simulation": [4, 1, 3, 2],
        "terminal": ["T_MAN"] * 4,
        "phase": ["A"] * 4,
        "value_pu": [3.0, 1.0, 2.8, 1.1],
        "time": [0.04, 0.01, 0.03, 0.02],
        "dbscan_cluster": [-1, 0, -1, 0],
        "kmeans_cluster": [1, 0, 0, 0],
        "sigma_flag": [True, False, False, True],
    })


def test_comparison_records_agreement_and_preserves_identity() -> None:
    observations = _annotated_observations()

    result = compare_anomaly_methods(observations)

    assert result.columns == [
        *observations.columns,
        "method_agreement",
        "anomaly_candidate",
        "anomaly_reasons",
    ]
    assert result["simulation"].to_list() == [4, 1, 3, 2]
    assert result["method_agreement"].to_list() == [3, 0, 1, 1]
    assert result["anomaly_candidate"].to_list() == [
        True,
        False,
        True,
        True,
    ]
    assert result["anomaly_reasons"].to_list() == [
        "sigma_3;dbscan_noise;kmeans_highest_centroid",
        "",
        "dbscan_noise",
        "sigma_3",
    ]
    assert result.schema["method_agreement"] == pl.Int8
    assert result.schema["anomaly_candidate"] == pl.Boolean
    assert result.schema["anomaly_reasons"] == pl.String


def test_comparison_exposes_method_disagreement_without_causation() -> None:
    result = compare_anomaly_methods(_annotated_observations())

    disagreement = result.filter(pl.col("simulation") == 3).row(
        0,
        named=True,
    )

    assert disagreement["method_agreement"] == 1
    assert disagreement["anomaly_candidate"] is True
    assert disagreement["anomaly_reasons"] == "dbscan_noise"
    assert "error" not in disagreement["anomaly_reasons"]
    assert "physical" not in disagreement["anomaly_reasons"]


@pytest.mark.parametrize(
    "missing_column",
    ["dbscan_cluster", "kmeans_cluster", "sigma_flag"],
)
def test_comparison_rejects_missing_method_labels(
    missing_column: str,
) -> None:
    observations = _annotated_observations().drop(missing_column)

    with pytest.raises(
        ValueError,
        match=f"Required method column is missing: {missing_column}",
    ):
        compare_anomaly_methods(observations)


def test_comparison_rejects_misleading_method_label_types() -> None:
    observations = _annotated_observations().with_columns(
        pl.col("sigma_flag").cast(pl.Int8)
    )

    with pytest.raises(ValueError, match="sigma_flag must be Boolean"):
        compare_anomaly_methods(observations)


def test_comparison_rejects_null_method_labels() -> None:
    observations = _annotated_observations().with_columns(
        pl.Series("dbscan_cluster", [-1, 0, None, 0], dtype=pl.Int64)
    )

    with pytest.raises(ValueError, match="must not contain null values"):
        compare_anomaly_methods(observations)
