"""Predeclared parameter-grid replay and candidate-set stability evidence."""

from collections.abc import Callable, Hashable, Iterable
from dataclasses import dataclass
from itertools import product
from math import isfinite
from typing import Literal, TypeAlias

ParameterValue: TypeAlias = bool | int | float | str | None
Applicability: TypeAlias = Literal["applicable", "non_applicable"]
Qualification: TypeAlias = Literal["stable", "sensitive", "non_applicable"]


@dataclass(frozen=True, slots=True)
class ParameterGrid:
    """Frozen sensitivity design declared before target-data replay."""

    configuration_id: str
    method: str
    varied_parameters: tuple[tuple[str, tuple[ParameterValue, ...]], ...]
    fixed_controls: tuple[tuple[str, ParameterValue], ...]
    seeds: tuple[int, ...]
    evaluation_measures: tuple[str, ...] = (
        "candidate_count",
        "candidate_rate",
        "applicability",
        "identity_jaccard",
    )
    stability_threshold: float = 0.80
    stability_rationale: str = (
        "Predeclared candidate-set stability qualification threshold."
    )

    def __post_init__(self) -> None:
        """Reject incomplete or mutable-looking experiment declarations."""
        if not self.configuration_id.strip():
            raise ValueError("configuration_id must not be empty.")
        if not self.method.strip():
            raise ValueError("method must not be empty.")
        if not self.varied_parameters:
            raise ValueError("Grid requires at least one varied parameter.")
        if not self.seeds:
            raise ValueError("Grid requires at least one seed.")
        if any(type(seed) is not int for seed in self.seeds):
            raise ValueError("seeds must contain only integers.")
        if len(set(self.seeds)) != len(self.seeds):
            raise ValueError("seeds must not contain duplicates.")
        if not isfinite(self.stability_threshold) or not (
            0.0 <= self.stability_threshold <= 1.0
        ):
            raise ValueError("stability_threshold must be between 0 and 1.")
        if not self.stability_rationale.strip():
            raise ValueError("stability_rationale must not be empty.")
        required_measures = {
            "candidate_count",
            "candidate_rate",
            "applicability",
            "identity_jaccard",
        }
        if not required_measures.issubset(self.evaluation_measures):
            raise ValueError(
                "evaluation_measures must include counts, rates, "
                "applicability, and identity_jaccard."
            )
        _validate_parameter_declaration(
            self.varied_parameters,
            self.fixed_controls,
        )

    @property
    def parameter_ranges(
        self,
    ) -> tuple[tuple[str, tuple[ParameterValue, ...]], ...]:
        """Return frozen varied-parameter ranges."""
        return self.varied_parameters


@dataclass(frozen=True, slots=True)
class SensitivityReplayInput:
    """One deterministic method configuration and seed to evaluate."""

    experiment_id: str
    run_id: str
    method: str
    parameters: tuple[tuple[str, ParameterValue], ...]
    seed: int

    def parameter(self, name: str) -> ParameterValue:
        """Return one declared parameter value.

        Raises:
            KeyError: If ``name`` is absent from this replay input.
        """
        for parameter_name, value in self.parameters:
            if parameter_name == name:
                return value
        raise KeyError(name)


@dataclass(frozen=True, slots=True)
class SensitivityReplayResult:
    """Candidate identities and applicability produced by one replay."""

    replay_input: SensitivityReplayInput
    candidate_ids: frozenset[Hashable]
    evaluated_count: int
    applicability: Applicability
    reason: str | None = None

    def __post_init__(self) -> None:
        """Validate candidate counts and explicit applicability semantics."""
        if type(self.evaluated_count) is not int or self.evaluated_count < 0:
            raise ValueError("evaluated_count must be a non-negative integer.")
        if len(self.candidate_ids) > self.evaluated_count:
            raise ValueError("candidate count cannot exceed evaluated_count.")
        if self.applicability not in {"applicable", "non_applicable"}:
            raise ValueError(
                "applicability must be applicable or non_applicable."
            )
        if self.applicability == "applicable":
            if self.evaluated_count == 0:
                raise ValueError(
                    "Applicable results require a positive evaluated_count."
                )
            if self.reason is not None:
                raise ValueError(
                    "Applicable results must not include a reason."
                )
        elif self.candidate_ids:
            raise ValueError(
                "Non-applicable results must not contain candidate identities."
            )
        elif not self.reason:
            raise ValueError("Non-applicable results require a reason.")


@dataclass(frozen=True, slots=True)
class SensitivityRunSummary:
    """Auditable sensitivity measures for one replay policy."""

    replay_input: SensitivityReplayInput
    candidate_count: int
    candidate_rate: float | None
    applicability: Applicability
    reason: str | None
    identity_jaccard: float | None


@dataclass(frozen=True, slots=True)
class SensitivitySummary:
    """Complete deterministic replay evidence and stability qualification."""

    configuration: ParameterGrid
    replay_inputs: tuple[SensitivityReplayInput, ...]
    results: tuple[SensitivityReplayResult, ...]
    reference_run_id: str
    runs: tuple[SensitivityRunSummary, ...]
    minimum_identity_jaccard: float | None
    qualification: Qualification


def build_replay_inputs(
    configuration: ParameterGrid,
) -> tuple[SensitivityReplayInput, ...]:
    """Expand frozen ranges and seeds into deterministic replay inputs.

    Range order, value order, and seed order are preserved. No observed target
    result participates in this expansion.

    Returns:
        Complete Cartesian parameter grid with one input per seed.
    """
    parameter_names = tuple(
        name for name, _values in configuration.varied_parameters
    )
    value_ranges = tuple(
        values for _name, values in configuration.varied_parameters
    )
    replay_inputs: list[SensitivityReplayInput] = []
    for varied_values in product(*value_ranges):
        varied = tuple(zip(parameter_names, varied_values, strict=True))
        parameters = (*configuration.fixed_controls, *varied)
        for seed in configuration.seeds:
            run_id = _run_id(configuration.configuration_id, parameters, seed)
            replay_inputs.append(
                SensitivityReplayInput(
                    experiment_id=configuration.configuration_id,
                    run_id=run_id,
                    method=configuration.method,
                    parameters=parameters,
                    seed=seed,
                )
            )
    return tuple(replay_inputs)


def identity_jaccard(
    left: Iterable[Hashable],
    right: Iterable[Hashable],
) -> float:
    """Compute identity Jaccard with explicit empty-set semantics.

    Two empty candidate sets have overlap 1.0. Exactly one empty set has
    overlap 0.0.

    Returns:
        Intersection size divided by union size, or 1.0 for two empty sets.
    """
    left_set = frozenset(left)
    right_set = frozenset(right)
    union = left_set | right_set
    if not union:
        return 1.0
    return len(left_set & right_set) / len(union)


def summarize_sensitivity(
    configuration: ParameterGrid,
    results: Iterable[SensitivityReplayResult],
    *,
    reference_run_id: str | None = None,
) -> SensitivitySummary:
    """Summarize candidate stability against one predeclared replay.

    Default reference is first replay input, making first value in every
    varied range and first seed the frozen baseline. Non-applicable results
    retain counts and reasons but receive no rate or overlap measure.

    Returns:
        Counts, rates, applicability, identity overlap, and qualification.

    Raises:
        ValueError: If results do not cover frozen replay inputs exactly once.
    """
    replay_inputs = build_replay_inputs(configuration)
    ordered_results = _order_results(replay_inputs, tuple(results))
    selected_reference = reference_run_id or replay_inputs[0].run_id
    by_run_id = {
        result.replay_input.run_id: result for result in ordered_results
    }
    if selected_reference not in by_run_id:
        raise ValueError("reference_run_id is not in the frozen replay grid.")
    reference = by_run_id[selected_reference]

    run_summaries = tuple(
        _summarize_run(result, reference) for result in ordered_results
    )
    comparison_overlaps = [
        run.identity_jaccard
        for run in run_summaries
        if run.replay_input.run_id != selected_reference
        and run.identity_jaccard is not None
    ]
    minimum_overlap = min(comparison_overlaps) if comparison_overlaps else None
    if minimum_overlap is None:
        qualification: Qualification = "non_applicable"
    elif minimum_overlap < configuration.stability_threshold:
        qualification = "sensitive"
    else:
        qualification = "stable"

    return SensitivitySummary(
        configuration=configuration,
        replay_inputs=replay_inputs,
        results=ordered_results,
        reference_run_id=selected_reference,
        runs=run_summaries,
        minimum_identity_jaccard=minimum_overlap,
        qualification=qualification,
    )


def replay_sensitivity(
    configuration: ParameterGrid,
    evaluator: Callable[[SensitivityReplayInput], SensitivityReplayResult],
    *,
    reference_run_id: str | None = None,
) -> SensitivitySummary:
    """Evaluate every frozen input once, then summarize candidate stability.

    Returns:
        Deterministic replay inputs, raw results, and stability summary.
    """
    replay_inputs = build_replay_inputs(configuration)
    results = tuple(evaluator(replay_input) for replay_input in replay_inputs)
    return summarize_sensitivity(
        configuration,
        results,
        reference_run_id=reference_run_id,
    )


def _validate_parameter_declaration(
    varied_parameters: tuple[tuple[str, tuple[ParameterValue, ...]], ...],
    fixed_controls: tuple[tuple[str, ParameterValue], ...],
) -> None:
    """Require named, non-overlapping, non-empty frozen parameter records."""
    varied_names = [name for name, _values in varied_parameters]
    fixed_names = [name for name, _value in fixed_controls]
    if any(not name.strip() for name in (*varied_names, *fixed_names)):
        raise ValueError("Parameter names must not be empty.")
    if len(set(varied_names)) != len(varied_names):
        raise ValueError("Varied parameter names must not contain duplicates.")
    if len(set(fixed_names)) != len(fixed_names):
        raise ValueError("Fixed control names must not contain duplicates.")
    if set(varied_names) & set(fixed_names):
        raise ValueError(
            "Varied parameters and fixed controls must not overlap."
        )
    if any(not values for _name, values in varied_parameters):
        raise ValueError("Every varied parameter requires a non-empty range.")
    if any(
        len(set(values)) != len(values) for _name, values in varied_parameters
    ):
        raise ValueError(
            "Varied parameter ranges must not contain duplicates."
        )


def _run_id(
    experiment_id: str,
    parameters: tuple[tuple[str, ParameterValue], ...],
    seed: int,
) -> str:
    """Serialize one deterministic sensitivity replay identity."""
    serialized = "|".join(f"{name}={value!r}" for name, value in parameters)
    return f"{experiment_id}|{serialized}|seed={seed}"


def _order_results(
    replay_inputs: tuple[SensitivityReplayInput, ...],
    results: tuple[SensitivityReplayResult, ...],
) -> tuple[SensitivityReplayResult, ...]:
    """Validate exact grid coverage and restore declared replay order."""
    if len(results) != len(replay_inputs):
        raise ValueError(
            "Expected exactly one result per frozen replay input."
        )
    result_by_id: dict[str, SensitivityReplayResult] = {}
    expected_by_id = {
        replay_input.run_id: replay_input for replay_input in replay_inputs
    }
    for result in results:
        run_id = result.replay_input.run_id
        if run_id in result_by_id:
            raise ValueError(
                "Expected exactly one result per frozen replay input."
            )
        expected_input = expected_by_id.get(run_id)
        if expected_input is None or result.replay_input != expected_input:
            raise ValueError("Result does not match a frozen replay input.")
        result_by_id[run_id] = result
    if result_by_id.keys() != expected_by_id.keys():
        raise ValueError(
            "Expected exactly one result per frozen replay input."
        )
    return tuple(result_by_id[item.run_id] for item in replay_inputs)


def _summarize_run(
    result: SensitivityReplayResult,
    reference: SensitivityReplayResult,
) -> SensitivityRunSummary:
    """Compute one result's count, rate, and candidate identity overlap."""
    applicable = result.applicability == "applicable"
    reference_applicable = reference.applicability == "applicable"
    candidate_rate = (
        len(result.candidate_ids) / result.evaluated_count
        if applicable
        else None
    )
    overlap = (
        identity_jaccard(reference.candidate_ids, result.candidate_ids)
        if applicable and reference_applicable
        else None
    )
    return SensitivityRunSummary(
        replay_input=result.replay_input,
        candidate_count=len(result.candidate_ids),
        candidate_rate=candidate_rate,
        applicability=result.applicability,
        reason=result.reason,
        identity_jaccard=overlap,
    )
