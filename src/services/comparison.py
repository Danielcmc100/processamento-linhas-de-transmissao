"""Comparison of explicit, applicable anomaly evidence.

Results identify analytical candidates only. They do not establish numerical
errors or physical causes. Cluster labels remain descriptive and never vote.
"""

from polars import (
    Boolean,
    DataFrame,
    Expr,
    Int8,
    String,
    col,
    concat_str,
    lit,
    when,
)

_METHODS = (
    ("sigma_flag", "sigma_applicability", "sigma_3"),
    ("mad_flag", "mad_applicability", "mad_modified_z"),
    ("flag", "applicability", "kmeans_distance"),
    ("dbscan_flag", "dbscan_applicability", "dbscan_noise"),
)
_APPLICABLE = "applicable"
_NON_APPLICABLE = "non_applicable"


def compare_anomaly_methods(df: DataFrame) -> DataFrame:
    """Compare applicable Boolean evidence without reading cluster labels.

    ``method_agreement`` is retained as the stable count of applicable
    positive criteria. ``applicable_method_count`` supplies its denominator,
    while ``method_disagreement`` explicitly marks mixed applicable votes.
    Reasons contain only criteria met, in stable method order.

    Returns:
        Input rows in original order with vote counts, disagreement,
        candidate status, and deterministic reasons.

    Raises:
        ValueError: If evidence columns or row states are invalid.
    """
    _validate_evidence_columns(df)

    signals = [
        _signal(flag_column, applicability_column)
        for flag_column, applicability_column, _ in _METHODS
    ]
    applicable = [
        col(applicability_column) == _APPLICABLE
        for _, applicability_column, _ in _METHODS
    ]
    agreement = _sum_booleans(signals)
    applicable_count = _sum_booleans(applicable)
    reasons = concat_str(
        [
            when(signal).then(lit(reason)).otherwise(lit(None, dtype=String))
            for signal, (_, _, reason) in zip(
                signals,
                _METHODS,
                strict=True,
            )
        ],
        separator=";",
        ignore_nulls=True,
    )

    return df.with_columns(
        agreement.alias("method_agreement"),
        applicable_count.alias("applicable_method_count"),
        (
            (applicable_count > 1)
            & (agreement > 0)
            & (agreement < applicable_count)
        ).alias("method_disagreement"),
        (agreement > 0).alias("anomaly_candidate"),
        reasons.alias("anomaly_reasons"),
    )


def _signal(flag_column: str, applicability_column: str) -> Expr:
    """Return positive evidence only when its method is applicable."""
    return (col(applicability_column) == _APPLICABLE) & col(
        flag_column
    ).fill_null(False)


def _sum_booleans(expressions: list[Expr]) -> Expr:
    """Return an Int8 row sum for a non-empty Boolean expression list."""
    total = expressions[0].cast(Int8)
    for expression in expressions[1:]:
        total += expression.cast(Int8)
    return total


def _validate_evidence_columns(df: DataFrame) -> None:
    """Validate explicit flags, applicability, and state consistency."""
    for flag_column, applicability_column, _ in _METHODS:
        for column in (flag_column, applicability_column):
            if column not in df.columns:
                raise ValueError(
                    f"Required evidence column is missing: {column}."
                )
        if df.schema[flag_column] != Boolean:
            raise ValueError(f"{flag_column} must be Boolean.")
        if df.schema[applicability_column] != String:
            raise ValueError(f"{applicability_column} must be String.")

        statuses = set(df[applicability_column].drop_nulls().to_list())
        valid_statuses = {_APPLICABLE, _NON_APPLICABLE}
        if df[applicability_column].null_count() or not statuses.issubset(
            valid_statuses
        ):
            message = (
                f"{applicability_column} must contain only applicable or "
                "non_applicable."
            )
            raise ValueError(message)

        applicable_nulls = df.filter(
            (col(applicability_column) == _APPLICABLE)
            & col(flag_column).is_null()
        )
        if not applicable_nulls.is_empty():
            message = (
                f"{flag_column} must be Boolean when "
                f"{applicability_column} is applicable."
            )
            raise ValueError(message)

        invalid_positive = df.filter(
            (col(applicability_column) == _NON_APPLICABLE)
            & col(flag_column).fill_null(False)
        )
        if not invalid_positive.is_empty():
            message = (
                f"{flag_column} must not be true when "
                f"{applicability_column} is non_applicable."
            )
            raise ValueError(message)
