"""Temperate Forest Restoration solution model.
   Excel filename: Drawdown_RRS-BIOSEQ_Model_v1.1c_MASTER_Temperate_Restoration_Mar2020.xlsm
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
    'Percent of Degraded Land Suitable for Intact Temperate Forest Restoration': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Percent_of_Degraded_Land_Suitable_for_Intact_Temperate_Forest_Restoration.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Temperate Forest Restoration'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-62p2050-Plausible-customPDS-avg-Jan2020"
PDS2 = "PDS-86p2050-Drawdown-customPDS-high-Jan2020"
PDS3 = "PDS-74p2050-Optimum-PDScustomadoption-max"

class Scenario(scenario.LandScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TLA
        self.ae = aez.AEZ(solution_name=self.name, cohort=2020,
                regimes=dd.THERMAL_MOISTURE_REGIMES8)
        if self.ac.use_custom_tla:
            self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))
            custom_world_vals = self.c_tla.get_world_values()
        else:
            custom_world_vals = None
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(),
            custom_world_values=custom_world_vals)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS

        # Current commitments made under Bonn Challenge (taken on 16/12/2019)
        bonn_mha = 149.012768

        # % current commitments are projects in temperate thermal moisture regime
        temperate_percent = 0.198187597540394

        # % current commitments in temperate thermal moisture regime available are
        # for intact forest restoration
        intact_percent = 0.4423

        # Calculated by subtracting the total degraded land suitable for tropical
        # forest restoration (304 Mha) and boreal (46 Mha) from the WRI estimates
        # of 500 Mha as the potential global area for forest restoration
        # TODO: the spatial-aez work in late 2019 provided direct data input of temperate
        #       forest area, distinct from boreal and tropical, which could be used here.
        title = 'Percent of Degraded Land Suitable for Intact Temperate Forest Restoration'
        intact_mha = self.ac.lookup_vma(vma_title=title)
        if intact_mha is None:
            intact_mha = VMAs[title].avg_high_low(statistic='mean')

        # Max land Expected total land commited under Bonn Challenge and NY Declaration 
        max_land = 350.0

        # Mha of current commitments in temperate thermal moisture regime
        committed_mha = bonn_mha * temperate_percent

        # Mha of total degraded land available for new commitments in
        # temperate thermal moisture regime, from New York Declaration
        nydf_new_mha = (max_land - bonn_mha) * temperate_percent

        # WRI prediction for max available land area
        wri_new_mha = intact_mha - committed_mha

        # DATA SOURCE 1, using NYDF land area
        ds1_future_commit = 1.0
        ds1_2030 = (committed_mha * intact_percent) + (nydf_new_mha * ds1_future_commit)

        # future land area with WRI prediction plus 44.23% and 100% commitment
        future_mha_44p = (committed_mha * intact_percent) + (wri_new_mha * 0.4423)
        future_mha_100p = (committed_mha * intact_percent) + (wri_new_mha * 1.0)

        ca_pds_data_sources = [
            {'name': 'Optimistic-Achieve Commitment in 15 years w/ 100% intact, (Charlotte Wheeler, 2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060).  In this '
                    'scenario, NYDF prediction for max area available for temperate forest '
                    'restoration, 100% new commitment for intact forest and year 2030 was '
                    'considered when the commitments will be realized.'),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2030, ds1_2030, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2031, ds1_2030, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Optimistic-Achieve Commitment in 15 years w/ 100% intact, WRI estimates (Charlotte Wheeler, 2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 100% new commitment for intact forest and year 2030 was '
                    'considered when the commitments will be realized. '),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2030, future_mha_100p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2031, future_mha_100p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative-Achieve Commitment in 15 years w/ 44.2% intact, (Charlotte Wheeler,2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 44.23% new commitment for intact forest and year 2030 was '
                    'considered when the commitments will be realized. '),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2030, future_mha_44p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2031, future_mha_44p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative-Achieve Commitment in 15 years w/ 44.2% intact with continued growth post-2030, (Charlotte Wheeler,2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 44.23% new commitment for intact forest and year 2030 was '
                    'considered when the commitments will be realized, with continued growth '
                    'in post 2030.'),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2030, future_mha_44p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative-Achieve Commitment in 30 years w/ 100% intact, (Charlotte Wheeler,2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 100% new commitment for intact forest and year 2045 was '
                    'considered when the commitments will be realized. '),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2045, future_mha_100p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2046, future_mha_100p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative-Achieve Commitment in 30 years w/ 44.2% intact, (Charlotte Wheeler,2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 44.23% new commitment for intact forest and year 2045 was '
                    'considered when the commitments will be realized. '),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2045, future_mha_44p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2046, future_mha_44p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative-Achieve Commitment in 30 years w/ 44.2% intact with continued growth, (Charlotte Wheeler,2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 44.23% new commitment for intact forest and year 2045 was '
                    'considered when the commitments will be realized, with continued growth '
                    'in post 2045. '),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2045, future_mha_44p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative-Achieve Commitment in 45 years w/ 100% intact (Charlotte Wheeler,2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 100% new commitment for intact forest and year 2060 was '
                    'considered when the commitments will be realized. '),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2060, future_mha_100p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative-Achieve Commitment in 45 years w/ 44.2% intact (Charlotte Wheeler,2016)', 'include': True,
                'description': (
                    'The adoption scenarios are calculated using the linear trendline based '
                    'on: (1) Current commitments to date, (2) Potential future commitments, (3) '
                    'The proportion of committee land restored to intact forest (100% or 44.23%), '
                    'and (4) The year commitments are realised (2030, 2045 or 2060). In this '
                    'scenario, WRI prediction for max area available for temperate forest '
                    'restoration, 44.23% new commitment for intact forest and year 2060 was '
                    'considered when the commitments will be realized. '),
                'maximum': intact_mha,
                'datapoints': pd.DataFrame([
                    [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [2060, future_mha_44p, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        self.initialize_adoption_bases()
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
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
            use_first_pds_datapoint_main=True,
            adoption_base_year=2018,
            copy_pds_to_ref=False,
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