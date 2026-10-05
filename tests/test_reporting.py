"""Integration tests for auditable ATP analysis artifacts."""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import polars as pl
import pytest
from polars import Series

matplotlib.use("Agg")

from src.services.config import AnalysisConfig  # noqa: E402
from src.services.pipeline import run_pipeline  # noqa: E402
from src.services.reporting import (  # noqa: E402
    ARTIFACT_NAMES,
    write_result_artifacts,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _config(
    tmp_path: Path,
    *,
    output_name: str = "output",
    overwrite: bool = False,
) -> AnalysisConfig:
    input_path = tmp_path / "input"
    output_dir = tmp_path / output_name
    input_path.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    shutil.copy2(FIXTURES / "representative.lis", input_path)
    return AnalysisConfig.model_validate({
        "input_path": input_path,
        "schema_version": "1.0.0",
        "generator_version": "1.0.0",
        "encoding": "iso-8859-1",
        "base_voltage": 112_677.0,
        "scenario": "SRPI",
        "sample_size": 2,
        "source_lineage": "representative-srpi-2",
        "event_definition": "absolute_phase_to_ground_maximum",
        "terminals": ["T_MAN", "T_OPO"],
        "phase_policy": "A",
        "dbscan": {"eps": 3.0, "min_samples": 2},
        "kmeans": {"n_clusters": 2, "random_state": 42},
        "threshold": 3.0,
        "output_dir": output_dir,
        "overwrite": overwrite,
    })


def test_writer_saves_complete_rerunnable_artifact_package(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    result = run_pipeline(config)

    written = write_result_artifacts(config, result)

    assert tuple(path.name for path in written) == ARTIFACT_NAMES
    assert {path.name for path in config.output_dir.iterdir()} == set(
        ARTIFACT_NAMES
    )
    assert (
        pl.read_csv(config.output_dir / "raw_observations.csv").columns
        == result.raw_observations.columns
    )
    assert (
        pl.read_csv(config.output_dir / "validated_observations.csv").columns
        == result.validated_observations.columns
    )
    assert (
        pl.read_csv(config.output_dir / "annotated_observations.csv").columns
        == result.annotated_observations.columns
    )
    assert pl.read_csv(config.output_dir / "summary.csv").columns == (
        result.summary.columns
    )
    assert (
        pl.read_csv(config.output_dir / "statistical_evidence.csv").columns
        == result.statistical_evidence.columns
    )
    assert (
        pl.read_csv(config.output_dir / "distribution_adequacy.csv").columns
        == result.distribution_adequacy.columns
    )

    saved_config_text = (config.output_dir / "configuration.json").read_text(
        encoding="utf-8"
    )
    assert saved_config_text.endswith("\n")
    assert AnalysisConfig.model_validate_json(saved_config_text) == config

    metadata_text = (config.output_dir / "metadata.json").read_text(
        encoding="utf-8"
    )
    assert metadata_text.endswith("\n")
    metadata = json.loads(metadata_text)
    assert metadata["artifacts"] == list(ARTIFACT_NAMES)
    assert metadata["counts"] == {
        "annotated_observations": 4,
        "validated_observations": 4,
        "statistical_evidence_rows": 2,
        "distribution_adequacy_rows": 2,
        "input_files": 1,
        "raw_observations": 12,
        "summary_rows": 2,
        "validation_issues": 0,
    }
    expected_hash = hashlib.sha256(
        (config.input_path / "representative.lis").read_bytes()
    ).hexdigest()
    assert metadata["inputs"] == [
        {
            "path": "representative.lis",
            "sha256": expected_hash,
        }
    ]
    generated_at = datetime.fromisoformat(
        metadata["runtime"]["generated_at_utc"]
    )
    utc_offset = generated_at.utcoffset()
    assert utc_offset is not None
    assert utc_offset.total_seconds() == 0
    assert set(metadata["software"]) == {
        "matplotlib",
        "numpy",
        "polars",
        "pydantic",
        "python",
        "scikit-learn",
        "scipy",
    }
    assert "physical_cause" not in metadata
    assert metadata["schema_version"] == "1.0.0"
    assert metadata["generator_version"] == "1.0.0"
    assert (config.output_dir / "combined.png").stat().st_size > 0
    assert (config.output_dir / "exceedance.png").stat().st_size > 0
    assert (config.output_dir / "overvoltage_histogram.png").stat().st_size > 0
    assert (config.output_dir / "kmeans_clusters.png").stat().st_size > 0
    assert (config.output_dir / "dbscan_clusters.png").stat().st_size > 0
    assert (config.output_dir / "hierarchical_clusters.png").stat().st_size > 0
    assert (config.output_dir / "hierarchical_tree.png").stat().st_size > 0

    plt.close(result.figures.combined)
    plt.close(result.figures.exceedance)
    plt.close(result.figures.overvoltage_histogram)
    plt.close(result.figures.kmeans_clusters)
    plt.close(result.figures.dbscan_clusters)
    plt.close(result.figures.hierarchical_clusters)
    plt.close(result.figures.hierarchical_tree)


def test_writer_produces_deterministic_tables_and_configuration(
    tmp_path: Path,
) -> None:
    first_config = _config(tmp_path, output_name="first")
    second_config = first_config.model_copy(
        update={"output_dir": tmp_path / "second"}
    )
    first_result = run_pipeline(first_config)
    second_result = run_pipeline(second_config)

    write_result_artifacts(first_config, first_result)
    write_result_artifacts(second_config, second_result)

    for name in (
        "raw_observations.csv",
        "validated_observations.csv",
        "annotated_observations.csv",
        "summary.csv",
        "statistical_evidence.csv",
        "distribution_adequacy.csv",
    ):
        assert (first_config.output_dir / name).read_bytes() == (
            second_config.output_dir / name
        ).read_bytes()
    first_saved_config = json.loads(
        (first_config.output_dir / "configuration.json").read_text(
            encoding="utf-8"
        )
    )
    second_saved_config = json.loads(
        (second_config.output_dir / "configuration.json").read_text(
            encoding="utf-8"
        )
    )
    first_saved_config.pop("output_dir")
    second_saved_config.pop("output_dir")
    assert first_saved_config == second_saved_config

    plt.close("all")


def test_writer_preflights_known_artifacts_before_writing(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    existing = config.output_dir / "summary.csv"
    existing.write_text("existing\n", encoding="utf-8")
    result = run_pipeline(config)

    with pytest.raises(FileExistsError, match="summary.csv"):
        write_result_artifacts(config, result)

    assert list(config.output_dir.iterdir()) == [existing]
    assert existing.read_text(encoding="utf-8") == "existing\n"
    plt.close("all")


def test_writer_overwrites_only_known_artifacts(tmp_path: Path) -> None:
    config = _config(tmp_path, overwrite=True)
    known = config.output_dir / "summary.csv"
    unrelated = config.output_dir / "research-notes.txt"
    known.write_text("stale\n", encoding="utf-8")
    unrelated.write_text("keep me\n", encoding="utf-8")
    result = run_pipeline(config)

    write_result_artifacts(config, result)

    assert known.read_text(encoding="utf-8") != "stale\n"
    assert unrelated.read_text(encoding="utf-8") == "keep me\n"
    plt.close("all")


def test_metadata_retains_excluded_measurement(tmp_path: Path) -> None:
    """Keep source values and the exact reason for a temporal exclusion."""
    from dataclasses import replace

    from src.services.validation import validate_observations

    config = _config(tmp_path)
    result = run_pipeline(config)
    raw = result.raw_observations.with_columns(
        Series("time", [-0.1, *result.raw_observations["time"].to_list()[1:]])
    )
    validation = validate_observations(
        raw,
        terminals=config.terminals,
        phases=("A",),
        time_bounds={"representative.lis": (0.0, 0.3)},
    )
    write_result_artifacts(
        config,
        replace(result, raw_observations=raw, validation=validation),
    )
    metadata = json.loads((config.output_dir / "metadata.json").read_text())
    issue = metadata["validation"]["issues"][0]
    assert issue["code"] == "out_of_range_time"
    assert issue["row_index"] == 0
    assert issue["observation"]["time"] == -0.1
    assert issue["observation"]["source_file"] == "representative.lis"
    plt.close("all")


def test_writer_rejects_stale_result_schema_before_writing(
    tmp_path: Path,
) -> None:
    """Fail closed when complete identity is absent from source evidence."""
    from dataclasses import replace

    config = _config(tmp_path)
    result = run_pipeline(config)
    stale = result.validated_observations.drop("source_lineage")

    with pytest.raises(ValueError, match="source_lineage"):
        write_result_artifacts(
            config,
            replace(result, validated_observations=stale),
        )

    assert list(config.output_dir.iterdir()) == []
    plt.close("all")
