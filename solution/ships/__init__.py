"""Oceanic Freight Improvements solution model.
   Excel filename: Drawdown-Oceanic Freight Improvements_RRS_v1.1_5Dec2018_PUBLIC.xlsm
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
  'PDS1-97p2050-Mean EEOI (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take the mean estimates of EEOI (Energy Efficiency Operations Index in
      # gCO2/ton-nmile) as projected by several studies referenced in the 3rd GHG IMO
      # Study (Smith et al, 2014), interpolate for missing years and convert them to
      # Estimated ton-nautical mile adoptions assuming that an efficient ship is one
      # that adopts a fixed set of 17 technologies and slow steaming, and a conventional
      # (non-efficient) ship is one that has average efficiency in 2008. This scenario
      # uses inputs calculated for the Drawdown book edition 1, some of which were
      # updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Book Edition 1 Scenario 1', 
      pds_adoption_use_ref_years=[2015], 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_base_adoption=[('World', 14427.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=11520609.511049619, ref_2014_cost=11520609.511049619, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.05, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=34.62518245159868, soln_avg_annual_use=1.3850072980639474, 
      conv_lifetime_capacity=34.62518245159868, conv_avg_annual_use=1.3850072980639474, 

      soln_var_oper_cost_per_funit=126122.92933096059, soln_fuel_cost_per_funit=1381104.13088959, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=1818597.774776236, 
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
      conv_fuel_consumed_per_funit=3663130.5135886758, soln_fuel_efficiency_factor=0.5010773206596144, 
      conv_fuel_emissions_factor=0.00289602, soln_fuel_emissions_factor=0.00289602, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS2-100p2050-1 SD Below Mean EEOI (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take (1 standard deviation below the mean of) the estimates of EEOI (Energy
      # Efficiency Operations Index in gCO2/ton-nmile) as projected by several studies
      # referenced in the 3rd GHG IMO Study (Smith et al, 2014), interpolate for missing
      # years and convert them to Estimated ton-nautical mile adoptions assuming that an
      # efficient ship is one that adopts a fixed set of 17 technologies and slow
      # steaming, and a conventional (non-efficient) ship is one that has average
      # efficiency in 2008. This scenario uses inputs calculated for the Drawdown book
      # edition 1, some of which were updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Book Edition 1 Scenario 2', 
      pds_adoption_use_ref_years=[2015], 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_base_adoption=[('World', 14427.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=11520609.511049619, ref_2014_cost=11520609.511049619, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.05, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=34.62518245159868, soln_avg_annual_use=1.3850072980639474, 
      conv_lifetime_capacity=34.62518245159868, conv_avg_annual_use=1.3850072980639474, 

      soln_var_oper_cost_per_funit=126122.92933096059, soln_fuel_cost_per_funit=1381104.13088959, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=1818597.774776236, 
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
      conv_fuel_consumed_per_funit=3663130.5135886758, soln_fuel_efficiency_factor=0.5010773206596144, 
      conv_fuel_emissions_factor=0.00289602, soln_fuel_emissions_factor=0.00289602, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS3-100p2050-Lowest EEOI (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take the lowest estimates of EEOI (Energy Efficiency Operations Index in
      # gCO2/ton-nmile) as projected by several studies referenced in the 3rd GHG IMO
      # Study (Smith et al, 2014), interpolate for missing years and convert them to
      # Estimated ton-nautical mile adoptions assuming that an efficient ship is one
      # that adopts a fixed set of 17 technologies and slow steaming, and a conventional
      # (non-efficient) ship is one that has average efficiency in 2008. This scenario
      # uses inputs calculated for the Drawdown book edition 1, some of which were
      # updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Book Edition 1 Scenario 3', 
      pds_adoption_use_ref_years=[2015], 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_base_adoption=[('World', 14427.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=11520609.511049619, ref_2014_cost=11520609.511049619, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.05, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=34.62518245159868, soln_avg_annual_use=1.3850072980639474, 
      conv_lifetime_capacity=34.62518245159868, conv_avg_annual_use=1.3850072980639474, 

      soln_var_oper_cost_per_funit=126122.92933096059, soln_fuel_cost_per_funit=1381104.13088959, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=1818597.774776236, 
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
      conv_fuel_consumed_per_funit=3663130.5135886758, soln_fuel_efficiency_factor=0.5010773206596144, 
      conv_fuel_emissions_factor=0.00289602, soln_fuel_emissions_factor=0.00289602, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
}

class Ships:
  name = 'Oceanic Freight Improvements'
  units = {
    "implementation unit": "Ship",
    "functional unit": "Billion Ton - nmiles",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-97p2050-Mean EEOI (Book Ed.1)'
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
          'Based on Smith et al, 2014 (max scenario); Fig 82,83 Pg 159,160': THISDIR.joinpath('tam', 'tam_based_on_Smith_et_al_2014_max_scenario_Fig_8283_Pg_159160.csv'),
          'Based on Buhaug et al,2009 (max scenario) Table 7.4 pg 94': THISDIR.joinpath('tam', 'tam_based_on_Buhaug_et_al2009_max_scenario_Table_7_4_pg_94.csv'),
          'Based on  RACE (max) Table 30 pg 126': THISDIR.joinpath('tam', 'tam_based_on_RACE_max_Table_30_pg_126.csv'),
      },
      'Ambitious Cases': {
          'Based on Smith et al, 2014 (min BAU scenario); Fig 82,83 Pg 159,160': THISDIR.joinpath('tam', 'tam_based_on_Smith_et_al_2014_min_BAU_scenario_Fig_8283_Pg_159160.csv'),
          'Based on Buhaug et al,2009 (min BAU) Table 7.4 pg 94': THISDIR.joinpath('tam', 'tam_based_on_Buhaug_et_al2009_min_BAU_Table_7_4_pg_94.csv'),
          'Based on RACE (min BAU) Table 30 pg 126': THISDIR.joinpath('tam', 'tam_based_on_RACE_min_BAU_Table_30_pg_126.csv'),
      },
      'Maximum Cases': {
          'OPRF study Pg 30 Appdx 1': THISDIR.joinpath('tam', 'tam_OPRF_study_Pg_30_Appdx_1.csv'),
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

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'PDS1 - Drawdown Team Calculations based on Projections from Smith et al (2014) - 3rd GHG Report of the IMO - Mean of projected EEOI values', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_Drawdown_Team_Calculations_based_on_Projections_from_Smith_et_al_2014_3rd_GHG_Repor_3eb1a907.csv')},
      {'name': 'PDS2 - Drawdown Team Calculations based on Projections from Smith et al (2014) - 3rd GHG Report of the IMO - 1 StDev more Ambitious than mean in EEOI terms', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_Drawdown_Team_Calculations_based_on_Projections_from_Smith_et_al_2014_3rd_GHG_Repor_e1bf2fbd.csv')},
      {'name': 'PDS3 - Drawdown Team Calculations based on Projections from Smith et al (2014) - 3rd GHG Report of the IMO - most ambitious values from all scenarios', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS3_Drawdown_Team_Calculations_based_on_Projections_from_Smith_et_al_2014_3rd_GHG_Repor_40d75a6d.csv')},
      {'name': 'Drawdown Book Edition 1 Scenario 1', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_1.csv')},
      {'name': 'Drawdown Book Edition 1 Scenario 2', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_2.csv')},
      {'name': 'Drawdown Book Edition 1 Scenario 3', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_3.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
        total_adoption_limit=pds_tam_per_region)

    ref_adoption_data_per_region = None

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = None
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()

    ht_ref_adoption_initial = pd.Series(
      [14427.0, 0.0, 0.0, 0.0, 0.0,
       0.0, 0.0, 0.0, 0.0, 0.0],
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
        bug_cfunits_double_count=False)
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

