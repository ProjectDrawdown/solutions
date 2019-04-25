"""Electric Vehicles solution model.
   Excel filename: Drawdown-Electric Vehicles_RRS_v1,1_31Dec2018_PUBLIC.xlsm
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
  'PDS1-16p2050-Based on IEA 2DS (Book Ed.1)': advanced_controls.AdvancedControls(
      # We use the IEA's 2DS projection of on-road vehicles (ETP 2016) as a base and
      # convert to passenger-km using annual usage rates and average occupancy from
      # ICCT.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 1', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=47609.897539880934, ref_2014_cost=47609.897539880934, 
      conv_2014_cost=27301.838757440706, 
      soln_first_cost_efficiency_rate=0.0215, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=0.00031246110689814923, soln_avg_annual_use=2.480710964561463e-05, 
      conv_lifetime_capacity=0.00031246110689814923, conv_avg_annual_use=2.48071096456146e-05, 

      soln_var_oper_cost_per_funit=4993722.539303601, soln_fuel_cost_per_funit=21463528.037433565, 
      soln_fixed_oper_cost_per_iunit=7952.96624522827, 
      conv_var_oper_cost_per_funit=11798368.442343, conv_fuel_cost_per_funit=55302452.42866199, 
      conv_fixed_oper_cost_per_iunit=7952.96624522827, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=10.251543667017724, 
      conv_indirect_co2_per_unit=9.679024775197812, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.112943427913429, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=52941803.48093162, soln_fuel_efficiency_factor=0.897390344515709, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.002273941593, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS2-30p2050-Based on IEA (2012 ETP) (Book Ed.1)': advanced_controls.AdvancedControls(
      # Using the IEA's Energy Technology Perspectives 2012 projections of EV sales'
      # growth, we project the sales and then global EV stock. Assuming the ICCT's
      # global car occupancy average and a 50% growth in this occupancy by 2050, we
      # estimate the total passenger-km of EV during the period of analysis.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 2', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=47609.897539880934, ref_2014_cost=47609.897539880934, 
      conv_2014_cost=27301.838757440706, 
      soln_first_cost_efficiency_rate=0.0215, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=0.00031246110689814923, soln_avg_annual_use=3.100888705701825e-05, 
      conv_lifetime_capacity=0.00031246110689814923, conv_avg_annual_use=2.48071096456146e-05, 

      soln_var_oper_cost_per_funit=4993722.539303601, soln_fuel_cost_per_funit=17170822.429946873, 
      soln_fixed_oper_cost_per_iunit=6362.37299618263, 
      conv_var_oper_cost_per_funit=11798301.217552487, conv_fuel_cost_per_funit=55302452.42866199, 
      conv_fixed_oper_cost_per_iunit=6362.37299618263, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=10.251543667017724, 
      conv_indirect_co2_per_unit=9.679024775197812, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.09035474233074314, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=52941803.48093162, soln_fuel_efficiency_factor=0.9179199248358034, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.002273941593, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS3-40p2050-Based on IEA (2012 ETP)+Double Occu (Book Ed.1)': advanced_controls.AdvancedControls(
      # Using the IEA's Energy Technology Perspectives 2012 projections of EV sales'
      # growth, we project the sales and then global EV stock. Assuming twice the ICCT's
      # global car occupancy average, we estimate the total passenger-km of EV during
      # the period of analysis.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Book Ed.1 Scenario 3', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Baseline Cases', 
      pds_source_post_2014='Baseline Cases', 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=47609.897539880934, ref_2014_cost=47609.897539880934, 
      conv_2014_cost=27301.838757440706, 
      soln_first_cost_efficiency_rate=0.0215, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=0.00031246110689814923, soln_avg_annual_use=4.96142192912292e-05, 
      conv_lifetime_capacity=0.00031246110689814923, conv_avg_annual_use=2.48071096456146e-05, 

      soln_var_oper_cost_per_funit=4993722.539303601, soln_fuel_cost_per_funit=17170822.429946873, 
      soln_fixed_oper_cost_per_iunit=3976.48312261414, 
      conv_var_oper_cost_per_funit=11798301.217552487, conv_fuel_cost_per_funit=55302452.42866199, 
      conv_fixed_oper_cost_per_iunit=3976.48312261414, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=10.251543667017724, 
      conv_indirect_co2_per_unit=9.679024775197812, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.07081975120966608, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=52940977.65763215, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=0.002273941593, soln_fuel_emissions_factor=0.002273941593, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
}

class ElectricVehicles:
  name = 'Electric Vehicles'
  units = {
    "implementation unit": "vehicle",
    "functional unit": "billion passenger-km",
    "first cost": "US$B",
    "operating cost": "US$B",
  }


  def __init__(self, scenario=None):
    datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS1-16p2050-Based on IEA 2DS (Book Ed.1)'
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
          'IEA (2016), "Energy Technology Perspectives - 6DS", IEA/OECD': thisdir.joinpath('tam_IEA_2016_Energy_Technology_Perspectives_6DS_IEAOECD.csv'),
          'ICCT (2012) "Global Transport Roadmap Model", http://www.theicct.org/global-transportation-roadmap-model': thisdir.joinpath('tam_ICCT_2012_Global_Transport_Roadmap_Model_httpwww_theicct_orgglob.csv'),
      },
      'Conservative Cases': {
          'IEA (2016), "Energy Technology Perspectives - 4DS", IEA/OECD': thisdir.joinpath('tam_IEA_2016_Energy_Technology_Perspectives_4DS_IEAOECD.csv'),
      },
      'Ambitious Cases': {
          'IEA (2016), "Energy Technology Perspectives - 2DS", IEA/OECD': thisdir.joinpath('tam_IEA_2016_Energy_Technology_Perspectives_2DS_IEAOECD.csv'),
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
          'Based on IEA Reference Tech Scenario- 2017': thisdir.joinpath('ad_based_on_IEA_Reference_Tech_Scenario_2017.csv'),
      },
      'Conservative Cases': {
          'Based on OPEC World Energy Outlook 2016': thisdir.joinpath('ad_based_on_OPEC_World_Energy_Outlook_2016.csv'),
          'Based on The Paris Declaration as Cited in (IEA, 2017- EV Outlook)': thisdir.joinpath('ad_based_on_The_Paris_Declaration_as_Cited_in_IEA_2017_EV_Outlook.csv'),
      },
      'Ambitious Cases': {
          'Based on: IEA ETP 2016 2DS': thisdir.joinpath('ad_based_on_IEA_ETP_2016_2DS.csv'),
          'Based on Bloomberg New Energy Finance - EV Outlook 2017': thisdir.joinpath('ad_based_on_Bloomberg_New_Energy_Finance_EV_Outlook_2017.csv'),
          'Based on IEA Beyond 2DS/B2DS Scenario': thisdir.joinpath('ad_based_on_IEA_Beyond_2DSB2DS_Scenario.csv'),
      },
      'Maximum Cases': {
          'Double EV occupancy on PDS2 = double pass-km': thisdir.joinpath('ad_Double_EV_occupancy_on_PDS2_double_passkm.csv'),
          'Drawdown Projections based on adjusted IEA data (ETP 2012) on projected growth in each year, and recent sales Data (IEA - ETP 2016)': thisdir.joinpath('ad_Drawdown_Projections_based_on_adjusted_IEA_data_ETP_2012_on_proj.csv'),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources, adconfig=adconfig)

    ca_pds_data_sources = [
      {'name': 'PDS2-Based on IEA (2017) B2DS+50% Occupancy Increase', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_PDS2based_on_IEA_2017_B2DS50_Occupancy_Increase.csv'))},
      {'name': 'PDS3-Based on IEA B2DS with 100% Increase in Car Occupancy', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_PDS3based_on_IEA_B2DS_with_100_Increase_in_Car_Occupancy.csv'))},
      {'name': 'Book Ed.1 Scenario 1', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Book_Ed_1_Scenario_1.csv'))},
      {'name': 'Book Ed.1 Scenario 2', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Book_Ed_1_Scenario_2.csv'))},
      {'name': 'Book Ed.1 Scenario 3', 'include': True,
          'filename': str(thisdir.joinpath('custom_pds_ad_Book_Ed_1_Scenario_3.csv'))},
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
      [16.701444916159307, 14.405959906291683, 8.68248837596512e-05, 2.7858260096477, 8.68248837596512e-05,
       8.68248837596512e-05, 2.6861138324271523, 0.09962535233678836, 4.508096807458965, 6.7600117997589235],
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

