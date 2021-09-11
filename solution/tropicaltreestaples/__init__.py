"""Tropical Tree Staples solution model.
   Excel filename: Drawdown_RRS-BIOSEQ_Model_v1.1b_MASTER_TropicalTreeStaples_Mar2020.xlsm
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
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'CONVENTIONAL Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'Yield from CONVENTIONAL Practice': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_from_CONVENTIONAL_Practice.csv"),
        use_weight=False),
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
    'Yield of Annual Staple Crops': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_of_Annual_Staple_Crops.csv"),
        use_weight=False),
    'Yield of Perennial Staple Crops': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_of_Perennial_Staple_Crops.csv"),
        use_weight=False),
    'C sequestered in above-ground biomass (AGB)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "C_sequestered_in_above_ground_biomass_AGB.csv"),
        use_weight=False),
    'Belowground Biomass (BGB)': vma.VMA(
        filename=None, use_weight=False),
    'Soil Organic Carbon (SOC)': vma.VMA(
        filename=None, use_weight=False),
    'Weight for financial variable on degraded area': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Weight_for_financial_variable_on_degraded_area.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Tropical Tree Staples'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-18p2050-Plausible-customPDS-low-Jan2020"
PDS2 = "PDS-43p2050-Drawdown-customPDS-avg-Jan2020"
PDS3 = "PDS-67p2050-Optimum-customPDS-high-Jan2020"

class Scenario(scenario.LandScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    _pds_ad_sources = scenario.load_sources(THISDIR/'ad'/'ad_sources.json', '*')

    def __init__(self, scen=None):
        if isinstance(scen, ac.AdvancedControls):
            self.scenario = scen.name
            self.ac = scen
        else:
            self.scenario = scen or PDS2
            self.ac = scenarios[self.scenario]

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

        # Set this ourselves, since we use it below
        adconfig = adoptiondata.make_adoption_config(overrides=[
            ('trend','World',self.ac.soln_pds_adoption_prognostication_trend),
            ('growth','World',self.ac.soln_pds_adoption_prognostication_growth)])
        self.ad = adoptiondata.AdoptionData(self.ac, self._pds_ad_sources, adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_2050 = self.tla_per_region.loc[2050]
        ref_base_2018 = pd.Series(self.ac.ref_base_adoption)

        # Data Source 1: Jong 2018
        # (https://link.springer.com/content/pdf/10.1007%2F978-981-10-5269-9.pdf);
        # FAOSTAT, accessed in 2018

        # 2050 medium adoption value based on historical data interpolation, based on FAOSTAT data
        ds1_adoption_data = self.ad.adoption_data(region='World')
        ds1_ad_2050 = ds1_adoption_data.loc[2050, 'FAOSTAT 2016 + Literature (Exponential)']
        ds1_percent = ds1_ad_2050 / tla_2050['World']

        ds1_percentages = pd.Series([0.0, ds1_percent, ds1_percent, ds1_percent,
             ds1_percent, ds1_percent, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds1_regional = tla_2050 * ds1_percentages
        ds1_regional.clip(lower=ref_base_2018, inplace=True)
        ds1_regional['World'] = 0.0
        ds1_world_2050 = ds1_regional.sum(axis=0)
        # Excel uses regional TLA to compute World, but doesn't populate regional adoption
        ds1_2050 = [ds1_world_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


        # Data Source 2: Jong 2018
        # (https://link.springer.com/content/pdf/10.1007%2F978-981-10-5269-9.pdf);
        # FAOSTAT, accessed in 2018

        # 2050 average adoption value based on historical data interpolation,
        # based on FAOSTAT data (without TLA limitation)
        ds2_adoption_data = self.ad.adoption_data(region='World')
        ds2_ad_2050 = ds2_adoption_data.loc[2050, 'FAOSTAT 2016 + Literature (2nd order)']
        ds2_percent = ds2_ad_2050 / tla_2050['World']

        ds2_percentages = pd.Series([0.0, ds2_percent, ds2_percent, ds2_percent,
             ds2_percent, ds2_percent, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds2_regional = tla_2050 * ds2_percentages
        ds2_regional.clip(lower=ref_base_2018, inplace=True)
        ds2_regional['World'] = 0.0
        ds2_world_2050 = ds2_regional.sum(axis=0)
        # Excel uses regional TLA to compute World, but doesn't populate regional adoption
        ds2_2050 = [ds2_world_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


        # Data Source 3: Jong 2018
        # (https://link.springer.com/content/pdf/10.1007%2F978-981-10-5269-9.pdf);
        # FAOSTAT, accessed in 2018

        # 2050 minimum adoption value based on historical data interpolation,
        # based on FAOSTAT data (without TLA limitation)
        ds3_adoption_data = self.ad.adoption_data(region='World')
        ds3_ad_2050 = ds3_adoption_data.loc[2050, 'FAOSTAT 2016 + Literature (linear)']
        ds3_percent = ds3_ad_2050 / tla_2050['World']

        ds3_percentages = pd.Series([0.0, ds3_percent, ds3_percent, ds3_percent,
             ds3_percent, ds3_percent, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds3_regional = tla_2050 * ds3_percentages
        ds3_regional.clip(lower=ref_base_2018, inplace=True)
        ds3_regional['World'] = 0.0
        ds3_world_2050 = ds3_regional.sum(axis=0)
        # Excel uses regional TLA to compute World, but doesn't populate regional adoption
        ds3_2050 = [ds3_world_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        ca_pds_data_sources = [
            {'name': 'Medium growth based on exponential interpolation of historical data, linear trend',
                'include': True,
                # This scenario is built on the historical (1962-2016) average global
                # growth rate of tropical staple crops based on FAOSTAT 2018 and Jong
                # et al. 2018 data (see "Master - Adoption Data" sheet for details).
                # Future projections up to 2060 were interpolated based on an exponential
                # best-curve fit applied to historical data available at decadal intervals
                # for the given time-period.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + ds1_2050,
                    ], columns=ca_pds_columns).set_index('Year')
                },
            {'name': 'High growth based on 2nd order polynomial interpolation of historical data, linear trend',
                'include': True,
                # This scenario is built on the historical (1962-2016) average global
                # growth rate of tropical staple crops based on FAOSTAT 2018 and Jong
                # et al. 2018 data (see "Master - Adoption Data" sheet for details).
                # Future projections up to 2060 were interpolated based on a 2nd order
                # polynomial best-curve fit applied to historical data available at
                # decadal intervals for the given time-period.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + ds2_2050,
                    ], columns=ca_pds_columns).set_index('Year')
                },
            {'name': 'Low growth based on linear interpolation of historical data, linear trend',
                'include': True,
                # This scenario is built on the historical (1962-2016) average global
                # growth rate of tropical staple crops based on FAOSTAT 2018 and Jong
                # et al. 2018 data (see "Master - Adoption Data" sheet for details).
                # Future projections up to 2060 were interpolated based on a linear
                # best-curve fit applied to historical data available at decadal
                # intervals for the given time-period.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + ds3_2050,
                    ], columns=ca_pds_columns).set_index('Year')
                },
            {'name': 'Medium growth with 70% adoption 2030 (based on exponential interpolations of historical data), linear trend',
                'include': True,
                # Scenario 1, with 70% adoption by 2030
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2030] + [0.7 * x for x in ds1_2050],
                    [2050] + ds1_2050,
                    ], columns=ca_pds_columns).set_index('Year')
                },
            {'name': 'High growth with 70% adoption 2030 (based on 2nd order polynomial interpolations of historical data), linear trend',
                'include': True,
                # Scenario 2, with 70% adoption by 2030
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2030] + [0.7 * x for x in ds2_2050],
                    [2050] + ds2_2050,
                    ], columns=ca_pds_columns).set_index('Year')
                },
            {'name': 'Low growth with 70% adoption 2030 (based on linear interpolations of historical data), linear trend',
                'include': True,
                # Scenario 3, with 70% adoption by 2030
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2030] + [0.7 * x for x in ds3_2050],
                    [2050] + ds3_2050,
                    ], columns=ca_pds_columns).set_index('Year')
                },
            {'name': 'Max adoption, linear growth',
                'include': True,
                # "100% adoption by 2050
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + [tla_2050['World'], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')
                },
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            for y in range(2012, 2019):
                df.loc[y] = [0.0001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

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
