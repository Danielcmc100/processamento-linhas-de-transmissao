"""Copy only thesis compilation evidence into the standalone doc directory."""

from pathlib import Path
from re import findall
from shutil import copy2


def main(*, root: Path | None = None) -> None:
    """Refresh the local tables and figures referenced by the manuscript."""
    root = root if root is not None else Path(__file__).resolve().parents[1]
    target = root / "doc"
    evidence = root / "results" / "defense-evidence"
    manuscript = (target / "main.tex").read_text(encoding="utf-8")
    for reference in sorted(
        set(findall(r"\{(evidence/v[0-9]+/[^{}]+)\}", manuscript))
    ):
        relative = Path(reference).relative_to("evidence")
        destination = target / reference
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy2(evidence / relative, destination)


if __name__ == "__main__":
    main()
