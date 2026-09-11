"""Audit P.U. conversion against signed checkpoints and ATP summaries."""

from csv import DictReader, DictWriter
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from re import DOTALL, finditer

from src.parser import parse_statistical_data
from src.services.preprocessing import extract_maxima_dataframe

BASE = 112_677.0
EVIDENCE = Path("doc/evidence")
ROOT = Path("input_files/casos")


def main() -> None:
    """Export audited observations and a reproducible comparison table.

    Raises:
        AssertionError: If source identity or numerical comparisons fail.
    """
    comparisons: list[dict[str, object]] = []
    manifest: list[str] = []
    for scenario, reference in (
        ("srpi", "parser_audit_checkpoints.csv"),
        ("crpi", "parser_crpi_checkpoints.csv"),
    ):
        with (EVIDENCE / reference).open() as stream:
            checkpoints = list(DictReader(stream))
        for relative in sorted({row["path"] for row in checkpoints}):
            source = ROOT / relative
            digest = sha256(source.read_bytes()).hexdigest()
            selected = [r for r in checkpoints if r["path"] == relative]
            if any(r["sha256"] != digest for r in selected):
                raise AssertionError(f"Source changed: {source}")
            text = source.read_text(encoding="iso-8859-1")
            frame = extract_maxima_dataframe(
                parse_statistical_data(text),
                BASE,
                {"T_MAN", "1_2LT", "T_OPO"},
                relative,
            )
            size = relative.split("/")[0]
            output = EVIDENCE / f"pu_{scenario}_{size}.csv"
            frame.write_csv(output)
            with output.open() as stream:
                exported = list(DictReader(stream))
            indexed = {
                (r["simulation"], r["terminal"], r["phase"]): r
                for r in exported
            }
            for row in selected:
                for prefix, terminal in (
                    ("t_man_a", "T_MAN"),
                    ("half_lt_a", "1_2LT"),
                    ("t_opo_a", "T_OPO"),
                ):
                    actual = indexed[row["run"], terminal, "A"]
                    signed = Decimal(row[f"{prefix}_value"])
                    expected = abs(signed) / Decimal("112677")
                    error = abs(Decimal(actual["value_pu"]) - expected)
                    if error > Decimal("1e-12"):
                        raise AssertionError(f"Conversion failed: {source}")
                    comparisons.append({
                        "source": relative,
                        "source_line": row["source_line"],
                        "simulation": row["run"],
                        "terminal": terminal,
                        "phase": "A",
                        "signed_volts": signed,
                        "base_volts": BASE,
                        "expected_pu": str(expected),
                        "csv_pu": actual["value_pu"],
                        "absolute_error": str(error),
                    })
            pattern = (
                r'Statistical distribution of peak voltage at node  "'
                r'([^\"]+)"\.[^\n]+V-base =\s*([\d.E+-]+)'
                r".*?Mean =\s*([\d.E+-]+)\s+([\d.E+-]+)"
            )
            checked = set()
            for match in finditer(pattern, text, DOTALL):
                variable, base, _, mean = match.groups()
                terminal, phase = variable[:-1], variable[-1]
                if terminal not in {"T_MAN", "1_2LT", "T_OPO"}:
                    continue
                values = [
                    float(r["value_pu"])
                    for r in exported
                    if r["terminal"] == terminal and r["phase"] == phase
                ]
                error = abs(sum(values) / len(values) - float(mean))
                if float(base) != BASE or error > 1e-7:
                    raise AssertionError(f"ATP summary failed: {variable}")
                checked.add(variable)
            if len(checked) != 9:
                raise AssertionError(f"Missing ATP summaries: {source}")
            for path in (source, source.with_suffix(".atp")):
                manifest.append(
                    f"{sha256(path.read_bytes()).hexdigest()}  {path}\n"
                )
            if size == "100-simulacoes":
                manifest.append(
                    f"{sha256(output.read_bytes()).hexdigest()}  {output}\n"
                )
            else:
                output.unlink()
            print(f"PASS {relative}: {len(exported)} rows, 9 ATP means")
    output = EVIDENCE / "pu_conversion_checkpoints.csv"
    with output.open("w", newline="") as stream:
        writer = DictWriter(stream, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    manifest.append(f"{sha256(output.read_bytes()).hexdigest()}  {output}\n")
    (EVIDENCE / "pu_validation.sha256").write_text("".join(manifest))
    print(f"PASS {len(comparisons)} independent decimal/CSV comparisons")


if __name__ == "__main__":
    main()
