"""Temperate Forest Restoration solution model.  # bb
   Excel filename: Drawdown-Temperate Forest Restoration_BioS_v1.1_3Jan2019_PUBLIC.xlsm  # bb
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
  'PDS-49p2050-Plausible-PDScustomadoption-avg': advanced_controls.AdvancedControls(  # bb
      # The current adoption of the solution was assumed to be 0. The future adoption  # bb
      # scenarios were built on the commitments given for temperate forest restoration  # bb
      # in the Bonn Challenge and New York Deceleration in addition to the World  # bb
      # Resources Institute's projected estimates for the solution. Several custom  # bb
      # adoption scenarios were built to project either the intact or wide scale  # bb
      # restoration of temperate forests in 15 years (by 2030), in 30 years (by 2045),  # bb
      # and in 45 years (by 2060) compare to the situation in 2015. This scenario  # bb
      # derives the result from the "average of all" PDS custom adoption scenarios. The  # bb
      # minor changes in the result in this scenario are due to the corrections made to  # bb
      # the AEZ model, which has very marginally changed the TLA of this solution.  # bb
      # Please note; there are nine custom adoption scenarios, but this scenario has  # bb
      # used only first seven custom adoption scenarios given in the "Custom PDS  # bb
      # adoption sheet".  # bb
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
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
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
      seq_rate_global={'value': 2.96222222222222, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
  'PDS-73p2050-Drawdown-PDScustomadoption-high': advanced_controls.AdvancedControls(  # bb
      # The current adoption of the solution was assumed to be 0. The future adoption  # bb
      # scenarios were built on the commitments given for temperate forest restoration  # bb
      # in the Bonn Challenge and New York Deceleration in addition to the World  # bb
      # Resources Institute's projected estimates for the solution. Several custom  # bb
      # adoption scenarios were built to project either the intact or wide scale  # bb
      # restoration of temperate forests in 15 years (by 2030), in 30 years (by 2045),  # bb
      # and in 45 years (by 2060) compare to the situation in 2015. This scenario  # bb
      # derives the result from the "high of all" PDS custom adoption scenarios. The  # bb
      # minor changes in the result in this scenario are due to the corrections made to  # bb
      # the AEZ model, which has very marginally changed the TLA of this solution.  # bb
      # Please note; there are nine custom adoption scenarios, but this scenario has  # bb
      # used only first seven custom adoption scenarios given in the "Custom PDS  # bb
      # adoption sheet".  # bb
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
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
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
      seq_rate_global={'value': 2.96222222222222, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
  'PDS-74p2050-Optimum-PDScustomadoption-max': advanced_controls.AdvancedControls(  # bb
      # The current adoption of the solution was assumed to be 0. The future adoption  # bb
      # scenarios were built on the commitments given for temperate forest restoration  # bb
      # in the Bonn Challenge and New York Deceleration in addition to the World  # bb
      # Resources Institute's projected estimates for the solution. Several custom  # bb
      # adoption scenarios were built to project either the intact or wide scale  # bb
      # restoration of temperate forests in 15 years (by 2030), in 30 years (by 2045),  # bb
      # and in 45 years (by 2060) compare to the situation in 2015. This scenario  # bb
      # presents the result of the "Optimistic-Achieve Commitment in 15 years w/ 100%  # bb
      # intact, WRI estimates (Charlotte Wheller, 2016)" PDS custom scenario. The minor  # bb
      # changes in the result in this scenario are due to the corrections made to the  # bb
      # AEZ model, which has very marginally changed the TLA of this solution. Please  # bb
      # note; there are nine custom adoption scenarios, but this scenario has used only  # bb
      # first seven custom adoption scenarios given in the "Custom PDS adoption sheet".  # bb
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
      soln_pds_adoption_custom_name='Optimistic-Achieve Commitment in 15 years w/ 100% intact, WRI estimates (Charlotte Wheeler, 2016)',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost=0.0, ref_2014_cost=0.0,   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
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
      seq_rate_global={'value': 2.96222222222222, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
  'PDS-49p2050-Plausible-PDScustom-avg-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # This scenario presents the plausible scenario results of the Book edition 1.  # bb
      # Thus, it has the same inputs as that of Book edition 1. The results based on new  # bb
      # changes are stored as separate scenarios. The current adoption of the solution  # bb
      # was assumed to be 0. The future adoption scenarios were built on the commitments  # bb
      # given for temperate forest restoration in the Bonn Challenge and New York  # bb
      # Deceleration in addition to the World Resources Institute's projected estimates  # bb
      # for the solution. Several custom adoption scenarios were built to project either  # bb
      # the intact or wide scale restoration of temperate forests in 15 years (by 2030),  # bb
      # in 30 years (by 2045), and in 45 years (by 2060) compare to the situation in  # bb
      # 2015. This scenario derives the result from the "average of all" PDS custom  # bb
      # adoption scenarios. Please note; there are nine custom adoption scenarios, but  # bb
      # this scenario has used only first seven custom adoption scenarios given in the  # bb
      # "Custom PDS adoption sheet".  # bb
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
      pds_2014_cost=0.0, ref_2014_cost=0.0,   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
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
      seq_rate_global={'value': 2.96222222222222, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
  'PDS-73p2050-Drawdown-PDScustom-high-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # This scenario presents the plausible scenario results of the Book edition 1.  # bb
      # Thus, it has the same inputs as that of Book edition 1. The results based on new  # bb
      # changes are stored as separate scenarios. The current adoption of the solution  # bb
      # was assumed to be 0. The future adoption scenarios were built on the commitments  # bb
      # given for temperate forest restoration in the Bonn Challenge and New York  # bb
      # Deceleration in addition to the World Resources Institute's projected estimates  # bb
      # for the solution. Several custom adoption scenarios were built to project either  # bb
      # the intact or wide scale restoration of temperate forests in 15 years (by 2030),  # bb
      # in 30 years (by 2045), and in 45 years (by 2060) compare to the situation in  # bb
      # 2015. This scenario derives the result from the "high of all" PDS custom  # bb
      # adoption scenarios. Please note; there are nine custom adoption scenarios, but  # bb
      # this scenario has used only first seven custom adoption scenarios given in the  # bb
      # "Custom PDS adoption sheet".  # bb
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
      pds_2014_cost=0.0, ref_2014_cost=0.0,   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
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
      seq_rate_global={'value': 2.96222222222222, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
  'PDS-74p2050-Optimum-PDScustom-100%in15years-Bookedition1': advanced_controls.AdvancedControls(  # bb
      # This scenario presents the plausible scenario results of the Book edition 1.  # bb
      # Thus, it has the same inputs as that of Book edition 1. The results based on new  # bb
      # changes are stored as separate scenarios. The current adoption of the solution  # bb
      # was assumed to be 0. The future adoption scenarios were built on the commitments  # bb
      # given for temperate forest restoration in the Bonn Challenge and New York  # bb
      # Deceleration in addition to the World Resources Institute's projected estimates  # bb
      # for the solution. Several custom adoption scenarios were built to project either  # bb
      # the intact or wide scale restoration of temperate forests in 15 years (by 2030),  # bb
      # in 30 years (by 2045), and in 45 years (by 2060) compare to the situation in  # bb
      # 2015. This scenario presents the result of the "Optimistic-Achieve Commitment in  # bb
      # 15 years w/ 100% intact, WRI estimates (Charlotte Wheller, 2016)" PDS custom  # bb
      # scenario.  # bb
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
      soln_pds_adoption_custom_name='Optimistic-Achieve Commitment in 15 years w/ 100% intact, WRI estimates (Charlotte Wheeler, 2016)',   # bb
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)],   # bb
  # bb
      # financial  # bb
      pds_2014_cost=0.0, ref_2014_cost=0.0,   # bb
      conv_2014_cost=0.0,   # bb
      soln_first_cost_efficiency_rate=0.0,   # bb
      conv_first_cost_efficiency_rate=0.0,   # bb
      npv_discount_rate=0.1,   # bb
      soln_expected_lifetime=30.0,   # bb
      conv_expected_lifetime=30.0,   # bb
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
      seq_rate_global={'value': 2.96222222222222, 'statistic': 'mean'},   # bb
      disturbance_rate=0.0,   # bb
  # bb
    ),  # bb
}  # bb
  # bb
class TemperateForests:  # bb
  name = 'Temperate Forest Restoration'  # bb
  units = {  # bb
    "implementation unit": None,  # bb
    "functional unit": "Mha",  # bb
    "first cost": "US$B",  # bb
    "operating cost": "US$B",  # bb
  }  # bb
  # bb
  def __init__(self, scenario=None):  # bb
    if scenario is None:  # bb
      scenario = 'PDS-49p2050-Plausible-PDScustomadoption-avg'  # bb
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
      {'name': 'Optimistic-Achieve Commitment in 15 years w/ 100% intact, (Charlotte Wheeler, 2016)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_OptimisticAchieve_Commitment_in_15_years_w_100_intact_Charlotted335a232.csv')},  # bb
      {'name': 'Optimistic-Achieve Commitment in 15 years w/ 100% intact, WRI estimates (Charlotte Wheeler, 2016)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_OptimisticAchieve_Commitment_in_15_years_w_100_intact_WRI_estim77145929.csv')},  # bb
      {'name': 'Conservative-Achieve Commitment in 15 years w/ 44.2% intact, (Charlotte Wheeler,2016)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_ConservativeAchieve_Commitment_in_15_years_w_44_2_intact_Charlo9cfd2163.csv')},  # bb
      {'name': 'Conservative-Achieve Commitment in 15 years w/ 44.2% intact with continued growth post-2030, (Charlotte Wheeler,2016)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_ConservativeAchieve_Commitment_in_15_years_w_44_2_intact_with_c884d17bc.csv')},  # bb
      {'name': 'Conservative-Achieve Commitment in 30 years w/ 100% intact, (Charlotte Wheeler,2016)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_ConservativeAchieve_Commitment_in_30_years_w_100_intact_Charlot524478a3.csv')},  # bb
      {'name': 'Conservative-Achieve Commitment in 30 years w/ 44.2% intact, (Charlotte Wheeler,2016)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_ConservativeAchieve_Commitment_in_30_years_w_44_2_intact_Charlo9cfd2163.csv')},  # bb
      {'name': 'Conservative-Achieve Commitment in 30 years w/ 44.2% intact with continued growth, (Charlotte Wheeler,2016)', 'include': True,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_ConservativeAchieve_Commitment_in_30_years_w_44_2_intact_with_c89569afb.csv')},  # bb
      {'name': 'Conservative-Achieve Commitment in 45 years w/ 100% intact (Charlotte Wheeler,2016)', 'include': False,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_ConservativeAchieve_Commitment_in_45_years_w_100_intact_Charlot524478a3.csv')},  # bb
      {'name': 'Conservative-Achieve Commitment in 45 years w/ 44.2% intact (Charlotte Wheeler,2016)', 'include': False,  # bb
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_ConservativeAchieve_Commitment_in_45_years_w_44_2_intact_Charlo9cfd2163.csv')},  # bb
    ]  # bb
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,  # bb
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,  # bb
        high_sd_mult=1.0, low_sd_mult=1.0,  # bb
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
      [0.0, 0.0, 0.0, 0.0, 0.0,  # bb
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
        land_distribution=self.ae.get_land_distribution())  # bb
  # bb
