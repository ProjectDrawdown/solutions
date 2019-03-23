"""Utility Scale Solar Photovoltaics solution model.
   Excel filename: SolarPVUtility_RRS_ELECGEN
"""

import pathlib

import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import ch4calcs
from model import co2calcs
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import tam
from model import unitadoption
from model import vma
from solution import rrs

scenarios = {
    'PDS3-16p2050-Optimum (Updated)': advanced_controls.AdvancedControls(
      pds_2014_cost=1444.93954, ref_2014_cost=1444.93954,
      conv_2014_cost=2010.03170851964,
      soln_first_cost_efficiency_rate=0.182810601365724,
      soln_first_cost_below_conv=True,
      conv_first_cost_efficiency_rate=0.02,

      ch4_is_co2eq=True, n2o_is_co2eq=True,
      co2eq_conversion_source="AR5 with feedback",
      soln_indirect_co2_per_iunit=78779.26,
      conv_indirect_co2_per_unit=0.0, conv_indirect_co2_is_iunits=False,

      soln_lifetime_capacity=50358.6825, soln_avg_annual_use=1918.426,
      conv_lifetime_capacity=178770.55602092, conv_avg_annual_use=4967.65,

      report_start_year=2020, report_end_year=2050,

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
      soln_fixed_oper_cost_per_iunit=23.2278,
      conv_var_oper_cost_per_funit=0.00475243216795082, conv_fuel_cost_per_funit=0.09,
      conv_fixed_oper_cost_per_iunit=32.8906457343352,

      npv_discount_rate=0.094,

      emissions_use_co2eq=True,
      emissions_grid_source="meta_analysis", emissions_grid_range="mean",

      soln_ref_adoption_regional_data=False,
      soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Existing Adoption Prognostications',
      soln_pds_adoption_prognostication_source='Based on: Greenpeace (2015) Advanced Energy Revolution',
      soln_pds_adoption_prognostication_trend='3rd Poly',
      soln_pds_adoption_prognostication_growth='Medium',
      source_until_2014 = 'ALL SOURCES',
      ref_source_post_2014 = 'Baseline Cases',
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario',

      solution_category='REPLACEMENT',
      ),
    'PDS2-15p2050-Drawdown (Updated)': advanced_controls.AdvancedControls(
      pds_2014_cost=1444.93954, ref_2014_cost=1444.93954,
      conv_2014_cost=2010.03170851964,
      soln_first_cost_efficiency_rate=0.182810601365724,
      soln_first_cost_below_conv=True,
      conv_first_cost_efficiency_rate=0.02,

      ch4_is_co2eq=True, n2o_is_co2eq=True,
      co2eq_conversion_source="AR5 with feedback",
      soln_indirect_co2_per_iunit=78779.26,
      conv_indirect_co2_per_unit=0.0, conv_indirect_co2_is_iunits=False,

      soln_lifetime_capacity=50358.6825, soln_avg_annual_use=1918.426,
      conv_lifetime_capacity=178770.55602092, conv_avg_annual_use=4967.65,

      report_start_year=2020, report_end_year=2050,

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
      soln_fixed_oper_cost_per_iunit=23.2278,
      conv_var_oper_cost_per_funit=0.00475243216795082, conv_fuel_cost_per_funit=0.09,
      conv_fixed_oper_cost_per_iunit=32.8906457343352,

      npv_discount_rate=0.094,

      emissions_use_co2eq=True,
      emissions_grid_source="meta_analysis", emissions_grid_range="mean",

      soln_ref_adoption_regional_data=False,
      soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Existing Adoption Prognostications',
      soln_pds_adoption_prognostication_source='Based on: Greenpeace (2015) Advanced Energy Revolution',
      soln_pds_adoption_prognostication_trend='3rd Poly',
      soln_pds_adoption_prognostication_growth='Medium',
      source_until_2014 = 'ALL SOURCES',
      ref_source_post_2014 = 'Baseline Cases',
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario',

      solution_category='REPLACEMENT',
      ),
    'PDS1-10p2050-Plausible (Updated)': advanced_controls.AdvancedControls(
      pds_2014_cost=1444.93954421485, ref_2014_cost=1444.93954421485,
      conv_2014_cost=2010.03170851964,
      soln_first_cost_efficiency_rate=0.18256529904906,
      soln_first_cost_below_conv=True,
      conv_first_cost_efficiency_rate=0.02,

      ch4_is_co2eq=True, n2o_is_co2eq=True,
      co2eq_conversion_source="AR5 with feedback",
      soln_indirect_co2_per_iunit=45779.2611111111,
      conv_indirect_co2_per_unit=0.0, conv_indirect_co2_is_iunits=False,

      soln_lifetime_capacity=50358.672, soln_avg_annual_use=1918.4256,
      conv_lifetime_capacity=178021.674400926, conv_avg_annual_use=4967.64844181569,

      report_start_year=2020, report_end_year=2050,

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
      soln_fixed_oper_cost_per_iunit=23.2278265906509,
      conv_var_oper_cost_per_funit=0.00475243216795082, conv_fuel_cost_per_funit=0.07,
      conv_fixed_oper_cost_per_iunit=32.8906457343352,

      npv_discount_rate=0.094,

      emissions_use_co2eq=True,
      emissions_grid_source="meta_analysis", emissions_grid_range="mean",

      soln_ref_adoption_regional_data=False,
      soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Existing Adoption Prognostications',
      soln_pds_adoption_prognostication_source='Ambitious Cases',
      soln_pds_adoption_prognostication_trend='3rd Poly',
      soln_pds_adoption_prognostication_growth='High',
      source_until_2014 = 'ALL SOURCES',
      ref_source_post_2014 = 'Baseline Cases',
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario',

      solution_category='REPLACEMENT',
      ),
    'PDS-16p2050- Optimum (Book Ed.1)': advanced_controls.AdvancedControls(
      pds_2014_cost=1444.93954421485, ref_2014_cost=1444.93954421485,
      conv_2014_cost=2010.03170851964,
      soln_first_cost_efficiency_rate=0.196222222222222,
      soln_first_cost_below_conv=True,
      conv_first_cost_efficiency_rate=0.02,

      ch4_is_co2eq=True, n2o_is_co2eq=True,
      co2eq_conversion_source="AR5 with feedback",
      soln_indirect_co2_per_iunit=47157.2222222222,
      conv_indirect_co2_per_unit=0.0, conv_indirect_co2_is_iunits=False,

      soln_lifetime_capacity=48343.8, soln_avg_annual_use=1841.66857142857,
      conv_lifetime_capacity=182411.275767661, conv_avg_annual_use=4946.840187342,

      report_start_year=2020, report_end_year=2050,

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
      soln_fixed_oper_cost_per_iunit=23.1879129357938,
      conv_var_oper_cost_per_funit=0.00375269040354899, conv_fuel_cost_per_funit=0.0731,
      conv_fixed_oper_cost_per_iunit=32.951404311078,

      npv_discount_rate=0.094,

      emissions_use_co2eq=True,
      emissions_grid_source="meta_analysis", emissions_grid_range="mean",

      soln_ref_adoption_regional_data=False,
      soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Existing Adoption Prognostications',
      soln_pds_adoption_prognostication_source='Based on: Greenpeace (2015) Advanced Energy Revolution',
      soln_pds_adoption_prognostication_trend='3rd Poly',
      soln_pds_adoption_prognostication_growth='Medium',
      source_until_2014 = 'ALL SOURCES',
      ref_source_post_2014 = 'Baseline Cases',
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario',

      solution_category='REPLACEMENT',
      ),
    'PDS-15p2050- Drawdown (Book Ed.1)': advanced_controls.AdvancedControls(
      pds_2014_cost=1444.93954421485, ref_2014_cost=1444.93954421485,
      conv_2014_cost=2010.03170851964,
      soln_first_cost_efficiency_rate=0.196222222222222,
      soln_first_cost_below_conv=True,
      conv_first_cost_efficiency_rate=0.02,

      ch4_is_co2eq=True, n2o_is_co2eq=True,
      co2eq_conversion_source="AR5 with feedback",
      soln_indirect_co2_per_iunit=47157.2222222222,
      conv_indirect_co2_per_unit=0.0, conv_indirect_co2_is_iunits=False,

      soln_lifetime_capacity=48343.8, soln_avg_annual_use=1841.66857142857,
      conv_lifetime_capacity=182411.275767661, conv_avg_annual_use=4946.840187342,

      report_start_year=2020, report_end_year=2050,

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
      soln_fixed_oper_cost_per_iunit=23.1879129357938,
      conv_var_oper_cost_per_funit=0.00375269040354899, conv_fuel_cost_per_funit=0.0731,
      conv_fixed_oper_cost_per_iunit=32.951404311078,

      npv_discount_rate=0.094,

      emissions_use_co2eq=True,
      emissions_grid_source="meta_analysis", emissions_grid_range="mean",

      soln_ref_adoption_regional_data=False,
      soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Existing Adoption Prognostications',
      soln_pds_adoption_prognostication_source='Based on: Greenpeace (2015) Advanced Energy Revolution',
      soln_pds_adoption_prognostication_trend='3rd Poly',
      soln_pds_adoption_prognostication_growth='Medium',
      source_until_2014 = 'ALL SOURCES',
      ref_source_post_2014 = 'Baseline Cases',
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario',

      solution_category='REPLACEMENT',
      ),
    'PDS-10p2050- Plausible (Book Ed.1)': advanced_controls.AdvancedControls(
      pds_2014_cost=1444.93954421485, ref_2014_cost=1444.93954421485,
      conv_2014_cost=2010.03170851964,
      soln_first_cost_efficiency_rate=0.196222222222222,
      soln_first_cost_below_conv=True,
      conv_first_cost_efficiency_rate=0.02,

      ch4_is_co2eq=True, n2o_is_co2eq=True,
      co2eq_conversion_source="AR5 with feedback",
      soln_indirect_co2_per_iunit=47157.2222222222,
      conv_indirect_co2_per_unit=0.0, conv_indirect_co2_is_iunits=False,

      soln_lifetime_capacity=48343.8, soln_avg_annual_use=1841.66857142857,
      conv_lifetime_capacity=182411.275767661, conv_avg_annual_use=4946.840187342,

      report_start_year=2020, report_end_year=2050,

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0,
      soln_fixed_oper_cost_per_iunit=23.1879129357938,
      conv_var_oper_cost_per_funit=0.00375269040354899, conv_fuel_cost_per_funit=0.0731,
      conv_fixed_oper_cost_per_iunit=32.951404311078,

      npv_discount_rate=0.094,

      emissions_use_co2eq=True,
      emissions_grid_source="meta_analysis", emissions_grid_range="mean",

      soln_ref_adoption_regional_data=False,
      soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Existing Adoption Prognostications',
      soln_pds_adoption_prognostication_source='Ambitious Cases',
      soln_pds_adoption_prognostication_trend='3rd Poly',
      soln_pds_adoption_prognostication_growth='High',
      source_until_2014 = 'ALL SOURCES',
      ref_source_post_2014 = 'Baseline Cases',
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario',

      solution_category='REPLACEMENT',
      ),
    }

class SolarPVUtil:
  name = 'Solar Farms'
  def __init__(self, scenario=None):
    datadir = pathlib.Path(__file__).parents[2].joinpath('data')
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS3-16p2050-Optimum (Updated)'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    tamconfig_list = [
      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
        'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['source_until_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['source_after_2014', 'Baseline Cases', self.ac.pds_source_post_2014, 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES'],
      ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
        '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
        'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.tam_ref_data_sources,
        tam_pds_data_sources=rrs.tam_pds_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    adconfig_list = [
      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
        'Latin America', 'China', 'India', 'EU', 'USA'],
      ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
        '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'Medium', 'Medium', 'Medium', 'Medium',
        'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
    ad_data_sources = {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': str(thisdir.joinpath('ad_based_on_IEA_ETP_2016_6DS.csv')),
        'Based on: AMPERE (2014) IMAGE Refpol': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv')),
        'Based on: AMPERE (2014) MESSAGE REFPol': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv')),
        'Based on: AMPERE (2014) GEM E3 REFpol': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv')),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': str(thisdir.joinpath('ad_based_on_IEA_ETP_2016_4DS.csv')),
        'Based on: AMPERE (2014) IMAGE 550': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv')),
        'Based on: AMPERE (2014) MESSAGE 550': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv')),
        'Based on: AMPERE (2014) GEM E3 550': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_GEM_E3_550.csv')),
        'Based on: Greenpeace (2015) Reference': str(thisdir.joinpath(
          'ad_based_on_Greenpeace_2015_Reference.csv')),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': str(thisdir.joinpath('ad_based_on_IEA_ETP_2016_2DS.csv')),
        'Based on: AMPERE (2014) IMAGE 450': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv')),
        'Based on: AMPERE (2014) MESSAGE 450': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv')),
        'Based on: AMPERE (2014) GEM E3 450': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_GEM_E3_450.csv')),
        'Based on: Greenpeace (2015) Energy Revolution': str(thisdir.joinpath(
          'ad_based_on_Greenpeace_2015_Energy_Revolution.csv')),
        '[Source 6 - Ambitious]': str(thisdir.joinpath('ad_source_6_ambitious.csv')),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace (2015) Advanced Energy Revolution': str(thisdir.joinpath(
          'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv')),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources, adconfig=adconfig)

    ht_ref_datapoints = pd.DataFrame([
      [2014, 112.6330333333330, 75.0042455555555, 0.3323833333333, 21.0725044444444,
        1.5750777777778, 14.6506188888889, 14.9722222222222, 2.7483011111111,
        55.2720544444444, 13.1246500000000],
      [2050, 272.4140979910870, 97.4018860358948, 0.5231196255289, 60.1981419861308,
        6.4355535154359, 42.2455157032626, 31.5651938643273, 14.3335762256287,
        72.8270231949823, 16.4152440574767]],
      columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
          "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    ht_pds_datapoints = pd.DataFrame([
      [2014, 112.6330333333330, 75.0042455555555, 0.3323833333333, 21.0725044444444,
        1.5750777777778, 14.6506188888889, 14.9722222222222, 2.7483011111111,
        55.2720544444444, 13.1246500000000],
      [2050, 2603.6606403329600, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
      columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
          "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        pds_adoption_data_per_region=self.ad.adoption_data_per_region(),
        pds_adoption_trend_per_region=self.ad.adoption_trend_per_region(),
        pds_adoption_is_single_source=self.ad.adoption_is_single_source())

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=str(datadir),
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
        bug_cfunits_double_count=True)

    soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
    soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
    conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()
    soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()

    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
                                  ref_learning_increase_mult=2, conv_learning_increase_mult=2,
                                  soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
                                  soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
                                  conv_ref_tot_iunits=conv_ref_tot_iunits,
                                  soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
                                  soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
                                  conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
                                  fc_convert_iunit_factor=rrs.TERAWATT_TO_KILOWATT)

    self.oc = operatingcost.OperatingCost(ac=self.ac,
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
        conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),
        soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),
        soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),
        conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),
        single_iunit_purchase_year=2017,
        soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),
        conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit(),
        conversion_factor=rrs.TERAWATT_TO_KILOWATT)

    self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)
    self.c2 = co2calcs.CO2Calcs(ac=self.ac,
                                ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
                                soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
                                soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
                                soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),
                                soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),
                                soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),
                                soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
                                soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
                                conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
                                conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
                                conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
                                soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
                                fuel_in_liters=False)

    # VMA tables are present on xls but are not used in model computation
    self.VMAs = []

  def to_dict(self):
    """Return all data as a dict, to be serialized to JSON."""
    rs = dict()
    rs['tam_data'] = self.tm.to_dict()
    rs['adoption_data'] = self.ad.to_dict()
    rs['helper_tables'] = self.ht.to_dict()
    rs['emissions_factors'] = self.ef.to_dict()
    rs['unit_adoption'] = self.ua.to_dict()
    rs['first_cost'] = self.fc.to_dict()
    rs['operating_cost'] = self.oc.to_dict()
    rs['ch4_calcs'] = self.c4.to_dict()
    rs['co2_calcs'] = self.c2.to_dict()
    return rs
