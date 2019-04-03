"""Electric Bicycles solution model.
   Excel filename: Drawdown-Electric Bicycles_RRS_v1.1_30Nov2018_PUBLIC.xlsm
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
REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

scenarios = {
  'PDS1-3p2050_Based on Navigant, Bloomberg (Book Ed.1)': advanced_controls.AdvancedControls(
      # Using sales data from Navigant and other data from Bloomberg, we estimate the
      # stock of e-bikes in each Drawdown Region. We assume that Sealed Lead Acid (SLA)
      # batteries are retired/replaced every three years, and that Lithium Ion batteries
      # (Li) are replaced every 8 years. We further assume that over time more sales for
      # Li batteries occurs as a percent of all e-bike battery sales. Sales growth slows
      # from 5% or 2% in some regions to 1% worldwide. This scenario has older inputs
      # that match those used for the book edition 1, but which have been updated in the
      # newer scenarios.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Book Reference Scenario', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 1', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=391146.9061220421, ref_2014_cost=391146.9061220421, 
      conv_2014_cost=533792.5232451062, 
      soln_first_cost_efficiency_rate=0.06, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.045, 
      soln_lifetime_capacity=0.017048616067320818, soln_avg_annual_use=0.009300303712680364, 
      conv_lifetime_capacity=0.1615250444807001, conv_avg_annual_use=0.010728885808352105, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=8200.07908254629, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=19796898.423763297, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=119.47434825446553, 
      conv_indirect_co2_per_unit=363.08846239681094, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=5.865578742880033e-05, conv_annual_energy_used=0.004239652217925736, 
      conv_fuel_consumed_per_funit=34734831.72341607, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS2-5p2050_Based on ITDP/UCD (Book Ed.1)': advanced_controls.AdvancedControls(
      # ITDP and UCDavis published their Global High Shift (and then High Shift Cycling)
      # Scenario results in 2014-2015. Using this raw data, we interpolate and
      # extrapolate where data are unavailable. Regions are regrouped according to our
      # best matching to Drawdown regions. This scenario uses inputs from previous
      # models used to develop results for the Drawdown book Edition 1, some of which
      # have been updated in newer scenarios.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Book Reference Scenario', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 2', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=391146.9061220421, ref_2014_cost=391146.9061220421, 
      conv_2014_cost=533792.5232451062, 
      soln_first_cost_efficiency_rate=0.06, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.045, 
      soln_lifetime_capacity=0.017048616067320818, soln_avg_annual_use=0.009300303712680364, 
      conv_lifetime_capacity=0.1615250444807001, conv_avg_annual_use=0.010728885808352105, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=8200.07908254629, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=19796898.423763297, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=119.47434825446553, 
      conv_indirect_co2_per_unit=363.08846239681094, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=5.865578742880033e-05, conv_annual_energy_used=0.004239652217925736, 
      conv_fuel_consumed_per_funit=34734831.72341607, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS3-6p2050_Growth to 6.5% (Book Ed.1)': advanced_controls.AdvancedControls(
      # We assume that adoption growth to 6.5% linearly by 2050, and also that all users
      # switch from ICE cars, hence the conventional emissions are based on only fuel
      # emissions. This scenario uses inputs for the model developed for the Drawdown
      # book edition 1, some inputs which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Book Reference Scenario', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.065), ('OECD90', 0.065), ('Eastern Europe', 0.065), ('Asia (Sans Japan)', 0.065), ('Middle East and Africa', 0.065), ('Latin America', 0.065), ('China', 0.065), ('India', 0.065), ('EU', 0.065), ('USA', 0.065)], 

      # financial
      pds_2014_cost=391146.9061220421, ref_2014_cost=391146.9061220421, 
      conv_2014_cost=533792.5232451062, 
      soln_first_cost_efficiency_rate=0.06, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.045, 
      soln_lifetime_capacity=0.017048616067320818, soln_avg_annual_use=0.009300303712680364, 
      conv_lifetime_capacity=0.1615250444807001, conv_avg_annual_use=0.010728885808352105, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=8200.07908254629, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=19796898.423763297, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=119.47434825446553, 
      conv_indirect_co2_per_unit=363.08846239681094, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=5.865578742880033e-05, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=52940977.6576322, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
}

class ElectricBicycles:
  name = 'Electric Bicycles'
  units = {
    "implementation unit": "MWh of Batteries",
    "functional unit": "Billion PKM",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-3p2050_Based on Navigant, Bloomberg (Book Ed.1)'
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
          'ETP 2016, URBAN 6 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam_ETP_2016_URBAN_6_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ICCT, 2012, "Global Transportation Roadmap Model" + Non-motorized Travel Adjustment': THISDIR.joinpath('tam_ICCT_2012_Global_Transportation_Roadmap_Model_Nonmotorized_Travd9c4b8f9.csv'),
      },
      'Conservative Cases': {
          'ETP 2016, URBAN 4 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam_ETP_2016_URBAN_4_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ITDP/UC Davis 2014 Global High Shift Baseline': THISDIR.joinpath('tam_ITDPUC_Davis_2014_Global_High_Shift_Baseline.csv'),
      },
      'Ambitious Cases': {
          'ETP 2016, URBAN 2 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam_ETP_2016_URBAN_2_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ITDP/UC Davis 2014 Global High Shift HighShift': THISDIR.joinpath('tam_ITDPUC_Davis_2014_Global_High_Shift_HighShift.csv'),
      },
      'Region: OECD90': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baselinc9982a01.csv'),
        },
        'Ambitious Cases': {
          'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_sh9baf7ca0.csv'),
        },
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      tam_pds_data_sources=tam_ref_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Book Ed.1 Scenario 1', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_1.csv')},
      {'name': 'Book Ed.1 Scenario 2', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_2.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0)

    # Custom REF Data
    ca_ref_data_sources = [
      {'name': 'Book Reference Scenario', 'include': False,
          'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Book_Reference_Scenario.csv')},
    ]
    self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
        soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0)
    ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = None
    elif self.ac.soln_pds_adoption_basis == 'Linear':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = None
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [561.0, 35.63818652262168, 1.9927024684919843, 441.0159122922099, 1.248023339153054,
       3.6014881104912106, 277.7410283849392, 5.674389798859366, 28.00294411913302, 7.901342605929202],
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
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
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

