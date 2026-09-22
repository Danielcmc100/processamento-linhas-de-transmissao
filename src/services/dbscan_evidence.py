"""Calibrated contextual DBSCAN anomaly evidence."""

from collections.abc import Sequence
from math import isfinite

from numpy import asarray, dtype, float64, int32, ndarray, percentile
from numpy import isfinite as values_are_finite
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
from sklearn.cluster import DBSCAN  # type: ignore[reportMissingTypeStubs]
from sklearn.neighbors import (  # type: ignore[reportMissingTypeStubs]
    NearestNeighbors,
)
from sklearn.preprocessing import (  # type: ignore[reportMissingTypeStubs]
    StandardScaler,
)

_DEFAULT_GROUP_COLUMNS = (
    "scenario",
    "source_lineage",
    "terminal",
    "phase",
)
_EPS_PERCENTILE = 95.0


def evaluate_dbscan_evidence(
    observations: DataFrame,
    *,
    value_col: str = "value_pu",
    group_columns: Sequence[str] = _DEFAULT_GROUP_COLUMNS,
    min_samples: int = 5,
    effective_eps: float | None = None,
    calibration_mask: Sequence[bool] | None = None,
    calibration_col: str | None = None,
) -> DataFrame:
    """Emit scaled, group-local DBSCAN evidence and diagnostics.

    A StandardScaler is fitted only on calibration rows. Unless an effective
    epsilon is supplied explicitly, epsilon is the calibration group 95th
    percentile of each point's ``min_samples``-nearest-neighbor distance.
    DBSCAN labels remain descriptive; noise membership is the explicit
    Boolean candidate criterion. Sparse, constant, and all-noise groups are
    non-applicable and do not vote.

    Returns:
        Input rows in original order with prefixed DBSCAN evidence,
        diagnostics, and frozen configuration metadata.

    Raises:
        ValueError: If parameters, columns, values, or calibration selection
            are invalid.
    """
    _validate_parameters(min_samples, effective_eps)
    _validate_columns(observations, value_col, group_columns)
    _validate_values(observations, value_col)
    calibration_values, calibration_source = _calibration_selection(
        observations,
        calibration_mask=calibration_mask,
        calibration_col=calibration_col,
    )
    threshold_policy = (
        "calibration_k_distance_percentile_95"
        if effective_eps is None
        else "explicit_effective_eps"
    )
    parameter_source = (
        calibration_source
        if effective_eps is None
        else "explicit_effective_eps"
    )
    configuration_id = _configuration_id(
        value_col=value_col,
        group_columns=group_columns,
        min_samples=min_samples,
        effective_eps=effective_eps,
    )
    if observations.is_empty():
        return _empty_evidence(observations)

    row_index_col = _available_column(observations, "_dbscan_row_index")
    calibration_internal_col = _available_column(
        observations, "_dbscan_calibration"
    )
    indexed = observations.with_row_index(row_index_col).with_columns(
        Series(calibration_internal_col, calibration_values, dtype=Boolean)
    )
    groups: list[DataFrame] = []
    for group in indexed.partition_by(
        list(group_columns), maintain_order=True
    ):
        groups.append(
            _evaluate_group(
                group,
                value_col=value_col,
                group_columns=group_columns,
                calibration_col=calibration_internal_col,
                min_samples=min_samples,
                configured_eps=effective_eps,
                threshold_policy=threshold_policy,
                parameter_source=parameter_source,
                calibration_source=calibration_source,
                configuration_id=configuration_id,
            )
        )

    return (
        concat(groups)
        .sort(row_index_col)
        .drop(row_index_col, calibration_internal_col)
    )


def _evaluate_group(
    group: DataFrame,
    *,
    value_col: str,
    group_columns: Sequence[str],
    calibration_col: str,
    min_samples: int,
    configured_eps: float | None,
    threshold_policy: str,
    parameter_source: str,
    calibration_source: str,
    configuration_id: str,
) -> DataFrame:
    """Fit and evaluate one comparable observation group."""
    calibration = group.filter(group[calibration_col])
    calibration_count = calibration.height
    base_metadata = {
        "group_key": _group_key(group, group_columns),
        "value_col": value_col,
        "min_samples": min_samples,
        "threshold_policy": threshold_policy,
        "parameter_source": parameter_source,
        "calibration_source": calibration_source,
        "configuration_id": configuration_id,
        "calibration_count": calibration_count,
    }
    if calibration_count < min_samples:
        reason = (
            f"At least {min_samples} calibration observations are required."
        )
        metadata = _metadata_columns(
            group.height,
            effective_eps=configured_eps,
            cluster_count=0,
            noise_count=0,
            noise_rate=None,
            **base_metadata,
        )
        return _non_applicable(group, metadata, reason)
    if calibration[value_col].n_unique() == 1:
        metadata = _metadata_columns(
            group.height,
            effective_eps=configured_eps,
            cluster_count=0,
            noise_count=0,
            noise_rate=None,
            **base_metadata,
        )
        return _non_applicable(
            group,
            metadata,
            "Calibration values have zero variance.",
        )

    scaler = StandardScaler()  # type: ignore[reportUnknownVariableType]
    calibration_array = calibration[value_col].to_numpy().reshape(-1, 1)
    scaled_calibration: ndarray[tuple[int, int], dtype[float64]] = asarray(
        scaler.fit_transform(  # type: ignore[reportUnknownMemberType]
            calibration_array
        )
    )
    effective_eps = configured_eps or _calibrated_epsilon(
        scaled_calibration, min_samples
    )
    if effective_eps == 0.0:
        metadata = _metadata_columns(
            group.height,
            effective_eps=effective_eps,
            cluster_count=0,
            noise_count=0,
            noise_rate=None,
            **base_metadata,
        )
        return _non_applicable(
            group,
            metadata,
            "Calibrated epsilon is zero.",
        )

    values = group[value_col].to_numpy().reshape(-1, 1)
    scaled_values: ndarray[tuple[int, int], dtype[float64]] = asarray(
        scaler.transform(values)  # type: ignore[reportUnknownMemberType]
    )
    model = DBSCAN(eps=effective_eps, min_samples=min_samples)
    labels = asarray(
        model.fit_predict(  # type: ignore[reportUnknownMemberType]
            scaled_values
        ),
        dtype=int32,
    )
    scores = _nearest_neighbor_distances(scaled_values, min_samples)
    noise = labels == -1
    noise_count = int(noise.sum())
    cluster_count = len(set(labels.tolist()) - {-1})
    noise_rate = noise_count / group.height
    metadata = _metadata_columns(
        group.height,
        effective_eps=effective_eps,
        cluster_count=cluster_count,
        noise_count=noise_count,
        noise_rate=noise_rate,
        **base_metadata,
    )
    if cluster_count == 0:
        return group.with_columns(
            Series("dbscan_cluster", labels, dtype=Int32),
            Series("dbscan_score", scores, dtype=Float64),
            Series(
                "dbscan_threshold",
                [effective_eps] * group.height,
                dtype=Float64,
            ),
            Series("dbscan_flag", [None] * group.height, dtype=Boolean),
            Series(
                "dbscan_applicability",
                ["non_applicable"] * group.height,
                dtype=String,
            ),
            Series(
                "dbscan_reason",
                ["DBSCAN classified every row as noise."] * group.height,
                dtype=String,
            ),
            *metadata,
        )

    reasons = [
        "DBSCAN classified row as noise." if bool(flag) else None
        for flag in noise
    ]
    return group.with_columns(
        Series("dbscan_cluster", labels, dtype=Int32),
        Series("dbscan_score", scores, dtype=Float64),
        Series(
            "dbscan_threshold",
            [effective_eps] * group.height,
            dtype=Float64,
        ),
        Series("dbscan_flag", noise, dtype=Boolean),
        Series(
            "dbscan_applicability",
            ["applicable"] * group.height,
            dtype=String,
        ),
        Series("dbscan_reason", reasons, dtype=String),
        *metadata,
    )


def _calibrated_epsilon(
    scaled_values: ndarray[tuple[int, int], dtype[float64]],
    min_samples: int,
) -> float:
    """Return development k-distance 95th percentile."""
    distances = _nearest_neighbor_distances(scaled_values, min_samples)
    return float(percentile(distances, _EPS_PERCENTILE, method="higher"))


def _nearest_neighbor_distances(
    scaled_values: ndarray[tuple[int, int], dtype[float64]],
    min_samples: int,
) -> ndarray[tuple[int], dtype[float64]]:
    """Return each row's min_samples-neighbor distance."""
    neighbors = NearestNeighbors(n_neighbors=min_samples)
    neighbors.fit(scaled_values)  # type: ignore[reportUnknownMemberType]
    distances, _ = neighbors.kneighbors(  # type: ignore[reportUnknownMemberType]
        scaled_values
    )
    distance_array: ndarray[tuple[int, int], dtype[float64]] = asarray(
        distances
    )
    return distance_array[:, -1]


def _metadata_columns(
    row_count: int,
    *,
    group_key: str,
    value_col: str,
    min_samples: int,
    threshold_policy: str,
    parameter_source: str,
    calibration_source: str,
    configuration_id: str,
    calibration_count: int,
    effective_eps: float | None,
    cluster_count: int,
    noise_count: int,
    noise_rate: float | None,
) -> list[Series]:
    """Build repeated DBSCAN diagnostics and method metadata."""
    return [
        Series("dbscan_method", ["dbscan"] * row_count, dtype=String),
        Series("dbscan_group_key", [group_key] * row_count, dtype=String),
        Series("dbscan_feature_space", [value_col] * row_count, dtype=String),
        Series(
            "dbscan_scaling_policy",
            ["standard_scaler_fit_on_calibration_group"] * row_count,
            dtype=String,
        ),
        Series(
            "dbscan_threshold_policy",
            [threshold_policy] * row_count,
            dtype=String,
        ),
        Series(
            "dbscan_parameter_source",
            [parameter_source] * row_count,
            dtype=String,
        ),
        Series(
            "dbscan_calibration_source",
            [calibration_source] * row_count,
            dtype=String,
        ),
        Series(
            "dbscan_configuration_id",
            [configuration_id] * row_count,
            dtype=String,
        ),
        Series(
            "dbscan_calibration_count",
            [calibration_count] * row_count,
            dtype=Int64,
        ),
        Series(
            "dbscan_effective_eps",
            [effective_eps] * row_count,
            dtype=Float64,
        ),
        Series(
            "dbscan_min_samples",
            [min_samples] * row_count,
            dtype=Int64,
        ),
        Series(
            "dbscan_cluster_count",
            [cluster_count] * row_count,
            dtype=Int64,
        ),
        Series(
            "dbscan_noise_count",
            [noise_count] * row_count,
            dtype=Int64,
        ),
        Series(
            "dbscan_noise_rate",
            [noise_rate] * row_count,
            dtype=Float64,
        ),
    ]


def _non_applicable(
    group: DataFrame,
    metadata: list[Series],
    reason: str,
) -> DataFrame:
    """Return explicit nullable evidence for an unusable group."""
    row_count = group.height
    return group.with_columns(
        Series("dbscan_cluster", [None] * row_count, dtype=Int32),
        Series("dbscan_score", [None] * row_count, dtype=Float64),
        Series("dbscan_threshold", [None] * row_count, dtype=Float64),
        Series("dbscan_flag", [None] * row_count, dtype=Boolean),
        Series(
            "dbscan_applicability",
            ["non_applicable"] * row_count,
            dtype=String,
        ),
        Series("dbscan_reason", [reason] * row_count, dtype=String),
        *metadata,
    )


def _calibration_selection(
    observations: DataFrame,
    *,
    calibration_mask: Sequence[bool] | None,
    calibration_col: str | None,
) -> tuple[list[bool], str]:
    """Resolve development rows and serialize their source."""
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


def _validate_parameters(
    min_samples: int,
    effective_eps: float | None,
) -> None:
    """Validate effective DBSCAN parameters."""
    if type(min_samples) is not int or min_samples < 1:
        message = "min_samples must be an integer greater than zero."
        raise ValueError(message)
    if effective_eps is not None and (
        not isfinite(effective_eps) or effective_eps <= 0.0
    ):
        message = "effective_eps must be finite and greater than zero."
        raise ValueError(message)


def _validate_columns(
    observations: DataFrame,
    value_col: str,
    group_columns: Sequence[str],
) -> None:
    """Require value and complete comparable-group identity."""
    required = (*group_columns, value_col)
    missing = [column for column in required if column not in observations]
    if missing:
        message = f"Missing required columns: {', '.join(missing)}."
        raise ValueError(message)
    if len(set(group_columns)) != len(group_columns):
        message = "group_columns must not contain duplicates."
        raise ValueError(message)


def _validate_values(observations: DataFrame, value_col: str) -> None:
    """Reject values that cannot support scaled distance evidence."""
    if not observations.schema[value_col].is_numeric():
        message = f"{value_col} must contain numeric values."
        raise ValueError(message)
    values = observations[value_col].cast(Float64).to_numpy()
    if not values_are_finite(values).all():
        message = f"{value_col} must contain only finite values."
        raise ValueError(message)


def _configuration_id(
    *,
    value_col: str,
    group_columns: Sequence[str],
    min_samples: int,
    effective_eps: float | None,
) -> str:
    """Serialize stable DBSCAN configuration identity."""
    groups = ",".join(group_columns)
    epsilon = "calibration_p95" if effective_eps is None else effective_eps
    return (
        f"dbscan|feature={value_col}|groups={groups}|scale=standard"
        f"|min_samples={min_samples}|eps={epsilon}"
    )


def _group_key(group: DataFrame, group_columns: Sequence[str]) -> str:
    """Serialize stable comparable-group identity."""
    return "|".join(
        f"{column}={group.item(0, column)}" for column in group_columns
    )


def _empty_evidence(observations: DataFrame) -> DataFrame:
    """Add declared empty DBSCAN evidence columns."""
    return observations.with_columns(
        Series("dbscan_cluster", [], dtype=Int32),
        Series("dbscan_score", [], dtype=Float64),
        Series("dbscan_threshold", [], dtype=Float64),
        Series("dbscan_flag", [], dtype=Boolean),
        Series("dbscan_applicability", [], dtype=String),
        Series("dbscan_reason", [], dtype=String),
        Series("dbscan_method", [], dtype=String),
        Series("dbscan_group_key", [], dtype=String),
        Series("dbscan_feature_space", [], dtype=String),
        Series("dbscan_scaling_policy", [], dtype=String),
        Series("dbscan_threshold_policy", [], dtype=String),
        Series("dbscan_parameter_source", [], dtype=String),
        Series("dbscan_calibration_source", [], dtype=String),
        Series("dbscan_configuration_id", [], dtype=String),
        Series("dbscan_calibration_count", [], dtype=Int64),
        Series("dbscan_effective_eps", [], dtype=Float64),
        Series("dbscan_min_samples", [], dtype=Int64),
        Series("dbscan_cluster_count", [], dtype=Int64),
        Series("dbscan_noise_count", [], dtype=Int64),
        Series("dbscan_noise_rate", [], dtype=Float64),
    )


def _available_column(data: DataFrame, base_name: str) -> str:
    """Return an internal column name absent from input data."""
    name = base_name
    while name in data.columns:
        name = f"_{name}"
    return name
