"""Tests for deterministic controlled perturbation datasets."""

import pytest
from polars import DataFrame, Int64
from polars.testing import assert_frame_equal

from src.services.perturbations import (
    GENERATOR_VERSION,
    generate_controlled_perturbations,
    split_by_source_run,
)


def _observations(count: int = 100) -> DataFrame:
    return DataFrame({
        "scenario": ["SRPI"] * count,
        "sample_size": [count] * count,
        "source_lineage": ["lineage-a"] * count,
        "source_file": ["case.lis"] * count,
        "source_sha256": ["a" * 64] * count,
        "simulation": list(range(1, count + 1)),
        "terminal": ["T_MAN"] * count,
        "phase": ["A"] * count,
        "value_pu": [1.0 + index / 100 for index in range(count)],
    })


def test_clean_control_is_copied_and_unlabeled() -> None:
    original = _observations(10)
    snapshot = original.clone()

    result = generate_controlled_perturbations(
        original,
        family="clean",
        contamination_rate=0.0,
        intensity=0.0,
        seed=17,
    )

    assert_frame_equal(original, snapshot)
    assert result.status == "applicable"
    assert result.manifest.is_empty()
    assert not any(result.data["controlled_label"])
    assert result.data["intervention_family"].unique().to_list() == ["clean"]


def test_point_perturbation_is_deterministic_and_preserves_input() -> None:
    original = _observations()
    snapshot = original.clone()

    first = generate_controlled_perturbations(
        original,
        family="point",
        contamination_rate=0.05,
        intensity=0.5,
        seed=42,
    )
    second = generate_controlled_perturbations(
        original,
        family="point",
        contamination_rate=0.05,
        intensity=0.5,
        seed=42,
    )

    assert_frame_equal(original, snapshot)
    assert_frame_equal(first.data, second.data)
    assert_frame_equal(first.manifest, second.manifest)
    assert first.manifest.height == 5


def test_manifest_preserves_identity_values_and_configuration() -> None:
    result = generate_controlled_perturbations(
        _observations(),
        family="point",
        contamination_rate=0.01,
        intensity=0.25,
        seed=11,
    )

    row = result.manifest.row(0, named=True)
    assert row["scenario"] == "SRPI"
    assert row["source_lineage"] == "lineage-a"
    assert row["source_file"] == "case.lis"
    assert row["source_sha256"] == "a" * 64
    assert row["simulation"] >= 1
    assert row["terminal"] == "T_MAN"
    assert row["phase"] == "A"
    assert row["injected_value"] == pytest.approx(row["original_value"] + 0.25)
    assert row["intervention_family"] == "point"
    assert row["intensity"] == 0.25
    assert row["requested_contamination_rate"] == 0.01
    assert row["effective_contamination_rate"] == 0.01
    assert row["seed"] == 11
    assert row["generator_version"] == GENERATOR_VERSION


@pytest.mark.parametrize("rate", [0.01, 0.05, 0.10])
def test_predeclared_point_contamination_rates(rate: float) -> None:
    result = generate_controlled_perturbations(
        _observations(),
        family="point",
        contamination_rate=rate,
        intensity=0.5,
        seed=3,
    )

    assert result.status == "applicable"
    assert result.manifest.height == int(100 * rate)
    assert result.effective_contamination_rate == pytest.approx(rate)


def test_contextual_perturbation_uses_group_relative_value() -> None:
    observations = _observations()

    result = generate_controlled_perturbations(
        observations,
        family="contextual",
        contamination_rate=0.01,
        intensity=4.0,
        seed=9,
    )

    row = result.manifest.row(0, named=True)
    assert row["injected_value"] != row["original_value"]
    assert row["intervention_family"] == "contextual"
    assert result.data["controlled_label"].sum() == 1


def test_collective_perturbation_changes_contiguous_runs_and_peers() -> None:
    rows = []
    for simulation in range(1, 21):
        for phase in ("A", "B", "C"):
            rows.append({
                "scenario": "SRPI",
                "sample_size": 20,
                "source_lineage": "lineage-a",
                "source_file": "case.lis",
                "source_sha256": "a" * 64,
                "simulation": simulation,
                "terminal": "T_MAN",
                "phase": phase,
                "value_pu": 1.0,
            })
    observations = DataFrame(rows)

    result = generate_controlled_perturbations(
        observations,
        family="collective",
        contamination_rate=0.10,
        intensity=0.4,
        seed=21,
    )

    simulations = sorted(result.manifest["simulation"].unique().to_list())
    assert len(simulations) == 2
    assert simulations[1] == simulations[0] + 1
    assert result.manifest.height == 6
    assert set(result.manifest["phase"]) == {"A", "B", "C"}


def test_infeasible_rate_is_explicit_for_small_dataset() -> None:
    result = generate_controlled_perturbations(
        _observations(10),
        family="point",
        contamination_rate=0.01,
        intensity=0.5,
        seed=2,
    )

    assert result.status == "infeasible"
    assert result.reason == (
        "Requested contamination selects zero observations."
    )
    assert result.manifest.is_empty()
    assert not any(result.data["controlled_label"])


def test_split_keeps_all_source_run_peers_together() -> None:
    rows = []
    for lineage in ("lineage-a", "lineage-b"):
        for simulation in range(1, 11):
            for terminal in ("T_MAN", "T_OPO"):
                for phase in ("A", "B", "C"):
                    rows.append({
                        "source_lineage": lineage,
                        "simulation": simulation,
                        "terminal": terminal,
                        "phase": phase,
                        "value_pu": 1.0,
                    })
    observations = DataFrame(rows)

    first = split_by_source_run(
        observations,
        development_fraction=0.7,
        seed=31,
    )
    second = split_by_source_run(
        observations,
        development_fraction=0.7,
        seed=31,
    )

    assert_frame_equal(first, second)
    peer_split_counts = (
        first
        .group_by("source_lineage", "simulation")
        .agg("benchmark_split")
        .select("benchmark_split")
        .to_series()
        .map_elements(lambda values: len(set(values)), return_dtype=Int64)
    )
    assert peer_split_counts.max() == 1
    assert set(first["benchmark_split"]) == {"development", "evaluation"}
