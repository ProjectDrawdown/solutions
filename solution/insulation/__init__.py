"""Insulation solution model.
   Excel filename: Drawdown-Insulation_RRS_v1,1_18Dec2018_PUBLIC.xlsm
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

from model import tam
from solution import rrs

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

scenarios = {
  'PDS1-69p2050-Slow Growth, Medium (Book Ed.1)': advanced_controls.AdvancedControls(
      # This scenario envisions a relatively low adoption of medium insulation. We use a
      # 1.47% annual retrofit of total building stock in cold climates, and a 2.824 RSI.
      # This scenario uses data calculated for the Drawdown book edition 1, some of
      # which have been updated.
      report_start_year = 2020, report_end_year = 2050, 

      pds_2014_cost = 100133030.2635106, ref_2014_cost = 100133030.2635106, 
      conv_2014_cost = 0.0, 
      soln_first_cost_efficiency_rate = 0.0, 
      conv_first_cost_efficiency_rate = 0.0, soln_first_cost_below_conv = True, 
      npv_discount_rate = 0.04, 

      ch4_is_co2eq = False, n2o_is_co2eq = False, 
      co2eq_conversion_source = 'AR5 with feedback', 
      soln_indirect_co2_per_iunit = 0.0, 
      conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False, 
      ch4_co2_per_twh = 0.0, n2o_co2_per_twh = 0.0, 

      soln_lifetime_capacity = 30.0, soln_avg_annual_use = 1.0, 
      conv_lifetime_capacity = 30.0, conv_avg_annual_use = 1.0, 

      soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 6601698.20809853, 
      soln_fixed_oper_cost_per_iunit = 0.0, 
      conv_var_oper_cost_per_funit = 0.0, conv_fuel_cost_per_funit = 8820257.47880107, 
      conv_fixed_oper_cost_per_iunit = 0.0, 
      soln_energy_efficiency_factor = 0.25152998946286, conv_annual_energy_used = 0.029820472057714, 
      conv_fuel_consumed_per_funit = 310.812002708002, soln_fuel_efficiency_factor = 0.25152998946286, 
      conv_fuel_emissions_factor = 61.051339971807074, soln_fuel_emissions_factor = 61.051339971807074, 

      emissions_grid_source = 'Meta-Analysis', emissions_grid_range = 'Mean', 
      emissions_use_co2eq = True, 
      conv_emissions_per_funit = 0.0, soln_emissions_per_funit = 0.0, 

      soln_ref_adoption_basis = 'Custom', 
      soln_ref_adoption_custom_name = 'Drawdown Book Edition 1 REF Scenario', 
      soln_ref_adoption_regional_data = False, soln_pds_adoption_regional_data = False, 
      soln_pds_adoption_basis = 'Fully Customized PDS', 
      soln_pds_adoption_custom_name = 'Drawdown Book Edition 1 PDS 1 Scenario', 
      source_until_2014 = 'ALL SOURCES', 
      ref_source_post_2014 = 'ALL SOURCES', 
      pds_source_post_2014 = 'ALL SOURCES', 

    ),
  'PDS2-100p2050-Medium Growth, Medium (Book Ed.1)': advanced_controls.AdvancedControls(
      # This scenario envisions a medium adoption of medium insulation. We use a 3.5%
      # annual retrofit of total building stock in cold climates, and a 2.5 RSI. This
      # scenario uses data calculated for the Drawdown book edition 1, some of which
      # have been updated.
      report_start_year = 2020, report_end_year = 2050, 

      pds_2014_cost = 100133030.2635106, ref_2014_cost = 100133030.2635106, 
      conv_2014_cost = 0.0, 
      soln_first_cost_efficiency_rate = 0.0, 
      conv_first_cost_efficiency_rate = 0.0, soln_first_cost_below_conv = True, 
      npv_discount_rate = 0.04, 

      ch4_is_co2eq = False, n2o_is_co2eq = False, 
      co2eq_conversion_source = 'AR5 with feedback', 
      soln_indirect_co2_per_iunit = 0.0, 
      conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False, 
      ch4_co2_per_twh = 0.0, n2o_co2_per_twh = 0.0, 

      soln_lifetime_capacity = 30.0, soln_avg_annual_use = 1.0, 
      conv_lifetime_capacity = 30.0, conv_avg_annual_use = 1.0, 

      soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 7457278.2958681, 
      soln_fixed_oper_cost_per_iunit = 0.0, 
      conv_var_oper_cost_per_funit = 0.0, conv_fuel_cost_per_funit = 8820257.47880107, 
      conv_fixed_oper_cost_per_iunit = 0.0, 
      soln_energy_efficiency_factor = 0.154528276097246, conv_annual_energy_used = 0.029820472057714, 
      conv_fuel_consumed_per_funit = 310.812002708002, soln_fuel_efficiency_factor = 0.154528276097246, 
      conv_fuel_emissions_factor = 61.051339971807074, soln_fuel_emissions_factor = 61.051339971807074, 

      emissions_grid_source = 'Meta-Analysis', emissions_grid_range = 'Mean', 
      emissions_use_co2eq = True, 
      conv_emissions_per_funit = 0.0, soln_emissions_per_funit = 0.0, 

      soln_ref_adoption_basis = 'Custom', 
      soln_ref_adoption_custom_name = 'Drawdown Book Edition 1 REF Scenario', 
      soln_ref_adoption_regional_data = False, soln_pds_adoption_regional_data = False, 
      soln_pds_adoption_basis = 'Fully Customized PDS', 
      soln_pds_adoption_custom_name = 'Drawdown Book Edition 1 PDS 2 Scenario', 
      source_until_2014 = 'ALL SOURCES', 
      ref_source_post_2014 = 'ALL SOURCES', 
      pds_source_post_2014 = 'ALL SOURCES', 

    ),
  'PDS3-100p2050-High Growth, Lower (Book Ed.1)': advanced_controls.AdvancedControls(
      # This scenario envisions a relatively aggressive adoption of slightly lower
      # insulation. We use a 5% annual retrofit of total building stock in cold
      # climates, and a 2.475 RSI. This scenario uses data calculated for the Drawdown
      # book edition 1, some of which have been updated.
      report_start_year = 2020, report_end_year = 2050, 

      pds_2014_cost = 100133030.2635106, ref_2014_cost = 100133030.2635106, 
      conv_2014_cost = 0.0, 
      soln_first_cost_efficiency_rate = 0.0, 
      conv_first_cost_efficiency_rate = 0.0, soln_first_cost_below_conv = True, 
      npv_discount_rate = 0.04, 

      ch4_is_co2eq = False, n2o_is_co2eq = False, 
      co2eq_conversion_source = 'AR5 with feedback', 
      soln_indirect_co2_per_iunit = 0.0, 
      conv_indirect_co2_per_unit = 0.0, conv_indirect_co2_is_iunits = False, 
      ch4_co2_per_twh = 0.0, n2o_co2_per_twh = 0.0, 

      soln_lifetime_capacity = 30.0, soln_avg_annual_use = 1.0, 
      conv_lifetime_capacity = 30.0, conv_avg_annual_use = 1.0, 

      soln_var_oper_cost_per_funit = 0.0, soln_fuel_cost_per_funit = 7532604.3392607, 
      soln_fixed_oper_cost_per_iunit = 0.0, 
      conv_var_oper_cost_per_funit = 0.0, conv_fuel_cost_per_funit = 8820257.47880107, 
      conv_fixed_oper_cost_per_iunit = 0.0, 
      soln_energy_efficiency_factor = 0.145988157673986, conv_annual_energy_used = 0.029820472057714, 
      conv_fuel_consumed_per_funit = 310.812002708002, soln_fuel_efficiency_factor = 0.145988157673986, 
      conv_fuel_emissions_factor = 61.051339971807074, soln_fuel_emissions_factor = 61.051339971807074, 

      emissions_grid_source = 'Meta-Analysis', emissions_grid_range = 'Mean', 
      emissions_use_co2eq = True, 
      conv_emissions_per_funit = 0.0, soln_emissions_per_funit = 0.0, 

      soln_ref_adoption_basis = 'Custom', 
      soln_ref_adoption_custom_name = 'Drawdown Book Edition 1 REF Scenario', 
      soln_ref_adoption_regional_data = False, soln_pds_adoption_regional_data = False, 
      soln_pds_adoption_basis = 'Fully Customized PDS', 
      soln_pds_adoption_custom_name = 'Drawdown Book Edition 1 PDS 3 Scenario', 
      source_until_2014 = 'ALL SOURCES', 
      ref_source_post_2014 = 'ALL SOURCES', 
      pds_source_post_2014 = 'ALL SOURCES', 

    ),
}

class Insulation:
  name = 'Insulation'
  def __init__(self, scenario=None):
    datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS1-69p2050-Slow Growth, Medium (Book Ed.1)'
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
    tam_ref_data_sources = {
      'Baseline Cases': {
          'Project Drawdown Analysis of Several Sources.Click to see source.': str(thisdir.joinpath('tam_Project_Drawdown_Analysis_of_Several_Sources_Click_to_see_source.csv')),
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      tam_pds_data_sources=tam_ref_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    ca_pds_data_sources = [
      {'name': 'Halfway to Passive House', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Halfway_to_Passive_House.csv'))},
      {'name': 'Almost Passive House', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Almost_Passive_House.csv'))},
      {'name': 'Passive House', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Passive_House.csv'))},
      {'name': 'Drawdown Book Edition 1 PDS 1 Scenario', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Drawdown_Book_Edition_1_PDS_1_Scenario.csv'))},
      {'name': 'Drawdown Book Edition 1 PDS 2 Scenario', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Drawdown_Book_Edition_1_PDS_2_Scenario.csv'))},
      {'name': 'Drawdown Book Edition 1 PDS 3 Scenario', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Drawdown_Book_Edition_1_PDS_3_Scenario.csv'))},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name)
    pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
    pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
    pds_adoption_is_single_source = True

    ca_ref_data_sources = [
      {'name': 'Frozen Efficiency - Natural Rate of Insulation (1.4%)', 'include': False,
          'filename': str(thisdir.joinpath('custom_ref_ad_Frozen_Efficiency_Natural_Rate_of_Insulation_1_4.csv'))},
      {'name': 'Drawdown Book Edition 1 REF Scenario', 'include': False,
          'filename': str(thisdir.joinpath('custom_ref_ad_Drawdown_Book_Edition_1_REF_Scenario.csv'))},
    ]
    self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
        soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name)
    ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

    ht_ref_adoption_initial = pd.Series(
      [35739.10972659552, 0.0, 0.0, 0.0, 0.0,
       0.0, 0.0, 0.0, 0.0, 0.0],
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
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_data_per_region=ref_adoption_data_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=datadir,
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
        fc_convert_iunit_factor=1.0)

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
        conversion_factor=1.0)

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

