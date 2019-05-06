"""Tropical Tree Staples solution model.  # bb
   Excel filename: Tropical_Tree_Staples(Grassland)_L-Use_v1.1b_02Aug18.xlsm  # bb
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
  'PDS-52p2050-Plausible-PDScustom-low-BookVersion1': advanced_controls.AdvancedControls(  # bb
      # The current adoption of this solution is based on the historical data  # bb
      # (1962-2012) available on tropical staple crops (avocados, bananas, Brazil nuts,  # bb
      # carobs, cashew nuts, coconuts, dates, oil palm, plantains) for different regions  # bb
      # from FAO. The data was interpolated to get the current adoption value in the  # bb
      # year 2014. The future adoption was also projected based on the historical growth  # bb
      # rate with some of the custom scenarios assuming an early growth (60-75%) by  # bb
      # 2030. This scenario presents the "low of all" PDS custom adoption scenario. The  # bb
      # results are marginally higher than the Book Version 1 result, so no separate  # bb
      # scenario was stored for the later. This version involves changes in the net  # bb
      # profit margin calculation methodology, correction of current adoption value,  # bb
      # revision of the custom adoption scenarios, and estimation of operational cost  # bb
      # which was missing in the Book Version 1. This solution was allocated both in the  # bb
      # cropland and grassland AEZs, so we have created two separate models for this  # bb
      # solution. One for the cropland AEZs and one for the grassland AEZs. The model  # bb
      # built for the cropland AEZs has only half of the allocated current adoption of  # bb
      # this solution, so that model doesn't have any future adoption scenarios and  # bb
      # therefore no results were generated there. This model is built for the grassland  # bb
      # AEZs, where half of the current adoption and all of the future adoption of this  # bb
      # solution is allocated. Thus, for this solution, the results are coming only from  # bb
      # this model, although we have created two separate models.  # bb
  # bb
      # general  # bb
      solution_category=SOLUTION_CATEGORY.LAND,   # bb
      vmas=VMAs,   # bb
      report_start_year=2020, report_end_year=2050,   # bb
  # bb
      # TLA  # bb
      use_custom_tla=True,   # bb
  # bb
      # adoption  # bb
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,   # bb
      soln_pds_adoption_basis='Fully Customized PDS',   # bb
      soln_pds_adoption_custom_name='Low of All Custom Scenarios',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost='mean', ref_2014_cost='mean',   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
      yield_from_conv_practice='mean',   # bb
      yield_gain_from_conv_to_soln=0.0,   # bb
  # bb
      soln_fixed_oper_cost_per_iunit='mean',   # bb
      conv_fixed_oper_cost_per_iunit='mean',   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
  # bb
      tco2eq_reduced_per_land_unit=0.0,   # bb
      tco2eq_rplu_rate='One-time',   # bb
      tco2_reduced_per_land_unit=0.0,   # bb
      tco2_rplu_rate='One-time',   # bb
      tn2o_co2_reduced_per_land_unit=0.0,   # bb
      tn2o_co2_rplu_rate='One-time',   # bb
      tch4_co2_reduced_per_land_unit=0.0,   # bb
      tch4_co2_rplu_rate='One-time',   # bb
      land_annual_emissons_lifetime=100.0,   # bb
  # bb
      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',   # bb
      emissions_use_co2eq=True,   # bb
      emissions_use_agg_co2eq=True,   # bb
  # bb
      # sequestration  # bb
      seq_rate_global='mean',   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
  'PDS-68p2050-Drawdown-PDScustom-avg-BookVersion1': advanced_controls.AdvancedControls(  # bb
      # The current adoption of this solution is based on the historical data  # bb
      # (1962-2012) available on tropical staple crops (avocados, bananas, Brazil nuts,  # bb
      # carobs, cashew nuts, coconuts, dates, oil palm, plantains) for different regions  # bb
      # from FAO. The data was interpolated to get the current adoption value in the  # bb
      # year 2014. The future adoption was also projected based on the historical growth  # bb
      # rate with some of the custom scenarios assuming an early growth (60-75%) by  # bb
      # 2030. This scenario presents the "average of all" PDS custom adoption scenario.  # bb
      # The results are marginally higher than the Book Version 1 result, so no separate  # bb
      # scenario was stored for the later. This version involves changes in the net  # bb
      # profit margin calculation methodology, correction of current adoption value,  # bb
      # revision of the custom adoption scenarios, and estimation of operational cost  # bb
      # which was missing in the Book Version 1. This solution was allocated both in the  # bb
      # cropland and grassland AEZs, so we have created two separate models for this  # bb
      # solution. One for the cropland AEZs and one for the grassland AEZs. The model  # bb
      # built for the cropland AEZs has only half of the allocated current adoption of  # bb
      # this solution, so that model doesn't have any future adoption scenarios and  # bb
      # therefore no results were generated there. This model is built for the grassland  # bb
      # AEZs, where half of the current adoption and all of the future adoption of this  # bb
      # solution is allocated. Thus, for this solution, the results are coming only from  # bb
      # this model, although we have created two separate models.  # bb
  # bb
      # general  # bb
      solution_category=SOLUTION_CATEGORY.LAND,   # bb
      vmas=VMAs,   # bb
      report_start_year=2020, report_end_year=2050,   # bb
  # bb
      # TLA  # bb
      use_custom_tla=True,   # bb
  # bb
      # adoption  # bb
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,   # bb
      soln_pds_adoption_basis='Fully Customized PDS',   # bb
      soln_pds_adoption_custom_name='Average of All Custom Scenarios',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost='mean', ref_2014_cost='mean',   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
      yield_from_conv_practice='mean',   # bb
      yield_gain_from_conv_to_soln=0.0,   # bb
  # bb
      soln_fixed_oper_cost_per_iunit='mean',   # bb
      conv_fixed_oper_cost_per_iunit='mean',   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
  # bb
      tco2eq_reduced_per_land_unit=0.0,   # bb
      tco2eq_rplu_rate='One-time',   # bb
      tco2_reduced_per_land_unit=0.0,   # bb
      tco2_rplu_rate='One-time',   # bb
      tn2o_co2_reduced_per_land_unit=0.0,   # bb
      tn2o_co2_rplu_rate='One-time',   # bb
      tch4_co2_reduced_per_land_unit=0.0,   # bb
      tch4_co2_rplu_rate='One-time',   # bb
      land_annual_emissons_lifetime=100.0,   # bb
  # bb
      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',   # bb
      emissions_use_co2eq=True,   # bb
      emissions_use_agg_co2eq=True,   # bb
  # bb
      # sequestration  # bb
      seq_rate_global='mean',   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
  'PDS-84p2050-Optimum-PDScustom-high-BookVersion1': advanced_controls.AdvancedControls(  # bb
      # The current adoption of this solution is based on the historical data  # bb
      # (1962-2012) available on tropical staple crops (avocados, bananas, Brazil nuts,  # bb
      # carobs, cashew nuts, coconuts, dates, oil palm, plantains) for different regions  # bb
      # from FAO. The data was interpolated to get the current adoption value in the  # bb
      # year 2014. The future adoption was also projected based on the historical growth  # bb
      # rate with some of the custom scenarios assuming an early growth (60-75%) by  # bb
      # 2030. This scenario presents the "high of all" PDS custom adoption scenario. The  # bb
      # results are marginally higher than the Book Version 1 result, so no separate  # bb
      # scenario was stored for the later. This version involves changes in the net  # bb
      # profit margin calculation methodology, correction of current adoption value,  # bb
      # revision of the custom adoption scenarios, and estimation of operational cost  # bb
      # which was missing in the Book Version 1. This solution was allocated both in the  # bb
      # cropland and grassland AEZs, so we have created two separate models for this  # bb
      # solution. One for the cropland AEZs and one for the grassland AEZs. The model  # bb
      # built for the cropland AEZs has only half of the allocated current adoption of  # bb
      # this solution, so that model doesn't have any future adoption scenarios and  # bb
      # therefore no results were generated there. This model is built for the grassland  # bb
      # AEZs, where half of the current adoption and all of the future adoption of this  # bb
      # solution is allocated. Thus, for this solution, the results are coming only from  # bb
      # this model, although we have created two separate models.  # bb
  # bb
      # general  # bb
      solution_category=SOLUTION_CATEGORY.LAND,   # bb
      vmas=VMAs,   # bb
      report_start_year=2020, report_end_year=2050,   # bb
  # bb
      # TLA  # bb
      use_custom_tla=True,   # bb
  # bb
      # adoption  # bb
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,   # bb
      soln_pds_adoption_basis='Fully Customized PDS',   # bb
      soln_pds_adoption_custom_name='High of All Custom Scenarios',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost='mean', ref_2014_cost='mean',   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
      yield_from_conv_practice='mean',   # bb
      yield_gain_from_conv_to_soln=0.0,   # bb
  # bb
      soln_fixed_oper_cost_per_iunit='mean',   # bb
      conv_fixed_oper_cost_per_iunit='mean',   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
  # bb
      tco2eq_reduced_per_land_unit=0.0,   # bb
      tco2eq_rplu_rate='One-time',   # bb
      tco2_reduced_per_land_unit=0.0,   # bb
      tco2_rplu_rate='One-time',   # bb
      tn2o_co2_reduced_per_land_unit=0.0,   # bb
      tn2o_co2_rplu_rate='One-time',   # bb
      tch4_co2_reduced_per_land_unit=0.0,   # bb
      tch4_co2_rplu_rate='One-time',   # bb
      land_annual_emissons_lifetime=100.0,   # bb
  # bb
      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',   # bb
      emissions_use_co2eq=True,   # bb
      emissions_use_agg_co2eq=True,   # bb
  # bb
      # sequestration  # bb
      seq_rate_global='mean',   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
}  # bb
  # bb
class TropicalTreeStaples:  # bb
  name = 'Tropical Tree Staples'  # bb
  units = {  # bb
    "implementation unit": None,  # bb
    "functional unit": "Mha",  # bb
    "first cost": "US$B",  # bb
    "operating cost": "US$B",  # bb
  }  # bb
  # bb
  def __init__(self, scenario=None):  # bb
    if scenario is None:  # bb
      scenario = 'PDS-52p2050-Plausible-PDScustom-low-BookVersion1'  # bb
    self.scenario = scenario  # bb
    self.ac = scenarios[scenario]  # bb
  # bb
    # TLA  # bb
    self.ae = aez.AEZ(solution_name=self.name)  # bb
    if self.ac.use_custom_tla:  # bb
      self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))  # bb
      custom_world_vals = self.c_tla.get_world_values()  # bb
    else:  # bb
      custom_world_vals = None  # bb
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(), custom_world_values=custom_world_vals)  # bb
  # bb
    # Custom PDS Data  # bb
    ca_pds_data_sources = [  # bb
      {'name': 'Average growth, linear trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Average_growth_linear_trend.csv')},  # bb
      {'name': 'Medium growth, linear trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Medium_growth_linear_trend.csv')},  # bb
      {'name': 'Low growth linear trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_growth_linear_trend.csv')},  # bb
      {'name': 'Low early growth, linear trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_early_growth_linear_trend.csv')},  # bb
      {'name': 'Max early growth, linear trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Max_early_growth_linear_trend.csv')},  # bb
    ]  # bb
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,  # bb
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,  # bb
        high_sd_mult=1.0, low_sd_mult=1.0)  # bb
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
      [25.424461981811515, 0.03142549034684199, 0.0, 28.59165470128803, 17.01389600193888,  # bb
       5.211947770049295, 0.0, 0.0, 0.0, 0.0],  # bb
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
        land_distribution=self.ae.get_land_distribution())  # bb
  # bb
