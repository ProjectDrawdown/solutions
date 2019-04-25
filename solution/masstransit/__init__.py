"""Mass Transit solution model.
   Excel filename: Drawdown-Mass Transit_RRS_v1.1_29Nov2018_PUBLIC.xlsm
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
  'PDS1-21p2050-based on IEA (Book Ed.1)': advanced_controls.AdvancedControls(
      # Using a linear interpolation of the IEA's 2DS Mass Transit scenario data, we
      # project adoption to 2060. The reference scenario is based on the IEA's 6DS
      # scenario where adoption increases, peaks then declines. This was seen as more
      # realistic that the drastic increase that the standard Drawdown scenario would
      # imply. This scenario uses inputs calculated for the Drawdown book edition 1,
      # some of which have been updated since publication.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Adoption Based on IEA 6DS', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Book Edition 1 Scenario 1', 
      pds_adoption_use_ref_years=[2015, 2016, 2017, 2018, 2019, 2020, 2021], 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=7.019830211942056, soln_avg_annual_use=7.019830211942056, 
      conv_lifetime_capacity=14.162003603585898, conv_avg_annual_use=14.162003603585898, 

      soln_var_oper_cost_per_funit=0.14, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.013273817396536613, conv_fuel_cost_per_funit=0.0553033150884721, 
      conv_fixed_oper_cost_per_iunit=1.5971260490990509, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=1.864345210577371e-05, 
      conv_indirect_co2_per_unit=3.097673458077077e-05, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=9.261385289614363e-12, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.052941803480931623, soln_fuel_efficiency_factor=0.8268821867810374, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.002273941593, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS2-35p2050-based on ITDP/UCD (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take the Global High Shift Cycling Scenario data from the ITDP's 2015
      # publication, and interpolate for missing years using a 3rd degree polynomial
      # curve fit. The reference scenario is based on the IEA 6DS scenario where
      # adoption increases then peaks and declines. This was used instead of the
      # standard Drawdown reference scenario since that was seen as too optimistic given
      # current trends. This scenario uses inputs calculated for the Drawdown book
      # edition 1, some of which have been updated since publication.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Adoption Based on IEA 6DS', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Book Edition 1 Scenario 2', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=7.019830211942056, soln_avg_annual_use=7.019830211942056, 
      conv_lifetime_capacity=14.162003603585898, conv_avg_annual_use=14.162003603585898, 

      soln_var_oper_cost_per_funit=0.14, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.013273817396536613, conv_fuel_cost_per_funit=0.0553033150884721, 
      conv_fixed_oper_cost_per_iunit=1.5971260490990509, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=1.864345210577371e-05, 
      conv_indirect_co2_per_unit=3.097673458077077e-05, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=9.261385289614363e-12, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.052941803480931623, soln_fuel_efficiency_factor=0.8268821867810374, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.002273941593, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS3-45p2050-linear (Book Ed.1)': advanced_controls.AdvancedControls(
      # Taking the maximum expected mass transit mobility worldwide as 45% of the Urban
      # mobility TAM in 2050, we project a linear growth out to 2050 from current
      # adoption. The reference scenario is based on the IEA's 6DS scenario where
      # adoption increases, peaks then declines. This was seen as more realistic that
      # the drastic increase that the standard Drawdown scenario would imply. This
      # scenario uses inputs calculated for the Drawdown book edition 1, some of which
      # have been updated since publication.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Custom', 
      soln_ref_adoption_custom_name='Adoption Based on IEA 6DS', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.45), ('OECD90', 0.45), ('Eastern Europe', 0.45), ('Asia (Sans Japan)', 0.45), ('Middle East and Africa', 0.45), ('Latin America', 0.45), ('China', 0.45), ('India', 0.45), ('EU', 0.45), ('USA', 0.45)], 

      # financial
      pds_2014_cost=0.0, ref_2014_cost=0.0, 
      conv_2014_cost=0.0, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=7.019830211942056, soln_avg_annual_use=7.019830211942056, 
      conv_lifetime_capacity=14.162003603585898, conv_avg_annual_use=14.162003603585898, 

      soln_var_oper_cost_per_funit=0.14, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.013273817396536613, conv_fuel_cost_per_funit=0.0553033150884721, 
      conv_fixed_oper_cost_per_iunit=1.5971260490990509, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=1.864345210577371e-05, 
      conv_indirect_co2_per_unit=3.097673458077077e-05, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=9.261385289614363e-12, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.052941803480931623, soln_fuel_efficiency_factor=0.8268821867810374, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.002273941593, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
}

class MassTransit:
  name = 'Mass Transit'
  units = {
    "implementation unit": "Urban trip",
    "functional unit": "Pkm (urban)",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-21p2050-based on IEA (Book Ed.1)'
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
          'ICCT, 2012, "Global Transportation Roadmap Model" + Non-motorized Travel Adjustment': THISDIR.joinpath('tam_ICCT_2012_Global_Transportation_Roadmap_Model_Nonmotorized_Trav7dc8c23e.csv'),
      },
      'Conservative Cases': {
          'ETP 2016, URBAN 4 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam_ETP_2016_URBAN_4_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - Baseline Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated700acab5.csv'),
      },
      'Ambitious Cases': {
          'ETP 2016, URBAN 2 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam_ETP_2016_URBAN_2_DS_Nonmotorized_Travel_Adjustment.csv'),
          'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - HighShift Scenario': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updatede9cf6e2b.csv'),
      },
      'Region: OECD90': {
        'Ambitious Cases': {
          'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated052085ff.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Ambitious Cases': {
          'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated052085ff.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Ambitious Cases': {
          'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated052085ff.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Ambitious Cases': {
          'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated052085ff.csv'),
        },
      },
      'Region: Latin America': {
        'Ambitious Cases': {
          'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated052085ff.csv'),
        },
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      tam_pds_data_sources=tam_ref_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Drawdown Book Edition 1 Scenario 1', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_1.csv')},
      {'name': 'Drawdown Book Edition 1 Scenario 2', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_2.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0)

    # Custom REF Data
    ca_ref_data_sources = [
      {'name': 'Custom REF Adoption - Fixed Mass Transit Pass-km Annually', 'include': False,
          'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Custom_REF_Adoption_Fixed_Mass_Transit_Passkm_Annually.csv')},
      {'name': 'Adoption Based on IEA 6DS', 'include': False,
          'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Adoption_based_on_IEA_6DS.csv')},
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
      [9607070620938.643, 2177533057697.923, 575975431282.0925, 4506889445113.769, 1416146219920.7346,
       1334877448730.5225, 0.0, 0.0, 0.0, 0.0],
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

