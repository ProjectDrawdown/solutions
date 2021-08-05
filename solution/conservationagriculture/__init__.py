"""Conservation Agriculture solution model.
   Excel filename: Drawdown_RRS-BIOSEQAgri_Model_v1.1b_Conservation_Agriculture_28Feb2020.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import aez
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import dd
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import scenario
from model import unitadoption
from model import vma
from model import tla
from model import conversions

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = {
    'Current Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
        use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'CONVENTIONAL Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'Yield from CONVENTIONAL Practice': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_from_CONVENTIONAL_Practice.csv"),
        use_weight=True),
    'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_Gain_Increase_from_CONVENTIONAL_to_SOLUTION.csv"),
        use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    't CO2-eq (Aggregate emissions) Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_CO2_eq_Aggregate_emissions_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    't CO2 Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't N2O-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't CH4-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2 Emissions per  Implementation Unit - SOLUTION': vma.VMA(
        filename=None, use_weight=False),
    'Sequestration Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
        use_weight=False),
    'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing': vma.VMA(
        filename=None, use_weight=False),
    'Disturbance Rate': vma.VMA(
        filename=None, use_weight=False),
    'Dataset to Use for Projecting Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Dataset_to_Use_for_Projecting_Adoption.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Conservation Agriculture'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)


class Scenario(scenario.Scenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    def __init__(self, scenario=None):
        if scenario is None:
            scenario = list(scenarios.keys())[0]
        self.scenario = scenario
        self.ac = scenarios[scenario]

        # TLA
        self.ae = aez.AEZ(solution_name=self.name, cohort=2020,
                regimes=dd.THERMAL_MOISTURE_REGIMES8)
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

        adconfig_list = [
            ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
             'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['trend', self.ac.soln_pds_adoption_prognostication_trend, 'Medium',
             'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
             'Medium', 'Medium', 'Medium'],
            ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'NOTE',
             'NOTE', 'NOTE', 'NOTE', 'NOTE', 'NOTE',
             'NOTE', 'NOTE', 'NOTE'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
            'Raw Data for ALL LAND TYPES': {
                'FAOSTAT (Sum of all Regions)': THISDIR.joinpath('ad', 'ad_FAOSTAT_Sum_of_all_Regions.csv'),
                'Prestele baseline and Topdown (moderate growth) projection': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_Topdown_moderate_growth_projection.csv'),
                'Prestele baseline and BottoUp: (maximum)': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_BottoUp_maximum.csv'),
            },
            'Region: OECD90': {
                'Raw Data for ALL LAND TYPES': {
                  'FAOSTAT': THISDIR.joinpath('ad', 'ad_FAOSTAT.csv'),
                  'Prestele baseline and Topdown (moderate growth) projection': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_Topdown_moderate_growth_projection.csv'),
                  'Prestele baseline and BottoUp: (maximum)': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_BottoUp_maximum.csv'),
              },
            },
            'Region: Eastern Europe': {
                'Raw Data for ALL LAND TYPES': {
                  'FAOSTAT': THISDIR.joinpath('ad', 'ad_FAOSTAT.csv'),
                  'Prestele baseline and Topdown (moderate growth) projection': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_Topdown_moderate_growth_projection.csv'),
                  'Prestele baseline and BottoUp: (maximum)': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_BottoUp_maximum.csv'),
              },
            },
            'Region: Asia (Sans Japan)': {
                'Raw Data for ALL LAND TYPES': {
                  'FAOSTAT': THISDIR.joinpath('ad', 'ad_FAOSTAT.csv'),
                  'Prestele baseline and Topdown (moderate growth) projection': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_Topdown_moderate_growth_projection.csv'),
                  'Prestele baseline and BottoUp: (maximum)': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_BottoUp_maximum.csv'),
              },
            },
            'Region: Middle East and Africa': {
                'Raw Data for ALL LAND TYPES': {
                  'FAOSTAT': THISDIR.joinpath('ad', 'ad_FAOSTAT.csv'),
                  'Prestele baseline and Topdown (moderate growth) projection': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_Topdown_moderate_growth_projection.csv'),
                  'Prestele baseline and BottoUp: (maximum)': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_BottoUp_maximum.csv'),
              },
            },
            'Region: Latin America': {
                'Raw Data for ALL LAND TYPES': {
                  'FAOSTAT': THISDIR.joinpath('ad', 'ad_FAOSTAT.csv'),
                  'Prestele baseline and Topdown (moderate growth) projection': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_Topdown_moderate_growth_projection.csv'),
                  'Prestele baseline and BottoUp: (maximum)': THISDIR.joinpath('ad', 'ad_Prestele_baseline_and_BottoUp_maximum.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_2050 = self.tla_per_region.loc[2050]
        ad_2018 = pd.Series(self.ac.ref_base_adoption)

        # % smallholder area, based on updates to smallholder area VMA sheet
        # (34.1% was estimated in Book Ed1)
        smallholder_land = 0.315909724971454
        large_farm_land = 1.0 - smallholder_land
        max_cons_ag_large_farm_tla = self.tla_per_region.loc[2050] * large_farm_land
        max_cons_ag_large_farm_tla[dd.SPECIAL_COUNTRIES] = 0.0
        ad_2080 = 1.5 * pd.Series(self.ac.ref_base_adoption)

        # Maximum technical potential adoption area available for CA out of the 685 Mha based
        # on percentage in Prestele et al 2018 (81.4%, bottom up, likely maximum future area)
        # Values used in 2017 Project Drawdown book publication.
        prestele_pct_book = pd.Series([0., 0.3952, 0.1662, 0.1632, 0.1422, 0.7332, 0., 0., 0., 0.],
                index=dd.REGIONS)
        prestele_mult = 0.814
        prestele_ad_book = self.tla_per_region.loc[2050] * prestele_mult * prestele_pct_book

        # Data Source 1
        # Source: Refer sheet "PD regional CA annual adoption"
        if 'BookVersion' in self.ac.name:
            pct = pd.Series([0., 0.3952, 0.1662, 0.1632, 0.1422, 0.7332, 0., 0., 0., 0.],
                    index=dd.REGIONS)
        else:
            pct = pd.Series([0., 0.465683756524670, 0.169344179047277, 0.194261406995049,
                    0.141859451675443, 0.712235299292505, 0., 0., 0., 0.], index=dd.REGIONS)
        ds1_poss_adopt_2050 = max_cons_ag_large_farm_tla * pct
        ds1_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds1_datapoints.loc[2018] = ad_2018
        ds1_datapoints.loc[2030] = (1.0 * ds1_poss_adopt_2050)
        ds1_datapoints.loc[2050] = (1.0 * ds1_poss_adopt_2050)
        ds1_datapoints.loc[2080] = ad_2080
        ds1_datapoints['World'] = 0.0
        ds1_datapoints['World'] = ds1_datapoints.sum(axis=1)

        # Data Source 2
        # Source: Refer sheet "PD regional CA annual adoption"
        if 'BookVersion' in self.ac.name:
            pct = pd.Series([0., 0.7208, 0.4918, 0.4888, 0.4678, 1.0, 0., 0., 0., 0.],
                    index=dd.REGIONS)
        else:
            pct = pd.Series([0., 0.791283756524669, 0.494944179047277, 0.519861406995050,
                    0.467459451675442, 1.037835299292510, 0., 0., 0., 0.], index=dd.REGIONS)
        ds2_poss_adopt_2050 = max_cons_ag_large_farm_tla * pct
        ds2_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds2_datapoints.loc[2018] = ad_2018
        ds2_datapoints.loc[2030] = (1.0 * ds2_poss_adopt_2050)
        ds2_datapoints.loc[2050] = (1.0 * ds2_poss_adopt_2050)
        ds2_datapoints.loc[2080] = ad_2080
        ds2_datapoints['World'] = 0.0
        ds2_datapoints['World'] = ds2_datapoints.sum(axis=1)

        # Data Source 3
        # Source: Refer sheet "PD regional CA annual adoption"
        ds3_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds3_datapoints.loc[2018] = ad_2018
        ds3_datapoints.loc[2030] = (0.8 * max_cons_ag_large_farm_tla)
        ds3_datapoints.loc[2050] = (1.0 * max_cons_ag_large_farm_tla)
        ds3_datapoints.loc[2080] = ad_2080
        ds3_datapoints['World'] = 0.0
        ds3_datapoints['World'] = ds3_datapoints.sum(axis=1)

        # Data Source 4
        # Source: Refer sheet "PD regional CA annual adoption"
        ds4_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds4_datapoints.loc[2018] = ad_2018
        ds4_datapoints.loc[2030] = (0.8 * ds2_poss_adopt_2050)
        ds4_datapoints.loc[2050] = (0.6 * ds2_poss_adopt_2050)
        ds4_datapoints.loc[2080] = ad_2080
        ds4_datapoints['World'] = 0.0
        ds4_datapoints['World'] = ds4_datapoints.sum(axis=1)

        # Data Source 5
        # Source: Refer sheet "PD regional CA annual adoption"
        ds5_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds5_datapoints.loc[2018] = ad_2018
        ds5_datapoints.loc[2030] = (0.8 * ds1_poss_adopt_2050)
        ds5_datapoints.loc[2050] = (0.6 * ds1_poss_adopt_2050)
        ds5_datapoints.loc[2080] = ad_2080
        ds5_datapoints['World'] = 0.0
        ds5_datapoints['World'] = ds5_datapoints.sum(axis=1)

        # Data Source 6
        # Source: see PresteleAdoptionCalc sheet
        if 'BookVersion' in self.ac.name:
            ds6_prestele_poss_adopt_2050 = prestele_ad_book
        else:
            pct = pd.Series([0., 0.740285597497468, 0.61878404520945, 0.581170964964222,
                    0.0900760503108076, 0.803736844958406, 0., 0., 0., 0.], index=dd.REGIONS)
            ds6_prestele_poss_adopt_2050 = self.tla_per_region.loc[2050] * prestele_mult * pct
        ds6_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds6_datapoints.loc[2018] = ad_2018
        ds6_datapoints.loc[2030] = (0.8 * ds6_prestele_poss_adopt_2050)
        ds6_datapoints.loc[2050] = (0.6 * ds6_prestele_poss_adopt_2050)
        ds6_datapoints.loc[2080] = ad_2080
        ds6_datapoints['World'] = 0.0
        ds6_datapoints['World'] = ds6_datapoints.sum(axis=1)

        # Data Source 7
        # Source: see PresteleAdoptionCalc sheet
        if 'BookVersion' in self.ac.name:
            ds7_prestele_poss_adopt_2050 = prestele_ad_book
        else:
            pct = pd.Series([0., 1.0, 1.0, 1.0, 0.320741884451365, 1.0, 0., 0., 0., 0.],
                    index=dd.REGIONS)
            ds7_prestele_poss_adopt_2050 = self.tla_per_region.loc[2050] * prestele_mult * pct
        ds7_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds7_datapoints.loc[2018] = ad_2018
        ds7_datapoints.loc[2030] = (0.8 * ds7_prestele_poss_adopt_2050)
        ds7_datapoints.loc[2050] = (0.6 * ds7_prestele_poss_adopt_2050)
        ds7_datapoints.loc[2080] = ad_2080
        ds7_datapoints['World'] = 0.0
        ds7_datapoints['World'] = ds7_datapoints.sum(axis=1)

        # Data Source 8
        # Source: see PresteleAdoptionCalc sheet
        if 'BookVersion' in self.ac.name:
            ds8_prestele_poss_adopt_2050 = prestele_ad_book
        else:
            pct = pd.Series([0., 0.46568375652467, 0.169344179047277, 0.194261406995049,
                    0.141859451675443, 0.712235299292505, 0., 0., 0., 0.], index=dd.REGIONS)
            ds8_prestele_poss_adopt_2050 = self.tla_per_region.loc[2050] * prestele_mult * pct
        ds8_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds8_datapoints.loc[2018] = ad_2018
        ds8_datapoints.loc[2050] = (1.0 * ds8_prestele_poss_adopt_2050)
        ds8_datapoints['World'] = 0.0
        ds8_datapoints['World'] = ds8_datapoints.sum(axis=1)

        ca_pds_data_sources = [
            {'name': 'Low,High Early Adoption, Polynomial Trend', 'include': False,
                'description': (
                    'An annual growth rate of 0.36% was used to forecast regional adoption. '
                    'Regional adoption of CA in the year 2050 was calculated and their '
                    'percentage to the total arable land area was estimated, and are used as '
                    'assumptions 1-5, below. It is also assumed that 100% of the projected '
                    'adoption will be achieved by 2030. As, it is a bridge solution to RA, the '
                    'area under CA will decline post 2030 and will remains to only 80% of the '
                    'estimated adoption by 2050. '
                    ),
                'datapoints': ds1_datapoints, 'datapoints_degree': 3},
            {'name': 'High,High Early Adoption, Polynomial Trend', 'include': False,
                'description': (
                    'Adoption of CA was reported maximum in Brazil, across the globe. Thus, its '
                    'annual growth rate of 1.24% was used to forecast regional adoption. '
                    'Regional adoption of CA in the year 2050 was calculated and their '
                    'percentage to the total arable land area was estimated, and are used as '
                    'assumptions 1-5, below. It is also assumed that 100% of the projected '
                    'adoption will be achieved by 2030. As, it is a bridge solution to RA, the '
                    'area under CA will decline post 2030 and will remains to only 80% of the '
                    'estimated adoption by 2050. '
                    ),
                'datapoints': ds2_datapoints, 'datapoints_degree': 3},
            {'name': 'Max, Polynomial Trend', 'include': False,
                'description': (
                    'A 100% regional adoption was assumed in this scenario. '
                    ),
                'datapoints': ds3_datapoints, 'datapoints_degree': 3},
            {'name': 'High, Early Adoption, Polynomial Trend', 'include': False,
                'description': (
                    'Adoption of CA was reported maximum in Brazil, across the globe. Thus, its '
                    'annual growth rate of 1.24% was used to forecast regional adoption. '
                    'Regional adoption of CA in the year 2050 was calculated and their '
                    'percentage to the total arable land area was estimated, and are used as '
                    'assumptions 1-5, below. It is also assumed that 80% of the projected '
                    'adoption will be achieved by 2030. As, it is a bridge solution to RA, the '
                    'area under CA will decline post 2030 and will remains to only 60% of the '
                    'estimated adoption by 2050. '
                    ),
                'datapoints': ds4_datapoints, 'datapoints_degree': 3},
            {'name': 'Low, Early Adoption, Polynomial Trend', 'include': False,
                'description': (
                    'An annual growth rate of 0.36% was used to forecast regional adoption. '
                    'Regional adoption of CA in the year 2050 was calculated and their '
                    'percentage to the total arable land area was estimated, and are used as '
                    'assumptions 1-5, below. It is also assumed that 80% of the projected '
                    'adoption will be achieved by 2030. As, it is a bridge solution to RA, the '
                    'area under CA will decline post 2030 and will remains to only 60% of the '
                    'estimated adoption by 2050. '
                    ),
                'datapoints': ds5_datapoints, 'datapoints_degree': 3},
            {'name': 'Moderate CA Adoption rates based on Prestele Topdown map, polynomial', 'include': False,
                'description': (
                    'Regional adoption of CA in the year 2050 was calculated and their '
                    'percentage to the total arable land area was estimated, and are used as '
                    'assumptions 1-5, below. It is also assumed that 80% of the projected '
                    'adoption will be achieved by 2030. It is a bridge solution to RA so the '
                    'area under CA will decline post 2030 and will remain to only 60% of the '
                    'estimated adoption by 2050. SEI added current and projected adoption and '
                    'max potential adoption (assumption 10)  based on Prestele et al 2018. after '
                    'applying Prestele regional percent adoption by TopDown projection '
                    '(intermediate adoption rate to 2050), to country -level data available in '
                    'their supplementary materials, then summing by PDrawdown regions (which '
                    'differ from Prestele regions). The % of regional Drawdown TLA projected by '
                    '2050 using Prestele projections (not mean of data) was calculated and used '
                    'in Revised growth assumptions 1-5. '
                    ),
                'datapoints': ds6_datapoints, 'datapoints_degree': 3},
            {'name': 'Likely max CA based on Prestele BottomUp Map, polynominal', 'include': False,
                'description': (
                    'Regional adoption of CA in the year 2050 was calculated and their '
                    'percentage to the total arable land area was estimated, and are used as '
                    'assumptions 1-5, below. It is also assumed that 80% of the projected '
                    'adoption will be achieved by 2030. It is a bridge solution to RA so the '
                    'area under CA will decline post 2030 and will remain to only 60% of the '
                    'estimated adoption by 2050. SEI added current and projected adoption and '
                    'max potential adoption (assumption 10)  based on Prestele et al 2018. after '
                    'applying Prestele regional percent adoption by BOTTOM UP projection (forced '
                    'to 2050), to country -level data available in their supplementary '
                    'materials, then summing by PDrawdown regions (which differ from Prestele '
                    'regions). The % of regional Drawdown TLA projected by 2050 using Prestele '
                    'projections (not mean of data) was calculated OR if the bottom up '
                    'projection result in extent larger than Drawdown regional TLA, then 100% '
                    'was used in Revised growth assumptions 1-5. '
                    ),
                'datapoints': ds7_datapoints, 'datapoints_degree': 3},
            {'name': 'Baseline scenario', 'include': True,
                'description': (
                    'tis is the average of scenarios 1-7 '
                    ),
                'datapoints': ds8_datapoints, 'maximum': max_cons_ag_large_farm_tla['World']},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014] = [108.926170040128000, 43.700575542980000, 9.040960261572450,
                    8.934730992728910, 1.113417893008100, 46.136485349838400, 0.0, 0.0, 0.0, 0.0]
            df.loc[2015] = [118.522634649202000, 47.190416175021700, 10.277201842542000,
                    10.390765035686000, 1.355692262948170, 49.308559333003700, 0.0, 0.0, 0.0, 0.0]
            df.loc[2016] = [128.231557482326000, 50.685767480789800, 11.580017143547000,
                    11.936077959964700, 1.613327416836600, 52.416367481188000, 0.0, 0.0, 0.0, 0.0]
            df.loc[2017] = [138.054065103220000, 54.187020002847500, 12.949707603363100,
                    13.570892429945200, 1.886419963055470, 55.460025104009000, 0.0, 0.0, 0.0, 0.0]
            df.loc[2018] = [147.991284075603000, 57.694564283758300, 14.386574660765900,
                    15.295431110007600, 2.175066509986860, 58.439647511084400, 0.0, 0.0, 0.0, 0.0]

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': '[Type Scenario 1 Name Here (REF CASE)...]', 'include': True,
                'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Type_Scenario_1_Name_Here_REF_CASE_.csv')},
        ]
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        if self.ac.soln_ref_adoption_basis == 'Custom':
            ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()
        else:
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
            list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial /
            self.tla_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2018] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            use_first_pds_datapoint_main=False,
            adoption_base_year=2018,
            copy_pds_to_ref=False, copy_ref_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=self.tla_per_region,
            pds_total_adoption_units=self.tla_per_region,
            electricity_unit_factor=1000000.0,
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
            conv_ref_first_cost_uses_tot_units=True,
            fc_convert_iunit_factor=conversions.mha_to_ha)

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
            conversion_factor=conversions.mha_to_ha)

        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
            soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
            soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),
            soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),
            soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
            conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)

