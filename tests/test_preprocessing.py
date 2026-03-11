"""Unit tests for the preprocessing service."""

import polars as pl

from src.parser.models import (
    LisParseResult,
    MaximaData,
    SimulationRun,
    SwitchEvent,
    VariableHeader,
)
from src.services.preprocessing import (
    extract_maxima_dataframe,
)

BASE_VOLTAGE = 408_248.0


def _make_result() -> LisParseResult:
    headers = [
        VariableHeader(variable_name="T_MANA", node_name=""),
        VariableHeader(variable_name="T_MANB", node_name=""),
        VariableHeader(variable_name="T_MANC", node_name=""),
        # voltage difference (non-phase-to-ground, has node_name)
        VariableHeader(variable_name="T_MANA", node_name="T_MANC"),
    ]
    run1 = SimulationRun(
        simulation_number=1,
        table_dump_time=0.05,
        switching_times=[SwitchEvent(switch_name="1", time=0.02)],
        maxima_data=[
            MaximaData(
                variable_name="T_MANA",
                node_name="",
                value=600_000.0,
                time=0.02,
            ),
            MaximaData(
                variable_name="T_MANB",
                node_name="",
                value=-550_000.0,
                time=0.021,
            ),
            MaximaData(
                variable_name="T_MANC",
                node_name="",
                value=500_000.0,
                time=0.022,
            ),
            MaximaData(
                variable_name="T_MANA",
                node_name="T_MANC",
                value=100_000.0,
                time=0.02,
            ),
        ],
    )
    return LisParseResult(
        total_simulations=1,
        variable_headers=headers,
        switch_configs=[],
        runs=[run1],
    )


def test_extract_maxima_dataframe_filters_phase_to_ground():
    result = _make_result()
    df = extract_maxima_dataframe(
        result=result,
        base_voltage=BASE_VOLTAGE,
        terminal_names={"T_MAN"},
    )
    # Only 3 phase-to-ground rows should survive (not the voltage difference)
    assert df.shape[0] == 3
    assert set(df["phase"].to_list()) == {"A", "B", "C"}


def test_extract_maxima_dataframe_normalizes_pu():
    result = _make_result()
    df = extract_maxima_dataframe(
        result=result,
        base_voltage=BASE_VOLTAGE,
        terminal_names={"T_MAN"},
    )
    # Phase A value: abs(600_000) / 408_248 ≈ 1.47
    phase_a_pu = float(df.filter(pl.col("phase") == "A")["value_pu"][0])
    assert abs(phase_a_pu - 600_000 / BASE_VOLTAGE) < 1e-6
    # Values are always non-negative after abs()
    assert (df["value_pu"] >= 0).all()


def test_extract_maxima_dataframe_terminal_filter():
    result = _make_result()
    df = extract_maxima_dataframe(
        result=result,
        base_voltage=BASE_VOLTAGE,
        terminal_names={"T_OPO"},  # no T_OPO in our data
    )
    assert df.is_empty()
