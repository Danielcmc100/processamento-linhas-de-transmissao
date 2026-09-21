"""Tests for canonical ATP dataset manifest discovery and validation."""

from hashlib import sha256
from pathlib import Path

from src.services.dataset_manifest import (
    ACCEPTED_BASE_VOLTAGE,
    DEFAULT_EVENT_DEFINITION,
    DatasetManifestEntry,
    build_dataset_manifest,
    validate_dataset_manifest,
)

SAMPLE_SIZES = (50, 100, 200, 1_000, 10_000)
SCENARIOS = ("SRPI", "CRPI")


def _case_path(root: Path, size: int, scenario: str) -> Path:
    return (
        root
        / f"{size}-simulacoes"
        / "casos"
        / "T_MAN"
        / scenario
        / "CASO-COMPLETO"
        / "SDEF"
        / "case.lis"
    )


def _write_case(
    root: Path,
    size: int,
    scenario: str,
    *,
    base_voltage: int = 112_677,
    declared_runs: int | None = None,
    effective_runs: int | None = None,
    include_base: bool = True,
) -> Path:
    path = _case_path(root, size, scenario)
    path.parent.mkdir(parents=True, exist_ok=True)
    declared = size if declared_runs is None else declared_runs
    effective = size if effective_runs is None else effective_runs
    lines = [f"NENERG = {declared}\n"]
    lines.extend(
        f"Random switching times for simulation number {run}:\n"
        for run in range(1, effective + 1)
    )
    if include_base:
        lines.append(
            "Statistical output of node voltage "
            f"0.1127E+06 |0      {base_voltage}.T_MANAT_MANBT_MANC\n"
        )
    path.write_text("".join(lines), encoding="latin-1")
    return path


def _write_matrix(root: Path) -> None:
    for size in SAMPLE_SIZES:
        for scenario in SCENARIOS:
            _write_case(root, size, scenario)


def test_build_manifest_discovers_ten_sources_deterministically(
    tmp_path: Path,
) -> None:
    _write_matrix(tmp_path)

    manifest = build_dataset_manifest(tmp_path)

    assert [(entry.sample_size, entry.scenario) for entry in manifest] == [
        (size, scenario) for size in SAMPLE_SIZES for scenario in SCENARIOS
    ]
    assert all(entry.coverage_status == "present" for entry in manifest)
    assert all(entry.included for entry in manifest)
    assert all(
        entry.base_voltage == ACCEPTED_BASE_VOLTAGE for entry in manifest
    )
    assert all(
        entry.terminals == ("T_MAN", "1_2LT", "T_OPO") for entry in manifest
    )
    assert all(entry.phases == ("A", "B", "C") for entry in manifest)
    assert all(
        entry.event_definition == DEFAULT_EVENT_DEFINITION
        for entry in manifest
    )


def test_build_manifest_records_hash_counts_and_assumptions(
    tmp_path: Path,
) -> None:
    path = _write_case(tmp_path, 50, "SRPI")

    entry = build_dataset_manifest(tmp_path)[0]

    assert entry.source_path == path.relative_to(tmp_path).as_posix()
    assert entry.source_sha256 == sha256(path.read_bytes()).hexdigest()
    assert entry.expected_run_count == 50
    assert entry.declared_run_count == 50
    assert entry.effective_run_count == 50
    assert entry.time_window == (0.0, 0.3)
    assert entry.experiment_assumptions
    assert entry.relationship_status == "independence_not_established"


def test_missing_source_has_explicit_coverage_and_exclusion(
    tmp_path: Path,
) -> None:
    _write_matrix(tmp_path)
    _case_path(tmp_path, 200, "CRPI").unlink()

    manifest = build_dataset_manifest(tmp_path)
    result = validate_dataset_manifest(manifest)
    missing = next(
        entry
        for entry in manifest
        if entry.sample_size == 200 and entry.scenario == "CRPI"
    )

    assert missing.coverage_status == "missing"
    assert not missing.included
    assert missing.exclusion_reasons == ("source file does not exist",)
    assert result.missing_coverage == (("CRPI", 200),)
    assert not result.is_valid


def test_wrong_base_is_excluded_with_exact_reason(tmp_path: Path) -> None:
    _write_case(tmp_path, 50, "SRPI", base_voltage=100_000)

    entry = build_dataset_manifest(tmp_path)[0]

    assert not entry.included
    assert entry.exclusion_reasons == (
        "base voltage 100000 V does not equal accepted 112677 V",
    )


def test_missing_base_provenance_fails_closed(tmp_path: Path) -> None:
    _write_case(tmp_path, 50, "SRPI", include_base=False)

    entry = build_dataset_manifest(tmp_path)[0]

    assert entry.base_voltage is None
    assert not entry.included
    assert entry.exclusion_reasons == ("base voltage declaration not found",)


def test_declared_count_mismatch_is_excluded(tmp_path: Path) -> None:
    _write_case(tmp_path, 50, "SRPI", declared_runs=49)

    entry = build_dataset_manifest(tmp_path)[0]

    assert not entry.included
    assert entry.exclusion_reasons == (
        "declared NENERG 49 does not equal expected 50",
    )


def test_effective_count_mismatch_is_excluded(tmp_path: Path) -> None:
    _write_case(tmp_path, 50, "SRPI", effective_runs=49)

    entry = build_dataset_manifest(tmp_path)[0]

    assert not entry.included
    assert entry.exclusion_reasons == (
        "effective run count 49 does not equal declared NENERG 50",
    )


def test_validation_rejects_missing_hash_and_incompatible_event() -> None:
    shared = {
        "sample_size": 50,
        "source_path": "source/case.lis",
        "expected_run_count": 50,
        "declared_run_count": 50,
        "effective_run_count": 50,
        "terminals": ("T_MAN", "1_2LT", "T_OPO"),
        "phases": ("A", "B", "C"),
        "base_voltage": ACCEPTED_BASE_VOLTAGE,
        "time_window": (0.0, 0.3),
        "experiment_assumptions": ("same model",),
        "relationship_status": "independence_not_established",
        "coverage_status": "present",
        "included": True,
        "exclusion_reasons": (),
    }
    entries = (
        DatasetManifestEntry(
            scenario="SRPI",
            source_sha256="",
            event_definition=DEFAULT_EVENT_DEFINITION,
            **shared,
        ),
        DatasetManifestEntry(
            scenario="CRPI",
            source_sha256="a" * 64,
            event_definition="different event",
            **shared,
        ),
    )

    result = validate_dataset_manifest(entries)

    assert not result.is_valid
    assert result.exclusions[("SRPI", 50)] == (
        "source SHA-256 provenance is missing or invalid",
    )
    assert result.exclusions[("CRPI", 50)] == (
        "event definition differs from canonical definition",
    )
