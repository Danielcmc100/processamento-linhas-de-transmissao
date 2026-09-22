"""Leakage-safe execution of the controlled anomaly benchmark."""

from dataclasses import dataclass
from math import floor

from numpy import asarray, percentile
from polars import (
    Boolean,
    DataFrame,
    Float64,
    Int64,
    Series,
    String,
    col,
    concat,
    lit,
)
from sklearn.neighbors import (  # type: ignore[reportMissingTypeStubs]
    NearestNeighbors,
)
from sklearn.preprocessing import (  # type: ignore[reportMissingTypeStubs]
    StandardScaler,
)

from src.services.benchmark import summarize_controlled_benchmark
from src.services.kmeans_evidence import evaluate_kmeans_evidence
from src.services.perturbations import (
    ControlledPerturbationResult,
    InterventionFamily,
    generate_controlled_perturbations,
)

BENCHMARK_SAMPLE_SIZE = 1_000
DEVELOPMENT_FRACTION = 0.70
SPLIT_SEED = 31
KMEANS_SEED = 42
DBSCAN_MIN_SAMPLES = 5
DBSCAN_PERCENTILE = 95.0
CONTAMINATION_RATES = (0.01, 0.05, 0.10)
INTERVENTION_INTENSITIES = {
    "point": 0.30,
    "contextual": 4.0,
    "collective": 0.20,
}
INTERVENTION_SEEDS = {
    "point": 101,
    "contextual": 211,
    "collective": 307,
}
_GROUP_COLUMNS = (
    "scenario",
    "source_lineage",
    "terminal",
    "phase",
)


@dataclass(frozen=True, slots=True)
class ControlledBenchmarkResult:
    """Benchmark metrics and row-level intervention provenance."""

    metrics: DataFrame
    intervention_manifest: DataFrame


def run_controlled_benchmark(
    observations: DataFrame,
) -> ControlledBenchmarkResult:
    """Execute frozen controlled conditions without source-run leakage.

    The 1,000-simulation canonical cases provide enough evaluation runs for
    every declared contamination rate. Complete source-run identities are
    assigned to development or evaluation before any copied-data injection.
    Development values stay clean and exclusively fit scalers, K-Means, and
    density-novelty thresholds. Metrics use evaluation rows only.

    DBSCAN has no out-of-sample prediction API. Its benchmark analogue is a
    declared k-nearest-neighbor novelty score: development-only standardized
    distances and their 95th percentile form a frozen density threshold.

    Returns:
        Condition metrics and injected-row manifest.

    Raises:
        ValueError: If canonical benchmark observations are unavailable.
    """
    benchmark_source = observations.filter(
        col("sample_size") == BENCHMARK_SAMPLE_SIZE
    )
    if benchmark_source.is_empty():
        message = (
            "Controlled benchmark requires canonical sample_size=1000 "
            "observations."
        )
        raise ValueError(message)

    split = _split_by_source_run_block(benchmark_source)
    development = split.filter(col("benchmark_split") == "development")
    evaluation = split.filter(col("benchmark_split") == "evaluation")
    conditions: list[tuple[InterventionFamily, float, float, int]] = [
        ("clean", 0.0, 0.0, SPLIT_SEED)
    ]
    for family in ("point", "contextual", "collective"):
        for rate in CONTAMINATION_RATES:
            conditions.append((
                family,
                rate,
                INTERVENTION_INTENSITIES[family],
                INTERVENTION_SEEDS[family] + round(rate * 100),
            ))

    metric_tables: list[DataFrame] = []
    manifests: list[DataFrame] = []
    for family, rate, intensity, seed in conditions:
        perturbation = generate_controlled_perturbations(
            evaluation.drop("benchmark_split"),
            family=family,
            contamination_rate=rate,
            intensity=intensity,
            seed=seed,
        )
        metric_tables.append(
            _evaluate_condition(
                development,
                perturbation,
                family=family,
                rate=rate,
                intensity=intensity,
                seed=seed,
            )
        )
        if not perturbation.manifest.is_empty():
            manifests.append(
                perturbation.manifest.with_columns(
                    lit("evaluation").alias("benchmark_split")
                )
            )

    manifest = concat(manifests, how="vertical_relaxed")
    return ControlledBenchmarkResult(
        metrics=concat(metric_tables, how="vertical_relaxed").sort(
            "intervention_family",
            "requested_contamination_rate",
            "method",
        ),
        intervention_manifest=manifest.sort(
            "intervention_family",
            "requested_contamination_rate",
            "source_lineage",
            "simulation",
            "terminal",
            "phase",
        ),
    )


def _split_by_source_run_block(observations: DataFrame) -> DataFrame:
    """Split contiguous run blocks by lineage while preserving all peers."""
    split_by_key: dict[tuple[str, int], str] = {}
    keys = sorted({
        (str(lineage), int(simulation))
        for lineage, simulation in observations.select(
            "source_lineage", "simulation"
        ).iter_rows()
    })
    lineages = sorted({lineage for lineage, _ in keys})
    for lineage in lineages:
        lineage_keys = [key for key in keys if key[0] == lineage]
        development_count = floor(len(lineage_keys) * DEVELOPMENT_FRACTION)
        development_count = min(
            max(development_count, 1), len(lineage_keys) - 1
        )
        for index, key in enumerate(lineage_keys):
            split_by_key[key] = (
                "development" if index < development_count else "evaluation"
            )
    labels = [
        split_by_key[(str(lineage), int(simulation))]
        for lineage, simulation in observations.select(
            "source_lineage", "simulation"
        ).iter_rows()
    ]
    return observations.clone().with_columns(
        Series("benchmark_split", labels, dtype=String)
    )


def _evaluate_condition(
    development: DataFrame,
    perturbation: ControlledPerturbationResult,
    *,
    family: InterventionFamily,
    rate: float,
    intensity: float,
    seed: int,
) -> DataFrame:
    """Evaluate both frozen methods for one intervention condition."""
    evaluation = perturbation.data.with_columns(
        lit("evaluation").alias("benchmark_split")
    )
    clean_development = development.with_columns(
        lit(False).alias("controlled_label"),
        lit(family).alias("intervention_family"),
        lit(intensity).alias("intervention_intensity"),
        lit(rate).alias("requested_contamination_rate"),
    )
    combined = concat(
        [clean_development, evaluation],
        how="diagonal_relaxed",
    ).with_columns(
        (col("benchmark_split") == "development").alias(
            "benchmark_calibration"
        )
    )
    if perturbation.status != "applicable":
        return _infeasible_condition(
            family=family,
            rate=rate,
            intensity=intensity,
            seed=seed,
            reason=perturbation.reason or "Intervention is infeasible.",
        )

    kmeans = evaluate_kmeans_evidence(
        combined,
        calibration_col="benchmark_calibration",
        n_clusters=2,
        random_state=KMEANS_SEED,
    ).filter(col("benchmark_split") == "evaluation")
    kmeans_evidence = kmeans.select(
        "intervention_family",
        "intervention_intensity",
        "method",
        "controlled_label",
        "flag",
        "applicability",
    )
    novelty_evidence = _density_novelty_evidence(combined)
    evidence = concat(
        [kmeans_evidence, novelty_evidence], how="vertical_relaxed"
    )
    summary = summarize_controlled_benchmark(evidence)
    return summary.with_columns(
        lit(rate, dtype=Float64).alias("requested_contamination_rate"),
        lit(
            perturbation.effective_contamination_rate,
            dtype=Float64,
        ).alias("effective_contamination_rate"),
        lit(seed, dtype=Int64).alias("intervention_seed"),
        lit(SPLIT_SEED, dtype=Int64).alias("split_seed"),
        lit(DEVELOPMENT_FRACTION, dtype=Float64).alias("development_fraction"),
        lit(perturbation.status).alias("condition_status"),
        lit(perturbation.reason, dtype=String).alias("condition_reason"),
        lit(
            "metrics quantify declared synthetic intervention detection; "
            "they do not estimate ATP numerical-error accuracy"
        ).alias("interpretation_scope"),
    )


def _density_novelty_evidence(observations: DataFrame) -> DataFrame:
    """Score evaluation rows against development-only local density."""
    evaluated: list[DataFrame] = []
    for group in observations.partition_by(
        list(_GROUP_COLUMNS), maintain_order=True
    ):
        development = group.filter(col("benchmark_split") == "development")
        evaluation = group.filter(col("benchmark_split") == "evaluation")
        if development.height < DBSCAN_MIN_SAMPLES:
            evaluated.append(
                _non_applicable_novelty(
                    evaluation,
                    "Too few development observations for density scoring.",
                )
            )
            continue
        if development["value_pu"].n_unique() == 1:
            evaluated.append(
                _non_applicable_novelty(
                    evaluation,
                    "Development values have zero variance.",
                )
            )
            continue

        scaler = StandardScaler()  # type: ignore[reportUnknownVariableType]
        development_values = development["value_pu"].to_numpy().reshape(-1, 1)
        scaled_development = asarray(
            scaler.fit_transform(  # type: ignore[reportUnknownMemberType]
                development_values
            )
        )
        neighbors = NearestNeighbors(n_neighbors=DBSCAN_MIN_SAMPLES)
        neighbors.fit(  # type: ignore[reportUnknownMemberType]
            scaled_development
        )
        development_distances, _ = neighbors.kneighbors(  # type: ignore[reportUnknownMemberType]
            scaled_development
        )
        threshold = float(
            percentile(
                development_distances[:, -1],
                DBSCAN_PERCENTILE,
                method="higher",
            )
        )
        scaled_evaluation = asarray(
            scaler.transform(  # type: ignore[reportUnknownMemberType]
                evaluation["value_pu"].to_numpy().reshape(-1, 1)
            )
        )
        evaluation_distances, _ = neighbors.kneighbors(  # type: ignore[reportUnknownMemberType]
            scaled_evaluation
        )
        scores = evaluation_distances[:, -1]
        flags = scores > threshold
        evaluated.append(
            evaluation.select(
                "intervention_family",
                "intervention_intensity",
                "controlled_label",
            ).with_columns(
                Series("flag", flags, dtype=Boolean),
                lit("applicable").alias("applicability"),
                lit("dbscan_density_novelty").alias("method"),
            )
        )
    return concat(evaluated, how="vertical_relaxed")


def _non_applicable_novelty(
    evaluation: DataFrame,
    reason: str,
) -> DataFrame:
    """Return explicit non-applicable density evidence."""
    return evaluation.select(
        "intervention_family",
        "intervention_intensity",
        "controlled_label",
    ).with_columns(
        lit(None, dtype=Boolean).alias("flag"),
        lit("non_applicable").alias("applicability"),
        lit("dbscan_density_novelty").alias("method"),
        lit(reason).alias("reason"),
    )


def _infeasible_condition(
    *,
    family: InterventionFamily,
    rate: float,
    intensity: float,
    seed: int,
    reason: str,
) -> DataFrame:
    """Serialize an infeasible condition for both methods."""
    evidence = DataFrame(
        {
            "intervention_family": [family, family],
            "intervention_intensity": [intensity, intensity],
            "method": ["kmeans", "dbscan_density_novelty"],
            "controlled_label": [False, False],
            "flag": [None, None],
            "applicability": ["non_applicable", "non_applicable"],
        },
        schema_overrides={"flag": Boolean},
    )
    return summarize_controlled_benchmark(evidence).with_columns(
        lit(rate, dtype=Float64).alias("requested_contamination_rate"),
        lit(0.0, dtype=Float64).alias("effective_contamination_rate"),
        lit(seed, dtype=Int64).alias("intervention_seed"),
        lit(SPLIT_SEED, dtype=Int64).alias("split_seed"),
        lit(DEVELOPMENT_FRACTION, dtype=Float64).alias("development_fraction"),
        lit("infeasible").alias("condition_status"),
        lit(reason).alias("condition_reason"),
        lit(
            "metrics quantify declared synthetic intervention detection; "
            "they do not estimate ATP numerical-error accuracy"
        ).alias("interpretation_scope"),
    )
