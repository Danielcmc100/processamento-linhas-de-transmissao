"""Internal comparison metrics for fitted cluster partitions."""

from collections.abc import Sequence

from numpy import asarray, int32
from polars import (
    DataFrame,
    Float64,
    Int32,
    Int64,
    String,
    col,
    concat,
)
from polars._typing import PolarsDataType
from sklearn.metrics import (  # type: ignore[reportMissingTypeStubs]
    davies_bouldin_score,
    silhouette_score,
)

_KMEANS_METHOD = "kmeans"
_DBSCAN_METHOD = "dbscan"
_HIERARCHICAL_METHOD = "hierarchical"
_HIERARCHICAL_GROUP_COLUMNS = (
    "scenario",
    "source_lineage",
    "terminal",
)


def evaluate_cluster_comparison(
    observations: DataFrame,
    *,
    grouping_policy: Sequence[str],
) -> DataFrame:
    """Calculate internal metrics for each fitted clustering partition.

    DBSCAN noise labels are excluded because they do not identify a cluster.
    Silhouette and Davies--Bouldin scores are emitted only when every retained
    cluster contains at least two observations.

    Returns:
        One comparison record per algorithm and comparable observation group.

    Raises:
        ValueError: If required observation columns are missing.
    """
    return _concat_comparison_results([
        _evaluate_method(
            observations,
            method=_KMEANS_METHOD,
            label_col="kmeans_cluster",
            group_columns=grouping_policy,
            exclude_noise=False,
        ),
        _evaluate_method(
            observations,
            method=_DBSCAN_METHOD,
            label_col="dbscan_cluster",
            group_columns=grouping_policy,
            exclude_noise=True,
        ),
        _evaluate_method(
            observations,
            method=_HIERARCHICAL_METHOD,
            label_col="hierarchical_cluster",
            group_columns=_HIERARCHICAL_GROUP_COLUMNS,
            exclude_noise=False,
        ),
    ])


def _evaluate_method(
    observations: DataFrame,
    *,
    method: str,
    label_col: str,
    group_columns: Sequence[str],
    exclude_noise: bool,
) -> DataFrame:
    """Calculate metrics for one method within each fitted group."""
    _validate_columns(observations, label_col, group_columns)
    records: list[dict[str, str | int | float | None]] = []
    for group in observations.partition_by(
        list(group_columns), maintain_order=True
    ):
        records.append(
            _evaluate_group(
                group,
                method=method,
                label_col=label_col,
                group_columns=group_columns,
                exclude_noise=exclude_noise,
            )
        )
    return DataFrame(records, schema=_comparison_schema())


def _evaluate_group(
    group: DataFrame,
    *,
    method: str,
    label_col: str,
    group_columns: Sequence[str],
    exclude_noise: bool,
) -> dict[str, str | int | float | None]:
    """Return comparison scores or explicit inapplicability for one group."""
    labelled = group.filter(col(label_col).is_not_null())
    if exclude_noise:
        evaluated = labelled.filter(col(label_col) != -1)
    else:
        evaluated = labelled
    excluded_count = labelled.height - evaluated.height
    labels = evaluated[label_col].cast(Int32).to_numpy()
    cluster_sizes = _cluster_sizes(labels)
    record: dict[str, str | int | float | None] = {
        "method": method,
        "group_key": _group_key(group, group_columns),
        "feature_space": "value_pu",
        "observation_count": group.height,
        "labelled_count": labelled.height,
        "evaluated_count": evaluated.height,
        "excluded_noise_count": excluded_count,
        "cluster_count": len(cluster_sizes),
        "silhouette_score": None,
        "davies_bouldin_score": None,
        "applicability": "non_applicable",
        "reason": _inapplicability_reason(cluster_sizes),
    }
    if record["reason"] is not None:
        return record

    values = evaluated["value_pu"].cast(Float64).to_numpy().reshape(-1, 1)
    record["silhouette_score"] = float(
        silhouette_score(values, labels)  # type: ignore[reportUnknownMemberType]
    )
    record["davies_bouldin_score"] = float(
        davies_bouldin_score(values, labels)  # type: ignore[reportUnknownMemberType]
    )
    record["applicability"] = "applicable"
    record["reason"] = None
    return record


def _cluster_sizes(labels: object) -> list[int]:
    """Return member counts for each distinct label."""
    values = asarray(labels, dtype=int32)
    return [int((values == label).sum()) for label in set(values.tolist())]


def _inapplicability_reason(cluster_sizes: Sequence[int]) -> str | None:
    """State whether labels meet both internal metric preconditions."""
    if len(cluster_sizes) < 2:
        return "At least two retained clusters are required."
    if any(size < 2 for size in cluster_sizes):
        return "Each retained cluster requires at least two observations."
    return None


def _group_key(group: DataFrame, group_columns: Sequence[str]) -> str:
    """Build a stable, auditable key for one observation group."""
    values = group.select(list(group_columns)).row(0)
    return ";".join(
        f"{column}={value}"
        for column, value in zip(group_columns, values, strict=True)
    )


def _concat_comparison_results(results: Sequence[DataFrame]) -> DataFrame:
    """Concatenate method results while retaining the declared schema."""
    if not results:
        return DataFrame(schema=_comparison_schema())
    return concat(results)


def _validate_columns(
    observations: DataFrame,
    label_col: str,
    group_columns: Sequence[str],
) -> None:
    required = ["value_pu", label_col, *group_columns]
    missing = [column for column in required if column not in observations]
    if missing:
        names = ", ".join(missing)
        raise ValueError(
            f"Required clustering comparison columns are missing: {names}."
        )


def _comparison_schema() -> dict[str, PolarsDataType]:
    """Declare stable artifact columns and their Polars data types."""
    return {
        "method": String,
        "group_key": String,
        "feature_space": String,
        "observation_count": Int64,
        "labelled_count": Int64,
        "evaluated_count": Int64,
        "excluded_noise_count": Int64,
        "cluster_count": Int64,
        "silhouette_score": Float64,
        "davies_bouldin_score": Float64,
        "applicability": String,
        "reason": String,
    }
