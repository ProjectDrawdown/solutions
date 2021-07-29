"""Nuclear solution model.
   Excel filename: Nuclear_RRS_ELECGEN_v1.1b_18Jan2020.xlsm
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
from model import conversions
from solution import rrs

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = {
    'Current Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
        use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
        use_weight=True),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
        use_weight=True),
    'SOLUTION Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
        use_weight=False),
    'CONVENTIONAL Average Annual Use': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
        use_weight=True),
    'SOLUTION Average Annual Use': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
        use_weight=False),
    'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=True),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Fixed_Operating_Cost_FOM.csv"),
        use_weight=True),
    'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Fixed_Operating_Cost_FOM.csv"),
        use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'Total Energy Used per SOLUTION functional unit': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Consumed per CONVENTIONAL Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    '2005-2014 Average CONVENTIONAL Fuel Price per functional unit': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "2005_2014_Average_CONVENTIONAL_Fuel_Price_per_functional_unit.csv"),
        use_weight=True),
    'Weighted Average CONVENTIONAL Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "Weighted_Average_CONVENTIONAL_Plant_Efficiency.csv"),
        use_weight=True),
    'Coal Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath(*('energy', 'vma_Coal_Plant_Efficiency_2.csv')),
        use_weight=False),
    'Natural Gas Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "Natural_Gas_Plant_Efficiency.csv"),
        use_weight=False),
    'Oil Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath(*('energy', 'vma_Oil_Plant_Efficiency_2.csv')),
        use_weight=False),
    'Fuel price (Uranium)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Fuel_price_Uranium.csv"),
        use_weight=False),
    'Discount Rate: Commercial / Industry': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "Discount_Rate_Commercial_Industry.csv"),
        use_weight=False),
    'Learning Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Learning_Rate.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "TW",
    "functional unit": "TWh",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Nuclear'
solution_category = ac.SOLUTION_CATEGORY.REPLACEMENT

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
                '3rd Poly', '3rd Poly', '3rd Poly'],
            ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
                'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.energy_tam_2_ref_data_sources,
            tam_pds_data_sources=rrs.energy_tam_2_pds_data_sources)
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
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
            'Baseline Cases': {
                'Based on BP Energy Outlook 2019 (Evolving transition Scenario)': THISDIR.joinpath('ad', 'ad_based_on_BP_Energy_Outlook_2019_Evolving_transition_Scenario.csv'),
                'Based on IEEJ Outlook - 2019, Ref Scenario': THISDIR.joinpath('ad', 'ad_based_on_IEEJ_Outlook_2019_Ref_Scenario.csv'),
                'Based on IEA, WEO-2018, Current Policies Scenario (CPS)': THISDIR.joinpath('ad', 'ad_based_on_IEA_WEO2018_Current_Policies_Scenario_CPS.csv'),
                'Based on: IEA ETP 2017 Ref Tech': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2017_Ref_Tech.csv'),
            },
            'Conservative Cases': {
                'Based on Equinor (2018), Reform Scenario': THISDIR.joinpath('ad', 'ad_based_on_Equinor_2018_Reform_Scenario.csv'),
                'Based on IEA, WEO-2018, New Policies Scenario (NPS)': THISDIR.joinpath('ad', 'ad_based_on_IEA_WEO2018_New_Policies_Scenario_NPS.csv'),
            },
            'Ambitious Cases': {
                'Based on Equinor (2018), Renewal Scenario': THISDIR.joinpath('ad', 'ad_based_on_Equinor_2018_Renewal_Scenario.csv'),
                'Based on IEEJ Outlook - 2019, Advanced Tech Scenario': THISDIR.joinpath('ad', 'ad_based_on_IEEJ_Outlook_2019_Advanced_Tech_Scenario.csv'),
                'Based on: Grantham Institute and Carbon Tracker (2017), Strong Scenario, Original, Medium': THISDIR.joinpath('ad', 'ad_based_on_Grantham_Institute_and_Carbon_Tracker_2017_Strong_Scenario_Original_Medium.csv'),
                'Based on IEA, WEO-2018, SDS Scenario': THISDIR.joinpath('ad', 'ad_based_on_IEA_WEO2018_SDS_Scenario.csv'),
                'Based on: IEA ETP 2017 B2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2017_B2DS.csv'),
                'Based on: IEA ETP 2017 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2017_2DS.csv'),
            },
            '100% RES2050 Case': {
                'Based on average of: LUT/EWG 2019 100% RES, Ecofys 2018 1.5C and Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_average_of_LUTEWG_2019_100_RES_Ecofys_2018_1_5C_and_Greenpeace_2015_Advanced_Revolution.csv'),
            },
            'Region: OECD90': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 GEM E3 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 GEM E3 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: Eastern Europe': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 GEM E3 Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 GEM E3 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 GEM E3 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: Asia (Sans Japan)': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: Middle East and Africa': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: Latin America': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: China': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 GEM E3 Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 GEM E3 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 GEM E3 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: India': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 GEM E3 Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 GEM E3 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 GEM E3 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: EU': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 GEM E3 Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 GEM E3 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 GEM E3 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
            'Region: USA': {
                'Baseline Cases': {
                  'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
                  'Based on: AMPERE 2014 GEM E3 Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
              },
                'Conservative Cases': {
                  'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                  'Based on: AMPERE 2014 GEM E3 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
              },
                'Ambitious Cases': {
                  'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                  'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                  'Based on: AMPERE 2014 GEM E3 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
                  'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'Project Drawdown High Growth, Ambitious Cases, adjusted', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Project_Drawdown_High_Growth_Ambitious_Cases_adjusted.csv')},
            {'name': 'Project Drawdown High Growth, Conservative Cases, adjusted, smoothed curve', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Project_Drawdown_High_Growth_Conservative_Cases_adjusted_smoothed_curve.csv')},
            {'name': 'Optimum Nuclear reduces to 0% of TAM by 2050, based on AMPERE RefPol Scenario (2014) till peaking', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Optimum_Nuclear_reduces_to_0_of_TAM_by_2050_based_on_AMPERE_RefPol_Scenario_2014_till_peaking.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': 'Custom REF Adoption mirroring decline in nuclear in Plausible SCenario', 'include': False,
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Custom_REF_Adoption_mirroring_decline_in_nuclear_in_Plausible_SCenario.csv')},
        ]
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=ref_tam_per_region)

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

        ht_ref_adoption_initial = pd.Series(list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
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
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            use_first_pds_datapoint_main=False,
            adoption_base_year=2018,
            copy_pds_to_ref=True,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=2)

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
            fc_convert_iunit_factor=conversions.terawatt_to_kilowatt())

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
            conversion_factor=conversions.terawatt_to_kilowatt())

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

