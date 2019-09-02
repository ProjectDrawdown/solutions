"""Tests for unitadoption.py."""

import pathlib
import numpy as np
import pandas as pd
import pytest
from unittest import mock
from model import advanced_controls
from model import unitadoption
from model.advanced_controls import SOLUTION_CATEGORY


this_dir = pathlib.Path(__file__)
ref_tam_per_region_filename = this_dir.parents[0].joinpath('data', 'ref_tam_per_region.csv')
pds_tam_per_region_filename = this_dir.parents[0].joinpath('data', 'pds_tam_per_region.csv')
ref_tam_per_region = pd.read_csv(ref_tam_per_region_filename, header=0, index_col=0,
                                 skipinitialspace=True, comment='#')
pds_tam_per_region = pd.read_csv(pds_tam_per_region_filename, header=0, index_col=0,
                                 skipinitialspace=True, comment='#')


def test_ref_population():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    population = ua.ref_population()
    assert population['World'][2014] == pytest.approx(7249.180596)
    assert population['Middle East and Africa'][2031] == pytest.approx(2093.543821)
    assert population['USA'][2060] == pytest.approx(465.280628)


def test_ref_gdp():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    gdp = ua.ref_gdp()
    assert gdp['World'][2014] == pytest.approx(58307.866135)
    assert gdp['Latin America'][2030] == pytest.approx(8390.982338)
    assert gdp['USA'][2060] == pytest.approx(36982.727199)


def test_ref_gdp_per_capita():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    gpc = ua.ref_gdp_per_capita()
    assert gpc['World'][2060] == pytest.approx(21.67246)
    assert gpc['Asia (Sans Japan)'][2029] == pytest.approx(6.51399)
    assert gpc['USA'][2014] == pytest.approx(43.77208)


def test_ref_tam_per_capita():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    tpc = ua.ref_tam_per_capita()
    assert tpc['World'][2016] == pytest.approx(3.38350004047)
    assert tpc['Latin America'][2029] == pytest.approx(3.62748818668)
    assert tpc['USA'][2059] == pytest.approx(12.21081396314)


def test_ref_tam_per_gdp_per_capita():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    tpgpc = ua.ref_tam_per_gdp_per_capita()
    assert tpgpc['OECD90'][2014] == pytest.approx(256.68795471511)
    assert tpgpc['China'][2033] == pytest.approx(743.15450999975)
    assert tpgpc['EU'][2060] == pytest.approx(85.95558928452)


def test_ref_tam_growth():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    tg = ua.ref_tam_growth()
    assert tg['Eastern Europe'][2015] == pytest.approx(24.26693428425)
    assert tg['India'][2037] == pytest.approx(171.36849827619)
    assert tg['EU'][2060] == pytest.approx(71.14797759969)
    assert tg['World'][2014] == ''


def test_pds_population():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    population = ua.pds_population()
    assert population['World'][2016] == pytest.approx(7415.5738320)
    assert population['India'][2031] == pytest.approx(1539.9070540)
    assert population['USA'][2060] == pytest.approx(403.5036840)


def test_pds_gdp():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    gdp = ua.pds_gdp()
    assert gdp['Eastern Europe'][2014] == pytest.approx(2621.864076293940)
    assert gdp['Latin America'][2030] == pytest.approx(8058.323682075440)
    assert gdp['USA'][2060] == pytest.approx(32072.400550257600)


def test_pds_gdp_per_capita():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    gpc = ua.pds_gdp_per_capita()
    assert gpc['World'][2060] == pytest.approx(21.703844951868)
    assert gpc['Asia (Sans Japan)'][2029] == pytest.approx(6.52868)
    assert gpc['USA'][2014] == pytest.approx(44.49768)


def test_pds_tam_per_capita():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=pds_tam_per_region,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    tpc = ua.pds_tam_per_capita()
    assert tpc['World'][2015] == pytest.approx(3.357451)
    assert tpc['India'][2039] == pytest.approx(2.945601)
    assert tpc['USA'][2058] == pytest.approx(13.978179)


def test_pds_tam_per_gdp_per_capita():
    # we pass pds_total_adoption_units=ref_tam_per_region for convenience,
    # the test is just checking the results of the calculation.
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=ref_tam_per_region,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    tpgpc = ua.pds_tam_per_gdp_per_capita()
    assert tpgpc['OECD90'][2015] == pytest.approx(247.759624)
    assert tpgpc['China'][2032] == pytest.approx(759.164408)
    assert tpgpc['EU'][2060] == pytest.approx(85.955589)


def test_pds_tam_growth():
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=ref_tam_per_region,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=None)
    tg = ua.pds_tam_growth()
    assert tg['Eastern Europe'][2015] == pytest.approx(24.266934)
    assert tg['India'][2033] == pytest.approx(159.378951)
    assert tg['USA'][2060] == pytest.approx(33.502722)
    assert tg['OECD90'][2014] == ''


def test_cumulative_degraded_land_unprotected():
    ac = advanced_controls.AdvancedControls(degradation_rate=0.003074, delay_protection_1yr=True, disturbance_rate=1)
    tla_per_reg = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_tla_per_reg.csv'), index_col=0)
    units_adopted = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_units_adopted.csv'),
                                index_col=0)
    ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=None, soln_pds_funits_adopted=units_adopted,
                                   pds_total_adoption_units=tla_per_reg)
    expected_world = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_pds_deg_unprotected_land.csv'), index_col=0)
    pd.testing.assert_frame_equal(ua._cumulative_degraded_land('PDS', 'unprotected').loc[:, ['World']], expected_world)


def test_cumulative_degraded_land_protected():
    ac = advanced_controls.AdvancedControls(
        disturbance_rate=0.0000157962432447763, delay_protection_1yr=True,degradation_rate=1)
    units_adopted = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_units_adopted.csv'), index_col=0)
    ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=None, soln_pds_funits_adopted=units_adopted)
    expected_world = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_pds_deg_protected_land.csv'), index_col=0)
    pd.testing.assert_frame_equal(ua._cumulative_degraded_land('PDS', 'protected').loc[:, ['World']], expected_world)


def test_total_undegraded_land():
    ac = advanced_controls.AdvancedControls(degradation_rate=0.003074, disturbance_rate=0.0000157962432447763,
                                            delay_protection_1yr=True)
    tla_per_reg = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_tla_per_reg.csv'), index_col=0)
    units_adopted = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_units_adopted.csv'), index_col=0)
    ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=None, soln_pds_funits_adopted=units_adopted,
                                   pds_total_adoption_units=tla_per_reg)
    expected_world = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_total_undegraded_land.csv'), index_col=0)
    # identical for REF and PDS so just test PDS
    pd.testing.assert_frame_equal(ua.pds_total_undegraded_land().loc[:, ['World']], expected_world)


def test_annual_reduction_in_total_degraded_land():
    cumu_ridl = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_cumu_ridl.csv'), index_col=0)
    expected_world = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_annu_ridl.csv'), index_col=0)
    with mock.patch.object(unitadoption.UnitAdoption, 'cumulative_reduction_in_total_degraded_land',
                           new=lambda x: cumu_ridl):
        ua = unitadoption.UnitAdoption(ac=advanced_controls.AdvancedControls(solution_category=SOLUTION_CATEGORY.LAND),
                                       soln_ref_funits_adopted=None, soln_pds_funits_adopted=None)
        pd.testing.assert_frame_equal(ua.annual_reduction_in_total_degraded_land().loc[:, ['World']], expected_world)


def test_soln_pds_cumulative_funits_bug_behavior():
    funits = [
        ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
         'China', 'India', 'EU', 'USA'],
        [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
        [2015, 176.24, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [2016, 272.03, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [2017, 383.31, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted, soln_ref_funits_adopted=None,
                                   bug_cfunits_double_count=True)
    result = ua.soln_pds_cumulative_funits()
    v = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
          'China', 'India', 'EU', 'USA'],
         [2014, 112.63, 150.0, 0.66, 42.14, 3.16, 29.30, 29.94, 5.50, 110.54, 26.24],
         [2015, 288.87, 151.0, 1.66, 43.14, 4.16, 30.30, 30.94, 6.50, 111.54, 27.24],
         [2016, 560.90, 152.0, 2.66, 44.14, 5.16, 31.30, 31.94, 7.50, 112.54, 28.24],
         [2017, 944.21, 153.0, 3.66, 45.14, 6.16, 32.30, 32.94, 8.50, 113.54, 29.24]]
    expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
    expected.name = "soln_pds_cumulative_funits"
    pd.testing.assert_frame_equal(result.iloc[0:5], expected, check_exact=False)

    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted, soln_ref_funits_adopted=None,

                                   bug_cfunits_double_count=False)
    result = ua.soln_pds_cumulative_funits()
    v = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
          'China', 'India', 'EU', 'USA'],
         [2014, 112.63, 75.0, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
         [2015, 288.87, 76.0, 1.33, 22.07, 2.58, 15.65, 15.97, 3.75, 56.27, 14.12],
         [2016, 560.90, 77.0, 2.33, 23.07, 3.58, 16.65, 16.97, 4.75, 57.27, 15.12],
         [2017, 944.21, 78.0, 3.33, 24.07, 4.58, 17.65, 17.97, 5.75, 58.27, 16.12]]
    expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
    expected.name = "soln_pds_cumulative_funits"
    pd.testing.assert_frame_equal(result.iloc[0:5], expected, check_exact=False)


def test_soln_pds_cumulative_funits_missing_data():
    funits = [
        ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
         'China', 'India', 'EU', 'USA'],
        [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
        [2015, 176.24, 1.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        [2016, 272.03, np.nan, 1.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        [2017, 383.31, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]]
    soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted, soln_ref_funits_adopted=None,

                                   bug_cfunits_double_count=True)
    result = ua.soln_pds_cumulative_funits()
    v = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
          'China', 'India', 'EU', 'USA'],
         [2014, 112.63, 150.00, 0.66, 42.14, 3.16, 29.30, 29.94, 5.50, 110.54, 26.24],
         [2015, 288.87, 151.00, 0.66, 42.14, 3.16, 29.30, 29.94, 5.50, 110.54, 26.24],
         [2016, 560.90, 151.00, 1.66, 42.14, 3.16, 29.30, 29.94, 5.50, 110.54, 26.24],
         [2017, 944.21, 151.00, 1.66, 42.14, 3.16, 29.30, 29.94, 5.50, 110.54, 26.24]]
    expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
    expected.name = "soln_pds_cumulative_funits"
    pd.testing.assert_frame_equal(result.iloc[0:5], expected, check_exact=False)


def test_soln_ref_cumulative_funits():
    funits = [
        ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
         'China', 'India', 'EU', 'USA'],
        [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
        [2015, 117.07, 75.63, 0.34, 22.16, 1.71, 15.42, 15.43, 3.07, 55.76, 13.22],
        [2016, 121.51, 76.25, 0.34, 23.25, 1.85, 16.18, 15.89, 3.39, 56.25, 13.31],
        [2017, 125.95, 76.87, 0.35, 24.33, 1.98, 16.95, 16.35, 3.71, 56.73, 13.40]]
    soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_ref_cumulative_funits()
    v = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
          'China', 'India', 'EU', 'USA'],
         [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
         [2015, 229.70, 150.63, 0.67, 43.23, 3.29, 30.07, 30.41, 5.82, 111.03, 26.34],
         [2016, 351.21, 226.88, 1.01, 66.48, 5.13, 46.25, 46.30, 9.21, 167.28, 39.65],
         [2017, 477.16, 303.75, 1.36, 90.81, 7.11, 63.20, 62.65, 12.92, 224.01, 53.05]]
    expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
    expected.name = "soln_ref_cumulative_funits"
    pd.testing.assert_frame_equal(result.iloc[0:5], expected, check_exact=False,
                                  check_less_precise=2)


def test_soln_ref_cumulative_funits_with_NaN():
    funits = [
        ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
         'China', 'India', 'EU', 'USA'],
        [2014, 112.63, 75.00, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        [2015, 117.07, 75.63, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        [2016, 121.51, 76.25, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        [2017, 125.95, 76.87, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]]
    soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_ref_cumulative_funits()
    v = [['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
          'China', 'India', 'EU', 'USA'],
         [2014, 112.63, 75.00, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
         [2015, 229.70, 150.63, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
         [2016, 351.21, 226.88, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
         [2017, 477.16, 303.75, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    expected = pd.DataFrame(v[1:], columns=v[0]).set_index('Year')
    expected.name = "soln_ref_cumulative_funits"
    pd.testing.assert_frame_equal(result.iloc[0:5], expected, check_exact=False,
                                  check_less_precise=2)


def test_soln_net_annual_funits_adopted():
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 112.63, 75.00, 0.33],
              [2015, 117.07, 75.63, 0.34], [2016, 121.51, 76.25, 0.34]]
    soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 112.63, 75.00, 0.33],
              [2015, 176.24, 0.0, 0.0], [2016, 272.03, 0.0, 0.0]]
    soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_net_annual_funits_adopted()
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 0.0, 0.0, 0.0],
              [2015, 59.17, -75.63, -0.34], [2016, 150.52, -76.25, -0.34]]
    expected = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    expected.name = "soln_net_annual_funits_adopted"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_net_annual_funits_adopted_with_NaN():
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 112.63, 75.00, 0.33],
              [2015, 117.07, 75.63, 0.34], [2016, 121.51, 76.25, 0.34]]
    soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 112.63, 75.00, 0.33],
              [2015, 176.24, np.nan, np.nan], [2016, 272.03, np.nan, np.nan]]
    soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ua = unitadoption.UnitAdoption(ac=None,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_net_annual_funits_adopted()
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 0.0, 0.0, 0.0],
              [2015, 59.17, np.nan, np.nan], [2016, 150.52, np.nan, np.nan]]
    expected = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    expected.name = "soln_net_annual_funits_adopted"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_net_annual_funits_adopted_land():
    """ Using data from Silvopasture """
    sp_world = [0, 0, 0, 1.496434895, 4.926272512, 8.334043824, 11.71939477, 15.08199659, 18.42154804, 21.7377775,

                25.03044494, 28.2993437, 30.91186053, 34.15769987, 37.38144769, 40.58301746, 43.762352, 46.91942388,

                50.05423562, 53.16681962, 56.25723801, 59.32558217, 62.28412644, 65.31390912, 68.32225856, 71.30936481,

                74.27544198, 77.22072697, 80.14547809, 83.0499736, 85.93451014, 88.79940118, 91.376051, 94.23271025,

                97.07117348, 99.89175284, 102.6947702, 105.5903814, 108.3342353, 111.0613919, 113.7722351, 116.4671514,

                119.146528, 121.8107521, 124.4602097, 127.0952848, 129.7163586]
    f = this_dir.parents[0].joinpath('data', 'ad_sp_pds.csv')
    pds_ad = pd.read_csv(f, index_col=0)
    f = this_dir.parents[0].joinpath('data', 'ad_sp_ref.csv')
    ref_ad = pd.read_csv(f, index_col=0)
    ac = advanced_controls.AdvancedControls(soln_expected_lifetime=30)
    ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=ref_ad,
                                   soln_pds_funits_adopted=pds_ad)
    result = ua.soln_net_annual_funits_adopted()['World'].values
    # We only check world values because regional calcs have bugs and are unused in the xls
    np.testing.assert_array_almost_equal(result, sp_world)


def test_soln_net_annual_funits_adopted_cache():
    # soln_net_annual_funits_adopted is used in a number of places, check that it is not
    # being inadvertantly modified.
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 112.63, 75.00, 0.33],
              [2015, 117.07, 75.63, 0.34], [2016, 121.51, 76.25, 0.34]]
    soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'], [2014, 112.63, 75.00, 0.33],
              [2015, 176.24, 0.0, 0.0], [2016, 272.03, 0.0, 0.0]]
    soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ac = advanced_controls.AdvancedControls(
        conv_lifetime_capacity=182411.28, conv_avg_annual_use=4946.84,
        soln_lifetime_capacity=48343.80, soln_avg_annual_use=1841.67)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    original = ua.soln_net_annual_funits_adopted().copy(deep=True)
    _ = ua.conv_ref_annual_tot_iunits()
    _ = ua.soln_pds_net_grid_electricity_units_saved()
    _ = ua.soln_pds_net_grid_electricity_units_used()
    _ = ua.soln_pds_fuel_units_avoided()
    _ = ua.soln_pds_direct_co2_emissions_saved()
    _ = ua.soln_pds_direct_ch4_co2_emissions_saved()
    _ = ua.soln_pds_direct_n2o_co2_emissions_saved()
    final = ua.soln_net_annual_funits_adopted()
    pd.testing.assert_frame_equal(original, final, check_exact=True)


def test_conv_ref_tot_iunits():
    ac = advanced_controls.AdvancedControls(conv_avg_annual_use=4946.840187342)
    funits = [
        ['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',

         'China', 'India', 'EU', 'USA'],
        [2014, 112.63, 75.00, 0.33, 21.07, 1.58, 14.65, 14.97, 2.75, 55.27, 13.12],
        [2015, 117.07, 75.63, 0.34, 22.16, 1.71, 15.42, 15.43, 3.07, 55.76, 13.22],
        [2016, 121.51, 76.25, 0.34, 23.25, 1.85, 16.18, 15.89, 3.39, 56.25, 13.31]]
    soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.conv_ref_tot_iunits()
    funits = [['Year', 'World', 'OECD90', 'Eastern Europe'],
              [2014, 4.53535289538, 1.93172544646, 0.40864109200],
              [2015, 4.87963781659, 1.94274331751, 0.41354556337],
              [2016, 5.05302431141, 1.95081104871, 0.41846626996]]
    expected = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    expected.name = "conv_ref_tot_iunits"
    pd.testing.assert_frame_equal(result.iloc[0:3, 0:3], expected, check_exact=False)


def test_conv_ref_tot_iunits_land():
    f = this_dir.parents[0].joinpath('data', 'sp_tla.csv')
    sp_tla = pd.read_csv(f, index_col=0)
    f = this_dir.parents[0].joinpath('data', 'ad_sp_ref.csv')
    ref_ad = pd.read_csv(f, index_col=0)
    ua = unitadoption.UnitAdoption(ac=advanced_controls.AdvancedControls(solution_category=SOLUTION_CATEGORY.LAND),
                                   pds_total_adoption_units=sp_tla, soln_ref_funits_adopted=ref_ad,
                                   soln_pds_funits_adopted=None)
    # test only world values as regional data has bugs in xls
    result = ua.conv_ref_tot_iunits()['World'].values
    world_expected = np.array([619.83739797667] * 47)
    np.testing.assert_array_almost_equal(result, world_expected)


def test_conv_ref_annual_tot_iunits():
    ac = advanced_controls.AdvancedControls(conv_avg_annual_use=4946.840187342)
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.conv_ref_annual_tot_iunits()
    expected = pd.DataFrame(conv_ref_annual_tot_iunits_list[1:],
                            columns=conv_ref_annual_tot_iunits_list[0]).set_index('Year')
    expected.name = "conv_ref_annual_tot_iunits"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_net_grid_electricity_units_used():
    ac = advanced_controls.AdvancedControls(soln_annual_energy_used=0,
                                            conv_annual_energy_used=1)
    soln_pds_funits_adopted = pd.DataFrame([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
    soln_ref_funits_adopted = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_net_grid_electricity_units_used()
    expected = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    expected.name = "soln_pds_net_grid_electricity_units_used"
    pd.testing.assert_frame_equal(result, expected)

    ac = advanced_controls.AdvancedControls(soln_annual_energy_used=4,
                                            conv_annual_energy_used=1)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    expected = pd.DataFrame([[3.0, 6.0, 9.0, 12.0], [15.0, 18.0, 21.0, 24.0]])
    expected.name = "soln_pds_net_grid_electricity_units_used"
    result = ua.soln_pds_net_grid_electricity_units_used()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)

    ac = advanced_controls.AdvancedControls(soln_annual_energy_used=4,
                                            conv_annual_energy_used=1)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted,
                                   electricity_unit_factor=10.0)
    expected = pd.DataFrame([[30.0, 60.0, 90.0, 120.0], [150.0, 180.0, 210.0, 240.0]])
    expected.name = "soln_pds_net_grid_electricity_units_used"
    result = ua.soln_pds_net_grid_electricity_units_used()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_net_grid_electricity_units_saved():
    soln_pds_funits_adopted = pd.DataFrame([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
    soln_ref_funits_adopted = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    ac = advanced_controls.AdvancedControls(soln_energy_efficiency_factor=0,
                                            conv_annual_energy_used=0)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_net_grid_electricity_units_saved()
    expected = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    expected.name = "soln_pds_net_grid_electricity_units_saved"
    pd.testing.assert_frame_equal(result, expected)

    ac = advanced_controls.AdvancedControls(soln_energy_efficiency_factor=2,
                                            conv_annual_energy_used=3)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    expected = pd.DataFrame([[6.0, 12.0, 18.0, 24.0], [30.0, 36.0, 42.0, 48.0]])
    expected.name = "soln_pds_net_grid_electricity_units_saved"
    result = ua.soln_pds_net_grid_electricity_units_saved()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)

    ac = advanced_controls.AdvancedControls(soln_energy_efficiency_factor=2,
                                            conv_annual_energy_used=3)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted,
                                   electricity_unit_factor=10.0)
    expected = pd.DataFrame([[60.0, 120.0, 180.0, 240.0], [300.0, 360.0, 420.0, 480.0]])
    expected.name = "soln_pds_net_grid_electricity_units_saved"
    result = ua.soln_pds_net_grid_electricity_units_saved()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_fuel_units_avoided():
    ac = advanced_controls.AdvancedControls(conv_fuel_consumed_per_funit=0,
                                            soln_fuel_efficiency_factor=1)
    soln_pds_funits_adopted = pd.DataFrame([[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]])
    soln_ref_funits_adopted = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_ref_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_fuel_units_avoided()
    expected = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    expected.name = "soln_pds_fuel_units_avoided"
    pd.testing.assert_frame_equal(result, expected)

    ac = advanced_controls.AdvancedControls(conv_fuel_consumed_per_funit=2,
                                            soln_fuel_efficiency_factor=2)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_fuel_units_avoided()
    expected = pd.DataFrame([[4.0, 8.0, 12.0, 16.0], [4.0, 8.0, 12.0, 16.0]])
    expected.name = "soln_pds_fuel_units_avoided"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_direct_co2_emissions_saved():
    ac = advanced_controls.AdvancedControls(conv_emissions_per_funit=7,
                                            soln_emissions_per_funit=5)
    soln_pds_funits_adopted = pd.DataFrame([[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]])
    soln_ref_funits_adopted = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_direct_co2_emissions_saved()
    expected = pd.DataFrame([[2.0, 4.0, 6.0, 8.0], [2.0, 4.0, 6.0, 8.0]])
    expected.name = "soln_pds_direct_co2_emissions_saved"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_direct_ch4_emissions_saved():
    ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback',
                                            ch4_is_co2eq=False, ch4_co2_per_funit=2.0)
    soln_pds_funits_adopted = pd.DataFrame([[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]])
    soln_ref_funits_adopted = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_direct_ch4_co2_emissions_saved()
    expected = pd.DataFrame([[68.0, 136.0, 204.0, 272.0], [68.0, 136.0, 204.0, 272.0]])
    expected.name = "soln_pds_direct_ch4_co2_emissions_saved"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)

    ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback',
                                            ch4_is_co2eq=True, ch4_co2_per_funit=2.0)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_direct_ch4_co2_emissions_saved()
    expected = pd.DataFrame([[2.0, 4.0, 6.0, 8.0], [2.0, 4.0, 6.0, 8.0]])
    expected.name = "soln_pds_direct_ch4_co2_emissions_saved"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_direct_n2o_emissions_saved():
    ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback',
                                            n2o_is_co2eq=False, n2o_co2_per_funit=2.0)
    soln_pds_funits_adopted = pd.DataFrame([[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]])
    soln_ref_funits_adopted = pd.DataFrame([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_direct_n2o_co2_emissions_saved()
    expected = pd.DataFrame([[596.0, 1192.0, 1788.0, 2384.0], [596.0, 1192.0, 1788.0, 2384.0]])
    expected.name = "soln_pds_direct_n2o_co2_emissions_saved"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)

    ac = advanced_controls.AdvancedControls(co2eq_conversion_source='AR5 with feedback',
                                            n2o_is_co2eq=True, n2o_co2_per_funit=2.0)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_direct_n2o_co2_emissions_saved()
    expected = pd.DataFrame([[2.0, 4.0, 6.0, 8.0], [2.0, 4.0, 6.0, 8.0]])
    expected.name = "soln_pds_direct_n2o_co2_emissions_saved"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_tot_iunits_reqd():
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_avg_annual_use=1841.66857142857)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=None)
    result = ua.soln_pds_tot_iunits_reqd()
    expected = pd.DataFrame(soln_pds_tot_iunits_reqd_list[1:],
                            columns=soln_pds_tot_iunits_reqd_list[0]).set_index('Year')
    expected.name = "soln_pds_tot_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_new_iunits_reqd():
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=48343.8,
                                            soln_avg_annual_use=1841.66857142857)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=None)
    result = ua.soln_pds_new_iunits_reqd()
    expected = pd.DataFrame(soln_pds_new_iunits_reqd_list[1:],
                            columns=soln_pds_new_iunits_reqd_list[0]).set_index('Year')
    expected.name = "soln_pds_new_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_new_iunits_reqd_multiple_replacements():
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=20000.0,
                                            soln_avg_annual_use=5000.0)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=None)
    result = ua.soln_pds_new_iunits_reqd()
    # values from SolarPVUtil setting 'Unit Adoption Calculations'
    # AH127 = 20000 and AH128 = 5000 to match advanced_controls above
    assert result.loc[2015, 'World'] == pytest.approx(0.01272157755)
    assert result.loc[2035, 'World'] == pytest.approx(0.15275428774)
    assert result.loc[2060, 'World'] == pytest.approx(0.37217842574)


def test_soln_pds_new_iunits_reqd_repeated_cost_for_iunits():
    soln_pds_funits_adopted = pd.DataFrame(soln_funits_adopted_altcement_list[1:],
                                           columns=soln_funits_adopted_altcement_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=30.0, soln_avg_annual_use=1.0)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted, soln_ref_funits_adopted=None,

                                   repeated_cost_for_iunits=True)
    result = ua.soln_pds_new_iunits_reqd()
    expected = pd.DataFrame(soln_new_iunits_reqd_altcement_list[1:],
                            columns=soln_new_iunits_reqd_altcement_list[0]).set_index('Year')
    expected.name = "soln_pds_new_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_new_iunits_reqd_with_zero_funits_sometimes():
    funits_adopted = pd.DataFrame(soln_pds_funits_adopted_leds_commercial_list[1:],
                                  columns=soln_pds_funits_adopted_leds_commercial_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=50000.0,
                                            soln_avg_annual_use=3635.85)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=funits_adopted,
                                   soln_ref_funits_adopted=None)
    result = ua.soln_pds_new_iunits_reqd()
    expected = pd.DataFrame(soln_pds_new_iunits_reqd_leds_commercial_list[1:],
                            columns=soln_pds_new_iunits_reqd_leds_commercial_list[0]).set_index(
        'Year')
    expected.name = "soln_pds_new_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None,
                                   soln_ref_funits_adopted=funits_adopted)
    result = ua.soln_ref_new_iunits_reqd()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_new_iunits_reqd_rounding_bug():
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_onshorewind_list[1:],
                                           columns=soln_pds_funits_adopted_onshorewind_list[0]).set_index(
        'Year')
    zero_funits_adopted = pd.DataFrame(0, index=soln_pds_funits_adopted.index.copy(),
                                       columns=soln_pds_funits_adopted.columns.copy())
    ac = advanced_controls.AdvancedControls(
        soln_lifetime_capacity=63998.595, soln_avg_annual_use=2844.382,
        conv_lifetime_capacity=63998.595, conv_avg_annual_use=2844.382)
    expected = pd.DataFrame(soln_pds_new_iunits_reqd_onshorewind_list[1:],
                            columns=soln_pds_new_iunits_reqd_onshorewind_list[0]).set_index('Year')
    expected.name = "soln_pds_new_iunits_reqd"
    # 63998.595/2844.382 = 22.5 which cannot be represented by a floating point number
    # and will instead be 22.4999. Python's round() will return 22. Excel handles
    # this differently to return the 23 that humans expect.
    # This test case will fail if *_new_iunits_reqd() uses the basic Python round().
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_pds_funits_adopted)
    result = ua.soln_pds_new_iunits_reqd()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)
    result = ua.soln_ref_new_iunits_reqd()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=zero_funits_adopted)
    result = ua.conv_ref_new_iunits()
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_new_iunits_reqd_land():
    """ Using data from Silvopasture """
    sp_world = [0, 0, 1.49643489480934, 3.42983761673287, 3.40777131208006, 3.3853509490275, 3.36260182010352,

                3.3395514466838, 3.31622945888586, 3.29266744308518, 3.26889875807274, 2.61251683499262,
                3.24583933270031, 3.22374782069915, 3.20156976815986, 3.17933454067742, 3.15707188573589,

                3.13481173478948, 3.1125840024759, 3.09041838609068, 3.06834416845413, 2.95854426200356,
                3.02978268035292, 3.00834944629167, 2.98710624970022, 2.96607716645508, 2.94528498898256,

                2.92475112400388, 2.90449550819716, 2.88453654207888, 2.86489104204179, 2.57664981813053,

                2.85665924514041, 4.33489812403127, 6.25041698217706, 6.2107886876006, 6.28096212022842,
                6.10645576424633, 6.06670797541483, 6.02707271316069, 5.98758372231941, 5.94827534797025,

                5.27674091268659, 5.89529695122053, 5.8588229736597, 5.8226435345909]
    f = this_dir.parents[0].joinpath('data', 'ad_sp_pds.csv')
    sp_ad = pd.read_csv(f, index_col=0)
    ac = advanced_controls.AdvancedControls(soln_expected_lifetime=30)
    ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=None, soln_pds_funits_adopted=sp_ad)
    result = ua.soln_pds_new_iunits_reqd()['World'].values
    # We only check world values because regional calcs have bugs and are unused in the xls
    np.testing.assert_array_almost_equal(result, sp_world)


def test_soln_pds_big4_iunits_reqd():
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_avg_annual_use=1841.67)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_big4_iunits_reqd()
    expected = pd.DataFrame(soln_pds_big4_iunits_reqd_list[1:],
                            columns=soln_pds_big4_iunits_reqd_list[0]).set_index('Year')
    expected.name = "soln_pds_big4_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_pds_big4_iunits_reqd_with_NaN():
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_no_regional_data_list[1:],
                                           columns=soln_pds_funits_adopted_no_regional_data_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_avg_annual_use=1841.67)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_pds_big4_iunits_reqd()
    expected = pd.DataFrame(soln_pds_big4_iunits_reqd_no_regional_data_list[1:],
                            columns=soln_pds_big4_iunits_reqd_no_regional_data_list[0]).set_index(
        'Year')
    expected.name = "soln_pds_big4_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_ref_tot_iunits_reqd():
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_avg_annual_use=1841.66857142857)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_ref_tot_iunits_reqd()
    expected = pd.DataFrame(soln_ref_tot_iunits_reqd_list[1:],
                            columns=soln_ref_tot_iunits_reqd_list[0]).set_index('Year')
    expected.name = "soln_ref_tot_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_ref_new_iunits_reqd():
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=48343.8,
                                            soln_avg_annual_use=1841.66857142857)
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_ref_new_iunits_reqd()
    expected = pd.DataFrame(soln_ref_new_iunits_reqd_list[1:],
                            columns=soln_ref_new_iunits_reqd_list[0]).set_index('Year')
    expected.name = "soln_ref_new_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_soln_ref_new_iunits_reqd_multiple_replacements():
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=20000.0,
                                            soln_avg_annual_use=5000.0)
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.soln_ref_new_iunits_reqd()
    # values from SolarPVUtil setting 'Unit Adoption Calculations'
    # AH189 = 20000 and AH190 = 5000 to match advanced_controls above
    assert result.loc[2015, 'World'] == pytest.approx(0.00088767258)
    assert result.loc[2035, 'World'] == pytest.approx(0.00443836291)
    assert result.loc[2060, 'World'] == pytest.approx(0.00887672581)


def test_soln_ref_new_iunits_reqd_repeated_cost_for_iunits():
    soln_ref_funits_adopted = pd.DataFrame(soln_funits_adopted_altcement_list[1:],
                                           columns=soln_funits_adopted_altcement_list[0]).set_index(
        'Year')
    ac = advanced_controls.AdvancedControls(soln_lifetime_capacity=30.0, soln_avg_annual_use=1.0)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=None, soln_ref_funits_adopted=soln_ref_funits_adopted,

                                   repeated_cost_for_iunits=True)
    result = ua.soln_ref_new_iunits_reqd()
    expected = pd.DataFrame(soln_new_iunits_reqd_altcement_list[1:],
                            columns=soln_new_iunits_reqd_altcement_list[0]).set_index('Year')
    expected.name = "soln_ref_new_iunits_reqd"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_conv_ref_new_iunits():
    ac = advanced_controls.AdvancedControls(conv_lifetime_capacity=182411.28,
                                            conv_avg_annual_use=4946.84)
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.conv_ref_new_iunits()
    expected = pd.DataFrame(conv_ref_new_iunits_list[1:],
                            columns=conv_ref_new_iunits_list[0]).set_index('Year')
    expected.name = "conv_ref_new_iunits"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_conv_ref_new_iunits_multiple_replacements():
    ac = advanced_controls.AdvancedControls(conv_lifetime_capacity=20000.0,
                                            conv_avg_annual_use=5000.0)
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_list[1:],
                                           columns=soln_ref_funits_adopted_list[0]).set_index(
        'Year')
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_list[1:],
                                           columns=soln_pds_funits_adopted_list[0]).set_index(
        'Year')
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.conv_ref_new_iunits()
    # values from SolarPVUtil setting 'Unit Adoption Calculations'
    # AH252 = 4.0 and 'Advanced Controls'!F95 = 5000.0
    assert result.loc[2015, 'World'] == pytest.approx(0.01183390497)
    assert result.loc[2035, 'World'] == pytest.approx(0.14831592483)
    assert result.loc[2060, 'World'] == pytest.approx(0.36330169992)


def test_conv_ref_new_iunits_land():
    sp_world = [0, 0, 1.496434895, 3.429837617, 3.407771312, 3.385350949, 3.36260182, 3.339551447, 3.316229459,

                3.292667443, 3.268898758, 2.612516835, 3.245839333, 3.223747821, 3.201569768, 3.179334541, 3.157071886,

                3.134811735, 3.112584002, 3.090418386, 3.068344168, 2.958544262, 3.02978268, 3.008349446, 2.98710625,

                2.966077166, 2.945284989, 2.924751124, 2.904495508, 2.884536542, 2.864891042, 2.576649818, 2.856659245,

                4.334898124, 6.250416982, 6.210788688, 6.28096212, 6.106455764, 6.066707975, 6.027072713, 5.987583722,

                5.948275348, 5.276740913, 5.895296951, 5.858822974, 5.822643535]
    f = this_dir.parents[0].joinpath('data', 'ad_sp_pds.csv')
    pds_ad = pd.read_csv(f, index_col=0)
    f = this_dir.parents[0].joinpath('data', 'ad_sp_ref.csv')
    ref_ad = pd.read_csv(f, index_col=0)
    ac = advanced_controls.AdvancedControls(soln_expected_lifetime=30, conv_expected_lifetime=30)
    ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=ref_ad,
                                   soln_pds_funits_adopted=pds_ad)
    # test only world values as regional data has bugs in xls
    result = ua.conv_ref_new_iunits()['World'].values
    np.testing.assert_array_almost_equal(result, sp_world)


def test_conv_ref_new_iunits_repeated_cost_for_iunits():
    soln_pds_funits_adopted = pd.DataFrame(soln_funits_adopted_altcement_list[1:],
                                           columns=soln_funits_adopted_altcement_list[0]).set_index(
        'Year')
    soln_ref_funits_adopted = pd.DataFrame(0, index=soln_pds_funits_adopted.index,
                                           columns=soln_pds_funits_adopted.columns)
    ac = advanced_controls.AdvancedControls(conv_lifetime_capacity=30.0, conv_avg_annual_use=1.0)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   ref_total_adoption_units=None, pds_total_adoption_units=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted,
                                   repeated_cost_for_iunits=True)
    result = ua.conv_ref_new_iunits()
    expected = pd.DataFrame(soln_new_iunits_reqd_altcement_list[1:],
                            columns=soln_new_iunits_reqd_altcement_list[0]).set_index('Year')
    expected.name = "conv_ref_new_iunits"
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_direct_co2eq_emissions_saved_land():
    annual_ridl = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_annu_ridl.csv'), index_col=0)
    ac = advanced_controls.AdvancedControls(tco2eq_reduced_per_land_unit=313.791126867655, tco2eq_rplu_rate='One-time',

                                            delay_protection_1yr=False)
    expected = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_des_co2eq.csv'), index_col=0)
    with mock.patch.object(unitadoption.UnitAdoption, 'annual_reduction_in_total_degraded_land',
                           new=lambda x: annual_ridl):
        ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=None,
                                       soln_pds_funits_adopted=None)
        pd.testing.assert_frame_equal(ua.direct_co2eq_emissions_saved_land(), expected)


def test_net_land_units_after_emissions_lifetime():
    soln_pds_funits_adopted = pd.DataFrame(net_annual_land_units_adopted[1:],
                                           columns=net_annual_land_units_adopted[0]).set_index(
        'Year')
    soln_ref_funits_adopted = soln_pds_funits_adopted.copy()
    soln_ref_funits_adopted.loc[:, :] = 0.0
    ac = advanced_controls.AdvancedControls(land_annual_emissons_lifetime=10)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.net_land_units_after_emissions_lifetime()
    # Values from Conservation Agriculture with EG250 lifetime set to 10 years
    assert result.loc[2025, 'World'] == pytest.approx(0.0)
    assert result.loc[2026, 'World'] == pytest.approx(34.364230608997)
    assert result.loc[2035, 'OECD90'] == pytest.approx(71.617279280633)
    assert result.loc[2041, 'Latin America'] == pytest.approx(20.308752662402)
    assert result.loc[2046, 'Eastern Europe'] == pytest.approx(60.326701097136)
    assert result.loc[2059, 'Middle East and Africa'] == pytest.approx(56.865588505200)


def test_soln_pds_annual_land_area_harvested():
    new_land_units_reqd = pd.read_csv(this_dir.parents[0].joinpath('data', 'afforestation_nlur.csv'),
                                      index_col=0)
    ac = advanced_controls.AdvancedControls(harvest_frequency=20)
    expected = pd.read_csv(this_dir.parents[0].joinpath('data', 'afforestation_harvest.csv'),
                           index_col=0)
    with mock.patch.object(unitadoption.UnitAdoption, 'soln_pds_new_iunits_reqd',
                           new=lambda x: new_land_units_reqd):
        ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=None,
                                       soln_pds_funits_adopted=None)
        pd.testing.assert_frame_equal(ua.soln_pds_annual_land_area_harvested().loc[:, ['World']],
                                      expected.loc[:, ['World']])


def test_soln_pds_annual_land_area_harvested_perennial_biomass():
    soln_pds_funits_adopted = pd.DataFrame(net_annual_land_units_adopted_perbiomass_list[1:],
                                           columns=net_annual_land_units_adopted_perbiomass_list[0]).set_index('Year')
    ac = advanced_controls.AdvancedControls(harvest_frequency=20, soln_expected_lifetime=30.0)
    ua = unitadoption.UnitAdoption(ac=ac, soln_ref_funits_adopted=None,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted)
    result = ua.soln_pds_annual_land_area_harvested()
    expected = pd.DataFrame(soln_pds_annual_land_area_harvested_perennial_biomass_list[1:],
                            columns=soln_pds_annual_land_area_harvested_perennial_biomass_list[0]).set_index('Year')
    expected.name = 'soln_pds_annual_land_area_harvested'
    pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_direct_co2eq_emissions_saved_land_annual_not_protect():
    soln_pds_funits_adopted = pd.DataFrame(net_annual_land_units_adopted[1:],
                                           columns=net_annual_land_units_adopted[0]).set_index('Year')
    soln_ref_funits_adopted = soln_pds_funits_adopted.copy()
    soln_ref_funits_adopted.loc[:, :] = 0.0
    ac = advanced_controls.AdvancedControls(land_annual_emissons_lifetime=100,
                                            tco2eq_rplu_rate='Annual', disturbance_rate=0.0,
                                            tco2eq_reduced_per_land_unit=0.23357743333333333)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.direct_co2eq_emissions_saved_land()
    # Values from Conservation Agriculture
    assert result.loc[2015, 'OECD90'] == pytest.approx(2.29507225337865)
    assert result.loc[2021, 'World'] == pytest.approx(45.78887963463810)
    assert result.loc[2024, 'Middle East and Africa'] == pytest.approx(11.59338822588380)
    assert result.loc[2037, 'Latin America'] == pytest.approx(4.38116850491692)
    assert result.loc[2048, 'Asia (Sans Japan)'] == pytest.approx(16.95946227408880)
    assert result.loc[2060, 'Eastern Europe'] == pytest.approx(5.64414944055870)


def test_direct_co2eq_emissions_saved_land_onetime_not_protect():
    soln_pds_funits_adopted = pd.DataFrame(net_annual_land_units_adopted_SRI_list[1:],
                                           columns=net_annual_land_units_adopted_SRI_list[0]).set_index('Year')
    soln_ref_funits_adopted = soln_pds_funits_adopted.copy()
    soln_ref_funits_adopted.loc[:, :] = 0.0
    ac = advanced_controls.AdvancedControls(land_annual_emissons_lifetime=100,
                                            tco2eq_rplu_rate='One-time', disturbance_rate=0.0,
                                            tco2eq_reduced_per_land_unit=1.9964000000000002)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.direct_co2eq_emissions_saved_land()
    # Values from System of Rice Intensification Unit Adoption Calculations AT308:AU354
    assert result.loc[2015, 'World'] == pytest.approx(2.33469083300138)
    assert result.loc[2026, 'World'] == pytest.approx(2.33469083300142)
    assert result.loc[2034, 'World'] == pytest.approx(2.21940156759949)
    assert result.loc[2043, 'World'] == pytest.approx(1.44103756555924)
    assert result.loc[2052, 'World'] == pytest.approx(0.85917976648569)
    assert result.loc[2060, 'World'] == pytest.approx(0.51015076817701)


def test_direct_co2eq_emissions_saved_land_delta_pds_ref_factor():
    soln_pds_funits_adopted = pd.DataFrame(soln_pds_funits_adopted_smallholder_list[1:],
                                           columns=soln_pds_funits_adopted_smallholder_list[0]).set_index('Year')
    soln_ref_funits_adopted = pd.DataFrame(soln_ref_funits_adopted_smallholder_list[1:],
                                           columns=soln_ref_funits_adopted_smallholder_list[0]).set_index('Year')
    ac = advanced_controls.AdvancedControls(tco2eq_reduced_per_land_unit=313.791126867655,
                                            avoided_deforest_with_intensification=0.255526315789474)
    ua = unitadoption.UnitAdoption(ac=ac,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.direct_co2eq_emissions_saved_land()
    # Values from Smallholder Intensification Unit Adoption Calculations AT308:AU354
    assert result.loc[2015, 'World'] == pytest.approx(86.1366493749314)
    assert result.loc[2016, 'World'] == pytest.approx(86.1366493749369)
    assert result.loc[2024, 'World'] == pytest.approx(86.1366493749388)
    assert result.loc[2030, 'World'] == pytest.approx(86.1366493749314)
    assert result.loc[2031, 'World'] == pytest.approx(55.3589385314735)
    assert result.loc[2040, 'World'] == pytest.approx(55.3589385314684)
    assert result.loc[2050, 'World'] == pytest.approx(55.3589385314713)
    assert result.loc[2051, 'World'] == pytest.approx(11.2040578334937)
    assert result.loc[2060, 'World'] == pytest.approx(11.2040578334931)


def test_various_direct_emissions_saved_land_onetime_protect():
    soln_pds_funits_adopted = pd.DataFrame(net_annual_land_units_adopted[1:],
                                           columns=net_annual_land_units_adopted[0]).set_index('Year')
    soln_ref_funits_adopted = soln_pds_funits_adopted.copy()
    soln_ref_funits_adopted.loc[:, :] = 0.0
    tla_per_reg = pd.read_csv(this_dir.parents[0].joinpath('data', 'fp_tla_per_reg.csv'),
                              index_col=0)
    ac = advanced_controls.AdvancedControls(delay_protection_1yr=True, tco2eq_rplu_rate='One-time',
                                            disturbance_rate=0.0, degradation_rate=0.1,
                                            tch4_co2_reduced_per_land_unit=0.1,
                                            tco2eq_reduced_per_land_unit=0.0)
    ua = unitadoption.UnitAdoption(ac=ac, pds_total_adoption_units=tla_per_reg,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.direct_ch4_co2_emissions_saved_land()
    assert not all(result.loc[:, 'World'] == 0.0)
    ac = advanced_controls.AdvancedControls(delay_protection_1yr=True,
                                            tco2eq_rplu_rate='One-time', disturbance_rate=0.0, degradation_rate=0.1,
                                            tn2o_co2_reduced_per_land_unit=0.1, tco2eq_reduced_per_land_unit=0.0)
    ua = unitadoption.UnitAdoption(ac=ac, pds_total_adoption_units=tla_per_reg,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.direct_n2o_co2_emissions_saved_land()
    assert not all(result.loc[:, 'World'] == 0.0)
    ac = advanced_controls.AdvancedControls(delay_protection_1yr=True,
                                            tco2eq_rplu_rate='One-time', disturbance_rate=0.0, degradation_rate=0.1,
                                            tco2_reduced_per_land_unit=0.1, tco2eq_reduced_per_land_unit=0.0)
    ua = unitadoption.UnitAdoption(ac=ac, pds_total_adoption_units=tla_per_reg,
                                   soln_pds_funits_adopted=soln_pds_funits_adopted,
                                   soln_ref_funits_adopted=soln_ref_funits_adopted)
    result = ua.direct_co2_emissions_saved_land()
    assert not all(result.loc[:, 'World'] == 0.0)


# SolarPVUtil 'Unit Adoption Calculations'!B134:L181
soln_pds_funits_adopted_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778, 14.65061888889,
     14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
    [2015, 176.24092107213, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 272.03135207741, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 383.30935172620, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 509.37947394851, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 649.54627267436, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 654.00000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 969.38811535670, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 1147.67226717322, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 1337.27131121334, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 1537.48980140706, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 1595.40000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 1967.00333597537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 2194.90748820999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 2430.64930231826, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 2673.53333223022, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 3040.20000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 3177.94625518520, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 3438.08425608826, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 3702.58268851506, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 3970.74610639560, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 4241.87906365990, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 4515.28611423798, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 4790.27181205984, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 5066.14071105551, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 5342.19736515499, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 5665.20000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 5892.09215438547, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 6164.53939737649, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 6434.39261119138, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 6700.95634976017, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 6963.53516701285, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 7221.43361687946, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 7473.95625328999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 7720.40763017447, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 7960.09230146291, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 8167.80000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 8416.37974297171, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 8631.59162105212, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 8837.25500925653, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 9032.67446151498, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 9217.15453175747, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 9389.99977391402, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 9550.51474191465, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 9698.00398968936, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 9831.77207116817, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 9951.12354028110, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil 'Unit Adoption Calculations'!B134:L181 with regional columns set to nan.
soln_pds_funits_adopted_no_regional_data_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778, 14.65061888889,
     14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
    [2015, 176.24092107213, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2016, 272.03135207741, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2017, 383.30935172620, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2018, 509.37947394851, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2019, 649.54627267436, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2020, 654.00000000000, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2021, 969.38811535670, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    [2022, 1147.67226717322, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2023, 1337.27131121334, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2024, 1537.48980140706, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2025, 1595.40000000000, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2026, 1967.00333597537, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2027, 2194.90748820999, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2028, 2430.64930231826, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2029, 2673.53333223022, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2030, 3040.20000000000, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2031, 3177.94625518520, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2032, 3438.08425608826, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2033, 3702.58268851506, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2034, 3970.74610639560, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2035, 4241.87906365990, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2036, 4515.28611423798, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2037, 4790.27181205984, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2038, 5066.14071105551, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2039, 5342.19736515499, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2040, 5665.20000000000, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2041, 5892.09215438547, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2042, 6164.53939737649, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2043, 6434.39261119138, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2044, 6700.95634976017, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2045, 6963.53516701285, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2046, 7221.43361687946, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2047, 7473.95625328999, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2048, 7720.40763017447, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2049, 7960.09230146291, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2050, 8167.80000000000, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2051, 8416.37974297171, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2052, 8631.59162105212, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2053, 8837.25500925653, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2054, 9032.67446151498, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2055, 9217.15453175747, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2056, 9389.99977391402, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2057, 9550.51474191465, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2058, 9698.00398968936, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2059, 9831.77207116817, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],

    [2060, 9951.12354028110, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
     np.nan]]

# SolarPVUtil 'Unit Adoption Calculations'!AX134:BH181
soln_pds_tot_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.06115814489, 0.04072624506, 0.00018047945, 0.01144207203, 0.00085524497, 0.00795507895, 0.00812970502,
     0.00149228865, 0.03001194422, 0.00712649942],
    [2015, 0.09569632876, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 0.14770917868, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 0.20813155943, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 0.27658585364, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 0.35269444391, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 0.35511275489, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 0.52636404313, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 0.62316981729, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 0.72611941799, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 0.83483522783, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 0.86627964703, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 1.06805500539, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 1.19180373834, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 1.31980821089, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 1.45169080567, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 1.65078562298, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 1.72557989233, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 1.86683114944, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 2.01045005923, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 2.15605900432, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 2.30328036731, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 2.45173653082, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 2.60104987747, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 2.75084278988, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 2.90073765065, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 3.07612351532, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 3.19932274775, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 3.34725774931, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 3.49378422970, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 3.63852457153, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 3.78110115742, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 3.92113636998, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 4.05825259183, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 4.19207220558, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 4.32221759385, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 4.43499993794, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 4.56997522439, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 4.68683223190, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 4.79850454439, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 4.90461454447, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 5.00478461475, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 5.09863713786, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 5.18579449640, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 5.26587907300, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 5.33851325027, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 5.40331941081, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil 'Unit Adoption Calculations'!BN134:BS181
soln_pds_big4_iunits_reqd_list = [
    ["Year", "Rest of World", "China", "India", "EU", "USA"],
    [2014, 0.01439770758, 0.00812970502, 0.00149228865, 0.03001194422, 0.00712649942],
    [2015, 0.09569632876, 0.00, 0.00, 0.00, 0.00],
    [2016, 0.14770917868, 0.00, 0.00, 0.00, 0.00],
    [2017, 0.20813155943, 0.00, 0.00, 0.00, 0.00],
    [2018, 0.27658585364, 0.00, 0.00, 0.00, 0.00],
    [2019, 0.35269444391, 0.00, 0.00, 0.00, 0.00],
    [2020, 0.35511275489, 0.00, 0.00, 0.00, 0.00],
    [2021, 0.52636404313, 0.00, 0.00, 0.00, 0.00],
    [2022, 0.62316981729, 0.00, 0.00, 0.00, 0.00],
    [2023, 0.72611941799, 0.00, 0.00, 0.00, 0.00],
    [2024, 0.83483522783, 0.00, 0.00, 0.00, 0.00],
    [2025, 0.86627964703, 0.00, 0.00, 0.00, 0.00],
    [2026, 1.06805500539, 0.00, 0.00, 0.00, 0.00],
    [2027, 1.19180373834, 0.00, 0.00, 0.00, 0.00],
    [2028, 1.31980821089, 0.00, 0.00, 0.00, 0.00],
    [2029, 1.45169080567, 0.00, 0.00, 0.00, 0.00],
    [2030, 1.65078562298, 0.00, 0.00, 0.00, 0.00],
    [2031, 1.72557989233, 0.00, 0.00, 0.00, 0.00],
    [2032, 1.86683114944, 0.00, 0.00, 0.00, 0.00],
    [2033, 2.01045005923, 0.00, 0.00, 0.00, 0.00],
    [2034, 2.15605900432, 0.00, 0.00, 0.00, 0.00],
    [2035, 2.30328036731, 0.00, 0.00, 0.00, 0.00],
    [2036, 2.45173653082, 0.00, 0.00, 0.00, 0.00],
    [2037, 2.60104987747, 0.00, 0.00, 0.00, 0.00],
    [2038, 2.75084278988, 0.00, 0.00, 0.00, 0.00],
    [2039, 2.90073765065, 0.00, 0.00, 0.00, 0.00],
    [2040, 3.07612351532, 0.00, 0.00, 0.00, 0.00],
    [2041, 3.19932274775, 0.00, 0.00, 0.00, 0.00],
    [2042, 3.34725774931, 0.00, 0.00, 0.00, 0.00],
    [2043, 3.49378422970, 0.00, 0.00, 0.00, 0.00],
    [2044, 3.63852457153, 0.00, 0.00, 0.00, 0.00],
    [2045, 3.78110115742, 0.00, 0.00, 0.00, 0.00],
    [2046, 3.92113636998, 0.00, 0.00, 0.00, 0.00],
    [2047, 4.05825259183, 0.00, 0.00, 0.00, 0.00],
    [2048, 4.19207220558, 0.00, 0.00, 0.00, 0.00],
    [2049, 4.32221759385, 0.00, 0.00, 0.00, 0.00],
    [2050, 4.43499993794, 0.00, 0.00, 0.00, 0.00],
    [2051, 4.56997522439, 0.00, 0.00, 0.00, 0.00],
    [2052, 4.68683223190, 0.00, 0.00, 0.00, 0.00],
    [2053, 4.79850454439, 0.00, 0.00, 0.00, 0.00],
    [2054, 4.90461454447, 0.00, 0.00, 0.00, 0.00],
    [2055, 5.00478461475, 0.00, 0.00, 0.00, 0.00],
    [2056, 5.09863713786, 0.00, 0.00, 0.00, 0.00],
    [2057, 5.18579449640, 0.00, 0.00, 0.00, 0.00],
    [2058, 5.26587907300, 0.00, 0.00, 0.00, 0.00],
    [2059, 5.33851325027, 0.00, 0.00, 0.00, 0.00],
    [2060, 5.40331941081, 0.00, 0.00, 0.00, 0.00]]

# SolarPVUtil 'Unit Adoption Calculations'!BN134:BS181
soln_pds_big4_iunits_reqd_no_regional_data_list = [
    ["Year", "Rest of World", "China", "India", "EU", "USA"],
    [2014, 0.01439770758, 0.00812970502, 0.00149228865, 0.03001194422, 0.00712649942],
    [2015, 0.09569632876, np.nan, np.nan, np.nan, np.nan],
    [2016, 0.14770917868, np.nan, np.nan, np.nan, np.nan],
    [2017, 0.20813155943, np.nan, np.nan, np.nan, np.nan],
    [2018, 0.27658585364, np.nan, np.nan, np.nan, np.nan],
    [2019, 0.35269444391, np.nan, np.nan, np.nan, np.nan],
    [2020, 0.35511275489, np.nan, np.nan, np.nan, np.nan],
    [2021, 0.52636404313, np.nan, np.nan, np.nan, np.nan],
    [2022, 0.62316981729, np.nan, np.nan, np.nan, np.nan],
    [2023, 0.72611941799, np.nan, np.nan, np.nan, np.nan],
    [2024, 0.83483522783, np.nan, np.nan, np.nan, np.nan],
    [2025, 0.86627964703, np.nan, np.nan, np.nan, np.nan],
    [2026, 1.06805500539, np.nan, np.nan, np.nan, np.nan],
    [2027, 1.19180373834, np.nan, np.nan, np.nan, np.nan],
    [2028, 1.31980821089, np.nan, np.nan, np.nan, np.nan],
    [2029, 1.45169080567, np.nan, np.nan, np.nan, np.nan],
    [2030, 1.65078562298, np.nan, np.nan, np.nan, np.nan],
    [2031, 1.72557989233, np.nan, np.nan, np.nan, np.nan],
    [2032, 1.86683114944, np.nan, np.nan, np.nan, np.nan],
    [2033, 2.01045005923, np.nan, np.nan, np.nan, np.nan],
    [2034, 2.15605900432, np.nan, np.nan, np.nan, np.nan],
    [2035, 2.30328036731, np.nan, np.nan, np.nan, np.nan],
    [2036, 2.45173653082, np.nan, np.nan, np.nan, np.nan],
    [2037, 2.60104987747, np.nan, np.nan, np.nan, np.nan],
    [2038, 2.75084278988, np.nan, np.nan, np.nan, np.nan],
    [2039, 2.90073765065, np.nan, np.nan, np.nan, np.nan],
    [2040, 3.07612351532, np.nan, np.nan, np.nan, np.nan],
    [2041, 3.19932274775, np.nan, np.nan, np.nan, np.nan],
    [2042, 3.34725774931, np.nan, np.nan, np.nan, np.nan],
    [2043, 3.49378422970, np.nan, np.nan, np.nan, np.nan],
    [2044, 3.63852457153, np.nan, np.nan, np.nan, np.nan],
    [2045, 3.78110115742, np.nan, np.nan, np.nan, np.nan],
    [2046, 3.92113636998, np.nan, np.nan, np.nan, np.nan],
    [2047, 4.05825259183, np.nan, np.nan, np.nan, np.nan],
    [2048, 4.19207220558, np.nan, np.nan, np.nan, np.nan],
    [2049, 4.32221759385, np.nan, np.nan, np.nan, np.nan],
    [2050, 4.43499993794, np.nan, np.nan, np.nan, np.nan],
    [2051, 4.56997522439, np.nan, np.nan, np.nan, np.nan],
    [2052, 4.68683223190, np.nan, np.nan, np.nan, np.nan],
    [2053, 4.79850454439, np.nan, np.nan, np.nan, np.nan],
    [2054, 4.90461454447, np.nan, np.nan, np.nan, np.nan],
    [2055, 5.00478461475, np.nan, np.nan, np.nan, np.nan],
    [2056, 5.09863713786, np.nan, np.nan, np.nan, np.nan],
    [2057, 5.18579449640, np.nan, np.nan, np.nan, np.nan],
    [2058, 5.26587907300, np.nan, np.nan, np.nan, np.nan],
    [2059, 5.33851325027, np.nan, np.nan, np.nan, np.nan],
    [2060, 5.40331941081, np.nan, np.nan, np.nan, np.nan]]

# SolarPVUtil 'Unit Adoption Calculations'!AG134:AQ181
soln_pds_new_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2015, 0.03453818387, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 0.05201284992, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 0.06042238076, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 0.06845429421, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 0.07610859028, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 0.00241831098, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 0.17125128823, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 0.09680577417, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2023, 0.10294960069, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2024, 0.10871580984, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2025, 0.03144441920, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2026, 0.20177535836, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2027, 0.12374873295, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2028, 0.12800447256, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2029, 0.13188259477, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2030, 0.19909481731, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2031, 0.07479426935, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2032, 0.14125125711, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2033, 0.14361890979, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2034, 0.14560894508, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2035, 0.14722136299, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2036, 0.14845616351, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2037, 0.14931334665, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2038, 0.14979291240, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2039, 0.14989486077, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2040, 0.17538586468, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2041, 0.12319923243, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2042, 0.18247318543, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2043, 0.19853933031, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2044, 0.20516272259, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2045, 0.21103088010, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2046, 0.21614380284, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2047, 0.13953453283, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2048, 0.30507090198, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2049, 0.22695116243, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2050, 0.21573194479, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2051, 0.24369109629, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 0.14830142671, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 0.31344767084, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 0.22985873303, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 0.22817454284, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 0.22573511788, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 0.28625217585, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 0.15487884595, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 0.21388543438, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 0.20842507034, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# SolarPVUtil 'Unit Adoption Calculations'!B197:L244
soln_ref_funits_adopted_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778, 14.65061888889,
     14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
    [2015, 117.07139624049, 75.62640223557, 0.33768156367, 22.15920892112, 1.71009099271, 15.41714380040,
     15.43313810117, 3.07011430874, 55.75969246529, 13.21605539049],
    [2016, 121.50975914765, 76.24855891557, 0.34297979401, 23.24591339780, 1.84510420765, 16.18366871191,
     15.89405398012, 3.39192750636, 56.24733048614, 13.30746078097],
    [2017, 125.94812205481, 76.87071559558, 0.34827802435, 24.33261787447, 1.98011742258, 16.95019362342,
     16.35496985906, 3.71374070399, 56.73496850699, 13.39886617146],
    [2018, 130.38648496197, 77.49287227559, 0.35357625469, 25.41932235115, 2.11513063752, 17.71671853493,
     16.81588573801, 4.03555390161, 57.22260652784, 13.49027156194],
    [2019, 134.82484786913, 78.11502895560, 0.35887448503, 26.50602682782, 2.25014385245, 18.48324344644,
     17.27680161696, 4.35736709924, 57.71024454869, 13.58167695243],
    [2020, 139.26321077629, 78.73718563561, 0.36417271537, 27.59273130450, 2.38515706739, 19.24976835795,
     17.73771749591, 4.67918029686, 58.19788256953, 13.67308234291],
    [2021, 143.70157368345, 79.35934231562, 0.36947094570, 28.67943578117, 2.52017028232, 20.01629326946,
     18.19863337485, 5.00099349449, 58.68552059038, 13.76448773340],
    [2022, 148.13993659061, 79.98149899563, 0.37476917604, 29.76614025785, 2.65518349726, 20.78281818097,
     18.65954925380, 5.32280669212, 59.17315861123, 13.85589312388],
    [2023, 152.57829949777, 80.60365567564, 0.38006740638, 30.85284473453, 2.79019671219, 21.54934309248,
     19.12046513275, 5.64461988974, 59.66079663208, 13.94729851437],
    [2024, 157.01666240493, 81.22581235565, 0.38536563672, 31.93954921120, 2.92520992713, 22.31586800399,
     19.58138101170, 5.96643308737, 60.14843465293, 14.03870390485],
    [2025, 161.45502531209, 81.84796903566, 0.39066386706, 33.02625368788, 3.06022314206, 23.08239291550,
     20.04229689064, 6.28824628499, 60.63607267378, 14.13010929534],
    [2026, 165.89338821925, 82.47012571567, 0.39596209740, 34.11295816455, 3.19523635700, 23.84891782701,
     20.50321276959, 6.61005948262, 61.12371069462, 14.22151468583],
    [2027, 170.33175112641, 83.09228239568, 0.40126032774, 35.19966264123, 3.33024957193, 24.61544273852,
     20.96412864854, 6.93187268024, 61.61134871547, 14.31292007631],
    [2028, 174.77011403357, 83.71443907569, 0.40655855808, 36.28636711790, 3.46526278687, 25.38196765003,
     21.42504452749, 7.25368587787, 62.09898673632, 14.40432546680],
    [2029, 179.20847694073, 84.33659575570, 0.41185678841, 37.37307159458, 3.60027600180, 26.14849256154,
     21.88596040643, 7.57549907549, 62.58662475717, 14.49573085728],
    [2030, 183.64683984789, 84.95875243571, 0.41715501875, 38.45977607125, 3.73528921674, 26.91501747306,
     22.34687628538, 7.89731227312, 63.07426277802, 14.58713624777],
    [2031, 188.08520275505, 85.58090911572, 0.42245324909, 39.54648054793, 3.87030243167, 27.68154238457,
     22.80779216433, 8.21912547074, 63.56190079887, 14.67854163825],
    [2032, 192.52356566221, 86.20306579573, 0.42775147943, 40.63318502461, 4.00531564661, 28.44806729608,
     23.26870804327, 8.54093866837, 64.04953881971, 14.76994702874],
    [2033, 196.96192856937, 86.82522247573, 0.43304970977, 41.71988950128, 4.14032886154, 29.21459220759,
     23.72962392222, 8.86275186600, 64.53717684056, 14.86135241922],
    [2034, 201.40029147653, 87.44737915574, 0.43834794011, 42.80659397796, 4.27534207648, 29.98111711910,
     24.19053980117, 9.18456506362, 65.02481486141, 14.95275780971],
    [2035, 205.83865438369, 88.06953583575, 0.44364617045, 43.89329845463, 4.41035529141, 30.74764203061,
     24.65145568012, 9.50637826125, 65.51245288226, 15.04416320019],
    [2036, 210.27701729085, 88.69169251576, 0.44894440079, 44.98000293131, 4.54536850635, 31.51416694212,
     25.11237155906, 9.82819145887, 66.00009090311, 15.13556859068],
    [2037, 214.71538019801, 89.31384919577, 0.45424263112, 46.06670740798, 4.68038172128, 32.28069185363,
     25.57328743801, 10.15000465650, 66.48772892395, 15.22697398117],
    [2038, 219.15374310517, 89.93600587578, 0.45954086146, 47.15341188466, 4.81539493622, 33.04721676514,
     26.03420331696, 10.47181785412, 66.97536694480, 15.31837937165],
    [2039, 223.59210601233, 90.55816255579, 0.46483909180, 48.24011636133, 4.95040815115, 33.81374167665,
     26.49511919591, 10.79363105175, 67.46300496565, 15.40978476214],
    [2040, 228.03046891949, 91.18031923580, 0.47013732214, 49.32682083801, 5.08542136609, 34.58026658816,
     26.95603507485, 11.11544424937, 67.95064298650, 15.50119015262],
    [2041, 232.46883182665, 91.80247591581, 0.47543555248, 50.41352531469, 5.22043458102, 35.34679149967,
     27.41695095380, 11.43725744700, 68.43828100735, 15.59259554311],
    [2042, 236.90719473381, 92.42463259582, 0.48073378282, 51.50022979136, 5.35544779596, 36.11331641118,
     27.87786683275, 11.75907064462, 68.92591902820, 15.68400093359],
    [2043, 241.34555764097, 93.04678927583, 0.48603201316, 52.58693426804, 5.49046101089, 36.87984132269,
     28.33878271170, 12.08088384225, 69.41355704904, 15.77540632408],
    [2044, 245.78392054813, 93.66894595584, 0.49133024350, 53.67363874471, 5.62547422583, 37.64636623420,
     28.79969859064, 12.40269703988, 69.90119506989, 15.86681171456],
    [2045, 250.22228345529, 94.29110263585, 0.49662847384, 54.76034322139, 5.76048744076, 38.41289114571,
     29.26061446959, 12.72451023750, 70.38883309074, 15.95821710505],
    [2046, 254.66064636245, 94.91325931586, 0.50192670417, 55.84704769806, 5.89550065570, 39.17941605722,
     29.72153034854, 13.04632343513, 70.87647111159, 16.04962249553],
    [2047, 259.09900926961, 95.53541599587, 0.50722493451, 56.93375217474, 6.03051387063, 39.94594096873,
     30.18244622749, 13.36813663275, 71.36410913244, 16.14102788602],
    [2048, 263.53737217677, 96.15757267588, 0.51252316485, 58.02045665141, 6.16552708557, 40.71246588024,
     30.64336210643, 13.68994983038, 71.85174715329, 16.23243327651],
    [2049, 267.97573508393, 96.77972935589, 0.51782139519, 59.10716112809, 6.30054030050, 41.47899079175,
     31.10427798538, 14.01176302800, 72.33938517413, 16.32383866699],
    [2050, 272.41409799109, 97.40188603589, 0.52311962553, 60.19386560477, 6.43555351544, 42.24551570326,
     31.56519386433, 14.33357622563, 72.82702319498, 16.41524405748],
    [2051, 276.85246089825, 98.02404271590, 0.52841785587, 61.28057008144, 6.57056673037, 43.01204061477,
     32.02610974327, 14.65538942325, 73.31466121583, 16.50664944796],
    [2052, 281.29082380541, 98.64619939591, 0.53371608621, 62.36727455812, 6.70557994531, 43.77856552628,
     32.48702562222, 14.97720262088, 73.80229923668, 16.59805483845],
    [2053, 285.72918671257, 99.26835607592, 0.53901431655, 63.45397903479, 6.84059316024, 44.54509043779,
     32.94794150117, 15.29901581851, 74.28993725753, 16.68946022893],
    [2054, 290.16754961973, 99.89051275593, 0.54431254688, 64.54068351147, 6.97560637518, 45.31161534930,
     33.40885738012, 15.62082901613, 74.77757527838, 16.78086561942],
    [2055, 294.60591252689, 100.51266943594, 0.54961077722, 65.62738798814, 7.11061959011, 46.07814026081,
     33.86977325906, 15.94264221376, 75.26521329922, 16.87227100990],
    [2056, 299.04427543405, 101.13482611595, 0.55490900756, 66.71409246482, 7.24563280505, 46.84466517233,
     34.33068913801, 16.26445541138, 75.75285132007, 16.96367640039],
    [2057, 303.48263834121, 101.75698279596, 0.56020723790, 67.80079694150, 7.38064601998, 47.61119008384,
     34.79160501696, 16.58626860901, 76.24048934092, 17.05508179088],
    [2058, 307.92100124837, 102.37913947597, 0.56550546824, 68.88750141817, 7.51565923492, 48.37771499535,
     35.25252089591, 16.90808180663, 76.72812736177, 17.14648718136],
    [2059, 312.35936415553, 103.00129615598, 0.57080369858, 69.97420589485, 7.65067244985, 49.14423990686,
     35.71343677485, 17.22989500426, 77.21576538262, 17.23789257185],
    [2060, 316.79772706269, 103.62345283599, 0.57610192892, 71.06091037152, 7.78568566479, 49.91076481837,
     36.17435265380, 17.55170820188, 77.70340340347, 17.32929796233]]

# SolarPVUtil 'Unit Adoption Calculations'!AX197:BH244
soln_ref_tot_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.06115814489, 0.04072624506, 0.00018047945, 0.01144207203, 0.00085524497, 0.00795507895, 0.00812970502,
     0.00149228865, 0.03001194422, 0.00712649942],
    [2015, 0.06356811321, 0.04106406734, 0.00018335632, 0.01203213720, 0.00092855523, 0.00837129114, 0.00837997582,
     0.00166702867, 0.03027672478, 0.00717613125],
    [2016, 0.06597808152, 0.04140188962, 0.00018623318, 0.01262220236, 0.00100186550, 0.00878750333, 0.00863024663,
     0.00184176869, 0.03054150533, 0.00722576309],
    [2017, 0.06838804984, 0.04173971190, 0.00018911004, 0.01321226753, 0.00107517577, 0.00920371553, 0.00888051744,
     0.00201650870, 0.03080628588, 0.00727539492],
    [2018, 0.07079801816, 0.04207753419, 0.00019198691, 0.01380233270, 0.00114848604, 0.00961992772, 0.00913078824,
     0.00219124872, 0.03107106643, 0.00732502676],
    [2019, 0.07320798648, 0.04241535647, 0.00019486377, 0.01439239787, 0.00122179630, 0.01003613991, 0.00938105905,
     0.00236598874, 0.03133584698, 0.00737465859],
    [2020, 0.07561795479, 0.04275317875, 0.00019774064, 0.01498246304, 0.00129510657, 0.01045235210, 0.00963132986,
     0.00254072876, 0.03160062754, 0.00742429043],
    [2021, 0.07802792311, 0.04309100103, 0.00020061750, 0.01557252821, 0.00136841684, 0.01086856429, 0.00988160066,
     0.00271546877, 0.03186540809, 0.00747392226],
    [2022, 0.08043789143, 0.04342882332, 0.00020349436, 0.01616259338, 0.00144172710, 0.01128477648, 0.01013187147,
     0.00289020879, 0.03213018864, 0.00752355410],
    [2023, 0.08284785974, 0.04376664560, 0.00020637123, 0.01675265855, 0.00151503737, 0.01170098867, 0.01038214228,
     0.00306494881, 0.03239496919, 0.00757318593],
    [2024, 0.08525782806, 0.04410446788, 0.00020924809, 0.01734272372, 0.00158834764, 0.01211720086, 0.01063241308,
     0.00323968882, 0.03265974974, 0.00762281777],
    [2025, 0.08766779638, 0.04444229016, 0.00021212496, 0.01793278889, 0.00166165791, 0.01253341305, 0.01088268389,
     0.00341442884, 0.03292453030, 0.00767244960],
    [2026, 0.09007776469, 0.04478011245, 0.00021500182, 0.01852285405, 0.00173496817, 0.01294962525, 0.01113295470,
     0.00358916886, 0.03318931085, 0.00772208144],
    [2027, 0.09248773301, 0.04511793473, 0.00021787869, 0.01911291922, 0.00180827844, 0.01336583744, 0.01138322550,
     0.00376390887, 0.03345409140, 0.00777171327],
    [2028, 0.09489770133, 0.04545575701, 0.00022075555, 0.01970298439, 0.00188158871, 0.01378204963, 0.01163349631,
     0.00393864889, 0.03371887195, 0.00782134511],
    [2029, 0.09730766964, 0.04579357929, 0.00022363241, 0.02029304956, 0.00195489897, 0.01419826182, 0.01188376712,
     0.00411338891, 0.03398365250, 0.00787097694],
    [2030, 0.09971763796, 0.04613140157, 0.00022650928, 0.02088311473, 0.00202820924, 0.01461447401, 0.01213403792,
     0.00428812893, 0.03424843305, 0.00792060878],
    [2031, 0.10212760628, 0.04646922386, 0.00022938614, 0.02147317990, 0.00210151951, 0.01503068620, 0.01238430873,
     0.00446286894, 0.03451321361, 0.00797024061],
    [2032, 0.10453757459, 0.04680704614, 0.00023226301, 0.02206324507, 0.00217482978, 0.01544689839, 0.01263457954,
     0.00463760896, 0.03477799416, 0.00801987244],
    [2033, 0.10694754291, 0.04714486842, 0.00023513987, 0.02265331024, 0.00224814004, 0.01586311058, 0.01288485034,
     0.00481234898, 0.03504277471, 0.00806950428],
    [2034, 0.10935751123, 0.04748269070, 0.00023801673, 0.02324337541, 0.00232145031, 0.01627932278, 0.01313512115,
     0.00498708899, 0.03530755526, 0.00811913611],
    [2035, 0.11176747954, 0.04782051299, 0.00024089360, 0.02383344057, 0.00239476058, 0.01669553497, 0.01338539196,
     0.00516182901, 0.03557233581, 0.00816876795],
    [2036, 0.11417744786, 0.04815833527, 0.00024377046, 0.02442350574, 0.00246807084, 0.01711174716, 0.01363566276,
     0.00533656903, 0.03583711637, 0.00821839978],
    [2037, 0.11658741618, 0.04849615755, 0.00024664733, 0.02501357091, 0.00254138111, 0.01752795935, 0.01388593357,
     0.00551130905, 0.03610189692, 0.00826803162],
    [2038, 0.11899738449, 0.04883397983, 0.00024952419, 0.02560363608, 0.00261469138, 0.01794417154, 0.01413620438,
     0.00568604906, 0.03636667747, 0.00831766345],
    [2039, 0.12140735281, 0.04917180212, 0.00025240106, 0.02619370125, 0.00268800165, 0.01836038373, 0.01438647518,
     0.00586078908, 0.03663145802, 0.00836729529],
    [2040, 0.12381732113, 0.04950962440, 0.00025527792, 0.02678376642, 0.00276131191, 0.01877659592, 0.01463674599,
     0.00603552910, 0.03689623857, 0.00841692712],
    [2041, 0.12622728944, 0.04984744668, 0.00025815478, 0.02737383159, 0.00283462218, 0.01919280811, 0.01488701680,
     0.00621026911, 0.03716101913, 0.00846655896],
    [2042, 0.12863725776, 0.05018526896, 0.00026103165, 0.02796389676, 0.00290793245, 0.01960902030, 0.01513728760,
     0.00638500913, 0.03742579968, 0.00851619079],
    [2043, 0.13104722608, 0.05052309124, 0.00026390851, 0.02855396193, 0.00298124271, 0.02002523250, 0.01538755841,
     0.00655974915, 0.03769058023, 0.00856582263],
    [2044, 0.13345719439, 0.05086091353, 0.00026678538, 0.02914402709, 0.00305455298, 0.02044144469, 0.01563782922,
     0.00673448917, 0.03795536078, 0.00861545446],
    [2045, 0.13586716271, 0.05119873581, 0.00026966224, 0.02973409226, 0.00312786325, 0.02085765688, 0.01588810002,
     0.00690922918, 0.03822014133, 0.00866508630],
    [2046, 0.13827713103, 0.05153655809, 0.00027253911, 0.03032415743, 0.00320117352, 0.02127386907, 0.01613837083,
     0.00708396920, 0.03848492189, 0.00871471813],
    [2047, 0.14068709935, 0.05187438037, 0.00027541597, 0.03091422260, 0.00327448378, 0.02169008126, 0.01638864163,
     0.00725870922, 0.03874970244, 0.00876434997],
    [2048, 0.14309706766, 0.05221220266, 0.00027829283, 0.03150428777, 0.00334779405, 0.02210629345, 0.01663891244,
     0.00743344923, 0.03901448299, 0.00881398180],
    [2049, 0.14550703598, 0.05255002494, 0.00028116970, 0.03209435294, 0.00342110432, 0.02252250564, 0.01688918325,
     0.00760818925, 0.03927926354, 0.00886361364],
    [2050, 0.14791700430, 0.05288784722, 0.00028404656, 0.03268441811, 0.00349441458, 0.02293871783, 0.01713945405,
     0.00778292927, 0.03954404409, 0.00891324547],
    [2051, 0.15032697261, 0.05322566950, 0.00028692343, 0.03327448328, 0.00356772485, 0.02335493002, 0.01738972486,
     0.00795766928, 0.03980882465, 0.00896287731],
    [2052, 0.15273694093, 0.05356349178, 0.00028980029, 0.03386454845, 0.00364103512, 0.02377114222, 0.01763999567,
     0.00813240930, 0.04007360520, 0.00901250914],
    [2053, 0.15514690925, 0.05390131407, 0.00029267715, 0.03445461361, 0.00371434539, 0.02418735441, 0.01789026647,
     0.00830714932, 0.04033838575, 0.00906214098],
    [2054, 0.15755687756, 0.05423913635, 0.00029555402, 0.03504467878, 0.00378765565, 0.02460356660, 0.01814053728,
     0.00848188934, 0.04060316630, 0.00911177281],
    [2055, 0.15996684588, 0.05457695863, 0.00029843088, 0.03563474395, 0.00386096592, 0.02501977879, 0.01839080809,
     0.00865662935, 0.04086794685, 0.00916140465],
    [2056, 0.16237681420, 0.05491478091, 0.00030130775, 0.03622480912, 0.00393427619, 0.02543599098, 0.01864107889,
     0.00883136937, 0.04113272741, 0.00921103648],
    [2057, 0.16478678251, 0.05525260320, 0.00030418461, 0.03681487429, 0.00400758645, 0.02585220317, 0.01889134970,
     0.00900610939, 0.04139750796, 0.00926066832],
    [2058, 0.16719675083, 0.05559042548, 0.00030706148, 0.03740493946, 0.00408089672, 0.02626841536, 0.01914162051,
     0.00918084940, 0.04166228851, 0.00931030015],
    [2059, 0.16960671915, 0.05592824776, 0.00030993834, 0.03799500463, 0.00415420699, 0.02668462755, 0.01939189131,
     0.00935558942, 0.04192706906, 0.00935993199],
    [2060, 0.17201668746, 0.05626607004, 0.00031281520, 0.03858506980, 0.00422751726, 0.02710083975, 0.01964216212,
     0.00953032944, 0.04219184961, 0.00940956382]]

# SolarPVUtil 'Unit Adoption Calculations'!AG197:AQ244
soln_ref_new_iunits_reqd_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2015, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2016, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2017, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2018, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2019, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2020, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2021, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2022, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2023, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2024, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2025, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2026, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2027, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2028, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2029, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2030, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2031, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2032, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2033, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2034, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2035, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2036, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2037, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2038, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2039, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2040, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2041, 0.00240996832, 0.00033782228, 0.00000287686, 0.00059006517, 0.00007331027, 0.00041621219, 0.00025027081,
     0.00017474002, 0.00026478055, 0.00004963183],
    [2042, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2043, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2044, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2045, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2046, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2047, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2048, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2049, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2050, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2051, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2052, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2053, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2054, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2055, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2056, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2057, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2058, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2059, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367],
    [2060, 0.00481993663, 0.00067564456, 0.00000575373, 0.00118013034, 0.00014662053, 0.00083242438, 0.00050054161,
     0.00034948003, 0.00052956110, 0.00009926367]]

# SolarPVUtil 'Unit Adoption Calculations'!AG251:AQ298
conv_ref_new_iunits_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2015, 0.01196107466, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2016, 0.01846675143, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2017, 0.02159755171, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2018, 0.02458776809, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2019, 0.02743740058, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2020, 0.00000310591, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2021, 0.06285825712, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2022, 0.03514279466, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2023, 0.03743009156, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2024, 0.03957680456, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2025, 0.01080929112, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2026, 0.07422212143, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2027, 0.04517344019, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2028, 0.04675781761, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2029, 0.04820161112, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2030, 0.07322417769, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2031, 0.02694808953, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2032, 0.05168948830, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2033, 0.05257094623, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2034, 0.05331182027, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2035, 0.05391211041, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2036, 0.05437181665, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2037, 0.05469093900, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2038, 0.05486947745, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2039, 0.05490743200, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2040, 0.06439752648, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2041, 0.04496886559, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2042, 0.05417779227, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2043, 0.05365341124, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2044, 0.05298844631, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2045, 0.05218289748, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2046, 0.05123676476, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2047, 0.05015004813, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2048, 0.04892274762, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2049, 0.04755486320, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2050, 0.04109074236, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2051, 0.04935299521, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2052, 0.04260770657, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2053, 0.05263856124, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2054, 0.05707343410, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2055, 0.05799284659, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2056, 0.05863109128, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2057, 0.05898816818, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2058, 0.02892073402, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2059, 0.08900216185, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    [2060, 0.05837239211, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]]

# SolarPVUtil 'Unit Adoption Calculations'!B251:L298
conv_ref_funits_adopted_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 59.16952483163, -75.62640223557, -0.33768156367, -22.15920892112, -1.71009099271, -15.41714380040,
     -15.43313810117, -3.07011430874, -55.75969246529, -13.21605539049],
    [2016, 150.52159292976, -76.24855891557, -0.34297979401, -23.24591339780, -1.84510420765, -16.18366871191,
     -15.89405398012, -3.39192750636, -56.24733048614, -13.30746078097],
    [2017, 257.36122967139, -76.87071559558, -0.34827802435, -24.33261787447, -1.98011742258, -16.95019362342,
     -16.35496985906, -3.71374070399, -56.73496850699, -13.39886617146],
    [2018, 378.99298898654, -77.49287227559, -0.35357625469, -25.41932235115, -2.11513063752, -17.71671853493,
     -16.81588573801, -4.03555390161, -57.22260652784, -13.49027156194],
    [2019, 514.72142480523, -78.11502895560, -0.35887448503, -26.50602682782, -2.25014385245, -18.48324344644,
     -17.27680161696, -4.35736709924, -57.71024454869, -13.58167695243],
    [2020, 514.73678922371, -78.73718563561, -0.36417271537, -27.59273130450, -2.38515706739, -19.24976835795,
     -17.73771749591, -4.67918029686, -58.19788256953, -13.67308234291],
    [2021, 825.68654167325, -79.35934231562, -0.36947094570, -28.67943578117, -2.52017028232, -20.01629326946,
     -18.19863337485, -5.00099349449, -58.68552059038, -13.76448773340],
    [2022, 999.53233058261, -79.98149899563, -0.37476917604, -29.76614025785, -2.65518349726, -20.78281818097,
     -18.65954925380, -5.32280669212, -59.17315861123, -13.85589312388],
    [2023, 1184.69301171557, -80.60365567564, -0.38006740638, -30.85284473453, -2.79019671219, -21.54934309248,
     -19.12046513275, -5.64461988974, -59.66079663208, -13.94729851437],
    [2024, 1380.47313900213, -81.22581235565, -0.38536563672, -31.93954921120, -2.92520992713, -22.31586800399,
     -19.58138101170, -5.96643308737, -60.14843465293, -14.03870390485],
    [2025, 1433.94497468791, -81.84796903566, -0.39066386706, -33.02625368788, -3.06022314206, -23.08239291550,
     -20.04229689064, -6.28824628499, -60.63607267378, -14.13010929534],
    [2026, 1801.10994775612, -82.47012571567, -0.39596209740, -34.11295816455, -3.19523635700, -23.84891782701,
     -20.50321276959, -6.61005948262, -61.12371069462, -14.22151468583],
    [2027, 2024.57573708357, -83.09228239568, -0.40126032774, -35.19966264123, -3.33024957193, -24.61544273852,
     -20.96412864854, -6.93187268024, -61.61134871547, -14.31292007631],
    [2028, 2255.87918828469, -83.71443907569, -0.40655855808, -36.28636711790, -3.46526278687, -25.38196765003,
     -21.42504452749, -7.25368587787, -62.09898673632, -14.40432546680],
    [2029, 2494.32485528949, -84.33659575570, -0.41185678841, -37.37307159458, -3.60027600180, -26.14849256154,
     -21.88596040643, -7.57549907549, -62.58662475717, -14.49573085728],
    [2030, 2856.55316015211, -84.95875243571, -0.41715501875, -38.45977607125, -3.73528921674, -26.91501747306,
     -22.34687628538, -7.89731227312, -63.07426277802, -14.58713624777],
    [2031, 2989.86105243015, -85.58090911572, -0.42245324909, -39.54648054793, -3.87030243167, -27.68154238457,
     -22.80779216433, -8.21912547074, -63.56190079887, -14.67854163825],
    [2032, 3245.56069042605, -86.20306579573, -0.42775147943, -40.63318502461, -4.00531564661, -28.44806729608,
     -23.26870804327, -8.54093866837, -64.04953881971, -14.76994702874],
    [2033, 3505.62075994569, -86.82522247573, -0.43304970977, -41.71988950128, -4.14032886154, -29.21459220759,
     -23.72962392222, -8.86275186600, -64.53717684056, -14.86135241922],
    [2034, 3769.34581491907, -87.44737915574, -0.43834794011, -42.80659397796, -4.27534207648, -29.98111711910,
     -24.19053980117, -9.18456506362, -65.02481486141, -14.95275780971],
    [2035, 4036.04040927621, -88.06953583575, -0.44364617045, -43.89329845463, -4.41035529141, -30.74764203061,
     -24.65145568012, -9.50637826125, -65.51245288226, -15.04416320019],
    [2036, 4305.00909694713, -88.69169251576, -0.44894440079, -44.98000293131, -4.54536850635, -31.51416694212,
     -25.11237155906, -9.82819145887, -66.00009090311, -15.13556859068],
    [2037, 4575.55643186183, -89.31384919577, -0.45424263112, -46.06670740798, -4.68038172128, -32.28069185363,
     -25.57328743801, -10.15000465650, -66.48772892395, -15.22697398117],
    [2038, 4846.98696795034, -89.93600587578, -0.45954086146, -47.15341188466, -4.81539493622, -33.04721676514,
     -26.03420331696, -10.47181785412, -66.97536694480, -15.31837937165],
    [2039, 5118.60525914267, -90.55816255579, -0.46483909180, -48.24011636133, -4.95040815115, -33.81374167665,
     -26.49511919591, -10.79363105175, -67.46300496565, -15.40978476214],
    [2040, 5437.16953108051, -91.18031923580, -0.47013732214, -49.32682083801, -5.08542136609, -34.58026658816,
     -26.95603507485, -11.11544424937, -67.95064298650, -15.50119015262],
    [2041, 5659.62332255882, -91.80247591581, -0.47543555248, -50.41352531469, -5.22043458102, -35.34679149967,
     -27.41695095380, -11.43725744700, -68.43828100735, -15.59259554311],
    [2042, 5927.63220264268, -92.42463259582, -0.48073378282, -51.50022979136, -5.35544779596, -36.11331641118,
     -27.87786683275, -11.75907064462, -68.92591902820, -15.68400093359],
    [2043, 6193.04705355042, -93.04678927583, -0.48603201316, -52.58693426804, -5.49046101089, -36.87984132269,
     -28.33878271170, -12.08088384225, -69.41355704904, -15.77540632408],
    [2044, 6455.17242921204, -93.66894595584, -0.49133024350, -53.67363874471, -5.62547422583, -37.64636623420,
     -28.79969859064, -12.40269703988, -69.90119506989, -15.86681171456],
    [2045, 6713.31288355757, -94.29110263585, -0.49662847384, -54.76034322139, -5.76048744076, -38.41289114571,
     -29.26061446959, -12.72451023750, -70.38883309074, -15.95821710505],
    [2046, 6966.77297051701, -94.91325931586, -0.50192670417, -55.84704769806, -5.89550065570, -39.17941605722,
     -29.72153034854, -13.04632343513, -70.87647111159, -16.04962249553],
    [2047, 7214.85724402038, -95.53541599587, -0.50722493451, -56.93375217474, -6.03051387063, -39.94594096873,
     -30.18244622749, -13.36813663275, -71.36410913244, -16.14102788602],
    [2048, 7456.87025799770, -96.15757267588, -0.51252316485, -58.02045665141, -6.16552708557, -40.71246588024,
     -30.64336210643, -13.68994983038, -71.85174715329, -16.23243327651],
    [2049, 7692.11656637898, -96.77972935589, -0.51782139519, -59.10716112809, -6.30054030050, -41.47899079175,
     -31.10427798538, -14.01176302800, -72.33938517413, -16.32383866699],
    [2050, 7895.38590200891, -97.40188603589, -0.52311962553, -60.19386560477, -6.43555351544, -42.24551570326,
     -31.56519386433, -14.33357622563, -72.82702319498, -16.41524405748],
    [2051, 8139.52728207347, -98.02404271590, -0.52841785587, -61.28057008144, -6.57056673037, -43.01204061477,
     -32.02610974327, -14.65538942325, -73.31466121583, -16.50664944796],
    [2052, 8350.30079724671, -98.64619939591, -0.53371608621, -62.36727455812, -6.70557994531, -43.77856552628,
     -32.48702562222, -14.97720262088, -73.80229923668, -16.59805483845],
    [2053, 8551.52582254397, -99.26835607592, -0.53901431655, -63.45397903479, -6.84059316024, -44.54509043779,
     -32.94794150117, -15.29901581851, -74.28993725753, -16.68946022893],
    [2054, 8742.50691189525, -99.89051275593, -0.54431254688, -64.54068351147, -6.97560637518, -45.31161534930,
     -33.40885738012, -15.62082901613, -74.77757527838, -16.78086561942],
    [2055, 8922.54861923059, -100.51266943594, -0.54961077722, -65.62738798814, -7.11061959011, -46.07814026081,
     -33.86977325906, -15.94264221376, -75.26521329922, -16.87227100990],
    [2056, 9090.95549847998, -101.13482611595, -0.55490900756, -66.71409246482, -7.24563280505, -46.84466517233,
     -34.33068913801, -16.26445541138, -75.75285132007, -16.96367640039],
    [2057, 9247.03210357344, -101.75698279596, -0.56020723790, -67.80079694150, -7.38064601998, -47.61119008384,
     -34.79160501696, -16.58626860901, -76.24048934092, -17.05508179088],
    [2058, 9390.08298844099, -102.37913947597, -0.56550546824, -68.88750141817, -7.51565923492, -48.37771499535,
     -35.25252089591, -16.90808180663, -76.72812736177, -17.14648718136],
    [2059, 9519.41270701265, -103.00129615598, -0.57080369858, -69.97420589485, -7.65067244985, -49.14423990686,
     -35.71343677485, -17.22989500426, -77.21576538262, -17.23789257185],
    [2060, 9634.32581321841, -103.62345283599, -0.57610192892, -71.06091037152, -7.78568566479, -49.91076481837,
     -36.17435265380, -17.55170820188, -77.70340340347, -17.32929796233]]

# SolarPVUtil 'Unit Adoption Calculations'!AX251:BH298
conv_ref_annual_tot_iunits_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 0.01196107466, -0.01528781998, -0.00006826207, -0.00447946731, -0.00034569360, -0.00311656395,
     -0.00311979719, -0.00062062128, -0.01127177963, -0.00267161560],
    [2016, 0.03042782609, -0.01541358848, -0.00006933311, -0.00469914380, -0.00037298642, -0.00327151638,
     -0.00321297098, -0.00068567558, -0.01137035529, -0.00269009313],
    [2017, 0.05202537780, -0.01553935698, -0.00007040414, -0.00491882029, -0.00040027924, -0.00342646881,
     -0.00330614478, -0.00075072987, -0.01146893095, -0.00270857066],
    [2018, 0.07661314589, -0.01566512548, -0.00007147517, -0.00513849678, -0.00042757206, -0.00358142124,
     -0.00339931858, -0.00081578417, -0.01156750660, -0.00272704819],
    [2019, 0.10405054647, -0.01579089398, -0.00007254621, -0.00535817326, -0.00045486488, -0.00373637367,
     -0.00349249237, -0.00088083846, -0.01166608226, -0.00274552572],
    [2020, 0.10405365238, -0.01591666249, -0.00007361724, -0.00557784975, -0.00048215770, -0.00389132610,
     -0.00358566617, -0.00094589276, -0.01176465792, -0.00276400325],
    [2021, 0.16691190950, -0.01604243099, -0.00007468827, -0.00579752624, -0.00050945052, -0.00404627854,
     -0.00367883996, -0.00101094705, -0.01186323357, -0.00278248078],
    [2022, 0.20205470416, -0.01616819949, -0.00007575931, -0.00601720273, -0.00053674333, -0.00420123097,
     -0.00377201376, -0.00107600134, -0.01196180923, -0.00280095831],
    [2023, 0.23948479572, -0.01629396799, -0.00007683034, -0.00623687921, -0.00056403615, -0.00435618340,
     -0.00386518756, -0.00114105564, -0.01206038489, -0.00281943584],
    [2024, 0.27906160028, -0.01641973649, -0.00007790137, -0.00645655570, -0.00059132897, -0.00451113583,
     -0.00395836135, -0.00120610993, -0.01215896054, -0.00283791337],
    [2025, 0.28987089139, -0.01654550500, -0.00007897241, -0.00667623219, -0.00061862179, -0.00466608826,
     -0.00405153515, -0.00127116423, -0.01225753620, -0.00285639090],
    [2026, 0.36409301282, -0.01667127350, -0.00008004344, -0.00689590868, -0.00064591461, -0.00482104069,
     -0.00414470894, -0.00133621852, -0.01235611186, -0.00287486843],
    [2027, 0.40926645301, -0.01679704200, -0.00008111447, -0.00711558516, -0.00067320743, -0.00497599312,
     -0.00423788274, -0.00140127282, -0.01245468751, -0.00289334596],
    [2028, 0.45602427062, -0.01692281050, -0.00008218550, -0.00733526165, -0.00070050025, -0.00513094555,
     -0.00433105654, -0.00146632711, -0.01255326317, -0.00291182349],
    [2029, 0.50422588174, -0.01704857900, -0.00008325654, -0.00755493814, -0.00072779307, -0.00528589798,
     -0.00442423033, -0.00153138140, -0.01265183883, -0.00293030102],
    [2030, 0.57745005943, -0.01717434751, -0.00008432757, -0.00777461463, -0.00075508589, -0.00544085041,
     -0.00451740413, -0.00159643570, -0.01275041448, -0.00294877855],
    [2031, 0.60439814896, -0.01730011601, -0.00008539860, -0.00799429111, -0.00078237871, -0.00559580284,
     -0.00461057792, -0.00166148999, -0.01284899014, -0.00296725608],
    [2032, 0.65608763726, -0.01742588451, -0.00008646964, -0.00821396760, -0.00080967153, -0.00575075527,
     -0.00470375172, -0.00172654429, -0.01294756580, -0.00298573361],
    [2033, 0.70865858350, -0.01755165301, -0.00008754067, -0.00843364409, -0.00083696435, -0.00590570770,
     -0.00479692552, -0.00179159858, -0.01304614146, -0.00300421114],
    [2034, 0.76197040377, -0.01767742151, -0.00008861170, -0.00865332058, -0.00086425717, -0.00606066014,
     -0.00489009931, -0.00185665288, -0.01314471711, -0.00302268867],
    [2035, 0.81588251418, -0.01780319002, -0.00008968274, -0.00887299706, -0.00089154998, -0.00621561257,
     -0.00498327311, -0.00192170717, -0.01324329277, -0.00304116621],
    [2036, 0.87025433083, -0.01792895852, -0.00009075377, -0.00909267355, -0.00091884280, -0.00637056500,
     -0.00507644691, -0.00198676147, -0.01334186843, -0.00305964374],
    [2037, 0.92494526982, -0.01805472702, -0.00009182480, -0.00931235004, -0.00094613562, -0.00652551743,
     -0.00516962070, -0.00205181576, -0.01344044408, -0.00307812127],
    [2038, 0.97981474727, -0.01818049552, -0.00009289584, -0.00953202653, -0.00097342844, -0.00668046986,
     -0.00526279450, -0.00211687005, -0.01353901974, -0.00309659880],
    [2039, 1.03472217927, -0.01830626402, -0.00009396687, -0.00975170301, -0.00100072126, -0.00683542229,
     -0.00535596829, -0.00218192435, -0.01363759540, -0.00311507633],
    [2040, 1.09911970575, -0.01843203253, -0.00009503790, -0.00997137950, -0.00102801408, -0.00699037472,
     -0.00544914209, -0.00224697864, -0.01373617105, -0.00313355386],
    [2041, 1.14408857134, -0.01855780103, -0.00009610894, -0.01019105599, -0.00105530690, -0.00714532715,
     -0.00554231589, -0.00231203294, -0.01383474671, -0.00315203139],
    [2042, 1.19826636361, -0.01868356953, -0.00009717997, -0.01041073248, -0.00108259972, -0.00730027958,
     -0.00563548968, -0.00237708723, -0.01393332237, -0.00317050892],
    [2043, 1.25191977485, -0.01880933803, -0.00009825100, -0.01063040896, -0.00110989254, -0.00745523201,
     -0.00572866348, -0.00244214153, -0.01403189802, -0.00318898645],
    [2044, 1.30490822116, -0.01893510653, -0.00009932204, -0.01085008545, -0.00113718536, -0.00761018444,
     -0.00582183727, -0.00250719582, -0.01413047368, -0.00320746398],
    [2045, 1.35709111864, -0.01906087504, -0.00010039307, -0.01106976194, -0.00116447818, -0.00776513687,
     -0.00591501107, -0.00257225011, -0.01422904934, -0.00322594151],
    [2046, 1.40832788339, -0.01918664354, -0.00010146410, -0.01128943843, -0.00119177100, -0.00792008930,
     -0.00600818487, -0.00263730441, -0.01432762499, -0.00324441904],
    [2047, 1.45847793153, -0.01931241204, -0.00010253514, -0.01150911491, -0.00121906381, -0.00807504173,
     -0.00610135866, -0.00270235870, -0.01442620065, -0.00326289657],
    [2048, 1.50740067914, -0.01943818054, -0.00010360617, -0.01172879140, -0.00124635663, -0.00822999417,
     -0.00619453246, -0.00276741300, -0.01452477631, -0.00328137410],
    [2049, 1.55495554234, -0.01956394904, -0.00010467720, -0.01194846789, -0.00127364945, -0.00838494660,
     -0.00628770625, -0.00283246729, -0.01462335197, -0.00329985163],
    [2050, 1.59604628470, -0.01968971755, -0.00010574824, -0.01216814438, -0.00130094227, -0.00853989903,
     -0.00638088005, -0.00289752159, -0.01472192762, -0.00331832916],
    [2051, 1.64539927991, -0.01981548605, -0.00010681927, -0.01238782086, -0.00132823509, -0.00869485146,
     -0.00647405385, -0.00296257588, -0.01482050328, -0.00333680669],
    [2052, 1.68800698648, -0.01994125455, -0.00010789030, -0.01260749735, -0.00135552791, -0.00884980389,
     -0.00656722764, -0.00302763017, -0.01491907894, -0.00335528422],
    [2053, 1.72868447306, -0.02006702305, -0.00010896134, -0.01282717384, -0.00138282073, -0.00900475632,
     -0.00666040144, -0.00309268447, -0.01501765459, -0.00337376175],
    [2054, 1.76729115573, -0.02019279155, -0.00011003237, -0.01304685033, -0.00141011355, -0.00915970875,
     -0.00675357523, -0.00315773876, -0.01511623025, -0.00339223928],
    [2055, 1.80368645061, -0.02031856006, -0.00011110340, -0.01326652681, -0.00143740637, -0.00931466118,
     -0.00684674903, -0.00322279306, -0.01521480591, -0.00341071682],
    [2056, 1.83772977379, -0.02044432856, -0.00011217444, -0.01348620330, -0.00146469919, -0.00946961361,
     -0.00693992283, -0.00328784735, -0.01531338156, -0.00342919435],
    [2057, 1.86928054139, -0.02057009706, -0.00011324547, -0.01370587979, -0.00149199201, -0.00962456604,
     -0.00703309662, -0.00335290165, -0.01541195722, -0.00344767188],
    [2058, 1.89819816950, -0.02069586556, -0.00011431650, -0.01392555628, -0.00151928483, -0.00977951847,
     -0.00712627042, -0.00341795594, -0.01551053288, -0.00346614941],
    [2059, 1.92434207423, -0.02082163406, -0.00011538754, -0.01414523276, -0.00154657765, -0.00993447090,
     -0.00721944422, -0.00348301024, -0.01560910853, -0.00348462694],
    [2060, 1.94757167168, -0.02094740257, -0.00011645857, -0.01436490925, -0.00157387046, -0.01008942333,
     -0.00731261801, -0.00354806453, -0.01570768419, -0.00350310447]]

# OnshoreWind 'Unit Adoption Calculations'!B134:L181
soln_pds_funits_adopted_onshorewind_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 689.000000000000, 443.891000000000, 1.901000000000, 194.660000000000, 5.326000000000, 18.675000000000,
     157.379000000000, 33.455000000000, 230.075000000000, 183.892000000000],
    [2015, 908.852091292092, 7.979307763897, 8.139074822128, 267.105377199355, 10.548121943227, 19.796556813059,
     193.585193194663, 40.367846031734, 258.054136815553, 200.383500527664],
    [2016, 1118.924124296810, 18.289603021309, 18.442885924723, 317.716448448747, 16.383711165564, 27.229966343952,
     228.859473927792, 49.708580768335, 282.958747699733, 221.799500024898],
    [2017, 1336.742619087160, 28.822708213117, 28.969899047158, 369.095911898688, 23.824718159254, 36.340490138663,
     264.832505429901, 60.744386447915, 307.012853337278, 244.167420690858],
    [2018, 1562.065729353660, 39.570702379249, 39.712174211143, 421.275401154747, 32.833701457715, 47.086509090785,
     301.467234026338, 73.425072904995, 330.249417933141, 267.434822928226],
    [2019, 1794.651608786810, 50.525664559634, 50.661771438390, 474.286549822494, 43.373219594365, 59.426404093907,
     338.726606042452, 87.700449974095, 352.701405692269, 291.549267139683],
    [2020, 2034.258411077130, 61.679673794197, 61.810750750610, 528.160991507498, 55.405831102622, 73.318556041619,
     376.573567803594, 103.520327489735, 374.401780819616, 316.458313727912],
    [2021, 2280.644289915120, 73.024809122868, 73.151172169512, 582.930359815329, 68.894094515905, 88.721345827513,
     414.971065635111, 120.834515286435, 395.383507520130, 342.109523095594],
    [2022, 2533.567398991300, 84.553149585574, 84.675095716808, 638.626288351557, 83.800568367632, 105.593154345177,
     453.882045862354, 139.592823198715, 415.679549998763, 368.450455645410],
    [2023, 2792.785891996160, 96.256774222242, 96.374581414208, 695.280410721750, 100.087811191222, 123.892362488204,
     493.269454810670, 159.745061061095, 435.322872460465, 395.428671780044],
    [2024, 3058.057922620220, 108.127762072800, 108.241689283424, 752.924360531480, 117.718381520092, 143.577351150183,
     533.096238805409, 181.241038708096, 454.346439110187, 422.991731902175],
    [2025, 3329.141644553990, 120.158192177175, 120.268479346165, 811.589771386315, 136.654837887662, 164.606501224704,
     573.325344171921, 204.030565974237, 472.783214152879, 451.087196414487],
    [2026, 3605.795211487980, 132.340143575296, 132.447011624144, 871.308276891825, 156.859738827349, 186.938193605358,
     613.919717235553, 228.063452694039, 490.666161793492, 479.662625719661],
    [2027, 3887.776777112690, 144.665695307090, 144.769346139070, 932.111510653579, 178.295642872573, 210.530809185736,
     654.842304321656, 253.289508702021, 508.028246236976, 508.665580220378],
    [2028, 4174.844495118640, 157.126926412483, 157.227542912654, 994.031106277148, 200.925108556750, 235.342728859427,
     696.056051755578, 279.658543832704, 524.902431688282, 538.043620319321],
    [2029, 4466.756519196320, 169.715915931405, 169.813661966607, 1057.098697368100, 224.710694413300, 261.332333520023,
     737.523905862668, 307.120367920607, 541.321682352361, 567.744306419171],
    [2030, 4763.271003036270, 182.424742903783, 182.519763322640, 1121.345917532010, 249.614958975640, 288.458004061113,
     779.208812968275, 335.624790800251, 557.318962434163, 597.715198922610],
    [2031, 5064.146100328970, 195.245486369544, 195.337907002463, 1186.804400374440, 275.600460777190, 316.678121376288,
     821.073719397750, 365.121622306156, 572.927236138638, 627.903858232320],
    [2032, 5369.139964764930, 208.170225368615, 208.260153027788, 1253.505779500960, 302.629758351367, 345.951066359138,
     863.081571476439, 395.560672272843, 588.179467670738, 658.257844750982],
    [2033, 5678.010750034680, 221.191038940926, 221.278561420325, 1321.481688517140, 330.665410231590, 376.235219903254,
     905.195315529693, 426.891750534830, 603.108621235412, 688.724718881278],
    [2034, 5990.516609828710, 234.300006126402, 234.385192201784, 1390.763761028560, 359.669974951278, 407.488962902227,
     947.377897882861, 459.064666926638, 617.747661037612, 719.252041025891],
    [2035, 6306.415697837540, 247.489205964972, 247.572105393877, 1461.383630640780, 389.606011043848, 439.670676249646,
     989.592264861291, 492.029231282787, 632.129551282288, 749.787371587501],
    [2036, 6625.466167751670, 260.750717496563, 260.831361018314, 1533.372930959370, 420.436077042718, 472.738740839101,
     1031.801362790330, 525.735253437798, 646.287256174390, 780.278270968791],
    [2037, 6947.426173261610, 274.076619761103, 274.155019096807, 1606.763295589900, 452.122731481308, 506.651537564184,
     1073.968137995340, 560.132543226190, 660.253739918869, 810.672299572442],
    [2038, 7272.053868057880, 287.458991798520, 287.535139651065, 1681.586358137940, 484.628532893036, 541.367447318485,
     1116.055536801650, 595.170910482483, 674.061966720675, 840.917017801136],
    [2039, 7599.107405830970, 300.889912648741, 300.963782702799, 1757.873752209060, 517.916039811319, 576.844850995594,
     1158.026505534620, 630.800165041198, 687.744900784760, 870.959986057555],
    [2040, 7928.344940271400, 314.361461351693, 314.433008273721, 1835.657111408830, 551.947810769577, 613.042129489101,
     1199.843990519600, 666.970116736854, 701.335506316074, 900.748764744380],
    [2041, 8259.524625069690, 327.865716947305, 327.934876385541, 1914.968069342830, 586.686404301227, 649.917663692597,
     1241.470938081940, 703.630575403973, 714.866747519566, 930.230914264294],
    [2042, 8592.404613916320, 341.394758475504, 341.461447059970, 1995.838259616600, 622.094378939688, 687.429834499673,
     1282.870294546980, 740.731350877072, 728.371588600189, 959.353995019978],
    [2043, 8926.743060501820, 354.940664976218, 355.004780318718, 2078.299315835740, 658.134293218379, 725.537022803918,
     1324.005006240080, 778.222252990674, 741.882993762892, 988.065567414114],
    [2044, 9262.298118516700, 368.495515489374, 368.556936183497, 2162.382871605810, 694.768705670716, 764.197609498923,
     1364.838019486580, 816.053091579298, 755.433927212626, 1016.313191849380],
    [2045, 9598.827941651450, 382.051389054900, 382.109974676016, 2248.120560532370, 731.960174830120, 803.369975478279,
     1405.332280611840, 854.173676477463, 769.057353154341, 1044.044428728470],
    [2046, 9936.090683596600, 395.600364712723, 395.655955817988, 2335.544016221010, 769.671259230008, 843.012501635575,
     1445.450735941190, 892.533817519691, 782.786235792989, 1071.206838454050],
    [2047, 10273.844498042700, 409.134521502771, 409.186939631122, 2424.684872277270, 807.864517403799,
     883.083568864403, 1485.156331800000, 931.083324540500, 796.653539333519, 1097.747981428810],
    [2048, 10611.847538680100, 422.645938464972, 422.694986137129, 2515.574762306750, 846.502507884910,
     923.541558058352, 1524.412014513610, 969.772007374412, 810.692227980882, 1123.615418055430],
    [2049, 10949.857959199500, 436.126694639254, 436.172155357720, 2608.245319915000, 885.547789206761,
     964.344850111014, 1563.180730407370, 1008.549675855950, 824.935265940030, 1148.756708736600],
    [2050, 11287.633913291300, 449.568869065543, 449.610507314607, 2702.728178707600, 924.962919902769,
     1005.451825915980, 1601.425425806630, 1047.366139819620, 839.415617415911, 1173.119413874990],
    [2051, 11624.933554646000, 462.964540783767, 463.002102029498, 2799.054972290120, 964.710458506353,
     1046.820866366830, 1639.109047036740, 1086.171209099960, 854.166246613477, 1196.651093873280],
    [2052, 11961.515036954200, 476.305788833855, 476.338999524107, 2897.257334268110, 1004.752963550930,
     1088.410352357170, 1676.194540423040, 1124.914693531480, 869.220117737679, 1219.299309134160],
    [2053, 12297.136513906300, 489.584692255734, 489.613259820142, 2997.366898247170, 1045.052993569920,
     1130.178664780590, 1712.644852290890, 1163.546402948710, 884.610194993467, 1241.011620060320],
    [2054, 12631.556139192900, 502.793330089331, 502.816942939315, 3099.415297832850, 1085.573107096750,
     1172.084184530670, 1748.422928965630, 1202.016147186150, 900.369442585792, 1261.735587054420],
    [2055, 12964.532066504500, 515.923781374574, 515.942108903336, 3203.434166630720, 1126.275862664820,
     1214.085292501000, 1783.491716772620, 1240.273736078340, 916.530824719603, 1281.418770519150],
    [2056, 13295.822449531500, 528.968125151390, 528.980817733917, 3309.455138246360, 1167.123818807560,
     1256.140369585170, 1817.814162037200, 1278.268979459800, 933.127305599852, 1300.008730857210],
    [2057, 13625.185441964500, 541.918440459708, 541.925129452768, 3417.509846285330, 1208.079534058380,
     1298.207796676790, 1851.353211084720, 1315.951687165030, 950.191849431490, 1317.453028471250],
    [2058, 13952.379197494000, 554.766806339455, 554.767104081600, 3527.629924353200, 1249.105566950710,
     1340.245954669420, 1884.071810240530, 1353.271669028570, 967.757420419466, 1333.699223763980],
    [2059, 14277.161869810600, 567.505301830558, 567.498801642124, 3639.847006055540, 1290.164476017960,
     1382.213224456680, 1915.932905829980, 1390.178734884930, 985.856982768732, 1348.694877138060],
    [2060, 14599.291612604600, 580.126005972945, 580.112282156049, 3754.192724997930, 1331.218819793550,
     1424.067986932140, 1946.899444178430, 1426.622694568640, 1004.523500684240, 1362.387548996190]]

# OnshoreWind 'Unit Adoption Calculations'!AG135:AQ181
soln_pds_new_iunits_reqd_onshorewind_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2015, 0.077293447678, 0.000000000000, 0.002193121326, 0.025469637060, 0.001835942550, 0.000394305973,
     0.012729019237, 0.002430350787, 0.009836631232, 0.005797920437],
    [2016, 0.073855070453, 0.003624792752, 0.003622513116, 0.017793345356, 0.002051619375, 0.002613365410,
     0.012401386569, 0.003283924148, 0.008755719479, 0.007529227613],
    [2017, 0.076578495712, 0.003703126089, 0.003700984299, 0.018063489169, 0.002616036451, 0.003202988837,
     0.012647046530, 0.003879860609, 0.008456707164, 0.007863894746],
    [2018, 0.079216895011, 0.003778674653, 0.003776664022, 0.018344754416, 0.003167290223, 0.003777980226,
     0.012879679521, 0.004458151703, 0.008169284082, 0.008180125678],
    [2019, 0.081770268351, 0.003851438443, 0.003849552285, 0.018637141097, 0.003705380690, 0.004338339577,
     0.013099285545, 0.005018797429, 0.007893450232, 0.008477920410],
    [2020, 0.084238615731, 0.003921417459, 0.003919649088, 0.018940649211, 0.004230307852, 0.004884066890,
     0.013305864599, 0.005561797788, 0.007629205616, 0.008757278941],
    [2021, 0.086621937151, 0.003988611701, 0.003986954431, 0.019255278759, 0.004742071710, 0.005415162164,
     0.013499416686, 0.006087152779, 0.007376550231, 0.009018201271],
    [2022, 0.088920232612, 0.004053021170, 0.004051468314, 0.019581029741, 0.005240672263, 0.005931625400,
     0.013679941804, 0.006594862403, 0.007135484080, 0.009260687401],
    [2023, 0.091133502112, 0.004114645866, 0.004113190738, 0.019917902156, 0.005726109511, 0.006433456597,
     0.013847439953, 0.007084926660, 0.006906007161, 0.009484737329],
    [2024, 0.093261745653, 0.004173485787, 0.004172121701, 0.020265896005, 0.006198383455, 0.006920655756,
     0.014001911134, 0.007557345549, 0.006688119475, 0.009690351058],
    [2025, 0.095304963234, 0.004229540935, 0.004228261205, 0.020625011287, 0.006657494095, 0.007393222877,
     0.014143355346, 0.008012119071, 0.006481821022, 0.009877528585],
    [2026, 0.097263154855, 0.004282811309, 0.004281609249, 0.020995248003, 0.007103441429, 0.007851157960,
     0.014271772590, 0.008449247225, 0.006287111802, 0.010046269912],
    [2027, 0.099136320517, 0.004333296910, 0.004332165832, 0.021376606153, 0.007536225460, 0.008294461004,
     0.014387162866, 0.008868730012, 0.006103991814, 0.010196575038],
    [2028, 0.100924460219, 0.004380997737, 0.004379930956, 0.021769085736, 0.007955846185, 0.008723132010,
     0.014489526173, 0.009270567431, 0.005932461059, 0.010328443964],
    [2029, 0.102627573961, 0.004425913790, 0.004424904620, 0.022172686753, 0.008362303606, 0.009137170978,
     0.014578862511, 0.009654759483, 0.005772519536, 0.010441876689],
    [2030, 0.104245661743, 0.004468045070, 0.004467086824, 0.022587409203, 0.008755597723, 0.009536577907,
     0.014655171881, 0.010021306168, 0.005624167247, 0.010536873213],
    [2031, 0.105778723566, 0.004507391576, 0.004506477569, 0.023013253087, 0.009135728535, 0.009921352798,
     0.014718454283, 0.010370207485, 0.005487404190, 0.010613433537],
    [2032, 0.107226759428, 0.004543953308, 0.004543076853, 0.023450218405, 0.009502696042, 0.010291495651,
     0.014768709716, 0.010701463434, 0.005362230366, 0.010671557660],
    [2033, 0.108589769331, 0.004577730267, 0.004576884677, 0.023898305156, 0.009856500245, 0.010647006465,
     0.014805938180, 0.011015074017, 0.005248645774, 0.010711245582],
    [2034, 0.109867753274, 0.004608722452, 0.004607901042, 0.024357513341, 0.010197141143, 0.010987885241,
     0.014830139676, 0.011311039232, 0.005146650416, 0.010732497303],
    [2035, 0.111060711258, 0.004636929863, 0.004636125947, 0.024827842959, 0.010524618737, 0.011314131979,
     0.014841314204, 0.011589359079, 0.005056244290, 0.010735312824],
    [2036, 0.112168643281, 0.004662352501, 0.004661559391, 0.025309294011, 0.010838933026, 0.011625746679,
     0.014839461763, 0.011850033559, 0.004977427396, 0.010719692144],
    [2037, 0.113191549345, 0.004684990365, 0.004684201376, 0.025801866497, 0.011140084011, 0.011922729340,
     0.014824582354, 0.012093062672, 0.004910199736, 0.010685635264],
    [2038, 0.114129429449, 0.004704843455, 0.004704051901, 0.026305560416, 0.011428071691, 0.012205079963,
     0.014796675976, 0.012318446417, 0.004854561308, 0.010633142183],
    [2039, 0.192275731271, 0.004721911772, 0.006914232292, 0.052290012829, 0.013538838616, 0.012867104520,
     0.027484761867, 0.014956535582, 0.014647143344, 0.016360133338],
    [2040, 0.189605182231, 0.008360988067, 0.008357891687, 0.045139657911, 0.014016176512, 0.015339250503,
     0.027103168885, 0.016000201953, 0.013533771630, 0.018002075032],
    [2041, 0.193011409715, 0.008450820174, 0.008447839015, 0.045946859945, 0.014829091355, 0.016167328438,
     0.027281841562, 0.016768586057, 0.013213888585, 0.018228940482],
    [2042, 0.196247585280, 0.008535082733, 0.008532203424, 0.046776304846, 0.015615679588, 0.016966142297,
     0.027434460302, 0.017501679426, 0.012917184006, 0.018418933530],
    [2043, 0.199313708925, 0.008613775745, 0.008610984912, 0.047627992614, 0.016375941212, 0.017735692079,
     0.027561025105, 0.018199482061, 0.012643657892, 0.018572054178],
    [2044, 0.202209780650, 0.008686899210, 0.008684183481, 0.048501923249, 0.017109876226, 0.018475977785,
     0.027661535971, 0.018861993960, 0.012393310244, 0.018688302423],
    [2045, 0.204935800456, 0.008754453127, 0.008751799129, 0.049398096752, 0.017817484632, 0.019186999413,
     0.027735992900, 0.019489215125, 0.012166141061, 0.018767678268],
    [2046, 0.207491768342, 0.008816437497, 0.008813831858, 0.050316513121, 0.018498766429, 0.019868756965,
     0.027784395892, 0.020081145554, 0.011962150343, 0.018810181711],
    [2047, 0.209877684309, 0.008872852320, 0.008870281668, 0.051257172358, 0.019153721616, 0.020521250441,
     0.027806744947, 0.020637785249, 0.011781338091, 0.018815812753],
    [2048, 0.212093548357, 0.008923697595, 0.008921148557, 0.052220074462, 0.019782350194, 0.021144479840,
     0.027803040066, 0.021159134209, 0.011623704305, 0.018784571393],
    [2049, 0.214139360484, 0.008968973323, 0.008966432527, 0.053205219434, 0.020384652163, 0.021738445162,
     0.027773281247, 0.021645192435, 0.011489248983, 0.018716457632],
    [2050, 0.216015120693, 0.009008679504, 0.009006133577, 0.054212607272, 0.020960627523, 0.022303146408,
     0.027717468492, 0.022095959925, 0.011377972128, 0.018611471470],
    [2051, 0.217720828981, 0.009042816137, 0.009040251707, 0.055242237978, 0.021510276274, 0.022838583577,
     0.027635601799, 0.022511436681, 0.011289873737, 0.018469612907],
    [2052, 0.219256485350, 0.009071383223, 0.009068786917, 0.056294111551, 0.022033598416, 0.023344756669,
     0.027527681169, 0.022891622701, 0.011224953813, 0.018290881942],
    [2053, 0.220622089800, 0.009094380762, 0.009091739207, 0.057368227991, 0.022530593948, 0.023821665685,
     0.027393706603, 0.023236517987, 0.011183212353, 0.018075278576],
    [2054, 0.221817642330, 0.009111808754, 0.009109108578, 0.058464587299, 0.023001262872, 0.024269310624,
     0.027233678100, 0.023546122538, 0.011164649359, 0.017822802808],
    [2055, 0.222843142941, 0.009123667198, 0.009120895029, 0.059583189473, 0.023445605186, 0.024687691486,
     0.027047595659, 0.023820436354, 0.011169264831, 0.017533454640],
    [2056, 0.223698591632, 0.009129956094, 0.009127098560, 0.060724034515, 0.023863620891, 0.025076808272,
     0.026835459282, 0.024059459436, 0.011197058768, 0.017207234069],
    [2057, 0.224383988403, 0.009130675444, 0.009127719171, 0.061887122424, 0.024255309987, 0.025436660981,
     0.026597268968, 0.024263191782, 0.011248031170, 0.016844141098],
    [2058, 0.224899333255, 0.009125825246, 0.009122756863, 0.063072453200, 0.024620672474, 0.025767249614,
     0.026333024716, 0.024431633394, 0.011322182038, 0.016444175725],
    [2059, 0.225244626188, 0.009115405501, 0.009112211634, 0.064280026844, 0.024959708351, 0.026068574170,
     0.026042726528, 0.024564784270, 0.011419511372, 0.016007337951],
    [2060, 0.225419867201, 0.009099416209, 0.009096083486, 0.065509843355, 0.025272417620, 0.026340634649,
     0.025726374403, 0.024662644412, 0.011540019170, 0.015533627776]]

# Alternate Cement 'Unit Adoption Calculations'!B134:L181
soln_funits_adopted_altcement_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 222.222222, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 222.703192, 42.116996, 12.424431, 163.800714, 3.206397, 1.154654, 170.811140, 41.665041, 13.602438,
     16.646779],
    [2016, 609.148337, 117.977901, 27.112990, 412.849266, 33.775844, 17.432336, 325.612968, 65.175302, 13.669529,
     31.277073],
    [2017, 934.565664, 194.599717, 42.254483, 633.389025, 46.440035, 17.882404, 330.589587, 92.201734, 13.878352,
     46.823306],
    [2018, 975.119605, 242.609222, 57.753094, 609.424282, 46.986309, 18.346698, 340.504586, 93.047453, 14.209510,
     63.164601],
    [2019, 973.006043, 237.419406, 73.534464, 595.533069, 47.693902, 18.825203, 354.236377, 91.604222, 14.646482,
     63.119003],
    [2020, 981.751223, 234.366686, 89.540626, 589.967696, 48.558311, 19.317904, 370.886844, 91.658279, 15.175174,
     63.964271],
    [2021, 999.595665, 233.157862, 105.726194, 591.311421, 49.575399, 19.824789, 389.733827, 93.041111, 15.783532,
     65.667799],
    [2022, 1014.465706, 233.544814, 111.422252, 598.411428, 50.741368, 20.345845, 410.194305, 95.613202, 16.461227,
     68.098278],
    [2023, 1030.233806, 235.317091, 111.656705, 610.326224, 52.052729, 20.881058, 431.795728, 99.258692, 17.199388,
     71.149521],
    [2024, 1052.387957, 238.295807, 112.871265, 626.284184, 53.506284, 21.430418, 454.153629, 103.881081, 17.990386,
     74.735321],
    [2025, 1079.978053, 242.328605, 114.905658, 645.650774, 55.099103, 21.993913, 476.954050, 109.399770, 18.827644,
     78.785427],
    [2026, 1050.177794, 235.240633, 110.903042, 627.052313, 54.876971, 22.104835, 463.082817, 108.710778, 18.496449,
     77.519524],
    [2027, 1024.285761, 228.969865, 107.470799, 610.925810, 54.705410, 22.213877, 450.302625, 108.368217, 18.199765,
     76.501339],
    [2028, 1001.775069, 223.424048, 104.523646, 596.924133, 54.582215, 22.321027, 438.456091, 108.327800, 17.934090,
     75.694575],
    [2029, 982.205642, 218.524180, 101.991340, 584.758465, 54.505379, 22.426278, 427.412820, 108.552179, 17.696392,
     75.069237],
    [2030, 965.209294, 214.202593, 99.815894, 574.188102, 54.473085, 22.529619, 417.064573, 109.009827, 17.484047,
     74.600485],
    [2031, 949.210997, 210.388857, 97.549362, 563.837209, 54.754525, 22.681044, 402.321376, 109.589118, 17.311451,
     74.067716],
    [2032, 935.219104, 207.045937, 95.552062, 554.713167, 55.077392, 22.830545, 388.108403, 110.352578, 17.159980,
     73.653835],
    [2033, 923.017422, 204.131586, 93.791163, 546.676188, 55.440368, 22.978116, 374.363452, 111.281265, 17.027947,
     73.344656],
    [2034, 912.425429, 201.609910, 92.239540, 539.609942, 55.842287, 23.123750, 361.034921, 112.359261, 16.913910,
     73.128433],
    [2035, 903.293046, 199.450591, 90.874864, 533.418024, 56.282125, 23.267442, 348.080162, 113.573258, 16.816640,
     72.995475],
    [2036, 895.496395, 197.628251, 89.678868, 528.021095, 56.758994, 23.409187, 335.464166, 114.912214, 16.735104,
     72.937838],
    [2037, 888.934378, 196.121914, 88.636765, 523.354579, 57.272138, 23.548981, 323.158501, 116.367078, 16.668440,
     72.949079],
    [2038, 883.525934, 194.914581, 87.736781, 519.366823, 57.820929, 23.686820, 311.140469, 117.930564, 16.615949,
     73.024061],
    [2039, 879.207875, 193.992878, 86.969792, 516.017643, 58.404859, 23.822702, 299.392442, 119.596974, 16.577076,
     73.158798],
    [2040, 875.933203, 193.346783, 86.329048, 513.277204, 59.023543, 23.956625, 287.901349, 121.362061, 16.551405,
     73.350337],
    [2041, 873.969055, 193.234283, 85.809960, 511.125182, 59.711043, 24.088587, 285.901349, 123.317061, 16.538651,
     73.650337],
    [2042, 872.699055, 193.121783, 85.409960, 509.550182, 60.398543, 24.218587, 283.901349, 125.272061, 16.538651,
     73.950337],
    [2043, 872.119747, 193.009283, 85.128413, 508.549383, 61.086043, 24.346625, 281.901349, 127.227061, 16.551365,
     74.250337],
    [2044, 872.238009, 192.896783, 84.966583, 508.128399, 61.773543, 24.472701, 279.901349, 129.182061, 16.576874,
     74.550337],
    [2045, 873.071140, 192.784283, 84.927648, 508.301349, 62.461043, 24.596817, 277.901349, 131.137061, 16.615377,
     74.850337],
    [2046, 871.801140, 192.671783, 84.527648, 506.726349, 63.148543, 24.726817, 275.901349, 133.092061, 16.615377,
     75.150337],
    [2047, 870.531140, 192.559283, 84.127648, 505.151349, 63.836043, 24.856817, 273.901349, 135.047061, 16.615377,
     75.450337],
    [2048, 869.261140, 192.446783, 83.727648, 503.576349, 64.523543, 24.986817, 271.901349, 137.002061, 16.615377,
     75.750337],
    [2049, 867.991140, 192.334283, 83.327648, 502.001349, 65.211043, 25.116817, 269.901349, 138.957061, 16.615377,
     76.050337],
    [2050, 866.721140, 192.221783, 82.927648, 500.426349, 65.898543, 25.246817, 267.901349, 140.912061, 16.615377,
     76.350337],
    [2051, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# Alternative Cement 'Unit Adoption Calculations'!AG134:AQ181
soln_new_iunits_reqd_altcement_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2015, 222.703192, 42.116996, 12.424431, 163.800714, 3.206397, 1.154654, 170.811140, 41.665041, 13.602438,
     16.646779],
    [2016, 609.148337, 117.977901, 27.112990, 412.849266, 33.775844, 17.432336, 325.612968, 65.175302, 13.669529,
     31.277073],
    [2017, 934.565664, 194.599717, 42.254483, 633.389025, 46.440035, 17.882404, 330.589587, 92.201734, 13.878352,
     46.823306],
    [2018, 975.119605, 242.609222, 57.753094, 609.424282, 46.986309, 18.346698, 340.504586, 93.047453, 14.209510,
     63.164601],
    [2019, 973.006043, 237.419406, 73.534464, 595.533069, 47.693902, 18.825203, 354.236377, 91.604222, 14.646482,
     63.119003],
    [2020, 981.751223, 234.366686, 89.540626, 589.967696, 48.558311, 19.317904, 370.886844, 91.658279, 15.175174,
     63.964271],
    [2021, 999.595665, 233.157862, 105.726194, 591.311421, 49.575399, 19.824789, 389.733827, 93.041111, 15.783532,
     65.667799],
    [2022, 1014.465706, 233.544814, 111.422252, 598.411428, 50.741368, 20.345845, 410.194305, 95.613202, 16.461227,
     68.098278],
    [2023, 1030.233806, 235.317091, 111.656705, 610.326224, 52.052729, 20.881058, 431.795728, 99.258692, 17.199388,
     71.149521],
    [2024, 1052.387957, 238.295807, 112.871265, 626.284184, 53.506284, 21.430418, 454.153629, 103.881081, 17.990386,
     74.735321],
    [2025, 1079.978053, 242.328605, 114.905658, 645.650774, 55.099103, 21.993913, 476.954050, 109.399770, 18.827644,
     78.785427],
    [2026, 1050.177794, 235.240633, 110.903042, 627.052313, 54.876971, 22.104835, 463.082817, 108.710778, 18.496449,
     77.519524],
    [2027, 1024.285761, 228.969865, 107.470799, 610.925810, 54.705410, 22.213877, 450.302625, 108.368217, 18.199765,
     76.501339],
    [2028, 1001.775069, 223.424048, 104.523646, 596.924133, 54.582215, 22.321027, 438.456091, 108.327800, 17.934090,
     75.694575],
    [2029, 982.205642, 218.524180, 101.991340, 584.758465, 54.505379, 22.426278, 427.412820, 108.552179, 17.696392,
     75.069237],
    [2030, 965.209294, 214.202593, 99.815894, 574.188102, 54.473085, 22.529619, 417.064573, 109.009827, 17.484047,
     74.600485],
    [2031, 949.210997, 210.388857, 97.549362, 563.837209, 54.754525, 22.681044, 402.321376, 109.589118, 17.311451,
     74.067716],
    [2032, 935.219104, 207.045937, 95.552062, 554.713167, 55.077392, 22.830545, 388.108403, 110.352578, 17.159980,
     73.653835],
    [2033, 923.017422, 204.131586, 93.791163, 546.676188, 55.440368, 22.978116, 374.363452, 111.281265, 17.027947,
     73.344656],
    [2034, 912.425429, 201.609910, 92.239540, 539.609942, 55.842287, 23.123750, 361.034921, 112.359261, 16.913910,
     73.128433],
    [2035, 903.293046, 199.450591, 90.874864, 533.418024, 56.282125, 23.267442, 348.080162, 113.573258, 16.816640,
     72.995475],
    [2036, 895.496395, 197.628251, 89.678868, 528.021095, 56.758994, 23.409187, 335.464166, 114.912214, 16.735104,
     72.937838],
    [2037, 888.934378, 196.121914, 88.636765, 523.354579, 57.272138, 23.548981, 323.158501, 116.367078, 16.668440,
     72.949079],
    [2038, 883.525934, 194.914581, 87.736781, 519.366823, 57.820929, 23.686820, 311.140469, 117.930564, 16.615949,
     73.024061],
    [2039, 879.207875, 193.992878, 86.969792, 516.017643, 58.404859, 23.822702, 299.392442, 119.596974, 16.577076,
     73.158798],
    [2040, 875.933203, 193.346783, 86.329048, 513.277204, 59.023543, 23.956625, 287.901349, 121.362061, 16.551405,
     73.350337],
    [2041, 873.969055, 193.234283, 85.809960, 511.125182, 59.711043, 24.088587, 285.901349, 123.317061, 16.538651,
     73.650337],
    [2042, 872.699055, 193.121783, 85.409960, 509.550182, 60.398543, 24.218587, 283.901349, 125.272061, 16.538651,
     73.950337],
    [2043, 872.119747, 193.009283, 85.128413, 508.549383, 61.086043, 24.346625, 281.901349, 127.227061, 16.551365,
     74.250337],
    [2044, 872.238009, 192.896783, 84.966583, 508.128399, 61.773543, 24.472701, 279.901349, 129.182061, 16.576874,
     74.550337],
    [2045, 873.071140, 192.784283, 84.927648, 508.301349, 62.461043, 24.596817, 277.901349, 131.137061, 16.615377,
     74.850337],
    [2046, 871.801140, 192.671783, 84.527648, 506.726349, 63.148543, 24.726817, 275.901349, 133.092061, 16.615377,
     75.150337],
    [2047, 870.531140, 192.559283, 84.127648, 505.151349, 63.836043, 24.856817, 273.901349, 135.047061, 16.615377,
     75.450337],
    [2048, 869.261140, 192.446783, 83.727648, 503.576349, 64.523543, 24.986817, 271.901349, 137.002061, 16.615377,
     75.750337],
    [2049, 867.991140, 192.334283, 83.327648, 502.001349, 65.211043, 25.116817, 269.901349, 138.957061, 16.615377,
     76.050337],
    [2050, 866.721140, 192.221783, 82.927648, 500.426349, 65.898543, 25.246817, 267.901349, 140.912061, 16.615377,
     76.350337],
    [2051, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2052, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2053, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2054, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2055, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2056, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2057, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2058, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2059, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2060, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# LEDS Commercial 'Unit Adoption Calculations'!B134:L181
soln_pds_funits_adopted_leds_commercial_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 2.05593864030338, 1.20353956168215, 0.17104652142369, 0.54208947982419, 0.15340928478054, 0.12392820164126,
     0.32342057805813, 0.07626534974849, 0.39542396445037, 0.84472440562913],
    [2015, 3.81566580389025, 8.77629136597486, 1.65751918249442, 4.45494937975652, 2.59696306568176, 1.45440735877370,
     2.86283553030392, 1.32627533425510, 3.03024368276945, 6.62706467185556],
    [2016, 8.79053380644722, 10.58332553982170, 1.94030758267108, 5.22074482572912, 2.94371637832498, 1.67260433152741,
     3.48288923720094, 1.65507505361876, 3.60593567837457, 7.82862052809416],
    [2017, 13.78270640645570, 12.41130659721250, 2.20938568585493, 5.95592481907978, 3.24131304127593, 1.87034672524930,
     4.11341953426801, 1.99331295940846, 4.17541844876660, 9.00256940963803],
    [2018, 18.78607658964190, 14.25833387135090, 2.46527412180902, 6.66339315269597, 3.49296525972354, 2.04905700433178,
     4.75432033788329, 2.34082289719569, 4.73869942630316, 10.14903728284640],
    [2019, 23.79453734173190, 16.12250669544030, 2.70849352029638, 7.34605361946515, 3.70188523885672, 2.21015763316730,
     5.40548556442496, 2.69743871255192, 5.29578604334186, 11.26815011407840],
    [2020, 28.80198164845180, 18.00192440268440, 2.93956451108004, 8.00681001227479, 3.87128518386439, 2.35507107614829,
     6.06680913027120, 3.06299425104863, 5.84668573224032, 12.36003386969330],
    [2021, 33.80230249552770, 19.89468632628670, 3.15900772392303, 8.64856612401237, 4.00437729993547, 2.48521979766717,
     6.73818495180019, 3.43732335825730, 6.39140592535616, 13.42481451605020],
    [2022, 38.78939286868590, 21.79889179945080, 3.36734378858839, 9.27422574756535, 4.10437379225889, 2.60202626211637,
     7.41950694539008, 3.82025987974941, 6.92995405504699, 14.46261801950840],
    [2023, 43.75714575365240, 23.71264015538020, 3.56509333483916, 9.88669267582120, 4.17448686602355, 2.70691293388832,
     8.11066902741908, 4.21163766109644, 7.46233755367043, 15.47357034642700],
    [2024, 48.69945413615340, 25.63403072727840, 3.75277699243836, 10.48887070166740, 4.21792872641839,
     2.80130227737547, 8.81156511426534, 4.61129054786987, 7.98856385358410, 16.45779746316540],
    [2025, 53.61021100191490, 27.56116284834900, 3.93091539114904, 11.08366361799140, 4.23791157863231,
     2.88661675697023, 9.52208912230705, 5.01905238564119, 8.50864038714562, 17.41542533608250],
    [2026, 58.48330933666320, 29.49213585179560, 4.10002916073422, 11.67397521768070, 4.23764762785424,
     2.96427883706503, 10.24213496792240, 5.43475701998186, 9.02257458671260, 18.34657993153770],
    [2027, 63.31264212612430, 31.42504907082170, 4.26063893095694, 12.26270929362270, 4.22034907927310,
     3.03571098205231, 10.97159656748950, 5.85823829646336, 9.53037388464266, 19.25138721589020],
    [2028, 68.09210235602450, 33.35800183863080, 4.41326533158023, 12.85276963870490, 4.18922813807781,
     3.10233565632450, 11.71036783738660, 6.28933006065719, 10.03204571329340, 20.12997315549910],
    [2029, 72.81558301208970, 35.28909348842660, 4.55842899236713, 13.44706004581490, 4.14749700945728,
     3.16557532427403, 12.45834269399180, 6.72786615813481, 10.52759750502250, 20.98246371672360],
    [2030, 77.47697708004630, 37.21642335341250, 4.69665054308067, 14.04848430783990, 4.09836789860044,
     3.22685245029332, 13.21541505368340, 7.17368043446772, 11.01703669218750, 21.80898486592300],
    [2031, 82.07017754562020, 39.13809076679220, 4.82845061348389, 14.65994621766760, 4.04505301069620,
     3.28758949877481, 13.98147883283940, 7.62660673522737, 11.50037070714600, 22.60966256945640],
    [2032, 86.58907739453760, 41.05219506176910, 4.95434983333982, 15.28434956818540, 3.99076455093349,
     3.34920893411094, 14.75642794783820, 8.08647890598527, 11.97760698225580, 23.38462279368300],
    [2033, 91.02756961252470, 42.95683557154680, 5.07486883241149, 15.92459815228080, 3.93871472450122,
     3.41313322069412, 15.54015631505780, 8.55313079231288, 12.44875294987430, 24.13399150496210],
    [2034, 95.37954718530750, 44.85011162932890, 5.19052824046193, 16.58359576284120, 3.89211573658832,
     3.48078482291679, 16.33255785087640, 9.02639623978168, 12.91381604235920, 24.85789466965270],
    [2035, 99.63890309861230, 46.73012256831890, 5.30184868725419, 17.26424619275410, 3.85417979238370,
     3.55358620517138, 17.13352647167210, 9.50610909396316, 13.37280369206810, 25.55645825411420],
    [2036, 103.79953033816500, 48.59496772172040, 5.40935080255130, 17.96945323490690, 3.82811909707628,
     3.63295983185032, 17.94295609382330, 9.99210320042880, 13.82572333135860, 26.22980822470580],
    [2037, 107.85532188969200, 50.44274642273690, 5.51355521611628, 18.70212068218720, 3.81714585585497,
     3.72032816734605, 18.76074063370800, 10.48421240475010, 14.27258239258840, 26.87807054778650],
    [2038, 111.80017073892000, 52.27155800457200, 5.61498255771218, 19.46515232748240, 3.82447227390871,
     3.81711367605099, 19.58677400770450, 10.98227055249840, 14.71338830811510, 27.50137118971570],
    [2039, 115.62796987157300, 54.07950180042920, 5.71415345710202, 20.26145196368000, 3.85331055642641,
     3.92473882235756, 20.42095013219080, 11.48611148924540, 15.14814851029630, 28.09983611685240],
    [2040, 119.33261227338000, 55.86467714351210, 5.81158854404885, 21.09392338366740, 3.90687290859699,
     4.04462607065822, 21.26316292354530, 11.99556906056250, 15.57687043148950, 28.67359129555600],
    [2041, 122.90799093006500, 57.62518336702420, 5.90780844831569, 21.96547038033210, 3.98837153560937,
     4.17819788534537, 22.11330629814590, 12.51047711202110, 15.99956150405250, 29.22276269218560],
    [2042, 126.34799882735500, 59.35911980416910, 6.00333379966558, 22.87899674656160, 4.10101864265246,
     4.32687673081146, 22.97127417237100, 13.03066948919270, 16.41622916034280, 29.74747627310040],
    [2043, 129.64652895097600, 61.06458578815030, 6.09868522786156, 23.83740627524340, 4.24802643491519,
     4.49208507144891, 23.83696046259870, 13.55598003764880, 16.82688083271810, 30.24785800465950],
    [2044, 132.79747428665400, 62.73968065217140, 6.19438336266665, 24.84360275926490, 4.43260711758648,
     4.67524537165016, 24.71025908520720, 14.08624260296100, 17.23152395353590, 30.72403385322230],
    [2045, 135.79472782011500, 64.38250372943600, 6.29094883384390, 25.90048999151350, 4.65797289585525,
     4.87778009580763, 25.59106395657460, 14.62129103070060, 17.63016595515400, 31.17612978514790],
    [2046, 138.63218253708600, 65.99115435314750, 6.38890227115633, 27.01097176487690, 4.92733597491040,
     5.10111170831376, 26.47926899307920, 15.16095916643910, 18.02281426992980, 31.60427176679540],
    [2047, 141.30373142329200, 67.56373185650960, 6.48876430436698, 28.17795187224230, 5.24390855994087,
     5.34666267356097, 27.37476811109910, 15.70508085574810, 18.40947633022110, 32.00858576452420],
    [2048, 143.80326746446000, 69.09833557272580, 6.59105556323888, 29.40433410649740, 5.61090285613558,
     5.61585545594170, 28.27745522701240, 16.25348994419900, 18.79015956838540, 32.38919774469330],
    [2049, 146.12468364631500, 70.59306483499960, 6.69629667753507, 30.69302226052950, 6.03153106868344,
     5.91011251984838, 29.18722425719740, 16.80602027736330, 19.16487141678030, 32.74623367366200],
    [2050, 148.26187295458500, 72.04601897653460, 6.80500827701858, 32.04692012722610, 6.50900540277337,
     6.23085632967343, 30.10396911803220, 17.36250570081240, 19.53361930776360, 33.07981951778950],
    [2051, 150.20872837499400, 73.45529733053430, 6.91771099145245, 33.46893149947480, 7.04653806359429,
     6.57950934980930, 31.02758372589510, 17.92278006011790, 19.89641067369270, 33.39008124343500],
    [2052, 151.95914289327000, 74.81899923020240, 7.03492545059971, 34.96196017016290, 7.64734125633512,
     6.95749404464840, 31.95796199716410, 18.48667720085130, 20.25325294692530, 33.67714481695760],
    [2053, 153.50700949513800, 76.13522400874230, 7.15717228422339, 36.52890993217800, 8.31462718618479,
     7.36623287858317, 32.89499784821750, 19.05403096858390, 20.60415355981910, 33.94113620471660],
    [2054, 154.84622116632400, 77.40207099935760, 7.28497212208653, 38.17268457840740, 9.05160805833220,
     7.80714831600604, 33.83858519543340, 19.62467520888730, 20.94911994473160, 34.18218137307120],
    [2055, 155.97067089255500, 78.61763953525180, 7.41884559395216, 39.89618790173880, 9.86149607796628,
     8.28166282130944, 34.78861795519000, 20.19844376733300, 21.28815953402040, 34.40040628838060],
    [2056, 156.87425165955700, 79.78002894962850, 7.55931332958332, 41.70232369505950, 10.74750345027600,
     8.79119885888579, 35.74499004386550, 20.77517048949240, 21.62127976004330, 34.59593691700390],
    [2057, 157.55085645305500, 80.88733857569130, 7.70689595874303, 43.59399575125700, 11.71284238045010,
     9.33717889312754, 36.70759537783800, 21.35468922093710, 21.94848805515770, 34.76889922530030],
    [2058, 157.99437825877700, 81.93766774664370, 7.86211411119434, 45.57410786321880, 12.76072507367770,
     9.92102538842711, 37.67632787348580, 21.93683380723840, 22.26979185172130, 34.91941917962920],
    [2059, 158.19871006244700, 82.92911579568930, 8.02548841670028, 47.64556382383240, 13.89436373514770,
     10.54416080917690, 38.65108144718700, 22.52143809396800, 22.58519858209180, 35.04762274634950],
    [2060, 158.15774484979300, 83.85978205603160, 8.19753950502388, 49.81126742598520, 15.11697057004890,
     11.20800761976940, 39.63175001531980, 23.10833592669720, 22.89471567862670, 35.15363589182070]]

# LEDS Commercial 'Unit Adoption Calculations'!AG134:AQ181
soln_pds_new_iunits_reqd_leds_commercial_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2015, 0.000483993334044822, 0.002082800941813530, 0.000408837730123832, 0.001076188484104770, 0.000672072219948903,
     0.000365933456312126, 0.000698437766202070, 0.000343801307674025, 0.000724677783274633, 0.001590368212722310],

    [2016, 0.001368281970531500, 0.000497004599707586, 0.000077777796162289, 0.000210623498211588, 0.000095370632078666,
     0.000060012644293277, 0.000170538858010375, 0.000090432696443379, 0.000158337663986447, 0.000330474539994389],

    [2017, 0.001373041407101090, 0.000502765806452636, 0.000074006931854685, 0.000202203059353565, 0.000081850643714937,
     0.000054386840414727, 0.000173420327314676, 0.000093028564376887, 0.000156629885829182, 0.000322881549443424],

    [2018, 0.001376121177492520, 0.000508004255989209, 0.000070379260957985, 0.000194581276349736, 0.000069214136569882,
     0.000049152269505752, 0.000176272619501707, 0.000095578733387578, 0.000154924151859003, 0.000315323204534935],

    [2019, 0.001377521281705780, 0.000512719948317301, 0.000066894783472188, 0.000187758149200099, 0.000057461110643503,
     0.000044308931566352, 0.000179095734571468, 0.000098083203475454, 0.000153220462075911, 0.000307799505268922],

    [2020, 0.001377241719740890, 0.000516912883436915, 0.000063553499397296, 0.000181733677904656, 0.000046591565935798,
     0.000039856826596527, 0.000181889672523960, 0.000100541974640513, 0.000151518816479905, 0.000300310451645386],

    [2021, 0.001375282491597830, 0.000520583061348051, 0.000060355408733307, 0.000176507862463406, 0.000036605502446769,
     0.000035795954596278, 0.000184654433359182, 0.000102955046882757, 0.000149819215070984, 0.000292856043664325],

    [2022, 0.001371643597276610, 0.000523730482050707, 0.000057300511480221, 0.000172080702876351, 0.000027502920176414,
     0.000032126315565604, 0.000187390017077134, 0.000105322420202184, 0.000148121657849150, 0.000285436281325743],

    [2023, 0.001366325036777230, 0.000526355145544883, 0.000054388807638040, 0.000168452199143489, 0.000019283819124734,
     0.000028847909504506, 0.000190096423677817, 0.000107644094598796, 0.000146426144814402, 0.000278051164629633],

    [2024, 0.001359326810099690, 0.000528457051830579, 0.000051620297206761, 0.000165622351264818, 0.000011948199291730,
     0.000025960736412983, 0.000192773653161232, 0.000109920070072591, 0.000144732675966740, 0.000270700693576002],

    [2025, 0.001350648917243990, 0.000530036200907801, 0.000048994980186387, 0.000163591159240343, 0.000005496060677400,
     0.000023464796291035, 0.000195421705527375, 0.000112150346623571, 0.000143041251306164, 0.000263384868164847],

    [2026, 0.001340291358210130, 0.000531092592776539, 0.000046512856576916, 0.000162358623070060, 0.000000000000000000,
     0.000021360089138662, 0.000198040580776250, 0.000114334924251735, 0.000141351870832675, 0.000256103688396166],

    [2027, 0.001328254132998100, 0.000531626227436801, 0.000044173926378349, 0.000161924742753971, 0.000000000000000000,
     0.000019646614955865, 0.000200630278907855, 0.000116473802957083, 0.000139664534546271, 0.000248857154269966],

    [2028, 0.001314537241607910, 0.000531637104888580, 0.000041978189590685, 0.000162289518292075, 0.000000000000000000,
     0.000018324373742643, 0.000203190799922189, 0.000118566982739614, 0.000137979242446953, 0.000241645265786237],

    [2029, 0.001299140684039570, 0.000531125225131886, 0.000039925646213925, 0.000163452949684372, 0.000000000000000000,
     0.000017393365498997, 0.000205722143819255, 0.000120614463599330, 0.000136295994534723, 0.000234468022944988],

    [2030, 0.001766057794337880, 0.002612891529980240, 0.000446854026371901, 0.001241603521035630, 0.000672072219948903,
     0.000382787046537052, 0.000906662076801121, 0.000466417553210255, 0.000859292574084210, 0.001817693638468530],

    [2031, 0.002631590540899900, 0.001025537793700640, 0.000114027935855405, 0.000378799278243136, 0.000095370632078666,
     0.000076717692213707, 0.000381236158271953, 0.000215005024993692, 0.000291273295257966, 0.000550692014184303],

    [2032, 0.002615914421366650, 0.001029218849063550, 0.000108634108403752, 0.000373938238339991, 0.000081850643714937,
     0.000071334579000235, 0.000386561440121511, 0.000219511277018468, 0.000287888401749728, 0.000536025717719518],

    [2033, 0.002596878969477080, 0.001031854390009510, 0.000103526667773907, 0.000370674510145232, 0.000069214136569882,
     0.000066733931725915, 0.000391828367736528, 0.000223926131197611, 0.000284507596615662, 0.000521428712539682],

    [2034, 0.002574484185231200, 0.001033444416538510, 0.000098705613965869, 0.000369008093658860, 0.000057461110643503,
     0.000062915750390746, 0.000397036941117008, 0.000228249587531124, 0.000281130879855770, 0.000506900998644799],

    [2035, 0.002548730068628990, 0.001033988928650550, 0.000094170946979638, 0.000368938988880876, 0.000000000000000000,
     0.000059880034994726, 0.000402187160262948, 0.000232481646019002, 0.000277758251470049, 0.000492442576034871],

    [2036, 0.002519616619670450, 0.001033487926345640, 0.000089922666815215, 0.000370467195811275, 0.000000000000000000,
     0.000057626785537858, 0.000407279025174349, 0.000236622306661250, 0.000274389711458500, 0.000478053444709892],

    [2037, 0.002487143838355600, 0.001031941409623770, 0.000085960773472598, 0.000373592714450066, 0.000000000000000000,
     0.000056156002020140, 0.000412312535851209, 0.000240671569457865, 0.000271025259821124, 0.000463733604669868],

    [2038, 0.002451311724684420, 0.001029349378484930, 0.000082285266951789, 0.000378315544797242, 0.000002015049590533,
     0.000055467684441573, 0.000417287692293533, 0.000244629434408850, 0.000267664896557920, 0.000449483055914794],

    [2039, 0.002412120278656910, 0.001025711832929140, 0.000078896147252788, 0.000384635686852802, 0.000007931648037652,
     0.000055561832802157, 0.000422204494501317, 0.000248495901514200, 0.000264308621668889, 0.000435301798444677],

    [2040, 0.002369569500273110, 0.001021028772956400, 0.000075793414375594, 0.000392553140616750, 0.000014731727703448,
     0.000056438447101891, 0.000427062942474560, 0.000252270970773921, 0.000260956435154029, 0.000421189832259508],

    [2041, 0.002323659389532940, 0.001015300198566690, 0.000072977068320206, 0.000402067906089086, 0.000022415288587917,
     0.000058097527340776, 0.000431863036213264, 0.000255954642188008, 0.000257608337013342, 0.000407147157359291],

    [2042, 0.002274389946436480, 0.001008526109760030, 0.000070447109086626, 0.000413179983269809, 0.000030982330691060,
     0.000060539073518811, 0.000436604775717432, 0.000259546915756464, 0.000254264327246827, 0.000393173773744030],

    [2043, 0.002221761170983700, 0.001000706506536400, 0.000068203536674854, 0.000425889372158917, 0.000040432854012881,
     0.000063763085635997, 0.000441288160987058, 0.000263047791479288, 0.000250924405854485, 0.000379269681413719],

    [2044, 0.002165773063174570, 0.000991841388895826, 0.000066246351084889, 0.000440196072756415, 0.000050766858553374,
     0.000067769563692335, 0.000445913192022145, 0.000266457269356480, 0.000247588572836314, 0.000365434880368363],

    [2045, 0.002590418957053970, 0.003064731698651810, 0.000473413282440563, 0.001532288569167070, 0.000734056564261448,
     0.000438491963999948, 0.001148917635024760, 0.000613576657062066, 0.000968934611466950, 0.001942037583330270],

    [2046, 0.003412000821018890, 0.001467979210071380, 0.000140968936532669, 0.000684224907288152, 0.000169455943369054,
     0.000138142561915737, 0.000625527049399080, 0.000363434728017347, 0.000399266835908938, 0.000668447692126891],

    [2047, 0.003350694152710380, 0.001461738755924970, 0.000136100047100522, 0.000694903104152789, 0.000168920403201844,
     0.000138870633910976, 0.000632858487034851, 0.000369165880291151, 0.000394235489856020, 0.000647227774385425],

    [2048, 0.003284348485867420, 0.001453930030153120, 0.000131660737901086, 0.000707977268579999, 0.000170151825471984,
     0.000140772404814940, 0.000640102393318811, 0.000374759935796506, 0.000389210276364360, 0.000626111793571389],

    [2049, 0.003212963820489950, 0.001444553032755850, 0.000127651008934360, 0.000723447400569792, 0.000173150210179474,
     0.000143847874627630, 0.000647258768250964, 0.000380216894533415, 0.000384191195433960, 0.000605099749684780],

    [2050, 0.003136540156578020, 0.001433607763733140, 0.000124070860200347, 0.000741313500122168, 0.000131323991388514,
     0.000148097043349046, 0.000654327611831310, 0.000385536756501874, 0.000379178247064815, 0.000584191642725602],

    [2051, 0.003055077494131580, 0.001421094223084990, 0.000120920291699043, 0.000761575567237116, 0.000147842364459733,
     0.000153519910979190, 0.000661308924059847, 0.000390719521701887, 0.000374171431256930, 0.000563387472693845],

    [2052, 0.002968575833150680, 0.001407012410811400, 0.000118199303430451, 0.000784233601914656, 0.000165244218749627,
     0.000160116477518057, 0.000668202704936571, 0.000395765190133449, 0.000369170748010304, 0.000542687239589528],

    [2053, 0.002877035173635280, 0.001391362326912370, 0.000115907895394569, 0.000809287604154766, 0.000185544603848730,
     0.000167886742965652, 0.000675008954461489, 0.000400673761796566, 0.000364176197324937, 0.000522090943412632],

    [2054, 0.002780455515585390, 0.001374143971387900, 0.000114046067591399, 0.000836737573957462, 0.000210630019023094,
     0.000176830707321972, 0.000681727672634603, 0.000405445236691234, 0.000359187779200828, 0.000501598584163169],

    [2055, 0.002678836859001050, 0.001355357344238010, 0.000112613820020940, 0.000866583511322734, 0.000237482396634806,
     0.000186948370587018, 0.000688358859455898, 0.000410079614817454, 0.000354205493637976, 0.000481210161841132],

    [2056, 0.002572179203882180, 0.001335002445462670, 0.000111611152683190, 0.000898825416250590, 0.000266101736683869,
     0.000198239732760790, 0.000694902514925393, 0.000414576896175226, 0.000349229340636384, 0.000460925676446520],

    [2057, 0.002460482550228850, 0.001313079275061900, 0.000111038065578153, 0.000933463288741025, 0.000296488039170282,
     0.000210704793843288, 0.000701358639043079, 0.000418937080764552, 0.000344259320196052, 0.000440745127979343],

    [2058, 0.002343746898041050, 0.001289587833035680, 0.000110894558705826, 0.000970497128794037, 0.000328641304094047,
     0.000224343553834512, 0.000707727231808951, 0.000423160168585428, 0.000339295432316975, 0.000420668516439593],

    [2059, 0.002221972247318740, 0.001264528119384040, 0.000111180632066210, 0.001009926936409630, 0.000362561531455156,
     0.000239156012734464, 0.000714008293223019, 0.000427246159637856, 0.000334337676999158, 0.000400695841827272],

    [2060, 0.002590418957053970, 0.003320701075920480, 0.000520734015783138, 0.002127941195692580, 0.001070320941202530,
     0.000621075626855264, 0.001418639589487340, 0.000774996361595863, 0.001054063837517230,
     0.001971195316864690]]

# Conservation Agriculture 'Unit Adoption Calculations'!B251:L298
net_annual_land_units_adopted = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America",
     "China", "India", "EU", "USA"],
    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 34.364230608997, 9.825744810302, 6.148757492366, 9.275197273082, 6.790872900350, 2.587628596994, 0.0, 0.0,
     0.0, 0.0],
    [2016, 66.517122903922, 19.017348143354, 11.910876935363, 17.968505161512, 13.039105733049, 4.970124798308, 0.0,
     0.0, 0.0, 0.0],
    [2017, 96.513575989335, 27.590611671048, 17.295679198443, 26.093909377354, 18.910127684083, 7.153779161864, 0.0,
     0.0, 0.0, 0.0],
    [2018, 124.408488886390, 35.561337030573, 22.312485180785, 33.665395661564, 24.394448540439, 9.144882182384, 0.0,
     0.0, 0.0, 0.0],
    [2019, 150.256760665755, 42.945325878132, 26.970615761691, 40.696949727051, 29.498338722040, 10.949724292618, 0.0,
     0.0, 0.0, 0.0],
    [2020, 174.113290420125, 49.758379842538, 31.279391832960, 47.202557319616, 34.230529665469, 12.574595861639, 0.0,
     0.0, 0.0, 0.0],
    [2021, 196.032977078286, 56.016300546588, 35.248134292849, 53.196204166225, 38.600444850107, 14.025787188401, 0.0,
     0.0, 0.0, 0.0],
    [2022, 216.070719813015, 61.734889616716, 38.886164022724, 58.691875968611, 42.617774030423, 15.309588483939, 0.0,
     0.0, 0.0, 0.0],
    [2023, 234.281417586852, 66.929948665619, 42.202801913795, 63.703558494064, 46.292335831356, 16.432289895988, 0.0,
     0.0, 0.0, 0.0],
    [2024, 250.719969456490, 71.617279280633, 45.207368871525, 68.245237462702, 49.634025258507, 17.400181460183, 0.0,
     0.0, 0.0, 0.0],
    [2025, 265.441274487491, 75.812683035267, 47.909185779589, 72.330898628744, 52.652791858058, 18.219553120190, 0.0,
     0.0, 0.0, 0.0],
    [2026, 278.500231666505, 79.531961519043, 50.317573544638, 75.974527704967, 55.358630760060, 18.896694712683, 0.0,
     0.0, 0.0, 0.0],
    [2027, 289.951739997006, 82.790916285080, 52.441853068317, 79.190110460834, 57.761579978691, 19.437895948358, 0.0,
     0.0, 0.0, 0.0],
    [2028, 299.850698580804, 85.605348872603, 54.291345235993, 81.991632638247, 59.871721115162, 19.849446416944, 0.0,
     0.0, 0.0, 0.0],
    [2029, 308.252006343024, 87.991060800851, 55.875370968415, 84.393079972652, 61.699182273541, 20.137635563796, 0.0,
     0.0, 0.0, 0.0],
    [2030, 315.210562229124, 89.963853567329, 57.203251175180, 86.408438239482, 63.254142685543, 20.308752662402, 0.0,
     0.0, 0.0, 0.0],
    [2031, 320.781265373767, 91.539528659552, 58.284306741347, 88.051693178591, 64.546838750407, 20.369086836208, 0.0,
     0.0, 0.0, 0.0],
    [2032, 325.019014675415, 92.733887525651, 59.127858611081, 89.336830577274, 65.587571586534, 20.324927001811, 0.0,
     0.0, 0.0, 0.0],
    [2033, 327.978709033254, 93.562731599865, 59.743227671593, 90.277836170847, 66.386716122630, 20.182561877164, 0.0,
     0.0, 0.0, 0.0],
    [2034, 329.715247515706, 94.041862260545, 60.139734861789, 90.888695767283, 66.954731938241, 19.948279948998, 0.0,
     0.0, 0.0, 0.0],
    [2035, 330.283528952892, 94.187080880023, 60.326701097136, 91.183395127757, 67.302176140514, 19.628369438026, 0.0,
     0.0, 0.0, 0.0],
    [2036, 329.738452305887, 94.014188772619, 60.313447306567, 91.175920028469, 67.439718518063, 19.229118292979, 0.0,
     0.0, 0.0, 0.0],
    [2037, 328.134916451431, 93.538987206261, 60.109294421954, 90.880256297442, 67.378159496111, 18.756814142506, 0.0,
     0.0, 0.0, 0.0],
    [2038, 325.527820176760, 92.777277421742, 59.723563381764, 90.310389699032, 67.128451218236, 18.217744261223, 0.0,
     0.0, 0.0, 0.0],
    [2039, 321.972062429281, 91.744860558329, 59.165575132550, 89.480306068731, 66.701722370048, 17.618195534562, 0.0,
     0.0, 0.0, 0.0],
    [2040, 317.522541919276, 90.457537737167, 58.444650623645, 88.403991219982, 66.109307318414, 16.964454411319, 0.0,
     0.0, 0.0, 0.0],
    [2041, 312.234157390981, 88.931109969094, 57.570110819624, 87.095430997375, 65.362780156275, 16.262806846835, 0.0,
     0.0, 0.0, 0.0],
    [2042, 306.161807567575, 87.181378195975, 56.551276675624, 85.568611240534, 64.473994309755, 15.519538243670, 0.0,
     0.0, 0.0, 0.0],
    [2043, 299.360391096159, 85.224143263531, 55.397469181678, 83.837517794020, 63.455128149478, 14.740933384361, 0.0,
     0.0, 0.0, 0.0],
    [2044, 291.884806478860, 83.075205888234, 54.118009321964, 81.916136575681, 62.318736933981, 13.933276340978, 0.0,
     0.0, 0.0, 0.0],
    [2045, 283.789952276063, 80.750366655556, 52.722218098060, 79.818453444844, 61.077810889875, 13.102850395074, 0.0,
     0.0, 0.0, 0.0],
    [2046, 275.130726836373, 78.265425997677, 51.219416516943, 77.558454336668, 59.745838275449, 12.255937920673, 0.0,
     0.0, 0.0, 0.0],
    [2047, 265.962028388908, 75.636184182057, 49.618925614891, 75.150125189749, 58.336871062129, 11.398820267569, 0.0,
     0.0, 0.0, 0.0],
    [2048, 256.338755112558, 72.878441249919, 47.930066440191, 72.607451978832, 56.865588505200, 10.537777592942, 0.0,
     0.0, 0.0, 0.0],
    [2049, 246.315804938125, 70.007996986062, 46.162160062353, 69.944420699517, 55.347350648884, 9.679088710032, 0.0,
     0.0, 0.0, 0.0],
    [2050, 235.948075573865, 67.040650876260, 44.324527566307, 67.175017381444, 53.798229476494, 8.829030883230, 0.0,
     0.0, 0.0, 0.0],
    [2051, 225.290464534044, 63.992202080325, 42.426490074279, 64.313228119875, 52.234999355902, 7.993879576929, 0.0,
     0.0, 0.0, 0.0],
    [2052, 214.397869018058, 60.878449304990, 40.477368741146, 61.373039018869, 50.675062572037, 7.179908168981, 0.0,
     0.0, 0.0, 0.0],
    [2053, 203.325185681147, 57.715190746946, 38.486484747769, 58.368436288805, 49.136280012631, 6.393387630517, 0.0,
     0.0, 0.0, 0.0],
    [2054, 192.127310975522, 54.518223993480, 36.463159321402, 55.313406143917, 47.636676321029, 5.640586105245, 0.0,
     0.0, 0.0, 0.0],
    [2055, 180.859140511054, 51.303345851852, 34.416713743283, 52.221934938446, 46.193996046974, 4.927768418597, 0.0,
     0.0, 0.0, 0.0],
    [2056, 169.575569178971, 48.086352219137, 32.356469357325, 49.108009066315, 44.825108668057, 4.261195519447, 0.0,
     0.0, 0.0, 0.0],
    [2057, 158.331490948312, 44.883037808002, 30.291747549840, 45.985615018855, 43.545296541900, 3.647123724281, 0.0,
     0.0, 0.0, 0.0],
    [2058, 147.181798513733, 41.709195887125, 28.231869813027, 42.868739484445, 42.367506257802, 3.091803886023, 0.0,
     0.0, 0.0, 0.0],
    [2059, 136.181382872027, 38.580617887216, 26.186157725958, 39.771369206684, 41.301684442275, 2.601480314599, 0.0,
     0.0, 0.0, 0.0],
    [2060, 125.385132921962, 35.513092879863, 24.163932962240, 36.707491168307, 40.354331744346, 2.182389471924, 0.0,
     0.0, 0.0, 0.0]]

# Perennial Biomass 'Helper Tables'!B91:C137
net_annual_land_units_adopted_perbiomass_list = [
    ["Year", "World"],
    [2014, 0.018875000000], [2015, 1.592449158401], [2016, 3.166023316803],
    [2017, 4.739597475204], [2018, 6.313171633605], [2019, 7.886745792006],
    [2020, 9.460319950407], [2021, 11.033894108809], [2022, 12.607468267210],
    [2023, 14.181042425611], [2024, 15.754616584012], [2025, 17.328190742413],
    [2026, 18.901764900815], [2027, 20.475339059216], [2028, 22.048913217617],
    [2029, 23.622487376018], [2030, 25.196061534420], [2031, 26.603521590755],
    [2032, 28.010981647090], [2033, 29.418441703425], [2034, 30.825901759760],
    [2035, 32.233361816095], [2036, 33.640821872431], [2037, 35.048281928766],
    [2038, 36.455741985101], [2039, 37.863202041436], [2040, 39.270662097771],
    [2041, 40.678122154107], [2042, 42.085582210442], [2043, 43.493042266777],
    [2044, 44.900502323112], [2045, 46.307962379447], [2046, 47.715422435783],
    [2047, 49.122882492118], [2048, 50.530342548453], [2049, 51.937802604788],
    [2050, 53.345262661123], [2051, 54.752722717459], [2052, 56.160182773794],
    [2053, 57.567642830129], [2054, 58.975102886464], [2055, 60.382562942799],
    [2056, 61.790022999135], [2057, 63.197483055470], [2058, 64.356942826961],
    [2059, 65.500902580650], [2060, 66.644862334338]]

# Perennial Biomass 'Unit Adoption Calculations'!EH136:EI182
soln_pds_annual_land_area_harvested_perennial_biomass_list = [
    ["Year", "World"],
    [2015, 0.0], [2016, 0.0], [2017, 0.0], [2018, 0.0], [2019, 0.0], [2020, 0.0], [2021, 0.0],
    [2022, 0.0], [2023, 0.0], [2024, 0.0], [2025, 0.0], [2026, 0.0], [2027, 0.0], [2028, 0.0],
    [2029, 0.0], [2030, 0.0], [2031, 0.0], [2032, 0.0], [2033, 0.0], [2034, 0.0], [2035, 0.0],
    [2036, 1.5735741584013], [2037, 1.5735741584013], [2038, 1.5735741584013],
    [2039, 1.5735741584010], [2040, 1.5735741584012], [2041, 1.5735741584011],
    [2042, 1.5735741584010], [2043, 1.5735741584012], [2044, 1.5735741584012],
    [2045, 1.5735741584012], [2046, 1.5735741584011], [2047, 1.5735741584012],
    [2048, 1.5735741584011], [2049, 1.5735741584013], [2050, 1.5735741584010],
    [2051, 1.5735741584013], [2052, 1.4074600563350], [2053, 1.4074600563350],
    [2054, 1.4074600563353], [2055, 1.4074600563351], [2056, 2.9810342147365],
    [2057, 2.9810342147363], [2058, 2.9810342147365], [2059, 2.9810342147363],
    [2060, 2.9810342147363]]

# System of Rice Intensification 'Helper Tables'!B91:C137
net_annual_land_units_adopted_SRI_list = [
    ["Year", "World"],
    [2014, 3.490000000000], [2015, 4.659450427270], [2016, 5.828900854540],
    [2017, 6.998351281809], [2018, 8.167801709079], [2019, 9.337252136349],
    [2020, 10.506702563619], [2021, 11.676152990889], [2022, 12.845603418159],
    [2023, 14.015053845428], [2024, 15.184504272698], [2025, 16.353954699968],
    [2026, 17.523405127238], [2027, 18.700746952847], [2028, 20.325170091707],
    [2029, 21.882091213410], [2030, 23.371297158388], [2031, 24.555735712325],
    [2032, 25.718606768629], [2033, 26.857321482078], [2034, 27.969023329203],
    [2035, 29.050598951173], [2036, 30.098709481992], [2037, 31.109848842324],
    [2038, 32.080434679120], [2039, 33.006934930049], [2040, 33.886027888195],
    [2041, 34.714786283780], [2042, 35.490867550749], [2043, 36.212685606028],
    [2044, 36.896534905574], [2045, 37.557349448483], [2046, 38.191637316803],
    [2047, 38.797050855640], [2048, 39.371276479349], [2049, 39.912124338590],
    [2050, 40.417630733480], [2051, 40.886165021880], [2052, 41.316529561294],
    [2053, 41.683197966299], [2054, 42.022887730787], [2055, 42.350656761902],
    [2056, 42.665659777437], [2057, 42.967041817449], [2058, 43.253953303807],
    [2059, 43.525567982113], [2060, 43.781103329828]]

# Smallholder Intensification 'Helper Tables'!B91:C137
soln_pds_funits_adopted_smallholder_list = [
    ["Year", "World"],
    [2014, 8.75], [2015, 9.824265632254], [2016, 10.898531264509], [2017, 11.972796896764],
    [2018, 13.047062529019], [2019, 14.121328161274], [2020, 15.195593793529],
    [2021, 16.269859425784], [2022, 17.344125058039], [2023, 18.418390690294],
    [2024, 19.492656322549], [2025, 20.566921954803], [2026, 21.641187587058],
    [2027, 22.715453219313], [2028, 23.789718851568], [2029, 24.863984483823],
    [2030, 25.938250116078], [2031, 26.628667093451], [2032, 27.319084070824],
    [2033, 28.009501048197], [2034, 28.699918025570], [2035, 29.390335002942],
    [2036, 30.080751980315], [2037, 30.771168957688], [2038, 31.461585935061],
    [2039, 32.152002912434], [2040, 32.842419889807], [2041, 33.532836867180],
    [2042, 34.223253844553], [2043, 34.913670821925], [2044, 35.604087799298],
    [2045, 36.294504776671], [2046, 36.984921754044], [2047, 37.675338731417],
    [2048, 38.365755708790], [2049, 39.056172686163], [2050, 39.746589663536],
    [2051, 39.886322684958], [2052, 40.026055706379], [2053, 40.165788727801],
    [2054, 40.305521749223], [2055, 40.445254770645], [2056, 40.584987792067],
    [2057, 40.724720813489], [2058, 40.864453834911], [2059, 41.004186856333],
    [2060, 41.143919877755]]

# Smallholder Intensification 'Helper Tables'!B91:C137
soln_ref_funits_adopted_smallholder_list = [
    ["Year", "World"],
    [2014, 8.75], [2015, 8.75], [2016, 8.75], [2017, 8.75], [2018, 8.75],
    [2019, 8.75], [2020, 8.75], [2021, 8.75], [2022, 8.75], [2023, 8.75],
    [2024, 8.75], [2025, 8.75], [2026, 8.75], [2027, 8.75], [2028, 8.75],
    [2029, 8.75], [2030, 8.75], [2031, 8.75], [2032, 8.75], [2033, 8.75],
    [2034, 8.75], [2035, 8.75], [2036, 8.75], [2037, 8.75], [2038, 8.75],
    [2039, 8.75], [2040, 8.75], [2041, 8.75], [2042, 8.75], [2043, 8.75],
    [2044, 8.75], [2045, 8.75], [2046, 8.75], [2047, 8.75], [2048, 8.75],
    [2049, 8.75], [2050, 8.75], [2051, 8.75], [2052, 8.75], [2053, 8.75],
    [2054, 8.75], [2055, 8.75], [2056, 8.75], [2057, 8.75], [2058, 8.75],
    [2059, 8.75], [2060, 8.75]]
