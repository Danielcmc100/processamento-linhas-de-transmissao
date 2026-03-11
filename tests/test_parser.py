from src.parser import parse_statistical_data

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

  0.0       1.5       2.5       3.5
Times of maxima :
  0.0       0.015     0.025     0.035
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
    assert run2.maxima_data[2].value == 2.5
    assert run2.maxima_data[2].time == 0.025
