"""Tropical Tree Staples solution model.
   Excel filename: Tropical_Tree_Staples(Grassland)_L-Use_v1.1b_02Aug18.xlsm
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

scenarios = {
  'PDS-52p2050-Plausible-PDScustom-low-BookVersion1': advanced_controls.AdvancedControls(
      # The current adoption of this solution is based on the historical data
      # (1962-2012) available on tropical staple crops (avocados, bananas, Brazil nuts,
      # carobs, cashew nuts, coconuts, dates, oil palm, plantains) for different regions
      # from FAO. The data was interpolated to get the current adoption value in the
      # year 2014. The future adoption was also projected based on the historical growth
      # rate with some of the custom scenarios assuming an early growth (60-75%) by
      # 2030. This scenario presents the "low of all" PDS custom adoption scenario. The
      # results are marginally higher than the Book Version 1 result, so no separate
      # scenario was stored for the later. This version involves changes in the net
      # profit margin calculation methodology, correction of current adoption value,
      # revision of the custom adoption scenarios, and estimation of operational cost
      # which was missing in the Book Version 1. This solution was allocated both in the
      # cropland and grassland AEZs, so we have created two separate models for this
      # solution. One for the cropland AEZs and one for the grassland AEZs. The model
      # built for the cropland AEZs has only half of the allocated current adoption of
      # this solution, so that model doesn't have any future adoption scenarios and
      # therefore no results were generated there. This model is built for the grassland
      # AEZs, where half of the current adoption and all of the future adoption of this
      # solution is allocated. Thus, for this solution, the results are coming only from
      # this model, although we have created two separate models.

      # general
      solution_category=SOLUTION_CATEGORY.LAND,
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050,

      # TLA
      use_custom_tla=True,

      # adoption
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Fully Customized PDS',
      soln_pds_adoption_custom_name='Low of All Custom Scenarios',
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],

      # financial
      pds_2014_cost='mean', ref_2014_cost='mean',
      conv_2014_cost=0.0,
      soln_first_cost_efficiency_rate=0.0,
      conv_first_cost_efficiency_rate=0.0,
      npv_discount_rate=0.1,
      soln_expected_lifetime=30.0,
      conv_expected_lifetime=30.0,
      yield_from_conv_practice='mean',
      yield_gain_from_conv_to_soln=0.0,

      soln_fixed_oper_cost_per_iunit='mean',
      conv_fixed_oper_cost_per_iunit='mean',

      # emissions
      soln_indirect_co2_per_iunit=0.0,
      conv_indirect_co2_per_unit=0.0,

      tco2eq_reduced_per_land_unit=0.0,
      tco2eq_rplu_rate='One-time',
      tco2_reduced_per_land_unit=0.0,
      tco2_rplu_rate='One-time',
      tn2o_co2_reduced_per_land_unit=0.0,
      tn2o_co2_rplu_rate='One-time',
      tch4_co2_reduced_per_land_unit=0.0,
      tch4_co2_rplu_rate='One-time',
      land_annual_emissons_lifetime=100.0,

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
      emissions_use_co2eq=True,
      emissions_use_agg_co2eq=True,

      # sequestration
      seq_rate_global='mean',
      disturbance_rate=0.0,

    ),
  'PDS-68p2050-Drawdown-PDScustom-avg-BookVersion1': advanced_controls.AdvancedControls(
      # The current adoption of this solution is based on the historical data
      # (1962-2012) available on tropical staple crops (avocados, bananas, Brazil nuts,
      # carobs, cashew nuts, coconuts, dates, oil palm, plantains) for different regions
      # from FAO. The data was interpolated to get the current adoption value in the
      # year 2014. The future adoption was also projected based on the historical growth
      # rate with some of the custom scenarios assuming an early growth (60-75%) by
      # 2030. This scenario presents the "average of all" PDS custom adoption scenario.
      # The results are marginally higher than the Book Version 1 result, so no separate
      # scenario was stored for the later. This version involves changes in the net
      # profit margin calculation methodology, correction of current adoption value,
      # revision of the custom adoption scenarios, and estimation of operational cost
      # which was missing in the Book Version 1. This solution was allocated both in the
      # cropland and grassland AEZs, so we have created two separate models for this
      # solution. One for the cropland AEZs and one for the grassland AEZs. The model
      # built for the cropland AEZs has only half of the allocated current adoption of
      # this solution, so that model doesn't have any future adoption scenarios and
      # therefore no results were generated there. This model is built for the grassland
      # AEZs, where half of the current adoption and all of the future adoption of this
      # solution is allocated. Thus, for this solution, the results are coming only from
      # this model, although we have created two separate models.

      # general
      solution_category=SOLUTION_CATEGORY.LAND,
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050,

      # TLA
      use_custom_tla=True,

      # adoption
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Fully Customized PDS',
      soln_pds_adoption_custom_name='Average of All Custom Scenarios',
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],

      # financial
      pds_2014_cost='mean', ref_2014_cost='mean',
      conv_2014_cost=0.0,
      soln_first_cost_efficiency_rate=0.0,
      conv_first_cost_efficiency_rate=0.0,
      npv_discount_rate=0.1,
      soln_expected_lifetime=30.0,
      conv_expected_lifetime=30.0,
      yield_from_conv_practice='mean',
      yield_gain_from_conv_to_soln=0.0,

      soln_fixed_oper_cost_per_iunit='mean',
      conv_fixed_oper_cost_per_iunit='mean',

      # emissions
      soln_indirect_co2_per_iunit=0.0,
      conv_indirect_co2_per_unit=0.0,

      tco2eq_reduced_per_land_unit=0.0,
      tco2eq_rplu_rate='One-time',
      tco2_reduced_per_land_unit=0.0,
      tco2_rplu_rate='One-time',
      tn2o_co2_reduced_per_land_unit=0.0,
      tn2o_co2_rplu_rate='One-time',
      tch4_co2_reduced_per_land_unit=0.0,
      tch4_co2_rplu_rate='One-time',
      land_annual_emissons_lifetime=100.0,

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
      emissions_use_co2eq=True,
      emissions_use_agg_co2eq=True,

      # sequestration
      seq_rate_global='mean',
      disturbance_rate=0.0,

    ),
  'PDS-84p2050-Optimum-PDScustom-high-BookVersion1': advanced_controls.AdvancedControls(
      # The current adoption of this solution is based on the historical data
      # (1962-2012) available on tropical staple crops (avocados, bananas, Brazil nuts,
      # carobs, cashew nuts, coconuts, dates, oil palm, plantains) for different regions
      # from FAO. The data was interpolated to get the current adoption value in the
      # year 2014. The future adoption was also projected based on the historical growth
      # rate with some of the custom scenarios assuming an early growth (60-75%) by
      # 2030. This scenario presents the "high of all" PDS custom adoption scenario. The
      # results are marginally higher than the Book Version 1 result, so no separate
      # scenario was stored for the later. This version involves changes in the net
      # profit margin calculation methodology, correction of current adoption value,
      # revision of the custom adoption scenarios, and estimation of operational cost
      # which was missing in the Book Version 1. This solution was allocated both in the
      # cropland and grassland AEZs, so we have created two separate models for this
      # solution. One for the cropland AEZs and one for the grassland AEZs. The model
      # built for the cropland AEZs has only half of the allocated current adoption of
      # this solution, so that model doesn't have any future adoption scenarios and
      # therefore no results were generated there. This model is built for the grassland
      # AEZs, where half of the current adoption and all of the future adoption of this
      # solution is allocated. Thus, for this solution, the results are coming only from
      # this model, although we have created two separate models.

      # general
      solution_category=SOLUTION_CATEGORY.LAND,
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050,

      # TLA
      use_custom_tla=True,

      # adoption
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Fully Customized PDS',
      soln_pds_adoption_custom_name='High of All Custom Scenarios',
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],

      # financial
      pds_2014_cost='mean', ref_2014_cost='mean',
      conv_2014_cost=0.0,
      soln_first_cost_efficiency_rate=0.0,
      conv_first_cost_efficiency_rate=0.0,
      npv_discount_rate=0.1,
      soln_expected_lifetime=30.0,
      conv_expected_lifetime=30.0,
      yield_from_conv_practice='mean',
      yield_gain_from_conv_to_soln=0.0,

      soln_fixed_oper_cost_per_iunit='mean',
      conv_fixed_oper_cost_per_iunit='mean',

      # emissions
      soln_indirect_co2_per_iunit=0.0,
      conv_indirect_co2_per_unit=0.0,

      tco2eq_reduced_per_land_unit=0.0,
      tco2eq_rplu_rate='One-time',
      tco2_reduced_per_land_unit=0.0,
      tco2_rplu_rate='One-time',
      tn2o_co2_reduced_per_land_unit=0.0,
      tn2o_co2_rplu_rate='One-time',
      tch4_co2_reduced_per_land_unit=0.0,
      tch4_co2_rplu_rate='One-time',
      land_annual_emissons_lifetime=100.0,

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
      emissions_use_co2eq=True,
      emissions_use_agg_co2eq=True,

      # sequestration
      seq_rate_global='mean',
      disturbance_rate=0.0,

    ),
}

class TropicalTreeStaples:
  name = 'Tropical Tree Staples'
  units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS-52p2050-Plausible-PDScustom-low-BookVersion1'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    # TLA
    self.ae = aez.AEZ(solution_name=self.name)
    if self.ac.use_custom_tla:
      self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))
      custom_world_vals = self.c_tla.get_world_values()
    else:
      custom_world_vals = None
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(), custom_world_values=custom_world_vals)

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Average growth, linear trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Average_growth_linear_trend.csv')},
      {'name': 'Medium growth, linear trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Medium_growth_linear_trend.csv')},
      {'name': 'Low growth linear trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_growth_linear_trend.csv')},
      {'name': 'Low early growth, linear trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_early_growth_linear_trend.csv')},
      {'name': 'Max early growth, linear trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Max_early_growth_linear_trend.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0)

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [25.424461981811515, 0.03142549034684199, 0.0, 28.59165470128803, 17.01389600193888,
       5.211947770049295, 0.0, 0.0, 0.0, 0.0],
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
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        pds_total_adoption_units=self.tla_per_region,
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
                                regime_distribution=self.ae.get_land_distribution())

