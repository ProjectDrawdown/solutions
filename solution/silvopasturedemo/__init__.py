"""Silvopasture solution model.
   Excel filename: Silvopasture_L-Use_v1.1a_3Aug18.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import aez
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

from model import tla
from solution import land

DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = vma.generate_vma_dict(THISDIR.joinpath('vma_data'))

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

kwargs = {
      # general
      'solution_category': SOLUTION_CATEGORY.LAND,
      'vmas': VMAs,
      'report_start_year': 2020, 'report_end_year': 2050,

      # TLA
      'use_custom_tla': False,

      # adoption
      'soln_ref_adoption_regional_data': False, 'soln_pds_adoption_regional_data': False,
      'soln_pds_adoption_basis': 'Fully Customized PDS',
      'soln_pds_adoption_custom_name': 'Low of All Custom Scenarios',
      'pds_adoption_use_ref_years': [2015, 2016],
      'pds_adoption_final_percentage': [('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],

      # financial
      'pds_2014_cost': {'value': 462.453005939073, 'statistic': 'mean'}, 'ref_2014_cost': {'value': 462.453005939073, 'statistic': 'mean'},
      'conv_2014_cost': 0.0,
      'soln_first_cost_efficiency_rate': 0.0,
      'conv_first_cost_efficiency_rate': 0.0,
      'npv_discount_rate': 0.1,
      'soln_expected_lifetime': 30.0,
      'conv_expected_lifetime': 30.0,
      'yield_from_conv_practice': {'value': 3.42857142857143, 'statistic': 'mean'},
      'yield_gain_from_conv_to_soln': {'value': 0.100544967245763, 'statistic': 'mean'},

      'soln_fixed_oper_cost_per_iunit': {'value': 837.643130909091, 'statistic': 'mean'},
      'conv_fixed_oper_cost_per_iunit': {'value': 328.415857769938, 'statistic': 'mean'},

      # emissions
      'soln_indirect_co2_per_iunit': 0.0,
      'conv_indirect_co2_per_unit': 0.0,
      'soln_annual_energy_used': 0.0, 'conv_annual_energy_used': 0.0,

      'tco2eq_reduced_per_land_unit': 0.0,
      'tco2eq_rplu_rate': 'One-time',
      'tco2_reduced_per_land_unit': 0.0,
      'tco2_rplu_rate': 'One-time',
      'tn2o_co2_reduced_per_land_unit': 0.0,
      'tn2o_co2_rplu_rate': 'One-time',
      'tch4_co2_reduced_per_land_unit': 0.0,
      'tch4_co2_rplu_rate': 'One-time',
      'land_annual_emissons_lifetime': 100.0,

      'emissions_grid_source': 'Meta-Analysis', 'emissions_grid_range': 'Mean',
      'emissions_use_co2eq': True,
      'emissions_use_agg_co2eq': True,

      # sequestration
      'seq_rate_global': {'value': 4.64561688311688, 'statistic': 'mean'},
      'disturbance_rate': 0.0,

      'harvest_frequency': 100.0,
      'carbon_not_emitted_after_harvesting': 0.0,
}

default_kwargs = kwargs.copy()
regional_kwargs = kwargs.copy()
regional_kwargs['pds_2014_cost'] = 'mean per region'
regional_kwargs['ref_2014_cost'] = 'mean per region'

scenarios = {
  'default': advanced_controls.AdvancedControls(**default_kwargs),
  'regional': advanced_controls.AdvancedControls(**regional_kwargs),
}

class SilvopastureDemo:
  name = 'Silvopasture'
  units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'default'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    # TLA
    self.ae = aez.AEZ(solution_name=self.name)
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Linear trend based on Zomers  >30% tree cover percent area applied in grassland area', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Linear_trend_based_on_Zomers_30_tree_cover_percent_area_applied_in_grassland_area.csv')},
      {'name': 'Linear trend based on Zomers >30% tree cover percent area and conversion of >10% are to 30% tree cover area applied in grassland area', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Linear_trend_based_on_Zomers_30_tree_cover_percent_area_and_conversion_of_10_are_to_30_t_d419700f.csv')},
      {'name': 'Medium growth, linear trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Medium_growth_linear_trend.csv')},
      {'name': 'High growth, linear trend', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_growth_linear_trend.csv')},
      {'name': 'Low growth, linear trend (based on improved pasture area)', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_growth_linear_trend_based_on_improved_pasture_area.csv')},
      {'name': 'High growth, linear trend (based on improved pasture area)', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_growth_linear_trend_based_on_improved_pasture_area.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=0.5, low_sd_mult=1.0,
        total_adoption_limit=self.tla_per_region,
        match_regions_to_world=True
)


    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = None

    # ht_ref_adoption_initial = pd.Series( [314.15] + [0.] * 9, index=REGIONS)
    ht_ref_adoption_initial = pd.Series(
      [314.15,  108.658048, 0.0, 58.321546, 34.40992, 107.332575, np.nan, np.nan, np.nan, np.nan],
       index=REGIONS)
    ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial / self.tla_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_total_adoption_units=self.tla_per_region, pds_total_adoption_units=self.tla_per_region,
        electricity_unit_factor=1000000.0,
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
        conv_ref_first_cost_uses_tot_units=True,
        calc_per_region=True,
        fc_convert_iunit_factor=land.MHA_TO_HA)

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
        conversion_factor=land.MHA_TO_HA)

    self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

    self.c2 = co2calcs.CO2Calcs(ac=self.ac,
        ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
        soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
        soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
        soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),
        soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),
        soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),
        regime_distribution=self.ae.get_land_distribution())

