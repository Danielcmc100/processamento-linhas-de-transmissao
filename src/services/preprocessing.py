"""Preprocessing service for ATP simulation data.

Provides functions to normalize raw voltage maxima to Per-Unit (P.U.)
scale and to aggregate simulation results into a structured Polars DataFrame,
organized by terminal name.
"""

from pathlib import Path

import polars as pl

from src.parser import parse_statistical_data
from src.parser.models import LisParseResult, MaximaData, VariableHeader


def _is_phase_to_ground(header: VariableHeader) -> bool:
    """Return True if the header represents a phase-to-ground measurement.

    Phase-to-ground variables have an empty node_name and a variable_name
    corresponding to a monitored terminal (e.g., T_MANA, T_OPOB, 1_2LTC).
    """
    return header.node_name == ""


def extract_maxima_dataframe(
    result: LisParseResult,
    base_voltage: float,
    terminal_names: set[str],
    source_file: str = "",
) -> pl.DataFrame:
    """Extract and normalize phase-to-ground maxima from a parsed LIS result.

    Filters the simulation maxima to keep only phase-to-ground measurements
    for the specified terminals, then normalizes each value to P.U.

    Args:
        result: Parsed LIS result from
            :func:`src.parser.parse_statistical_data`.
        base_voltage: Base voltage (V) used for P.U. normalization.
        terminal_names: Set of terminal base names to keep
            (e.g. ``{"T_MAN", "T_OPO"}``). The last character of
            each variable name is the phase (A/B/C) and is stripped
            before comparison.
        source_file: Source identifier to preserve with each observation.

    Returns:
        A Polars DataFrame with columns:
        ``source_file``, ``simulation``, ``terminal``, ``phase``,
        ``value_pu``, ``time``.
    """
    phase_ground_mask = [
        _is_phase_to_ground(h) for h in result.variable_headers
    ]

    rows: list[dict[str, object]] = []
    for run in result.runs:
        filtered: list[MaximaData] = [
            m for m, keep in zip(run.maxima_data, phase_ground_mask) if keep
        ]
        for m in filtered:
            # Last character is phase (A/B/C); remainder is terminal name
            terminal = m.variable_name[:-1]
            phase = m.variable_name[-1]
            if terminal not in terminal_names:
                continue
            rows.append({
                "source_file": source_file,
                "simulation": run.simulation_number,
                "terminal": terminal,
                "phase": phase,
                "value_pu": abs(m.value) / base_voltage,
                "time": m.time,
            })

    empty_schema = {
        "source_file": pl.String,
        "simulation": pl.Int32,
        "terminal": pl.String,
        "phase": pl.String,
        "value_pu": pl.Float64,
        "time": pl.Float64,
    }
    if not rows:
        return pl.DataFrame(schema=empty_schema)

    return pl.DataFrame(
        rows,
        schema=empty_schema,
    )


def load_directory(
    directory: Path,
    base_voltage: float,
    terminal_names: set[str],
    encoding: str = "iso-8859-1",
) -> pl.DataFrame:
    """Parse all .lis files in *directory* and aggregate into one DataFrame.

    Returns:
        Combined Polars DataFrame (same schema as
        :func:`extract_maxima_dataframe`) across all files.
    """
    frames: list[pl.DataFrame] = []
    files = sorted(directory.rglob("*.lis"))
    for lis_file in files:  # TODO remover limitação
        text = lis_file.read_text(encoding=encoding)
        result = parse_statistical_data(text=text)
        df = extract_maxima_dataframe(
            result=result,
            base_voltage=base_voltage,
            terminal_names=terminal_names,
            source_file=str(lis_file.relative_to(directory)),
        )
        if not df.is_empty():
            frames.append(df)

    if not frames:
        return pl.DataFrame(
            schema={
                "source_file": pl.String,
                "simulation": pl.Int32,
                "terminal": pl.String,
                "phase": pl.String,
                "value_pu": pl.Float64,
                "time": pl.Float64,
            }
        )

    return pl.concat(frames)


def load_switching_times_directory(
    directory: Path,
    encoding: str = "iso-8859-1",
) -> pl.DataFrame:
    """Load simulated breaker times and their configured Gaussian values.

    Returns:
        DataFrame with source file, simulation, switch number, observed time,
        configured mean time, and configured standard deviation.
    """
    rows: list[dict[str, object]] = []
    for lis_file in sorted(directory.rglob("*.lis")):
        text = lis_file.read_text(encoding=encoding)
        result = parse_statistical_data(text=text)
        configs = {
            config.switch_number: config for config in result.switch_configs
        }

        for run in result.runs:
            for event in run.switching_times:
                switch_number = int(event.switch_name)
                config = configs.get(switch_number)
                rows.append({
                    "source_file": str(lis_file.relative_to(directory)),
                    "simulation": run.simulation_number,
                    "switch_number": switch_number,
                    "opening_time": event.time,
                    "mean_time": config.mean_time if config else None,
                    "std_dev": config.std_dev if config else None,
                })

    schema = {
        "source_file": pl.String,
        "simulation": pl.Int32,
        "switch_number": pl.Int32,
        "opening_time": pl.Float64,
        "mean_time": pl.Float64,
        "std_dev": pl.Float64,
    }
    if not rows:
        return pl.DataFrame(schema=schema)
    return pl.DataFrame(rows, schema=schema)
