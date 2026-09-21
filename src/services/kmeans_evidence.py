"""Contextual K-Means labels and distance-based anomaly evidence."""

from collections.abc import Sequence

from numpy import (
    absolute,
    arange,
    argsort,
    asarray,
    empty,
    int32,
    isfinite,
    percentile,
)
from polars import (
    Boolean,
    DataFrame,
    Float64,
    Int32,
    Int64,
    Series,
    String,
    concat,
)
from sklearn.cluster import KMeans  # type: ignore[reportMissingTypeStubs]
from sklearn.preprocessing import (  # type: ignore[reportMissingTypeStubs]
    StandardScaler,
)

_DEFAULT_GROUP_COLUMNS = (
    "scenario",
    "source_lineage",
    "terminal",
    "phase",
)
_THRESHOLD_PERCENTILE = 99.0


def evaluate_kmeans_evidence(
    observations: DataFrame,
    *,
    value_col: str = "value_pu",
    group_columns: Sequence[str] = _DEFAULT_GROUP_COLUMNS,
    n_clusters: int = 2,
    random_state: int = 42,
    calibration_mask: Sequence[bool] | None = None,
    calibration_col: str | None = None,
) -> DataFrame:
    """Emit group-local K-Means labels and calibrated distance evidence.

    Scaling, centroids, and 99th-percentile distance thresholds are fitted
    only from calibration observations. Cluster labels remain descriptive;
    only a distance strictly above its group threshold creates a candidate
    flag. When no calibration selection is supplied, all rows calibrate the
    exploratory model.

    Returns:
        Input rows in their original order with labels, explicit evidence,
        applicability, and frozen method metadata.

    Raises:
        ValueError: If parameters, columns, values, or calibration selection
            are invalid.
    """
    _validate_parameters(n_clusters, random_state)
    _validate_columns(observations, value_col, group_columns)
    _validate_values(observations, value_col)
    calibration_values, parameter_source = _calibration_selection(
        observations,
        calibration_mask=calibration_mask,
        calibration_col=calibration_col,
    )
    configuration_id = _configuration_id(
        value_col=value_col,
        group_columns=group_columns,
        n_clusters=n_clusters,
        random_state=random_state,
    )
    if observations.is_empty():
        return _empty_evidence(
            observations,
            parameter_source=parameter_source,
            configuration_id=configuration_id,
        )

    row_index_col = _available_column(observations, "_kmeans_row_index")
    calibration_internal_col = _available_column(
        observations, "_kmeans_calibration"
    )
    indexed = observations.with_row_index(row_index_col).with_columns(
        Series(
            calibration_internal_col,
            calibration_values,
            dtype=Boolean,
        )
    )
    evaluated_groups: list[DataFrame] = []
    for group in indexed.partition_by(
        list(group_columns), maintain_order=True
    ):
        evaluated_groups.append(
            _evaluate_group(
                group,
                value_col=value_col,
                group_columns=group_columns,
                calibration_col=calibration_internal_col,
                n_clusters=n_clusters,
                random_state=random_state,
                parameter_source=parameter_source,
                configuration_id=configuration_id,
            )
        )

    return (
        concat(evaluated_groups)
        .sort(row_index_col)
        .drop(row_index_col, calibration_internal_col)
    )


def _evaluate_group(
    group: DataFrame,
    *,
    value_col: str,
    group_columns: Sequence[str],
    calibration_col: str,
    n_clusters: int,
    random_state: int,
    parameter_source: str,
    configuration_id: str,
) -> DataFrame:
    """Fit and evaluate one comparable observation group."""
    group_key = _group_key(group, group_columns)
    calibration = group.filter(group[calibration_col])
    calibration_count = calibration.height
    minimum_count = max(3, n_clusters + 1)
    metadata = _metadata_columns(
        group.height,
        group_key=group_key,
        value_col=value_col,
        n_clusters=n_clusters,
        random_state=random_state,
        parameter_source=parameter_source,
        configuration_id=configuration_id,
        calibration_count=calibration_count,
    )

    if calibration_count < minimum_count:
        reason = (
            f"At least {minimum_count} calibration observations are required."
        )
        return _non_applicable(group, metadata, reason)

    calibration_values = calibration[value_col].to_numpy().reshape(-1, 1)
    if len(set(calibration[value_col].to_list())) == 1:
        return _non_applicable(
            group,
            metadata,
            "Calibration values have zero variance.",
        )
    if calibration[value_col].n_unique() < n_clusters:
        reason = "Too few distinct calibration values for n_clusters."
        return _non_applicable(group, metadata, reason)

    scaler = StandardScaler()  # type: ignore[reportUnknownVariableType]
    scaled_calibration = scaler.fit_transform(  # type: ignore[reportUnknownMemberType]
        calibration_values
    )
    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=10,  # type: ignore[reportArgumentType]
    )
    model.fit(scaled_calibration)  # type: ignore[reportUnknownMemberType]
    centroids = asarray(model.cluster_centers_).reshape(-1)

    all_values = group[value_col].to_numpy().reshape(-1, 1)
    scaled_values = asarray(
        scaler.transform(  # type: ignore[reportUnknownMemberType]
            all_values
        )
    )
    raw_labels = model.predict(  # type: ignore[reportUnknownMemberType]
        scaled_values
    )
    normalized_labels = empty(n_clusters, dtype=int32)
    normalized_labels[argsort(centroids)] = arange(n_clusters, dtype=int32)
    labels = normalized_labels[raw_labels]
    scores = absolute(scaled_values.reshape(-1) - centroids[raw_labels])

    calibration_scaled = asarray(
        scaler.transform(  # type: ignore[reportUnknownMemberType]
            calibration_values
        )
    )
    calibration_labels = model.predict(  # type: ignore[reportUnknownMemberType]
        calibration_scaled
    )
    calibration_scores = absolute(
        calibration_scaled.reshape(-1) - centroids[calibration_labels]
    )
    threshold = float(
        percentile(
            calibration_scores,
            _THRESHOLD_PERCENTILE,
            method="higher",
        )
    )
    flags = scores > threshold
    reasons = [
        "Distance exceeds calibrated threshold." if bool(flag) else None
        for flag in flags
    ]

    return group.with_columns(
        Series("kmeans_cluster", labels, dtype=Int32),
        Series("score", scores, dtype=Float64),
        Series("threshold", [threshold] * group.height, dtype=Float64),
        Series("flag", flags, dtype=Boolean),
        Series("applicability", ["applicable"] * group.height, dtype=String),
        Series("reason", reasons, dtype=String),
        *metadata,
    )


def _metadata_columns(
    row_count: int,
    *,
    group_key: str,
    value_col: str,
    n_clusters: int,
    random_state: int,
    parameter_source: str,
    configuration_id: str,
    calibration_count: int,
) -> list[Series]:
    """Build repeated auditable method metadata columns."""
    return [
        Series("method", ["kmeans"] * row_count, dtype=String),
        Series("group_key", [group_key] * row_count, dtype=String),
        Series("feature_space", [value_col] * row_count, dtype=String),
        Series(
            "scaling_policy",
            ["standard_scaler_fit_on_calibration_group"] * row_count,
            dtype=String,
        ),
        Series(
            "threshold_policy",
            ["calibration_distance_percentile_99"] * row_count,
            dtype=String,
        ),
        Series("random_state", [random_state] * row_count, dtype=Int64),
        Series("n_clusters", [n_clusters] * row_count, dtype=Int64),
        Series(
            "parameter_source", [parameter_source] * row_count, dtype=String
        ),
        Series(
            "configuration_id", [configuration_id] * row_count, dtype=String
        ),
        Series(
            "calibration_count", [calibration_count] * row_count, dtype=Int64
        ),
    ]


def _non_applicable(
    group: DataFrame,
    metadata: list[Series],
    reason: str,
) -> DataFrame:
    """Return explicit nullable evidence for a degenerate group."""
    row_count = group.height
    return group.with_columns(
        Series("kmeans_cluster", [None] * row_count, dtype=Int32),
        Series("score", [None] * row_count, dtype=Float64),
        Series("threshold", [None] * row_count, dtype=Float64),
        Series("flag", [None] * row_count, dtype=Boolean),
        Series(
            "applicability",
            ["non_applicable"] * row_count,
            dtype=String,
        ),
        Series("reason", [reason] * row_count, dtype=String),
        *metadata,
    )


def _calibration_selection(
    observations: DataFrame,
    *,
    calibration_mask: Sequence[bool] | None,
    calibration_col: str | None,
) -> tuple[list[bool], str]:
    """Resolve an explicit or default development selection."""
    if calibration_mask is not None and calibration_col is not None:
        message = (
            "calibration_mask and calibration_col are mutually exclusive."
        )
        raise ValueError(message)
    if calibration_mask is not None:
        if len(calibration_mask) != observations.height:
            message = "calibration_mask length must match the row count."
            raise ValueError(message)
        if any(type(value) is not bool for value in calibration_mask):
            message = "calibration_mask must contain only Boolean values."
            raise ValueError(message)
        return list(calibration_mask), "explicit_calibration_mask"
    if calibration_col is not None:
        if calibration_col not in observations.columns:
            message = f"Calibration column is missing: {calibration_col}."
            raise ValueError(message)
        if observations.schema[calibration_col] != Boolean:
            message = f"{calibration_col} must contain Boolean values."
            raise ValueError(message)
        values = observations[calibration_col].to_list()
        if any(value is None for value in values):
            message = f"{calibration_col} must not contain null values."
            raise ValueError(message)
        return [bool(value) for value in values], (
            f"calibration_column:{calibration_col}"
        )
    return [True] * observations.height, "all_observations"


def _validate_parameters(n_clusters: int, random_state: int) -> None:
    """Validate deterministic K-Means configuration."""
    if type(n_clusters) is not int or n_clusters < 1:
        message = "n_clusters must be an integer greater than zero."
        raise ValueError(message)
    if type(random_state) is not int:
        message = "random_state must be an integer."
        raise ValueError(message)


def _validate_columns(
    observations: DataFrame,
    value_col: str,
    group_columns: Sequence[str],
) -> None:
    """Require value and complete comparable-group identity."""
    required_columns = (*group_columns, value_col)
    missing_columns = [
        column
        for column in required_columns
        if column not in observations.columns
    ]
    if missing_columns:
        joined_columns = ", ".join(missing_columns)
        message = f"Missing required columns: {joined_columns}."
        raise ValueError(message)
    if len(set(group_columns)) != len(group_columns):
        message = "group_columns must not contain duplicates."
        raise ValueError(message)


def _validate_values(observations: DataFrame, value_col: str) -> None:
    """Reject inputs that cannot support distance evidence."""
    if not observations.schema[value_col].is_numeric():
        message = f"{value_col} must contain numeric values."
        raise ValueError(message)
    values = observations[value_col].cast(Float64).to_numpy()
    if not isfinite(values).all():
        message = f"{value_col} must contain only finite values."
        raise ValueError(message)


def _configuration_id(
    *,
    value_col: str,
    group_columns: Sequence[str],
    n_clusters: int,
    random_state: int,
) -> str:
    """Serialize stable configuration identity."""
    groups = ",".join(group_columns)
    return (
        f"kmeans|feature={value_col}|groups={groups}|scale=standard"
        f"|clusters={n_clusters}|seed={random_state}|threshold=p99"
    )


def _group_key(group: DataFrame, group_columns: Sequence[str]) -> str:
    """Serialize stable comparable-group identity."""
    return "|".join(
        f"{column}={group.item(0, column)}" for column in group_columns
    )


def _empty_evidence(
    observations: DataFrame,
    *,
    parameter_source: str,
    configuration_id: str,
) -> DataFrame:
    """Add declared empty evidence columns."""
    return observations.with_columns(
        Series("kmeans_cluster", [], dtype=Int32),
        Series("score", [], dtype=Float64),
        Series("threshold", [], dtype=Float64),
        Series("flag", [], dtype=Boolean),
        Series("applicability", [], dtype=String),
        Series("reason", [], dtype=String),
        Series("method", [], dtype=String),
        Series("group_key", [], dtype=String),
        Series("feature_space", [], dtype=String),
        Series("scaling_policy", [], dtype=String),
        Series("threshold_policy", [], dtype=String),
        Series("random_state", [], dtype=Int64),
        Series("n_clusters", [], dtype=Int64),
        Series("parameter_source", [], dtype=String),
        Series("configuration_id", [], dtype=String),
        Series("calibration_count", [], dtype=Int64),
    )


def _available_column(data: DataFrame, base_name: str) -> str:
    """Return an internal column name absent from input data."""
    name = base_name
    while name in data.columns:
        name = f"_{name}"
    return name
