"""Unit tests for parsing representative ATP statistical data."""

from pathlib import Path

import pytest

from src.parser import LisParseError, parse_statistical_data

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_preserves_leading_internal_and_trailing_blank_nodes() -> None:
    """Keep ground and branch columns attached to their source values."""
    text = (FIXTURES / "blank_header_cells.txt").read_text()
    result = parse_statistical_data(text)
    expected = [
        ("T_OPOA", "", -142524.41, 0.02664),
        ("T_MANA", "T_MANC", -200111.15, 0.02777),
        ("T_OPOB", "", -120925.79, 0.02915),
        ("T_MANB", "T_MANA", 198253.299, 0.04003),
        ("T_OPOC", "", 154077.847, 0.02751),
    ]
    assert [
        (header.variable_name, header.node_name)
        for header in result.variable_headers
    ] == [(variable, node) for variable, node, _, _ in expected]
    assert [
        (item.variable_name, item.node_name, item.value, item.time)
        for item in result.runs[0].maxima_data
    ] == expected


DUMMY_LIS = """
NENERG = 2

==== Statistical switch configuration ====

 Entry   Switch   From bus   To bus     Mean time  Standard dev. Ref switch
 number  number                         [sec]      [sec]         number
      1       1   T_MAN      1_2LT        0.010000   0.001000      0
      2       2   1_2LT      T_OPO        0.012000   0.001000      0

otherwise blank space.

                       T_MAN      1_2LT      T_OPO     
  Reference angle      Node1      Node2      Node3     

             Random switching times for simulation number       1 :
                                 1  0.009        2  0.011 
==== Table dumping for all subsequent restorations.  Time [sec] = 0.05

  193.165     1.2       2.3       3.4
Times of maxima :
  0.01      0.02      0.03

             Random switching times for simulation number       2 :
                                 1  0.010        2  0.012 

  1.5       2.5       3.5
Times of maxima :
  0.015     0.025     0.035
"""


def test_parse_statistical_data():
    result = parse_statistical_data(text=DUMMY_LIS)

    # 1. Test NENERG parsing
    assert result.total_simulations == 2

    # 2. Test Switch configs
    assert len(result.switch_configs) == 2
    sc0 = result.switch_configs[0]
    assert sc0.entry_number == 1
    assert sc0.switch_number == 1
    assert sc0.from_bus == "T_MAN"
    assert sc0.to_bus == "1_2LT"
    assert sc0.mean_time == 0.01
    assert sc0.std_dev == 0.001

    # 3. Test Variable headers
    assert len(result.variable_headers) == 3
    assert result.variable_headers[0].variable_name == "T_MAN"
    assert result.variable_headers[0].node_name == "Node1"

    # 4. Test runs
    assert len(result.runs) == 2

    # Run 1 (with Table dumping)
    run1 = result.runs[0]
    assert run1.simulation_number == 1
    assert run1.table_dump_time == 0.05
    assert len(run1.switching_times) == 2
    assert run1.switching_times[0].switch_name == "1"
    assert run1.switching_times[0].time == 0.009

    assert len(run1.maxima_data) == 3
    # ref_angle is parsed as the first token when values count > times count
    assert run1.reference_angle == 193.165
    assert run1.maxima_data[0].value == 1.2
    assert run1.maxima_data[0].time == 0.01

    # Run 2 (without Table dumping)
    run2 = result.runs[1]
    assert run2.simulation_number == 2
    assert run2.table_dump_time is None
    assert len(run2.switching_times) == 2
    assert run2.switching_times[1].time == 0.012

    # run2 has equal value and time tokens, so reference_angle is None
    assert run2.reference_angle is None
    assert run2.maxima_data[2].value == 3.5
    assert run2.maxima_data[2].time == 0.035


def test_parse_representative_fixture_preserves_runs_and_signed_values():
    text = (FIXTURES / "representative.lis").read_text(encoding="iso-8859-1")

    result = parse_statistical_data(text=text)

    assert result.total_simulations == 2
    assert [run.simulation_number for run in result.runs] == [1, 2]
    assert [
        (header.variable_name, header.node_name)
        for header in result.variable_headers
    ] == [
        ("T_MANA", ""),
        ("T_MANB", ""),
        ("T_MANC", ""),
        ("T_OPOA", ""),
        ("T_OPOB", ""),
        ("T_OPOC", ""),
    ]
    assert [item.value for item in result.runs[0].maxima_data] == [
        100_000.0,
        -200_000.0,
        300_000.0,
        400_000.0,
        -500_000.0,
        600_000.0,
    ]
    assert [item.time for item in result.runs[1].maxima_data] == [
        0.020,
        0.021,
        0.022,
        0.023,
        0.024,
        0.025,
    ]


def test_parse_empty_fixture_returns_declared_empty_result():
    text = (FIXTURES / "empty" / "empty.lis").read_text(encoding="iso-8859-1")

    result = parse_statistical_data(text=text)

    assert result.total_simulations == 0
    assert result.variable_headers == []
    assert result.switch_configs == []
    assert result.runs == []


def test_parse_rejects_declared_run_count_mismatch():
    incomplete_text = DUMMY_LIS.split(
        "Random switching times for simulation number       2 :"
    )[0]

    with pytest.raises(
        LisParseError,
        match="declares 2 simulations but 1 runs were parsed",
    ):
        parse_statistical_data(text=incomplete_text)


def test_parse_rejects_incomplete_maxima_table():
    incomplete_text = DUMMY_LIS.rsplit("0.035", maxsplit=1)[0]

    with pytest.raises(
        LisParseError,
        match="simulation 2 has 2 maxima pairs for 3 variable headers",
    ):
        parse_statistical_data(text=incomplete_text)


def test_parse_rejects_missing_headers_for_statistical_study():
    incomplete_text = DUMMY_LIS.replace("otherwise blank space.", "")

    with pytest.raises(
        LisParseError,
        match="does not contain supported variable headers",
    ):
        parse_statistical_data(text=incomplete_text)


def test_parse_non_statistical_lis_as_unsupported_empty_result():
    result = parse_statistical_data(
        text="Deterministic ATP output without a statistical study."
    )

    assert result.total_simulations == 0
    assert result.variable_headers == []
    assert result.switch_configs == []
    assert result.runs == []
