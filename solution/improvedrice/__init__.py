"""Improved Rice solution model.
   Excel filename: Drawdown-Improved Rice_BioS.Agri_v1.1_6Dec2018_PUBLIC.xlsm
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
  'PDS-54p2050-Plausible-PDScustom-avg-BookVersion1': advanced_controls.AdvancedControls(
      # The current adoption was only available for the "direct seeded rice", which is
      # one of the practices proposed under this solution. However, due to the
      # limitation of the required data, we have used the average adoption of direct
      # seeded rice across different countries as the current adoption for this
      # solution. The future area under this solution is projected based on the
      # available adoption data at the country level, which is largely available for the
      # Asian region. As the rice is primarily cultivated in the Asian region, it is
      # assumed that the other regions will also follow the similar trends. The
      # projected scenarios were based on the average to high adoption growth rate with
      # some of the scenarios assuming an early adoption (75% by 2030). This scenario
      # presents the result of the "average of all" PDS custom adoption scenario. This
      # version also involves the correction of the current adoption, conventional
      # operational cost and net profit margin, solution net profit margin with revised
      # methodology and the estimation of operational cost which was missing in the Book
      # Version 1 results.

      # general
      solution_category=SOLUTION_CATEGORY.LAND, 
      vmas=VMAs, 
      report_start_year=2020, report_end_year=2050, 

      # TLA
      use_custom_tla=False, 

      # adoption
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Average of All Custom Scenarios', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      npv_discount_rate=0.1, 
      soln_expected_lifetime=30.0, 
      conv_expected_lifetime=30.0, 
      yield_from_conv_practice='mean', 
      yield_gain_from_conv_to_soln='mean', 

      soln_fixed_oper_cost_per_iunit='mean', 
      conv_fixed_oper_cost_per_iunit='mean', 

      # emissions
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 

      tco2eq_reduced_per_land_unit=0.0, 
      tco2eq_rplu_rate='One-time', 
      tco2_reduced_per_land_unit=0.0, 
      tco2_rplu_rate='One-time', 
      tn2o_co2_reduced_per_land_unit='mean', 
      tn2o_co2_rplu_rate='Annual', 
      tch4_co2_reduced_per_land_unit='mean', 
      tch4_co2_rplu_rate='Annual', 
      land_annual_emissons_lifetime=100.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      emissions_use_agg_co2eq=False, 

      # sequestration
      seq_rate_global='mean', 
      disturbance_rate=0.0, 

    ),
  'PDS-80p2050-Drawdown-PDScustom-high-BookVersion1': advanced_controls.AdvancedControls(
      # The current adoption was only available for the "direct seeded rice", which is
      # one of the practices proposed under this solution. However, due to the
      # limitation of the required data, we have used the average adoption of direct
      # seeded rice across different countries as the current adoption for this
      # solution. The future area under this solution is projected based on the
      # available adoption data at the country level, which is largely available for the
      # Asian region. As the rice is primarily cultivated in the Asian region, it is
      # assumed that the other regions will also follow the similar trends. The
      # projected scenarios were based on the average to high adoption growth rate with
      # some of the scenarios assuming an early adoption (75% by 2030). This scenario
      # presents the result of the "high of all" PDS custom adoption scenario. This
      # version also involves the correction of the current adoption, conventional
      # operational cost and net profit margin, solution net profit margin with revised
      # methodology and the estimation of operational cost which was missing in the Book
      # Version 1 results.

      # general
      solution_category=SOLUTION_CATEGORY.LAND, 
      vmas=VMAs, 
      report_start_year=2020, report_end_year=2050, 

      # TLA
      use_custom_tla=False, 

      # adoption
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='High of All Custom Scenarios', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      npv_discount_rate=0.1, 
      soln_expected_lifetime=30.0, 
      conv_expected_lifetime=30.0, 
      yield_from_conv_practice='mean', 
      yield_gain_from_conv_to_soln='mean', 

      soln_fixed_oper_cost_per_iunit='mean', 
      conv_fixed_oper_cost_per_iunit='mean', 

      # emissions
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 

      tco2eq_reduced_per_land_unit=0.0, 
      tco2eq_rplu_rate='One-time', 
      tco2_reduced_per_land_unit=0.0, 
      tco2_rplu_rate='One-time', 
      tn2o_co2_reduced_per_land_unit='mean', 
      tn2o_co2_rplu_rate='Annual', 
      tch4_co2_reduced_per_land_unit='mean', 
      tch4_co2_rplu_rate='Annual', 
      land_annual_emissons_lifetime=100.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      emissions_use_agg_co2eq=False, 

      # sequestration
      seq_rate_global='mean', 
      disturbance_rate=0.0, 

    ),
  'PDS-100p2050-Optimum-PDS-max-BookVersion1': advanced_controls.AdvancedControls(
      # The current adoption was only available for the "direct seeded rice", which is
      # one of the practices proposed under this solution. However, due to the
      # limitation of the required data, we have used the average adoption of direct
      # seeded rice across different countries as the current adoption for this
      # solution. The future area under this solution is projected based on the
      # available adoption data at the country level, which is largely available for the
      # Asian region. As the rice is primarily cultivated in the Asian region, it is
      # assumed that the other regions will also follow the similar trends. The
      # projected scenarios were based on the average to high adoption growth rate with
      # some of the scenarios assuming an early adoption (75% by 2030). This scenario
      # presents the result of the "max linear trend (100% adoption by 2050)" PDS custom
      # adoption scenario. This version also involves the correction of the current
      # adoption, conventional operational cost and net profit margin, solution net
      # profit margin with revised methodology and the estimation of operational cost
      # which was missing in the Book Version 1 results.

      # general
      solution_category=SOLUTION_CATEGORY.LAND, 
      vmas=VMAs, 
      report_start_year=2020, report_end_year=2050, 

      # TLA
      use_custom_tla=False, 

      # adoption
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Max Growth, Linear Trend', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      npv_discount_rate=0.1, 
      soln_expected_lifetime=30.0, 
      conv_expected_lifetime=30.0, 
      yield_from_conv_practice='mean', 
      yield_gain_from_conv_to_soln='mean', 

      soln_fixed_oper_cost_per_iunit='mean', 
      conv_fixed_oper_cost_per_iunit='mean', 

      # emissions
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 

      tco2eq_reduced_per_land_unit=0.0, 
      tco2eq_rplu_rate='One-time', 
      tco2_reduced_per_land_unit=0.0, 
      tco2_rplu_rate='One-time', 
      tn2o_co2_reduced_per_land_unit='mean', 
      tn2o_co2_rplu_rate='Annual', 
      tch4_co2_reduced_per_land_unit='mean', 
      tch4_co2_rplu_rate='Annual', 
      land_annual_emissons_lifetime=100.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      emissions_use_agg_co2eq=False, 

      # sequestration
      seq_rate_global='mean', 
      disturbance_rate=0.0, 

    ),
}

class ImprovedRice:
  name = 'Improved Rice'
  units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS-54p2050-Plausible-PDScustom-avg-BookVersion1'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    # TLA
    self.ae = aez.AEZ(solution_name=self.name)
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Low, Linear Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_Linear_Trend.csv')},
      {'name': 'High, Linear Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_Linear_Trend.csv')},
      {'name': 'Medium Linear Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Medium_Linear_Trend.csv')},
      {'name': 'Low high early growth', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_high_early_growth.csv')},
      {'name': 'High, high early growth', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_high_early_growth.csv')},
      {'name': 'Medium, high early growth', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Medium_high_early_growth.csv')},
      {'name': 'Max Growth, Linear Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Max_Growth_Linear_Trend.csv')},
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
      [2.8510574999999996, 0.0, 0.0, 0.0, 0.0,
       0.0, 0.0, 0.0, 0.0, 0.0],
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

