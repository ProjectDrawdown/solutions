"""Forest Protection solution model.
   Excel filename: Drawdown-Forest Protection_BioS.Prot_v1.1_3Jan2019_PUBLIC.xlsm
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
  'PDS-87p2050-Plausible-PDScustom-avg-Bookedition1': advanced_controls.AdvancedControls(
      # The current adoption is based on the FAO 2015 estimates for global area under
      # forest protection. The future adoption scenarios are based on the national and
      # international commitments for forest protection. Considering a higher rate of
      # forest degradation and reduced area of intact forest, adoption scenarios are
      # build to maximize the area under forest protection. Thus, protection of 80%-100%
      # of the intact forest were assumed in different custom adoption scenarios with
      # some scenarios assuming an early adoption 75-90% by 2030. This scenario derives
      # the result from the "average of all" PDS custom adoption scenarios. The results
      # are similar to that of the Book edition 1, so no new scenario was created for
      # the latter. This model upgrade involves, changes in the TLA, current adoption,
      # and creation of new custom adoption scenarios.

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
      soln_expected_lifetime=0.0,
      conv_expected_lifetime=0.0,
      yield_from_conv_practice=0.0,
      yield_gain_from_conv_to_soln=0.0,

      soln_fixed_oper_cost_per_iunit=0.0,
      conv_fixed_oper_cost_per_iunit=0.0,

      # emissions
      soln_indirect_co2_per_iunit=0.0,
      conv_indirect_co2_per_unit=0.0,
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,

      tco2eq_reduced_per_land_unit={'value': 313.791126867655, 'statistic': 'mean'},
      tco2eq_rplu_rate='One-time',
      tco2_reduced_per_land_unit=0.0,
      tco2_rplu_rate='One-time',
      tn2o_co2_reduced_per_land_unit=0.0,
      tn2o_co2_rplu_rate='One-time',
      tch4_co2_reduced_per_land_unit=0.0,
      tch4_co2_rplu_rate='One-time',
      land_annual_emissons_lifetime=30.0,

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
      emissions_use_co2eq=True,
      emissions_use_agg_co2eq=True,

      # sequestration
      seq_rate_global={'value': 0.596666666666667, 'statistic': 'mean'},
      global_multi_for_regrowth=1.0,
      degradation_rate={'value': 0.003074, 'statistic': 'mean'},
      disturbance_rate={'value': 1.57962432447763e-05, 'statistic': 'mean'},

      delay_protection_1yr=True,
      delay_regrowth_1yr=True,
      include_unprotected_land_in_regrowth_calcs=False,

    ),
  'PDS-89p2050-Drawdown-PDScustom-aggmax-Bookedition1': advanced_controls.AdvancedControls(
      # The current adoption is based on the FAO 2015 estimates for global area under
      # forest protection. The future adoption scenarios are based on the national and
      # international commitments for forest protection. Considering a higher rate of
      # forest degradation and reduced area of intact forest, adoption scenarios are
      # build to maximize the area under forest protection. Thus, protection of 80%-100%
      # of the intact forest were assumed in different custom adoption scenarios with
      # some scenarios assuming an early adoption 75-90% by 2030. This scenario presents
      # the result of the "Aggressive-Max, High early growth 2" PDS custom adoption
      # scenario, with standard deviation input set to "1.5" in the Custom PDS Adoption
      # sheet. The results are marginally lesser than the Book edition 1, so no new
      # scenario was created for the latter. This model upgrade involves, changes in the
      # TLA, current adoption, and creation of new custom adoption scenarios.

      # general
      solution_category=SOLUTION_CATEGORY.LAND,
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050,

      # TLA
      use_custom_tla=False,

      # adoption
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,
      soln_pds_adoption_basis='Fully Customized PDS',
      soln_pds_adoption_custom_name='Aggressive-Max, high early growth2',
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0,
      conv_2014_cost=0.0,
      soln_first_cost_efficiency_rate=0.0,
      conv_first_cost_efficiency_rate=0.0,
      npv_discount_rate=0.1,
      soln_expected_lifetime=0.0,
      conv_expected_lifetime=0.0,
      yield_from_conv_practice=0.0,
      yield_gain_from_conv_to_soln=0.0,

      soln_fixed_oper_cost_per_iunit=0.0,
      conv_fixed_oper_cost_per_iunit=0.0,

      # emissions
      soln_indirect_co2_per_iunit=0.0,
      conv_indirect_co2_per_unit=0.0,
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,

      tco2eq_reduced_per_land_unit={'value': 313.791126867655, 'statistic': 'mean'},
      tco2eq_rplu_rate='One-time',
      tco2_reduced_per_land_unit=0.0,
      tco2_rplu_rate='One-time',
      tn2o_co2_reduced_per_land_unit=0.0,
      tn2o_co2_rplu_rate='One-time',
      tch4_co2_reduced_per_land_unit=0.0,
      tch4_co2_rplu_rate='One-time',
      land_annual_emissons_lifetime=30.0,

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
      emissions_use_co2eq=True,
      emissions_use_agg_co2eq=True,

      # sequestration
      seq_rate_global={'value': 0.596666666666667, 'statistic': 'mean'},
      global_multi_for_regrowth=1.0,
      degradation_rate={'value': 0.003074, 'statistic': 'mean'},
      disturbance_rate={'value': 1.57962432447763e-05, 'statistic': 'mean'},

      delay_protection_1yr=True,
      delay_regrowth_1yr=True,
      include_unprotected_land_in_regrowth_calcs=False,

    ),
  'PDS-92p2050-Optimum-PDScustom-high-Bookedition1': advanced_controls.AdvancedControls(
      # The current adoption is based on the FAO 2015 estimates for global area under
      # forest protection. The future adoption scenarios are based on the national and
      # international commitments for forest protection. Considering a higher rate of
      # forest degradation and reduced area of intact forest, adoption scenarios are
      # build to maximize the area under forest protection. Thus, protection of 80%-100%
      # of the intact forest were assumed in different custom adoption scenarios with
      # some scenarios assuming an early adoption 75-90% by 2030. This scenario derives
      # the result from the "high of all" PDS custom adoption scenarios, with standard
      # deviation input set to "1.5" in the Custom PDS Adoption sheet. The results are
      # marginally higher than the Book edition 1, so no new scenario was created for
      # the latter. This model upgrade involves, changes in the TLA, current adoption,
      # and creation of new custom adoption scenarios.

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
      soln_expected_lifetime=0.0,
      conv_expected_lifetime=0.0,
      yield_from_conv_practice=0.0,
      yield_gain_from_conv_to_soln=0.0,

      soln_fixed_oper_cost_per_iunit=0.0,
      conv_fixed_oper_cost_per_iunit=0.0,

      # emissions
      soln_indirect_co2_per_iunit=0.0,
      conv_indirect_co2_per_unit=0.0,
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,

      tco2eq_reduced_per_land_unit={'value': 313.791126867655, 'statistic': 'mean'},
      tco2eq_rplu_rate='One-time',
      tco2_reduced_per_land_unit=0.0,
      tco2_rplu_rate='One-time',
      tn2o_co2_reduced_per_land_unit=0.0,
      tn2o_co2_rplu_rate='One-time',
      tch4_co2_reduced_per_land_unit=0.0,
      tch4_co2_rplu_rate='One-time',
      land_annual_emissons_lifetime=30.0,

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
      emissions_use_co2eq=True,
      emissions_use_agg_co2eq=True,

      # sequestration
      seq_rate_global={'value': 0.596666666666667, 'statistic': 'mean'},
      global_multi_for_regrowth=1.0,
      degradation_rate={'value': 0.003074, 'statistic': 'mean'},
      disturbance_rate={'value': 1.57962432447763e-05, 'statistic': 'mean'},

      delay_protection_1yr=True,
      delay_regrowth_1yr=True,
      include_unprotected_land_in_regrowth_calcs=False,

    ),
}

class ForestProtection:
  name = 'Forest Protection'
  units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS-87p2050-Plausible-PDScustom-avg-Bookedition1'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    # TLA
    self.ae = aez.AEZ(solution_name=self.name)
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Aggressive-Low, Linear Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveLow_Linear_Trend.csv')},
      {'name': 'Aggressive-High, Linear Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveHigh_Linear_Trend.csv')},
      {'name': 'Aggressive-high early growth', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Aggressivehigh_early_growth.csv')},
      {'name': 'Aggressive-Max, high early growth1', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveMax_high_early_growth1.csv')},
      {'name': 'Aggressive-Max, high early growth2', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveMax_high_early_growth2.csv')},
      {'name': 'Aggressive-Max, urgent complete early growth', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveMax_urgent_complete_early_growth.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.5, low_sd_mult=1.0,
        total_adoption_limit=self.tla_per_region)

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [651.0, 0.0, 0.0, 0.0, 0.0,
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
        conv_ref_first_cost_uses_tot_units=True,
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
                                tot_red_in_deg_land=self.ua.cumulative_reduction_in_total_degraded_land(),
                                pds_protected_deg_land=self.ua.pds_cumulative_degraded_land_protected(),
                                ref_protected_deg_land=self.ua.ref_cumulative_degraded_land_protected(),
                                regime_distribution=self.ae.get_land_distribution())

