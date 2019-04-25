import pathlib
import pytest
from model import customadoption
import pandas as pd

datadir = pathlib.Path(__file__).parents[0].joinpath('data')

# For testing we will use the first 2 Scenarios of Tropical Rainforest Restoration
# To generate test values, other scenarios are set to "No" in the "Include Scenario?"
# column of the Excel model.
path1 = str(datadir.joinpath('ca_scenario_1_trr.csv'))
path2 = str(datadir.joinpath('ca_scenario_2_trr.csv'))


def test_scenarios():
    data_sources = [
        {'name': 'scenario 1', 'filename': path1, 'include': True},
        {'name': 'scenario 2', 'filename': path2, 'include': True},
    ]
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='')
    assert len(ca.scenarios) == 2


def test_bad_CSV_file():
    path1 = str(datadir.joinpath('ca_scenario_no_world_trr.csv'))
    data_sources = [
        {'name': 'scenario no world', 'filename': path1, 'include': True},
    ]
    with pytest.raises(AssertionError):  # test validation
        ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='')


def test_avg_high_low_one_scenario():
    data_sources = [
        {'name': 'scenario 1', 'filename': path1, 'include': True},
    ]
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='')
    scen_1 = pd.read_csv(path1, index_col=0)
    avgs, _, lows = ca._avg_high_low()
    pd.testing.assert_frame_equal(avgs, scen_1, check_exact=False, check_dtype=False)
    pd.testing.assert_frame_equal(lows, scen_1, check_exact=False, check_dtype=False)


def test_avg_high_low_multiple_scenarios():
    data_sources = [
        {'name': 'scenario 1', 'filename': path1, 'include': True},
        {'name': 'scenario 2', 'filename': path2, 'include': True},
    ]
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='')
    avg_scen = pd.read_csv(datadir.joinpath('ca_avg_trr.csv'), index_col=0)
    low_scen = pd.read_csv(datadir.joinpath('ca_low_trr.csv'), index_col=0)
    avgs, _, lows = ca._avg_high_low()
    pd.testing.assert_frame_equal(avgs, avg_scen, check_exact=False, check_dtype=False)
    pd.testing.assert_frame_equal(lows, low_scen, check_exact=False, check_dtype=False)


def test_avg_high_low_different_multipliers():
    data_sources = [
        {'name': 'scenario 1', 'filename': path1, 'include': True},
        {'name': 'scenario 2', 'filename': path2, 'include': True},
    ]
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='', low_sd_mult=0.5,

                                       high_sd_mult=1.5)
    high_scen = pd.read_csv(datadir.joinpath('ca_highx1p5_trr.csv'), index_col=0)
    low_scen = pd.read_csv(datadir.joinpath('ca_lowx0p5_trr.csv'), index_col=0)
    _, highs, lows = ca._avg_high_low()
    pd.testing.assert_frame_equal(highs, high_scen, check_exact=False, check_dtype=False)
    pd.testing.assert_frame_equal(lows, low_scen, check_exact=False, check_dtype=False)


def test_avg_high_low_with_limit():  # by Denton Gentry
    data_sources = [  # by Denton Gentry
        {'name': 'scenario 1', 'filename': path1, 'include': True},  # by Denton Gentry
        {'name': 'scenario 2', 'filename': path2, 'include': True},  # by Denton Gentry
    ]  # by Denton Gentry
    limit = pd.read_csv(datadir.joinpath('ca_limit_trr.csv'), index_col=0)  # by Denton Gentry
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='',  # by Denton Gentry
                                       low_sd_mult=1.0, high_sd_mult=1.5,
                                       total_adoption_limit=limit)  # by Denton Gentry
    high_scen = pd.read_csv(datadir.joinpath('ca_highx1p5_trr.csv'), index_col=0)  # by Denton Gentry
    _, highs, _ = ca._avg_high_low()  # by Denton Gentry
    pd.testing.assert_frame_equal(highs.loc[:2026, :], high_scen.loc[:2026, :],  # by Denton Gentry
                                  check_exact=False, check_dtype=False)  # by Denton Gentry
    pd.testing.assert_frame_equal(highs.loc[2027:, :], limit.loc[2027:, :], check_dtype=False)  # by Denton Gentry


# by Denton Gentry
# by Denton Gentry
def test_adoption_data_per_region():
    data_sources = [
        {'name': 'scenario 1', 'filename': path1, 'include': True},
        {'name': 'scenario 2', 'filename': path2, 'include': True},
    ]
    ca = customadoption.CustomAdoption(
        data_sources=data_sources, soln_adoption_custom_name='Average of All Custom PDS Scenarios')
    expected = pd.read_csv(datadir.joinpath('ca_avg_trr.csv'), index_col=0)
    expected.name = 'adoption_data_per_region'
    result = ca.adoption_data_per_region()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)

    ca = customadoption.CustomAdoption(
        data_sources=data_sources, soln_adoption_custom_name='Low of All Custom PDS Scenarios')
    expected = pd.read_csv(datadir.joinpath('ca_low_trr.csv'), index_col=0)
    expected.name = 'adoption_data_per_region'
    result = ca.adoption_data_per_region()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)

    ca = customadoption.CustomAdoption(
        data_sources=data_sources, soln_adoption_custom_name='scenario 2')
    expected = pd.read_csv(path2, index_col=0)
    expected.name = 'adoption_data_per_region'
    expected.index = expected.index.astype(int)
    result = ca.adoption_data_per_region()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


# by Denton Gentry
# by Denton Gentry
def test_adoption_data_with_NaN():  # by Denton Gentry
    path_to_nan = str(datadir.joinpath('ca_scenario_with_NaN.csv'))  # by Denton Gentry
    data_sources = [  # by Denton Gentry
        {'name': 'scenario with nan', 'filename': path_to_nan, 'include': True},  # by Denton Gentry
    ]  # by Denton Gentry
    ca = customadoption.CustomAdoption(data_sources=data_sources,  # by Denton Gentry
                                       soln_adoption_custom_name='scenario with nan')  # by Denton Gentry
    avgs, _, _ = ca._avg_high_low()  # by Denton Gentry
    assert not pd.isna(avgs.loc[2030, 'World'])  # by Denton Gentry
    assert pd.isna(avgs.loc[2012, 'World'])  # by Denton Gentry
    assert pd.isna(avgs.loc[2030, 'OECD90'])  # by Denton Gentry
