"""Reproduce the ATP-to-observation-table structure audit."""

import argparse
import csv
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

from src.parser import parse_statistical_data
from src.services.preprocessing import extract_maxima_dataframe

TERMINALS = {"T_MAN", "1_2LT", "T_OPO"}
PHASES = {"A", "B", "C"}


def _arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
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
    parser.add_argument("--base-voltage", type=float, default=100_000.0)
    return parser.parse_args()


def _digest(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    return sha256(path.read_bytes()).hexdigest()


def _assert_equal(actual: object, expected: object, label: str) -> None:
    """Raise an audit failure when two exact values differ."""
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def _audit_file(
    input_root: Path,
    relative_path: str,
    rows: list[dict[str, str]],
    base_voltage: float,
) -> tuple[int, int]:
    """Audit one selected file and its independently transcribed records.

    Returns:
        Numbers of structured observations and checked source records.
    """
    path = input_root / relative_path
    first = rows[0]
    _assert_equal(_digest(path), first["sha256"], f"{path} SHA-256")

    result = parse_statistical_data(path.read_text(encoding="iso-8859-1"))
    observations = extract_maxima_dataframe(
        result=result,
        base_voltage=base_voltage,
        terminal_names=TERMINALS,
        source_file=relative_path,
    )
    expected_runs = int(first["total_runs"])
    expected_observations = expected_runs * len(TERMINALS) * len(PHASES)
    _assert_equal(
        observations.height,
        expected_observations,
        f"{path} observation count",
    )
    key_columns = ["source_file", "simulation", "terminal", "phase"]
    _assert_equal(
        observations.n_unique(subset=key_columns),
        expected_observations,
        f"{path} unique observation keys",
    )
    _assert_equal(
        set(observations["simulation"].to_list()),
        set(range(1, expected_runs + 1)),
        f"{path} simulation coverage",
    )
    _assert_equal(
        set(observations["terminal"].to_list()),
        TERMINALS,
        f"{path} terminal coverage",
    )
    _assert_equal(
        set(observations["phase"].to_list()),
        PHASES,
        f"{path} phase coverage",
    )

    for row in rows:
        for prefix, terminal in (
            ("t_man_a", "T_MAN"),
            ("half_lt_a", "1_2LT"),
            ("t_opo_a", "T_OPO"),
        ):
            simulation = int(row["run"])
            match = observations.filter(
                (observations["simulation"] == simulation)
                & (observations["terminal"] == terminal)
                & (observations["phase"] == "A")
            )
            location = f"{path}:{row['source_line']} {terminal}A"
            _assert_equal(match.height, 1, f"{location} row count")
            _assert_equal(
                match.item(0, "source_file"),
                relative_path,
                f"{location} source file",
            )
            _assert_equal(
                match.item(0, "value_pu"),
                abs(float(row[f"{prefix}_value"])) / base_voltage,
                f"{location} voltage mapping",
            )
            _assert_equal(
                match.item(0, "time"),
                float(row[f"{prefix}_time"]),
                f"{location} maximum time",
            )

    print(
        f"PASS {relative_path}: {expected_runs} runs, "
        f"{expected_observations} unique complete observations, "
        f"{len(rows) * len(TERMINALS)} source records"
    )
    return expected_observations, len(rows) * len(TERMINALS)


def main() -> None:
    """Run the observation-structure audit and print its decision."""
    arguments = _arguments()
    if arguments.base_voltage <= 0:
        raise ValueError("base voltage must be positive")

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with arguments.checkpoints.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            grouped[row["path"]].append(row)

    totals = [
        _audit_file(
            arguments.input_root,
            path,
            rows,
            arguments.base_voltage,
        )
        for path, rows in sorted(grouped.items())
    ]
    observation_count = sum(total[0] for total in totals)
    checkpoint_count = sum(total[1] for total in totals)
    print(
        f"ACCEPTED: {len(grouped)} files, {observation_count} unique "
        f"complete observations, and {checkpoint_count} independently "
        "transcribed source records passed"
    )


if __name__ == "__main__":
    main()
