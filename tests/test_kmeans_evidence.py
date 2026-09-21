"""Tests for contextual K-Means anomaly evidence."""

from collections.abc import Sequence

import pytest
from polars import DataFrame

from src.services.kmeans_evidence import evaluate_kmeans_evidence


def _observations(
    values: Sequence[float],
    *,
    terminals: Sequence[str] | None = None,
) -> DataFrame:
    row_count = len(values)
    return DataFrame({
        "observation_id": list(range(row_count)),
        "scenario": ["SRPI"] * row_count,
        "source_lineage": ["srpi-200"] * row_count,
        "terminal": terminals or ["T_OPO"] * row_count,
        "phase": ["A"] * row_count,
        "value_pu": values,
    })


def test_emits_distance_evidence_and_frozen_metadata() -> None:
    result = evaluate_kmeans_evidence(
        _observations([0.9, 1.0, 1.1, 2.9, 3.0, 3.1]),
        n_clusters=2,
        random_state=17,
    )

    assert result["method"].unique().to_list() == ["kmeans"]
    assert result["feature_space"].unique().to_list() == ["value_pu"]
    assert result["scaling_policy"].unique().to_list() == [
        "standard_scaler_fit_on_calibration_group"
    ]
    assert result["threshold_policy"].unique().to_list() == [
        "calibration_distance_percentile_99"
    ]
    assert result["random_state"].unique().to_list() == [17]
    assert result["n_clusters"].unique().to_list() == [2]
    assert result["parameter_source"].unique().to_list() == [
        "all_observations"
    ]
    assert result["configuration_id"].n_unique() == 1
    assert result["group_key"].n_unique() == 1
    assert result["score"].null_count() == 0
    assert result["threshold"].null_count() == 0
    assert result["applicability"].unique().to_list() == ["applicable"]


def test_upper_dense_cluster_membership_does_not_create_flags() -> None:
    result = evaluate_kmeans_evidence(
        _observations([0.9, 1.0, 1.1, 2.9, 3.0, 3.1]),
        n_clusters=2,
    )

    upper = result.filter(result["value_pu"] > 2.0)
    assert upper["kmeans_cluster"].n_unique() == 1
    assert upper["kmeans_cluster"].item(0) == 1
    assert upper["flag"].to_list() == [False, False, False]


def test_isolated_evaluation_point_can_exceed_development_threshold() -> None:
    observations = _observations([0.9, 1.0, 1.1, 2.9, 3.0, 3.1, 5.0])
    calibration_mask = [True, True, True, True, True, True, False]

    result = evaluate_kmeans_evidence(
        observations,
        n_clusters=2,
        calibration_mask=calibration_mask,
    )

    isolated = result.row(-1, named=True)
    assert isolated["flag"] is True
    assert isolated["score"] > isolated["threshold"]
    assert isolated["reason"] == "Distance exceeds calibrated threshold."
    assert result["parameter_source"].unique().to_list() == [
        "explicit_calibration_mask"
    ]


def test_models_terminal_offsets_within_separate_groups() -> None:
    observations = _observations(
        [0.9, 1.0, 1.1, 9.9, 10.0, 10.1],
        terminals=["T_MAN"] * 3 + ["T_OPO"] * 3,
    )

    result = evaluate_kmeans_evidence(observations, n_clusters=1)

    assert result["group_key"].n_unique() == 2
    assert result["flag"].to_list() == [False] * 6
    assert result["applicability"].unique().to_list() == ["applicable"]


def test_sparse_group_is_non_applicable_and_does_not_vote() -> None:
    result = evaluate_kmeans_evidence(_observations([1.0, 2.0]), n_clusters=2)

    assert result["kmeans_cluster"].to_list() == [None, None]
    assert result["score"].to_list() == [None, None]
    assert result["threshold"].to_list() == [None, None]
    assert result["flag"].to_list() == [None, None]
    assert result["applicability"].to_list() == [
        "non_applicable",
        "non_applicable",
    ]
    assert result["reason"].unique().to_list() == [
        "At least 3 calibration observations are required."
    ]


def test_constant_group_is_non_applicable() -> None:
    result = evaluate_kmeans_evidence(
        _observations([2.0, 2.0, 2.0, 2.0]), n_clusters=2
    )

    assert result["flag"].to_list() == [None] * 4
    assert result["applicability"].unique().to_list() == ["non_applicable"]
    assert result["reason"].unique().to_list() == [
        "Calibration values have zero variance."
    ]


def test_boolean_split_controls_calibration_and_preserves_order() -> None:
    observations = _observations([5.0, 0.9, 1.0, 1.1, 2.9, 3.0, 3.1])
    observations = observations.with_columns(
        DataFrame({"development": [False, True, True, True, True, True, True]})
    )

    result = evaluate_kmeans_evidence(
        observations,
        n_clusters=2,
        calibration_col="development",
    )

    assert result["observation_id"].to_list() == list(range(7))
    assert result.item(0, "flag") is True
    assert result["parameter_source"].unique().to_list() == [
        "calibration_column:development"
    ]


def test_result_is_deterministic() -> None:
    observations = _observations([0.8, 0.9, 1.0, 2.8, 2.9, 3.0, 5.0])
    mask = [True, True, True, True, True, True, False]

    first = evaluate_kmeans_evidence(
        observations, n_clusters=2, random_state=23, calibration_mask=mask
    )
    second = evaluate_kmeans_evidence(
        observations, n_clusters=2, random_state=23, calibration_mask=mask
    )

    assert first.equals(second)


def test_rejects_invalid_values_and_calibration_inputs() -> None:
    with pytest.raises(ValueError, match="value_pu must contain only finite"):
        evaluate_kmeans_evidence(_observations([1.0, float("nan"), 2.0]))

    observations = _observations([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="calibration_mask length"):
        evaluate_kmeans_evidence(observations, calibration_mask=[True])

    with pytest.raises(ValueError, match="mutually exclusive"):
        evaluate_kmeans_evidence(
            observations,
            calibration_mask=[True, True, True],
            calibration_col="development",
        )


def test_rejects_missing_comparable_group_column() -> None:
    observations = _observations([1.0, 2.0, 3.0]).drop("source_lineage")

    with pytest.raises(
        ValueError, match="Missing required columns: source_lineage"
    ):
        evaluate_kmeans_evidence(observations)
