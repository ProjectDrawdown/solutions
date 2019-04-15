"""High Efficient Heat Pumps solution model.
   Excel filename: Drawdown-High Efficient Heat Pumps_RRS_v1.1_19Nov2018_PUBLIC.xlsm
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
  'PDS1-25p2050-Bass Diff. (Book Ed.1)': advanced_controls.AdvancedControls(
      # Assuming that Heat Pumps replace only coal, oil, gas and electricity-based
      # conventional space heating/cooling (that is, not biomass, renewables nor
      # commercial heat), we estimate the cost and emissions for units of the current
      # average conventional size used. We model the growth by a Bass-diffusion curve
      # growing to 25% of the TAM by 2050. This scenario uses inputs calculated for the
      # Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Bass Diffusion S-Curve', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Based on: IEA ETP 2016 4DS', 
      pds_source_post_2014='Drawdown TAM: Drawdown Integrated TAM - PDS1', 
      pds_base_adoption=[('World', 2.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_s_curve_innovation=[('World', 0.00112096), ('OECD90', 0.00112096), ('Eastern Europe', 0.00112096), ('Asia (Sans Japan)', 0.00112096), ('Middle East and Africa', 0.00112096), ('Latin America', 0.00112096), ('China', 0.00112096), ('India', 0.00112096), ('EU', 0.00112096), ('USA', 0.00112096)], 
      pds_adoption_s_curve_imitation=[('World', 0.09693403461267407), ('OECD90', 0.103333441), ('Eastern Europe', 0.103333441), ('Asia (Sans Japan)', 0.103333441), ('Middle East and Africa', 0.103333441), ('Latin America', 0.103333441), ('China', 0.103333441), ('India', 0.103333441), ('EU', 0.103333441), ('USA', 0.103333441)], 

      # financial
      pds_2014_cost=8417.842235795455, ref_2014_cost=8417.842235795455, 
      conv_2014_cost=4179.335712753406, 
      soln_first_cost_efficiency_rate=0.0961, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0536818181818182, 
      soln_lifetime_capacity=4.965930424528303e-05, soln_avg_annual_use=2.452311320754717e-06, 
      conv_lifetime_capacity=4.4824973684210526e-05, conv_avg_annual_use=2.3980438596491226e-06, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0416280354784867, 
      soln_fixed_oper_cost_per_iunit=91.22464666666667, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=0.0818, 
      conv_fixed_oper_cost_per_iunit=97.73540814814815, 

      # emissions
      ch4_is_co2eq=True, n2o_is_co2eq=True, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.3295964804314072, conv_annual_energy_used=0.29063151854349806, 
      conv_fuel_consumed_per_funit=2552.969708808781, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=61.051339971807074, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS2-45p2050-Bass Diff. (Book Ed.1)': advanced_controls.AdvancedControls(
      # Assuming that Heat Pumps replace only coal, oil, gas and electricity-based
      # conventional space heating/cooling (that is, not biomass, renewables nor
      # commercial heat), we estimate the cost and emissions for units of the current
      # average conventional size used. We model the growth by a Bass-diffusion curve
      # growing to 45% of the TAM by 2050. This scenario uses inputs calculated for the
      # Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Bass Diffusion S-Curve', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Based on: IEA ETP 2016 4DS', 
      pds_source_post_2014='Drawdown TAM: Drawdown Integrated TAM - PDS2', 
      pds_base_adoption=[('World', 2.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_s_curve_innovation=[('World', 0.00112096), ('OECD90', 0.00112096), ('Eastern Europe', 0.00112096), ('Asia (Sans Japan)', 0.00112096), ('Middle East and Africa', 0.00112096), ('Latin America', 0.00112096), ('China', 0.00112096), ('India', 0.00112096), ('EU', 0.00112096), ('USA', 0.00112096)], 
      pds_adoption_s_curve_imitation=[('World', 0.13192094462919884), ('OECD90', 0.103333441), ('Eastern Europe', 0.103333441), ('Asia (Sans Japan)', 0.103333441), ('Middle East and Africa', 0.103333441), ('Latin America', 0.103333441), ('China', 0.103333441), ('India', 0.103333441), ('EU', 0.103333441), ('USA', 0.103333441)], 

      # financial
      pds_2014_cost=8417.842235795455, ref_2014_cost=8417.842235795455, 
      conv_2014_cost=4179.335712753406, 
      soln_first_cost_efficiency_rate=0.0961, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0536818181818182, 
      soln_lifetime_capacity=4.965930424528303e-05, soln_avg_annual_use=2.452311320754717e-06, 
      conv_lifetime_capacity=4.4824973684210526e-05, conv_avg_annual_use=2.3980438596491226e-06, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0416280354784867, 
      soln_fixed_oper_cost_per_iunit=91.22464666666667, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=0.0818, 
      conv_fixed_oper_cost_per_iunit=97.73540814814815, 

      # emissions
      ch4_is_co2eq=True, n2o_is_co2eq=True, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.3295964804314072, conv_annual_energy_used=0.29063151854349806, 
      conv_fuel_consumed_per_funit=2552.969708808781, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=61.051339971807074, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS3-60p2050-Bass Diff (Book Ed.1)': advanced_controls.AdvancedControls(
      # Assuming that Heat Pumps replace only coal, oil, gas and electricity-based
      # conventional space heating/cooling (that is, not biomass, renewables nor
      # commercial heat), we estimate the cost and emissions for units of the current
      # average conventional size used. We model the growth by a Bass-diffusion curve
      # growing to 60% of the TAM by 2050. This scenario uses inputs calculated for the
      # Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Bass Diffusion S-Curve', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Based on: IEA ETP 2016 4DS', 
      pds_source_post_2014='Drawdown TAM: Drawdown Integrated TAM - PDS3', 
      pds_base_adoption=[('World', 2.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_s_curve_innovation=[('World', 0.00112096), ('OECD90', 0.00112096), ('Eastern Europe', 0.00112096), ('Asia (Sans Japan)', 0.00112096), ('Middle East and Africa', 0.00112096), ('Latin America', 0.00112096), ('China', 0.00112096), ('India', 0.00112096), ('EU', 0.00112096), ('USA', 0.00112096)], 
      pds_adoption_s_curve_imitation=[('World', 0.15404782805293277), ('OECD90', 0.103333441), ('Eastern Europe', 0.103333441), ('Asia (Sans Japan)', 0.103333441), ('Middle East and Africa', 0.103333441), ('Latin America', 0.103333441), ('China', 0.103333441), ('India', 0.103333441), ('EU', 0.103333441), ('USA', 0.103333441)], 

      # financial
      pds_2014_cost=8417.842235795455, ref_2014_cost=8417.842235795455, 
      conv_2014_cost=4179.335712753406, 
      soln_first_cost_efficiency_rate=0.0961, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0536818181818182, 
      soln_lifetime_capacity=4.965930424528303e-05, soln_avg_annual_use=2.452311320754717e-06, 
      conv_lifetime_capacity=4.4824973684210526e-05, conv_avg_annual_use=2.3980438596491226e-06, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=0.0416280354784867, 
      soln_fixed_oper_cost_per_iunit=91.22464666666667, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=0.0818, 
      conv_fixed_oper_cost_per_iunit=97.73540814814815, 

      # emissions
      ch4_is_co2eq=True, n2o_is_co2eq=True, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.3295964804314072, conv_annual_energy_used=0.29063151854349806, 
      conv_fuel_consumed_per_funit=2552.969708808781, soln_fuel_efficiency_factor=1.0, 
      conv_fuel_emissions_factor=61.051339971807074, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
}

class HeatPumps:
  name = 'High Efficient Heat Pumps'
  units = {
    "implementation unit": "Installation Units",
    "functional unit": "TWh",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-25p2050-Bass Diff. (Book Ed.1)'
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
      ['trend', '2nd Poly', '2nd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    tam_ref_data_sources = {
      'Baseline Cases': {
          'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('tam_based_on_IEA_ETP_2016_6DS.csv'),
      },
      'Conservative Cases': {
          'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('tam_based_on_IEA_ETP_2016_4DS.csv'),
      },
      'Ambitious Cases': {
          'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('tam_based_on_IEA_ETP_2016_2DS.csv'),
      },
    }
    tam_pds_data_sources = {
      'Ambitious Cases': {
          'Drawdown TAM: Drawdown Integrated TAM - PDS1': THISDIR.joinpath('tam_pds_Drawdown_TAM_Drawdown_Integrated_TAM_PDS1.csv'),
          'Drawdown TAM: Drawdown Integrated TAM - PDS2': THISDIR.joinpath('tam_pds_Drawdown_TAM_Drawdown_Integrated_TAM_PDS2.csv'),
      },
      'Maximum Cases': {
          'Drawdown TAM: Drawdown Integrated TAM - PDS3': THISDIR.joinpath('tam_pds_Drawdown_TAM_Drawdown_Integrated_TAM_PDS3.csv'),
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      tam_pds_data_sources=tam_pds_data_sources)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    adconfig_list = [
      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['trend', self.ac.soln_pds_adoption_prognostication_trend, '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'Medium',
       'Medium', 'Low', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0], dtype=np.object).set_index('param')
    ad_data_sources = {
      'Baseline Cases': {
          'No Standards Case (David Siap, 2016, based on US Federal Rulemakings, 2016)': THISDIR.joinpath('ad_No_Standards_Case_David_Siap_2016_based_on_US_Federal_Rulemakinf773431f.csv'),
      },
      'Conservative Cases': {
          'Standards Case (David Siap, 2016, based on US Federal Rulemakings, 2016)': THISDIR.joinpath('ad_Standards_Case_David_Siap_2016_based_on_US_Federal_Rulemakings_3ae88b3a.csv'),
      },
      'Ambitious Cases': {
          'Aggressive Standards Case (David Siap, 2016, based on US Federal Rulemakings, 2016)': THISDIR.joinpath('ad_Aggressive_Standards_Case_David_Siap_2016_based_on_US_Federal_R8b178f0d.csv'),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    sconfig_list = [['region', 'base_year', 'last_year'],
      ['World', 2014, 2050],
      ['OECD90', 2014, 2050],
      ['Eastern Europe', 2014, 2050],
      ['Asia (Sans Japan)', 2014, 2050],
      ['Middle East and Africa', 2014, 2050],
      ['Latin America', 2014, 2050],
      ['China', 2014, 2050],
      ['India', 2014, 2050],
      ['EU', 2014, 2050],
      ['USA', 2014, 2050]]
    sconfig = pd.DataFrame(sconfig_list[1:], columns=sconfig_list[0], dtype=np.object).set_index('region')
    sconfig['pds_tam_2050'] = pds_tam_per_region.loc[[2050]].T
    sc_regions, sc_percentages = zip(*self.ac.pds_base_adoption)
    sconfig['base_adoption'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    sconfig['base_percent'] = sconfig['base_adoption'] / pds_tam_per_region.loc[2014]
    sc_regions, sc_percentages = zip(*self.ac.pds_adoption_final_percentage)
    sconfig['last_percent'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    if self.ac.pds_adoption_s_curve_innovation is not None:
      sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_innovation)
      sconfig['innovation'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    if self.ac.pds_adoption_s_curve_imitation is not None:
      sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_imitation)
      sconfig['imitation'] = pd.Series(list(sc_percentages), index=list(sc_regions))
    self.sc = s_curve.SCurve(transition_period=16, sconfig=sconfig)

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Logistic S-Curve':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = self.sc.logistic_adoption()
      pds_adoption_is_single_source = None
    elif self.ac.soln_pds_adoption_basis == 'Bass Diffusion S-Curve':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = self.sc.bass_diffusion_adoption()
      pds_adoption_is_single_source = None
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()

    ht_ref_adoption_initial = pd.Series(
      [2.0, 0.0, 0.0, 0.0, 0.0,
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
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
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
        conversion_factor=(1.0, 1000000000.0))

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

