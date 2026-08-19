"""Comparison of statistical and clustering anomaly evidence.

The comparison marks analytical candidates only. It does not establish that
an observation is a numerical error or identify its physical cause.
"""

import polars as pl

METHOD_COLUMNS = (
    "dbscan_cluster",
    "kmeans_cluster",
    "sigma_flag",
)


def compare_anomaly_methods(df: pl.DataFrame) -> pl.DataFrame:
    """Compare three method labels for every observation.

    DBSCAN noise (label ``-1``), a true three-sigma flag, and membership in
    the highest centroid-ordered K-Means cluster each count as one signal.
    Highest-centroid membership is candidate evidence, not proof of an
    outlier. Reasons are serialized in a stable method order for CSV output.

    Returns:
        The input rows in their original order with agreement count,
        candidate status, and deterministic reasons.

    Raises:
        ValueError: If method columns are missing, null, or incorrectly typed.
    """
    _validate_method_columns(df)

    dbscan_signal = pl.col("dbscan_cluster") == -1
    sigma_signal = pl.col("sigma_flag")
    highest_kmeans = df["kmeans_cluster"].max()
    kmeans_signal = (
        pl.lit(False)
        if highest_kmeans is None
        else pl.col("kmeans_cluster") == highest_kmeans
    )
    agreement = (
        sigma_signal.cast(pl.Int8)
        + dbscan_signal.cast(pl.Int8)
        + kmeans_signal.cast(pl.Int8)
    )
    reasons = pl.concat_str(
        [
            pl
            .when(sigma_signal)
            .then(pl.lit("sigma_3"))
            .otherwise(pl.lit(None)),
            pl
            .when(dbscan_signal)
            .then(pl.lit("dbscan_noise"))
            .otherwise(pl.lit(None)),
            pl
            .when(kmeans_signal)
            .then(pl.lit("kmeans_highest_centroid"))
            .otherwise(pl.lit(None)),
        ],
        separator=";",
        ignore_nulls=True,
    )

    return df.with_columns(
        agreement.alias("method_agreement"),
        (agreement > 0).alias("anomaly_candidate"),
        reasons.alias("anomaly_reasons"),
    )


def _validate_method_columns(df: pl.DataFrame) -> None:
    for column in METHOD_COLUMNS:
        if column not in df.columns:
            raise ValueError(f"Required method column is missing: {column}.")
        if df[column].null_count():
            message = f"Method column {column} must not contain null values."
            raise ValueError(message)

    for column in ("dbscan_cluster", "kmeans_cluster"):
        if not df.schema[column].is_integer():
            raise ValueError(f"{column} must contain integer labels.")
    if df.schema["sigma_flag"] != pl.Boolean:
        raise ValueError("sigma_flag must be Boolean.")
