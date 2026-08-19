"""Clustering labels for candidate anomaly analysis."""

from math import isfinite

import numpy as np
import polars as pl
from sklearn.cluster import (  # type: ignore[reportMissingTypeStubs]
    DBSCAN,
    KMeans,
)
from sklearn.preprocessing import (  # type: ignore[reportMissingTypeStubs]
    StandardScaler,
)


def detect_outliers_dbscan(
    df: pl.DataFrame,
    value_col: str = "value_pu",
    eps: float = 0.5,
    min_samples: int = 5,
    label_col: str = "dbscan_cluster",
) -> pl.DataFrame:
    """Add DBSCAN cluster labels without changing the input row order.

    DBSCAN marks candidate noise points with cluster label ``-1``.

    Returns:
        Input DataFrame with an added Int32 label column.
    """
    _validate_dbscan_parameters(eps, min_samples)
    values = _validated_values(df, value_col)
    if df.is_empty():
        return _with_empty_label(df, label_col)

    labels: np.ndarray[tuple[int], np.dtype[np.int32]] = DBSCAN(
        eps=eps, min_samples=min_samples
    ).fit_predict(values)  # type: ignore[reportUnknownMemberType]

    return df.with_columns(pl.Series(label_col, labels.astype(np.int32)))


def detect_outliers_dbscan_per_terminal(
    df: pl.DataFrame,
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    eps: float = 0.5,
    min_samples: int = 5,
    label_col: str = "dbscan_cluster",
) -> pl.DataFrame:
    """Apply DBSCAN independently to each terminal group.

    Running DBSCAN on the full dataset at once can be misleading when
    terminals have different voltage ranges or densities.  This function
    fits a separate DBSCAN model for each terminal, then reassembles the
    result preserving the original row order.

    Returns:
        Input DataFrame with an added Int32 label column.
    """
    _validate_dbscan_parameters(eps, min_samples)
    _validated_values(df, value_col)
    if terminal_col not in df.columns:
        raise ValueError(
            f"Required clustering column is missing: {terminal_col}."
        )
    if df.is_empty():
        return _with_empty_label(df, label_col)

    row_index_col = _available_internal_column(df, "_clustering_row_index")
    indexed = df.with_row_index(row_index_col)
    groups: list[pl.DataFrame] = []
    for subset in indexed.partition_by(terminal_col, maintain_order=True):
        labelled = detect_outliers_dbscan(
            subset,
            value_col=value_col,
            eps=eps,
            min_samples=min_samples,
            label_col=label_col,
        )
        groups.append(labelled)

    return pl.concat(groups).sort(row_index_col).drop(row_index_col)


def cluster_kmeans(
    df: pl.DataFrame,
    value_col: str = "value_pu",
    n_clusters: int = 3,
    random_state: int = 42,
    label_col: str = "kmeans_cluster",
) -> pl.DataFrame:
    """Add deterministic, centroid-ordered K-Means cluster labels.

    Returns:
        Input DataFrame with an added Int32 label column. Label zero identifies
        the cluster with the lowest centroid.
    """
    _validate_cluster_count(n_clusters)
    values = _validated_values(df, value_col)
    if df.is_empty():
        return _with_empty_label(df, label_col)
    if n_clusters > df.height:
        raise ValueError("n_clusters must not exceed the row count.")

    scaler = StandardScaler()  # type: ignore[reportUnknownVariableType]
    scaled: np.ndarray[tuple[int, int], np.dtype[np.float64]] = (
        scaler.fit_transform(values)  # type: ignore[reportUnknownMemberType]
    )

    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10,  # type: ignore[reportArgumentType]
    )
    labels: np.ndarray[tuple[int], np.dtype[np.int32]] = model.fit_predict(
        scaled
    )  # type: ignore[reportUnknownMemberType]
    centroids = np.asarray(model.cluster_centers_).reshape(-1)
    centroid_order = np.argsort(centroids)
    normalized_labels = np.empty(n_clusters, dtype=np.int32)
    normalized_labels[centroid_order] = np.arange(
        n_clusters,
        dtype=np.int32,
    )

    return df.with_columns(pl.Series(label_col, normalized_labels[labels]))


def filter_valid_events(
    df: pl.DataFrame,
    cluster_col: str = "dbscan_cluster",
) -> pl.DataFrame:
    """Remove rows labelled as candidate noise by DBSCAN.

    Returns:
        DataFrame containing rows whose cluster label is not ``-1``.
    """
    return df.filter(pl.col(cluster_col) != -1)


def _validate_dbscan_parameters(eps: float, min_samples: int) -> None:
    if not isfinite(eps) or eps <= 0:
        raise ValueError("eps must be finite and greater than zero.")
    if type(min_samples) is not int or min_samples < 1:
        raise ValueError("min_samples must be an integer greater than zero.")


def _validate_cluster_count(n_clusters: int) -> None:
    if type(n_clusters) is not int or n_clusters < 1:
        raise ValueError("n_clusters must be an integer greater than zero.")


def _validated_values(
    df: pl.DataFrame,
    value_col: str,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    if value_col not in df.columns:
        raise ValueError(
            f"Required clustering column is missing: {value_col}."
        )
    if df.is_empty():
        return np.empty((0, 1), dtype=np.float64)
    if not df.schema[value_col].is_numeric():
        raise ValueError(f"{value_col} must contain numeric values.")

    values = df[value_col].cast(pl.Float64).to_numpy().reshape(-1, 1)
    if not np.isfinite(values).all():
        raise ValueError(f"{value_col} must contain only finite values.")
    return values


def _with_empty_label(df: pl.DataFrame, label_col: str) -> pl.DataFrame:
    return df.with_columns(
        pl.Series(label_col, [], dtype=pl.Int32),
    )


def _available_internal_column(df: pl.DataFrame, base_name: str) -> str:
    name = base_name
    while name in df.columns:
        name = f"_{name}"
    return name
