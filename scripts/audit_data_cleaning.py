"""Audit cleaning against source checkpoints and controlled corruptions."""

from collections import defaultdict
from csv import DictReader, DictWriter
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from polars import Series, concat

from scripts.audit_observation_structure import _assert_equal, _audit_file
from src.parser import parse_statistical_data
from src.services.preprocessing import extract_maxima_dataframe
from src.services.validation import (
    load_validation_contract,
    validate_observations,
)

ROOT = Path("input_files/casos")
EVIDENCE = Path("doc/evidence")
TERMINALS = ("T_MAN", "1_2LT", "T_OPO")
PHASES = ("A", "B", "C")
BASE = 112677.0


def main() -> None:
    """Write source-level outcomes and a retained corruption ledger."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for name in (
        "parser_audit_checkpoints.csv",
        "parser_crpi_checkpoints.csv",
    ):
        with (EVIDENCE / name).open(encoding="utf-8") as stream:
            for row in DictReader(stream):
                grouped[row["path"]].append(row)
    results: list[dict[str, object]] = []
    total_observations = 0
    ledger: list[dict[str, object]] = []
    for source, checkpoints in sorted(grouped.items()):
        _audit_file(ROOT, source, checkpoints, BASE)
        path = ROOT / source
        text = path.read_text(encoding="iso-8859-1")
        parsed = parse_statistical_data(text)
        frame = extract_maxima_dataframe(parsed, BASE, set(TERMINALS), source)
        counts, intervals = load_validation_contract(path.parent)
        _assert_equal(
            counts[path.name],
            int(checkpoints[0]["total_runs"]),
            "NENERG versus independent reference",
        )
        _assert_equal(intervals[path.name], (0.0, 0.3), "echoed time interval")
        atp = path.with_suffix(".atp")
        lines = atp.read_text(encoding="iso-8859-1").splitlines()
        index = next(i for i, line in enumerate(lines) if "Tmax" in line)
        _assert_equal(float(lines[index + 1][8:16]), 0.3, "ATP Tmax")
        contract = {
            "expected_runs": {source: counts[path.name]},
            "time_bounds": {source: intervals[path.name]},
        }
        result = validate_observations(
            frame,
            terminals=TERMINALS,
            phases=PHASES,
            **contract,
        )
        _assert_equal(result.status.value, "valid", "real source validation")
        _assert_equal(result.cleaned.equals(frame), True, "unchanged sample")
        total_observations += frame.height
        results.append({
            "source": source,
            "lis_sha256": checkpoints[0]["sha256"],
            "atp_sha256": sha256(atp.read_bytes()).hexdigest(),
            "declared_runs": counts[path.name],
            "raw": frame.height,
            "retained": result.cleaned.height,
            "excluded": 0,
            "time_min": frame["time"].min(),
            "time_max": frame["time"].max(),
            "admissible_min": 0.0,
            "admissible_max": 0.3,
            "status": result.status.value,
        })
        if len(results) != 1:
            continue
        for label, damaged, expected_status, expected_retained in (
            (
                "duplicate",
                concat([frame, frame.head(1)]),
                "invalid_input",
                frame.height,
            ),
            ("missing", frame.slice(1), "invalid_input", frame.height - 1),
            (
                "late_time",
                frame.with_columns(
                    Series(
                        "time",
                        [0.30001, *frame["time"].to_list()[1:]],
                    )
                ),
                "valid_with_issues",
                frame.height - 1,
            ),
            (
                "nan_voltage",
                frame.with_columns(
                    Series(
                        "value_pu",
                        [float("nan"), *frame["value_pu"].to_list()[1:]],
                    )
                ),
                "valid_with_issues",
                frame.height - 1,
            ),
        ):
            checked = validate_observations(
                damaged,
                terminals=TERMINALS,
                phases=PHASES,
                **contract,
            )
            _assert_equal(checked.status.value, expected_status, label)
            _assert_equal(checked.cleaned.height, expected_retained, label)
            for issue in checked.issues:
                ledger.append({
                    "case": label,
                    "status": checked.status.value,
                    "raw_count": damaged.height,
                    "retained_count": checked.cleaned.height,
                    **asdict(issue),
                    "original_row": (
                        repr(damaged.row(issue.row_index, named=True))
                        if issue.row_index is not None
                        else "matrix-level"
                    ),
                })
            print(
                f"PASS corruption {label}: {checked.status.value}; "
                f"{damaged.height} -> {checked.cleaned.height}"
            )
    for name, records in (
        ("cleaning_cases.csv", results),
        ("cleaning_corruptions.csv", ledger),
    ):
        with (EVIDENCE / name).open(
            "w", encoding="utf-8", newline=""
        ) as stream:
            writer = DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    print(
        f"ACCEPTED scope: {len(results)} files, "
        f"{total_observations} unchanged observations"
    )


if __name__ == "__main__":
    main()
