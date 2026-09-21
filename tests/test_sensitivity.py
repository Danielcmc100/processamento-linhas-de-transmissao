"""Unit tests for predeclared parameter-sensitivity evidence."""

from dataclasses import FrozenInstanceError

import pytest

from src.services.sensitivity import (
    Applicability,
    ParameterGrid,
    SensitivityReplayInput,
    SensitivityReplayResult,
    build_replay_inputs,
    identity_jaccard,
    replay_sensitivity,
    summarize_sensitivity,
)


def _grid() -> ParameterGrid:
    return ParameterGrid(
        configuration_id="kmeans-sensitivity-v1",
        method="kmeans",
        varied_parameters=(("n_clusters", (2, 3)),),
        fixed_controls=(
            ("feature", "value_pu"),
            ("threshold_policy", "development_p99"),
        ),
        seeds=(17, 23),
        evaluation_measures=(
            "candidate_count",
            "candidate_rate",
            "applicability",
            "identity_jaccard",
        ),
        stability_threshold=0.80,
        stability_rationale="Predeclared thesis qualification threshold.",
    )


def _result(
    replay_input: SensitivityReplayInput,
    candidates: set[str],
    *,
    evaluated_count: int = 10,
    applicability: Applicability = "applicable",
) -> SensitivityReplayResult:
    return SensitivityReplayResult(
        replay_input=replay_input,
        candidate_ids=frozenset(candidates),
        evaluated_count=evaluated_count,
        applicability=applicability,
        reason=None if applicability == "applicable" else "Degenerate fit.",
    )


def test_grid_records_frozen_declaration_before_replay() -> None:
    grid = _grid()

    assert grid.varied_parameters == (("n_clusters", (2, 3)),)
    assert grid.parameter_ranges == (("n_clusters", (2, 3)),)
    assert grid.fixed_controls[0] == ("feature", "value_pu")
    assert grid.seeds == (17, 23)
    assert grid.stability_threshold == 0.80
    assert "identity_jaccard" in grid.evaluation_measures
    with pytest.raises(FrozenInstanceError):
        grid.method = "dbscan"  # type: ignore[misc]


def test_builds_complete_replay_grid_in_stable_order() -> None:
    inputs = build_replay_inputs(_grid())

    assert len(inputs) == 4
    assert [item.seed for item in inputs] == [17, 23, 17, 23]
    assert [item.parameter("n_clusters") for item in inputs] == [2, 2, 3, 3]
    assert all(item.parameter("feature") == "value_pu" for item in inputs)
    assert len({item.run_id for item in inputs}) == 4
    assert inputs == build_replay_inputs(_grid())


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (set(), set(), 1.0),
        ({"a"}, set(), 0.0),
        ({"a", "b"}, {"b", "c"}, 1 / 3),
        ({"a", "b"}, {"a", "b"}, 1.0),
    ],
)
def test_identity_jaccard_has_explicit_empty_set_semantics(
    left: set[str],
    right: set[str],
    expected: float,
) -> None:
    assert identity_jaccard(left, right) == pytest.approx(expected)


def test_summary_exposes_counts_rates_applicability_and_overlap() -> None:
    grid = _grid()
    inputs = build_replay_inputs(grid)
    results = (
        _result(inputs[0], {"a", "b"}),
        _result(inputs[1], {"a"}),
        _result(
            inputs[2],
            set(),
            evaluated_count=0,
            applicability="non_applicable",
        ),
        _result(inputs[3], {"a", "b"}),
    )

    summary = summarize_sensitivity(grid, results)

    assert summary.reference_run_id == inputs[0].run_id
    assert summary.runs[0].candidate_count == 2
    assert summary.runs[0].candidate_rate == pytest.approx(0.2)
    assert summary.runs[0].identity_jaccard == 1.0
    assert summary.runs[2].candidate_rate is None
    assert summary.runs[2].identity_jaccard is None
    assert summary.runs[2].applicability == "non_applicable"


def test_same_rates_with_different_identities_are_sensitive() -> None:
    grid = _grid()
    inputs = build_replay_inputs(grid)
    results = tuple(
        _result(
            replay_input,
            {"a", "b"} if index == 0 else {"c", "d"},
        )
        for index, replay_input in enumerate(inputs)
    )

    summary = summarize_sensitivity(grid, results)

    assert {run.candidate_rate for run in summary.runs} == {0.2}
    assert summary.minimum_identity_jaccard == 0.0
    assert summary.qualification == "sensitive"


def test_threshold_boundary_is_stable_but_lower_overlap_is_sensitive() -> None:
    grid = _grid()
    inputs = build_replay_inputs(grid)
    stable_results = (
        _result(inputs[0], {"a", "b", "c", "d", "e"}),
        _result(inputs[1], {"a", "b", "c", "d"}),
        _result(inputs[2], {"a", "b", "c", "d", "e"}),
        _result(inputs[3], {"a", "b", "c", "d", "e"}),
    )
    sensitive_results = (
        *stable_results[:1],
        _result(inputs[1], {"a", "b", "c"}),
        *stable_results[2:],
    )

    assert (
        summarize_sensitivity(grid, stable_results).qualification == "stable"
    )
    assert (
        summarize_sensitivity(grid, sensitive_results).qualification
        == "sensitive"
    )


def test_replay_is_deterministic_and_returns_inputs_with_results() -> None:
    grid = _grid()

    def evaluator(
        replay_input: SensitivityReplayInput,
    ) -> SensitivityReplayResult:
        candidates = {f"candidate-{replay_input.seed % 2}"}
        return _result(replay_input, candidates)

    first = replay_sensitivity(grid, evaluator)
    second = replay_sensitivity(grid, evaluator)

    assert first == second
    assert first.replay_inputs == build_replay_inputs(grid)
    assert tuple(run.replay_input for run in first.results) == (
        first.replay_inputs
    )


def test_rejects_unfrozen_or_incomplete_replay_evidence() -> None:
    with pytest.raises(ValueError, match="at least one varied parameter"):
        ParameterGrid(
            configuration_id="invalid",
            method="kmeans",
            varied_parameters=(),
            fixed_controls=(),
            seeds=(1,),
        )

    grid = _grid()
    inputs = build_replay_inputs(grid)
    with pytest.raises(ValueError, match="exactly one result"):
        summarize_sensitivity(grid, (_result(inputs[0], {"a"}),))

    with pytest.raises(ValueError, match="cannot exceed evaluated_count"):
        _result(inputs[0], {"a", "b"}, evaluated_count=1)
