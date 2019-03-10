"""Instream Hydro (Small Hydro <10MW) solution model.
   Excel filename: Drawdown-Instream Hydro (Small Hydro sub10MW)_RRS.ES_v1.1_14Jan2019_PUBLIC.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import unitadoption
from model import vma

from solution import rrs

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

from model import tam
scenarios = {
  'PDS-4p2050-Plausible (Book Ed. 1)': advanced_controls.AdvancedControls(
      # Plausible Scenario, Due to the uncertainty associated with the development of
      # these technologies, the Plausible Scenario follows a customized high-growth
      # adoption. Using the 2030 projection from IRENA (2016), it is assumed that
      # electricity generation from small hydro will double by 2050
      report_start_year = 2020, report_end_year = 2050, 

      pds_2014_cost = 2721.6052631578946, ref_2014_cost = 2721.6052631578946, 
      conv_2014_cost = 2010.0317085196398, 
      soln_first_cost_efficiency_rate = 0.02, 
      conv_first_cost_efficiency_rate = 0.02, soln_first_cost_below_conv = True, 
      npv_discount_rate = 0.063, 

      ch4_is_co2eq = True, n2o_is_co2eq = True, 
      co2eq_conversion_source = 'AR5 with feedback', 
      soln_indirect_co2_per_iunit = 22932.352941176472, 
      conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False, 
      ch4_co2_per_twh = 0.0, n2o_co2_per_twh = 0.0, 

      soln_lifetime_capacity = 161608.13345783597, soln_avg_annual_use = 3834.769268491023, 
      conv_lifetime_capacity = 182411.2757676607, conv_avg_annual_use = 4946.8401873420025, 

      soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0, 
      soln_fixed_oper_cost_per_iunit = 0.0, 
      conv_var_oper_cost_per_funit = 0.003752690403548987, conv_fuel_cost_per_funit = 0.07, 
      conv_fixed_oper_cost_per_iunit = 32.951404311078015, 
      conv_fuel_consumed_per_funit = 0.0, soln_fuel_efficiency_factor = 0.0, 
      conv_fuel_emissions_factor = 0.0, soln_fuel_emissions_factor = 0.0, 

      emissions_grid_source = 'Meta-Analysis', emissions_grid_range = 'Mean', 
      emissions_use_co2eq = True, 
      conv_emissions_per_funit = 0.0, soln_emissions_per_funit = 0.0, 

      soln_ref_adoption_regional_data = False, soln_pds_adoption_regional_data = False, 
      soln_pds_adoption_basis = 'Fully Customized PDS', 
      pds_adoption_use_ref_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023], 
      soln_pds_adoption_custom_name = 'High Ambitious, double growth by 2030 & 2050', 
      source_until_2014 = 'ALL SOURCES', 
      ref_source_post_2014 = 'Baseline Cases', 
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario', 

      solution_category = 'REPLACEMENT', 
    ),
  'PDS-3p2050-Drawdown (Book Ed.1)': advanced_controls.AdvancedControls(
      # Drawdown Scenario, This scenario is derived from the evaluation of the ambitious
      # scenarios of three energy systems models, following a low-growth trajectory.
      # None of the models explicitly identify the evolution of small hydro systems for
      # electricity generation; therefore, a conservative assumption was adopted that,
      # in the future, the current share of 14 percent of all hydroelectricity would
      # continue to come from small systems.
      report_start_year = 2020, report_end_year = 2050, 

      pds_2014_cost = 2721.6052631578946, ref_2014_cost = 2721.6052631578946, 
      conv_2014_cost = 2010.0317085196398, 
      soln_first_cost_efficiency_rate = 0.02, 
      conv_first_cost_efficiency_rate = 0.02, soln_first_cost_below_conv = True, 
      npv_discount_rate = 0.063, 

      ch4_is_co2eq = True, n2o_is_co2eq = True, 
      co2eq_conversion_source = 'AR5 with feedback', 
      soln_indirect_co2_per_iunit = 22932.352941176472, 
      conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False, 
      ch4_co2_per_twh = 0.0, n2o_co2_per_twh = 0.0, 

      soln_lifetime_capacity = 161608.13345783597, soln_avg_annual_use = 3834.769268491023, 
      conv_lifetime_capacity = 182411.2757676607, conv_avg_annual_use = 4946.8401873420025, 

      soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0, 
      soln_fixed_oper_cost_per_iunit = 0.0, 
      conv_var_oper_cost_per_funit = 0.003752690403548987, conv_fuel_cost_per_funit = 0.07, 
      conv_fixed_oper_cost_per_iunit = 32.951404311078015, 
      conv_fuel_consumed_per_funit = 0.0, soln_fuel_efficiency_factor = 0.0, 
      conv_fuel_emissions_factor = 0.0, soln_fuel_emissions_factor = 0.0, 

      emissions_grid_source = 'Meta-Analysis', emissions_grid_range = 'Mean', 
      emissions_use_co2eq = True, 
      conv_emissions_per_funit = 0.0, soln_emissions_per_funit = 0.0, 

      soln_ref_adoption_regional_data = False, soln_pds_adoption_regional_data = False, 
      soln_pds_adoption_basis = 'Fully Customized PDS', 
      soln_pds_adoption_custom_name = 'Low Ambitious Growth, 10% higher compared to REF case', 
      source_until_2014 = 'ALL SOURCES', 
      ref_source_post_2014 = 'Baseline Cases', 
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario', 

      solution_category = 'REPLACEMENT', 
    ),
  'PDS-4p2050-Optimum (Book Ed. 1)': advanced_controls.AdvancedControls(
      # Optimum Scenario, follows a customized high-growth adoption. As the Plausible
      # Scenario, uses the 2030 projection from IRENA (2016), it is assumed that
      # electricity generation from small hydro will double by 2050.
      report_start_year = 2020, report_end_year = 2050, 

      pds_2014_cost = 2721.6052631578946, ref_2014_cost = 2721.6052631578946, 
      conv_2014_cost = 2010.0317085196398, 
      soln_first_cost_efficiency_rate = 0.02, 
      conv_first_cost_efficiency_rate = 0.02, soln_first_cost_below_conv = True, 
      npv_discount_rate = 0.063, 

      ch4_is_co2eq = True, n2o_is_co2eq = True, 
      co2eq_conversion_source = 'AR5 with feedback', 
      soln_indirect_co2_per_iunit = 22932.352941176472, 
      conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False, 
      ch4_co2_per_twh = 0.0, n2o_co2_per_twh = 0.0, 

      soln_lifetime_capacity = 161608.13345783597, soln_avg_annual_use = 3834.769268491023, 
      conv_lifetime_capacity = 182411.2757676607, conv_avg_annual_use = 4946.8401873420025, 

      soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 0.0, 
      soln_fixed_oper_cost_per_iunit = 0.0, 
      conv_var_oper_cost_per_funit = 0.003752690403548987, conv_fuel_cost_per_funit = 0.07, 
      conv_fixed_oper_cost_per_iunit = 32.951404311078015, 
      conv_fuel_consumed_per_funit = 0.0, soln_fuel_efficiency_factor = 0.0, 
      conv_fuel_emissions_factor = 0.0, soln_fuel_emissions_factor = 0.0, 

      emissions_grid_source = 'Meta-Analysis', emissions_grid_range = 'Mean', 
      emissions_use_co2eq = True, 
      conv_emissions_per_funit = 0.0, soln_emissions_per_funit = 0.0, 

      soln_ref_adoption_regional_data = False, soln_pds_adoption_regional_data = False, 
      soln_pds_adoption_basis = 'Fully Customized PDS', 
      pds_adoption_use_ref_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023], 
      soln_pds_adoption_custom_name = 'High Ambitious, double growth by 2030 & 2050', 
      source_until_2014 = 'ALL SOURCES', 
      ref_source_post_2014 = 'Baseline Cases', 
      pds_source_post_2014 = 'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario', 

      solution_category = 'REPLACEMENT', 
    ),
}

class InstreamHydro:
  name = 'Instream Hydro (Small Hydro <10MW)'
  def __init__(self, scenario=None):
    datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS-4p2050-Plausible (Book Ed. 1)'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    tamconfig_list = [
      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,
       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014,
       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014,
       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014],
      ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['trend', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.tam_ref_data_sources,
      tam_pds_data_sources=rrs.tam_pds_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    ca_data_sources = [
      {'name': 'High Ambitious, double growth by 2030 & 2050', 'include': True,
          'filename': str(thisdir.joinpath('custom_ad_High_Ambitious_double_growth_by_2030_2050.csv'))},
      {'name': 'Conservative Growth of 2.5% annum', 'include': True,
          'filename': str(thisdir.joinpath('custom_ad_Conservative_Growth_of_2_5_annum.csv'))},
      {'name': 'Low Ambitious Growth, 10% higher compared to REF case', 'include': True,
          'filename': str(thisdir.joinpath('custom_ad_Low_Ambitious_Growth_10_higher_compared_to_REF_case.csv'))},
    ]
    self.ca = customadoption.CustomAdoption(data_sources=ca_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name)
    adoption_data_per_region = self.ca.adoption_data_per_region()
    adoption_trend_per_region = self.ca.adoption_trend_per_region()
    adoption_is_single_source = True

    ht_ref_adoption_initial = pd.Series(
      [547.672, 69.035, 38.758, 403.057, 17.967,
       18.856, 383.689, 4.014, 23.027, 3.148],
       index=REGIONS)
    ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_pds_adoption_final_percentage = pd.Series(
      [0.0, 0.0, 0.0, 0.0, 0.0,
       0.0, 0.0, 0.0, 0.0, 0.0],
       index=REGIONS)
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        adoption_data_per_region=adoption_data_per_region,
        adoption_trend_per_region=adoption_trend_per_region,
        adoption_is_single_source=adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=datadir,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted())
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

    self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],
        soln_avg_annual_use=self.ac.soln_avg_annual_use,
        conv_avg_annual_use=self.ac.conv_avg_annual_use)

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

