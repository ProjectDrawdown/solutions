"""Bamboo solution model.
   Excel filename: Drawdown_RRS-BIOSEQ_Model_v1.1_MASTER_Bamboo-Mar2020.xlsm
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
from model import unitadoption
from model import vma
from model import tla
from solution import land

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
        filename=None, use_weight=False),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'CONVENTIONAL Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
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
    'Indirect CO2 Emissions per SOLUTION Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'Sequestration Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
        use_weight=False),
    'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestered_Carbon_NOT_Emitted_after_Cyclical_Harvesting_Clearing.csv"),
        use_weight=False),
    'Disturbance Rate': vma.VMA(
        filename=None, use_weight=False),
    'Above-ground biomass (AGB)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Above_ground_biomass_AGB.csv"),
        use_weight=False),
    'Below-ground biomass (BGB)': vma.VMA(
        filename=None, use_weight=False),
    'Soil organic carbon (SOC)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Soil_organic_carbon_SOC.csv"),
        use_weight=False),
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

name = 'Bamboo'
solution_category = ac.SOLUTION_CATEGORY.LAND

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
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0],
            dtype=np.object).set_index('param')
        ad_data_sources = {
            'Raw Data for ALL LAND TYPES': {
                'FAO 2010': THISDIR.joinpath('ad', 'ad_FAO_2010.csv'),
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        adoption_2014 = self.ac.ref_base_adoption['World']
        tla_2050 = self.tla_per_region.loc[2050, 'World']
        ds4_percent_adoption_2050 = 0.85
        ds4_adoption_2050 = ds4_percent_adoption_2050 * tla_2050
        ca_pds_data_sources = [
            {'name': 'Low growth, linear trend', 'include': True, 'least_sq': True,
                # This scenario projects the future adoption of bamboo based on historical regional
                # growth reported for the 1990-2010 period in the Global Forest Resource Assessment
                # 2010 report, published by the FAO.
                'datapoints': pd.DataFrame([
                   [1990, np.nan, 0.0, 0.0, 15.412, 3.688, 10.399, 0.0, 0.0, 0.0, 0.0],
                   [2000, np.nan, 0.0, 0.0, 16.311, 3.656, 10.399, 0.0, 0.0, 0.0, 0.0],
                   [2005, np.nan, 0.0, 0.0, 16.943, 3.640, 10.399, 0.0, 0.0, 0.0, 0.0],
                   [2010, np.nan, 0.0, 0.0, 17.360, 3.627, 10.399, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium growth, linear trend', 'include': True,
                # This scenario projects the future adoption of bamboo based on the highest
                # historical regional annual growth rate, based on 1990-2010 FAO data. The highest
                # annual growth rate was reported in the Asia region (0.0974 Mha/year). Thus, it
                # was assumed that bamboo plantation in other regions will grow by half of the
                # growth rate calculated in Asia (0.05 Mha/year), while bamboo plantation in Asia
                # continues to grow with the same rate.
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Medium_growth_linear_trend.csv')},
            {'name': 'High growth, linear trend', 'include': True,
                # This scenario projects the future adoption of bamboo based on the highest
                # historical regional annual growth rate, based on 1990-2010 FAO data. The highest
                # annual growth rate was reported in the Asia region. Thus, it was assumed that
                # bamboo plantation in other regions will grow at the same growth rate calculated
                # in Asia (0.0974 Mha/year), while bamboo plantation in Asia continues to grow at
                # double this rate (0.19 Mha/year).
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_growth_linear_trend.csv')},
            {'name': 'Max growth, linear trend', 'include': True,
                # Considering the limited total land available for bamboo, this scenario
                # projects an aggressive adoption of bamboo plantation and projects a worldwide
                # 85% adoption of bamboo plantation by 2050.
                'datapoints': pd.DataFrame([
                   [2014, adoption_2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                   [2050, ds4_adoption_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Song et al. 2013', 'include': True,
                # "Annual increase in global bamboo forests based on a global historical annual
                # expansion of bamboo forests of 3%, as reported in Song et al. 2013 (see p.7
                # of publication).
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Song_et_al__2013.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        # Manual adjustment made in spreadsheet for Drawdown 2020.
        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014] = [32.8913636108367000, 0.0, 0.0, 18.0440250214314000, 3.9611495064729000,
                    10.8861890829324000, 0.0, 0.0, 0.0, 0.0]
            df.loc[2015] = [33.0453659423780000, 0.0, 0.0, 18.1703910504150000, 3.9772571687142000,
                    10.8977177232488000, 0.0, 0.0, 0.0, 0.0]
            df.loc[2016] = [33.2014226143695000, 0.0, 0.0, 18.2979284861039000, 3.9938159101118100,
                    10.9096782181539000, 0.0, 0.0, 0.0, 0.0]
            df.loc[2017] = [33.3595689913150000, 0.0, 0.0, 18.4266654288099000, 4.0108468526825300,
                    10.9220567098226000, 0.0, 0.0, 0.0, 0.0]
            df.loc[2018] = [33.5198404377181000, 0.0, 0.0, 18.5566299788448000, 4.0283711184431500,
                    10.9348393404302000, 0.0, 0.0, 0.0, 0.0]

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': '[Type Scenario 1 Name Here (REF CASE)...]', 'include': True,
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
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
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
            copy_pds_to_ref=False,
            copy_ref_datapoint=False,
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
            fc_convert_iunit_factor=land.MHA_TO_HA)

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
            conversion_factor=land.MHA_TO_HA)

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

