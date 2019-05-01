"""Green Roofs solution model.
   Excel filename: Drawdown-Green Roofs_RRS_v1.1_18Nov2018_PUBLIC.xlsm
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
from model import s_curve
from model import unitadoption
from model import vma
from model.advanced_controls import SOLUTION_CATEGORY

from model import tam
from solution import rrs

DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = vma.generate_vma_dict(THISDIR.joinpath('vma_data'))

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

scenarios = {
  'PDS1-30p2050-Integrated-FE-12.75% (Book)': advanced_controls.AdvancedControls(
      # The adoption of Green Roofs is modeled as a Logistic S-Curve growing from
      # current adoption to 30% of the TAM by 2050. To account for integration effects,
      # the fuel efficiency of the solution was reduced to 12.75% since other buildings
      # solutions reduce the total impact of Green Roofs.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Logistic S-Curve', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_base_adoption=[('World', 165284837.0), ('OECD90', 153214036.0), ('Eastern Europe', 2001574.0), ('Asia (Sans Japan)', 10001070.0), ('Middle East and Africa', 1759.0), ('Latin America', 66398.0), ('China', 10000000.0), ('India', 1070.0), ('EU', 129000000.0), ('USA', 21532448.0)], 
      pds_adoption_final_percentage=[('World', 0.3), ('OECD90', 0.6), ('Eastern Europe', 0.3), ('Asia (Sans Japan)', 0.3), ('Middle East and Africa', 0.3), ('Latin America', 0.3), ('China', 0.3), ('India', 0.3), ('EU', 0.6), ('USA', 0.3)], 

      # financial
      pds_2014_cost=182.99459999999996, ref_2014_cost=182.99459999999996, 
      conv_2014_cost=90.10418681818182, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.094, 
      soln_lifetime_capacity=40.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=18.5, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.13912500000000017, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=1.3761, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.00026161200949465267, soln_fuel_efficiency_factor=0.1275, 
      conv_fuel_emissions_factor=61.051339971807074, soln_fuel_emissions_factor=61.051339971807074, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS2-50p2050-Integrated-FE-12.6% (Book)': advanced_controls.AdvancedControls(
      # The adoption of Green Roofs is modeled as a Logistic S-Curve growing from
      # current adoption to 50% of the TAM by 2050. To account for integration effects,
      # the fuel efficiency of the solution was reduced to 12.6% since other buildings
      # solutions reduce the total impact of Green Roofs.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Logistic S-Curve', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_base_adoption=[('World', 165284837.0), ('OECD90', 153214036.0), ('Eastern Europe', 2001574.0), ('Asia (Sans Japan)', 10001070.0), ('Middle East and Africa', 1759.0), ('Latin America', 66398.0), ('China', 10000000.0), ('India', 1070.0), ('EU', 129000000.0), ('USA', 21532448.0)], 
      pds_adoption_final_percentage=[('World', 0.5), ('OECD90', 0.6), ('Eastern Europe', 0.5), ('Asia (Sans Japan)', 0.5), ('Middle East and Africa', 0.5), ('Latin America', 0.5), ('China', 0.5), ('India', 0.5), ('EU', 0.6), ('USA', 0.5)], 

      # financial
      pds_2014_cost=182.99459999999996, ref_2014_cost=182.99459999999996, 
      conv_2014_cost=90.10418681818182, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.094, 
      soln_lifetime_capacity=40.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=18.5, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.13912500000000017, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=1.3761, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.00026161200949465267, soln_fuel_efficiency_factor=0.126, 
      conv_fuel_emissions_factor=61.051339971807074, soln_fuel_emissions_factor=61.051339971807074, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS3-75p2050-Integrated-FE-12.54% (Book)': advanced_controls.AdvancedControls(
      # The adoption of Green Roofs is modeled as a Logistic S-Curve growing from
      # current adoption to 75% of the TAM by 2050. To account for integration effects,
      # the fuel efficiency of the solution was reduced to 12.54% since other buildings
      # solutions reduce the total impact of Green Roofs.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Logistic S-Curve', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_base_adoption=[('World', 165284837.0), ('OECD90', 153214036.0), ('Eastern Europe', 2001574.0), ('Asia (Sans Japan)', 10001070.0), ('Middle East and Africa', 1759.0), ('Latin America', 66398.0), ('China', 10000000.0), ('India', 1070.0), ('EU', 129000000.0), ('USA', 21532448.0)], 
      pds_adoption_final_percentage=[('World', 0.75), ('OECD90', 0.75), ('Eastern Europe', 0.75), ('Asia (Sans Japan)', 0.75), ('Middle East and Africa', 0.75), ('Latin America', 0.75), ('China', 0.75), ('India', 0.75), ('EU', 0.75), ('USA', 0.75)], 

      # financial
      pds_2014_cost=182.99459999999996, ref_2014_cost=182.99459999999996, 
      conv_2014_cost=90.10418681818182, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.094, 
      soln_lifetime_capacity=40.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=18.5, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.13912500000000017, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=1.3761, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.00026161200949465267, soln_fuel_efficiency_factor=0.1254, 
      conv_fuel_emissions_factor=61.051339971807074, soln_fuel_emissions_factor=61.051339971807074, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
}

class GreenRoofs:
  name = 'Green Roofs'
  units = {
    "implementation unit": "m²",
    "functional unit": "m²",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-30p2050-Integrated-FE-12.75% (Book)'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    # TAM
    tamconfig_list = [
      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
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
          'Custom (See TAM Factoring) based on  http://www.gbpn.org/databases-tools/mrv-tool/methodology.': THISDIR.joinpath('tam', 'tam_Custom_See_TAM_Factoring_based_on_httpwww_gbpn_orgdatabasestoolsmrvtoolmethodology_.csv'),
          'Based on GBPN - BEST PRACTICE POLICIES FOR LOW CARBON & ENERGY BUILDINGS BASED ON SCENARIO ANALYSIS May 2012': THISDIR.joinpath('tam', 'tam_based_on_GBPN_BEST_PRACTICE_POLICIES_FOR_LOW_CARBON_ENERGY_BUILDINGS_BASED_ON_SCENARIO_A_c7e92439.csv'),
          'IEA (2013)': THISDIR.joinpath('tam', 'tam_IEA_2013.csv'),
      },
      'Conservative Cases': {
          'McKinsey': THISDIR.joinpath('tam', 'tam_McKinsey.csv'),
          'Navigant (2014)': THISDIR.joinpath('tam', 'tam_Navigant_2014.csv'),
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      tam_pds_data_sources=tam_ref_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    adconfig_list = [
      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['trend', self.ac.soln_pds_adoption_prognostication_trend, '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'Medium',
       'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0], dtype=np.object).set_index('param')
    ad_data_sources = {
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    sconfig_list = [['region', 'base_year', 'last_year'],
      ['World', 2014, 2050],
      ['OECD90', 2014, 2050],
      ['Eastern Europe', 2014, 2050],
      ['Asia (Sans Japan)', 2014, 2050],
      ['Middle East and Africa', 2014, 2050],
      ['Latin America', 2014, 2050],
      ['China', 2014, 2050],
      ['India', 2014, 2050],
      ['EU', 2014, 2050],
      ['USA', 2014, 2050]]
    sconfig = pd.DataFrame(sconfig_list[1:], columns=sconfig_list[0], dtype=np.object).set_index('region')
    sconfig['pds_tam_2050'] = pds_tam_per_region.loc[[2050]].T
    sc_regions, sc_percentages = zip(*self.ac.pds_base_adoption)
    sconfig['base_adoption'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    sconfig['base_percent'] = sconfig['base_adoption'] / pds_tam_per_region.loc[2014]
    sc_regions, sc_percentages = zip(*self.ac.pds_adoption_final_percentage)
    sconfig['last_percent'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    if self.ac.pds_adoption_s_curve_innovation is not None:
      sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_innovation)
      sconfig['innovation'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    if self.ac.pds_adoption_s_curve_imitation is not None:
      sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_imitation)
      sconfig['imitation'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    self.sc = s_curve.SCurve(transition_period=16, sconfig=sconfig)

    ref_adoption_data_per_region = None

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Logistic S-Curve':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = self.sc.logistic_adoption()
      pds_adoption_is_single_source = None
    elif self.ac.soln_pds_adoption_basis == 'Bass Diffusion S-Curve':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = self.sc.bass_diffusion_adoption()
      pds_adoption_is_single_source = None
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()

    ht_ref_adoption_initial = pd.Series(
      [165284837.0, 153214036.0, 2001574.0, 10001070.0, 1759.0,
       66398.0, 10000000.0, 1070.0, 129000000.0, 21532448.0],
       index=REGIONS)
    ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
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

