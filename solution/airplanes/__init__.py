"""Aircraft Fuel Efficiency solution model.
   Excel filename: Drawdown-Aircraft Fuel Efficiency_RRS_v1.1_5Dec2018_PUBLIC.xlsm
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

from model import tam
from solution import rrs

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

scenarios = {
  'PDS1-68p2050_14.9% Efficiency (Book Ed.1)': advanced_controls.AdvancedControls(
      # Taking the production rate of aircraft by the two major suppliers - Airbus and
      # Boeing, we project the production of "efficient model" aircraft over the future.
      # Each aircraft in the fleet is assumed to work around an average number of
      # passenger-km per year according to an estimate for each of single aisle and twin
      # aisle from our brief schedule calculations including downtime for maintenance
      # checks, and new models offer around 15% efficiency improvement. We assume that
      # the production rate of the big players remains constant. This book scenario uses
      # previously estimated inputs (including lifetime, annual use, operations cost and
      # fuel emissions factors) which have been updated in the latest scenario.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 1', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=18028435.066958193, ref_2014_cost=18028435.066958193, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=10.120965472617776, soln_avg_annual_use=0.42170689469240735, 
      conv_lifetime_capacity=10.500501677840942, conv_avg_annual_use=0.42170689469240735, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=65213534.48438975, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=76646661.48997816, 
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
      conv_fuel_consumed_per_funit=64983529.2760908, soln_fuel_efficiency_factor=0.14916666666666664, 
      conv_fuel_emissions_factor=0.0017733703679999999, soln_fuel_emissions_factor=0.0017733703679999999, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS2-73p2050_3rd Manufacturer+Retrofit (Book Ed.1)': advanced_controls.AdvancedControls(
      # Taking the production rate of aircraft by the two major suppliers - Airbus and
      # Boeing, we project the production of "efficient model" aircraft over the future.
      # We also assume that a third manufacturer enters the market (possibly COMAC or
      # UAC) in 2025 and produces first single aisle then twin aisle aircraft of
      # competitive quality. 50 aircraft per year are retrofitted to equivalent new-
      # aircraft efficiency. Each aircraft in the fleet is assumed to work around an
      # average number of passenger-km per year according to an estimate for each of
      # single aisle and twin aisle from our brief schedule calculations including
      # downtime for maintenance checks, and new models are 15% more efficient). We
      # assume that the production rate of the big players remains constant, and the
      # newcomer produces 60 single aisle and 30 twin aisle p.a. This book scenario uses
      # previously estimated inputs (including lifetime, annual use, operations cost and
      # fuel emissions factors) which have been updated in the latest scenario

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 2', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=18028435.066958193, ref_2014_cost=18028435.066958193, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=10.120965472617776, soln_avg_annual_use=0.42170689469240735, 
      conv_lifetime_capacity=10.500501677840942, conv_avg_annual_use=0.42170689469240735, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=65213534.48438975, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=76646661.48997816, 
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
      conv_fuel_consumed_per_funit=64983529.2760908, soln_fuel_efficiency_factor=0.14916666666666664, 
      conv_fuel_emissions_factor=0.0017733703679999999, soln_fuel_emissions_factor=0.0017733703679999999, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS3-73p2050_3rd Manufacturer+Retrofit+18% (Book Ed.1)': advanced_controls.AdvancedControls(
      # Taking the production rate of aircraft by the two major suppliers - Airbus and
      # Boeing, we project the production of "efficient model" aircraft over the future.
      # We also assume that a third manufacturer enters the market (possibly COMAC or
      # UAC) in 2025 and produces first single aisle then twin aisle aircraft of
      # competitive quality. 50 aircraft per year are retrofitted to equivalent new-
      # aircraft efficiency. Each aircraft in the fleet is assumed to work around an
      # average number of passenger-km per year according to an estimate for each of
      # single aisle and twin aisle from our brief schedule calculations including
      # downtime for maintenance checks, and new models are 18.3% more efficient). We
      # assume that the production rate of the big players remains constant, and the
      # newcomer produces 60 single aisle and 30 twin aisle p.a. This book scenario uses
      # previously estimated inputs (including lifetime, annual use, operations cost and
      # fuel emissions factors) which have been updated in the latest scenario

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 2', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=18028435.066958193, ref_2014_cost=18028435.066958193, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=10.120965472617776, soln_avg_annual_use=0.42170689469240735, 
      conv_lifetime_capacity=10.500501677840942, conv_avg_annual_use=0.42170689469240735, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=65213534.48438975, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=76646661.48997816, 
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
      conv_fuel_consumed_per_funit=64983529.2760908, soln_fuel_efficiency_factor=0.183, 
      conv_fuel_emissions_factor=0.0017733703679999999, soln_fuel_emissions_factor=0.0017733703679999999, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
}

class Airplanes:
  name = 'Aircraft Fuel Efficiency'
  units = {
    "implementation unit": "Aircraft",
    "functional unit": "Billion passenger km",
    "first cost": "US$B",
    "operating cost": "US$B",
  }


  def __init__(self, scenario=None):
    datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS1-68p2050_14.9% Efficiency (Book Ed.1)'
    self.scenario = scenario
    self.ac = scenarios[scenario]

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
          'Based on: IEA ETP 2016 6DS': thisdir.joinpath('tam_based_on_IEA_ETP_2016_6DS.csv'),
          'ICCT (2012) Global Roadmap Model': thisdir.joinpath('tam_ICCT_2012_Global_Roadmap_Model.csv'),
      },
      'Conservative Cases': {
          'Based on: IEA ETP 2016 4DS': thisdir.joinpath('tam_based_on_IEA_ETP_2016_4DS.csv'),
      },
      'Ambitious Cases': {
          'Based on: IEA ETP 2016 2DS': thisdir.joinpath('tam_based_on_IEA_ETP_2016_2DS.csv'),
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
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources, adconfig=adconfig)

    ca_pds_data_sources = [
      {'name': 'PDS1 - Drawdown Projection of Production of Efficient Aircraft of Airbus and Boeing and Third Manufacturer at 13%', 'include': False,
          'filename': str(thisdir.joinpath('custom_pds_ad_PDS1_Drawdown_Projection_of_Production_of_Efficient_Aircraft_of_.csv'))},
      {'name': 'PDS2 - Drawdown Projection of Production of Efficient Aircraft of Airbus and Boeing and Third Manufacturer at 18%', 'include': False,
          'filename': str(thisdir.joinpath('custom_pds_ad_PDS2_Drawdown_Projection_of_Production_of_Efficient_Aircraft_of_.csv'))},
      {'name': 'PDS3 - Drawdown Projection of Production of Efficient Aircraft of Airbus and Boeing and Third Manufacturer at 20%', 'include': False,
          'filename': str(thisdir.joinpath('custom_pds_ad_PDS3_Drawdown_Projection_of_Production_of_Efficient_Aircraft_of_.csv'))},
      {'name': 'Book Ed.1 Scenario 1', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Book_Ed_1_Scenario_1.csv'))},
      {'name': 'Book Ed.1 Scenario 2', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Book_Ed_1_Scenario_2.csv'))},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name)

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = True
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()

    ht_ref_adoption_initial = pd.Series(
      [490.5239834755743, 0.0, 0.0, 0.0, 0.0,
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
                                        ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
                                        pds_adoption_data_per_region=pds_adoption_data_per_region,
                                        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=datadir,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
        repeated_cost_for_iunits=False,
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

    self.VMAs = []

