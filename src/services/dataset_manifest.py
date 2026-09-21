"""Canonical source manifest for thesis-defense ATP datasets."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from re import compile as compile_pattern
from typing import Iterable

ACCEPTED_BASE_VOLTAGE = 112_677.0
DEFAULT_EVENT_DEFINITION = (
    "maximum absolute phase-to-ground voltage from 0.0 to 0.3 seconds"
)
SAMPLE_SIZES = (50, 100, 200, 1_000, 10_000)
SCENARIOS = ("SRPI", "CRPI")
TERMINALS = ("T_MAN", "1_2LT", "T_OPO")
PHASES = ("A", "B", "C")
DEFAULT_TIME_WINDOW = (0.0, 0.3)
DEFAULT_ASSUMPTIONS = (
    "SRPI and CRPI are analyzed separately before comparison.",
    "Sample-size source independence is not established.",
)

_NENERG_PATTERN = compile_pattern(rb"NENERG\s*=\s*(\d+)")
_RUN_PATTERN = compile_pattern(
    rb"Random switching times for simulation number\s+(\d+)\s*:"
)
_BASE_PATTERN = compile_pattern(
    rb"Statistical output of\s+node\s+voltage.*?"
    rb"\|0\s+([0-9]+(?:\.[0-9]*)?)\.?(?:T_MAN[ABC])"
)


@dataclass(frozen=True, slots=True)
class DatasetManifestEntry:
    """Provenance and compatibility record for one ATP source."""

    scenario: str
    sample_size: int
    source_path: str
    source_sha256: str
    expected_run_count: int
    declared_run_count: int | None
    effective_run_count: int | None
    terminals: tuple[str, ...]
    phases: tuple[str, ...]
    base_voltage: float | None
    time_window: tuple[float, float]
    event_definition: str
    experiment_assumptions: tuple[str, ...]
    relationship_status: str
    coverage_status: str
    included: bool
    exclusion_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DatasetManifestValidation:
    """Coverage and exclusion summary for a dataset manifest."""

    is_valid: bool
    missing_coverage: tuple[tuple[str, int], ...]
    exclusions: dict[tuple[str, int], tuple[str, ...]]


@dataclass(frozen=True, slots=True)
class _SourceDeclarations:
    """Declarations obtained without materializing parsed observations."""

    source_sha256: str
    declared_run_count: int | None
    effective_run_count: int
    base_voltage: float | None
    conflicting_base: bool


def build_dataset_manifest(
    root: Path | str = Path("input_files/casos"),
) -> tuple[DatasetManifestEntry, ...]:
    """Discover canonical scenario-size sources in deterministic order.

    Args:
        root: Directory containing ``{size}-simulacoes`` directories.

    Returns:
        Ten manifest rows, including explicit rows for missing sources.
    """
    source_root = Path(root)
    entries: list[DatasetManifestEntry] = []
    for sample_size in SAMPLE_SIZES:
        for scenario in SCENARIOS:
            path = _canonical_path(source_root, sample_size, scenario)
            entries.append(
                _build_entry(
                    source_root,
                    path,
                    sample_size,
                    scenario,
                )
            )
    return tuple(entries)


def validate_dataset_manifest(
    entries: Iterable[DatasetManifestEntry],
) -> DatasetManifestValidation:
    """Validate coverage, provenance, and comparison compatibility.

    Returns:
        Deterministic coverage and exact exclusion details.
    """
    manifest = tuple(entries)
    observed_keys = {
        (entry.scenario, entry.sample_size)
        for entry in manifest
        if entry.coverage_status == "present"
    }
    required_keys = {
        (scenario, sample_size)
        for sample_size in SAMPLE_SIZES
        for scenario in SCENARIOS
    }
    missing = tuple(
        (scenario, sample_size)
        for sample_size in SAMPLE_SIZES
        for scenario in SCENARIOS
        if (scenario, sample_size) not in observed_keys
    )
    exclusions: dict[tuple[str, int], tuple[str, ...]] = {}
    for entry in manifest:
        reasons = list(entry.exclusion_reasons)
        if entry.coverage_status == "missing":
            exclusions[(entry.scenario, entry.sample_size)] = tuple(reasons)
            continue
        if not _is_sha256(entry.source_sha256):
            _append_unique(
                reasons,
                "source SHA-256 provenance is missing or invalid",
            )
        if entry.declared_run_count != entry.expected_run_count:
            declared = entry.declared_run_count
            if declared is None:
                _append_unique(reasons, "single NENERG declaration not found")
            else:
                _append_unique(
                    reasons,
                    f"declared NENERG {declared} does not equal expected "
                    f"{entry.expected_run_count}",
                )
        elif entry.effective_run_count != entry.declared_run_count:
            _append_unique(
                reasons,
                "effective run count "
                f"{entry.effective_run_count} does not equal declared "
                f"NENERG {entry.declared_run_count}",
            )
        if entry.event_definition != DEFAULT_EVENT_DEFINITION:
            _append_unique(
                reasons,
                "event definition differs from canonical definition",
            )
        if entry.base_voltage != ACCEPTED_BASE_VOLTAGE:
            if entry.base_voltage is None:
                _append_unique(
                    reasons,
                    "base voltage declaration not found",
                )
            else:
                _append_unique(
                    reasons,
                    _invalid_base_reason(entry.base_voltage),
                )
        if not entry.experiment_assumptions:
            _append_unique(reasons, "experiment assumptions are missing")
        if reasons:
            exclusions[(entry.scenario, entry.sample_size)] = tuple(reasons)

    complete = required_keys == observed_keys
    return DatasetManifestValidation(
        is_valid=complete and not missing and not exclusions,
        missing_coverage=missing,
        exclusions=exclusions,
    )


def _canonical_path(root: Path, sample_size: int, scenario: str) -> Path:
    return (
        root
        / f"{sample_size}-simulacoes"
        / "casos"
        / "T_MAN"
        / scenario
        / "CASO-COMPLETO"
        / "SDEF"
        / "case.lis"
    )


def _build_entry(
    root: Path,
    path: Path,
    sample_size: int,
    scenario: str,
) -> DatasetManifestEntry:
    source_path = path.relative_to(root).as_posix()
    if not path.is_file():
        return DatasetManifestEntry(
            scenario=scenario,
            sample_size=sample_size,
            source_path=source_path,
            source_sha256="",
            expected_run_count=sample_size,
            declared_run_count=None,
            effective_run_count=None,
            terminals=TERMINALS,
            phases=PHASES,
            base_voltage=None,
            time_window=DEFAULT_TIME_WINDOW,
            event_definition=DEFAULT_EVENT_DEFINITION,
            experiment_assumptions=DEFAULT_ASSUMPTIONS,
            relationship_status="independence_not_established",
            coverage_status="missing",
            included=False,
            exclusion_reasons=("source file does not exist",),
        )

    declarations = _scan_source(path)
    reasons = _source_exclusions(declarations, sample_size)
    return DatasetManifestEntry(
        scenario=scenario,
        sample_size=sample_size,
        source_path=source_path,
        source_sha256=declarations.source_sha256,
        expected_run_count=sample_size,
        declared_run_count=declarations.declared_run_count,
        effective_run_count=declarations.effective_run_count,
        terminals=TERMINALS,
        phases=PHASES,
        base_voltage=declarations.base_voltage,
        time_window=DEFAULT_TIME_WINDOW,
        event_definition=DEFAULT_EVENT_DEFINITION,
        experiment_assumptions=DEFAULT_ASSUMPTIONS,
        relationship_status="independence_not_established",
        coverage_status="present",
        included=not reasons,
        exclusion_reasons=reasons,
    )


def _scan_source(path: Path) -> _SourceDeclarations:
    digest = sha256()
    declared_counts: set[int] = set()
    run_ids: set[int] = set()
    base_voltages: set[float] = set()
    with path.open("rb") as source:
        for line in source:
            digest.update(line)
            if match := _NENERG_PATTERN.search(line):
                declared_counts.add(int(match.group(1)))
            if match := _RUN_PATTERN.search(line):
                run_ids.add(int(match.group(1)))
            if match := _BASE_PATTERN.search(line):
                base_voltages.add(float(match.group(1)))
    declared = (
        next(iter(declared_counts)) if len(declared_counts) == 1 else None
    )
    base = next(iter(base_voltages)) if len(base_voltages) == 1 else None
    return _SourceDeclarations(
        source_sha256=digest.hexdigest(),
        declared_run_count=declared,
        effective_run_count=len(run_ids),
        base_voltage=base,
        conflicting_base=len(base_voltages) > 1,
    )


def _source_exclusions(
    declarations: _SourceDeclarations,
    expected_runs: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    declared = declarations.declared_run_count
    if declared is None:
        reasons.append("single NENERG declaration not found")
    elif declared != expected_runs:
        reasons.append(
            f"declared NENERG {declared} does not equal expected "
            f"{expected_runs}"
        )
    if (
        declared == expected_runs
        and declarations.effective_run_count != declared
    ):
        reasons.append(
            "effective run count "
            f"{declarations.effective_run_count} does not equal declared "
            f"NENERG {declared}"
        )
    if declarations.conflicting_base:
        reasons.append("conflicting base voltage declarations found")
    elif declarations.base_voltage is None:
        reasons.append("base voltage declaration not found")
    elif declarations.base_voltage != ACCEPTED_BASE_VOLTAGE:
        reasons.append(_invalid_base_reason(declarations.base_voltage))
    return tuple(reasons)


def _invalid_base_reason(base_voltage: float) -> str:
    return (
        f"base voltage {base_voltage:g} V does not equal accepted "
        f"{ACCEPTED_BASE_VOLTAGE:g} V"
    )


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _append_unique(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)
