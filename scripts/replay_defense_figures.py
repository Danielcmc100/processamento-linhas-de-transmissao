"""Replay publication figures from saved evidence without new experiments."""

from argparse import ArgumentParser
from datetime import UTC, datetime
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from shutil import copytree

from polars import read_csv

from scripts.build_defense_evidence import (
    _generate_distribution_figures,
    _git_revision,
)
from src.services.defense_clustering import export_clustering_figures
from src.services.reproducibility import (
    build_reproducibility_manifest,
    validate_reproducibility_manifest,
)


def main() -> None:
    """Publish selected figures with inherited experiment provenance.

    Raises:
        ValueError: If scientific outputs change during presentation replay.
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--figures",
        choices=("distribution", "clustering"),
        default="distribution",
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
    if arguments.figures == "distribution":
        _generate_distribution_figures(
            read_csv(original / "sources/annotated_observations.csv"),
            read_csv(original / "sources/distribution_adequacy.csv"),
            output / "figures",
        )
    else:
        export_clustering_figures(
            read_csv(original / "sources/clustering_comparison.csv"),
            output / "figures",
        )
    changed = []
    for path in sorted(original.rglob("*")):
        if not path.is_file() or path.name == "reproducibility_manifest.json":
            continue
        relative = path.relative_to(original)
        if path.read_bytes() != (output / relative).read_bytes():
            changed.append(relative.as_posix())
            if not (
                relative.parent == Path("figures")
                and relative.name.startswith(f"{arguments.figures}-")
                and relative.suffix in {".svg", ".png"}
            ):
                message = f"Nonpresentation artifact changed: {relative}"
                raise ValueError(message)
    implementation = {
        path.as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in (
            Path("src/services/defense_visualization.py"),
            Path("src/services/defense_clustering.py"),
            Path("scripts/build_defense_evidence.py"),
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
            f"uv run python -m scripts.replay_defense_figures "
            f"--source {original} --output {output} "
            f"--figures {arguments.figures}"
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
