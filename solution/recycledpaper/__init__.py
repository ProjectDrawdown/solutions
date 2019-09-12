"""Recycled Paper solution model.
   Excel filename: Drawdown-Recycled Paper_RRS_v1.1_17Nov2018_PUBLIC.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import dd
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import unitadoption
from model import vma
from model import tam
from solution import rrs

DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = vma.generate_vma_dict(THISDIR.joinpath('vma_data'))

units = {
  "implementation unit": "Million Metric Tonnes of Recycled Paper Produced",
  "functional unit": "Million Metric Tonnes of Paper Produced",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Recycled Paper'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)


class Scenario:
  name = name
  units = units
  vmas = VMAs
  solution_category = solution_category

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = list(scenarios.keys())[0]
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
       '3rd Poly', '3rd Poly', '2nd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    tam_ref_data_sources = {
      'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__651dff99.csv'),
          'See sheet FAO 2009, annual growth rates in Drawdown regions (2015-2020, 2020-2030 and 2030-2045) from RISI': THISDIR.joinpath('tam', 'tam_See_sheet_FAO_2009_annual_growth_rates_in_Drawdown_regions_20152020_20202030_and_2030204_01422925.csv'),
      },
      'Ambitious Cases': {
          'See McKinnsey & Co 2013 sheet (annual growth after 2030 2,7%': THISDIR.joinpath('tam', 'tam_See_McKinnsey_Co_2013_sheet_annual_growth_after_2030_27.csv'),
      },
      'Maximum Cases': {
          'See McKinnsey & Co 2013 sheet (annual growth after 2030 2,2%': THISDIR.joinpath('tam', 'tam_See_McKinnsey_Co_2013_sheet_annual_growth_after_2030_22.csv'),
      },
      'Region: OECD90': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__651dff99.csv'),
          'See sheet FAO 2009': THISDIR.joinpath('tam', 'tam_See_sheet_FAO_2009.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__651dff99.csv'),
          'See sheet FAO 2009': THISDIR.joinpath('tam', 'tam_See_sheet_FAO_2009.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__651dff99.csv'),
          'See sheet FAO 2009': THISDIR.joinpath('tam', 'tam_See_sheet_FAO_2009.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__651dff99.csv'),
          'See sheet FAO 2009': THISDIR.joinpath('tam', 'tam_See_sheet_FAO_2009.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__651dff99.csv'),
          'See sheet FAO 2009': THISDIR.joinpath('tam', 'tam_See_sheet_FAO_2009.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions and countries (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__f4ea722f.csv'),
        },
        'Ambitious Cases': {
          'See sheet PÖYRY 2013. Linear interpolation 2011-2025 is used. After 2025 annual growth rate of 3,6% is used according to FAO 2009 Asia and the Pacific region annual growth rate 2020-2030.': THISDIR.joinpath('tam', 'tam_See_sheet_PÖYRY_2013__Linear_interpolation_20112025_is_used__After_2025_annual_growth_ra_5f611a03.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions and countries (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__f4ea722f.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions and countries (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__f4ea722f.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          '[FAO Stat 2014] Original data from webpage FAO Stat 2014. See RIGI data on the same sheet for annual growth rates in Drawdown regions and countries (2015-2020, 2020-2030 and 2030-2045).': THISDIR.joinpath('tam', 'tam_FAO_Stat_2014_Original_data_from_webpage_FAO_Stat_2014__See_RIGI_data_on_the_same_sheet__f4ea722f.csv'),
          'See sheet FAO 2015-2020, prognostication based on RIGI -0.9% annum growth': THISDIR.joinpath('tam', 'tam_See_sheet_FAO_20152020_prognostication_based_on_RIGI_0_9_annum_growth.csv'),
        },
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      main_includes_regional=True,
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
          'See sheet FAO Stat 2014, recycling target rates specially defined for each region and country based on current recycling rate and EU target 2030 recycling rate of 70% or closest best country/region recycling rate': THISDIR.joinpath('ad', 'ad_See_sheet_FAO_Stat_2014_recycling_target_rates_specially_defined_for_each_region_and_cou_45c9627f.csv'),
      },
      'Conservative Cases': {
          'See PÖYRY 2013 sheet': THISDIR.joinpath('ad', 'ad_See_PÖYRY_2013_sheet.csv'),
          'See McKinsey and Co. 2013 (adoption doubles every 25 years), 3rd Polynomial prognostication': THISDIR.joinpath('ad', 'ad_See_McKinsey_and_Co__2013_adoption_doubles_every_25_years_3rd_Polynomial_prognostication.csv'),
      },
      'Ambitious Cases': {
          'Sheet FAO Stat 2014, ceiling 75%': THISDIR.joinpath('ad', 'ad_Sheet_FAO_Stat_2014_ceiling_75.csv'),
      },
      'Maximum Cases': {
          'Sheet FAO Stat 2014, ceiling 81%': THISDIR.joinpath('ad', 'ad_Sheet_FAO_Stat_2014_ceiling_81.csv'),
          'See McKinsey and Co. 2013 (adoption doubles every 15 years), 3rd Polynomial prognostication': THISDIR.joinpath('ad', 'ad_See_McKinsey_and_Co__2013_adoption_doubles_every_15_years_3rd_Polynomial_prognostication.csv'),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Custom Scenario No.1 - Using Medium Trend of Prognostications', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Custom_Scenario_No_1_Using_Medium_Trend_of_Prognostications.csv')},
      {'name': 'Custom Scenario No.2 - Using High Trend of Existing Prognostications', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Custom_Scenario_No_2_Using_High_Trend_of_Existing_Prognostications.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
        total_adoption_limit=pds_tam_per_region)

    ref_adoption_data_per_region = None

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

    ht_ref_adoption_initial = pd.Series(
      [207.0, 125.0, 6.3, 78.0, 2.75,
       12.21, 44.0, 3.0, 69.0, 46.5],
       index=dd.REGIONS)
    ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=pds_tam_per_region,
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

