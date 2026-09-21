"""Unit tests for controlled anomaly benchmark metrics."""

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from src.services.benchmark import summarize_controlled_benchmark


def _evidence() -> pl.DataFrame:
    return pl.DataFrame({
        "intervention_family": [
            "point",
            "point",
            "point",
            "point",
            "point",
            "point",
            "clean",
            "clean",
            "contextual",
            "contextual",
            "collective",
            "collective",
        ],
        "intervention_intensity": [
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.0,
            0.0,
            2.0,
            2.0,
            3.0,
            3.0,
        ],
        "method": [
            "kmeans",
            "kmeans",
            "kmeans",
            "kmeans",
            "kmeans",
            "kmeans",
            "sigma",
            "sigma",
            "mad",
            "mad",
            "dbscan",
            "dbscan",
        ],
        "controlled_label": [
            True,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            False,
            True,
            True,
        ],
        "flag": [
            True,
            False,
            True,
            False,
            False,
            False,
            False,
            False,
            None,
            None,
            True,
            False,
        ],
        "applicability": [
            "applicable",
            "applicable",
            "applicable",
            "applicable",
            "applicable",
            "applicable",
            "applicable",
            "applicable",
            "non_applicable",
            "non_applicable",
            "applicable",
            "applicable",
        ],
    })


def test_benchmark_reports_counts_before_safe_metrics() -> None:
    result = summarize_controlled_benchmark(_evidence())

    assert result.columns[:12] == [
        "intervention_family",
        "intervention_intensity",
        "method",
        "row_count",
        "applicable_count",
        "excluded_count",
        "true_positive",
        "false_positive",
        "true_negative",
        "false_negative",
        "precision",
        "recall",
    ]
    point = result.filter(
        (pl.col("intervention_family") == "point")
        & (pl.col("method") == "kmeans")
    ).row(0, named=True)
    assert point["row_count"] == 6
    assert point["applicable_count"] == 6
    assert point["excluded_count"] == 0
    assert point["true_positive"] == 1
    assert point["false_positive"] == 1
    assert point["true_negative"] == 3
    assert point["false_negative"] == 1
    assert point["precision"] == pytest.approx(0.5)
    assert point["recall"] == pytest.approx(0.5)
    assert point["f1"] == pytest.approx(0.5)
    assert point["false_positive_rate"] == pytest.approx(0.25)


def test_benchmark_is_deterministically_sorted() -> None:
    evidence = _evidence()
    reversed_evidence = evidence.reverse()

    first = summarize_controlled_benchmark(evidence)
    second = summarize_controlled_benchmark(reversed_evidence)

    assert_frame_equal(first, second)
    assert first.select(
        "intervention_family",
        "intervention_intensity",
        "method",
    ).rows() == sorted(
        first.select(
            "intervention_family",
            "intervention_intensity",
            "method",
        ).rows()
    )


def test_confusion_counts_match_independent_recomputation() -> None:
    evidence = _evidence().filter(
        (pl.col("intervention_family") == "point")
        & (pl.col("method") == "kmeans")
    )
    row = summarize_controlled_benchmark(evidence).row(0, named=True)
    pairs = evidence.select("controlled_label", "flag").iter_rows()

    expected = {
        "true_positive": sum(truth and flag for truth, flag in pairs),
        "false_positive": sum(
            not truth and flag
            for truth, flag in evidence.select(
                "controlled_label", "flag"
            ).iter_rows()
        ),
        "true_negative": sum(
            not truth and not flag
            for truth, flag in evidence.select(
                "controlled_label", "flag"
            ).iter_rows()
        ),
        "false_negative": sum(
            truth and not flag
            for truth, flag in evidence.select(
                "controlled_label", "flag"
            ).iter_rows()
        ),
    }
    for column, count in expected.items():
        assert row[column] == count


def test_zero_denominators_are_null_with_explicit_reasons() -> None:
    result = summarize_controlled_benchmark(_evidence())
    clean = result.filter(pl.col("intervention_family") == "clean").row(
        0,
        named=True,
    )
    collective = result.filter(
        pl.col("intervention_family") == "collective"
    ).row(0, named=True)

    assert clean["precision"] is None
    assert clean["precision_applicability"] == "non_applicable"
    assert clean["precision_reason"] == "No predicted positive observations."
    assert clean["recall"] is None
    assert clean["recall_reason"] == "No positive controlled observations."
    assert clean["f1"] is None
    assert clean["f1_reason"] == (
        "No true or predicted positive observations."
    )
    assert clean["false_positive_rate"] == 0.0
    assert collective["false_positive_rate"] is None
    assert collective["false_positive_rate_applicability"] == (
        "non_applicable"
    )
    assert collective["false_positive_rate_reason"] == (
        "No negative controlled observations."
    )


def test_non_applicable_rows_are_excluded_from_counts_and_metrics() -> None:
    row = (
        summarize_controlled_benchmark(_evidence())
        .filter(pl.col("intervention_family") == "contextual")
        .row(0, named=True)
    )

    assert row["row_count"] == 2
    assert row["applicable_count"] == 0
    assert row["excluded_count"] == 2
    assert row["true_positive"] == 0
    assert row["false_positive"] == 0
    assert row["true_negative"] == 0
    assert row["false_negative"] == 0
    assert row["benchmark_applicability"] == "non_applicable"
    assert row["benchmark_reason"] == "No applicable method results."
    assert row["precision"] is None
    assert row["recall"] is None
    assert row["f1"] is None
    assert row["false_positive_rate"] is None


@pytest.mark.parametrize(
    "missing_column",
    [
        "intervention_family",
        "intervention_intensity",
        "method",
        "controlled_label",
        "flag",
        "applicability",
    ],
)
def test_benchmark_rejects_missing_columns(missing_column: str) -> None:
    with pytest.raises(
        ValueError,
        match=f"Required benchmark column is missing: {missing_column}",
    ):
        summarize_controlled_benchmark(_evidence().drop(missing_column))


def test_benchmark_rejects_invalid_flag_state() -> None:
    invalid = _evidence().with_columns(
        pl
        .when(pl.col("intervention_family") == "contextual")
        .then(True)
        .otherwise(pl.col("flag"))
        .alias("flag")
    )

    with pytest.raises(
        ValueError,
        match="flag must not be true when applicability is non_applicable",
    ):
        summarize_controlled_benchmark(invalid)


def test_empty_benchmark_has_declared_schema() -> None:
    result = summarize_controlled_benchmark(_evidence().clear())

    assert result.is_empty()
    assert result.schema["true_positive"] == pl.Int64
    assert result.schema["precision"] == pl.Float64
    assert result.schema["precision_reason"] == pl.String
