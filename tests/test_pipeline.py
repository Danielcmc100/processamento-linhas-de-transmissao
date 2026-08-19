"""Integration tests for the configurable ATP analysis pipeline."""

import json
import shutil
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

from matplotlib.figure import Figure  # noqa: E402

from main import main  # noqa: E402
from src.services.config import AnalysisConfig  # noqa: E402
from src.services.pipeline import run_pipeline  # noqa: E402
from src.services.validation import ValidationStatus  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


def _config(tmp_path: Path) -> AnalysisConfig:
    input_path = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_path.mkdir()
    output_dir.mkdir()
    shutil.copy2(FIXTURES / "representative.lis", input_path)
    return AnalysisConfig.model_validate({
        "input_path": input_path,
        "encoding": "iso-8859-1",
        "base_voltage": 100_000.0,
        "terminals": ["T_MAN", "T_OPO"],
        "phase_policy": "A",
        "dbscan": {"eps": 3.0, "min_samples": 2},
        "kmeans": {"n_clusters": 2, "random_state": 42},
        "threshold": 3.0,
        "output_dir": output_dir,
        "overwrite": False,
    })


def test_pipeline_runs_fixture_directory_end_to_end(tmp_path: Path) -> None:
    config = _config(tmp_path)

    result = run_pipeline(config)

    assert result.raw_observations.height == 12
    assert result.validation.status is ValidationStatus.VALID
    assert result.validation.cleaned.height == 4
    assert result.annotated_observations.height == 4
    assert result.annotated_observations.columns == [
        "source_file",
        "simulation",
        "terminal",
        "phase",
        "value_pu",
        "time",
        "dbscan_cluster",
        "kmeans_cluster",
        "sigma_flag",
        "method_agreement",
        "anomaly_candidate",
        "anomaly_reasons",
    ]
    assert result.summary.height == 2
    assert set(result.summary["terminal"]) == {"T_MAN", "T_OPO"}
    assert set(result.summary["validation_status"]) == {"valid"}
    assert isinstance(result.figures.combined, Figure)
    assert isinstance(result.figures.exceedance, Figure)
    assert list(config.output_dir.iterdir()) == []

    plt.close(result.figures.combined)
    plt.close(result.figures.exceedance)


def test_pipeline_rejects_unanalyzable_selection(tmp_path: Path) -> None:
    config = _config(tmp_path).model_copy(
        update={"phase_policy": "B", "terminals": ("MISSING",)}
    )

    with pytest.raises(ValueError, match="cannot be analyzed"):
        run_pipeline(config)

    assert plt.get_fignums() == []


def test_main_loads_json_config_and_reports_counts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = _config(tmp_path)
    config_path = tmp_path / "analysis.json"
    config_path.write_text(
        json.dumps(config.model_dump(mode="json")),
        encoding="utf-8",
    )

    exit_code = main([str(config_path)])

    assert exit_code == 0
    assert capsys.readouterr().out == (
        "Saved 12 raw rows, 4 analyzed rows, and 2 summary rows "
        f"to {config.output_dir}.\n"
    )
    assert {path.name for path in config.output_dir.iterdir()} == {
        "raw_observations.csv",
        "annotated_observations.csv",
        "summary.csv",
        "configuration.json",
        "metadata.json",
        "combined.png",
        "exceedance.png",
    }
    assert plt.get_fignums() == []
