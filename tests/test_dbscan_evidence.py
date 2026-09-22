"""Tests for calibrated contextual DBSCAN evidence."""

from collections.abc import Sequence

import pytest
from polars import Boolean, DataFrame

from src.services.dbscan_evidence import evaluate_dbscan_evidence


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


def test_emits_calibrated_epsilon_and_group_diagnostics() -> None:
    result = evaluate_dbscan_evidence(
        _observations([0.9, 1.0, 1.1, 2.9, 3.0, 3.1]),
        min_samples=3,
    )

    assert result["dbscan_method"].unique().to_list() == ["dbscan"]
    assert result["dbscan_feature_space"].unique().to_list() == ["value_pu"]
    assert result["dbscan_scaling_policy"].unique().to_list() == [
        "standard_scaler_fit_on_calibration_group"
    ]
    assert result["dbscan_threshold_policy"].unique().to_list() == [
        "calibration_k_distance_percentile_95"
    ]
    assert result["dbscan_parameter_source"].unique().to_list() == [
        "all_observations"
    ]
    effective_eps = result.item(0, "dbscan_effective_eps")
    assert isinstance(effective_eps, float)
    assert effective_eps > 0.0
    assert result["dbscan_threshold"].equals(
        result["dbscan_effective_eps"], null_equal=True
    )
    assert result["dbscan_min_samples"].unique().to_list() == [3]
    assert result["dbscan_cluster_count"].unique().to_list() == [2]
    assert result["dbscan_noise_count"].unique().to_list() == [0]
    assert result["dbscan_noise_rate"].unique().to_list() == [0.0]
    assert result["dbscan_applicability"].unique().to_list() == ["applicable"]
    assert result["dbscan_configuration_id"].n_unique() == 1
    assert result["dbscan_group_key"].n_unique() == 1


def test_isolated_target_is_explicit_noise_evidence() -> None:
    observations = _observations([0.9, 1.0, 1.1, 2.9, 3.0, 3.1, 6.0])
    calibration_mask = [True, True, True, True, True, True, False]

    result = evaluate_dbscan_evidence(
        observations,
        min_samples=3,
        calibration_mask=calibration_mask,
    )

    isolated = result.row(-1, named=True)
    assert isolated["dbscan_cluster"] == -1
    assert isolated["dbscan_score"] > isolated["dbscan_threshold"]
    assert isolated["dbscan_flag"] is True
    assert isolated["dbscan_reason"] == "DBSCAN classified row as noise."
    assert isolated["dbscan_noise_count"] == 1
    assert isolated["dbscan_noise_rate"] == pytest.approx(1 / 7)
    assert isolated["dbscan_cluster_count"] == 2
    assert isolated["dbscan_parameter_source"] == ("explicit_calibration_mask")


def test_explicit_epsilon_policy_is_recorded() -> None:
    result = evaluate_dbscan_evidence(
        _observations([0.9, 1.0, 1.1, 2.9, 3.0, 3.1]),
        min_samples=2,
        effective_eps=0.25,
    )

    assert result["dbscan_effective_eps"].unique().to_list() == [0.25]
    assert result["dbscan_threshold_policy"].unique().to_list() == [
        "explicit_effective_eps"
    ]
    assert result["dbscan_parameter_source"].unique().to_list() == [
        "explicit_effective_eps"
    ]


def test_models_terminal_offsets_in_separate_groups() -> None:
    result = evaluate_dbscan_evidence(
        _observations(
            [0.9, 1.0, 1.1, 9.9, 10.0, 10.1],
            terminals=["T_MAN"] * 3 + ["T_OPO"] * 3,
        ),
        min_samples=2,
    )

    assert result["dbscan_group_key"].n_unique() == 2
    assert result["dbscan_flag"].to_list() == [False] * 6
    assert result["observation_id"].to_list() == list(range(6))


def test_sparse_group_is_non_applicable_and_does_not_vote() -> None:
    result = evaluate_dbscan_evidence(
        _observations([1.0, 1.1, 1.2]), min_samples=4
    )

    assert result["dbscan_cluster"].to_list() == [None] * 3
    assert result["dbscan_score"].to_list() == [None] * 3
    assert result["dbscan_threshold"].to_list() == [None] * 3
    assert result["dbscan_flag"].to_list() == [None] * 3
    assert result["dbscan_applicability"].unique().to_list() == [
        "non_applicable"
    ]
    assert result["dbscan_reason"].unique().to_list() == [
        "At least 4 calibration observations are required."
    ]


def test_constant_group_is_non_applicable() -> None:
    result = evaluate_dbscan_evidence(
        _observations([2.0, 2.0, 2.0, 2.0]), min_samples=2
    )

    assert result["dbscan_flag"].to_list() == [None] * 4
    assert result["dbscan_applicability"].unique().to_list() == [
        "non_applicable"
    ]
    assert result["dbscan_reason"].unique().to_list() == [
        "Calibration values have zero variance."
    ]


def test_all_noise_group_is_non_applicable_and_does_not_vote() -> None:
    result = evaluate_dbscan_evidence(
        _observations([0.0, 1.0, 2.0, 3.0]),
        min_samples=2,
        effective_eps=0.0001,
    )

    assert result["dbscan_cluster"].to_list() == [-1] * 4
    assert result["dbscan_noise_count"].unique().to_list() == [4]
    assert result["dbscan_noise_rate"].unique().to_list() == [1.0]
    assert result["dbscan_cluster_count"].unique().to_list() == [0]
    assert result["dbscan_flag"].to_list() == [None] * 4
    assert result["dbscan_applicability"].unique().to_list() == [
        "non_applicable"
    ]
    assert result["dbscan_reason"].unique().to_list() == [
        "DBSCAN classified every row as noise."
    ]


def test_calibration_column_preserves_original_row_order() -> None:
    observations = _observations([6.0, 0.9, 1.0, 1.1, 2.9, 3.0, 3.1])
    observations = observations.with_columns(
        DataFrame({"development": [False, True, True, True, True, True, True]})
        .to_series()
        .cast(Boolean)
    )

    result = evaluate_dbscan_evidence(
        observations,
        min_samples=3,
        calibration_col="development",
    )

    assert result["observation_id"].to_list() == list(range(7))
    assert result.item(0, "dbscan_flag") is True
    assert result["dbscan_parameter_source"].unique().to_list() == [
        "calibration_column:development"
    ]


def test_rejects_invalid_values_and_parameters() -> None:
    with pytest.raises(ValueError, match="value_pu must contain only finite"):
        evaluate_dbscan_evidence(_observations([1.0, float("nan")]))

    with pytest.raises(ValueError, match="min_samples must be an integer"):
        evaluate_dbscan_evidence(_observations([1.0, 2.0]), min_samples=0)

    with pytest.raises(ValueError, match="effective_eps must be finite"):
        evaluate_dbscan_evidence(_observations([1.0, 2.0]), effective_eps=0.0)


def test_rejects_missing_comparable_group_column() -> None:
    observations = _observations([1.0, 2.0, 3.0]).drop("source_lineage")

    with pytest.raises(
        ValueError, match="Missing required columns: source_lineage"
    ):
        evaluate_dbscan_evidence(observations)
