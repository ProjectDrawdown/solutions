"""Tropical Forest Restoration solution model.
   Excel filename: Drawdown-Tropical Forest Restoration_BioS_v1.1_3Jan2019_PUBLIC.xlsm
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
      filename=None, use_weight=False),
  'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION First Cost per Implementation Unit': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Operating Cost per Functional Unit per Annum': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Net Profit Margin per Functional Unit per Annum': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
      filename=None, use_weight=False),
  'Yield from CONVENTIONAL Practice': vma.VMA(
      filename=None, use_weight=False),
  'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
      filename=None, use_weight=False),
  'Electricty Consumed per CONVENTIONAL Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Energy Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'Total Energy Used per SOLUTION functional unit': vma.VMA(
      filename=None, use_weight=False),
  'Fuel Consumed per CONVENTIONAL Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'Fuel Reduction Factor SOLUTION': vma.VMA(
      filename=None, use_weight=False),
  't CO2-eq (Aggregate emissions) Reduced per Land Unit': vma.VMA(
      filename=None, use_weight=False),
  't CO2 Reduced per Land Unit': vma.VMA(
      filename=None, use_weight=False),
  't N2O-CO2-eq Reduced per Land Unit': vma.VMA(
      filename=None, use_weight=False),
  't CH4-CO2-eq Reduced per Land Unit': vma.VMA(
      filename=None, use_weight=False),
  'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE': vma.VMA(
      filename=None, use_weight=False),
  'Indirect CO2 Emissions per SOLUTION Implementation Unit': vma.VMA(
      filename=None, use_weight=False),
  'Sequestration Rates': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
      use_weight=False),
  'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing': vma.VMA(
      filename=None, use_weight=False),
  'Disturbance Rate': vma.VMA(
      filename=None, use_weight=False),
  'Percent of Degraded Land Suitable for Intact Tropical Forest Restoration': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Percent_of_Degraded_Land_Suitable_for_Intact_Tropical_Forest_Restoration.csv"),
      use_weight=False),
  'Root:shoot ratio of degraded forest': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Root_shoot_ratio_of_degraded_forest.csv"),
      use_weight=False),
  'Start Carbon storage in Base year': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Start_Carbon_storage_in_Base_year.csv"),
      use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": None,
  "functional unit": "Mha",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Tropical Forest Restoration'
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
    self.ae = aez.AEZ(solution_name=self.name)
    if self.ac.use_custom_tla:
      self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))
      custom_world_vals = self.c_tla.get_world_values()
    else:
      custom_world_vals = None
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(), custom_world_values=custom_world_vals)

    # Custom PDS Data
    ca_pds_columns = ['Year'] + dd.REGIONS
    commit_13_dec_2016 = 136.32    # commitment to reforestation made Dec 13, 2016.
    commit_13_dec_2016_tmr = 0.93  # % commitment that are projects in tropical TMR (based on country level commitments)
    commit_13_dec_2016_mha = commit_13_dec_2016 * commit_13_dec_2016_tmr  # Mha of current commitments in tropical TMR
    intact_13_dec_2016 = 0.328     # % commitment in tropical TMR available are for intact forest
    #                                restoration (based on country level commitments)
    max_land_bonn = 350.0  # Max land Expected total land commited under Bonn Challenge and NY Declaration
    max_land_wri = self.tla_per_region.loc[2050, 'World']  # Total degraded land suitable for
    #                                restoration, considered to be in tropical TMRs by WRI

    commit_1_mha_new = max_land_bonn - commit_13_dec_2016  # Mha of total degraded land available for
    #         new commitments in tropical TMR + additional degraded land available from the Forest
    #         Protection solution, for which exact area has to be estimated.
    final_adoption_1 = (commit_13_dec_2016_mha * intact_13_dec_2016) + (commit_1_mha_new * 1.0)
    data_source_1 = {
            'name': 'Optimistic-Achieve Commitment in 15 years w/ 100% intact, NYDF/2030 (Charlotte Wheeler, 2016)',
            'include': True,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million
            #       hectares (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.This scenario projects the future adoption
            # of the solution considering, (1) 100% intact forest restoration, (2) 350 million
            # hectare land availability for future restoration of tropical forests, and
            # (3) the commitments will be realized by the year 2030.
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2030, final_adoption_1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2031, final_adoption_1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    commit_2_mha_new = max_land_wri - (commit_13_dec_2016 * commit_13_dec_2016_tmr)
    final_adoption_2 = (commit_13_dec_2016_mha * intact_13_dec_2016) + (commit_2_mha_new * 1.0)
    data_source_2 = {
            'name': 'Optimistic-Achieve Commitment in 15 years w/ 100% intact, WRI/2030 (Charlotte Wheeler, 2016)',
            'include': True,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.This scenario projects the future adoption
            # of the solution considering, (1) 100% intact forest restoration, (2) 304 million
            # hectare land availability for future restoration of tropical forests, and (3) the
            # commitments will be realized by the year 2030.
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2030, final_adoption_2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2031, final_adoption_2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    future_3_tmr = 0.328  # % of future commitments in tropical thermal moisture regime available are for intact forest restoration
    final_adoption_3 = ((commit_13_dec_2016_mha * intact_13_dec_2016) +
                    ((max_land_wri - commit_13_dec_2016_mha) * future_3_tmr))
    data_source_3 = {
            'name': 'Conservative-Achieve Commitment in 15 years w/ 32.8% intact, WRI/2030 (Charlotte Wheeler,2016)',
            'include': True,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.This scenario projects the future
            # adoption of the solution considering, (1) 32.8% intact forest restoration,
            # (2) 304 million hectare land availability for future restoration of tropical forests,
            # and (3) the commitments will be realized by the year 2030.
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2030, final_adoption_3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2031, final_adoption_3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    future_4_tmr = 0.328  # % of future commitments in tropical thermal moisture regime available are for intact forest restoration
    final_adoption_4 = ((commit_13_dec_2016_mha * intact_13_dec_2016) +
                    ((max_land_wri - commit_13_dec_2016_mha) * future_4_tmr))
    data_source_4 = {
            'name': 'Conservative-Achieve Commitment in 15 years w/ 32.8% intact with continued growth post-2030, WRI/2030 and beyond (Charlotte Wheeler,2016)',
            'include': True,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.This scenario projects the future
            # adoption of the solution considering, (1) 32.8% intact forest restoration,
            # (2) 304 million hectare land availability for future restoration of tropical forests,
            # and (3) the commitments will be realized by the year 2030.
            #
            # This is scenario 3, except, it is also assumed that the adoption of the solution
            # will continue post 2030 as well.
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2030, final_adoption_4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    future_5_tmr = 1.0  # % of future commitments in tropical thermal moisture regime available are for intact forest restoration
    final_adoption_5 = ((commit_13_dec_2016_mha * intact_13_dec_2016) +
                    ((max_land_wri - commit_13_dec_2016_mha) * future_5_tmr))
    data_source_5 = {
            'name': 'Conservative-Achieve Commitment in 30 years w/ 100% intact, WRI/2045 (Charlotte Wheeler,2016)',
            'include': True,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.This scenario projects the future
            # adoption of the solution considering, (1) 100% intact forest restoration,
            # (2) 304 million hectare land availability for future restoration of tropical forests,
            # and (3) the commitments will be realized by the year 2045.
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2045, final_adoption_5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2046, final_adoption_5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    future_6_tmr = 0.328  # % of future commitments in tropical thermal moisture regime available are for intact forest restoration
    final_adoption_6 = ((commit_13_dec_2016_mha * intact_13_dec_2016) +
                    ((max_land_wri - commit_13_dec_2016_mha) * future_6_tmr))
    data_source_6 = {
            'name': 'Conservative-Achieve Commitment in 30 years w/ 32.8% intact, WRI/2045 (Charlotte Wheeler,2016)',
            'include': True,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.This scenario projects the future
            # adoption of the solution considering, (1) 32.8% intact forest restoration,
            # (2) 304 million hectare land availability for future restoration of tropical forests,
            # and (3) the commitments will be realized by the year 2045.
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2045, final_adoption_6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2046, final_adoption_6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    future_7_tmr = 0.328  # % of future commitments in tropical thermal moisture regime available are for intact forest restoration
    final_adoption_7 = ((commit_13_dec_2016_mha * intact_13_dec_2016) +
                    ((max_land_wri - commit_13_dec_2016_mha) * future_7_tmr))
    data_source_7 = {
            'name': 'Conservative-Achieve Commitment in 30 years w/ 32.8% intact with continued growth, WRI/2045 (Charlotte Wheeler,2016)',
            'include': True,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario. This scenario projects the future
            # adoption of the solution considering, (1) 32.8% intact forest restoration,
            # (2) 304 million hectare land availability for future restoration of tropical forests,
            # and (3) the commitments will be realized by the year 2045.
            #
            # This is scenario 6, except, it is also assumed that the adoption of the solution
            # will continue post 2045 as well.
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2045, final_adoption_7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    future_8_tmr = 1.0  # % of future commitments in tropical thermal moisture regime available are for intact forest restoration
    final_adoption_8 = ((commit_13_dec_2016_mha * intact_13_dec_2016) +
                    ((max_land_wri - commit_13_dec_2016_mha) * future_8_tmr))
    data_source_8 = {
            'name': 'Conservative-Achieve Commitment in 45 years w/ 100% intact, WRI/2060 (Charlotte Wheeler,2016)',
            'include': False,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.
            #
            # This scenario projects the future adoption of the solution considering,
            # (1) 100% intact forest restoration, (2) 304 million hectare land availability
            # for future restoration of tropical forests, and (3) the commitments will be
            # realized by the year 2060. 
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2060, final_adoption_8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }


    future_9_tmr = 0.328  # % of future commitments in tropical thermal moisture regime available are for intact forest restoration
    final_adoption_9 = ((commit_13_dec_2016_mha * intact_13_dec_2016) +
                    ((max_land_wri - commit_13_dec_2016_mha) * future_9_tmr))
    data_source_9 = {
            'name': 'Conservative-Achieve Commitment in 45 years w/ 32.8% intact, WRI/2060 (Charlotte Wheeler,2016)',
            'include': False,
            # The adoption scenarios are calculated using the linear trendline based on
            #   (i) current restoration commitments to date (as taken on 13/12/2016 from Bonn
            #       Challenge website);
            #  (ii) potential future commitments for intact forest restoration in tropics {32.80%
            #       (based on current commitments) or 100% (projected)};
            # (iii) the proportion of committed land restored to intact forest {304 million hectares
            #       (based on WRI calculation) or 350 million hectares (based on New York
            #       Declaration)}; and
            #  (iv) the year commitments are realized (2030, 2045 or 2060).
            # The current restoration commitments is fixed in all custom scenarios, while the rest
            # variables changes from scenario to scenario.
            #
            # This scenario projects the future adoption of the solution considering,
            # (1) 32.8% intact forest restoration, (2) 304 million hectare land availability
            # for future restoration of tropical forests, and (3) the commitments will be realized
            # by the year 2060. 
            'datapoints': pd.DataFrame([
                [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2060, final_adoption_9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')
    }

    ca_pds_data_sources = [data_source_1, data_source_2, data_source_3, data_source_4,
            data_source_5, data_source_6, data_source_7, data_source_8, data_source_9]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
        total_adoption_limit=self.tla_per_region)


    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [0.0, 0.0, 0.0, 0.0, 0.0,
       0.0, 0.0, 0.0, 0.0, 0.0],
       index=dd.REGIONS)
    ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial / self.tla_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_total_adoption_units=self.tla_per_region, pds_total_adoption_units=self.tla_per_region,
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
        regime_distribution=self.ae.get_land_distribution())

