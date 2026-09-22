"""Integration tests for controlled benchmark execution."""

from polars import DataFrame

from src.services.controlled_benchmark_runner import (
    run_controlled_benchmark,
)


def _observations() -> DataFrame:
    rows: list[dict[str, object]] = []
    for simulation in range(1, 201):
        rows.append({
            "scenario": "SRPI",
            "sample_size": 1_000,
            "source_lineage": "srpi-1000",
            "source_file": "case.lis",
            "source_sha256": "a" * 64,
            "simulation": simulation,
            "terminal": "T_MAN",
            "phase": "A",
            "source_value": 112_677.0 + simulation * 100.0,
            "value_pu": 1.0 + simulation / 1_000,
            "time": simulation / 1_000,
            "base_voltage": 112_677.0,
            "event_definition": "absolute_phase_to_ground_maximum",
        })
    return DataFrame(rows)


def test_runner_aligns_method_evidence_before_concatenation() -> None:
    result = run_controlled_benchmark(_observations())

    methods = set(result.metrics["method"].to_list())
    assert methods == {"dbscan_density_novelty", "kmeans"}
    assert (
        result.metrics.filter(
            result.metrics["intervention_family"] == "clean"
        ).height
        == 2
    )
    assert not result.intervention_manifest.is_empty()
