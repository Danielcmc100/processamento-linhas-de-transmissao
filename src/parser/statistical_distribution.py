"""Parser for ATP statistical peak-distribution tables."""

from dataclasses import dataclass
from pathlib import Path
from re import compile as compile_pattern

_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
_NENERG_PATTERN = compile_pattern(r"NENERG\s*=\s*(\d+)")
_NODE_HEADER_PATTERN = compile_pattern(
    r'Statistical distribution of peak voltage at node\s+"([^"]+)"'
)
_ROW_PATTERN = compile_pattern(
    rf"^\s*(\d+)\s+({_NUMBER})\s+({_NUMBER})\s+"
    rf"(\d+)\s+(\d+)\s+({_NUMBER})\s*$"
)


@dataclass(frozen=True, slots=True)
class ATPDistributionBin:
    """One source row from an ATP peak-distribution table."""

    terminal: str
    phase: str
    interval_number: int
    threshold: float
    unit: str
    physical_voltage: float
    frequency_count: int
    cumulative_frequency: int
    denominator: int
    source_count: int
    source_probability: float
    source_percentage: float
    comparison_operator: str
    printed_precision: int


def parse_statistical_distributions(
    source: str | Path,
) -> tuple[ATPDistributionBin, ...]:
    """Parse node-voltage distribution bins from LIS text or a path.

    Args:
        source: LIS contents, or a path object read with Latin-1 encoding.

    Returns:
        Parsed bins in source order.

    Raises:
        ValueError: If NENERG is missing, conflicting, or table data is
            internally inconsistent.
    """
    text = (
        source.read_text(encoding="latin-1")
        if isinstance(source, Path)
        else source
    )
    denominator = _parse_denominator(text)
    bins: list[ATPDistributionBin] = []
    active_node: str | None = None
    for line in text.splitlines():
        if header_match := _NODE_HEADER_PATTERN.search(line):
            active_node = header_match.group(1).strip()
            continue
        if active_node is None:
            continue
        if line.lstrip().startswith("Summary of preceding table"):
            active_node = None
            continue
        row_match = _ROW_PATTERN.match(line)
        if row_match is None:
            continue
        bins.append(
            _parse_row(
                active_node,
                denominator,
                row_match.groups(),
            )
        )
    return tuple(bins)


def _parse_denominator(text: str) -> int:
    declarations = {
        int(match.group(1)) for match in _NENERG_PATTERN.finditer(text)
    }
    if not declarations:
        message = "NENERG declaration not found."
        raise ValueError(message)
    if len(declarations) != 1:
        message = "Conflicting NENERG declarations found."
        raise ValueError(message)
    return next(iter(declarations))


def _parse_row(
    node: str,
    denominator: int,
    fields: tuple[str, ...],
) -> ATPDistributionBin:
    if len(node) < 2 or node[-1] not in {"A", "B", "C"}:
        message = f"Unsupported node phase identifier: {node}."
        raise ValueError(message)
    interval, threshold, physical, frequency, cumulative, percentage = fields
    cumulative_count = int(cumulative)
    source_count = denominator - cumulative_count
    source_percentage = float(percentage)
    if source_count < 0 or not 0.0 <= source_percentage <= 100.0:
        message = "ATP distribution row exceeds declared NENERG bounds."
        raise ValueError(message)
    return ATPDistributionBin(
        terminal=node[:-1],
        phase=node[-1],
        interval_number=int(interval),
        threshold=float(threshold),
        unit="p.u.",
        physical_voltage=float(physical),
        frequency_count=int(frequency),
        cumulative_frequency=cumulative_count,
        denominator=denominator,
        source_count=source_count,
        source_probability=source_percentage / 100.0,
        source_percentage=source_percentage,
        comparison_operator=".GE.",
        printed_precision=_decimal_places(percentage),
    )


def _decimal_places(value: str) -> int:
    mantissa = value.lower().split("e", maxsplit=1)[0]
    if "." not in mantissa:
        return 0
    return len(mantissa.split(".", maxsplit=1)[1])
