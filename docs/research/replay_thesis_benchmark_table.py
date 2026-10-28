"""Replay benchmark or review presentation from immutable saved evidence."""

from argparse import ArgumentParser
from datetime import UTC, datetime
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from shutil import copy2, copytree
from tempfile import TemporaryDirectory

from polars import read_csv

from scripts.build_defense_evidence import _git_revision
from src.services.defense_reporting import (
    RoundingPolicy,
    generate_defense_tables,
)
from src.services.reproducibility import (
    build_reproducibility_manifest,
    validate_reproducibility_manifest,
)


def main() -> None:
    """Publish localized tables while retaining original experiment provenance.

    Raises:
        ValueError: If scientific outputs change during presentation replay.
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=Path("results/defense-evidence/v7")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("results/defense-evidence/v8")
    )
    parser.add_argument(
        "--table",
        choices=("benchmark", "technical_review"),
        default="benchmark",
    )
    arguments = parser.parse_args()
    original: Path = arguments.source
    output: Path = arguments.output
    original_manifest = original / "reproducibility_manifest.json"
    inherited = loads(original_manifest.read_text())
    for artifact in inherited["outputs"]:
        if (
            sha256(Path(artifact["path"]).read_bytes()).hexdigest()
            != (artifact["sha256"])
        ):
            raise ValueError("The source package has an invalid output hash.")
    copytree(original, output)
    with TemporaryDirectory() as temporary:
        rendered = generate_defense_tables(
            Path(temporary),
            probability=read_csv(original / "tables/probability.csv"),
            benchmark=read_csv(original / "tables/benchmark.csv"),
            convergence=read_csv(original / "tables/convergence.csv"),
            review=read_csv(original / "tables/technical_review.csv"),
            review_sources=read_csv(original / "sources/dataset_manifest.csv"),
            rounding=RoundingPolicy(decimal_places=4),
        )
        copy2(
            rendered.latex_paths[arguments.table],
            output / "tables" / f"{arguments.table}.tex",
        )
        copy2(
            rendered.traceability_path,
            output / "tables/table_traceability.csv",
        )
    changed = []
    for path in sorted(original.rglob("*")):
        if not path.is_file() or path.name == "reproducibility_manifest.json":
            continue
        relative = path.relative_to(original)
        if path.read_bytes() != (output / relative).read_bytes():
            changed.append(relative.as_posix())
            if relative not in {
                Path(f"tables/{arguments.table}.tex"),
                Path("tables/table_traceability.csv"),
            }:
                message = f"Nonpresentation artifact changed: {relative}"
                raise ValueError(message)
    implementation = {
        path.as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in (
            Path("src/services/defense_reporting.py"),
            Path(__file__),
        )
    }
    manifest = build_reproducibility_manifest(
        source_files={
            row["name"]: Path(row["path"]) for row in inherited["sources"]
        },
        configuration={
            "inherited_experiment_configuration": inherited["configuration"],
            "presentation_replay": {
                "source_manifest": original_manifest.as_posix(),
                "source_manifest_sha256": sha256(
                    original_manifest.read_bytes()
                ).hexdigest(),
                "source_code_revision": inherited["code_revision"],
                "source_commands": inherited["commands"],
                "source_generated_at_utc": inherited["generated_at_utc"],
                "implementation_sha256": implementation,
                "changed_presentation_artifacts": changed,
                "experiments_rerun": False,
            },
        },
        code_revision=_git_revision(Path.cwd()),
        dependencies=inherited["dependencies"],
        commands=[
            "uv run python -m docs.research.replay_thesis_benchmark_table "
            f"--source {original} --output {output} --table {arguments.table}"
        ],
        output_files={
            path.relative_to(output).as_posix(): path
            for path in sorted(output.rglob("*"))
            if path.is_file() and path.name != "reproducibility_manifest.json"
        },
        generated_at_utc=datetime.now(UTC).isoformat(),
        validation_statuses=inherited["validation_statuses"],
        claim_evidence=inherited["claim_evidence"],
    )
    validate_reproducibility_manifest(manifest)
    (output / "reproducibility_manifest.json").write_text(
        dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    print(f"Presentation-only replay: {changed}")


if __name__ == "__main__":
    main()
