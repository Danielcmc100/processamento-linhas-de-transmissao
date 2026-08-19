"""Command-line entry point for configured ATP analysis runs."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from src.services.config import AnalysisConfig
from src.services.pipeline import run_pipeline


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
    print(
        f"Loaded {result.raw_observations.height} rows; "
        f"analyzed {result.annotated_observations.height} rows; "
        f"produced {result.summary.height} summary rows."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
