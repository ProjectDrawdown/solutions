"""Tests for co2calc.py."""

import numpy as np
import pandas as pd
import pytest
from model import advanced_controls
from model import co2calcs
import pathlib

datadir = pathlib.Path(__file__).parents[0].joinpath('data')

def test_co2_mmt_reduced_allfields():
  # the real data from the SolarPVUtil solution has many fields as zero. Test them all.
  # Most of the values here are nonsensical for the real world, designed to ensure that
  # every factor influencing co2_mmt_reduced is non-zero.
  soln_pds_net_grid_electricity_units_saved = pd.DataFrame([[11.0, 11.0], [11.0, 11.0], [11.0, 11.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  soln_pds_net_grid_electricity_units_used = pd.DataFrame([[7.0, 7.0], [7.0, 7.0], [7.0, 7.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  emissions_saved = pd.DataFrame([
      [5000000.0, 5000000.0], [5000000.0, 5000000.0], [5000000.0, 5000000.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  soln_net_annual_funits_adopted = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  conv_ref_grid_CO2_per_KWh = pd.DataFrame([[2020, 1.0, 1.0], [2021, 1.0, 1.0], [2022, 1.0, 1.0]],
      columns=["Year", "A", "B"]).set_index('Year')
  ac = advanced_controls.AdvancedControls(report_start_year=2020, report_end_year=2050,
      solution_category="REPLACEMENT", conv_fuel_consumed_per_funit=1.0,
      fuel_emissions_factor=4000000.0, fuel_emissions_factor_2=0.0,
      soln_fuel_efficiency_factor=0.00,
      soln_indirect_co2_per_iunit=2000000.0, conv_indirect_co2_per_unit=1000000.0,
      conv_indirect_co2_is_iunits=False)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
      soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
      soln_pds_direct_co2_emissions_saved=emissions_saved,
      soln_pds_direct_ch4_co2_emissions_saved=emissions_saved,
      soln_pds_direct_n2o_co2_emissions_saved=emissions_saved,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh,
      conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
      fuel_in_liters=False)
  result = c2.co2_mmt_reduced()
  expected = pd.DataFrame([[23.0, 23.0], [23.0, 23.0], [23.0, 23.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_co2eq_mmt_reduced_allfields():
  # the real data from the SolarPVUtil solution has many fields as zero. Test them all.
  # Most of the values here are nonsensical for the real world, designed to ensure that
  # every factor influencing co2_mmt_reduced is non-zero.
  soln_pds_net_grid_electricity_units_saved = pd.DataFrame([[11.0, 11.0], [11.0, 11.0], [11.0, 11.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  soln_pds_net_grid_electricity_units_used = pd.DataFrame([[7.0, 7.0], [7.0, 7.0], [7.0, 7.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  emissions_saved = pd.DataFrame([
      [5000000.0, 5000000.0], [5000000.0, 5000000.0], [5000000.0, 5000000.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  soln_net_annual_funits_adopted = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  conv_ref_grid_CO2eq_per_KWh = pd.DataFrame([[2020, 1.0, 1.0], [2021, 1.0, 1.0], [2022, 1.0, 1.0]],
      columns=["Year", "A", "B"]).set_index('Year')
  ac = advanced_controls.AdvancedControls(report_start_year=2020, report_end_year=2050,
      solution_category="REPLACEMENT", conv_fuel_consumed_per_funit=1.0,
      fuel_emissions_factor=4000000.0, fuel_emissions_factor_2=0.0,
      soln_fuel_efficiency_factor=0.00,
      soln_indirect_co2_per_iunit=2000000.0, conv_indirect_co2_per_unit=1000000.0,
      conv_indirect_co2_is_iunits=False)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
      soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
      soln_pds_direct_co2_emissions_saved=emissions_saved,
      soln_pds_direct_ch4_co2_emissions_saved=emissions_saved,
      soln_pds_direct_n2o_co2_emissions_saved=emissions_saved,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None,
      conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
      fuel_in_liters=False)
  result = c2.co2eq_mmt_reduced()
  expected = pd.DataFrame([[23.0, 23.0], [23.0, 23.0], [23.0, 23.0]],
      columns=["A", "B"], index=[2020, 2021, 2022])
  pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_co2_ppm_calculator():
  # test replace
  soln_pds_net_grid_electricity_units_saved = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  soln_pds_net_grid_electricity_units_used = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  emissions_saved = pd.DataFrame([
      [1000000.0, 1000000.0], [1000000.0, 1000000.0], [1000000.0, 1000000.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  soln_net_annual_funits_adopted = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  conv_ref_grid_CO2_per_KWh = pd.DataFrame([[2020, 1.0, 1.0], [2021, 1.0, 1.0], [2022, 1.0, 1.0]],
      columns=["Year", "World", "B"]).set_index('Year')
  ac = advanced_controls.AdvancedControls(report_start_year=2020, report_end_year=2050,
      soln_indirect_co2_per_iunit=2000000.0, conv_indirect_co2_per_unit=1000000.0,
      conv_indirect_co2_is_iunits=False)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
      soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
      soln_pds_direct_co2_emissions_saved=emissions_saved,
      soln_pds_direct_ch4_co2_emissions_saved=emissions_saved,
      soln_pds_direct_n2o_co2_emissions_saved=emissions_saved,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh,
      conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2_per_KWh,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
      fuel_in_liters=False)
  result = c2.co2_ppm_calculator()
  expected = pd.DataFrame(co2_ppm_calculator_list[1:],
      columns=co2_ppm_calculator_list[0]).set_index('Year')
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

  # test land model (data from Tropical Forests 3Aug18)
  ac = advanced_controls.AdvancedControls(seq_rate_global=4.150868085, solution_category='LAND',
                                          emissions_use_co2eq=True)
  funits = pd.read_csv(datadir.joinpath('pds_adoption_trr.csv'), index_col=0)
  land_dist = pd.read_csv(datadir.joinpath('land_dist_trr.csv'), index_col=0)
  c2 = co2calcs.CO2Calcs(ac=ac, soln_net_annual_funits_adopted=funits, land_distribution=land_dist)
  result = c2.co2_ppm_calculator()
  assert result.at[2059, 'PPM'] == pytest.approx(6.79894469686587)
  assert result.at[2060, 'PPM'] == pytest.approx(6.98450283426954)
  assert result.at[2015, 'Total'] == pytest.approx(105.702086549681)

def test_co2eq_ppm_calculator():
  soln_pds_net_grid_electricity_units_saved = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  soln_pds_net_grid_electricity_units_used = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  emissions_saved = pd.DataFrame([
      [1000000.0, 1000000.0], [1000000.0, 1000000.0], [1000000.0, 1000000.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  soln_net_annual_funits_adopted = pd.DataFrame([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
      columns=["World", "B"], index=[2020, 2021, 2022])
  conv_ref_grid_CO2_per_KWh = pd.DataFrame([[2020, 1.0, 1.0], [2021, 1.0, 1.0], [2022, 1.0, 1.0]],
      columns=["Year", "World", "B"]).set_index('Year')
  # SolarPVUtil lacks a CH4 Calcs tab, so we craft up some data for the test.
  ch4_ppb_calculator = pd.DataFrame([[2020, 1.0], [2021, 1.0], [2022, 1.0]],
      columns=["Year", "PPB"]).set_index('Year')
  ac = advanced_controls.AdvancedControls(report_start_year=2020, report_end_year=2050,
      soln_indirect_co2_per_iunit=2000000.0, conv_indirect_co2_per_unit=1000000.0,
      conv_indirect_co2_is_iunits=False)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=ch4_ppb_calculator,
      soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
      soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
      soln_pds_direct_co2_emissions_saved=emissions_saved,
      soln_pds_direct_ch4_co2_emissions_saved=emissions_saved,
      soln_pds_direct_n2o_co2_emissions_saved=emissions_saved,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh,
      conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2_per_KWh,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
      fuel_in_liters=False)
  expected = pd.DataFrame(co2eq_ppm_calculator_list[1:],
      columns=co2eq_ppm_calculator_list[0]).set_index('Year')
  result = c2.co2eq_ppm_calculator()
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_co2_reduced_grid_emissions():
  ac = advanced_controls.AdvancedControls(report_start_year=2020, report_end_year=2050)
  soln_pds_net_grid_electricity_units_saved = pd.DataFrame([
      [2015, 1.0, 2.0, 3.0], [2016, 2.0, 3.0, 4.0], [2017, 3.0, 4.0, 5.0]],
      columns=["Year", "World", "OECD90", "Eastern Europe"]).set_index('Year')
  conv_ref_grid_CO2_per_KWh = pd.DataFrame([
      [2015, 0.5, 0.4, 0.7], [2016, 0.5, 0.4, 0.7], [2017, 0.5, 0.4, 0.7]],
      columns=["Year", "World", "OECD90", "Eastern Europe"]).set_index('Year')
  c2 = co2calcs.CO2Calcs(ac=ac,
      ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None,
      soln_ref_new_iunits_reqd=None,
      conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh,
      conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=None,
      fuel_in_liters=False)
  result = c2.co2_reduced_grid_emissions()
  expected = pd.DataFrame([
      [2015, 0.5, 0.8, 2.1], [2016, 1.0, 1.2, 2.8], [2017, 1.5, 1.6, 3.5]],
      columns=["Year", "World", "OECD90", "Eastern Europe"]).set_index('Year')
  pd.testing.assert_frame_equal(result.loc[2015:], expected, check_exact=False)

def test_co2_replaced_grid_emissions():
  ac = advanced_controls.AdvancedControls(solution_category="REPLACEMENT")
  soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
      columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
  conv_ref_grid_CO2_per_KWh = pd.DataFrame(conv_ref_grid_CO2_per_KWh_list[1:],
      columns=conv_ref_grid_CO2_per_KWh_list[0]).set_index('Year')
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted, fuel_in_liters=False)
  result = c2.co2_replaced_grid_emissions()
  expected = pd.DataFrame(co2_replaced_grid_emissions_list[1:],
      columns=co2_replaced_grid_emissions_list[0]).set_index('Year')
  pd.testing.assert_frame_equal(result.loc[2015:], expected, check_exact=False)

def test_co2_replaced_grid_emissions_not_replacement():
  ac = advanced_controls.AdvancedControls(solution_category="REDUCTION")
  soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
      columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
  conv_ref_grid_CO2_per_KWh = pd.DataFrame(conv_ref_grid_CO2_per_KWh_list[1:],
      columns=conv_ref_grid_CO2_per_KWh_list[0]).set_index('Year')
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted, fuel_in_liters=False)
  result = c2.co2_replaced_grid_emissions()
  expected = pd.DataFrame(0, index=soln_net_annual_funits_adopted.index.copy(),
      columns=soln_net_annual_funits_adopted.columns.copy(), dtype=np.float64)
  pd.testing.assert_frame_equal(result, expected)

def test_co2_increased_grid_usage_emissions():
  soln_pds_net_grid_electricity_units_used = pd.DataFrame([[2014, 2.0, 2.0, 2.0],
    [2015, 2.0, 2.0, 2.0], [2016, 2.0, 2.0, 2.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  conv_ref_grid_CO2_per_KWh = pd.DataFrame([[2014, 3.0, 3.0, 3.0],
    [2015, 3.0, 3.0, 3.0], [2016, 3.0, 3.0, 3.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  c2 = co2calcs.CO2Calcs(ac=None, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=None, fuel_in_liters=False)
  result = c2.co2_increased_grid_usage_emissions()
  expected = pd.DataFrame([[2014, 6.0, 6.0, 6.0], [2015, 6.0, 6.0, 6.0], [2016, 6.0, 6.0, 6.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_co2eq_replaced_grid_emissions():
  soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
      columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
  conv_ref_grid_CO2eq_per_KWh = pd.DataFrame(conv_ref_grid_CO2eq_per_KWh_list[1:],
      columns=conv_ref_grid_CO2eq_per_KWh_list[0]).set_index('Year')
  ac = advanced_controls.AdvancedControls(solution_category="REPLACEMENT")
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted, fuel_in_liters=False)
  result = c2.co2eq_replaced_grid_emissions()
  expected = pd.DataFrame(co2eq_replaced_grid_emissions_list[1:],
      columns=co2eq_replaced_grid_emissions_list[0]).set_index('Year')
  pd.testing.assert_frame_equal(result.loc[2015:], expected, check_exact=False)

def test_co2eq_replaced_grid_emissions_not_replacement():
  soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
      columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
  conv_ref_grid_CO2eq_per_KWh = pd.DataFrame(conv_ref_grid_CO2eq_per_KWh_list[1:],
      columns=conv_ref_grid_CO2eq_per_KWh_list[0]).set_index('Year')
  ac = advanced_controls.AdvancedControls(solution_category="REDUCTION")
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted, fuel_in_liters=False)
  result = c2.co2eq_replaced_grid_emissions()
  expected = pd.DataFrame(0, index=soln_net_annual_funits_adopted.index.copy(),
      columns=soln_net_annual_funits_adopted.columns.copy(), dtype=np.float64)
  pd.testing.assert_frame_equal(result, expected)

def test_co2eq_reduced_grid_emissions():
  soln_pds_net_grid_electricity_units_saved = pd.DataFrame([
      [2015, 1.0, 2.0, 3.0], [2016, 2.0, 3.0, 4.0], [2017, 3.0, 4.0, 5.0]],
      columns=["Year", "World", "OECD90", "Eastern Europe"]).set_index('Year')
  conv_ref_grid_CO2eq_per_KWh = pd.DataFrame([
      [2015, 0.5, 0.4, 0.7], [2016, 0.5, 0.4, 0.7], [2017, 0.5, 0.4, 0.7]],
      columns=["Year", "World", "OECD90", "Eastern Europe"]).set_index('Year')
  c2 = co2calcs.CO2Calcs(ac=None, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh,
      soln_net_annual_funits_adopted=None, fuel_in_liters=False)
  result = c2.co2eq_reduced_grid_emissions()
  expected = pd.DataFrame([
      [2015, 0.5, 0.8, 2.1], [2016, 1.0, 1.2, 2.8], [2017, 1.5, 1.6, 3.5]],
      columns=["Year", "World", "OECD90", "Eastern Europe"]).set_index('Year')
  pd.testing.assert_frame_equal(result.loc[2015:], expected, check_exact=False)

def test_co2eq_reduced_fuel_emissions():
  soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
      columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
  ac = advanced_controls.AdvancedControls(
      conv_fuel_consumed_per_funit=100.0,
      fuel_emissions_factor=140.0,
      fuel_emissions_factor_2=10.0,
      soln_fuel_efficiency_factor=0.03)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted, fuel_in_liters=False)
  result = c2.co2eq_reduced_fuel_emissions()
  expected = pd.DataFrame(co2eq_reduced_fuel_emissions_list[1:],
      columns=co2eq_reduced_fuel_emissions_list[0]).set_index('Year')
  pd.testing.assert_frame_equal(result.loc[2015:], expected)

def test_co2eq_reduced_fuel_emissions_liters():
  soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
      columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
  ac = advanced_controls.AdvancedControls(
      conv_fuel_consumed_per_funit=100.0,
      fuel_emissions_factor=140.0,
      fuel_emissions_factor_2=10.0,
      soln_fuel_efficiency_factor=0.03)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted, fuel_in_liters=True)
  with pytest.raises(NotImplementedError):
    _ = c2.co2eq_reduced_fuel_emissions()

def test_co2eq_increased_grid_usage_emissions():
  soln_pds_net_grid_electricity_units_used = pd.DataFrame([[2014, 2.0, 2.0, 2.0],
    [2015, 2.0, 2.0, 2.0], [2016, 2.0, 2.0, 2.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  conv_ref_grid_CO2eq_per_KWh = pd.DataFrame([[2014, 3.0, 3.0, 3.0],
    [2015, 3.0, 3.0, 3.0], [2016, 3.0, 3.0, 3.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  c2 = co2calcs.CO2Calcs(ac=None, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh,
      soln_net_annual_funits_adopted=None, fuel_in_liters=True)
  result = c2.co2eq_increased_grid_usage_emissions()
  expected = pd.DataFrame([[2014, 6.0, 6.0, 6.0], [2015, 6.0, 6.0, 6.0], [2016, 6.0, 6.0, 6.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_co2eq_direct_reduced_emissions():
  soln_pds_direct_co2_emissions_saved = pd.DataFrame([[2014, 1000000.0, 1100000.0, 1200000.0],
    [2015, 1000001.0, 1100001.0, 1200001.0], [2016, 1000002.0, 1100002.0, 1200002.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  soln_pds_direct_ch4_co2_emissions_saved = pd.DataFrame([[2014, 2200000.0, 2200000.0, 2200000.0],
    [2015, 2200002.0, 2200002.0, 2200002.0], [2016, 2200004.0, 2200004.0, 2200004.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  soln_pds_direct_n2o_co2_emissions_saved = pd.DataFrame([[2014, 3300000.0, 3300000.0, 3300000.0],
    [2015, 3300003.0, 3300003.0, 3300003.0], [2016, 3300006.0, 3300006.0, 3300006.0]],
    columns=["Year", "A", "B", "C"]).set_index("Year")
  c2 = co2calcs.CO2Calcs(ac=None, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=soln_pds_direct_co2_emissions_saved,
      soln_pds_direct_ch4_co2_emissions_saved=soln_pds_direct_ch4_co2_emissions_saved,
      soln_pds_direct_n2o_co2_emissions_saved=soln_pds_direct_n2o_co2_emissions_saved,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=None, fuel_in_liters=False)
  result = c2.co2eq_direct_reduced_emissions()
  expected = pd.DataFrame([[2014, 6.5, 6.6, 6.7], [2015, 6.500006, 6.600006, 6.700006],
    [2016, 6.500012, 6.600012, 6.700012]], columns=["Year", "A", "B", "C"]).set_index("Year")
  pd.testing.assert_frame_equal(result, expected, check_exact=False)

def test_co2eq_net_indirect_emissions():
  soln_net_annual_funits_adopted = pd.DataFrame(soln_net_annual_funits_adopted_list[1:],
      columns=soln_net_annual_funits_adopted_list[0]).set_index('Year')
  ac = advanced_controls.AdvancedControls(conv_indirect_co2_is_iunits=False,
      soln_indirect_co2_per_iunit=47157.2222222222, conv_indirect_co2_per_unit=0.0)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted, fuel_in_liters=True)
  expected = pd.DataFrame(co2eq_net_indirect_emissions_list[1:],
      columns=co2eq_net_indirect_emissions_list[0]).set_index('Year')
  result = c2.co2eq_net_indirect_emissions()
  pd.testing.assert_frame_equal(result.loc[2015:], expected, check_exact=False)

def test_co2eq_net_indirect_emissions_iunits():
  soln_pds_new_iunits_reqd = pd.DataFrame([[2014, 10.0, 11.0, 12.0], [2015, 12.0, 13.0, 14.0],
      [2016, 14.0, 15.0, 16.0], [2017, 16.0, 17.0, 18.0]],
      columns=['Year', 'A', 'B', 'C']).set_index('Year')
  soln_ref_new_iunits_reqd = pd.DataFrame([[2014, 8.0, 7.0, 6.0], [2015, 10.0, 8.0, 6.0],
      [2016, 11.0, 7.0, 3.0], [2017, 14.0, 9.0, 4.0]],
      columns=['Year', 'A', 'B', 'C']).set_index('Year')
  conv_ref_new_iunits = pd.DataFrame([[2014, 1.0, 1.0, 1.0], [2015, 1.0, 1.0, 1.0],
      [2016, 1.0, 1.0, 1.0], [2017, 1.0, 1.0, 1.0]],
      columns=['Year', 'A', 'B', 'C']).set_index('Year')
  ac = advanced_controls.AdvancedControls(conv_indirect_co2_is_iunits=True,
      soln_indirect_co2_per_iunit=100, conv_indirect_co2_per_unit=20.0)
  c2 = co2calcs.CO2Calcs(ac=ac, ch4_ppb_calculator=None,
      soln_pds_net_grid_electricity_units_saved=None,
      soln_pds_net_grid_electricity_units_used=None,
      soln_pds_direct_co2_emissions_saved=None,
      soln_pds_direct_ch4_co2_emissions_saved=None,
      soln_pds_direct_n2o_co2_emissions_saved=None,
      soln_pds_new_iunits_reqd=soln_pds_new_iunits_reqd,
      soln_ref_new_iunits_reqd=soln_ref_new_iunits_reqd,
      conv_ref_new_iunits=conv_ref_new_iunits,
      conv_ref_grid_CO2_per_KWh=None, conv_ref_grid_CO2eq_per_KWh=None,
      soln_net_annual_funits_adopted=[], fuel_in_liters=True)
  result = c2.co2eq_net_indirect_emissions()
  expected = pd.DataFrame([[2014, 0.00022, 0.00042, 0.00062], [2015, 0.00022, 0.00052, 0.00082],
      [2016, 0.00032, 0.00082, 0.00132], [2017, 0.00022, 0.00082, 0.00142]],
      columns=['Year', 'A', 'B', 'C']).set_index('Year')
  pd.testing.assert_frame_equal(result, expected, check_exact=False)


def test_co2_sequestered_global():
    """ Test vals from Tropical Forests """
    ac = advanced_controls.AdvancedControls(seq_rate_global=4.150868085)
    funits = pd.read_csv(datadir.joinpath('pds_adoption_trr.csv'), index_col=0)
    land_dist = pd.read_csv(datadir.joinpath('land_dist_trr.csv'), index_col=0)
    c2 = co2calcs.CO2Calcs(ac=ac, soln_net_annual_funits_adopted=funits, land_distribution=land_dist)
    df = c2.co2_sequestered_global()
    assert df.loc[2060, 'All'] == pytest.approx(2884.57122692783)
    assert df.loc[2015, 'Tropical-Semi-Arid'] == pytest.approx(42.2676049356999)


# 'Unit Adoption'!B251:L298
soln_net_annual_funits_adopted_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2015, 59.16952483163, -75.62640223557, -0.33768156367, -22.15920892112, -1.71009099271, -15.41714380040, -15.43313810117, -3.07011430874, -55.75969246529, -13.21605539049],
    [2016, 150.52159292976, -76.24855891557, -0.34297979401, -23.24591339780, -1.84510420765, -16.18366871191, -15.89405398012, -3.39192750636, -56.24733048614, -13.30746078097],
    [2017, 257.36122967139, -76.87071559558, -0.34827802435, -24.33261787447, -1.98011742258, -16.95019362342, -16.35496985906, -3.71374070399, -56.73496850699, -13.39886617146],
    [2018, 378.99298898654, -77.49287227559, -0.35357625469, -25.41932235115, -2.11513063752, -17.71671853493, -16.81588573801, -4.03555390161, -57.22260652784, -13.49027156194],
    [2019, 514.72142480523, -78.11502895560, -0.35887448503, -26.50602682782, -2.25014385245, -18.48324344644, -17.27680161696, -4.35736709924, -57.71024454869, -13.58167695243],
    [2020, 514.73678922371, -78.73718563561, -0.36417271537, -27.59273130450, -2.38515706739, -19.24976835795, -17.73771749591, -4.67918029686, -58.19788256953, -13.67308234291],
    [2021, 825.68654167325, -79.35934231562, -0.36947094570, -28.67943578117, -2.52017028232, -20.01629326946, -18.19863337485, -5.00099349449, -58.68552059038, -13.76448773340],
    [2022, 999.53233058261, -79.98149899563, -0.37476917604, -29.76614025785, -2.65518349726, -20.78281818097, -18.65954925380, -5.32280669212, -59.17315861123, -13.85589312388],
    [2023, 1184.69301171557, -80.60365567564, -0.38006740638, -30.85284473453, -2.79019671219, -21.54934309248, -19.12046513275, -5.64461988974, -59.66079663208, -13.94729851437],
    [2024, 1380.47313900213, -81.22581235565, -0.38536563672, -31.93954921120, -2.92520992713, -22.31586800399, -19.58138101170, -5.96643308737, -60.14843465293, -14.03870390485],
    [2025, 1433.94497468791, -81.84796903566, -0.39066386706, -33.02625368788, -3.06022314206, -23.08239291550, -20.04229689064, -6.28824628499, -60.63607267378, -14.13010929534],
    [2026, 1801.10994775612, -82.47012571567, -0.39596209740, -34.11295816455, -3.19523635700, -23.84891782701, -20.50321276959, -6.61005948262, -61.12371069462, -14.22151468583],
    [2027, 2024.57573708357, -83.09228239568, -0.40126032774, -35.19966264123, -3.33024957193, -24.61544273852, -20.96412864854, -6.93187268024, -61.61134871547, -14.31292007631],
    [2028, 2255.87918828469, -83.71443907569, -0.40655855808, -36.28636711790, -3.46526278687, -25.38196765003, -21.42504452749, -7.25368587787, -62.09898673632, -14.40432546680],
    [2029, 2494.32485528949, -84.33659575570, -0.41185678841, -37.37307159458, -3.60027600180, -26.14849256154, -21.88596040643, -7.57549907549, -62.58662475717, -14.49573085728],
    [2030, 2856.55316015211, -84.95875243571, -0.41715501875, -38.45977607125, -3.73528921674, -26.91501747306, -22.34687628538, -7.89731227312, -63.07426277802, -14.58713624777],
    [2031, 2989.86105243015, -85.58090911572, -0.42245324909, -39.54648054793, -3.87030243167, -27.68154238457, -22.80779216433, -8.21912547074, -63.56190079887, -14.67854163825],
    [2032, 3245.56069042605, -86.20306579573, -0.42775147943, -40.63318502461, -4.00531564661, -28.44806729608, -23.26870804327, -8.54093866837, -64.04953881971, -14.76994702874],
    [2033, 3505.62075994569, -86.82522247573, -0.43304970977, -41.71988950128, -4.14032886154, -29.21459220759, -23.72962392222, -8.86275186600, -64.53717684056, -14.86135241922],
    [2034, 3769.34581491907, -87.44737915574, -0.43834794011, -42.80659397796, -4.27534207648, -29.98111711910, -24.19053980117, -9.18456506362, -65.02481486141, -14.95275780971],
    [2035, 4036.04040927621, -88.06953583575, -0.44364617045, -43.89329845463, -4.41035529141, -30.74764203061, -24.65145568012, -9.50637826125, -65.51245288226, -15.04416320019],
    [2036, 4305.00909694713, -88.69169251576, -0.44894440079, -44.98000293131, -4.54536850635, -31.51416694212, -25.11237155906, -9.82819145887, -66.00009090311, -15.13556859068],
    [2037, 4575.55643186183, -89.31384919577, -0.45424263112, -46.06670740798, -4.68038172128, -32.28069185363, -25.57328743801, -10.15000465650, -66.48772892395, -15.22697398117],
    [2038, 4846.98696795034, -89.93600587578, -0.45954086146, -47.15341188466, -4.81539493622, -33.04721676514, -26.03420331696, -10.47181785412, -66.97536694480, -15.31837937165],
    [2039, 5118.60525914267, -90.55816255579, -0.46483909180, -48.24011636133, -4.95040815115, -33.81374167665, -26.49511919591, -10.79363105175, -67.46300496565, -15.40978476214],
    [2040, 5437.16953108051, -91.18031923580, -0.47013732214, -49.32682083801, -5.08542136609, -34.58026658816, -26.95603507485, -11.11544424937, -67.95064298650, -15.50119015262],
    [2041, 5659.62332255882, -91.80247591581, -0.47543555248, -50.41352531469, -5.22043458102, -35.34679149967, -27.41695095380, -11.43725744700, -68.43828100735, -15.59259554311],
    [2042, 5927.63220264268, -92.42463259582, -0.48073378282, -51.50022979136, -5.35544779596, -36.11331641118, -27.87786683275, -11.75907064462, -68.92591902820, -15.68400093359],
    [2043, 6193.04705355042, -93.04678927583, -0.48603201316, -52.58693426804, -5.49046101089, -36.87984132269, -28.33878271170, -12.08088384225, -69.41355704904, -15.77540632408],
    [2044, 6455.17242921204, -93.66894595584, -0.49133024350, -53.67363874471, -5.62547422583, -37.64636623420, -28.79969859064, -12.40269703988, -69.90119506989, -15.86681171456],
    [2045, 6713.31288355757, -94.29110263585, -0.49662847384, -54.76034322139, -5.76048744076, -38.41289114571, -29.26061446959, -12.72451023750, -70.38883309074, -15.95821710505],
    [2046, 6966.77297051701, -94.91325931586, -0.50192670417, -55.84704769806, -5.89550065570, -39.17941605722, -29.72153034854, -13.04632343513, -70.87647111159, -16.04962249553],
    [2047, 7214.85724402038, -95.53541599587, -0.50722493451, -56.93375217474, -6.03051387063, -39.94594096873, -30.18244622749, -13.36813663275, -71.36410913244, -16.14102788602],
    [2048, 7456.87025799770, -96.15757267588, -0.51252316485, -58.02045665141, -6.16552708557, -40.71246588024, -30.64336210643, -13.68994983038, -71.85174715329, -16.23243327651],
    [2049, 7692.11656637898, -96.77972935589, -0.51782139519, -59.10716112809, -6.30054030050, -41.47899079175, -31.10427798538, -14.01176302800, -72.33938517413, -16.32383866699],
    [2050, 7895.38590200891, -97.40188603589, -0.52311962553, -60.19386560477, -6.43555351544, -42.24551570326, -31.56519386433, -14.33357622563, -72.82702319498, -16.41524405748],
    [2051, 8139.52728207347, -98.02404271590, -0.52841785587, -61.28057008144, -6.57056673037, -43.01204061477, -32.02610974327, -14.65538942325, -73.31466121583, -16.50664944796],
    [2052, 8350.30079724671, -98.64619939591, -0.53371608621, -62.36727455812, -6.70557994531, -43.77856552628, -32.48702562222, -14.97720262088, -73.80229923668, -16.59805483845],
    [2053, 8551.52582254397, -99.26835607592, -0.53901431655, -63.45397903479, -6.84059316024, -44.54509043779, -32.94794150117, -15.29901581851, -74.28993725753, -16.68946022893],
    [2054, 8742.50691189525, -99.89051275593, -0.54431254688, -64.54068351147, -6.97560637518, -45.31161534930, -33.40885738012, -15.62082901613, -74.77757527838, -16.78086561942],
    [2055, 8922.54861923059, -100.51266943594, -0.54961077722, -65.62738798814, -7.11061959011, -46.07814026081, -33.86977325906, -15.94264221376, -75.26521329922, -16.87227100990],
    [2056, 9090.95549847998, -101.13482611595, -0.55490900756, -66.71409246482, -7.24563280505, -46.84466517233, -34.33068913801, -16.26445541138, -75.75285132007, -16.96367640039],
    [2057, 9247.03210357344, -101.75698279596, -0.56020723790, -67.80079694150, -7.38064601998, -47.61119008384, -34.79160501696, -16.58626860901, -76.24048934092, -17.05508179088],
    [2058, 9390.08298844099, -102.37913947597, -0.56550546824, -68.88750141817, -7.51565923492, -48.37771499535, -35.25252089591, -16.90808180663, -76.72812736177, -17.14648718136],
    [2059, 9519.41270701265, -103.00129615598, -0.57080369858, -69.97420589485, -7.65067244985, -49.14423990686, -35.71343677485, -17.22989500426, -77.21576538262, -17.23789257185],
    [2060, 9634.32581321841, -103.62345283599, -0.57610192892, -71.06091037152, -7.78568566479, -49.91076481837, -36.17435265380, -17.55170820188, -77.70340340347, -17.32929796233]]

# 'CO2 Calcs'!AP344:AZ390
co2eq_net_indirect_emissions_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 2.79027043127, -3.56633105609, -0.01592412454, -1.04496673936, -0.08064314096, -0.72702967623, -0.72778392302, -0.14477806270, -2.62947220863, -0.62323246095],
    [2016, 7.09818020703, -3.59567023691, -0.01617397436, -1.09621270386, -0.08700998914, -0.76317686182, -0.74951943555, -0.15995387918, -2.65246786314, -0.62754288526],
    [2017, 12.13644069900, -3.62500941772, -0.01642382419, -1.14745866835, -0.09337683732, -0.79932404741, -0.77125494808, -0.17512969565, -2.67546351765, -0.63185330957],
    [2018, 17.87225660230, -3.65434859854, -0.01667367401, -1.19870463285, -0.09974368550, -0.83547123300, -0.79299046061, -0.19030551213, -2.69845917217, -0.63616373388],
    [2019, 24.27283261208, -3.68368777935, -0.01692352384, -1.24995059735, -0.10611053368, -0.87161841859, -0.81472597314, -0.20548132860, -2.72145482668, -0.64047415820],
    [2020, 24.27355715538, -3.71302696017, -0.01717337367, -1.30119656184, -0.11247738186, -0.90776560418, -0.83646148567, -0.22065714508, -2.74445048119, -0.64478458251],
    [2021, 38.93708373158, -3.74236614099, -0.01742322349, -1.35244252634, -0.11884423004, -0.94391278977, -0.85819699820, -0.23583296155, -2.76744613571, -0.64909500682],
    [2022, 47.13516823158, -3.77170532180, -0.01767307332, -1.40368849084, -0.12521107822, -0.98005997536, -0.87993251073, -0.25100877803, -2.79044179022, -0.65340543113],
    [2023, 55.86683161858, -3.80104450262, -0.01792292314, -1.45493445533, -0.13157792640, -1.01620716096, -0.90166802326, -0.26618459450, -2.81343744473, -0.65771585544],
    [2024, 65.09927858773, -3.83038368344, -0.01817277297, -1.50618041983, -0.13794477458, -1.05235434655, -0.92340353579, -0.28136041097, -2.83643309925, -0.66202627975],
    [2025, 67.62086182580, -3.85972286425, -0.01842262279, -1.55742638433, -0.14431162276, -1.08850153214, -0.94513904832, -0.29653622745, -2.85942875376, -0.66633670406],
    [2026, 84.93534205299, -3.88906204507, -0.01867247262, -1.60867234882, -0.15067847094, -1.12464871773, -0.96687456085, -0.31171204392, -2.88242440827, -0.67064712838],
    [2027, 95.47336793937, -3.91840122588, -0.01892232244, -1.65991831332, -0.15704531912, -1.16079590332, -0.98861007337, -0.32688786040, -2.90542006279, -0.67495755269],
    [2028, 106.38099618843, -3.94774040670, -0.01917217227, -1.71116427782, -0.16341216730, -1.19694308891, -1.01034558590, -0.34206367687, -2.92841571730, -0.67926797700],
    [2029, 117.62543149530, -3.97707958752, -0.01942202210, -1.76241024231, -0.16977901548, -1.23309027450, -1.03208109843, -0.35723949335, -2.95141137181, -0.68357840131],
    [2030, 134.70711216288, -4.00641876833, -0.01967187192, -1.81365620681, -0.17614586366, -1.26923746009, -1.05381661096, -0.37241530982, -2.97440702633, -0.68788882562],
    [2031, 140.99354206302, -4.03575794915, -0.01992172175, -1.86490217131, -0.18251271184, -1.30538464568, -1.07555212349, -0.38759112630, -2.99740268084, -0.69219924993],
    [2032, 153.05162671413, -4.06509712997, -0.02017157157, -1.91614813580, -0.18887956002, -1.34153183127, -1.09728763602, -0.40276694277, -3.02039833535, -0.69650967424],
    [2033, 165.31533720359, -4.09443631078, -0.02042142140, -1.96739410030, -0.19524640820, -1.37767901686, -1.11902314855, -0.41794275925, -3.04339398987, -0.70082009856],
    [2034, 177.75187822654, -4.12377549160, -0.02067127122, -2.01864006479, -0.20161325638, -1.41382620246, -1.14075866108, -0.43311857572, -3.06638964438, -0.70513052287],
    [2035, 190.32845447811, -4.15311467241, -0.02092112105, -2.06988602929, -0.20798010456, -1.44997338805, -1.16249417361, -0.44829439219, -3.08938529889, -0.70944094718],
    [2036, 203.01227065342, -4.18245385323, -0.02117097087, -2.12113199379, -0.21434695274, -1.48612057364, -1.18422968614, -0.46347020867, -3.11238095340, -0.71375137149],
    [2037, 215.77053144763, -4.21179303405, -0.02142082070, -2.17237795828, -0.22071380092, -1.52226775923, -1.20596519867, -0.47864602514, -3.13537660792, -0.71806179580],
    [2038, 228.57044155585, -4.24113221486, -0.02167067052, -2.22362392278, -0.22708064909, -1.55841494482, -1.22770071120, -0.49382184162, -3.15837226243, -0.72237222011],
    [2039, 241.37920567323, -4.27047139568, -0.02192052035, -2.27486988728, -0.23344749727, -1.59456213041, -1.24943622373, -0.50899765809, -3.18136791694, -0.72668264442],
    [2040, 256.40181183706, -4.29981057650, -0.02217037018, -2.32611585177, -0.23981434545, -1.63070931600, -1.27117173625, -0.52417347457, -3.20436357146, -0.73099306874],
    [2041, 266.89211471598, -4.32914975731, -0.02242022000, -2.37736181627, -0.24618119363, -1.66685650159, -1.29290724878, -0.53934929104, -3.22735922597, -0.73530349305],
    [2042, 279.53066903162, -4.35848893813, -0.02267006983, -2.42860778077, -0.25254804181, -1.70300368718, -1.31464276131, -0.55452510752, -3.25035488048, -0.73961391736],
    [2043, 292.04689613696, -4.38782811894, -0.02291991965, -2.47985374526, -0.25891488999, -1.73915087277, -1.33637827384, -0.56970092399, -3.27335053500, -0.74392434167],
    [2044, 304.40800072711, -4.41716729976, -0.02316976948, -2.53109970976, -0.26528173817, -1.77529805837, -1.35811378637, -0.58487674046, -3.29634618951, -0.74823476598],
    [2045, 316.58118749723, -4.44650648058, -0.02341961930, -2.58234567426, -0.27164858635, -1.81144524396, -1.37984929890, -0.60005255694, -3.31934184402, -0.75254519029],
    [2046, 328.53366114244, -4.47584566139, -0.02366946913, -2.63359163875, -0.27801543453, -1.84759242955, -1.40158481143, -0.61522837341, -3.34233749854, -0.75685561460],
    [2047, 340.23262635788, -4.50518484221, -0.02391931895, -2.68483760325, -0.28438228271, -1.88373961514, -1.42332032396, -0.63040418989, -3.36533315305, -0.76116603892],
    [2048, 351.64528783868, -4.53452402303, -0.02416916878, -2.73608356775, -0.29074913089, -1.91988680073, -1.44505583649, -0.64558000636, -3.38832880756, -0.76547646323],
    [2049, 362.73885027997, -4.56386320384, -0.02441901860, -2.78732953224, -0.29711597907, -1.95603398632, -1.46679134902, -0.66075582284, -3.41132446208, -0.76978688754],
    [2050, 372.32446751124, -4.59320238466, -0.02466886843, -2.83857549674, -0.30348282725, -1.99218117191, -1.48852686155, -0.67593163931, -3.43432011659, -0.77409731185],
    [2051, 383.83749682458, -4.62254156547, -0.02491871826, -2.88982146124, -0.30984967543, -2.02832835750, -1.51026237408, -0.69110745579, -3.45731577110, -0.77840773616],
    [2052, 393.77699031816, -4.65188074629, -0.02516856808, -2.94106742573, -0.31621652361, -2.06447554309, -1.53199788661, -0.70628327226, -3.48031142562, -0.78271816047],
    [2053, 403.26620355278, -4.68121992711, -0.02541841791, -2.99231339023, -0.32258337179, -2.10062272868, -1.55373339914, -0.72145908873, -3.50330708013, -0.78702858478],
    [2054, 412.27234122356, -4.71055910792, -0.02566826773, -3.04355935472, -0.32895021997, -2.13676991428, -1.57546891166, -0.73663490521, -3.52630273464, -0.79133900910],
    [2055, 420.76260802564, -4.73989828874, -0.02591811756, -3.09480531922, -0.33531706815, -2.17291709987, -1.59720442419, -0.75181072168, -3.54929838915, -0.79564943341],
    [2056, 428.70420865415, -4.76923746956, -0.02616796738, -3.14605128372, -0.34168391633, -2.20906428546, -1.61893993672, -0.76698653816, -3.57229404367, -0.79995985772],
    [2057, 436.06434780424, -4.79857665037, -0.02641781721, -3.19729724821, -0.34805076451, -2.24521147105, -1.64067544925, -0.78216235463, -3.59528969818, -0.80427028203],
    [2058, 442.81023017102, -4.82791583119, -0.02666766703, -3.24854321271, -0.35441761269, -2.28135865664, -1.66241096178, -0.79733817111, -3.61828535269, -0.80858070634],
    [2059, 448.90906044964, -4.85725501200, -0.02691751686, -3.29978917721, -0.36078446087, -2.31750584223, -1.68414647431, -0.81251398758, -3.64128100721, -0.81289113065],
    [2060, 454.32804333523, -4.88659419282, -0.02716736668, -3.35103514170, -0.36715130905, -2.35365302782, -1.70588198684, -0.82768980406, -3.66427666172, -0.81720155496]]

# 'Emissions Factors'!A11:K57
conv_ref_grid_CO2eq_per_KWh_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 0.580491641, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2016, 0.580381730, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2017, 0.580191808, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2018, 0.579932742, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2019, 0.579613986, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2020, 0.581083120, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2021, 0.578829123, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2022, 0.578376324, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2023, 0.577890875, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2024, 0.577377675, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2025, 0.576724036, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2026, 0.576284921, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2027, 0.575712661, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2028, 0.575127412, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2029, 0.574531990, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2030, 0.573264022, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2031, 0.573320545, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2032, 0.572708901, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2033, 0.572095895, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2034, 0.571483259, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2035, 0.570821497, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2036, 0.570265395, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2037, 0.569663069, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2038, 0.569066909, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2039, 0.568478136, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2040, 0.567083308, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2041, 0.567327331, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2042, 0.566767481, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2043, 0.566219394, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2044, 0.565684079, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2045, 0.565044176, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2046, 0.564655700, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2047, 0.564164556, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2048, 0.563690051, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2049, 0.563233144, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2050, 0.563942003, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2051, 0.562376012, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2052, 0.561977781, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2053, 0.561601149, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2054, 0.561247194, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2055, 0.560917031, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2056, 0.560611819, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2057, 0.560332776, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2058, 0.560081211, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2059, 0.559858464, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666],
    [2060, 0.559324305, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666]]

# 'CO2 Calcs'!R288:AB334
co2eq_replaced_grid_emissions_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 34.34741457098, -34.33960397166, -0.24473402298, -10.14136021043, -0.48266276388, -8.70135444200, -8.27158177976, -2.41873546070, -20.10857832347, -8.78962397968],
    [2016, 87.35998257762, -34.62210602608, -0.24857390459, -10.63870023639, -0.52076942122, -9.13397704901, -8.51861536174, -2.67227031789, -20.28443487687, -8.85041511503],
    [2017, 149.31887709637, -34.90460808050, -0.25241378620, -11.13604026236, -0.55887607856, -9.56659965603, -8.76564894372, -2.92580517508, -20.46029143027, -8.91120625039],
    [2018, 219.79044346191, -35.18711013491, -0.25625366780, -11.63338028833, -0.59698273590, -9.99922226305, -9.01268252570, -3.17934003227, -20.63614798367, -8.97199738574],
    [2019, 298.33973689392, -35.46961218933, -0.26009354941, -12.13072031430, -0.63508939324, -10.43184487006, -9.25971610768, -3.43287488946, -20.81200453707, -9.03278852109],
    [2020, 299.10485925837, -35.75211424375, -0.26393343102, -12.62806034026, -0.67319605059, -10.86446747708, -9.50674968966, -3.68640974664, -20.98786109048, -9.09357965645],
    [2021, 477.93141689368, -36.03461629817, -0.26777331263, -13.12540036623, -0.71130270793, -11.29709008410, -9.75378327164, -3.93994460383, -21.16371764388, -9.15437079180],
    [2022, 578.10583547744, -36.31711835259, -0.27161319423, -13.62274039220, -0.74940936527, -11.72971269111, -10.00081685362, -4.19347946102, -21.33957419728, -9.21516192715],
    [2023, 684.62328103749, -36.59962040701, -0.27545307584, -14.12008041817, -0.78751602261, -12.16233529813, -10.24785043560, -4.44701431821, -21.51543075068, -9.27595306251],
    [2024, 797.05437165910, -36.88212246143, -0.27929295745, -14.61742044413, -0.82562267995, -12.59495790514, -10.49488401757, -4.70054917540, -21.69128730409, -9.33674419786],
    [2025, 826.99053313261, -37.16462451585, -0.28313283906, -15.11476047010, -0.86372933729, -13.02758051216, -10.74191759955, -4.95408403259, -21.86714385749, -9.39753533321],
    [2026, 1037.95250346173, -37.44712657026, -0.28697272066, -15.61210049607, -0.90183599463, -13.46020311918, -10.98895118153, -5.20761888978, -22.04300041089, -9.45832646857],
    [2027, 1165.57388557390, -37.72962862468, -0.29081260227, -16.10944052204, -0.93994265197, -13.89282572619, -11.23598476351, -5.46115374697, -22.21885696429, -9.51911760392],
    [2028, 1297.41795972499, -38.01213067910, -0.29465248388, -16.60678054800, -0.97804930931, -14.32544833321, -11.48301834549, -5.71468860415, -22.39471351770, -9.57990873928],
    [2029, 1433.06942203656, -38.29463273352, -0.29849236549, -17.10412057397, -1.01615596665, -14.75807094022, -11.73005192747, -5.96822346134, -22.57057007110, -9.64069987463],
    [2030, 1637.55915306579, -38.57713478794, -0.30233224709, -17.60146059994, -1.05426262399, -15.19069354724, -11.97708550945, -6.22175831853, -22.74642662450, -9.70149100998],
    [2031, 1714.14876834778, -38.85963684236, -0.30617212870, -18.09880062591, -1.09236928133, -15.62331615426, -12.22411909143, -6.47529317572, -22.92228317790, -9.76228214534],
    [2032, 1858.76149482384, -39.14213889678, -0.31001201031, -18.59614065187, -1.13047593868, -16.05593876127, -12.47115267340, -6.72882803291, -23.09813973131, -9.82307328069],
    [2033, 2005.55124627676, -39.42464095120, -0.31385189192, -19.09348067784, -1.16858259602, -16.48856136829, -12.71818625538, -6.98236289010, -23.27399628471, -9.88386441604],
    [2034, 2154.11802988531, -39.70714300561, -0.31769177352, -19.59082070381, -1.20668925336, -16.92118397531, -12.96521983736, -7.23589774729, -23.44985283811, -9.94465555140],
    [2035, 2303.85862880678, -39.98964506003, -0.32153165513, -20.08816072978, -1.24479591070, -17.35380658232, -13.21225341934, -7.48943260447, -23.62570939151, -10.00544668675],
    [2036, 2454.99771488230, -40.27214711445, -0.32537153674, -20.58550075574, -1.28290256804, -17.78642918934, -13.45928700132, -7.74296746166, -23.80156594492, -10.06623782210],
    [2037, 2606.52551763827, -40.55464916887, -0.32921141834, -21.08284078171, -1.32100922538, -18.21905179635, -13.70632058330, -7.99650231885, -23.97742249832, -10.12702895746],
    [2038, 2758.25989310781, -40.83715122329, -0.33305129995, -21.58018080768, -1.35911588272, -18.65167440337, -13.95335416528, -8.25003717604, -24.15327905172, -10.18782009281],
    [2039, 2909.81517549787, -41.11965327771, -0.33689118156, -22.07752083365, -1.39722254006, -19.08429701039, -14.20038774726, -8.50357203323, -24.32913560512, -10.24861122816],
    [2040, 3083.32808315463, -41.40215533213, -0.34073106317, -22.57486085961, -1.43532919740, -19.51691961740, -14.44742132923, -8.75710689042, -24.50499215853, -10.30940236352],
    [2041, 3210.85899521741, -41.68465738655, -0.34457094477, -23.07220088558, -1.47343585474, -19.94954222442, -14.69445491121, -9.01064174761, -24.68084871193, -10.37019349887],
    [2042, 3359.58917329810, -41.96715944096, -0.34841082638, -23.56954091155, -1.51154251208, -20.38216483144, -14.94148849319, -9.26417660480, -24.85670526533, -10.43098463423],
    [2043, 3506.62334726541, -42.24966149538, -0.35225070799, -24.06688093752, -1.54964916942, -20.81478743845, -15.18852207517, -9.51771146198, -25.03256181873, -10.49177576958],
    [2044, 3651.58827306494, -42.53216354980, -0.35609058960, -24.56422096349, -1.58775582677, -21.24741004547, -15.43555565715, -9.77124631917, -25.20841837214, -10.55256690493],
    [2045, 3793.31834724284, -42.81466560422, -0.35993047120, -25.06156098945, -1.62586248411, -21.68003265248, -15.68258923913, -10.02478117636, -25.38427492554, -10.61335804029],
    [2046, 3933.82806625397, -43.09716765864, -0.36377035281, -25.55890101542, -1.66396914145, -22.11265525950, -15.92962282111, -10.27831603355, -25.56013147894, -10.67414917564],
    [2047, 4070.36673693851, -43.37966971306, -0.36761023442, -26.05624104139, -1.70207579879, -22.54527786652, -16.17665640309, -10.53185089074, -25.73598803234, -10.73494031099],
    [2048, 4203.36357931442, -43.66217176748, -0.37145011603, -26.55358106736, -1.74018245613, -22.97790047353, -16.42368998506, -10.78538574793, -25.91184458575, -10.79573144635],
    [2049, 4332.45499453030, -43.94467382190, -0.37528999763, -27.05092109332, -1.77828911347, -23.41052308055, -16.67072356704, -11.03892060512, -26.08770113915, -10.85652258170],
    [2050, 4452.53974321577, -44.22717587631, -0.37912987924, -27.54826111929, -1.81639577081, -23.84314568757, -16.91775714902, -11.29245546230, -26.26355769255, -10.91731371705],
    [2051, 4577.47489004413, -44.50967793073, -0.38296976085, -28.04560114526, -1.85450242815, -24.27576829458, -17.16479073100, -11.54599031949, -26.43941424595, -10.97810485241],
    [2052, 4692.68350952313, -44.79217998515, -0.38680964246, -28.54294117123, -1.89260908549, -24.70839090160, -17.41182431298, -11.79952517668, -26.61527079936, -11.03889598776],
    [2053, 4802.54672782560, -45.07468203957, -0.39064952406, -29.04028119719, -1.93071574283, -25.14101350861, -17.65885789496, -12.05306003387, -26.79112735276, -11.09968712311],
    [2054, 4906.70746869867, -45.35718409399, -0.39448940567, -29.53762122316, -1.96882240017, -25.57363611563, -17.90589147694, -12.30659489106, -26.96698390616, -11.16047825847],
    [2055, 5004.80947891039, -45.63968614841, -0.39832928728, -30.03496124913, -2.00692905751, -26.00625872265, -18.15292505892, -12.56012974825, -27.14284045956, -11.22126939382],
    [2056, 5096.49710292905, -45.92218820283, -0.40216916888, -30.53230127510, -2.04503571486, -26.43888132966, -18.39995864090, -12.81366460544, -27.31869701297, -11.28206052917],
    [2057, 5181.41516896999, -46.20469025725, -0.40600905049, -31.02964130106, -2.08314237220, -26.87150393668, -18.64699222287, -13.06719946263, -27.49455356637, -11.34285166453],
    [2058, 5259.20904901760, -46.48719231166, -0.40984893210, -31.52698132703, -2.12124902954, -27.30412654370, -18.89402580485, -13.32073431981, -27.67041011977, -11.40364279988],
    [2059, 5329.52377273047, -46.76969436608, -0.41368881371, -32.02432135300, -2.15935568688, -27.73674915071, -19.14105938683, -13.57426917700, -27.84626667317, -11.46443393524],
    [2060, 5388.71259011725, -47.05219642050, -0.41752869531, -32.52166137897, -2.19746234422, -28.16937175773, -19.38809296881, -13.82780403419, -28.02212322658, -11.52522507059]]

# 'Emissions Factors'!A66:K112
conv_ref_grid_CO2_per_KWh_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2016, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2017, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2018, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2019, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2020, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2021, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2022, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2023, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2024, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2025, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2026, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2027, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2028, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2029, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2030, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2031, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2032, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2033, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2034, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2035, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2036, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2037, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2038, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2039, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2040, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2041, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2042, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2043, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2044, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2045, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2046, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2047, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2048, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2049, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2050, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2051, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2052, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2053, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2054, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2055, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2056, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2057, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2058, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2059, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067],
    [2060, 0.484512031, 0.392126590, 0.659977317, 0.385555834, 0.185499981, 0.491537631, 0.474730313, 0.725081980, 0.297016531, 0.594563067]]

# 'CO2 Calcs'!R234:AB280
co2_replaced_grid_emissions_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 28.66834665411, -29.65512322362, -0.22286217234, -8.54361226701, -0.31722184673, -7.57810633362, -7.32657847863, -2.22608456251, -16.56155043844, -7.85777842607],
    [2016, 72.92952271155, -29.89908740101, -0.22635888419, -8.96259751737, -0.34226679555, -7.95488217239, -7.54538921803, -2.45942551310, -16.70638699189, -7.91212469538],
    [2017, 124.69461210891, -30.14305157839, -0.22985559603, -9.38158276773, -0.36731174436, -8.33165801116, -7.76419995742, -2.69276646370, -16.85122354533, -7.96647096468],
    [2018, 183.62666285832, -30.38701575578, -0.23335230787, -9.80056801809, -0.39235669317, -8.70843384992, -7.98301069682, -2.92610741430, -16.99606009878, -8.02081723398],
    [2019, 249.38872297192, -30.63097993317, -0.23684901972, -10.21955326844, -0.41740164198, -9.08520968869, -8.20182143622, -3.15944836490, -17.14089665223, -8.07516350329],
    [2020, 249.39616721752, -30.87494411055, -0.24034573156, -10.63853851880, -0.44244659079, -9.46198552746, -8.42063217562, -3.39278931550, -17.28573320568, -8.12950977259],
    [2021, 400.05506334015, -31.11890828794, -0.24384244340, -11.05752376916, -0.46749153960, -9.83876136623, -8.63944291502, -3.62613026609, -17.43056975912, -8.18385604189],
    [2022, 484.28543961905, -31.36287246533, -0.24733915525, -11.47650901952, -0.49253648841, -10.21553720499, -8.85825365442, -3.85947121669, -17.57540631257, -8.23820231120],
    [2023, 573.99801731062, -31.60683664271, -0.25083586709, -11.89549426988, -0.51758143723, -10.59231304376, -9.07706439381, -4.09281216729, -17.72024286602, -8.29254858050],
    [2024, 668.85584442701, -31.85080082010, -0.25433257893, -12.31447952023, -0.54262638604, -10.96908888253, -9.29587513321, -4.32615311789, -17.86507941947, -8.34689484981],
    [2025, 694.76359214062, -32.09476499748, -0.25782929077, -12.73346477059, -0.56767133485, -11.34586472130, -9.51468587261, -4.55949406849, -18.00991597292, -8.40124111911],
    [2026, 872.65943898272, -32.33872917487, -0.26132600262, -13.15245002095, -0.59271628366, -11.72264056006, -9.73349661201, -4.79283501908, -18.15475252636, -8.45558738841],
    [2027, 980.93130244629, -32.58269335226, -0.26482271446, -13.57143527131, -0.61776123247, -12.09941639883, -9.95230735141, -5.02617596968, -18.29958907981, -8.50993365772],
    [2028, 1093.00060738317, -32.82665752964, -0.26831942630, -13.99042052166, -0.64280618128, -12.47619223760, -10.17111809081, -5.25951692028, -18.44442563326, -8.56427992702],
    [2029, 1208.53040180549, -33.07062170703, -0.27181613815, -14.40940577202, -0.66785113009, -12.85296807637, -10.38992883020, -5.49285787088, -18.58926218671, -8.61862619632],
    [2030, 1384.03437350855, -33.31458588442, -0.27531284999, -14.82839102238, -0.69289607890, -13.22974391513, -10.60873956960, -5.72619882148, -18.73409874015, -8.67297246563],
    [2031, 1448.62365115495, -33.55855006180, -0.27880956183, -15.24737627274, -0.71794102772, -13.60651975390, -10.82755030900, -5.95953977207, -18.87893529360, -8.72731873493],
    [2032, 1572.51320210634, -33.80251423919, -0.28230627368, -15.66636152310, -0.74298597653, -13.98329559267, -11.04636104840, -6.19288072267, -19.02377184705, -8.78166500423],
    [2033, 1698.51543459168, -34.04647841657, -0.28580298552, -16.08534677345, -0.76803092534, -14.36007143144, -11.26517178780, -6.42622167327, -19.16860840050, -8.83601127354],
    [2034, 1826.29339662308, -34.29044259396, -0.28929969736, -16.50433202381, -0.79307587415, -14.73684727020, -11.48398252720, -6.65956262387, -19.31344495395, -8.89035754284],
    [2035, 1955.51013621267, -34.53440677135, -0.29279640921, -16.92331727417, -0.81812082296, -15.11362310897, -11.70279326660, -6.89290357446, -19.45828150739, -8.94470381215],
    [2036, 2085.82870137258, -34.77837094873, -0.29629312105, -17.34230252453, -0.84316577177, -15.49039894774, -11.92160400599, -7.12624452506, -19.60311806084, -8.99905008145],
    [2037, 2216.91214011493, -35.02233512612, -0.29978983289, -17.76128777488, -0.86821072058, -15.86717478651, -12.14041474539, -7.35958547566, -19.74795461429, -9.05339635075],
    [2038, 2348.42350045186, -35.26629930350, -0.30328654473, -18.18027302524, -0.89325566940, -16.24395062527, -12.35922548479, -7.59292642626, -19.89279116774, -9.10774262006],
    [2039, 2480.02583039548, -35.51026348089, -0.30678325658, -18.59925827560, -0.91830061821, -16.62072646404, -12.57803622419, -7.82626737686, -20.03762772118, -9.16208888936],
    [2040, 2634.37405282108, -35.75422765828, -0.31027996842, -19.01824352596, -0.94334556702, -16.99750230281, -12.79684696359, -8.05960832745, -20.18246427463, -9.21643515866],
    [2041, 2742.15559115131, -35.99819183566, -0.31377668026, -19.43722877631, -0.96839051583, -17.37427814158, -13.01565770299, -8.29294927805, -20.32730082808, -9.27078142797],
    [2042, 2872.00911798777, -36.24215601305, -0.31727339211, -19.85621402667, -0.99343546464, -17.75105398034, -13.23446844238, -8.52629022865, -20.47213738153, -9.32512769727],
    [2043, 3000.60580647943, -36.48612019044, -0.32077010395, -20.27519927703, -1.01848041345, -18.12782981911, -13.45327918178, -8.75963117925, -20.61697393497, -9.37947396657],
    [2044, 3127.60870463842, -36.73008436782, -0.32426681579, -20.69418452739, -1.04352536226, -18.50460565788, -13.67208992118, -8.99297212985, -20.76181048842, -9.43382023588],
    [2045, 3252.68086047685, -36.97404854521, -0.32776352764, -21.11316977775, -1.06857031108, -18.88138149665, -13.89090066058, -9.22631308044, -20.90664704187, -9.48816650518],
    [2046, 3375.48532200687, -37.21801272259, -0.33126023948, -21.53215502810, -1.09361525989, -19.25815733541, -14.10971139998, -9.45965403104, -21.05148359532, -9.54251277449],
    [2047, 3495.68513724058, -37.46197689998, -0.33475695132, -21.95114027846, -1.11866020870, -19.63493317418, -14.32852213938, -9.69299498164, -21.19632014877, -9.59685904379],
    [2048, 3612.94335419012, -37.70594107737, -0.33825366317, -22.37012552882, -1.14370515751, -20.01170901295, -14.54733287877, -9.92633593224, -21.34115670221, -9.65120531309],
    [2049, 3726.92302086762, -37.94990525475, -0.34175037501, -22.78911077918, -1.16875010632, -20.38848485172, -14.76614361817, -10.15967688284, -21.48599325566, -9.70555158240],
    [2050, 3825.40945952962, -38.19386943214, -0.34524708685, -23.20809602953, -1.19379505513, -20.76526069048, -14.98495435757, -10.39301783343, -21.63082980911, -9.75989785170],
    [2051, 3943.69889545497, -38.43783360953, -0.34874379869, -23.62708127989, -1.21884000394, -21.14203652925, -15.20376509697, -10.62635878403, -21.77566636256, -9.81424412100],
    [2052, 4045.82119938908, -38.68179778691, -0.35224051054, -24.04606653025, -1.24388495275, -21.51881236802, -15.42257583637, -10.85969973463, -21.92050291600, -9.86859039031],
    [2053, 4143.31714509964, -38.92576196430, -0.35573722238, -24.46505178061, -1.26892990157, -21.89558820679, -15.64138657577, -11.09304068523, -22.06533946945, -9.92293665961],
    [2054, 4235.84978059879, -39.16972614168, -0.35923393422, -24.88403703097, -1.29397485038, -22.27236404555, -15.86019731516, -11.32638163583, -22.21017602290, -9.97728292891],
    [2055, 4323.08215389864, -39.41369031907, -0.36273064607, -25.30302228132, -1.31901979919, -22.64913988432, -16.07900805456, -11.55972258642, -22.35501257635, -10.03162919822],
    [2056, 4404.67731301133, -39.65765449646, -0.36622735791, -25.72200753168, -1.34406474800, -23.02591572309, -16.29781879396, -11.79306353702, -22.49984912980, -10.08597546752],
    [2057, 4480.29830594897, -39.90161867384, -0.36972406975, -26.14099278204, -1.36910969681, -23.40269156186, -16.51662953336, -12.02640448762, -22.64468568324, -10.14032173683],
    [2058, 4549.60818072370, -40.14558285123, -0.37322078160, -26.55997803240, -1.39415464562, -23.77946740062, -16.73544027276, -12.25974543822, -22.78952223669, -10.19466800613],
    [2059, 4612.26998534765, -40.38954702862, -0.37671749344, -26.97896328275, -1.41919959443, -24.15624323939, -16.95425101216, -12.49308638882, -22.93435879014, -10.24901427543],
    [2060, 4667.94676783292, -40.63351120600, -0.38021420528, -27.39794853311, -1.44424454325, -24.53301907816, -17.17306175155, -12.72642733941, -23.07919534359, -10.30336054474]]

# "CO2 Calcs"!U344:AE390 with Advanced Controls F159=100, G159=3%, I159=140.0, I163=10.0
co2eq_reduced_fuel_emissions_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 0.77097890856, -0.98541202113, -0.00439999077, -0.28873449224, -0.02228248564, -0.20088538372, -0.20109378946, -0.04000358944, -0.72654879282, -0.17220520174],
    [2016, 1.96129635587, -0.99351872267, -0.00446902672, -0.30289425157, -0.02404170783, -0.21087320332, -0.20709952336, -0.04419681541, -0.73290271623, -0.17339621398],
    [2017, 3.35341682262, -1.00162542421, -0.00453806266, -0.31705401090, -0.02580093002, -0.22086102291, -0.21310525726, -0.04839004137, -0.73925663965, -0.17458722621],
    [2018, 4.93827864649, -1.00973212575, -0.00460709860, -0.33121377024, -0.02756015221, -0.23084884251, -0.21911099117, -0.05258326734, -0.74561056306, -0.17577823845],
    [2019, 6.70682016521, -1.01783882729, -0.00467613454, -0.34537352957, -0.02931937440, -0.24083666211, -0.22511672507, -0.05677649330, -0.75196448647, -0.17696925069],
    [2020, 6.70702036358, -1.02594552883, -0.00474517048, -0.35953328890, -0.03107859659, -0.25082448170, -0.23112245897, -0.06096971927, -0.75831840988, -0.17816026293],
    [2021, 10.75869563800, -1.03405223037, -0.00481420642, -0.37369304823, -0.03283781878, -0.26081230130, -0.23712819287, -0.06516294523, -0.76467233329, -0.17935127517],
    [2022, 13.02390626749, -1.04215893191, -0.00488324236, -0.38785280756, -0.03459704097, -0.27080012090, -0.24313392678, -0.06935617120, -0.77102625670, -0.18054228740],
    [2023, 15.43654994265, -1.05026563345, -0.00495227831, -0.40201256689, -0.03635626316, -0.28078794050, -0.24913966068, -0.07354939716, -0.77738018012, -0.18173329964],
    [2024, 17.98756500120, -1.05837233499, -0.00502131425, -0.41617232622, -0.03811548535, -0.29077576009, -0.25514539458, -0.07774262313, -0.78373410353, -0.18292431188],
    [2025, 18.68430302018, -1.06647903653, -0.00509035019, -0.43033208555, -0.03987470754, -0.30076357969, -0.26115112849, -0.08193584909, -0.79008802694, -0.18411532412],
    [2026, 23.46846261926, -1.07458573808, -0.00515938613, -0.44449184488, -0.04163392973, -0.31075139929, -0.26715686239, -0.08612907506, -0.79644195035, -0.18530633636],
    [2027, 26.38022185420, -1.08269243962, -0.00522842207, -0.45865160422, -0.04339315192, -0.32073921888, -0.27316259629, -0.09032230102, -0.80279587376, -0.18649734859],
    [2028, 29.39410582335, -1.09079914116, -0.00529745801, -0.47281136355, -0.04515237411, -0.33072703848, -0.27916833019, -0.09451552699, -0.80914979717, -0.18768836083],
    [2029, 32.50105286442, -1.09890584270, -0.00536649395, -0.48697112288, -0.04691159630, -0.34071485808, -0.28517406410, -0.09870875295, -0.81550372059, -0.18887937307],
    [2030, 37.22088767678, -1.10701254424, -0.00543552989, -0.50113088221, -0.04867081849, -0.35070267767, -0.29117979800, -0.10290197892, -0.82185764400, -0.19007038531],
    [2031, 38.95788951316, -1.11511924578, -0.00550456584, -0.51529064154, -0.05043004068, -0.36069049727, -0.29718553190, -0.10709520488, -0.82821156741, -0.19126139755],
    [2032, 42.28965579625, -1.12322594732, -0.00557360178, -0.52945040087, -0.05218926288, -0.37067831687, -0.30319126580, -0.11128843085, -0.83456549082, -0.19245240978],
    [2033, 45.67823850209, -1.13133264886, -0.00564263772, -0.54361016020, -0.05394848507, -0.38066613646, -0.30919699971, -0.11548165681, -0.84091941423, -0.19364342202],
    [2034, 49.11457596840, -1.13943935040, -0.00571167366, -0.55776991953, -0.05570770726, -0.39065395606, -0.31520273361, -0.11967488278, -0.84727333764, -0.19483443426],
    [2035, 52.58960653287, -1.14754605194, -0.00578070960, -0.57192967886, -0.05746692945, -0.40064177566, -0.32120846751, -0.12386810874, -0.85362726106, -0.19602544650],
    [2036, 56.09426853322, -1.15565275348, -0.00584974554, -0.58608943819, -0.05922615164, -0.41062959526, -0.32721420141, -0.12806133471, -0.85998118447, -0.19721645874],
    [2037, 59.61950030716, -1.16375945502, -0.00591878148, -0.60024919753, -0.06098537383, -0.42061741485, -0.33321993532, -0.13225456067, -0.86633510788, -0.19840747097],
    [2038, 63.15624019239, -1.17186615656, -0.00598781742, -0.61440895686, -0.06274459602, -0.43060523445, -0.33922566922, -0.13644778664, -0.87268903129, -0.19959848321],
    [2039, 66.69542652663, -1.17997285810, -0.00605685337, -0.62856871619, -0.06450381821, -0.44059305405, -0.34523140312, -0.14064101260, -0.87904295470, -0.20078949545],
    [2040, 70.84631898998, -1.18807955964, -0.00612588931, -0.64272847552, -0.06626304040, -0.45058087364, -0.35123713703, -0.14483423857, -0.88539687811, -0.20198050769],
    [2041, 73.74489189294, -1.19618626118, -0.00619492525, -0.65688823485, -0.06802226259, -0.46056869324, -0.35724287093, -0.14902746453, -0.89175080153, -0.20317151993],
    [2042, 77.23704760043, -1.20429296272, -0.00626396119, -0.67104799418, -0.06978148478, -0.47055651284, -0.36324860483, -0.15322069050, -0.89810472494, -0.20436253216],
    [2043, 80.69540310776, -1.21239966426, -0.00633299713, -0.68520775351, -0.07154070697, -0.48054433243, -0.36925433873, -0.15741391646, -0.90445864835, -0.20555354440],
    [2044, 84.11089675263, -1.22050636580, -0.00640203307, -0.69936751284, -0.07329992916, -0.49053215203, -0.37526007264, -0.16160714243, -0.91081257176, -0.20674455664],
    [2045, 87.47446687276, -1.22861306735, -0.00647106901, -0.71352727217, -0.07505915135, -0.50051997163, -0.38126580654, -0.16580036839, -0.91716649517, -0.20793556888],
    [2046, 90.77705180584, -1.23671976889, -0.00654010496, -0.72768703151, -0.07681837354, -0.51050779123, -0.38727154044, -0.16999359436, -0.92352041858, -0.20912658112],
    [2047, 94.00958988959, -1.24482647043, -0.00660914090, -0.74184679084, -0.07857759573, -0.52049561082, -0.39327727434, -0.17418682032, -0.92987434200, -0.21031759335],
    [2048, 97.16301946171, -1.25293317197, -0.00667817684, -0.75600655017, -0.08033681792, -0.53048343042, -0.39928300825, -0.17838004629, -0.93622826541, -0.21150860559],
    [2049, 100.22827885992, -1.26103987351, -0.00674721278, -0.77016630950, -0.08209604012, -0.54047125002, -0.40528874215, -0.18257327225, -0.94258218882, -0.21269961783],
    [2050, 102.87687830318, -1.26914657505, -0.00681624872, -0.78432606883, -0.08385526231, -0.55045906961, -0.41129447605, -0.18676649822, -0.94893611223, -0.21389063007],
    [2051, 106.05804048542, -1.27725327659, -0.00688528466, -0.79848582816, -0.08561448450, -0.56044688921, -0.41730020995, -0.19095972419, -0.95529003564, -0.21508164231],
    [2052, 108.80441938813, -1.28535997813, -0.00695432060, -0.81264558749, -0.08737370669, -0.57043470881, -0.42330594386, -0.19515295015, -0.96164395905, -0.21627265454],
    [2053, 111.42638146775, -1.29346667967, -0.00702335654, -0.82680534682, -0.08913292888, -0.58042252840, -0.42931167776, -0.19934617612, -0.96799788247, -0.21746366678],
    [2054, 113.91486506200, -1.30157338121, -0.00709239249, -0.84096510615, -0.09089215107, -0.59041034800, -0.43531741166, -0.20353940208, -0.97435180588, -0.21865467902],
    [2055, 116.26080850858, -1.30968008275, -0.00716142843, -0.85512486549, -0.09265137326, -0.60039816760, -0.44132314557, -0.20773262805, -0.98070572929, -0.21984569126],
    [2056, 118.45515014519, -1.31778678429, -0.00723046437, -0.86928462482, -0.09441059545, -0.61038598720, -0.44732887947, -0.21192585401, -0.98705965270, -0.22103670350],
    [2057, 120.48882830956, -1.32589348583, -0.00729950031, -0.88344438415, -0.09616981764, -0.62037380679, -0.45333461337, -0.21611907998, -0.99341357611, -0.22222771574],
    [2058, 122.35278133939, -1.33400018737, -0.00736853625, -0.89760414348, -0.09792903983, -0.63036162639, -0.45934034727, -0.22031230594, -0.99976749952, -0.22341872797],
    [2059, 124.03794757238, -1.34210688891, -0.00743757219, -0.91176390281, -0.09968826202, -0.64034944599, -0.46534608118, -0.22450553191, -1.00612142294, -0.22460974021],
    [2060, 125.53526534624, -1.35021359045, -0.00750660813, -0.92592366214, -0.10144748421, -0.65033726558, -0.47135181508, -0.22869875787, -1.01247534635, -0.22580075245]]

# "CO2 Calcs"!A64:K110
co2eq_mmt_reduced_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 281.53832246658, -33.06503281241, -0.25150522783, -11.68639706732, -0.59179726531, -10.20752635460, -8.90141066296, -3.52672232084, -19.00172901916, -8.62695533687],
    [2021, 449.75302880009, -33.32630238756, -0.25516429556, -12.14665088812, -0.62529629666, -10.61398959562, -9.13271446631, -3.76927458751, -19.16094384147, -8.68462706015],
    [2022, 543.99457351336, -33.58757196270, -0.25882336328, -12.60690470892, -0.65879532802, -11.02045283665, -9.36401826967, -4.01182685419, -19.32015866377, -8.74229878343],
    [2023, 644.19299936156, -33.84884153784, -0.26248243100, -13.06715852972, -0.69229435937, -11.42691607767, -9.59532207302, -4.25437912087, -19.47937348607, -8.79997050671],
    [2024, 749.94265807256, -34.11011111298, -0.26614149873, -13.52741235053, -0.72579339072, -11.83337931869, -9.82662587637, -4.49693138755, -19.63858830837, -8.85764222999],
    [2025, 778.05397432700, -34.37138068813, -0.26980056645, -13.98766617133, -0.75929242207, -12.23984255971, -10.05792967972, -4.73948365423, -19.79780313067, -8.91531395327],
    [2026, 976.48562402800, -34.63265026327, -0.27345963417, -14.44791999213, -0.79279145342, -12.64630580073, -10.28923348307, -4.98203592091, -19.95701795297, -8.97298567655],
    [2027, 1096.48073948873, -34.89391983841, -0.27711870190, -14.90817381293, -0.82629048477, -13.05276904176, -10.52053728643, -5.22458818759, -20.11623277527, -9.03065739983],
    [2028, 1220.43106935991, -35.15518941356, -0.28077776962, -15.36842763373, -0.85978951613, -13.45923228278, -10.75184108978, -5.46714045427, -20.27544759757, -9.08832912311],
    [2029, 1347.94504340568, -35.41645898870, -0.28443683734, -15.82868145454, -0.89328854748, -13.86569552380, -10.98314489313, -5.70969272095, -20.43466241987, -9.14600084639],
    [2030, 1540.07292857969, -35.67772856384, -0.28809590507, -16.28893527534, -0.92678757883, -14.27215876482, -11.21444869648, -5.95224498763, -20.59387724217, -9.20367256967],
    [2031, 1612.11311579793, -35.93899813899, -0.29175497279, -16.74918909614, -0.96028661018, -14.67862200585, -11.44575249984, -6.19479725431, -20.75309206447, -9.26134429295],
    [2032, 1747.99952390596, -36.20026771413, -0.29541404051, -17.20944291694, -0.99378564153, -15.08508524687, -11.67705630319, -6.43734952099, -20.91230688678, -9.31901601623],
    [2033, 1885.91414757526, -36.46153728927, -0.29907310824, -17.66969673775, -1.02728467289, -15.49154848789, -11.90836010654, -6.67990178767, -21.07152170908, -9.37668773951],
    [2034, 2025.48072762716, -36.72280686442, -0.30273217596, -18.12995055855, -1.06078370424, -15.89801172891, -12.13966390989, -6.92245405435, -21.23073653138, -9.43435946279],
    [2035, 2166.11978086154, -36.98407643956, -0.30639124368, -18.59020437935, -1.09428273559, -16.30447496993, -12.37096771324, -7.16500632102, -21.38995135368, -9.49203118607],
    [2036, 2308.07971276209, -37.24534601470, -0.31005031141, -19.05045820015, -1.12778176694, -16.71093821096, -12.60227151660, -7.40755858770, -21.54916617598, -9.54970290935],
    [2037, 2450.37448649780, -37.50661558984, -0.31370937913, -19.51071202095, -1.16128079829, -17.11740145198, -12.83357531995, -7.65011085438, -21.70838099828, -9.60737463263],
    [2038, 2592.84569174435, -37.76788516499, -0.31736844685, -19.97096584176, -1.19477982964, -17.52386469300, -13.06487912330, -7.89266312106, -21.86759582058, -9.66504635591],
    [2039, 2735.13139635127, -38.02915474013, -0.32102751458, -20.43121966256, -1.22827886100, -17.93032793402, -13.29618292665, -8.13521538774, -22.02681064288, -9.72271807919],
    [2040, 2897.77259030755, -38.29042431527, -0.32468658230, -20.89147348336, -1.26177789235, -18.33679117505, -13.52748673001, -8.37776765442, -22.18602546518, -9.78038980247],
    [2041, 3017.71177239437, -38.55169389042, -0.32834565002, -21.35172730416, -1.29527692370, -18.74325441607, -13.75879053336, -8.62031992110, -22.34524028748, -9.83806152575],
    [2042, 3157.29555186691, -38.81296346556, -0.33200471775, -21.81198112496, -1.32877595505, -19.14971765709, -13.99009433671, -8.86287218778, -22.50445510979, -9.89573324903],
    [2043, 3295.27185423621, -39.07423304070, -0.33566378547, -22.27223494577, -1.36227498640, -19.55618089811, -14.22139814006, -9.10542445446, -22.66366993209, -9.95340497231],
    [2044, 3431.29116909046, -39.33550261585, -0.33932285319, -22.73248876657, -1.39577401776, -19.96264413913, -14.45270194341, -9.34797672114, -22.82288475439, -10.01107669559],
    [2045, 3564.21162661837, -39.59677219099, -0.34298192092, -23.19274258737, -1.42927304911, -20.36910738016, -14.68400574677, -9.59052898782, -22.98209957669, -10.06874841887],
    [2046, 3696.07145691736, -39.85804176613, -0.34664098864, -23.65299640817, -1.46277208046, -20.77557062118, -14.91530955012, -9.83308125450, -23.14131439899, -10.12642014215],
    [2047, 3824.14370047022, -40.11931134127, -0.35030005636, -24.11325022898, -1.49627111181, -21.18203386220, -15.14661335347, -10.07563352118, -23.30052922129, -10.18409186543],
    [2048, 3948.88131093746, -40.38058091642, -0.35395912408, -24.57350404978, -1.52977014316, -21.58849710322, -15.37791715682, -10.31818578785, -23.45974404359, -10.24176358871],
    [2049, 4069.94442311025, -40.64185049156, -0.35761819181, -25.03375787058, -1.56326917451, -21.99496034425, -15.60922096017, -10.56073805453, -23.61895886589, -10.29943531199],
    [2050, 4183.09215400771, -40.90312006670, -0.36127725953, -25.49401169138, -1.59676820587, -22.40142358527, -15.84052476353, -10.80329032121, -23.77817368819, -10.35710703527],
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

# "CO2 Calcs"!A9:K55
co2_mmt_reduced_list = [
    ["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)", "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"],
    [2015, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2016, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2017, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2019, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2020, 231.82963042573, -28.18786267921, -0.22791752837, -9.69687524586, -0.36104780552, -8.80504440498, -7.81529314892, -3.23310188969, -15.29960113436, -7.66288545301],
    [2021, 371.87667524657, -28.41059437732, -0.23123342633, -10.07877429105, -0.38148512834, -9.15566087775, -8.01837410969, -3.45546024978, -15.42779595671, -7.71411231024],
    [2022, 450.17417765496, -28.63332607543, -0.23454932429, -10.46067333624, -0.40192245116, -9.50627735053, -8.22145507047, -3.67781860986, -15.55599077906, -7.76533916747],
    [2023, 533.56773563469, -28.85605777355, -0.23786522225, -10.84257238143, -0.42235977398, -9.85689382330, -8.42453603124, -3.90017696995, -15.68418560140, -7.81656602470],
    [2024, 621.74413084048, -29.07878947166, -0.24118112021, -11.22447142663, -0.44279709681, -10.20751029607, -8.62761699201, -4.12253533004, -15.81238042375, -7.86779288193],
    [2025, 645.82703333500, -29.30152116977, -0.24449701817, -11.60637047182, -0.46323441963, -10.55812676885, -8.83069795278, -4.34489369013, -15.94057524609, -7.91901973916],
    [2026, 811.19255954899, -29.52425286788, -0.24781291613, -11.98826951701, -0.48367174245, -10.90874324162, -9.03377891355, -4.56725205022, -16.06877006844, -7.97024659639],
    [2027, 911.83815636112, -29.74698456599, -0.25112881409, -12.37016856220, -0.50410906527, -11.25935971439, -9.23685987432, -4.78961041031, -16.19696489079, -8.02147345362],
    [2028, 1016.01371701809, -29.96971626410, -0.25444471205, -12.75206760739, -0.52454638810, -11.60997618717, -9.43994083510, -5.01196877040, -16.32515971313, -8.07270031085],
    [2029, 1123.40602317462, -30.19244796221, -0.25776061001, -13.13396665259, -0.54498371092, -11.96059265994, -9.64302179587, -5.23432713048, -16.45335453548, -8.12392716808],
    [2030, 1286.54814902244, -30.41517966032, -0.26107650796, -13.51586569778, -0.56542103374, -12.31120913272, -9.84610275664, -5.45668549057, -16.58154935783, -8.17515402531],
    [2031, 1346.58799860510, -30.63791135843, -0.26439240592, -13.89776474297, -0.58585835656, -12.66182560549, -10.04918371741, -5.67904385066, -16.70974418017, -8.22638088254],
    [2032, 1461.75123118846, -30.86064305654, -0.26770830388, -14.27966378816, -0.60629567939, -13.01244207826, -10.25226467818, -5.90140221075, -16.83793900252, -8.27760773977],
    [2033, 1578.87833589017, -31.08337475465, -0.27102420184, -14.66156283336, -0.62673300221, -13.36305855104, -10.45534563895, -6.12376057084, -16.96613382486, -8.32883459700],
    [2034, 1697.65609436493, -31.30610645276, -0.27434009980, -15.04346187855, -0.64717032503, -13.71367502381, -10.65842659973, -6.34611893093, -17.09432864721, -8.38006145423],
    [2035, 1817.77128826743, -31.52883815087, -0.27765599776, -15.42536092374, -0.66760764785, -14.06429149658, -10.86150756050, -6.56847729101, -17.22252346956, -8.43128831146],
    [2036, 1938.91069925237, -31.75156984898, -0.28097189572, -15.80725996893, -0.68804497068, -14.41490796936, -11.06458852127, -6.79083565110, -17.35071829190, -8.48251516870],
    [2037, 2060.76110897447, -31.97430154709, -0.28428779368, -16.18915901413, -0.70848229350, -14.76552444213, -11.26766948204, -7.01319401119, -17.47891311425, -8.53374202593],
    [2038, 2183.00929908840, -32.19703324520, -0.28760369164, -16.57105805932, -0.72891961632, -15.11614091490, -11.47075044281, -7.23555237128, -17.60710793660, -8.58496888316],
    [2039, 2305.34205124888, -32.41976494331, -0.29091958959, -16.95295710451, -0.74935693914, -15.46675738768, -11.67383140359, -7.45791073137, -17.73530275894, -8.63619574039],
    [2040, 2448.81855997400, -32.64249664142, -0.29423548755, -17.33485614970, -0.76979426196, -15.81737386045, -11.87691236436, -7.68026909146, -17.86349758129, -8.68742259762],
    [2041, 2549.00836832827, -32.86522833953, -0.29755138551, -17.71675519489, -0.79023158479, -16.16799033322, -12.07999332513, -7.90262745155, -17.99169240363, -8.73864945485],
    [2042, 2669.71549655658, -33.08796003764, -0.30086728347, -18.09865424009, -0.81066890761, -16.51860680600, -12.28307428590, -8.12498581163, -18.11988722598, -8.78987631208],
    [2043, 2789.25431345024, -33.31069173576, -0.30418318143, -18.48055328528, -0.83110623043, -16.86922327877, -12.48615524667, -8.34734417172, -18.24808204833, -8.84110316931],
    [2044, 2907.31160066394, -33.53342343387, -0.30749907939, -18.86245233047, -0.85154355325, -17.21983975154, -12.68923620744, -8.56970253181, -18.37627687067, -8.89233002654],
    [2045, 3023.57413985238, -33.75615513198, -0.31081497735, -19.24435137566, -0.87198087608, -17.57045622432, -12.89231716822, -8.79206089190, -18.50447169302, -8.94355688377],
    [2046, 3137.72871267026, -33.97888683009, -0.31413087531, -19.62625042086, -0.89241819890, -17.92107269709, -13.09539812899, -9.01441925199, -18.63266651537, -8.99478374100],
    [2047, 3249.46210077229, -34.20161852820, -0.31744677327, -20.00814946605, -0.91285552172, -18.27168916986, -13.29847908976, -9.23677761208, -18.76086133771, -9.04601059823],
    [2048, 3358.46108581316, -34.42435022631, -0.32076267122, -20.39004851124, -0.93329284454, -18.62230564264, -13.50156005053, -9.45913597217, -18.88905616006, -9.09723745546],
    [2049, 3464.41244944757, -34.64708192442, -0.32407856918, -20.77194755643, -0.95373016737, -18.97292211541, -13.70464101130, -9.68149433225, -19.01725098240, -9.14846431269],
    [2050, 3555.96187032156, -34.86981362253, -0.32739446714, -21.15384660163, -0.97416749019, -19.32353858819, -13.90772197207, -9.90385269234, -19.14544580475, -9.19969116992],
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

# Not from spreadsheet, crafted up data for test case
co2_ppm_calculator_list = [
    ["Year", "PPM", "Total", 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055, 2056, 2057, 2058, 2059, 2060],
    [2020, 0.0002208524404346944, 1.749548862635562, 0.0, 0.0, 0.0, 0.0, 0.0, 1.749548862635562, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2021, 0.00042556622035450157, 3.3712504844042908, 0.0, 0.0, 0.0, 0.0, 0.0, 1.6217016217687286, 1.749548862635562, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [2022, 0.0006209249414467069, 4.918843201152522, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5475927167482313, 1.6217016217687286, 1.749548862635562, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

# Not from spreadsheet, crafted up data for test case
co2eq_ppm_calculator_list = [
    ["Year", "CO2-eq PPM", "CO2 PPM", "CH4 PPB", "CO2 RF", "CH4 RF"],
    [2020, 0.04371480078913237, 0.0002208524404346944, 1.0, 0.0000029539005752, 0.00058169961],
    [2021, 0.043919536828582295, 0.00042556622035450157, 1.0, 0.0000056919451699, 0.00058169961],
    [2022, 0.04411491679201163, 0.0006209249414467069, 1.0, 0.0000056919451699, 0.00058169961]]
