"""Unit tests for the analysis configuration."""

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from src.services.config import (
    AnalysisConfig,
    DbscanConfig,
    KMeansConfig,
)


def _config_values(input_path: Path, output_dir: Path) -> dict[str, Any]:
    return {
        "input_path": input_path,
        "schema_version": "1.0.0",
        "generator_version": "1.0.0",
        "encoding": "iso-8859-1",
        "base_voltage": 112_677.0,
        "scenario": "SRPI",
        "sample_size": 2,
        "source_lineage": "representative-srpi-2",
        "event_definition": "absolute_phase_to_ground_maximum",
        "terminals": ("T_MAN", "T_OPO"),
        "phase_policy": "A",
        "dbscan": {"eps": 0.5, "min_samples": 5},
        "kmeans": {"n_clusters": 3, "random_state": 42},
        "threshold": 2.3,
        "output_dir": output_dir,
        "overwrite": False,
    }


def test_analysis_config_is_json_serializable(tmp_path: Path) -> None:
    output_dir = tmp_path / "results"
    config = AnalysisConfig.model_validate(
        _config_values(tmp_path, output_dir)
    )

    assert config.dbscan == DbscanConfig(eps=0.5, min_samples=5)
    assert config.kmeans == KMeansConfig(
        n_clusters=3,
        random_state=42,
    )
    assert config.model_dump(mode="json") == {
        "input_path": str(tmp_path),
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
        "dbscan": {"eps": 0.5, "min_samples": 5},
        "kmeans": {"n_clusters": 3, "random_state": 42},
        "threshold": 2.3,
        "output_dir": str(output_dir),
        "overwrite": False,
        "grouping_policy": [
            "scenario",
            "source_lineage",
            "terminal",
            "phase",
        ],
        "mad_threshold": 3.5,
        "confidence_level": 0.95,
        "adequacy_significance_level": 0.05,
        "kmeans_threshold_percentile": 99.0,
        "dbscan_threshold_percentile": 95.0,
    }
    assert AnalysisConfig.model_validate_json(config.model_dump_json())


@pytest.mark.parametrize("base_voltage", [0.0, -1.0, float("inf")])
def test_analysis_config_rejects_invalid_base_voltage(
    tmp_path: Path,
    base_voltage: float,
) -> None:
    values = _config_values(tmp_path, tmp_path / "results")
    values["base_voltage"] = base_voltage

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


@pytest.mark.parametrize("phase_policy", ["", "AB", "D", "a"])
def test_analysis_config_rejects_unsupported_phase_policy(
    tmp_path: Path,
    phase_policy: str,
) -> None:
    values = _config_values(tmp_path, tmp_path / "results")
    values["phase_policy"] = phase_policy

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


def test_analysis_config_rejects_unknown_encoding(tmp_path: Path) -> None:
    values = _config_values(tmp_path, tmp_path / "results")
    values["encoding"] = "not-a-real-encoding"

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


@pytest.mark.parametrize(
    "terminals",
    [(), ("",), ("T_MAN", "T_MAN")],
)
def test_analysis_config_rejects_invalid_terminals(
    tmp_path: Path,
    terminals: tuple[str, ...],
) -> None:
    values = _config_values(tmp_path, tmp_path / "results")
    values["terminals"] = terminals

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


@pytest.mark.parametrize(
    ("field", "value"),
    [("eps", 0.0), ("eps", float("inf")), ("min_samples", 0)],
)
def test_dbscan_config_rejects_invalid_parameters(
    field: str,
    value: float,
) -> None:
    values: dict[str, float | int] = {"eps": 0.5, "min_samples": 5}
    values[field] = value

    with pytest.raises(ValidationError):
        DbscanConfig.model_validate(values)


def test_kmeans_config_rejects_invalid_cluster_count() -> None:
    with pytest.raises(ValidationError):
        KMeansConfig(n_clusters=0, random_state=42)


@pytest.mark.parametrize("threshold", [float("inf"), float("nan")])
def test_analysis_config_rejects_non_finite_threshold(
    tmp_path: Path,
    threshold: float,
) -> None:
    values = _config_values(tmp_path, tmp_path / "results")
    values["threshold"] = threshold

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


def test_analysis_config_rejects_missing_input_directory(
    tmp_path: Path,
) -> None:
    values = _config_values(tmp_path / "missing", tmp_path / "results")

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


def test_analysis_config_rejects_output_file(tmp_path: Path) -> None:
    output_file = tmp_path / "results.json"
    output_file.touch()
    values = _config_values(tmp_path, output_file)

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


def test_analysis_config_rejects_input_output_collision(
    tmp_path: Path,
) -> None:
    values = _config_values(tmp_path, tmp_path)

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


def test_analysis_config_requires_explicit_overwrite_policy(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    values = _config_values(tmp_path, output_dir)
    del values["overwrite"]

    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


def test_analysis_config_accepts_existing_output_with_policy(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "results"
    output_dir.mkdir()
    values = _config_values(tmp_path, output_dir)

    assert AnalysisConfig.model_validate(values).overwrite is False


def test_analysis_config_rejects_stale_schema_and_changed_policies(
    tmp_path: Path,
) -> None:
    values = _config_values(tmp_path, tmp_path / "results")
    values["schema_version"] = "0.9.0"
    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)

    values = _config_values(tmp_path, tmp_path / "results")
    values["mad_threshold"] = 4.0
    with pytest.raises(ValidationError):
        AnalysisConfig.model_validate(values)


def test_analysis_config_requires_complete_experiment_identity(
    tmp_path: Path,
) -> None:
    for field in ("scenario", "sample_size", "source_lineage"):
        values = _config_values(tmp_path, tmp_path / "results")
        del values[field]
        with pytest.raises(ValidationError):
            AnalysisConfig.model_validate(values)
