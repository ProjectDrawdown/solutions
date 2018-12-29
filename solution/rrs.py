"""Features shared by most or all of the
   Reduction and Replacement Solution (RRS) implementations.
"""

import pathlib
datadir = pathlib.Path(__file__).parents[1]

tam_ref_data_sources = {
    'Baseline Cases': {
      'Baseline: Based on- IEA ETP 2016 6DS': str(datadir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_6DS.csv')),
      'Baseline: Based on- AMPERE MESSAGE-MACRO Reference': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_Reference.csv')),
      'Baseline: Based on- AMPERE GEM E3 Reference': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_Reference.csv')),
      'Baseline: Based on- AMPERE IMAGE/TIMER Reference': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_Reference.csv')),
      },
    'Conservative Cases': {
      'Conservative: Based on- IEA ETP 2016 4DS': str(datadir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_4DS.csv')),
      'Conservative: Based on- AMPERE MESSAGE-MACRO 550': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_550.csv')),
      'Conservative: Based on- AMPERE GEM E3 550': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_550.csv')),
      'Conservative: Based on- AMPERE IMAGE/TIMER 550': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_550.csv')),
      'Conservative: Based on- Greenpeace 2015 Reference': str(datadir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Reference.csv')),
      },
    'Ambitious Cases': {
      'Ambitious: Based on- IEA ETP 2016 2DS': str(datadir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_2DS.csv')),
      'Ambitious: Based on- AMPERE MESSAGE-MACRO 450': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_450.csv')),
      'Ambitious: Based on- AMPERE GEM E3 450': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_450.csv')),
      'Ambitious: Based on- AMPERE IMAGE/TIMER 450': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_450.csv')),
      'Ambitious: Based on- Greenpeace Energy [R]evolution': str(datadir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Energy_Revolution.csv')),
      },
    '100% RES2050 Case': {
      '100% REN: Based on- Greenpeace Advanced [R]evolution': str(datadir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Advanced_Revolution.csv')),
      },
}
tam_pds_data_sources = {
    'Ambitious Cases': {
      'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario': str(datadir.joinpath(
        'data', 'energy', 'PDS_plausible_scenario.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario': str(datadir.joinpath(
        'data', 'energy', 'PDS_drawdown_scenario.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario': str(datadir.joinpath(
        'data', 'energy', 'PDS_optimum_scenario.csv')),
      },
}
