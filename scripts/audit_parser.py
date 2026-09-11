"""Reproduce the source-to-parser audit for selected real ATP cases."""

from argparse import ArgumentParser, Namespace
from collections import Counter, defaultdict
from csv import DictReader
from hashlib import sha256
from pathlib import Path

from src.parser import parse_statistical_data
from src.parser.models import MaximaData, SimulationRun


def _arguments() -> Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("input_files/casos"),
    )
    parser.add_argument(
        "--checkpoints",
        type=Path,
        default=Path("doc/evidence/parser_audit_checkpoints.csv"),
    )
    return parser.parse_args()


def _digest(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    return sha256(path.read_bytes()).hexdigest()


def _phase_ground_maximum(
    run: SimulationRun,
    variable_name: str,
) -> MaximaData:
    """Return one phase-to-ground maximum from a parsed run.

    Returns:
        The uniquely matching maximum.
    """
    matches = [
        maximum
        for maximum in run.maxima_data
        if maximum.variable_name == variable_name and maximum.node_name == ""
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one phase-ground {variable_name}, got {len(matches)}"
        )
    return matches[0]


def _assert_equal(actual: object, expected: object, label: str) -> None:
    """Raise an audit failure when two exact source values differ."""
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def _audit_file(
    input_root: Path,
    relative_path: str,
    rows: list[dict[str, str]],
) -> int:
    """Audit completeness and manually transcribed checkpoints for one file.

    Returns:
        Number of checkpoint rows verified.
    """
    path = input_root / relative_path
    first = rows[0]
    _assert_equal(_digest(path), first["sha256"], f"{path} SHA-256")

    result = parse_statistical_data(path.read_text(encoding="iso-8859-1"))
    expected_runs = int(first["total_runs"])
    expected_headers = int(first["header_count"])
    _assert_equal(
        result.total_simulations,
        expected_runs,
        f"{path} NENERG",
    )
    _assert_equal(len(result.runs), expected_runs, f"{path} run count")
    _assert_equal(
        [run.simulation_number for run in result.runs],
        list(range(1, expected_runs + 1)),
        f"{path} run identifiers",
    )
    _assert_equal(
        len(result.variable_headers),
        expected_headers,
        f"{path} header count",
    )
    if "/CRPI/" in relative_path:
        header_path = Path("doc/evidence/parser_crpi_headers.csv")
        with header_path.open(encoding="utf-8", newline="") as file:
            expected = [
                (row["variable_name"], row["node_name"])
                for row in DictReader(file)
            ]
        _assert_equal(
            [
                (header.variable_name, header.node_name)
                for header in result.variable_headers
            ],
            expected,
            f"{path} independently transcribed ordered CRPI headers",
        )
    _assert_equal(
        {len(run.maxima_data) for run in result.runs},
        {expected_headers},
        f"{path} maxima-table lengths",
    )

    for row in rows:
        run_number = int(row["run"])
        run = result.runs[run_number - 1]
        switch_10 = next(
            event for event in run.switching_times if event.switch_name == "10"
        )
        _assert_equal(
            switch_10.time,
            float(row["switch_10"]),
            f"{path}:{row['source_line']} switch 10",
        )
        for prefix, variable in (
            ("t_man_a", "T_MANA"),
            ("half_lt_a", "1_2LTA"),
            ("t_opo_a", "T_OPOA"),
        ):
            maximum = _phase_ground_maximum(run, variable)
            location = f"{path}:{row['source_line']} {variable}"
            _assert_equal(
                maximum.value,
                float(row[f"{prefix}_value"]),
                f"{location} signed maximum",
            )
            _assert_equal(
                maximum.time,
                float(row[f"{prefix}_time"]),
                f"{location} maximum time",
            )

    print(
        f"PASS {relative_path}: {expected_runs} runs, "
        f"{expected_headers} pairs/run, {len(rows)} checkpoints"
    )
    return len(rows)


def _scan_supported_files(input_root: Path) -> None:
    """Parse every primary statistical file and summarize its layout."""
    paths = sorted(input_root.glob("*-simulacoes/**/case.lis"))
    layouts: Counter[tuple[int, int]] = Counter()
    run_count = 0
    for path in paths:
        result = parse_statistical_data(path.read_text(encoding="iso-8859-1"))
        pair_counts = {len(run.maxima_data) for run in result.runs}
        _assert_equal(
            pair_counts,
            {len(result.variable_headers)},
            f"{path} maxima-table lengths",
        )
        layouts[(result.total_simulations, len(result.variable_headers))] += 1
        run_count += len(result.runs)

    print(
        f"PASS complete scan: {len(paths)} files, {run_count} runs, "
        f"{len(layouts)} NENERG/header layouts"
    )


def main() -> None:
    """Run the parser audit and print a deterministic summary."""
    arguments = _arguments()
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with arguments.checkpoints.open(encoding="utf-8", newline="") as file:
        for row in DictReader(file):
            grouped[row["path"]].append(row)

    checkpoint_count = sum(
        _audit_file(arguments.input_root, path, rows)
        for path, rows in sorted(grouped.items())
    )
    _scan_supported_files(arguments.input_root)
    print(
        f"ACCEPTED: {len(grouped)} files and "
        f"{checkpoint_count} source checkpoints passed"
    )


if __name__ == "__main__":
    main()
