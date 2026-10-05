"""Write auditable artifacts for a completed ATP analysis run."""

import hashlib
import json
import platform
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from src.services.config import AnalysisConfig
from src.services.pipeline import PipelineResult

ARTIFACT_NAMES = (
    "raw_observations.csv",
    "validated_observations.csv",
    "statistical_evidence.csv",
    "distribution_adequacy.csv",
    "annotated_observations.csv",
    "summary.csv",
    "configuration.json",
    "metadata.json",
    "combined.png",
    "exceedance.png",
    "overvoltage_histogram.png",
    "switching_time.png",
    "kmeans_clusters.png",
    "dbscan_clusters.png",
    "hierarchical_clusters.png",
    "hierarchical_tree.png",
)


def write_result_artifacts(
    config: AnalysisConfig,
    result: PipelineResult,
) -> tuple[Path, ...]:
    """Write one complete, reproducible analysis result package.

    Existing known artifacts are rejected before any file is written unless
    overwrite is enabled. Unrelated files in the output directory are never
    removed or replaced.

    Returns:
        Paths to all written artifacts in stable name order.

    Raises:
        FileExistsError: If a known artifact exists and overwrite is false.
        ValueError: If result evidence uses an incomplete or stale schema.
    """
    _validate_result_schema(config, result)
    targets = tuple(config.output_dir / name for name in ARTIFACT_NAMES)
    conflicts = [path for path in targets if path.exists()]
    if conflicts and not config.overwrite:
        names = ", ".join(path.name for path in conflicts)
        message = f"Result artifacts already exist: {names}."
        raise FileExistsError(message)

    config.output_dir.mkdir(parents=True, exist_ok=True)
    result.raw_observations.write_csv(
        config.output_dir / "raw_observations.csv"
    )
    result.validated_observations.write_csv(
        config.output_dir / "validated_observations.csv"
    )
    result.statistical_evidence.write_csv(
        config.output_dir / "statistical_evidence.csv"
    )
    result.distribution_adequacy.write_csv(
        config.output_dir / "distribution_adequacy.csv"
    )
    result.annotated_observations.write_csv(
        config.output_dir / "annotated_observations.csv"
    )
    result.summary.write_csv(config.output_dir / "summary.csv")
    _write_json(
        config.output_dir / "configuration.json",
        config.model_dump(mode="json"),
    )
    result.figures.combined.savefig(config.output_dir / "combined.png")
    result.figures.exceedance.savefig(config.output_dir / "exceedance.png")
    result.figures.overvoltage_histogram.savefig(
        config.output_dir / "overvoltage_histogram.png"
    )
    result.figures.switching_time.savefig(
        config.output_dir / "switching_time.png"
    )
    result.figures.kmeans_clusters.savefig(
        config.output_dir / "kmeans_clusters.png"
    )
    result.figures.dbscan_clusters.savefig(
        config.output_dir / "dbscan_clusters.png"
    )
    result.figures.hierarchical_clusters.savefig(
        config.output_dir / "hierarchical_clusters.png"
    )
    result.figures.hierarchical_tree.savefig(
        config.output_dir / "hierarchical_tree.png"
    )
    _write_json(
        config.output_dir / "metadata.json",
        _build_metadata(config, result),
    )
    return targets


def _build_metadata(
    config: AnalysisConfig,
    result: PipelineResult,
) -> dict[str, Any]:
    input_files = sorted(config.input_path.rglob("*.lis"))
    return {
        "schema_version": config.schema_version,
        "generator_version": config.generator_version,
        "artifacts": list(ARTIFACT_NAMES),
        "counts": {
            "annotated_observations": (result.annotated_observations.height),
            "distribution_adequacy_rows": (
                result.distribution_adequacy.height
            ),
            "input_files": len(input_files),
            "raw_observations": result.raw_observations.height,
            "statistical_evidence_rows": result.statistical_evidence.height,
            "summary_rows": result.summary.height,
            "validated_observations": result.validated_observations.height,
            "validation_issues": len(result.validation.issues),
        },
        "inputs": [
            {
                "path": path.relative_to(config.input_path).as_posix(),
                "sha256": _sha256(path),
            }
            for path in input_files
        ],
        "validation": {
            "status": result.validation.status.value,
            "issues": [
                {
                    **asdict(issue),
                    "observation": (
                        result.raw_observations.row(
                            issue.row_index, named=True
                        )
                        if issue.row_index is not None
                        else None
                    ),
                }
                for issue in result.validation.issues
            ],
        },
        "runtime": {
            "generated_at_utc": datetime.now(UTC).isoformat(),
        },
        "software": {
            "matplotlib": version("matplotlib"),
            "numpy": version("numpy"),
            "polars": version("polars"),
            "pydantic": version("pydantic"),
            "python": platform.python_version(),
            "scikit-learn": version("scikit-learn"),
            "scipy": version("scipy"),
        },
    }


def _validate_result_schema(
    config: AnalysisConfig,
    result: PipelineResult,
) -> None:
    """Fail closed before writing stale or internally inconsistent evidence."""
    identity_columns = (
        "source_file",
        "simulation",
        "terminal",
        "phase",
        "source_value",
        "value_pu",
        "time",
        "scenario",
        "sample_size",
        "source_lineage",
        "base_voltage",
        "event_definition",
    )
    for label, table in (
        ("raw_observations", result.raw_observations),
        ("validated_observations", result.validated_observations),
        ("annotated_observations", result.annotated_observations),
    ):
        missing = [
            column for column in identity_columns if column not in table
        ]
        if missing:
            fields = ", ".join(missing)
            raise ValueError(f"{label} uses stale schema; missing: {fields}.")

    statistical_columns = (
        "scenario",
        "sample_size",
        "terminal",
        "phase",
        "occurrence_count",
        "denominator",
        "empirical_probability",
        "confidence_interval_lower",
        "confidence_interval_upper",
        "validation_status",
    )
    adequacy_columns = (
        "scenario",
        "sample_size",
        "terminal",
        "phase",
        "decision",
        "applicability",
        "gaussian_inference_status",
    )
    for label, table, required in (
        (
            "statistical_evidence",
            result.statistical_evidence,
            statistical_columns,
        ),
        (
            "distribution_adequacy",
            result.distribution_adequacy,
            adequacy_columns,
        ),
    ):
        missing = [column for column in required if column not in table]
        if missing:
            fields = ", ".join(missing)
            raise ValueError(f"{label} uses stale schema; missing: {fields}.")

    denominator = sum(result.statistical_evidence["denominator"].to_list())
    if denominator != result.validated_observations.height:
        raise ValueError(
            "Primary statistics denominator must equal validated row count."
        )
    if config.schema_version != "1.0.0":
        raise ValueError("Unsupported result schema version.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
