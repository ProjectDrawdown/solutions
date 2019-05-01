"""Walkable Cities solution model.
   Excel filename: Drawdown-Walkable Cities_RRS_v1,1_31Dec2018_PUBLIC.xlsm
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
  'PDS1-4p2050-Based on ITDP/UCD (Book Ed.1)': advanced_controls.AdvancedControls(
      # Taking the projected walking according to ITDP/UCD's Global High Shift Cycling
      # Scenario (2015) results, we interpolate for missing years using a 3rd Degree
      # Poynomial. This is the book scenario which has the same inputs as the updated
      # scenario.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Custom REF Scenario 1: Fixed Passenger-km Annual after 2014', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Existing Adoption Prognostications', 
      soln_pds_adoption_prognostication_source='ITDP/UCD (2015) A Global High Shift Cycling Scenario - High Shift Scenario', 
      soln_pds_adoption_prognostication_trend='3rd Poly', 
      soln_pds_adoption_prognostication_growth='Medium', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_base_adoption=[('World', 1523.491464812742), ('OECD90', 205.85584501120192), ('Eastern Europe', 57.71269810953001), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 310.14334483044007), ('India', 180.29053359808), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=1.6209874133333332e-09, soln_avg_annual_use=1.6209874133333332e-09, 
      conv_lifetime_capacity=1.4162003604e-08, conv_avg_annual_use=1.4162003604e-08, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=11732406.139444258, conv_fuel_cost_per_funit=55303315.086855, 
      conv_fixed_oper_cost_per_iunit=1.5973752970573485, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=30976.73458017209, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=52941803.479383595, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS3-8p2050-Linear (Book Ed.1)': advanced_controls.AdvancedControls(
      # We project a straight linear growth in passenger-km to 7.6% of the global urban
      # mobility in 2050. This scenario was developed for the Drawdown book edition 1,
      # and has been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Custom REF Scenario 1: Fixed Passenger-km Annual after 2014', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_base_adoption=[('World', 1523.491464812742), ('OECD90', 205.85584501120192), ('Eastern Europe', 57.71269810953001), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 310.14334483044007), ('India', 180.29053359808), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.076), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=1.6209874133333332e-09, soln_avg_annual_use=1.6209874133333332e-09, 
      conv_lifetime_capacity=1.4162003604e-08, conv_avg_annual_use=1.4162003604e-08, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=11732406.139444258, conv_fuel_cost_per_funit=55303315.086855, 
      conv_fixed_oper_cost_per_iunit=1.5973752970573485, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=30976.73458017209, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=52941803.479383595, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS2-7p2050-2.4% Annual Density Increase (Book Ed.1)': advanced_controls.AdvancedControls(
      # We project the amount of walking that would happen in 1,737 cities worldwide
      # representing 57% of the global urban population then we scale the total amount
      # of walking to 100% of the world’s urban population. The background calculations
      # of this scenario use the population and density of each of the 1737 cities from
      # Demographia’s report and projects the fraction of each country’s urban
      # population in that city. We assume that that fraction is constant and then
      # project the city’s population each year to 2050 using UN projections of each
      # country’s urban population to 2050. With the TAM and total urban population
      # projections, we estimate the mobility per urban resident each year and then
      # apply 7% to walking in each city in each year when the density is over the
      # "dense city threshold" (~3,000 p/sqkm) and 2% otherwise. Each year is scaled to
      # the global urban population. City densities are assumed to increased by around
      # 2.4% annually which reverses historical declines of around 2%. This scenario was
      # calculated for the Drawdown book Edition 1. Some variables may have been
      # updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Custom REF Scenario 1: Fixed Passenger-km Annual after 2014', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='PDS2 - Increasing Urban Density with Density Driving Urban Walking (Book Ed.1)', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_base_adoption=[('World', 1523.491464812742), ('OECD90', 205.85584501120192), ('Eastern Europe', 57.71269810953001), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 310.14334483044007), ('India', 180.29053359808), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=1.6209874133333332e-09, soln_avg_annual_use=1.6209874133333332e-09, 
      conv_lifetime_capacity=1.4162003604e-08, conv_avg_annual_use=1.4162003604e-08, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=11732406.139444258, conv_fuel_cost_per_funit=55303315.086855, 
      conv_fixed_oper_cost_per_iunit=1.5973752970573485, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=30976.73458017209, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=52941803.479383595, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
}

class WalkableCities:
  name = 'Walkable Cities'
  units = {
    "implementation unit": "trip",
    "functional unit": "billion pass-km",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-4p2050-Based on ITDP/UCD (Book Ed.1)'
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
          'ETP 2016, URBAN 6 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ETP_2016_URBAN_6_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ICCT, 2012, "Global Transportation Roadmap Model" + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ICCT_2012_Global_Transportation_Roadmap_Model_Nonmotorized_Travel_Adjustment.csv'),
      },
      'Conservative Cases': {
          'ETP 2016, URBAN 4 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ETP_2016_URBAN_4_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ITDP/UC Davis 2014 Global High Shift Baseline': THISDIR.joinpath('tam', 'tam_ITDPUC_Davis_2014_Global_High_Shift_Baseline.csv'),
      },
      'Ambitious Cases': {
          'ETP 2016, URBAN 2 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ETP_2016_URBAN_2_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ITDP/UC Davis 2014 Global High Shift HighShift': THISDIR.joinpath('tam', 'tam_ITDPUC_Davis_2014_Global_High_Shift_HighShift.csv'),
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
      'Baseline Cases': {
          'ITDP/UCD (2015) A Global High Shift Cycling Scenario - Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDPUCD_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
      },
      'Ambitious Cases': {
          'ITDP/UCD (2015) A Global High Shift Cycling Scenario - High Shift Scenario': THISDIR.joinpath('ad', 'ad_ITDPUCD_2015_A_Global_High_Shift_Cycling_Scenario_High_Shift_Scenario.csv'),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'PDS2 - Density remains Constant and is the key driver of walking in cities.', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_Density_remains_Constant_and_is_the_key_driver_of_walking_in_cities_.csv')},
      {'name': 'PDS2 - Increasing Urban Density with Density Driving Urban Walking (Book Ed.1)', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_Increasing_Urban_Density_with_Density_Driving_Urban_Walking_Book_Ed_1.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
        total_adoption_limit=pds_tam_per_region)

    # Custom REF Data
    ca_ref_data_sources = [
      {'name': 'Custom REF Scenario 1: Fixed Passenger-km Annual after 2014', 'include': False,
          'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Custom_REF_Scenario_1_Fixed_Passengerkm_Annual_after_2014.csv')},
    ]
    self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
        soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
        total_adoption_limit=ref_tam_per_region)

    ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

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
    elif self.ac.soln_pds_adoption_basis == 'Linear':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = None
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [1523.491464812742, 205.85584501120192, 57.71269810953001, 0.0, 0.0,
       0.0, 310.14334483044007, 180.29053359808, 0.0, 0.0],
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
        ref_adoption_data_per_region=ref_adoption_data_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
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

