"""Rooftop Solar Photovoltaics solution model.
   Excel filename: SolarPVRooftop_RRS_ELECGEN
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

scenarios = [
    'PDS-7p2050-Plausible (Book Ed.1)',
    'PDS-10p2050-Drawdown (Book Ed. 1)',
    'PDS-10p2050-Optimum (Book Ed.1)',
    'PDS-7p2050-Drawdown Plausible Scenario (Revision Case)',
    'PDS-10p2050-Drawdown Scenario (Revision Case)',
    'PDS-10p2050-Drawdown Optimum Scenario (Revision Case)',
    ]


class SolarPVRoof:
  name = 'Rooftop Solar'
  def __init__(self, scenario=None):
    datadir = pathlib.PurePath(pathlib.Path(__file__).parents[2], 'data')
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS-7p2050-Plausible (Book Ed.1)'
    self.scenario = scenario

    if scenario == 'PDS-10p2050-Optimum (Book Ed.1)':
      soln_pds_adoption_prognostication_growth='Medium'
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario'
    elif scenario == 'PDS-10p2050-Drawdown (Book Ed. 1)':
      soln_pds_adoption_prognostication_growth='Medium'
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario'
    elif scenario == 'PDS-7p2050-Plausible (Book Ed.1)':
      soln_pds_adoption_prognostication_growth='High'
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario'
    elif scenario == 'PDS-10p2050-Drawdown Optimum Scenario (Revision Case)':
      soln_pds_adoption_prognostication_growth='Medium'
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario'
    elif scenario == 'PDS-10p2050-Drawdown Scenario (Revision Case)':
      soln_pds_adoption_prognostication_growth='Medium'
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario'
    elif scenario == 'PDS-7p2050-Drawdown Plausible Scenario (Revision Case)':
      soln_pds_adoption_prognostication_growth='High'
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario'
    else:
      raise KeyError('Unknown scenario ' + str(scenario))

    ac_scenarios = {
        'PDS-7p2050-Plausible (Book Ed.1)':  advanced_controls.AdvancedControls(
          pds_2014_cost = 1883.53039287357, ref_2014_cost = 1883.53039287357,
          conv_2014_cost = 2010.03170851964,
          soln_first_cost_efficiency_rate = 0.1966,
          soln_first_cost_below_conv = True,
          conv_first_cost_efficiency_rate = 0.02,

          ch4_is_co2eq = True, n2o_is_co2eq = True,
          co2eq_conversion_source = "AR5 with feedback",
          soln_indirect_co2_per_iunit = 46831.7391304348,
          conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False,

          soln_lifetime_capacity = 41401.1076923077, soln_avg_annual_use = 1725.04615384615,
          conv_lifetime_capacity = 182411.275767661, conv_avg_annual_use = 4946.840187342,

          report_start_year = 2020, report_end_year = 2050,

          soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0,
          soln_fixed_oper_cost_per_iunit = 21.4841902320724,
          conv_var_oper_cost_per_funit = 0.00375269040354899,
          conv_fixed_oper_cost_per_iunit = 32.951404311078,
          conv_fuel_cost_per_funit = 0.07,

          npv_discount_rate = 0.04,

          emissions_use_co2eq = True,
          emissions_grid_source = "Meta-Analysis", emissions_grid_range = "Mean",

          soln_ref_adoption_regional_data = False,
          soln_pds_adoption_regional_data = False,
          soln_pds_adoption_basis = "Existing Adoption Prognostications",
          soln_pds_adoption_prognostication_source = "Ambitious Cases",
          soln_pds_adoption_prognostication_trend = "3rd Poly",
          soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth,
          solution_category = "REPLACEMENT",
          ),
        'PDS-10p2050-Drawdown (Book Ed. 1)':  advanced_controls.AdvancedControls(
          pds_2014_cost = 1883.53039287357, ref_2014_cost = 1883.53039287357,
          conv_2014_cost = 2010.03170851964,
          soln_first_cost_efficiency_rate = 0.1966,
          soln_first_cost_below_conv = True,
          conv_first_cost_efficiency_rate = 0.02,

          ch4_is_co2eq = True, n2o_is_co2eq = True,
          co2eq_conversion_source = "AR5 with feedback",
          soln_indirect_co2_per_iunit = 46831.7391304348,
          conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False,

          soln_lifetime_capacity = 41401.1076923077, soln_avg_annual_use = 1725.04615384615,
          conv_lifetime_capacity = 182411.275767661, conv_avg_annual_use = 4946.840187342,

          report_start_year = 2020, report_end_year = 2050,

          soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0,
          soln_fixed_oper_cost_per_iunit = 17.5639203094299,
          conv_var_oper_cost_per_funit = 0.00375269040354899,
          conv_fixed_oper_cost_per_iunit = 32.951404311078,
          conv_fuel_cost_per_funit = 0.07,

          npv_discount_rate = 0.04,

          emissions_use_co2eq = True,
          emissions_grid_source = "Meta-Analysis", emissions_grid_range = "Mean",

          soln_ref_adoption_regional_data = False,
          soln_pds_adoption_regional_data = False,
          soln_pds_adoption_basis = "Existing Adoption Prognostications",
          soln_pds_adoption_prognostication_source = "Based on: Greenpeace Advanced Energy Revolution (2015)",
          soln_pds_adoption_prognostication_trend = "3rd Poly",
          soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth,
          solution_category = "REPLACEMENT",
          ),
        'PDS-10p2050-Optimum (Book Ed.1)': advanced_controls.AdvancedControls(
          pds_2014_cost = 1883.53039287357, ref_2014_cost = 1883.53039287357,
          conv_2014_cost = 2010.03170851964,
          soln_first_cost_efficiency_rate = 0.1966,
          soln_first_cost_below_conv = True,
          conv_first_cost_efficiency_rate = 0.02,

          ch4_is_co2eq = True, n2o_is_co2eq = True,
          co2eq_conversion_source = "AR5 with feedback",
          soln_indirect_co2_per_iunit = 46831.7391304348,
          conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False,

          soln_lifetime_capacity = 41401.1076923077, soln_avg_annual_use = 1725.04615384615,
          conv_lifetime_capacity = 182411.275767661, conv_avg_annual_use = 4946.840187342,

          report_start_year = 2020, report_end_year = 2050,

          soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0,
          soln_fixed_oper_cost_per_iunit = 17.5639203094299,
          conv_var_oper_cost_per_funit = 0.00375269040354899,
          conv_fixed_oper_cost_per_iunit = 32.951404311078,
          conv_fuel_cost_per_funit = 0.07,

          npv_discount_rate = 0.04,

          emissions_use_co2eq = True,
          emissions_grid_source = "Meta-Analysis", emissions_grid_range = "Mean",

          soln_ref_adoption_regional_data = False,
          soln_pds_adoption_regional_data = False,
          soln_pds_adoption_basis = "Existing Adoption Prognostications",
          soln_pds_adoption_prognostication_source = "Based on: Greenpeace Advanced Energy Revolution (2015)",
          soln_pds_adoption_prognostication_trend = "3rd Poly",
          soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth,
          solution_category = "REPLACEMENT",
          ),
        'PDS-7p2050-Drawdown Plausible Scenario (Revision Case)':  advanced_controls.AdvancedControls(
          pds_2014_cost = 1883.53039287357, ref_2014_cost = 1883.53039287357,
          conv_2014_cost = 2010.03170851964,
          soln_first_cost_efficiency_rate = 0.1826,
          soln_first_cost_below_conv = True,
          conv_first_cost_efficiency_rate = 0.02,

          ch4_is_co2eq = True, n2o_is_co2eq = True,
          co2eq_conversion_source = "AR5 with feedback",
          soln_indirect_co2_per_iunit = 47096.8181818182,
          conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False,

          soln_lifetime_capacity = 41401.1076923077, soln_avg_annual_use = 1725.04615384615,
          conv_lifetime_capacity = 178770.5, conv_avg_annual_use = 4967.64844181569,

          report_start_year = 2020, report_end_year = 2050,

          soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0,
          soln_fixed_oper_cost_per_iunit = 21.4841902320724,
          conv_var_oper_cost_per_funit = 0.00475243216795082,
          conv_fixed_oper_cost_per_iunit = 32.8906457343352,
          conv_fuel_cost_per_funit = 0.09,

          npv_discount_rate = 0.04,

          emissions_use_co2eq = True,
          emissions_grid_source = "Meta-Analysis", emissions_grid_range = "Mean",

          soln_ref_adoption_regional_data = False,
          soln_pds_adoption_regional_data = False,
          soln_pds_adoption_basis = "Existing Adoption Prognostications",
          soln_pds_adoption_prognostication_source = "Ambitious Cases",
          soln_pds_adoption_prognostication_trend = "3rd Poly",
          soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth,
          solution_category = "REPLACEMENT",
          ),
        'PDS-10p2050-Drawdown Scenario (Revision Case)':  advanced_controls.AdvancedControls(
          pds_2014_cost = 1883.53039287357, ref_2014_cost = 1883.53039287357,
          conv_2014_cost = 2010.03170851964,
          soln_first_cost_efficiency_rate = 0.1826,
          soln_first_cost_below_conv = True,
          conv_first_cost_efficiency_rate = 0.02,

          ch4_is_co2eq = True, n2o_is_co2eq = True,
          co2eq_conversion_source = "AR5 with feedback",
          soln_indirect_co2_per_iunit = 47096.8181818182,
          conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False,

          soln_lifetime_capacity = 41401.1076923077, soln_avg_annual_use = 1725.04615384615,
          conv_lifetime_capacity = 178770.5, conv_avg_annual_use = 4967.64844181569,

          report_start_year = 2020, report_end_year = 2050,

          soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0,
          soln_fixed_oper_cost_per_iunit = 21.4841902320724,
          conv_var_oper_cost_per_funit = 0.00475243216795082,
          conv_fixed_oper_cost_per_iunit = 32.8906457343352,
          conv_fuel_cost_per_funit = 0.09,

          npv_discount_rate = 0.04,

          emissions_use_co2eq = True,
          emissions_grid_source = "Meta-Analysis", emissions_grid_range = "Mean",

          soln_ref_adoption_regional_data = False,
          soln_pds_adoption_regional_data = False,
          soln_pds_adoption_basis = "Existing Adoption Prognostications",
          soln_pds_adoption_prognostication_source = "Based on: Greenpeace Advanced Energy Revolution (2015)",
          soln_pds_adoption_prognostication_trend = "3rd Poly",
          soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth,
          solution_category = "REPLACEMENT",
          ),
        'PDS-10p2050-Drawdown Optimum Scenario (Revision Case)': advanced_controls.AdvancedControls(
          pds_2014_cost = 1883.53039287357, ref_2014_cost = 1883.53039287357,
          conv_2014_cost = 2010.03170851964,
          soln_first_cost_efficiency_rate = 0.1826,
          soln_first_cost_below_conv = True,
          conv_first_cost_efficiency_rate = 0.02,

          ch4_is_co2eq = True, n2o_is_co2eq = True,
          co2eq_conversion_source = "AR5 with feedback",
          soln_indirect_co2_per_iunit = 47096.8181818182,
          conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False,

          soln_lifetime_capacity = 41401.1076923077, soln_avg_annual_use = 1725.04615384615,
          conv_lifetime_capacity = 178770.5, conv_avg_annual_use = 4967.64844181569,

          report_start_year = 2020, report_end_year = 2050,

          soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0,
          soln_fixed_oper_cost_per_iunit = 21.4841902320724,
          conv_var_oper_cost_per_funit = 0.00475243216795082,
          conv_fixed_oper_cost_per_iunit = 32.8906457343352,
          conv_fuel_cost_per_funit = 0.09,

          npv_discount_rate = 0.04,

          emissions_use_co2eq = True,
          emissions_grid_source = "Meta-Analysis", emissions_grid_range = "Mean",

          soln_ref_adoption_regional_data = False,
          soln_pds_adoption_regional_data = False,
          soln_pds_adoption_basis = "Existing Adoption Prognostications",
          soln_pds_adoption_prognostication_source = "Based on: Greenpeace Advanced Energy Revolution (2015)",
          soln_pds_adoption_prognostication_trend = "3rd Poly",
          soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth,
          solution_category = "REPLACEMENT",
          ),
        }
    self.ac = ac_scenarios[scenario]

    tamconfig_list = [
      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
        'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['source_until_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['source_after_2014', 'Baseline Cases', pds_source_post_2014, 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES'],
      ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
        '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
        'Medium', 'Medium', 'Medium'],
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
      ['growth', soln_pds_adoption_prognostication_growth, 'Medium', 'Medium', 'Medium', 'Medium',
        'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
    ad_data_sources = {
      'Baseline Cases': {
        'Based on: AMPERE IMAGE REFpol': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv')),
        'Based on: AMPERE 3 MESSAGE Refpol': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv')),
        'Based on:AMPERE 3 GEM E3 Refpol': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv')),
        'Based on:IEA ETP 2016 6DS': str(thisdir.joinpath('ad_based_on_IEA_ETP_2016_6DS.csv')),
      },
      'Conservative Cases': {
        'Based on:AMPERE3 IMAGE 550': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv')),
        'Based on:AMPERE 3 MESSAGE 550': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv')),
        'Based on:AMPERE 3 GEM E3 550': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_GEM_E3_550.csv')),
        'Based on:IEA ETP 2016 4DS': str(thisdir.joinpath('ad_based_on_IEA_ETP_2016_4DS.csv')),
        'Based on: Greenpeace Reference (2015)': str(thisdir.joinpath(
          'ad_based_on_Greenpeace_2015_Reference.csv')),
      },
      'Ambitious Cases': {
        'Based on: AMPERE3 IMAGE 450': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv')),
        'Based on:AMPERE 3 MESSAGE 450': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv')),
        'Based on: AMPERE 3 GEM E3 450': str(thisdir.joinpath(
          'ad_based_on_AMPERE_2014_GEM_E3_450.csv')),
        'Based on: IEA ETP 2016 2DS': str(thisdir.joinpath('ad_based_on_IEA_ETP_2016_2DS.csv')),
        'Based on: Greenpeace Energy Revolution (2015)': str(thisdir.joinpath(
          'ad_based_on_Greenpeace_2015_Energy_Revolution.csv')),
        '[Source 6 - Ambitious]': str(thisdir.joinpath('ad_source_6_ambitious.csv')),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace Advanced Energy Revolution (2015)': str(thisdir.joinpath(
          'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv')),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources, adconfig=adconfig)

    ht_ref_datapoints = pd.DataFrame([
      [2014, 75.4369666666666, 50.2347544444444, 0.222616666666667, 14.1134955555556,
        1.05492222222222, 9.81238111111111, 10.0277777777778, 1.84069888888889,
        37.0189455555555, 8.79035],
      [2050, 182.45174281035700, 65.23577153795550, 0.35036397925031, 40.31823609831760,
        0.0, 28.29430643576590, 21.14106676256430, 9.60003899341737,
        48.77654058142600, 10.99425436873670]],
      columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
          "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    ht_pds_datapoints = pd.DataFrame([
      [2014, 75.4369666666666, 50.2347544444444, 0.222616666666667, 14.1134955555556,
        1.05492222222222, 9.81238111111111, 10.0277777777778, 1.84069888888889,
        37.0189455555555, 8.79035],
      [2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
      columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
          "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        adoption_low_med_high_global=self.ad.adoption_low_med_high_global(),
        adoption_is_single_source=self.ad.adoption_is_single_source())

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=str(datadir),
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted())
    soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
    soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
    conv_ref_tot_iunits_reqd = self.ua.conv_ref_tot_iunits_reqd()
    soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()

    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
        ref_learning_increase_mult=2, conv_learning_increase_mult=2,
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
        conv_ref_tot_iunits_reqd=conv_ref_tot_iunits_reqd,
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
        conv_ref_new_iunits_reqd=self.ua.conv_ref_new_iunits_reqd())

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
        conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit())

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
        conv_ref_new_iunits_reqd=self.ua.conv_ref_new_iunits_reqd(),
        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        fuel_in_liters=False)

    # Variable Meta-analysis objects, not used in model computation only in UI
    self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],
        soln_avg_annual_use=self.ac.soln_avg_annual_use,
        conv_avg_annual_use=self.ac.conv_avg_annual_use)

    self.soln_2014_cost_vma = vma.VMA(substitutions=self.r2s.substitutions,
        filename=str(thisdir.joinpath('vma_soln_2014_cost.csv')))

    self.soln_lifetime_vma = vma.VMA(substitutions=self.r2s.substitutions,
        filename=str(thisdir.joinpath('vma_soln_lifetime_years.csv')),
        final_units='soln-TWh/TW')

    self.soln_avg_annual_use_vma = vma.VMA(substitutions=self.r2s.substitutions,
        filename=str(thisdir.joinpath('vma_soln_avg_annual_use.csv')))

    self.soln_fixed_oper_cost_per_iunit_vma = vma.VMA(substitutions=self.r2s.substitutions,
        filename=str(thisdir.joinpath('vma_soln_fixed_oper_cost_per_iunit.csv')),
        final_units='US$2014/kW')

    self.soln_indirect_co2_per_iunit_vma = vma.VMA(substitutions=self.r2s.substitutions,
        filename=str(thisdir.joinpath('vma_soln_indirect_co2_per_iunit.csv')))

    # SolarPVRooftop_RRS_ELECGEN 'Variable Meta-analysis'!C1033:X1035, VMA #28
    self.soln_solar_util_vs_roof_vma = vma.VMA(substitutions=self.r2s.substitutions,
        filename=str(datadir.joinpath('energy', 'vma_solar_util_vs_roof.csv')),
        postprocess=lambda mn, hi, lo: (1.0 - mn, 1.0 - lo, 1.0 - hi))

    self.VMAs = [
        #('Current Adoption', ),
        ('CONVENTIONAL First Cost per Implementation Unit', self.r2s.conv_2014_cost_vma),
        ('SOLUTION First Cost per Implementation Unit', self.soln_2014_cost_vma),
        ('Lifetime Capacity - CONVENTIONAL', self.r2s.conv_lifetime_vma),
        ('Lifetime Capacity - SOLUTION', self.soln_lifetime_vma),
        ('Average Annual Use - CONVENTIONAL', self.r2s.conv_avg_annual_use_vma),
        ('Average Annual Use - SOLUTION', self.soln_avg_annual_use_vma),
        ('CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit',
          self.r2s.conv_var_oper_cost_per_funit_vma),
        ('CONVENTIONAL Fixed Operating Cost (FOM) per Implementation Unit', 
          self.r2s.conv_fixed_oper_cost_per_iunit_vma),
        ('SOLUTION Fixed Operating Cost (FOM) per Implementation Unit',
          self.soln_fixed_oper_cost_per_iunit_vma),
        ('Indirect CO2 Emissions per SOLUTION Implementation Unit',
          self.soln_indirect_co2_per_iunit_vma),
        #('2005-2014 Average CONVENTIONAL Fuel Price per functional unit', ),
        ('Weighted Average CONVENTIONAL Plant Efficiency', self.r2s.conv_ref_plant_efficiency_vma),
        ('Coal Plant Efficiency', self.r2s.coal_plant_efficiency_vma),
        ('Natural Gas Plant Efficiency', self.r2s.natural_gas_plant_efficiency_vma),
        ('Oil Plant Efficiency', self.r2s.oil_plant_efficiency_vma),
        #('Lifecycle indirect CO2 emissions per functional unit by PV type', ),
        ('Percentage of Solar Photovoltaic Generation from Utility Scale',
          self.soln_solar_util_vs_roof_vma),
        #('Solar PV Module Learning Rate', ),
        #('Utility Scale PV BOS Learning Rate', ),
        #('Percentage of PV System Installed Costs from Module', ),
        ]

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
