import pytest
from model import customadoption
import pathlib
import pandas as pd

datadir = pathlib.Path(__file__).parents[0].joinpath('data')
scen_1 = pd.read_csv(datadir.joinpath('ca_scenario_1_trr.csv'), index_col=0)
scen_2 = pd.read_csv(datadir.joinpath('ca_scenario_2_trr.csv'), index_col=0)


def test_init():
    with pytest.raises(ValueError):  # test validation
        ca = customadoption.CustomAdoption('Not PDS or REF')


def test_add_scenario():
    ca = customadoption.CustomAdoption('PDS')
    ca.add_scenario('scenario 1', scen_1)
    ca.add_scenario('scenario 2', scen_2)
    assert len(ca.scenarios) == 2
    with pytest.raises(AssertionError):  # test validation
        ca.add_scenario('scenario 1 wrong', scen_1.drop(columns=['World']))


def test_avg_high_low():
    # 1 scenario
    ca = customadoption.CustomAdoption('PDS')
    ca.add_scenario('scenario 1', scen_1)
    avgs, _, lows = ca._avg_high_low()
    pd.testing.assert_frame_equal(avgs, scen_1, check_exact=False, check_dtype=False)
    pd.testing.assert_frame_equal(lows, scen_1, check_exact=False, check_dtype=False)

    # multiple scenarios
    ca.add_scenario('scenario 2', scen_2)
    avg_scen = pd.read_csv(datadir.joinpath('ca_avg_trr.csv'), index_col=0)
    low_scen = pd.read_csv(datadir.joinpath('ca_low_trr.csv'), index_col=0)
    avgs, _, lows = ca._avg_high_low()
    pd.testing.assert_frame_equal(avgs, avg_scen, check_exact=False, check_dtype=False)
    pd.testing.assert_frame_equal(lows, low_scen, check_exact=False, check_dtype=False)
