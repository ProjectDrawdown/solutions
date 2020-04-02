import pathlib
import pytest
from model import customadoption
import pandas as pd
import numpy as np

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


def test_avg_high_low_with_limit():
    data_sources = [
        {'name': 'scenario 1', 'filename': path1, 'include': True},
        {'name': 'scenario 2', 'filename': path2, 'include': True},
    ]
    limit = pd.read_csv(datadir.joinpath('ca_limit_trr.csv'), index_col=0)
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='',
                                       low_sd_mult=1.0, high_sd_mult=1.5,
                                       total_adoption_limit=limit)
    high_scen = pd.read_csv(datadir.joinpath('ca_highx1p5_trr.csv'), index_col=0)
    _, highs, _ = ca._avg_high_low()
    pd.testing.assert_frame_equal(highs.loc[:2026, :], high_scen.loc[:2026, :],
                                  check_exact=False, check_dtype=False)
    pd.testing.assert_frame_equal(highs.loc[2027:, :], limit.loc[2027:, :], check_dtype=False)


def test_avg_high_low_with_limit_per_source():
    data_sources = [
        {'name': 'scenario 1', 'filename': datadir.joinpath('ca_100.csv'), 'include': True},
        {'name': 'scenario 2', 'filename': datadir.joinpath('ca_300.csv'), 'include': True},
    ]
    limit = pd.read_csv(datadir.joinpath('ca_200.csv'), index_col=0)
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='',
                                       low_sd_mult=0.1, high_sd_mult=0.1,
                                       total_adoption_limit=limit)
    avg, high, low = ca._avg_high_low()
    # if the limit is not applied to each individual source before averaging, then the average
    # of 100.0 and 300.0 will be 200.0. Applying a limit of 200.0 to the computed average will
    # not change anything.
    # After applying the limit of 200.0 to ca_300.csv, the average of 100.0 and 200.0
    # will be 150.0.
    assert((avg == 150.0).all().all())
    assert((high == 155.0).all().all())
    assert((low == 145.0).all().all())


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


def test_adoption_data_with_NaN():
    path_to_nan = str(datadir.joinpath('ca_scenario_with_NaN.csv'))
    data_sources = [
        {'name': 'scenario with nan', 'filename': path_to_nan, 'include': True},
    ]
    ca = customadoption.CustomAdoption(data_sources=data_sources,
                                       soln_adoption_custom_name='scenario with nan')
    avgs, _, _ = ca._avg_high_low()
    assert not pd.isna(avgs.loc[2030, 'World'])
    assert pd.isna(avgs.loc[2012, 'World'])
    assert pd.isna(avgs.loc[2030, 'OECD90'])


def test_report():
    data_sources = []
    for i in range(1, 3):
        name = f'af_ca{i}'
        data_sources.append({'name': name, 'filename': datadir.joinpath(name + '.csv'), 'include': True})
    lims = pd.read_csv(datadir.joinpath('af_tla.csv'), index_col=0)
    ca = customadoption.CustomAdoption(data_sources=data_sources, soln_adoption_custom_name='',
                                       total_adoption_limit=lims)
    report, data = ca.report()
    print(report.iloc[1, :].values)
    assert list(report.iloc[0, :].values) == [True, True, True, False]
    assert list(report.iloc[1, :].values) == [False, False, np.nan, np.nan]


def test_datapoints_limit():
    # Datapoints from Tropical Tree Staples.
    adoption_2014 = 25.42446198181150
    tla_lim = 169.373472124130
    datapoints = pd.DataFrame([
        [2014, adoption_2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2030, 0.7 * tla_lim, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2050, 1.0 * tla_lim, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America", "China", "India",
                 "EU", "USA"]).set_index("Year")
    data_sources = [{'name': 'datapoints scenario', 'datapoints': datapoints, 'include': True}]
    limit = pd.DataFrame(tla_lim, index=range(2012, 2061), columns=datapoints.columns)
    ca = customadoption.CustomAdoption(data_sources=data_sources,
            soln_adoption_custom_name='datapoints scenario', total_adoption_limit=limit)
    # Tropical Tree Staples "Custom PDS Adoption"!A294:K343
    expected_list = [
        ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
            "Middle East and Africa", "Latin America", "China", "India",
            "EU", "USA"],
        [2012, 13.78234091867670, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2013, 19.60340145024380, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2014, 25.42446198181100, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2015, 31.24552251337990, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2016, 37.06658304494700, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2017, 42.88764357651420, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2018, 48.70870410808130, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2019, 54.52976463964840, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2020, 60.35082517121740, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2021, 66.17188570278450, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2022, 71.99294623435160, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2023, 77.81400676591870, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2024, 83.63506729748590, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2025, 89.45612782905480, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2026, 95.27718836062190, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2027, 101.0982488921890, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2028, 106.9193094237560, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2029, 112.7403699553230, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2030, 118.5614304868900, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2031, 121.1020325687530, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2032, 123.6426346506150, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2033, 126.1832367324770, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2034, 128.7238388143390, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2035, 131.2644408962010, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2036, 133.8050429780620, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2037, 136.3456450599250, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2038, 138.8862471417870, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2039, 141.4268492236490, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2040, 143.9674513055110, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2041, 146.5080533873720, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2042, 149.0486554692340, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2043, 151.5892575510960, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2044, 154.1298596329580, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2045, 156.6704617148210, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2046, 159.2110637966830, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2047, 161.7516658785440, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2048, 164.2922679604060, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2049, 166.8328700422680, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2050, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2051, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2052, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2053, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2054, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2055, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2056, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2057, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2058, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2059, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2060, 169.3734721241300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    expected = pd.DataFrame(expected_list[1:], columns=expected_list[0],
            dtype='float').set_index("Year")
    expected.index = expected.index.astype(int)
    expected.index.name = 'Year'
    result = ca.scenarios['datapoints scenario']['df']
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_datapoints_nolimit():
    datapoints = pd.DataFrame([
        [2020, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2050, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America"]).set_index("Year")
    data_sources = [{'name': 'datapoints scenario', 'datapoints': datapoints, 'include': True}]
    ca = customadoption.CustomAdoption(data_sources=data_sources,
            soln_adoption_custom_name='datapoints scenario')
    result = ca.scenarios['datapoints scenario']['df']
    assert result.loc[2040, 'World'] == pytest.approx(40)
    assert result.loc[2050, 'World'] == pytest.approx(50)
    assert result.loc[2060, 'World'] == pytest.approx(60)


def test_datapoints_no_negative():
    datapoints = pd.DataFrame([
        [2020, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2021, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                 "Middle East and Africa", "Latin America"]).set_index("Year")
    data_sources = [{'name': 'datapoints scenario', 'datapoints': datapoints, 'include': True}]
    ca = customadoption.CustomAdoption(data_sources=data_sources,
            soln_adoption_custom_name='datapoints scenario')
    result = ca.scenarios['datapoints scenario']['df']
    assert result.loc[2015, 'World'] == pytest.approx(0.0)  # i.e. not negative.


def test_growth():
    growth_initial = pd.DataFrame([[2018, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 0.0, 0.0, 0.0, 0.0]],
        columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                 'Middle East and Africa', 'Latin America',
                 'USA', 'EU', 'India', 'China']).set_index('Year')
    data_sources = [{'name': 'growth scenario', 'growth_rate': 0.1,
            'growth_initial': growth_initial, 'include': True}]
    ca = customadoption.CustomAdoption(data_sources=data_sources,
            soln_adoption_custom_name='growth scenario')
    result = ca.scenarios['growth scenario']['df']
    # expected values generated by modifying an Excel Custom PDS Adoption scenario to have a
    # 10% growth rate and initial values in the dataframe above. As Excel only handles the
    # World region for growth computations, we iteratively set the World to each value above.
    assert result.loc[2012, 'World'] == 1.0
    assert result.loc[2015, 'World'] == 1.0
    assert result.loc[2018, 'World'] == 1.0
    assert result.loc[2030, 'World'] == pytest.approx(12.2172551998265)
    assert result.loc[2040, 'World'] == pytest.approx(21.5649678663485)
    assert result.loc[2050, 'World'] == pytest.approx(30.9126805328706)
    assert result.loc[2060, 'World'] == pytest.approx(40.2603931993926)
    assert result.loc[2060, 'OECD90'] == pytest.approx(80.5207863987853)
    assert result.loc[2060, 'Eastern Europe'] == pytest.approx(120.781179598178)
    assert result.loc[2060, 'Asia (Sans Japan)'] == pytest.approx(161.041572797571)
    assert result.loc[2060, 'Middle East and Africa'] == pytest.approx(201.301965996963)
    assert result.loc[2060, 'Latin America'] == pytest.approx(241.562359196356)


def test_datapoints_with_implied_main_region():
    datapoints = pd.DataFrame([
        [2020, np.nan, 10.0, 10.0, 10.0, 10.0, 10.0, 1.0, 3.0, 5.0, 7.0],
        [2050, np.nan, 10.0, 10.0, 10.0, 10.0, 10.0, 1.0, 3.0, 5.0, 7.0]],
        columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                 'Middle East and Africa', 'Latin America',
                 'USA', 'EU', 'India', 'China']).set_index('Year')
    data_sources = [{'name': 'implied world', 'datapoints': datapoints, 'include': True}]
    ca = customadoption.CustomAdoption(data_sources=data_sources,
            soln_adoption_custom_name='implied world')
    result = ca.scenarios['implied world']['df']
    assert result.loc[2025, 'World'] == 50.0
    assert result.loc[2035, 'World'] == 50.0

def test_start_year_in_range():
    datapoints = pd.DataFrame([
        [1990, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2010, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2020, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2030, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2040, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2060, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [2070, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                 'Middle East and Africa', 'Latin America',
                 'USA', 'EU', 'India', 'China']).set_index('Year')
    data_sources = [{'name': 'implied world', 'datapoints': datapoints, 'include': True}]
    ca = customadoption.CustomAdoption(data_sources=data_sources,
            soln_adoption_custom_name='implied world')
    result = ca.scenarios['implied world']['df']
    assert result.first_valid_index() == 2012
    assert result.last_valid_index() == 2060
