"""Building Automation Systems solution model.
   Excel filename: Drawdown-Building Automation Systems_RRS_v1.1_18Nov2018_PUBLIC.xlsm
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
  'PDS1-51p2050-SCurve (Book Ed.1)': advanced_controls.AdvancedControls(
      # This scenario sums the adoption of individual regions (each of which has its own
      # logistic S-Curve for adoption), which rise from current adoption to some
      # realistic adoption in 2050 that differs by region. The scenario uses inputs
      # calculated for the Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=True, soln_pds_adoption_regional_data=True, 
      soln_pds_adoption_basis='Logistic S-Curve', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.95), ('OECD90', 0.999999999999999), ('Eastern Europe', 0.21270960344383177), ('Asia (Sans Japan)', 0.44770734907359283), ('Middle East and Africa', 0.08508384137753272), ('Latin America', 0.22385367453679642), ('China', 0.0), ('India', 0.0), ('EU', 0.999999999999999), ('USA', 0.999999999999999)], 

      # financial
      pds_2014_cost=6.93288626734667, ref_2014_cost=6.93288626734667, 
      conv_2014_cost=4.442162256132418, 
      soln_first_cost_efficiency_rate=0.1, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=15.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=25.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=21813111.35030163, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=24993401.868879557, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.1148, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.20269079954094618, 
      conv_fuel_consumed_per_funit=275.87, soln_fuel_efficiency_factor=0.2009, 
      conv_fuel_emissions_factor=61.0, soln_fuel_emissions_factor=61.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS2-70p2050-Linear (Book Ed.1)': advanced_controls.AdvancedControls(
      # This scenario sums the adoption of individual regions (each of which has its own
      # linear adoption), which rise from current adoption to some ambitious adoption in
      # 2050. The scenario uses inputs calculated for the Drawdown book edition 1, some
      # of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=True, soln_pds_adoption_regional_data=True, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.95), ('OECD90', 0.999999999999999), ('Eastern Europe', 0.5), ('Asia (Sans Japan)', 0.8), ('Middle East and Africa', 0.5), ('Latin America', 0.5), ('China', 0.0), ('India', 0.0), ('EU', 0.999999999999999), ('USA', 0.999999999999999)], 

      # financial
      pds_2014_cost=6.93288626734667, ref_2014_cost=6.93288626734667, 
      conv_2014_cost=4.442162256132418, 
      soln_first_cost_efficiency_rate=0.1, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=15.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=25.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=21813111.35030163, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=24993401.868879557, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.1116, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.20269079954094618, 
      conv_fuel_consumed_per_funit=275.87, soln_fuel_efficiency_factor=0.1788, 
      conv_fuel_emissions_factor=61.0, soln_fuel_emissions_factor=61.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS3-72p2050-Linear (Book Ed.1)': advanced_controls.AdvancedControls(
      # This scenario sums the adoption of individual regions (each of which has its own
      # linear adoption), which rise from current adoption to some very ambitious
      # adoption in 2050. The scenario uses inputs calculated for the Drawdown book
      # edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=True, soln_pds_adoption_regional_data=True, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.95), ('OECD90', 0.999999999999999), ('Eastern Europe', 0.8), ('Asia (Sans Japan)', 0.8), ('Middle East and Africa', 0.8), ('Latin America', 0.8), ('China', 0.0), ('India', 0.0), ('EU', 0.999999999999999), ('USA', 0.999999999999999)], 

      # financial
      pds_2014_cost=6.93288626734667, ref_2014_cost=6.93288626734667, 
      conv_2014_cost=4.442162256132418, 
      soln_first_cost_efficiency_rate=0.1, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=15.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=25.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=21942511.65564535, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=24993401.868879557, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.1091, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.20269079954094618, 
      conv_fuel_consumed_per_funit=275.87, soln_fuel_efficiency_factor=0.1648, 
      conv_fuel_emissions_factor=61.0, soln_fuel_emissions_factor=61.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
}

class BuildingAutomationSystems:
  name = 'Building Automation Systems'
  units = {
    "implementation unit": "Mm²",
    "functional unit": "Mm²",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS1-51p2050-SCurve (Book Ed.1)'
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
       'Medium', 'Medium', 'Medium', 'High', 'High', 'High', 'High'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    tam_ref_data_sources = {
      'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
          'Ürge-Vorsatz et al. (2015) – see TAM Factoring': thisdir.joinpath('tam_ÜrgeVorsatz_et_al__2015_see_TAM_Factoring.csv'),
      },
      'Region: OECD90': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
        },
      },
      'Region: Latin America': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
        },
      },
      'Region: China': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
          'Hong et al. (2014) – see TAM Factoring': thisdir.joinpath('tam_Hong_et_al__2014_see_TAM_Factoring.csv'),
        },
      },
      'Region: India': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
          'Chaturvedi et al (2014) – see TAM Factoring': thisdir.joinpath('tam_Chaturvedi_et_al_2014_see_TAM_Factoring.csv'),
        },
      },
      'Region: EU': {
        'Ambitious Cases': {
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': thisdir.joinpath('tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
          'Boermans et al. (2012); BPIE (2014) – see TAM Factoring': thisdir.joinpath('tam_Boermans_et_al__2012_BPIE_2014_see_TAM_Factoring.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'EIA, 2016, "Annual Energy Outlook 2016" – Reference Case': thisdir.joinpath('tam_EIA_2016_Annual_Energy_Outlook_2016_Reference_Case.csv'),
          'EIA, 2016, "Annual Energy Outlook 2016" – Reference Case w/o CPP': thisdir.joinpath('tam_EIA_2016_Annual_Energy_Outlook_2016_Reference_Case_wo_CPP.csv'),
        },
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

    sconfig_list = [
      ['region', 'base_year', 'last_year', 'base_percent', 'last_percent', 'base_adoption', 'pds_tam_2050'],
      ['World', 2014, 2050, 0.3469591450521351, 0.95, 16577.82591670033, 77969.42578838725],
      ['OECD90', 2014, 2050, 0.6774945040969459, 0.999999999999999, 14915.99, 30578.761254288427],
      ['Eastern Europe', 2014, 2050, 0.0, 0.21270960344383177, 0.0, 1532.2953039347105],
      ['Asia (Sans Japan)', 2014, 2050, 0.07415399905935922, 0.44770734907359283, 1087.7709445216651, 25358.333975041056],
      ['Middle East and Africa', 2014, 2050, 0.0, 0.08508384137753272, 0.0, 4140.661070930817],
      ['Latin America', 2014, 2050, 0.0, 0.22385367453679642, 0.0, 1021.9329224434589],
      ['China', 2014, 2050, 0.08478075075770555, 0.0, 1087.7709445216651, 18965.135056084015],
      ['India', 2014, 2050, 0.0, 0.0, 0.0, 8804.235498036302],
      ['EU', 2014, 2050, 0.48260313794749193, 0.999999999999999, 3622.85, 11003.357475720299],
      ['USA', 2014, 2050, 0.4456343028887654, 0.999999999999999, 11293.14, 36879.95839663896]]
    sconfig = pd.DataFrame(sconfig_list[1:], columns=sconfig_list[0], dtype=np.object).set_index('region')
    self.sc = s_curve.SCurve(transition_period=16, sconfig=sconfig)

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Logistic S-Curve':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = self.sc.logistic_adoption()
      pds_adoption_is_single_source = False
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()
    elif self.ac.soln_pds_adoption_basis == 'Linear':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = None
      pds_adoption_is_single_source = False

    ht_ref_adoption_initial = pd.Series(
      [16577.82591670033, 14915.99, 0.0, 1087.7709445216651, 0.0,
       0.0, 1087.7709445216651, 0.0, 3622.85, 11293.14],
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
        fc_convert_iunit_factor=1000000.0)

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

