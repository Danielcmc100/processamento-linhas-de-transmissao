"""Tests for final defense-evidence package orchestration."""

from pathlib import Path

import pytest

from scripts.build_defense_evidence import (
    _dataset_manifest_frame,
    build_defense_evidence,
)
from src.services.dataset_manifest import DatasetManifestEntry


def test_nonempty_output_requires_explicit_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "evidence"
    output.mkdir()
    existing = output / "keep.txt"
    existing.write_text("preserve", encoding="utf-8")

    with pytest.raises(FileExistsError, match="already contains"):
        build_defense_evidence(
            root=tmp_path / "unused",
            output=output,
        )

    assert existing.read_text(encoding="utf-8") == "preserve"


def test_dataset_manifest_frame_preserves_provenance() -> None:
    entry = DatasetManifestEntry(
        scenario="SRPI",
        sample_size=50,
        source_path="50/case.lis",
        source_sha256="a" * 64,
        expected_run_count=50,
        declared_run_count=50,
        effective_run_count=50,
        terminals=("T_MAN", "T_OPO"),
        phases=("A", "B", "C"),
        base_voltage=112_677.0,
        time_window=(0.0, 0.3),
        event_definition="maximum",
        experiment_assumptions=("separate scenarios",),
        relationship_status="independence_not_established",
        coverage_status="present",
        included=True,
        exclusion_reasons=(),
    )

    row = _dataset_manifest_frame((entry,)).row(0, named=True)

    assert row["source_sha256"] == "a" * 64
    assert row["terminals"] == "T_MAN|T_OPO"
    assert row["phases"] == "A|B|C"
    assert row["time_window"] == "0.0|0.3"
    assert row["experiment_assumptions"] == "separate scenarios"
    assert row["exclusion_reasons"] == ""
