"""Write auditable artifacts for a completed ATP analysis run."""

import hashlib
import json
import platform
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from src.services.config import AnalysisConfig
from src.services.pipeline import PipelineResult

ARTIFACT_NAMES = (
    "raw_observations.csv",
    "annotated_observations.csv",
    "summary.csv",
    "configuration.json",
    "metadata.json",
    "combined.png",
    "exceedance.png",
    "overvoltage_histogram.png",
    "switching_time.png",
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
    """
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
        "artifacts": list(ARTIFACT_NAMES),
        "counts": {
            "annotated_observations": (result.annotated_observations.height),
            "input_files": len(input_files),
            "raw_observations": result.raw_observations.height,
            "summary_rows": result.summary.height,
            "validation_issues": len(result.validation.issues),
        },
        "inputs": [
            {
                "path": path.relative_to(config.input_path).as_posix(),
                "sha256": _sha256(path),
            }
            for path in input_files
        ],
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
