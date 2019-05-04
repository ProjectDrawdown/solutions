"""Silvopasture solution model.  # bb
   Excel filename: Drawdown-Silvopasture_BioS_v1.1_3Jan2019_PUBLIC.xlsm  # bb
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
  'PDS-45p2050-Plausible-PDScustom-low-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # This scenario represents the results based on the revisions made to the current  # bb
      # adoption, future adoption scenarios, first cost, net profit margin, and carbon  # bb
      # sequestration. In addition, the revised model also estimates the operational  # bb
      # cost which was missing in the Book edition 1. This scenario derives result from  # bb
      # "low of all" PDS custom scenario. The results are marginally lower than Book  # bb
      # edition1, so no new scenario was created for the latter.  # bb
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
      soln_pds_adoption_custom_name='Low of All Custom Scenarios',   # bb
      pds_adoption_use_ref_years=[2015, 2016],   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost={'value': 462.453005939073, 'statistic': 'mean'}, ref_2014_cost={'value': 462.453005939073, 'statistic': 'mean'},   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
      yield_from_conv_practice={'value': 3.42857142857143, 'statistic': 'mean'},   # bb
      yield_gain_from_conv_to_soln={'value': 0.100544967245763, 'statistic': 'mean'},   # bb
  # bb
      soln_fixed_oper_cost_per_iunit={'value': 837.643130909091, 'statistic': 'mean'},   # bb
      conv_fixed_oper_cost_per_iunit={'value': 328.415857769938, 'statistic': 'mean'},   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,   # bb
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
      seq_rate_global={'value': 4.64561688311688, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
      harvest_frequency=100.0,   # bb
      carbon_not_emitted_after_harvesting=0.0,   # bb
  # bb
    ),  # bb
  'PDS-54p2050-Drawdown-PDScustom-high-basedonpasture-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # This scenario represents the results based on the revisions made to the current  # bb
      # adoption, future adoption scenarios, first cost, net profit margin, and carbon  # bb
      # sequestration. In addition, the revised model also estimates the operational  # bb
      # cost which was missing in the Book edition 1. This scenario present the result  # bb
      # of the from "high growth, linear trend (based on improved pasture area) " PDS  # bb
      # custom scenario. The results are higher than the Book edition1, largely due to  # bb
      # the correction of the current adoption, which was almost half in the Book  # bb
      # edition1.  # bb
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
      soln_pds_adoption_custom_name='High growth, linear trend (based on improved pasture area)',   # bb
      pds_adoption_use_ref_years=[2015, 2016],   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost={'value': 462.453005939073, 'statistic': 'mean'}, ref_2014_cost={'value': 462.453005939073, 'statistic': 'mean'},   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
      yield_from_conv_practice={'value': 3.42857142857143, 'statistic': 'mean'},   # bb
      yield_gain_from_conv_to_soln={'value': 0.100544967245763, 'statistic': 'mean'},   # bb
  # bb
      soln_fixed_oper_cost_per_iunit={'value': 837.643130909091, 'statistic': 'mean'},   # bb
      conv_fixed_oper_cost_per_iunit={'value': 328.415857769938, 'statistic': 'mean'},   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,   # bb
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
      seq_rate_global={'value': 4.64561688311688, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
      harvest_frequency=100.0,   # bb
      carbon_not_emitted_after_harvesting=0.0,   # bb
  # bb
    ),  # bb
  'PDS-54p2050-Optimum-PDScustom-high0.5SD-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # This scenario represents the results based on the revisions made to the current  # bb
      # adoption, future adoption scenarios, first cost, net profit margin, and carbon  # bb
      # sequestration. In addition, the revised model also estimates the operational  # bb
      # cost which was missing in the Book edition 1. This scenario derives result from  # bb
      # "high (with 0.5 standard deviation) of all" PDS custom scenarios. The results  # bb
      # are higher than the Book edition1, largely due to the correction of the current  # bb
      # adoption, which was almost half in the Book edition1.  # bb
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
      pds_adoption_use_ref_years=[2015, 2016],   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost={'value': 462.453005939073, 'statistic': 'mean'}, ref_2014_cost={'value': 462.453005939073, 'statistic': 'mean'},   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
      yield_from_conv_practice={'value': 3.42857142857143, 'statistic': 'mean'},   # bb
      yield_gain_from_conv_to_soln={'value': 0.100544967245763, 'statistic': 'mean'},   # bb
  # bb
      soln_fixed_oper_cost_per_iunit={'value': 837.643130909091, 'statistic': 'mean'},   # bb
      conv_fixed_oper_cost_per_iunit={'value': 328.415857769938, 'statistic': 'mean'},   # bb
  # bb
      # emissions  # bb
      soln_indirect_co2_per_iunit=0.0,   # bb
      conv_indirect_co2_per_unit=0.0,   # bb
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,   # bb
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
      seq_rate_global={'value': 4.64561688311688, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
      harvest_frequency=100.0,   # bb
      carbon_not_emitted_after_harvesting=0.0,   # bb
  # bb
    ),  # bb
}  # bb
  # bb
class Silvopasture:  # bb
  name = 'Silvopasture'  # bb
  units = {  # bb
    "implementation unit": None,  # bb
    "functional unit": "Mha",  # bb
    "first cost": "US$B",  # bb
    "operating cost": "US$B",  # bb
  }  # bb
  # bb
  def __init__(self, scenario=None):  # bb
    if scenario is None:  # bb
      scenario = 'PDS-45p2050-Plausible-PDScustom-low-Bookedition1'  # bb
    self.scenario = scenario  # bb
    self.ac = scenarios[scenario]  # bb
  # bb
    # TLA  # bb
    self.ae = aez.AEZ(solution_name=self.name)  # bb
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())  # bb
  # bb
    # Custom PDS Data  # bb
    ca_pds_data_sources = [  # bb
      {'name': 'Linear trend based on Zomers  >30% tree cover percent area applied in grassland area', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Linear_trend_based_on_Zomers_30_tree_cover_percent_area_applied77dc7578.csv')},  # bb
      {'name': 'Linear trend based on Zomers >30% tree cover percent area and conversion of >10% are to 30% tree cover area applied in grassland area', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Linear_trend_based_on_Zomers_30_tree_cover_percent_area_and_con55dcebcb.csv')},  # bb
      {'name': 'Medium growth, linear trend', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Medium_growth_linear_trend.csv')},  # bb
      {'name': 'High growth, linear trend', 'include': False,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_growth_linear_trend.csv')},  # bb
      {'name': 'Low growth, linear trend (based on improved pasture area)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_growth_linear_trend_based_on_improved_pasture_area.csv')},  # bb
      {'name': 'High growth, linear trend (based on improved pasture area)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_growth_linear_trend_based_on_improved_pasture_area.csv')},  # bb
    ]  # bb
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,  # bb
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,  # bb
        high_sd_mult=0.5, low_sd_mult=1.0,  # bb
        total_adoption_limit=self.tla_per_region)  # bb
  # bb
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
      [314.15, 0.0, 0.0, 0.0, 0.0,  # bb
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
        ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,  # bb
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,  # bb
        pds_adoption_is_single_source=pds_adoption_is_single_source)  # bb
  # bb
    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)  # bb
  # bb
    self.ua = unitadoption.UnitAdoption(ac=self.ac,  # bb
        tla_per_region=self.tla_per_region,  # bb
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
        annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),  # bb
        land_distribution=self.ae.get_land_distribution())  # bb
  # bb
