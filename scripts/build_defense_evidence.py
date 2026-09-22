"""Build versioned thesis-defense evidence from canonical ATP sources."""

from argparse import ArgumentParser
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from json import dumps
from pathlib import Path
from typing import Literal, cast

from matplotlib import pyplot
from polars import (
    DataFrame,
    Int64,
    String,
    col,
    concat,
    lit,
)
from polars import (
    len as row_count,
)

from src.parser.statistical_distribution import (
    parse_statistical_distributions,
)
from src.services.config import (
    AnalysisConfig,
    DbscanConfig,
    KMeansConfig,
)
from src.services.controlled_benchmark_runner import (
    run_controlled_benchmark,
)
from src.services.convergence import (
    build_convergence_table,
    build_method_comparison_matrix,
)
from src.services.dataset_manifest import (
    ACCEPTED_BASE_VOLTAGE,
    DatasetManifestEntry,
    build_dataset_manifest,
    validate_dataset_manifest,
)
from src.services.dbscan_evidence import evaluate_dbscan_evidence
from src.services.defense_reporting import (
    RoundingPolicy,
    generate_defense_tables,
)
from src.services.defense_visualization import (
    FigureContext,
    export_publication_figure,
    plot_convergence,
    plot_distribution_qq,
)
from src.services.kmeans_evidence import evaluate_kmeans_evidence
from src.services.pipeline import run_pipeline
from src.services.probability_reconciliation import (
    reconcile_probability_bin,
)
from src.services.reporting import write_result_artifacts
from src.services.reproducibility import (
    build_claim_evidence_row,
    build_reproducibility_manifest,
)
from src.services.sensitivity import (
    ParameterGrid,
    SensitivityReplayInput,
    SensitivityReplayResult,
    SensitivitySummary,
    replay_sensitivity,
)
from src.services.technical_review import select_review_cases

SCHEMA_VERSION = "1.0.0"
GENERATOR_VERSION = "1.0.0"
THRESHOLD_PU = 2.3
TERMINALS = ("T_MAN", "1_2LT", "T_OPO")
PHASES = ("A", "B", "C")
TERMINAL_POSITIONS = {"T_MAN": 0.0, "1_2LT": 0.5, "T_OPO": 1.0}


def main(arguments: list[str] | None = None) -> int:
    """Build canonical evidence package and return process status."""
    parser = _argument_parser()
    options = parser.parse_args(arguments)
    build_defense_evidence(
        root=options.root,
        output=options.output,
        overwrite=options.overwrite,
    )
    return 0


def build_defense_evidence(
    *,
    root: Path,
    output: Path,
    overwrite: bool = False,
) -> Path:
    """Run canonical sources and write one traceable evidence package.

    Returns:
        Path to final reproducibility manifest.

    Raises:
        FileExistsError: If output is non-empty without overwrite.
        ValueError: If canonical source coverage or provenance is invalid.
    """
    if output.exists() and any(output.iterdir()) and not overwrite:
        raise FileExistsError(
            f"Evidence output already contains artifacts: {output}."
        )
    entries = build_dataset_manifest(root)
    validation = validate_dataset_manifest(entries)
    if not validation.is_valid:
        raise ValueError(
            "Canonical dataset manifest is invalid: "
            f"missing={validation.missing_coverage}, "
            f"exclusions={validation.exclusions}."
        )
    output.mkdir(parents=True, exist_ok=True)

    statistical_tables: list[DataFrame] = []
    adequacy_tables: list[DataFrame] = []
    annotated_tables: list[DataFrame] = []
    reconciliation_rows: list[dict[str, object]] = []
    for entry in entries:
        _run_source_phases(
            root=root,
            output=output,
            entry=entry,
            overwrite=overwrite,
            statistical_tables=statistical_tables,
            adequacy_tables=adequacy_tables,
            annotated_tables=annotated_tables,
            reconciliation_rows=reconciliation_rows,
        )

    statistical = concat(statistical_tables, how="vertical_relaxed").sort(
        "scenario", "sample_size", "terminal", "phase"
    )
    adequacy = concat(adequacy_tables, how="vertical_relaxed").sort(
        "scenario", "sample_size", "terminal", "phase"
    )
    annotated = concat(annotated_tables, how="vertical_relaxed").sort(
        "scenario", "sample_size", "terminal", "phase", "simulation"
    )
    sources_dir = output / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    _dataset_manifest_frame(entries).write_csv(
        sources_dir / "dataset_manifest.csv"
    )
    statistical.write_csv(sources_dir / "statistical_evidence.csv")
    adequacy.write_csv(sources_dir / "distribution_adequacy.csv")
    annotated.write_csv(sources_dir / "annotated_observations.csv")
    DataFrame(reconciliation_rows).sort(
        "scenario", "sample_size", "terminal", "phase", "interval_number"
    ).write_csv(sources_dir / "probability_reconciliation.csv")

    candidates = _candidate_summary(annotated)
    convergence_input = _convergence_input(
        statistical,
        adequacy,
        candidates,
    )
    convergence = build_convergence_table(convergence_input)
    convergence.write_csv(sources_dir / "convergence.csv")

    method_matrix = build_method_comparison_matrix(
        annotated.with_columns(
            col("terminal")
            .replace_strict(TERMINAL_POSITIONS)
            .alias("terminal_position_km")
        ),
        analysis_mode="exploratory",
        multiplicity_qualification=(
            "Não são realizadas afirmações inferenciais múltiplas."
        ),
    )
    method_matrix.write_csv(sources_dir / "method_comparison.csv")
    sensitivity = _sensitivity_evidence(annotated)
    sensitivity.write_csv(sources_dir / "sensitivity.csv")

    review = _unresolved_review_table(annotated)
    benchmark_result = run_controlled_benchmark(annotated)
    benchmark = benchmark_result.metrics
    review.write_csv(sources_dir / "technical_review.csv")
    benchmark.write_csv(sources_dir / "controlled_benchmark.csv")
    benchmark_result.intervention_manifest.write_csv(
        sources_dir / "controlled_interventions.csv"
    )

    tables = generate_defense_tables(
        output / "tables",
        probability=statistical,
        benchmark=benchmark,
        convergence=convergence,
        review=review,
        rounding=RoundingPolicy(decimal_places=4),
        generator_version=GENERATOR_VERSION,
        overwrite=overwrite,
    )
    _generate_figures(annotated, adequacy, convergence, output / "figures")

    status = {
        "schema_version": SCHEMA_VERSION,
        "package_status": "incomplete",
        "accepted_layers": [
            "data_validity",
            "statistical_calculation",
            "analytical_candidate_generation",
        ],
        "incomplete_evidence": {
            "technical_review": (
                "Waveforms, repeat simulations, and a qualified independent "
                "electrical reviewer were unavailable."
            ),
        },
        "causal_conclusion": "unresolved",
    }
    status_path = output / "package_status.json"
    status_path.write_text(
        dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest_path = _write_manifest(
        root=root,
        output=output,
        entries=entries,
        status_path=status_path,
        table_paths=(
            *tables.source_paths.values(),
            *tables.latex_paths.values(),
            tables.traceability_path,
            tables.rounding_policy_path,
        ),
    )
    return manifest_path


def _run_source_phases(
    *,
    root: Path,
    output: Path,
    entry: DatasetManifestEntry,
    overwrite: bool,
    statistical_tables: list[DataFrame],
    adequacy_tables: list[DataFrame],
    annotated_tables: list[DataFrame],
    reconciliation_rows: list[dict[str, object]],
) -> None:
    """Run all configured phases for one canonical source."""
    source = root / entry.source_path
    source_dir = source.parent
    for phase in PHASES:
        run_dir = (
            output
            / "runs"
            / entry.scenario.lower()
            / str(entry.sample_size)
            / phase.lower()
        )
        config = AnalysisConfig(
            input_path=source_dir,
            schema_version=SCHEMA_VERSION,
            generator_version=GENERATOR_VERSION,
            encoding="iso-8859-1",
            base_voltage=ACCEPTED_BASE_VOLTAGE,
            scenario=cast(Literal["SRPI", "CRPI"], entry.scenario),
            sample_size=entry.sample_size,
            source_lineage=(f"{entry.scenario.lower()}-{entry.sample_size}"),
            event_definition="absolute_phase_to_ground_maximum",
            terminals=TERMINALS,
            phase_policy=phase,
            dbscan=DbscanConfig(eps=0.5, min_samples=5),
            kmeans=KMeansConfig(n_clusters=2, random_state=42),
            threshold=THRESHOLD_PU,
            output_dir=run_dir,
            overwrite=overwrite,
        )
        result = run_pipeline(config)
        write_result_artifacts(config, result)
        statistical_tables.append(result.statistical_evidence)
        adequacy_tables.append(result.distribution_adequacy)
        annotated_tables.append(
            result.annotated_observations.with_columns(
                lit(entry.source_sha256).alias("source_sha256")
            )
        )
        for source_bin in parse_statistical_distributions(source):
            if source_bin.phase != phase:
                continue
            direct_values = result.validated_observations.filter(
                col("terminal") == source_bin.terminal
            )["value_pu"].to_list()
            reconciliation = reconcile_probability_bin(
                source_bin,
                direct_values,
            )
            reconciliation_rows.append({
                "scenario": entry.scenario,
                "sample_size": entry.sample_size,
                "source_path": entry.source_path,
                "source_sha256": entry.source_sha256,
                **asdict(reconciliation),
            })
        pyplot.close("all")


def _dataset_manifest_frame(
    entries: tuple[DatasetManifestEntry, ...],
) -> DataFrame:
    """Serialize canonical dataset provenance as machine-readable rows."""
    rows: list[dict[str, object]] = []
    for entry in entries:
        row = asdict(entry)
        row["terminals"] = "|".join(entry.terminals)
        row["phases"] = "|".join(entry.phases)
        row["time_window"] = "|".join(
            str(value) for value in entry.time_window
        )
        row["experiment_assumptions"] = "|".join(entry.experiment_assumptions)
        row["exclusion_reasons"] = "|".join(entry.exclusion_reasons)
        rows.append(row)
    return DataFrame(rows)


def _candidate_summary(annotated: DataFrame) -> DataFrame:
    """Aggregate candidate counts without removing candidate observations."""
    scope = ["scenario", "sample_size", "terminal", "phase"]
    return (
        annotated
        .group_by(scope)
        .agg(
            row_count().alias("evaluated_count"),
            col("anomaly_candidate")
            .cast(Int64)
            .sum()
            .alias("candidate_count"),
        )
        .with_columns(
            (col("candidate_count") / col("evaluated_count")).alias(
                "candidate_rate"
            )
        )
    )


def _sensitivity_evidence(annotated: DataFrame) -> DataFrame:
    """Replay frozen detector grids on representative target-data scopes."""
    rows: list[dict[str, object]] = []
    for scenario in ("CRPI", "SRPI"):
        observations = annotated.filter(
            (col("scenario") == scenario)
            & (col("sample_size") == 10_000)
            & (col("terminal") == "T_OPO")
            & (col("phase") == "A")
        )
        if observations.is_empty():
            raise ValueError(
                f"Sensitivity scope is missing: {scenario}|10000|T_OPO|A."
            )
        kmeans_grid = ParameterGrid(
            configuration_id=(
                f"{scenario.lower()}-t_opo-a-kmeans-sensitivity-v1"
            ),
            method="kmeans_distance",
            varied_parameters=(("n_clusters", (2, 3)),),
            fixed_controls=(
                ("feature", "value_pu"),
                ("threshold_policy", "calibration_distance_percentile_99"),
                ("sample_size", 10_000),
            ),
            seeds=(17, 42),
        )
        kmeans_summary = replay_sensitivity(
            kmeans_grid,
            lambda replay, source=observations: _evaluate_sensitivity_replay(
                source,
                replay,
            ),
        )
        rows.extend(_sensitivity_rows(scenario, kmeans_summary))

        dbscan_grid = ParameterGrid(
            configuration_id=(
                f"{scenario.lower()}-t_opo-a-dbscan-sensitivity-v1"
            ),
            method="dbscan_noise",
            varied_parameters=(
                ("min_samples", (5, 10)),
                ("effective_eps", (0.4, 0.5, 0.6)),
            ),
            fixed_controls=(
                ("feature", "value_pu"),
                ("scaling_policy", "standard"),
                ("sample_size", 10_000),
            ),
            seeds=(0,),
        )
        dbscan_summary = replay_sensitivity(
            dbscan_grid,
            lambda replay, source=observations: _evaluate_sensitivity_replay(
                source,
                replay,
            ),
        )
        rows.extend(_sensitivity_rows(scenario, dbscan_summary))
    return DataFrame(rows).sort("scenario", "method", "run_id")


def _evaluate_sensitivity_replay(
    observations: DataFrame,
    replay: SensitivityReplayInput,
) -> SensitivityReplayResult:
    """Evaluate one detector configuration and retain candidate identities."""
    if replay.method == "kmeans_distance":
        n_clusters = replay.parameter("n_clusters")
        if type(n_clusters) is not int:
            raise TypeError("n_clusters must be an integer.")
        evaluated = evaluate_kmeans_evidence(
            observations,
            n_clusters=n_clusters,
            random_state=replay.seed,
        )
        flag_column = "flag"
        applicability_column = "applicability"
        reason_column = "reason"
    elif replay.method == "dbscan_noise":
        min_samples = replay.parameter("min_samples")
        effective_eps = replay.parameter("effective_eps")
        if type(min_samples) is not int:
            raise TypeError("min_samples must be an integer.")
        if not isinstance(effective_eps, (int, float)):
            raise TypeError("effective_eps must be numeric.")
        evaluated = evaluate_dbscan_evidence(
            observations,
            min_samples=min_samples,
            effective_eps=float(effective_eps),
        )
        flag_column = "dbscan_flag"
        applicability_column = "dbscan_applicability"
        reason_column = "dbscan_reason"
    else:
        raise ValueError(f"Unsupported sensitivity method: {replay.method}.")

    statuses = set(evaluated[applicability_column].to_list())
    if statuses != {"applicable"}:
        reasons = sorted(
            str(reason)
            for reason in evaluated[reason_column].drop_nulls().unique()
        )
        return SensitivityReplayResult(
            replay_input=replay,
            candidate_ids=frozenset(),
            evaluated_count=evaluated.height,
            applicability="non_applicable",
            reason="; ".join(reasons) or "Detector is non-applicable.",
        )

    identities = frozenset(
        tuple(identity)
        for identity in evaluated
        .filter(col(flag_column).fill_null(False))
        .select(
            "source_lineage",
            "simulation",
            "terminal",
            "phase",
        )
        .iter_rows()
    )
    return SensitivityReplayResult(
        replay_input=replay,
        candidate_ids=identities,
        evaluated_count=evaluated.height,
        applicability="applicable",
    )


def _sensitivity_rows(
    scenario: str,
    summary: SensitivitySummary,
) -> list[dict[str, object]]:
    """Serialize sensitivity results without discarding candidate identity."""
    rows: list[dict[str, object]] = []
    for run, result in zip(summary.runs, summary.results, strict=True):
        rows.append({
            "scenario": scenario,
            "sample_size": 10_000,
            "terminal": "T_OPO",
            "phase": "A",
            "configuration_id": summary.configuration.configuration_id,
            "method": run.replay_input.method,
            "run_id": run.replay_input.run_id,
            "parameters_json": dumps(dict(run.replay_input.parameters)),
            "seed": run.replay_input.seed,
            "evaluated_count": result.evaluated_count,
            "candidate_count": run.candidate_count,
            "candidate_rate": run.candidate_rate,
            "candidate_ids_json": dumps(
                sorted(repr(identity) for identity in result.candidate_ids),
                separators=(",", ":"),
            ),
            "applicability": run.applicability,
            "reason": run.reason,
            "identity_jaccard": run.identity_jaccard,
            "reference_run_id": summary.reference_run_id,
            "minimum_identity_jaccard": summary.minimum_identity_jaccard,
            "stability_threshold": (summary.configuration.stability_threshold),
            "stability_rationale": (summary.configuration.stability_rationale),
            "qualification": summary.qualification,
        })
    return rows


def _convergence_input(
    statistical: DataFrame,
    adequacy: DataFrame,
    candidates: DataFrame,
) -> DataFrame:
    """Assemble compatible convergence inputs from saved evidence tables."""
    scope = ["scenario", "sample_size", "terminal", "phase"]
    adequacy_status = adequacy.select(
        *scope,
        col("decision").alias("fitted_model_status"),
    )
    return (
        statistical
        .join(adequacy_status, on=scope, how="left")
        .join(candidates, on=scope, how="left")
        .with_columns(
            lit(ACCEPTED_BASE_VOLTAGE).alias("base_voltage"),
            lit("scenario|source_lineage|terminal|phase").alias(
                "grouping_policy"
            ),
            lit("defense-v1-frozen").alias("method_policy"),
            lit("independence_not_established").alias("relationship_status"),
        )
        .select(
            *scope,
            "base_voltage",
            "event_definition",
            "comparison_operator",
            "threshold",
            "grouping_policy",
            "method_policy",
            "relationship_status",
            "mean",
            "sample_standard_deviation",
            "median",
            "percentile_90",
            "percentile_95",
            "percentile_99",
            "empirical_probability",
            "confidence_interval_lower",
            "confidence_interval_upper",
            "fitted_model_status",
            "candidate_count",
            "candidate_rate",
        )
    )


def _unresolved_review_table(annotated: DataFrame) -> DataFrame:
    """Select representative cases and preserve unresolved review status."""
    selected = select_review_cases(annotated)
    return selected.select(
        "source_file",
        "source_sha256",
        "simulation",
        "terminal",
        "phase",
        "source_value",
        "value_pu",
        col("anomaly_reasons").alias("method_evidence"),
    ).with_columns(
        lit("unresolved").alias("conclusion"),
        lit("não disponível").alias("reviewer"),
        lit("não realizada").alias("review_date"),
        lit(
            "Ausência de forma de onda, repetição comparável e revisão "
            "elétrica independente qualificada."
        ).alias("rationale"),
    )


def _generate_figures(
    annotated: DataFrame,
    adequacy: DataFrame,
    convergence: DataFrame,
    output: Path,
) -> None:
    """Generate source-backed representative publication figures."""
    for scenario in ("SRPI", "CRPI"):
        context = FigureContext(
            scenario=scenario,
            sample_size=10_000,
            terminal="T_OPO",
            phase="A",
            method="comparação de métodos",
            unit="p.u.",
            threshold=THRESHOLD_PU,
            status="evidência analítica",
        )
        convergence_source = convergence.filter(
            (col("scenario") == scenario)
            & (col("terminal") == "T_OPO")
            & (col("phase") == "A")
        )
        figure, _ = plot_convergence(convergence_source, context)
        export_publication_figure(
            figure,
            output / f"convergence-{scenario.lower()}-t_opo-a",
        )
        pyplot.close(figure)

        observations = annotated.filter(
            (col("scenario") == scenario)
            & (col("sample_size") == 10_000)
            & (col("terminal") == "T_OPO")
            & (col("phase") == "A")
        )
        fit = adequacy.filter(
            (col("scenario") == scenario)
            & (col("sample_size") == 10_000)
            & (col("terminal") == "T_OPO")
            & (col("phase") == "A")
        ).row(0, named=True)
        distribution_source = observations.select("value_pu").with_columns(
            lit(fit["fitted_mean"]).alias("fitted_mean"),
            lit(fit["fitted_standard_deviation"]).alias(
                "fitted_standard_deviation"
            ),
            lit(str(fit["decision"]), dtype=String).alias("adequacy_status"),
        )
        figure, _ = plot_distribution_qq(distribution_source, context)
        export_publication_figure(
            figure,
            output / f"distribution-{scenario.lower()}-t_opo-a",
        )
        pyplot.close(figure)


def _write_manifest(
    *,
    root: Path,
    output: Path,
    entries: tuple[DatasetManifestEntry, ...],
    status_path: Path,
    table_paths: tuple[Path, ...],
) -> Path:
    """Write manifest with incomplete evidence made explicit."""
    source_files = {
        f"{entry.scenario}-{entry.sample_size}": root / entry.source_path
        for entry in entries
    }
    declared_paths = {
        status_path,
        *table_paths,
        *output.rglob("*"),
    }
    output_paths = {
        path.relative_to(output).as_posix(): path
        for path in sorted(declared_paths)
        if path.is_file() and path.name != "reproducibility_manifest.json"
    }
    claims = _claim_evidence(source_files)
    revision = _git_revision(Path.cwd())
    manifest = build_reproducibility_manifest(
        source_files=source_files,
        configuration={
            "schema_version": SCHEMA_VERSION,
            "base_voltage": ACCEPTED_BASE_VOLTAGE,
            "threshold_pu": THRESHOLD_PU,
            "scenarios": ["SRPI", "CRPI"],
            "sample_sizes": [50, 100, 200, 1_000, 10_000],
            "terminals": list(TERMINALS),
            "phases": list(PHASES),
        },
        code_revision=revision,
        dependencies={
            package: version(package)
            for package in (
                "matplotlib",
                "numpy",
                "polars",
                "scikit-learn",
                "scipy",
            )
        },
        commands=[
            "uv run python -m scripts.build_defense_evidence --overwrite"
        ],
        output_files=output_paths,
        generated_at_utc=datetime.now(UTC).isoformat(),
        validation_statuses={
            "dataset_manifest": "valid",
            "statistical_evidence": "valid",
            "detector_execution": "passed",
            "controlled_benchmark": "valid",
            "parameter_sensitivity": "valid",
            "technical_review": "incomplete",
        },
        claim_evidence=claims,
    )
    manifest_path = output / "reproducibility_manifest.json"
    manifest_path.write_text(
        dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _claim_evidence(source_files: dict[str, Path]) -> list[dict[str, object]]:
    """Map every specification requirement to concrete evidence layers."""
    definitions = (
        ("01", "canonical-matrix", "dataset_manifest", "dataset_manifest"),
        ("02", "accepted-base", "dataset_manifest", "dataset_manifest"),
        (
            "03",
            "observation-identity",
            "preprocessing",
            "annotated_observations",
        ),
        (
            "04",
            "descriptive-statistics",
            "statistical_evidence",
            "statistical_evidence",
        ),
        (
            "05",
            "empirical-probability",
            "statistical_evidence",
            "statistical_evidence",
        ),
        (
            "06",
            "atp-reconciliation",
            "probability_reconciliation",
            "probability_reconciliation",
        ),
        (
            "07",
            "gaussian-adequacy",
            "distribution_adequacy",
            "distribution_adequacy",
        ),
        ("08", "cluster-separation", "comparison", "method_comparison"),
        ("09", "kmeans-evidence", "kmeans_evidence", "annotated_observations"),
        ("10", "dbscan-evidence", "dbscan_evidence", "annotated_observations"),
        ("11", "method-comparison", "comparison", "method_comparison"),
        (
            "12",
            "controlled-perturbations",
            "perturbations",
            "controlled_benchmark",
        ),
        ("13", "controlled-performance", "benchmark", "controlled_benchmark"),
        ("14", "sample-convergence", "convergence", "convergence"),
        ("15", "structured-comparison", "convergence", "method_comparison"),
        ("16", "parameter-sensitivity", "sensitivity", "sensitivity"),
        ("17", "technical-review", "technical_review", "technical_review"),
        ("18", "publication-figures", "defense_visualization", "convergence"),
        ("19", "defense-tables", "defense_reporting", "statistical_evidence"),
        ("20", "methodology", "pipeline", "statistical_evidence"),
        ("21", "results", "pipeline", "statistical_evidence"),
        ("22", "claim-matrix", "reproducibility", "statistical_evidence"),
        ("23", "reproducibility", "reproducibility", "dataset_manifest"),
        ("24", "quality-gates", "pipeline", "statistical_evidence"),
        (
            "25",
            "robust-baseline",
            "distribution_adequacy",
            "method_comparison",
        ),
        ("26", "repeat-simulation", "technical_review", "technical_review"),
        (
            "27",
            "portuguese-manuscript",
            "defense_reporting",
            "statistical_evidence",
        ),
    )
    incomplete = {"17", "26"}
    rows: list[dict[str, object]] = []
    for number, claim_id, module, artifact in definitions:
        rows.append(
            build_claim_evidence_row(
                requirement_id=f"DEF-{number}",
                claim_id=claim_id,
                claim=f"Evidência rastreável para o requisito DEF-{number}.",
                code_paths=[f"src/services/{module}.py"],
                test_paths=[f"tests/test_{module}.py"],
                data_paths=list(source_files),
                output_artifacts=[f"sources/{artifact}.csv"],
                figure_table_labels=["chap:results"],
                manuscript_sections=["chap:results"],
                status=("incomplete" if number in incomplete else "accepted"),
            )
        )
    return rows


def _git_revision(repository: Path) -> str:
    """Read current revision without starting an external process."""
    head = (repository / ".git" / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head
    reference = repository / ".git" / head.removeprefix("ref: ")
    return reference.read_text(encoding="utf-8").strip()


def _argument_parser() -> ArgumentParser:
    """Create command-line interface for deterministic package generation."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("input_files/casos"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/defense-evidence/v1"),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
