"""Tests for final defense-evidence package orchestration."""

from hashlib import sha256
from json import loads
from pathlib import Path

import pytest
from numpy.random import default_rng
from polars import DataFrame, col, read_csv

from scripts.build_defense_evidence import (
    _argument_parser,
    _dataset_manifest_frame,
    _generate_distribution_figures,
    build_defense_evidence,
)
from scripts.prepare_defense_document import main
from src.services.dataset_manifest import DatasetManifestEntry
from src.services.reproducibility import validate_reproducibility_manifest


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
        phase_to_phase_base_voltage=195_161.0,
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


def test_default_publication_routes_to_v3() -> None:
    assert _argument_parser().parse_args([]).output == Path(
        "results/defense-evidence/v3"
    )


def _fixture_entries(root: Path) -> tuple[DatasetManifestEntry, ...]:
    """Create small sources under nominal canonical comparison-size labels.

    Only discovery is replaced: all sources declare and contain 50 runs,
    regardless of their nominal size label. Validation, parsing, analysis,
    benchmark, sensitivity, publication, and hashing use real implementations.
    These sources cannot validate real-data coverage or canonical counts.

    Returns:
        Ten explicitly synthetic manifest records.
    """
    entries = []
    generator = default_rng(73)
    header = " ".join(
        terminal + phase
        for terminal in ("T_MAN", "1_2LT", "T_OPO")
        for phase in ("A", "B", "C")
    )
    lines = ["NENERG = 50", "otherwise blank space.", "", header, ""]
    for simulation in range(1, 51):
        values = [
            315_000.0 if simulation == 50 else generator.normal(170_000, 4_000)
            for _ in range(9)
        ]
        lines.extend([
            f"Random switching times for simulation number {simulation} :",
            "1 0.01",
            "",
            " ".join(str(value) for value in values),
            "Times of maxima :",
            " ".join(["0.02"] * 9),
            "",
        ])
    for phase in ("A", "B", "C"):
        lines.extend([
            "Statistical distribution of peak voltage at node "
            f'"T_MAN{phase}".',
            "The base voltage for per unit printout is "
            "V-base = 1.12677000E+05",
            "20  1.0000000  1.12677000E+05  0  0  100.000000",
            "Summary of preceding table follows:",
        ])
    for size in (50, 100, 200, 1_000, 10_000):
        for scenario in ("SRPI", "CRPI"):
            source = root / scenario / str(size) / "case.lis"
            source.parent.mkdir(parents=True)
            source.write_text("\n".join(lines), encoding="iso-8859-1")
            entries.append(
                DatasetManifestEntry(
                    scenario=scenario,
                    sample_size=size,
                    source_path=source.relative_to(root).as_posix(),
                    source_sha256=sha256(source.read_bytes()).hexdigest(),
                    expected_run_count=50,
                    declared_run_count=50,
                    effective_run_count=50,
                    terminals=("T_MAN", "1_2LT", "T_OPO"),
                    phases=("A", "B", "C"),
                    base_voltage=112_677.0,
                    phase_to_phase_base_voltage=195_161.0,
                    time_window=(0.0, 0.3),
                    event_definition=(
                        "maximum absolute phase-to-ground voltage from "
                        "0.0 to 0.3 seconds"
                    ),
                    experiment_assumptions=("Synthetic 50-run fixture only.",),
                    relationship_status="independence_not_established",
                    coverage_status="present",
                    included=True,
                    exclusion_reasons=(),
                )
            )
    return tuple(entries)


def test_fixture_package_consumes_pipeline_contract_and_copies_assets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "input"
    entries = _fixture_entries(root)
    monkeypatch.setattr(
        "scripts.build_defense_evidence.build_dataset_manifest",
        lambda _: entries,
    )
    output = tmp_path / "results/defense-evidence/v3"
    historical = []
    for version in ("v1", "v2"):
        path = output.parent / version / "keep.txt"
        path.parent.mkdir(parents=True)
        path.write_bytes(version.encode())
        historical.append(path)

    manifest_path = build_defense_evidence(root=root, output=output)

    matrix = read_csv(
        output / "sources/method_comparison.csv",
        missing_utf8_is_empty_string=True,
    )
    assert matrix.height == 4_500
    assert set(matrix["compared_methods"]) == {
        "mad_modified_z;kmeans_distance;dbscan_noise"
    }
    methods = (
        ("mad_flag", "mad_applicability", "mad_modified_z"),
        ("flag", "applicability", "kmeans_distance"),
        ("dbscan_flag", "dbscan_applicability", "dbscan_noise"),
    )
    for row in matrix.iter_rows(named=True):
        applicable = [item for item in methods if row[item[1]] == "applicable"]
        positive = [item[2] for item in applicable if row[item[0]] is True]
        assert row["applicable_method_count"] == len(applicable)
        assert row["method_agreement"] == len(positive)
        assert row["anomaly_candidate"] == bool(positive)
        assert row["method_disagreement"] == (
            0 < len(positive) < len(applicable)
        )
        assert row["anomaly_reasons"] == ";".join(positive)
    assert matrix["anomaly_candidate"].sum() > 0
    statistical = read_csv(output / "sources/statistical_evidence.csv")
    adequacy = read_csv(output / "sources/distribution_adequacy.csv")
    assert statistical.height == adequacy.height == 90
    assert set(statistical["denominator"]) == {50}
    assert {"fitted_mean", "fitted_standard_deviation", "decision"} <= set(
        adequacy.columns
    )
    assert adequacy["fitted_standard_deviation"].null_count() == 0
    convergence = read_csv(output / "sources/convergence.csv")
    expected = matrix.group_by(
        "scenario", "sample_size", "terminal", "phase"
    ).agg(col("anomaly_candidate").sum().alias("candidate_count"))
    scope = ["scenario", "sample_size", "terminal", "phase"]
    assert (
        convergence
        .select(*scope, "candidate_count")
        .sort(scope)
        .equals(expected.sort(scope))
    )
    assert set(convergence["method_policy"]) == {"defense-v3-three-methods"}
    for path in output.rglob("*.csv"):
        table = read_csv(path)
        assert not any("sigma" in name.lower() for name in table.columns)
        assert "sigma_3" not in path.read_text(encoding="utf-8")
    for path in output.rglob("*.tex"):
        assert "sigma" not in path.read_text(encoding="utf-8").lower()

    manifest = loads(manifest_path.read_text(encoding="utf-8"))
    validate_reproducibility_manifest(manifest)
    assert manifest["package_status"] == "incomplete"
    assert manifest["validation_statuses"]["technical_review"] == "incomplete"
    for record in [*manifest["sources"], *manifest["outputs"]]:
        assert (
            sha256(Path(record["path"]).read_bytes()).hexdigest()
            == (record["sha256"])
        )
    assert len(manifest["sources"]) == 10
    assert len(manifest["outputs"]) == len([
        path
        for path in output.rglob("*")
        if path.is_file() and path != manifest_path
    ])
    references = [
        "evidence/v3/" + path.relative_to(output).as_posix()
        for directory in ("tables", "figures")
        for path in sorted((output / directory).iterdir())
        if path.suffix in {".tex", ".pdf", ".png"}
    ]
    assert references
    document = tmp_path / "doc"
    document.mkdir()
    (document / "main.tex").write_text(
        "\n".join("{" + reference + "}" for reference in references),
        encoding="utf-8",
    )
    main(root=tmp_path)
    for reference in references:
        relative = Path(reference).relative_to("evidence/v3")
        assert (document / reference).read_bytes() == (
            output / relative
        ).read_bytes()
    for path in historical:
        assert path.read_bytes() == path.parent.name.encode()


def test_distribution_exports_use_shared_scenario_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from matplotlib.figure import Figure

    observations = DataFrame({
        "scenario": ["SRPI"] * 4 + ["CRPI"] * 4,
        "sample_size": [10_000] * 8,
        "terminal": ["T_OPO"] * 8,
        "phase": ["A"] * 8,
        "value_pu": [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
    })
    adequacy = DataFrame({
        "scenario": ["SRPI", "CRPI"],
        "sample_size": [10_000] * 2,
        "terminal": ["T_OPO"] * 2,
        "phase": ["A"] * 2,
        "fitted_mean": [0.95, 1.35],
        "fitted_standard_deviation": [0.13] * 2,
        "decision": ["rejected", "not_rejected"],
    })
    exports: list[tuple[str, list[tuple[float, float]]]] = []

    def capture(figure: Figure, output: Path) -> None:
        exports.append((
            output.name,
            [axis.get_xlim() for axis in figure.axes],
        ))

    monkeypatch.setattr(
        "scripts.build_defense_evidence.export_publication_figure", capture
    )
    _generate_distribution_figures(observations, adequacy, tmp_path)
    assert [name for name, _ in exports] == [
        "distribution-srpi-t_opo-a",
        "distribution-crpi-t_opo-a",
    ]
    assert exports[0][1] == exports[1][1]


def test_sample_size_exports_share_axes_and_reference_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from matplotlib.figure import Figure

    from scripts.build_defense_evidence import _generate_sample_size_figures

    source = DataFrame({
        "scenario": ["SRPI"] * 2 + ["CRPI"] * 2,
        "terminal": ["T_OPO"] * 4,
        "phase": ["A"] * 4,
        "sample_size": [50, 10_000] * 2,
        "mean": [1.1, 1.12, 1.2, 1.23],
        "percentile_95": [1.3, 1.32, 1.4, 1.43],
        "empirical_probability": [0.0] * 4,
        "candidate_rate": [0.1, 0.09, 0.16, 0.02],
        "confidence_interval_lower": [0.0] * 4,
        "confidence_interval_upper": [0.0713, 0.0004] * 2,
        "coverage_status": ["present"] * 4,
        "independence_limitation": ["not established"] * 4,
    })
    exports: list[tuple[str, list[tuple[float, float]], str]] = []

    def capture(figure: Figure, output: Path) -> None:
        exports.append((
            output.name,
            [axis.get_ylim() for axis in figure.axes],
            str(getattr(figure, "_suptitle").get_text()),
        ))

    monkeypatch.setattr(
        "scripts.build_defense_evidence.export_publication_figure", capture
    )
    _generate_sample_size_figures(source, tmp_path)
    assert len(exports) == 2
    assert exports[0][1] == exports[1][1]
    assert all("T_OPO, fase A" in title for _, _, title in exports)
    assert all("50–10.000" in title for _, _, title in exports)
