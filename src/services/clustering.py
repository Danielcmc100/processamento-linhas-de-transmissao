"""Clustering and outlier detection service.

Applies unsupervised learning algorithms (DBSCAN, K-Means) to
groups of voltage maxima (in P.U.) in order to separate:
  - Typical overvoltage events (physical phenomena)
  - Numerical simulation artifacts / non-converged outliers
"""

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
) -> pl.DataFrame:
    """Label rows as outliers using DBSCAN on the value_pu column.

    DBSCAN marks noise points (outliers) with cluster label -1.

    Returns:
        Input DataFrame with an added ``cluster`` (Int32) column.
        Rows labelled -1 are considered numerical artifacts.
    """
    values = df[value_col].to_numpy().reshape(-1, 1)
    scaler = StandardScaler()  # type: ignore[reportUnknownVariableType]
    scaled: np.ndarray[tuple[int, int], np.dtype[np.float64]] = (
        scaler.fit_transform(values)  # type: ignore[reportUnknownMemberType]
    )

    labels: np.ndarray[tuple[int], np.dtype[np.int32]] = DBSCAN(
        eps=eps, min_samples=min_samples
    ).fit_predict(scaled)  # type: ignore[reportUnknownMemberType]

    return df.with_columns(pl.Series("cluster", labels.astype(np.int32)))


def detect_outliers_dbscan_per_terminal(
    df: pl.DataFrame,
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    eps: float = 0.5,
    min_samples: int = 5,
) -> pl.DataFrame:
    """Apply DBSCAN independently to each terminal group.

    Running DBSCAN on the full dataset at once can be misleading when
    terminals have different voltage ranges or densities.  This function
    fits a separate DBSCAN model for each terminal, then reassembles the
    result preserving the original row order.

    Returns:
        Input DataFrame with an added ``cluster`` (Int32) column.
        Rows labelled -1 are considered numerical artifacts for that terminal.
    """
    groups: list[pl.DataFrame] = []
    for terminal in df[terminal_col].unique().sort().to_list():
        subset = df.filter(pl.col(terminal_col) == terminal)
        labelled = detect_outliers_dbscan(
            subset,
            value_col=value_col,
            eps=eps,
            min_samples=min_samples,
        )
        groups.append(labelled)

    if not groups:
        return df.with_columns(pl.lit(0).cast(pl.Int32).alias("cluster"))

    return pl.concat(groups)


def cluster_kmeans(
    df: pl.DataFrame,
    value_col: str = "value_pu",
    n_clusters: int = 3,
    random_state: int = 42,
) -> pl.DataFrame:
    """Partition voltage maxima into *n_clusters* groups using K-Means.

    Returns:
        Input DataFrame with an added ``cluster`` (Int32) column.
    """
    values = df[value_col].to_numpy().reshape(-1, 1)
    scaler = StandardScaler()  # type: ignore[reportUnknownVariableType]
    scaled: np.ndarray[tuple[int, int], np.dtype[np.float64]] = (
        scaler.fit_transform(values)  # type: ignore[reportUnknownMemberType]
    )

    labels: np.ndarray[tuple[int], np.dtype[np.int32]] = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init="auto",
    ).fit_predict(scaled)  # type: ignore[reportUnknownMemberType]

    return df.with_columns(pl.Series("cluster", labels.astype(np.int32)))


def filter_valid_events(
    df: pl.DataFrame,
    cluster_col: str = "cluster",
) -> pl.DataFrame:
    """Remove rows flagged as outliers by DBSCAN (cluster == -1).

    Returns:
        Filtered DataFrame containing only physically plausible events.
    """
    return df.filter(pl.col(cluster_col) != -1)
