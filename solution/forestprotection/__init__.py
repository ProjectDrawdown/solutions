"""Forest Protection solution model.  # bb
   Excel filename: Drawdown-Forest Protection_BioS.Prot_v1.1_3Jan2019_PUBLIC.xlsm  # bb
"""  # bb
  # bb
import pathlib  # bb
  # bb
import numpy as np  # bb
import pandas as pd  # bb
  # bb
from model import adoptiondata  # bb
from model import advanced_controls  # bb
from model import aez  # bb
from model import ch4calcs  # bb
from model import co2calcs  # bb
from model import customadoption  # bb
from model import emissionsfactors  # bb
from model import firstcost  # bb
from model import helpertables  # bb
from model import operatingcost  # bb
from model import s_curve  # bb
from model import unitadoption  # bb
from model import vma  # bb
from model.advanced_controls import SOLUTION_CATEGORY  # bb
  # bb
from model import tla  # bb
from solution import land  # bb
  # bb
DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))  # bb
THISDIR = pathlib.Path(__file__).parents[0]  # bb
VMAs = vma.generate_vma_dict(THISDIR.joinpath('vma_data'))  # bb
  # bb
REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',  # bb
           'Latin America', 'China', 'India', 'EU', 'USA']  # bb
  # bb
scenarios = {  # bb
  'PDS-87p2050-Plausible-PDScustom-avg-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # The current adoption is based on the FAO 2015 estimates for global area under  # bb
      # forest protection. The future adoption scenarios are based on the national and  # bb
      # international commitments for forest protection. Considering a higher rate of  # bb
      # forest degradation and reduced area of intact forest, adoption scenarios are  # bb
      # build to maximize the area under forest protection. Thus, protection of 80%-100%  # bb
      # of the intact forest were assumed in different custom adoption scenarios with  # bb
      # some scenarios assuming an early adoption 75-90% by 2030. This scenario derives  # bb
      # the result from the "average of all" PDS custom adoption scenarios. The results  # bb
      # are similar to that of the Book edition 1, so no new scenario was created for  # bb
      # the latter. This model upgrade involves, changes in the TLA, current adoption,  # bb
      # and creation of new custom adoption scenarios.  # bb
  # bb
      # general  # bb
      solution_category=SOLUTION_CATEGORY.LAND,   # bb
      vmas=VMAs,   # bb
      report_start_year=2020, report_end_year=2050,   # bb
  # bb
      # TLA  # bb
      use_custom_tla=False,   # bb
  # bb
      # adoption  # bb
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,   # bb
      soln_pds_adoption_basis='Fully Customized PDS',   # bb
      soln_pds_adoption_custom_name='Average of All Custom Scenarios',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost=0.0, ref_2014_cost=0.0,   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=0.0,   # bb
      conv_expected_lifetime=0.0,   # bb
      yield_from_conv_practice=0.0,   # bb
      yield_gain_from_conv_to_soln=0.0,   # bb
  # bb
      soln_fixed_oper_cost_per_iunit=0.0,   # bb
      conv_fixed_oper_cost_per_iunit=0.0,   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,   # bb
  # bb
      tco2eq_reduced_per_land_unit={'value': 313.791126867655, 'statistic': 'mean'},   # bb
      tco2eq_rplu_rate='One-time',   # bb
      tco2_reduced_per_land_unit=0.0,   # bb
      tco2_rplu_rate='One-time',   # bb
      tn2o_co2_reduced_per_land_unit=0.0,   # bb
      tn2o_co2_rplu_rate='One-time',   # bb
      tch4_co2_reduced_per_land_unit=0.0,   # bb
      tch4_co2_rplu_rate='One-time',   # bb
      land_annual_emissons_lifetime=30.0,   # bb
  # bb
      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',   # bb
      emissions_use_co2eq=True,   # bb
      emissions_use_agg_co2eq=True,   # bb
  # bb
      # sequestration  # bb
      seq_rate_global={'value': 0.596666666666667, 'statistic': 'mean'},   # bb
      global_multi_for_regrowth=1.0,   # bb
      degradation_rate={'value': 0.003074, 'statistic': 'mean'},   # bb
      disturbance_rate={'value': 1.57962432447763e-05, 'statistic': 'mean'},   # bb
  # bb
      delay_protection_1yr=True,   # bb
      delay_regrowth_1yr=True,   # bb
      include_unprotected_land_in_regrowth_calcs=False,   # bb
  # bb
    ),  # bb
  'PDS-89p2050-Drawdown-PDScustom-aggmax-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # The current adoption is based on the FAO 2015 estimates for global area under  # bb
      # forest protection. The future adoption scenarios are based on the national and  # bb
      # international commitments for forest protection. Considering a higher rate of  # bb
      # forest degradation and reduced area of intact forest, adoption scenarios are  # bb
      # build to maximize the area under forest protection. Thus, protection of 80%-100%  # bb
      # of the intact forest were assumed in different custom adoption scenarios with  # bb
      # some scenarios assuming an early adoption 75-90% by 2030. This scenario presents  # bb
      # the result of the "Aggressive-Max, High early growth 2" PDS custom adoption  # bb
      # scenario, with standard deviation input set to "1.5" in the Custom PDS Adoption  # bb
      # sheet. The results are marginally lesser than the Book edition 1, so no new  # bb
      # scenario was created for the latter. This model upgrade involves, changes in the  # bb
      # TLA, current adoption, and creation of new custom adoption scenarios.  # bb
  # bb
      # general  # bb
      solution_category=SOLUTION_CATEGORY.LAND,   # bb
      vmas=VMAs,   # bb
      report_start_year=2020, report_end_year=2050,   # bb
  # bb
      # TLA  # bb
      use_custom_tla=False,   # bb
  # bb
      # adoption  # bb
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,   # bb
      soln_pds_adoption_basis='Fully Customized PDS',   # bb
      soln_pds_adoption_custom_name='Aggressive-Max, high early growth2',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost=0.0, ref_2014_cost=0.0,   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=0.0,   # bb
      conv_expected_lifetime=0.0,   # bb
      yield_from_conv_practice=0.0,   # bb
      yield_gain_from_conv_to_soln=0.0,   # bb
  # bb
      soln_fixed_oper_cost_per_iunit=0.0,   # bb
      conv_fixed_oper_cost_per_iunit=0.0,   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,   # bb
  # bb
      tco2eq_reduced_per_land_unit={'value': 313.791126867655, 'statistic': 'mean'},   # bb
      tco2eq_rplu_rate='One-time',   # bb
      tco2_reduced_per_land_unit=0.0,   # bb
      tco2_rplu_rate='One-time',   # bb
      tn2o_co2_reduced_per_land_unit=0.0,   # bb
      tn2o_co2_rplu_rate='One-time',   # bb
      tch4_co2_reduced_per_land_unit=0.0,   # bb
      tch4_co2_rplu_rate='One-time',   # bb
      land_annual_emissons_lifetime=30.0,   # bb
  # bb
      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',   # bb
      emissions_use_co2eq=True,   # bb
      emissions_use_agg_co2eq=True,   # bb
  # bb
      # sequestration  # bb
      seq_rate_global={'value': 0.596666666666667, 'statistic': 'mean'},   # bb
      global_multi_for_regrowth=1.0,   # bb
      degradation_rate={'value': 0.003074, 'statistic': 'mean'},   # bb
      disturbance_rate={'value': 1.57962432447763e-05, 'statistic': 'mean'},   # bb
  # bb
      delay_protection_1yr=True,   # bb
      delay_regrowth_1yr=True,   # bb
      include_unprotected_land_in_regrowth_calcs=False,   # bb
  # bb
    ),  # bb
  'PDS-92p2050-Optimum-PDScustom-high-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # The current adoption is based on the FAO 2015 estimates for global area under  # bb
      # forest protection. The future adoption scenarios are based on the national and  # bb
      # international commitments for forest protection. Considering a higher rate of  # bb
      # forest degradation and reduced area of intact forest, adoption scenarios are  # bb
      # build to maximize the area under forest protection. Thus, protection of 80%-100%  # bb
      # of the intact forest were assumed in different custom adoption scenarios with  # bb
      # some scenarios assuming an early adoption 75-90% by 2030. This scenario derives  # bb
      # the result from the "high of all" PDS custom adoption scenarios, with standard  # bb
      # deviation input set to "1.5" in the Custom PDS Adoption sheet. The results are  # bb
      # marginally higher than the Book edition 1, so no new scenario was created for  # bb
      # the latter. This model upgrade involves, changes in the TLA, current adoption,  # bb
      # and creation of new custom adoption scenarios.  # bb
  # bb
      # general  # bb
      solution_category=SOLUTION_CATEGORY.LAND,   # bb
      vmas=VMAs,   # bb
      report_start_year=2020, report_end_year=2050,   # bb
  # bb
      # TLA  # bb
      use_custom_tla=False,   # bb
  # bb
      # adoption  # bb
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,   # bb
      soln_pds_adoption_basis='Fully Customized PDS',   # bb
      soln_pds_adoption_custom_name='High of All Custom Scenarios',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost=0.0, ref_2014_cost=0.0,   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=0.0,   # bb
      conv_expected_lifetime=0.0,   # bb
      yield_from_conv_practice=0.0,   # bb
      yield_gain_from_conv_to_soln=0.0,   # bb
  # bb
      soln_fixed_oper_cost_per_iunit=0.0,   # bb
      conv_fixed_oper_cost_per_iunit=0.0,   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,   # bb
  # bb
      tco2eq_reduced_per_land_unit={'value': 313.791126867655, 'statistic': 'mean'},   # bb
      tco2eq_rplu_rate='One-time',   # bb
      tco2_reduced_per_land_unit=0.0,   # bb
      tco2_rplu_rate='One-time',   # bb
      tn2o_co2_reduced_per_land_unit=0.0,   # bb
      tn2o_co2_rplu_rate='One-time',   # bb
      tch4_co2_reduced_per_land_unit=0.0,   # bb
      tch4_co2_rplu_rate='One-time',   # bb
      land_annual_emissons_lifetime=30.0,   # bb
  # bb
      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',   # bb
      emissions_use_co2eq=True,   # bb
      emissions_use_agg_co2eq=True,   # bb
  # bb
      # sequestration  # bb
      seq_rate_global={'value': 0.596666666666667, 'statistic': 'mean'},   # bb
      global_multi_for_regrowth=1.0,   # bb
      degradation_rate={'value': 0.003074, 'statistic': 'mean'},   # bb
      disturbance_rate={'value': 1.57962432447763e-05, 'statistic': 'mean'},   # bb
  # bb
      delay_protection_1yr=True,   # bb
      delay_regrowth_1yr=True,   # bb
      include_unprotected_land_in_regrowth_calcs=False,   # bb
  # bb
    ),  # bb
}  # bb
  # bb
class ForestProtection:  # bb
  name = 'Forest Protection'  # bb
  units = {  # bb
    "implementation unit": None,  # bb
    "functional unit": "Mha",  # bb
    "first cost": "US$B",  # bb
    "operating cost": "US$B",  # bb
  }  # bb
  # bb
  def __init__(self, scenario=None):  # bb
    if scenario is None:  # bb
      scenario = 'PDS-87p2050-Plausible-PDScustom-avg-Bookedition1'  # bb
    self.scenario = scenario  # bb
    self.ac = scenarios[scenario]  # bb
  # bb
    # TLA  # bb
    self.ae = aez.AEZ(solution_name=self.name)  # bb
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())  # bb
  # bb
    # Custom PDS Data  # bb
    ca_pds_data_sources = [  # bb
      {'name': 'Aggressive-Low, Linear Trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveLow_Linear_Trend.csv')},  # bb
      {'name': 'Aggressive-High, Linear Trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveHigh_Linear_Trend.csv')},  # bb
      {'name': 'Aggressive-high early growth', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Aggressivehigh_early_growth.csv')},  # bb
      {'name': 'Aggressive-Max, high early growth1', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveMax_high_early_growth1.csv')},  # bb
      {'name': 'Aggressive-Max, high early growth2', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveMax_high_early_growth2.csv')},  # bb
      {'name': 'Aggressive-Max, urgent complete early growth', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_AggressiveMax_urgent_complete_early_growth.csv')},  # bb
    ]  # bb
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,  # bb
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,  # bb
        high_sd_mult=1.5, low_sd_mult=1.0,  # bb
        total_adoption_limit=self.tla_per_region)  # bb
  # bb
    if False:  # bb
      # One may wonder why this is here. This file was code generated.  # bb
      # This 'if False' allows subsequent conditions to all be elif.  # bb
      pass  # bb
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':  # bb
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()  # bb
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()  # bb
      pds_adoption_is_single_source = None  # bb
  # bb
    ht_ref_adoption_initial = pd.Series(  # bb
      [651.0, 0.0, 0.0, 0.0, 0.0,  # bb
       0.0, 0.0, 0.0, 0.0, 0.0],  # bb
       index=REGIONS)  # bb
    ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial / self.tla_per_region.loc[2014])  # bb
    ht_ref_datapoints = pd.DataFrame(columns=REGIONS)  # bb
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial  # bb
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)  # bb
    ht_pds_adoption_initial = ht_ref_adoption_initial  # bb
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)  # bb
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))  # bb
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]  # bb
    ht_pds_datapoints = pd.DataFrame(columns=REGIONS)  # bb
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial  # bb
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)  # bb
    self.ht = helpertables.HelperTables(ac=self.ac,  # bb
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,  # bb
        pds_adoption_data_per_region=pds_adoption_data_per_region,  # bb
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,  # bb
        pds_adoption_is_single_source=pds_adoption_is_single_source)  # bb
  # bb
    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)  # bb
  # bb
    self.ua = unitadoption.UnitAdoption(ac=self.ac,  # bb
        pds_total_adoption_units=self.tla_per_region,  # bb
        electricity_unit_factor=1000000.0,  # bb
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),  # bb
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),  # bb
        bug_cfunits_double_count=True)  # bb
    soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()  # bb
    soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()  # bb
    conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()  # bb
    soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()  # bb
  # bb
    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,  # bb
        ref_learning_increase_mult=2, conv_learning_increase_mult=2,  # bb
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,  # bb
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,  # bb
        conv_ref_tot_iunits=conv_ref_tot_iunits,  # bb
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),  # bb
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),  # bb
        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),  # bb
        conv_ref_first_cost_uses_tot_units=True,  # bb
        fc_convert_iunit_factor=land.MHA_TO_HA)  # bb
  # bb
    self.oc = operatingcost.OperatingCost(ac=self.ac,  # bb
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,  # bb
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,  # bb
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,  # bb
        conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),  # bb
        soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),  # bb
        soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),  # bb
        conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),  # bb
        single_iunit_purchase_year=2017,  # bb
        soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),  # bb
        conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit(),  # bb
        conversion_factor=land.MHA_TO_HA)  # bb
  # bb
    self.c4 = ch4calcs.CH4Calcs(ac=self.ac,  # bb
        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),  # bb
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)  # bb
  # bb
    self.c2 = co2calcs.CO2Calcs(ac=self.ac,  # bb
        ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),  # bb
        soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),  # bb
        soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),  # bb
        soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),  # bb
        soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),  # bb
        soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),  # bb
        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),  # bb
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),  # bb
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),  # bb
        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),  # bb
        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),  # bb
        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),  # bb
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,  # bb
        tot_red_in_deg_land=self.ua.cumulative_reduction_in_total_degraded_land(),  # bb
        pds_protected_deg_land=self.ua.pds_cumulative_degraded_land_protected(),  # bb
        ref_protected_deg_land=self.ua.ref_cumulative_degraded_land_protected(),  # bb
        land_distribution=self.ae.get_land_distribution())  # bb
  # bb
