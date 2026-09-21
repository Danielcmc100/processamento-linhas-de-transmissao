"""Tests for compatible cross-sample and method-comparison evidence."""

import polars
import pytest

from src.services.convergence import (
    build_convergence_table,
    build_method_comparison_matrix,
)

_SIZES = [50, 100, 200, 1_000, 10_000]


def _convergence_evidence(
    sizes: list[int] | None = None,
) -> polars.DataFrame:
    selected_sizes = sizes or _SIZES
    probabilities = {
        50: 0.2,
        100: 0.1,
        200: 0.08,
        1_000: 0.07,
        10_000: 0.069,
    }
    return polars.DataFrame({
        "scenario": ["SRPI"] * len(selected_sizes),
        "sample_size": selected_sizes,
        "base_voltage": [112677.0] * len(selected_sizes),
        "terminal": ["T_OPO"] * len(selected_sizes),
        "phase": ["A"] * len(selected_sizes),
        "event_definition": ["value_pu > 2 p.u."] * len(selected_sizes),
        "comparison_operator": [">"] * len(selected_sizes),
        "threshold": [2.0] * len(selected_sizes),
        "grouping_policy": ["scenario|source_lineage|terminal|phase"]
        * len(selected_sizes),
        "method_policy": ["frozen-v1"] * len(selected_sizes),
        "relationship_status": ["independence_not_established"]
        * len(selected_sizes),
        "mean": [1.8 + size / 1_000_000 for size in selected_sizes],
        "sample_standard_deviation": [0.2] * len(selected_sizes),
        "median": [1.75] * len(selected_sizes),
        "percentile_90": [2.1] * len(selected_sizes),
        "percentile_95": [2.2] * len(selected_sizes),
        "percentile_99": [2.4] * len(selected_sizes),
        "empirical_probability": [
            probabilities[size] for size in selected_sizes
        ],
        "confidence_interval_lower": [0.05] * len(selected_sizes),
        "confidence_interval_upper": [0.25] * len(selected_sizes),
        "fitted_model_status": ["not_rejected"] * len(selected_sizes),
        "candidate_count": [10, 10, 16, 70, 690][: len(selected_sizes)],
        "candidate_rate": [0.2, 0.1, 0.08, 0.07, 0.069][: len(selected_sizes)],
    })


def _method_evidence() -> polars.DataFrame:
    return polars.DataFrame({
        "scenario": ["SRPI", "SRPI"],
        "sample_size": [50, 50],
        "source_lineage": ["line-1", "line-1"],
        "simulation": [1, 1],
        "terminal": ["T_MAN", "T_MAN"],
        "terminal_position_km": [0.0, 0.0],
        "phase": ["A", "B"],
        "event_definition": ["absolute maximum"] * 2,
        "sigma_flag": [True, False],
        "sigma_applicability": ["applicable", "non_applicable"],
        "sigma_reason": ["Above 3 sigma.", "Fit rejected."],
        "mad_flag": [True, False],
        "mad_applicability": ["applicable", "applicable"],
        "mad_reason": ["Modified score above 3.5.", None],
        "flag": [False, False],
        "applicability": ["applicable", "applicable"],
        "reason": [None, None],
        "dbscan_flag": [True, False],
        "dbscan_applicability": ["applicable", "applicable"],
        "dbscan_reason": ["Noise point.", None],
        "method_agreement": [3, 0],
        "applicable_method_count": [4, 3],
        "method_disagreement": [True, False],
        "anomaly_candidate": [True, False],
        "anomaly_reasons": [
            "sigma_3;mad_modified_z;dbscan_noise",
            "",
        ],
    })


def test_convergence_reports_all_metrics_deltas_and_reference_role() -> None:
    result = build_convergence_table(_convergence_evidence())

    assert result["sample_size"].to_list() == _SIZES
    row = result.filter(polars.col("sample_size") == 100).row(0, named=True)
    assert row["confidence_interval_width"] == pytest.approx(0.2)
    assert row["previous_sample_size"] == 50
    assert row["empirical_probability_absolute_delta"] == pytest.approx(-0.1)
    assert row["empirical_probability_relative_delta"] == pytest.approx(-0.5)
    assert row["candidate_count"] == 10
    assert row["candidate_rate"] == pytest.approx(0.1)
    assert row["fitted_model_status"] == "not_rejected"

    reference = result.filter(polars.col("sample_size") == 10_000).row(
        0, named=True
    )
    assert reference["reference_role"] == "high_sample_empirical_reference"
    assert reference["reference_limitation"] == (
        "High-sample empirical reference; not ground truth."
    )


def test_relative_delta_is_null_when_previous_value_is_zero() -> None:
    evidence = _convergence_evidence().with_columns(
        polars
        .when(polars.col("sample_size") == 50)
        .then(0.0)
        .otherwise(polars.col("empirical_probability"))
        .alias("empirical_probability")
    )

    row = (
        build_convergence_table(evidence)
        .filter(polars.col("sample_size") == 100)
        .row(0, named=True)
    )

    assert row["empirical_probability_absolute_delta"] == pytest.approx(0.1)
    assert row["empirical_probability_relative_delta"] is None
    assert row["empirical_probability_relative_delta_reason"] == (
        "Previous value is zero."
    )


def test_missing_size_and_independence_limitation_are_explicit() -> None:
    result = build_convergence_table(
        _convergence_evidence([50, 200, 1_000, 10_000])
    )

    missing = result.filter(polars.col("sample_size") == 100).row(
        0, named=True
    )
    assert missing["coverage_status"] == "missing"
    assert missing["comparison_status"] == "incomplete"
    assert missing["mean"] is None
    assert missing["coverage_reason"] == (
        "Required sample size 100 is missing."
    )
    assert set(result["independence_limitation"]) == {
        "Dataset independence is not established; comparisons describe "
        "sampling consistency only."
    }


@pytest.mark.parametrize(
    ("column", "replacement", "message"),
    [
        ("base_voltage", 100000.0, "accepted base voltage"),
        ("threshold", 2.3, "threshold"),
        ("grouping_policy", "terminal|phase", "grouping_policy"),
        ("method_policy", "changed-v2", "method_policy"),
    ],
)
def test_rejects_incompatible_convergence_rows(
    column: str,
    replacement: object,
    message: str,
) -> None:
    evidence = _convergence_evidence().with_columns(
        polars
        .when(polars.col("sample_size") == 100)
        .then(polars.lit(replacement))
        .otherwise(polars.col(column))
        .alias(column)
    )

    with pytest.raises(ValueError, match=message):
        build_convergence_table(evidence)


def test_method_matrix_preserves_identity_status_reason_and_scope() -> None:
    evidence = _method_evidence()

    result = build_method_comparison_matrix(
        evidence,
        analysis_mode="exploratory",
        multiplicity_qualification=(
            "No inferential family-wise claim is made."
        ),
    )

    assert result.select(evidence.columns).equals(evidence)
    assert set(result["analysis_mode"]) == {"exploratory"}
    assert set(result["multiplicity_qualification"]) == {
        "No inferential family-wise claim is made."
    }
    assert result.item(0, "sigma_reason") == "Above 3 sigma."
    assert result.item(1, "sigma_applicability") == "non_applicable"
    assert result.select("simulation", "terminal", "phase").rows() == [
        (1, "T_MAN", "A"),
        (1, "T_MAN", "B"),
    ]


def test_inferential_matrix_requires_multiplicity_qualification() -> None:
    with pytest.raises(ValueError, match="multiplicity qualification"):
        build_method_comparison_matrix(
            _method_evidence(),
            analysis_mode="inferential",
            multiplicity_qualification="",
        )


def test_method_matrix_rejects_missing_explicit_method_reason() -> None:
    with pytest.raises(ValueError, match="dbscan_reason"):
        build_method_comparison_matrix(
            _method_evidence().drop("dbscan_reason")
        )
