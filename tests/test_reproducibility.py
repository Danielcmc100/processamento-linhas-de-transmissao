"""Tests for claim traceability and reproducibility manifests."""

import json
from hashlib import sha256
from pathlib import Path

import pytest
from PIL import Image, PngImagePlugin

from src.services.reproducibility import (
    GENERATOR_VERSION,
    SCHEMA_VERSION,
    artifacts_semantically_equal,
    build_claim_evidence_row,
    build_reproducibility_manifest,
    semantic_sha256,
    validate_reproducibility_manifest,
)


def _claim(status: str = "accepted") -> dict[str, object]:
    return build_claim_evidence_row(
        requirement_id="DEF-05",
        claim_id="claim-probability",
        claim="Empirical exceedance includes uncertainty.",
        code_paths=("src/services/statistical_evidence.py",),
        test_paths=("tests/test_statistical_evidence.py",),
        data_paths=("input/source.lis",),
        output_artifacts=("probability.csv",),
        figure_table_labels=("tab:probability",),
        manuscript_sections=("sec:results",),
        status=status,
    )


def test_claim_evidence_row_maps_every_required_layer() -> None:
    row = _claim()

    assert row == {
        "requirement_id": "DEF-05",
        "claim_id": "claim-probability",
        "claim": "Empirical exceedance includes uncertainty.",
        "code_paths": ["src/services/statistical_evidence.py"],
        "test_paths": ["tests/test_statistical_evidence.py"],
        "data_paths": ["input/source.lis"],
        "output_artifacts": ["probability.csv"],
        "figure_table_labels": ["tab:probability"],
        "manuscript_sections": ["sec:results"],
        "status": "accepted",
    }


def test_manifest_records_complete_reproduction_provenance(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.lis"
    output = tmp_path / "probability.csv"
    source.write_bytes(b"source-data")
    output.write_bytes(b"value\n0.1\n")

    manifest = build_reproducibility_manifest(
        source_files={"source": source},
        configuration={"threshold": 2.3},
        code_revision="abc123",
        dependencies={"polars": "1.0.0", "python": "3.13.0"},
        commands=("uv run pytest", "python scripts/build.py"),
        output_files={"probability": output},
        generated_at_utc="2026-09-21T12:00:00+00:00",
        validation_statuses={"tests": "passed", "latex": "passed"},
        claim_evidence=(_claim(),),
    )

    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["generator_version"] == GENERATOR_VERSION
    assert manifest["generated_at_utc"] == "2026-09-21T12:00:00+00:00"
    assert manifest["code_revision"] == "abc123"
    assert manifest["dependencies"] == {
        "polars": "1.0.0",
        "python": "3.13.0",
    }
    assert manifest["commands"] == [
        "uv run pytest",
        "python scripts/build.py",
    ]
    assert (
        manifest["configuration"]["sha256"]
        == sha256(b'{"threshold":2.3}').hexdigest()
    )
    assert (
        manifest["sources"][0]["sha256"] == sha256(b"source-data").hexdigest()
    )
    assert (
        manifest["outputs"][0]["sha256"] == sha256(b"value\n0.1\n").hexdigest()
    )
    assert manifest["package_status"] == "complete"
    validate_reproducibility_manifest(manifest)


def test_failed_gate_keeps_package_incomplete(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.csv"
    artifact.write_text("value\n1\n", encoding="utf-8")

    manifest = build_reproducibility_manifest(
        source_files={"source": artifact},
        configuration={},
        code_revision="abc123",
        dependencies={"python": "3.13.0"},
        commands=("uv run pytest",),
        output_files={"artifact": artifact},
        generated_at_utc="2026-09-21T12:00:00Z",
        validation_statuses={"tests": "failed"},
        claim_evidence=(_claim(),),
    )

    assert manifest["package_status"] == "incomplete"
    assert manifest["validation_statuses"] == {"tests": "failed"}


def test_json_semantic_hash_excludes_only_declared_fields(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        json.dumps({"runtime": {"generated_at": "one"}, "value": 4}),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps({"value": 4, "runtime": {"generated_at": "two"}}),
        encoding="utf-8",
    )

    exclusions = ("runtime.generated_at",)
    assert semantic_sha256(first, json_exclusions=exclusions) == (
        semantic_sha256(second, json_exclusions=exclusions)
    )
    assert artifacts_semantically_equal(
        first,
        second,
        json_exclusions=exclusions,
    )
    assert not artifacts_semantically_equal(first, second)


def test_semantic_equality_never_hides_analytical_json_changes(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        json.dumps({"generated_at": "one", "probability": 0.1}),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps({"generated_at": "two", "probability": 0.2}),
        encoding="utf-8",
    )

    assert not artifacts_semantically_equal(
        first,
        second,
        json_exclusions=("generated_at",),
    )


def test_image_semantics_ignore_metadata_but_preserve_pixels(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    changed = tmp_path / "changed.png"
    metadata_one = PngImagePlugin.PngInfo()
    metadata_one.add_text("generated_at", "one")
    metadata_two = PngImagePlugin.PngInfo()
    metadata_two.add_text("generated_at", "two")
    Image.new("RGB", (2, 2), (1, 2, 3)).save(first, pnginfo=metadata_one)
    Image.new("RGB", (2, 2), (1, 2, 3)).save(second, pnginfo=metadata_two)
    Image.new("RGB", (2, 2), (9, 2, 3)).save(changed)

    assert first.read_bytes() != second.read_bytes()
    assert artifacts_semantically_equal(first, second)
    assert not artifacts_semantically_equal(first, changed)


def test_manifest_declares_semantic_exclusions(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"
    output.write_text(
        json.dumps({"generated_at": "now", "value": 1}),
        encoding="utf-8",
    )

    manifest = build_reproducibility_manifest(
        source_files={"source": output},
        configuration={},
        code_revision="abc123",
        dependencies={"python": "3.13.0"},
        commands=("python build.py",),
        output_files={"evidence": output},
        generated_at_utc="2026-09-21T12:00:00Z",
        validation_statuses={"tests": "passed"},
        claim_evidence=(_claim(),),
        nondeterministic_json_fields={"evidence": ("generated_at",)},
    )

    output_record = manifest["outputs"][0]
    assert output_record["semantic_sha256"] == semantic_sha256(
        output,
        json_exclusions=("generated_at",),
    )
    assert manifest["semantic_hash_policy"] == {
        "json_exclusions": {"evidence": ["generated_at"]},
        "image_metadata": "excluded",
    }


def test_old_schema_is_rejected_with_expected_and_actual() -> None:
    with pytest.raises(
        ValueError,
        match=("Reproducibility schema mismatch: expected 1.0.0, got 0.9.0"),
    ):
        validate_reproducibility_manifest({"schema_version": "0.9.0"})


def test_manifest_is_deterministic_for_same_declared_inputs(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "artifact.csv"
    artifact.write_text("value\n1\n", encoding="utf-8")
    arguments = {
        "source_files": {"source": artifact},
        "configuration": {"seed": 42},
        "code_revision": "abc123",
        "dependencies": {"python": "3.13.0"},
        "commands": ("python build.py",),
        "output_files": {"artifact": artifact},
        "generated_at_utc": "2026-09-21T12:00:00Z",
        "validation_statuses": {"tests": "passed"},
        "claim_evidence": (_claim(),),
    }

    assert build_reproducibility_manifest(**arguments) == (
        build_reproducibility_manifest(**arguments)
    )
