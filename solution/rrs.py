"""Features shared by most or all of the
   Reduction and Replacement Solution (RRS) implementations.
"""

import pathlib
import pandas as pd
from model import vma


TERAWATT_TO_KILOWATT = 10**9

thisdir = pathlib.Path(__file__).parents[0]
parentdir = pathlib.Path(__file__).parents[1]
energy_tam_1_ref_data_sources = {
    'Baseline Cases': {
      'Based on: IEA ETP 2016 6DS': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv')),
      'Based on: AMPERE 2014 MESSAGE MACRO Reference': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv')),
      'Based on: AMPERE 2014 GEM E3 Reference': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv')),
      'Based on: AMPERE 2014 IMAGE TIMER Reference': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv')),
      },
    'Conservative Cases': {
      'Based on: IEA ETP 2016 4DS': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv')),
      'Based on: AMPERE 2014 MESSAGE MACRO 550': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv')),
      'Based on: AMPERE 2014 GEM E3 550': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv')),
      'Based on: AMPERE 2014 IMAGE TIMER 550': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv')),
      'Based on: Greenpeace 2015 Reference': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv')),
      },
    'Ambitious Cases': {
      'Based on: IEA ETP 2016 2DS': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv')),
      'Based on: AMPERE 2014 MESSAGE MACRO 450': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv')),
      'Based on: AMPERE 2014 GEM E3 450': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv')),
      'Based on: AMPERE 2014 IMAGE TIMER 450': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv')),
      'Based on: Greenpeace 2015 Energy Revolution': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv')),
      },
    '100% RES2050 Case': {
      'Based on: Greenpeace 2015 Advanced Revolution': str(parentdir.joinpath(
        'data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv')),
      },
}
energy_tam_1_pds_data_sources = {
    'Ambitious Cases': {
      'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_plausible_scenario_1.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_drawdown_scenario_1.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_optimum_scenario_1.csv')),
      },
}
energy_tam_2_ref_data_sources = {
    'Baseline Cases': {
        'Based on IEA, WEO-2018, Current Policies Scenario (CPS)': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_WEO2018_Current_Policies_Scenario_CPS.csv'),
        'Based on: IEA ETP 2017 Ref Tech': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2017_Ref_Tech.csv'),
        'Based on Equinor (2018), Rivalry Scenario': parentdir.joinpath('data', 'energy', 'tam_based_on_Equinor_2018_Rivalry_Scenario.csv'),
        'Based on IEEJ Outlook - 2019, Ref Scenario': parentdir.joinpath('data', 'energy', 'tam_based_on_IEEJ_Outlook_2019_Ref_Scenario.csv'),
    },
    'Conservative Cases': {
        'Based on IEA, WEO-2018, New Policies Scenario (NPS)': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_WEO2018_New_Policies_Scenario_NPS.csv'),
        'Based on IEEJ Outlook - 2019, Advanced Tech Scenario': parentdir.joinpath('data', 'energy', 'tam_based_on_IEEJ_Outlook_2019_Advanced_Tech_Scenario.csv'),
        'Based on IRENA. 2018) Roadmap-2050, REmap Case': parentdir.joinpath('data', 'energy', 'tam_based_on_IRENA__2018_Roadmap2050_REmap_Case.csv'),
        'Based on Equinor (2018), Reform Scenario': parentdir.joinpath('data', 'energy', 'tam_based_on_Equinor_2018_Reform_Scenario.csv'),
    },
    'Ambitious Cases': {
        'Based on IEA, WEO-2018, SDS Scenario': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_WEO2018_SDS_Scenario.csv'),
        'Based on: IEA ETP 2017 B2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2017_B2DS.csv'),
        'Based on Equinor (2018), Renewal Scenario': parentdir.joinpath('data', 'energy', 'tam_based_on_Equinor_2018_Renewal_Scenario.csv'),
        'Based on: IEA ETP 2017 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2017_2DS.csv'),
    },
    '100% RES2050 Case': {
        'Based on average of: LUT/EWG 2019 100% RES, Ecofys 2018 1.5C and Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_average_of_LUTEWG_2019_100_RES_Ecofys_2018_1_5C_and_Greenpeace_2015_Advanced_Revolution.csv'),
    },
    'Region: OECD90': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: Eastern Europe': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: Asia (Sans Japan)': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: Middle East and Africa': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: Latin America': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: China': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: India': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: EU': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
    'Region: USA': {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE 2014 GEM E3 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE 2014 GEM E3 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 550': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: Greenpeace 2015 Reference': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': parentdir.joinpath('data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE 2014 MESSAGE MACRO 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE 2014 GEM E3 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: AMPERE 2014 IMAGE TIMER 450': parentdir.joinpath('data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: Greenpeace 2015 Energy Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace 2015 Advanced Revolution': parentdir.joinpath('data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    },
}
energy_tam_2_pds_data_sources = {
    'Ambitious Cases': {
      'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_plausible_scenario_2.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_drawdown_scenario_2.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_optimum_scenario_2.csv')),
      },
}


class RRS:
  def __init__(self, total_energy_demand, soln_avg_annual_use, conv_avg_annual_use):
    """Data structures to support the Reduction and Replacement Solutions.
       Arguments:
         total_energy_demand: in Terawatt-Hours (TWh), value typically supplied by tam.py
         soln_avg_annual_use: average annual usage of the solution in hours.
         conv_avg_annual_use: average annual usage of the conventional technology in hours.
    """
    self.substitutions = {
        '@soln_avg_annual_use@': soln_avg_annual_use,
        '@conv_avg_annual_use@': conv_avg_annual_use,

        # source for energy mix coal, natural gas, nuclear, and oil:
        # The World Bank Data in The Shift Project Data Portal
        # http://www.tsp-data-portal.org/Breakdown-of-Electricity-Generation-by-Energy-Source#tspQvChart
        '@energy_mix_coal@': 8726.0 / total_energy_demand,
        '@energy_mix_natural_gas@': 4933.0 / total_energy_demand,
        '@energy_mix_nuclear@': 2417.0 / total_energy_demand,
        '@energy_mix_oil@': 1068.0 / total_energy_demand,

        # source for remaining energy mix data:
        # IRENA (2016) Renewable Energy Statistics
        # http://www.irena.org/DocumentDownloads/Publications/IRENA_RE_Statistics_2016.pdf
        '@energy_mix_hydroelectric@': 4019.0 / total_energy_demand,
        '@energy_mix_solar@': 188.073 / total_energy_demand,
        '@energy_mix_wave@': 0.954 / total_energy_demand,
        '@energy_mix_wind_onshore@': 688.956 / total_energy_demand,
        '@energy_mix_wind_offshore@': 24.89 / total_energy_demand,
        '@energy_mix_biomass@': 399.496 / total_energy_demand,
        '@energy_mix_concentrated_solar@': 8.735 / total_energy_demand,
        '@energy_mix_geothermal@': 74.195 / total_energy_demand,
        }
