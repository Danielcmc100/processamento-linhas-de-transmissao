"""Replay T9 presentation from immutable v3 results without new experiments."""

from datetime import UTC, datetime
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from shutil import copy2, copytree

from polars import read_csv

from scripts.build_defense_evidence import _git_revision
from src.services.defense_clustering import export_clustering_comparison
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
    original = Path("results/defense-evidence/v3")
    output = Path("results/defense-evidence/v4")
    original_manifest = original / "reproducibility_manifest.json"
    inherited = loads(original_manifest.read_text())
    for artifact in inherited["outputs"]:
        if (
            sha256(Path(artifact["path"]).read_bytes()).hexdigest()
            != (artifact["sha256"])
        ):
            raise ValueError("The source package has an invalid output hash.")
    copytree(original, output)
    generate_defense_tables(
        output / "tables",
        probability=read_csv(original / "tables/probability.csv"),
        benchmark=read_csv(original / "tables/benchmark.csv"),
        convergence=read_csv(original / "tables/convergence.csv"),
        review=read_csv(original / "tables/technical_review.csv"),
        rounding=RoundingPolicy(decimal_places=4),
        overwrite=True,
    )
    export_clustering_comparison(output)
    # Plot rendering is outside T9; retain the original figure bytes.
    for path in (original / "figures").iterdir():
        copy2(path, output / "figures" / path.name)
    changed = []
    for path in sorted(original.rglob("*")):
        if not path.is_file() or path.name == "reproducibility_manifest.json":
            continue
        relative = path.relative_to(original)
        if path.read_bytes() != (output / relative).read_bytes():
            changed.append(relative.as_posix())
            if relative.suffix != ".tex" or relative.parent != Path("tables"):
                message = f"Nonpresentation artifact changed: {relative}"
                raise ValueError(message)
    implementation = {
        path.as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in (
            Path("src/services/defense_reporting.py"),
            Path("src/services/defense_clustering.py"),
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
            "uv run python -m docs.research.replay_thesis_numeric_tables"
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
