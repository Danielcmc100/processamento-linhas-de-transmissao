"""Unit tests for explicit anomaly-evidence comparison."""

import polars as pl
import pytest

from src.services.comparison import compare_anomaly_methods


def _annotated_observations() -> pl.DataFrame:
    return pl.DataFrame({
        "source_file": ["run.lis"] * 5,
        "simulation": [4, 1, 3, 2, 5],
        "terminal": ["T_MAN"] * 5,
        "phase": ["A"] * 5,
        "value_pu": [3.0, 1.0, 2.8, 1.1, 1.2],
        "time": [0.04, 0.01, 0.03, 0.02, 0.05],
        "dbscan_cluster": [-1, 0, 7, -1, None],
        "kmeans_cluster": [0, 1, 1, 9, None],
        "sigma_flag": [True, False, False, True, None],
        "sigma_applicability": [
            "applicable",
            "applicable",
            "applicable",
            "applicable",
            "non_applicable",
        ],
        "mad_flag": [True, False, True, False, None],
        "mad_applicability": [
            "applicable",
            "applicable",
            "applicable",
            "non_applicable",
            "non_applicable",
        ],
        "flag": [True, False, False, None, None],
        "applicability": [
            "applicable",
            "applicable",
            "applicable",
            "non_applicable",
            "non_applicable",
        ],
        "dbscan_flag": [True, False, True, False, None],
        "dbscan_applicability": [
            "applicable",
            "applicable",
            "applicable",
            "applicable",
            "non_applicable",
        ],
    })


def test_comparison_records_explicit_votes_and_preserves_identity() -> None:
    observations = _annotated_observations()

    result = compare_anomaly_methods(observations)

    assert result.columns == [
        *observations.columns,
        "method_agreement",
        "applicable_method_count",
        "method_disagreement",
        "anomaly_candidate",
        "anomaly_reasons",
    ]
    assert result["simulation"].to_list() == [4, 1, 3, 2, 5]
    assert result["method_agreement"].to_list() == [4, 0, 2, 1, 0]
    assert result["applicable_method_count"].to_list() == [4, 4, 4, 2, 0]
    assert result["method_disagreement"].to_list() == [
        False,
        False,
        True,
        True,
        False,
    ]
    assert result["anomaly_candidate"].to_list() == [
        True,
        False,
        True,
        True,
        False,
    ]


def test_reasons_list_only_met_explicit_criteria_in_stable_order() -> None:
    result = compare_anomaly_methods(_annotated_observations())

    assert result["anomaly_reasons"].to_list() == [
        "sigma_3;mad_modified_z;kmeans_distance;dbscan_noise",
        "",
        "mad_modified_z;dbscan_noise",
        "sigma_3",
        "",
    ]
    assert all(
        "error" not in reason and "physical" not in reason
        for reason in result["anomaly_reasons"]
    )


def test_cluster_labels_cannot_change_explicit_flags() -> None:
    observations = _annotated_observations()
    changed_labels = observations.with_columns(
        pl.Series("dbscan_cluster", [42, -1, -1, 0, 8]),
        pl.Series("kmeans_cluster", [99, 99, 99, 99, 99]),
    )

    baseline = compare_anomaly_methods(observations)
    changed = compare_anomaly_methods(changed_labels)

    output_columns = [
        "method_agreement",
        "applicable_method_count",
        "method_disagreement",
        "anomaly_candidate",
        "anomaly_reasons",
    ]
    assert changed.select(output_columns).equals(
        baseline.select(output_columns)
    )


def test_non_applicable_methods_do_not_vote_or_create_disagreement() -> None:
    result = compare_anomaly_methods(_annotated_observations())

    partly_applicable = result.filter(pl.col("simulation") == 2).row(
        0,
        named=True,
    )
    no_applicable = result.filter(pl.col("simulation") == 5).row(
        0,
        named=True,
    )

    assert partly_applicable["method_agreement"] == 1
    assert partly_applicable["applicable_method_count"] == 2
    assert partly_applicable["method_disagreement"] is True
    assert no_applicable["method_agreement"] == 0
    assert no_applicable["applicable_method_count"] == 0
    assert no_applicable["method_disagreement"] is False
    assert no_applicable["anomaly_candidate"] is False


@pytest.mark.parametrize(
    "missing_column",
    [
        "sigma_flag",
        "sigma_applicability",
        "mad_flag",
        "mad_applicability",
        "flag",
        "applicability",
        "dbscan_flag",
        "dbscan_applicability",
    ],
)
def test_comparison_rejects_missing_evidence_columns(
    missing_column: str,
) -> None:
    observations = _annotated_observations().drop(missing_column)

    with pytest.raises(
        ValueError,
        match=f"Required evidence column is missing: {missing_column}",
    ):
        compare_anomaly_methods(observations)


def test_comparison_rejects_non_boolean_flags() -> None:
    observations = _annotated_observations().with_columns(
        pl.col("mad_flag").cast(pl.Int8)
    )

    with pytest.raises(ValueError, match="mad_flag must be Boolean"):
        compare_anomaly_methods(observations)


def test_comparison_rejects_null_applicable_flag() -> None:
    observations = _annotated_observations().with_columns(
        pl
        .when(pl.col("simulation") == 1)
        .then(None)
        .otherwise(pl.col("dbscan_flag"))
        .alias("dbscan_flag")
    )

    with pytest.raises(
        ValueError,
        match="dbscan_flag must be Boolean when dbscan_applicability",
    ):
        compare_anomaly_methods(observations)


def test_comparison_rejects_true_non_applicable_flag() -> None:
    observations = _annotated_observations().with_columns(
        pl
        .when(pl.col("simulation") == 2)
        .then(True)
        .otherwise(pl.col("mad_flag"))
        .alias("mad_flag")
    )

    with pytest.raises(
        ValueError,
        match="mad_flag must not be true when mad_applicability",
    ):
        compare_anomaly_methods(observations)


def test_comparison_rejects_unknown_applicability_status() -> None:
    observations = _annotated_observations().with_columns(
        pl
        .when(pl.col("simulation") == 1)
        .then(pl.lit("unknown"))
        .otherwise(pl.col("applicability"))
        .alias("applicability")
    )

    with pytest.raises(
        ValueError,
        match="applicability must contain only applicable or non_applicable",
    ):
        compare_anomaly_methods(observations)


def test_empty_comparison_has_declared_output_schema() -> None:
    result = compare_anomaly_methods(_annotated_observations().clear())

    assert result.height == 0
    assert result.schema["method_agreement"] == pl.Int8
    assert result.schema["applicable_method_count"] == pl.Int8
    assert result.schema["method_disagreement"] == pl.Boolean
    assert result.schema["anomaly_candidate"] == pl.Boolean
    assert result.schema["anomaly_reasons"] == pl.String
