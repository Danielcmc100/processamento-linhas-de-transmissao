"""Deterministic controlled perturbations for anomaly benchmarks."""

from dataclasses import dataclass
from math import isfinite
from statistics import mean, stdev
from typing import Literal

from numpy.random import default_rng
from polars import Boolean, DataFrame, Float64, Int64, Series, String

GENERATOR_VERSION = "1.0.0"

InterventionFamily = Literal["clean", "point", "contextual", "collective"]

_REQUIRED_COLUMNS = (
    "scenario",
    "sample_size",
    "source_lineage",
    "source_file",
    "simulation",
    "terminal",
    "phase",
    "value_pu",
)
_GROUP_COLUMNS = ("scenario", "source_lineage", "terminal", "phase")
_MANIFEST_SCHEMA = {
    "scenario": String,
    "sample_size": Int64,
    "source_lineage": String,
    "source_file": String,
    "source_sha256": String,
    "simulation": Int64,
    "terminal": String,
    "phase": String,
    "original_value": Float64,
    "injected_value": Float64,
    "intervention_family": String,
    "intensity": Float64,
    "requested_contamination_rate": Float64,
    "effective_contamination_rate": Float64,
    "seed": Int64,
    "generator_version": String,
}


@dataclass(frozen=True, slots=True)
class ControlledPerturbationResult:
    """Copied observations, injection manifest, and applicability status."""

    data: DataFrame
    manifest: DataFrame
    status: str
    reason: str | None
    requested_contamination_rate: float
    effective_contamination_rate: float


def generate_controlled_perturbations(
    observations: DataFrame,
    *,
    family: InterventionFamily,
    contamination_rate: float,
    intensity: float,
    seed: int,
) -> ControlledPerturbationResult:
    """Create one reproducible intervention condition on copied data.

    Point and collective interventions add ``intensity`` in P.U. Contextual
    interventions replace selected values with group mean plus ``intensity``
    sample standard deviations. Collective selection covers a contiguous
    simulation block and every terminal/phase peer in each selected run.

    Returns:
        Copied observations, trace manifest, and explicit applicability.

    Raises:
        ValueError: If configuration or required columns are invalid.
    """
    _validate_inputs(
        observations,
        family=family,
        contamination_rate=contamination_rate,
        intensity=intensity,
    )
    copied = observations.clone()
    if family == "clean":
        data = _label_data(copied, family, (), contamination_rate, intensity)
        return ControlledPerturbationResult(
            data=data,
            manifest=_empty_manifest(),
            status="applicable",
            reason=None,
            requested_contamination_rate=contamination_rate,
            effective_contamination_rate=0.0,
        )

    selected = _select_rows(
        copied,
        family=family,
        contamination_rate=contamination_rate,
        seed=seed,
    )
    if not selected:
        data = _label_data(copied, family, (), contamination_rate, intensity)
        return ControlledPerturbationResult(
            data=data,
            manifest=_empty_manifest(),
            status="infeasible",
            reason="Requested contamination selects zero observations.",
            requested_contamination_rate=contamination_rate,
            effective_contamination_rate=0.0,
        )

    original_values = [float(value) for value in copied["value_pu"]]
    injected_values = list(original_values)
    if family == "contextual":
        contextual_values = _contextual_values(copied, intensity)
        unusable = [
            index for index in selected if index not in contextual_values
        ]
        if unusable:
            data = _label_data(
                copied,
                family,
                (),
                contamination_rate,
                intensity,
            )
            return ControlledPerturbationResult(
                data=data,
                manifest=_empty_manifest(),
                status="infeasible",
                reason="Selected contextual group has zero variance.",
                requested_contamination_rate=contamination_rate,
                effective_contamination_rate=0.0,
            )
        for index in selected:
            injected_values[index] = contextual_values[index]
    else:
        for index in selected:
            injected_values[index] += intensity

    effective_rate = len(selected) / copied.height
    data = copied.with_columns(Series("value_pu", injected_values))
    data = _label_data(
        data,
        family,
        selected,
        contamination_rate,
        intensity,
    )
    manifest = _build_manifest(
        copied,
        selected,
        original_values,
        injected_values,
        family=family,
        contamination_rate=contamination_rate,
        effective_rate=effective_rate,
        intensity=intensity,
        seed=seed,
    )
    return ControlledPerturbationResult(
        data=data,
        manifest=manifest,
        status="applicable",
        reason=None,
        requested_contamination_rate=contamination_rate,
        effective_contamination_rate=effective_rate,
    )


def split_by_source_run(
    observations: DataFrame,
    *,
    development_fraction: float,
    seed: int,
) -> DataFrame:
    """Assign complete source-lineage simulation runs to one split.

    Returns:
        Copied observations with deterministic ``benchmark_split`` labels.

    Raises:
        ValueError: If split configuration or identity columns are invalid.
    """
    missing = [
        column
        for column in ("source_lineage", "simulation")
        if column not in observations.columns
    ]
    if missing:
        message = f"Missing required columns: {', '.join(missing)}."
        raise ValueError(message)
    if not 0.0 < development_fraction < 1.0:
        message = "development_fraction must be between zero and one."
        raise ValueError(message)

    keys = sorted({
        (str(lineage), int(simulation))
        for lineage, simulation in observations.select(
            "source_lineage", "simulation"
        ).iter_rows()
    })
    if len(keys) < 2:
        message = "At least two source-run identities are required."
        raise ValueError(message)
    permutation = default_rng(seed).permutation(len(keys)).tolist()
    development_count = round(len(keys) * development_fraction)
    development_count = min(max(development_count, 1), len(keys) - 1)
    development_keys = {
        keys[int(index)] for index in permutation[:development_count]
    }
    labels = [
        (
            "development"
            if (str(row[0]), int(row[1])) in development_keys
            else "evaluation"
        )
        for row in observations.select(
            "source_lineage", "simulation"
        ).iter_rows()
    ]
    return observations.clone().with_columns(
        Series("benchmark_split", labels, dtype=String)
    )


def _validate_inputs(
    observations: DataFrame,
    *,
    family: str,
    contamination_rate: float,
    intensity: float,
) -> None:
    missing = [
        column for column in _REQUIRED_COLUMNS if column not in observations
    ]
    if missing:
        message = f"Missing required columns: {', '.join(missing)}."
        raise ValueError(message)
    if family not in {"clean", "point", "contextual", "collective"}:
        message = f"Unsupported intervention family: {family}."
        raise ValueError(message)
    if (
        not isfinite(contamination_rate)
        or not 0.0 <= contamination_rate <= 1.0
    ):
        message = "contamination_rate must be finite and between zero and one."
        raise ValueError(message)
    if family != "clean" and contamination_rate == 0.0:
        message = "Non-clean interventions require positive contamination."
        raise ValueError(message)
    if not isfinite(intensity):
        message = "intensity must be finite."
        raise ValueError(message)


def _select_rows(
    observations: DataFrame,
    *,
    family: InterventionFamily,
    contamination_rate: float,
    seed: int,
) -> tuple[int, ...]:
    if family == "collective":
        return _select_collective_rows(observations, contamination_rate, seed)
    count = int(observations.height * contamination_rate)
    if count == 0:
        return ()
    selected = default_rng(seed).choice(
        observations.height,
        size=count,
        replace=False,
    )
    return tuple(sorted(int(index) for index in selected.tolist()))


def _select_collective_rows(
    observations: DataFrame,
    contamination_rate: float,
    seed: int,
) -> tuple[int, ...]:
    keys = sorted({
        (str(lineage), int(simulation))
        for lineage, simulation in observations.select(
            "source_lineage", "simulation"
        ).iter_rows()
    })
    run_count = int(len(keys) * contamination_rate)
    if run_count == 0:
        return ()
    blocks: list[tuple[tuple[str, int], ...]] = []
    lineages = sorted({lineage for lineage, _ in keys})
    for lineage in lineages:
        lineage_keys = [key for key in keys if key[0] == lineage]
        for start in range(len(lineage_keys) - run_count + 1):
            block = tuple(lineage_keys[start : start + run_count])
            simulations = [key[1] for key in block]
            if all(
                right == left + 1
                for left, right in zip(simulations, simulations[1:])
            ):
                blocks.append(block)
    if not blocks:
        return ()
    block_index = int(default_rng(seed).integers(0, len(blocks)))
    selected_keys = set(blocks[block_index])
    return tuple(
        index
        for index, (lineage, simulation) in enumerate(
            observations.select("source_lineage", "simulation").iter_rows()
        )
        if (str(lineage), int(simulation)) in selected_keys
    )


def _contextual_values(
    observations: DataFrame,
    intensity: float,
) -> dict[int, float]:
    rows = observations.to_dicts()
    grouped_indices: dict[tuple[object, ...], list[int]] = {}
    for index, row in enumerate(rows):
        key = tuple(row[column] for column in _GROUP_COLUMNS)
        grouped_indices.setdefault(key, []).append(index)
    injected: dict[int, float] = {}
    for indices in grouped_indices.values():
        values = [float(rows[index]["value_pu"]) for index in indices]
        if len(values) < 2 or stdev(values) == 0.0:
            continue
        contextual_value = mean(values) + intensity * stdev(values)
        for index in indices:
            injected[index] = contextual_value
    return injected


def _label_data(
    observations: DataFrame,
    family: InterventionFamily,
    selected: tuple[int, ...],
    contamination_rate: float,
    intensity: float,
) -> DataFrame:
    selected_indices = set(selected)
    labels = [
        index in selected_indices for index in range(observations.height)
    ]
    return observations.with_columns(
        Series("controlled_label", labels, dtype=Boolean),
        Series(
            "intervention_family",
            [family] * observations.height,
            dtype=String,
        ),
        Series(
            "intervention_intensity",
            [intensity] * observations.height,
            dtype=Float64,
        ),
        Series(
            "requested_contamination_rate",
            [contamination_rate] * observations.height,
            dtype=Float64,
        ),
    )


def _build_manifest(
    observations: DataFrame,
    selected: tuple[int, ...],
    original_values: list[float],
    injected_values: list[float],
    *,
    family: InterventionFamily,
    contamination_rate: float,
    effective_rate: float,
    intensity: float,
    seed: int,
) -> DataFrame:
    source_rows = observations.to_dicts()
    rows: list[dict[str, object]] = []
    for index in selected:
        source = source_rows[index]
        rows.append({
            "scenario": source["scenario"],
            "sample_size": source["sample_size"],
            "source_lineage": source["source_lineage"],
            "source_file": source["source_file"],
            "source_sha256": source.get("source_sha256", ""),
            "simulation": source["simulation"],
            "terminal": source["terminal"],
            "phase": source["phase"],
            "original_value": original_values[index],
            "injected_value": injected_values[index],
            "intervention_family": family,
            "intensity": intensity,
            "requested_contamination_rate": contamination_rate,
            "effective_contamination_rate": effective_rate,
            "seed": seed,
            "generator_version": GENERATOR_VERSION,
        })
    return DataFrame(rows, schema=_MANIFEST_SCHEMA, strict=False)


def _empty_manifest() -> DataFrame:
    return DataFrame(schema=_MANIFEST_SCHEMA)
