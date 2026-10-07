"""Clustering labels for candidate anomaly analysis."""

from numpy import (
    arange,
    argsort,
    asarray,
    diff,
    dtype,
    empty,
    float64,
    int32,
    isfinite,
    median,
    ndarray,
    zeros,
)
from polars import DataFrame, Float64, Int32, Series, col, concat
from sklearn.cluster import (  # type: ignore[reportMissingTypeStubs]
    DBSCAN,
    KMeans,
)
from sklearn.preprocessing import (  # type: ignore[reportMissingTypeStubs]
    StandardScaler,
)

from src.services.schemas import (
    HierarchicalClusterObservation,
    HierarchicalObservation,
)


def detect_outliers_dbscan(
    df: DataFrame,
    value_col: str = "value_pu",
    eps: float = 0.5,
    min_samples: int = 5,
    label_col: str = "dbscan_cluster",
) -> DataFrame:
    """Add DBSCAN cluster labels without changing the input row order.

    DBSCAN marks candidate noise points with cluster label ``-1``.

    Returns:
        Input DataFrame with an added Int32 label column.
    """
    _validate_dbscan_parameters(eps, min_samples)
    values = _validated_values(df, value_col)
    if df.is_empty():
        return _with_empty_label(df, label_col)

    labels: ndarray[tuple[int], dtype[int32]] = DBSCAN(
        eps=eps, min_samples=min_samples
    ).fit_predict(values)  # type: ignore[reportUnknownMemberType]

    return df.with_columns(Series(label_col, labels.astype(int32)))


def detect_outliers_dbscan_per_terminal(
    df: DataFrame,
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    eps: float = 0.5,
    min_samples: int = 5,
    label_col: str = "dbscan_cluster",
) -> DataFrame:
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
    groups: list[DataFrame] = []
    for subset in indexed.partition_by(terminal_col, maintain_order=True):
        labelled = detect_outliers_dbscan(
            subset,
            value_col=value_col,
            eps=eps,
            min_samples=min_samples,
            label_col=label_col,
        )
        groups.append(labelled)

    return concat(groups).sort(row_index_col).drop(row_index_col)


def cluster_kmeans(
    df: DataFrame,
    value_col: str = "value_pu",
    n_clusters: int = 3,
    random_state: int = 42,
    label_col: str = "kmeans_cluster",
) -> DataFrame:
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
    scaled: ndarray[tuple[int, int], dtype[float64]] = scaler.fit_transform(
        values
    )  # type: ignore[reportUnknownMemberType]

    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10,  # type: ignore[reportArgumentType]
    )
    labels: ndarray[tuple[int], dtype[int32]] = model.fit_predict(scaled)  # type: ignore[reportUnknownMemberType]
    centroids = asarray(model.cluster_centers_).reshape(-1)
    centroid_order = argsort(centroids)
    normalized_labels = empty(n_clusters, dtype=int32)
    normalized_labels[centroid_order] = arange(
        n_clusters,
        dtype=int32,
    )

    return df.with_columns(Series(label_col, normalized_labels[labels]))


def cluster_hierarchical(
    df: DataFrame,
    terminal_col: str = "terminal",
    value_col: str = "value_pu",
    min_gap_pu: float = 0.05,
    gap_factor: float = 5.0,
    max_tail_fraction: float = 0.1,
    label_col: str = "hierarchical_cluster",
) -> DataFrame:
    """Label separated upper tails using terminal-local single linkage.

    Sorted adjacent gaps are single-linkage merge distances in one dimension.
    Select the largest gap separating at most ``max_tail_fraction`` of the
    highest observations, with at least three reference observations. The
    gap must exceed both ``min_gap_pu`` and ``gap_factor`` times the median
    adjacent spacing. These exploratory parameters are not physical limits.

    Returns:
        Input rows with Int32 labels: zero for reference observations and
        one for a separated upper tail. No qualifying gap yields all zeros.

    Raises:
        ValueError: If parameters or required numeric values are invalid.
    """
    if not isfinite(min_gap_pu) or min_gap_pu <= 0:
        raise ValueError("min_gap_pu must be finite and greater than zero.")
    if not isfinite(gap_factor) or gap_factor < 1:
        raise ValueError("gap_factor must be finite and at least one.")
    if not isfinite(max_tail_fraction) or not 0 < max_tail_fraction < 0.5:
        raise ValueError("max_tail_fraction must be between zero and 0.5.")
    _validated_values(df, value_col)
    if terminal_col not in df.columns:
        raise ValueError(
            f"Required clustering column is missing: {terminal_col}."
        )
    HierarchicalObservation.validate(
        df.select(
            col(terminal_col).alias("terminal"),
            col(value_col).cast(Float64).alias("value_pu"),
        )
    )
    if df.is_empty():
        return _with_empty_label(df, label_col)

    row_index_col = _available_internal_column(df, "_clustering_row_index")
    indexed = df.with_row_index(row_index_col)
    groups: list[DataFrame] = []
    for subset in indexed.partition_by(terminal_col, maintain_order=True):
        labels = _hierarchical_labels(
            _validated_values(subset, value_col),
            min_gap_pu,
            gap_factor,
            max_tail_fraction,
        )
        labelled = subset.with_columns(Series(label_col, labels))
        HierarchicalClusterObservation.validate(
            labelled.select(
                col(terminal_col).alias("terminal"),
                col(value_col).cast(Float64).alias("value_pu"),
                col(label_col).alias("hierarchical_cluster"),
            )
        )
        groups.append(labelled)

    return concat(groups).sort(row_index_col).drop(row_index_col)


def _hierarchical_labels(
    values: ndarray[tuple[int, int], dtype[float64]],
    min_gap_pu: float,
    gap_factor: float,
    max_tail_fraction: float,
) -> ndarray[tuple[int], dtype[int32]]:
    """Return reference/upper-tail labels from single-linkage gaps.

    Returns:
        Binary labels in the original observation order.
    """
    flattened = values.reshape(-1)
    labels = zeros(flattened.size, dtype=int32)
    if flattened.size < 4:
        return labels
    order = argsort(flattened)
    gaps = diff(flattened[order])
    if not (gaps > 0).any():
        return labels
    threshold = max(min_gap_pu, gap_factor * float(median(gaps)))
    candidates = [
        index
        for index, gap in enumerate(gaps)
        if index + 1 >= 3
        and (flattened.size - index - 1) / flattened.size <= max_tail_fraction
        and gap > threshold
    ]
    if candidates:
        boundary = max(candidates, key=lambda index: float(gaps[index]))
        labels[order[boundary + 1 :]] = 1
    return labels


def filter_valid_events(
    df: DataFrame,
    cluster_col: str = "dbscan_cluster",
) -> DataFrame:
    """Remove rows labelled as candidate noise by DBSCAN.

    Returns:
        DataFrame containing rows whose cluster label is not ``-1``.
    """
    return df.filter(col(cluster_col) != -1)


def _validate_dbscan_parameters(eps: float, min_samples: int) -> None:
    if not isfinite(eps) or eps <= 0:
        raise ValueError("eps must be finite and greater than zero.")
    if type(min_samples) is not int or min_samples < 1:
        raise ValueError("min_samples must be an integer greater than zero.")


def _validate_cluster_count(n_clusters: int) -> None:
    if type(n_clusters) is not int or n_clusters < 1:
        raise ValueError("n_clusters must be an integer greater than zero.")


def _validated_values(
    df: DataFrame,
    value_col: str,
) -> ndarray[tuple[int, int], dtype[float64]]:
    if value_col not in df.columns:
        raise ValueError(
            f"Required clustering column is missing: {value_col}."
        )
    if df.is_empty():
        return empty((0, 1), dtype=float64)
    if not df.schema[value_col].is_numeric():
        raise ValueError(f"{value_col} must contain numeric values.")

    values = df[value_col].cast(Float64).to_numpy().reshape(-1, 1)
    if not isfinite(values).all():
        raise ValueError(f"{value_col} must contain only finite values.")
    return values


def _with_empty_label(df: DataFrame, label_col: str) -> DataFrame:
    return df.with_columns(
        Series(label_col, [], dtype=Int32),
    )


def _available_internal_column(df: DataFrame, base_name: str) -> str:
    name = base_name
    while name in df.columns:
        name = f"_{name}"
    return name
