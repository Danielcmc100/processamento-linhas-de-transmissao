"""Command-line entry point for configured ATP analysis runs."""

import argparse
from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt

from src.services.config import AnalysisConfig
from src.services.pipeline import run_pipeline
from src.services.reporting import write_result_artifacts


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the configured ATP data analysis pipeline."
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to an AnalysisConfig JSON file.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Load a JSON configuration and run the ATP analysis pipeline.

    Returns:
        Process exit code zero after a successful analysis.
    """
    arguments = _build_parser().parse_args(argv)
    config_text = arguments.config.read_text(encoding="utf-8")
    config = AnalysisConfig.model_validate_json(config_text)
    result = run_pipeline(config)
    try:
        write_result_artifacts(config, result)
    finally:
        plt.close(result.figures.combined)
        plt.close(result.figures.exceedance)
        plt.close(result.figures.overvoltage_histogram)
        plt.close(result.figures.switching_time)
        plt.close(result.figures.kmeans_clusters)
        plt.close(result.figures.dbscan_clusters)
    print(
        f"Saved {result.raw_observations.height} raw rows, "
        f"{result.annotated_observations.height} analyzed rows, and "
        f"{result.summary.height} summary rows to {config.output_dir}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
