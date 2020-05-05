"""Grassland Protection solution model.
   Excel filename: Drawdown_RRS-BIOSEQProtect_Model_v1.1d_Grassland Protection_Mar2020.xlsm
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
        filename=None, use_weight=False),
    'CONVENTIONAL Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=None, use_weight=False),
    'Yield from CONVENTIONAL Practice': vma.VMA(
        filename=None, use_weight=False),
    'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
        filename=None, use_weight=False),
    'Average Electricty Used DEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Energy Efficiency Factor UNDEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'ALTERNATIVE APPROACH Annual Energy Used UNDEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Consumed on DEGRADED Land': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Reduction Factor for UNDEGRADED Land': vma.VMA(
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
    'Indirect CO2-eq Emissions DEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2-eq Emissions UNDEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Sequestration Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
        use_weight=False),
    'Growth Rate of Land Degradation': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Growth_Rate_of_Land_Degradation.csv"),
        use_weight=False),
    'Disturbance Rate': vma.VMA(
        filename=None, use_weight=False),
    't C storage in Protected Landtype': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_C_storage_in_Protected_Landtype.csv"),
        use_weight=False),
    'Global Multipler for Regrowth': vma.VMA(
        filename=None, use_weight=False),
    'Tropical Multipler for Regrowth': vma.VMA(
        filename=None, use_weight=False),
    'Temperate Multiplier for Regrowth': vma.VMA(
        filename=None, use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Grassland Protection'
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
        if self.ac.use_custom_tla and self.ac.custom_tla_fixed_value is not None:
            self.c_tla = tla.CustomTLA(fixed_value=self.ac.custom_tla_fixed_value)
            custom_world_vals = self.c_tla.get_world_values()
        elif self.ac.use_custom_tla:
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
                'Henwood 1994 and Henwood 2010': THISDIR.joinpath('ad', 'ad_Henwood_1994_and_Henwood_2010.csv'),
                'Henwood 2010': THISDIR.joinpath('ad', 'ad_Henwood_2010.csv'),
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_world_2050 = self.tla_per_region.loc[2050, 'World']
        ad_2014 = 132.860079407797  # adoption in year 2014 (refer B647, adoption data sheet)
        ad_2018 = self.ac.ref_base_adoption['World']
        total_temperate_grassland = 1209.098

        # In Excel, the Custom PDS Scenarios tab columns AC:AF compute a limit on adoption
        # based on the amount of degraded land remaining. We compute the same limit here.
        def constrained_tla(ad_2050):
            (slope, intercept) = np.polyfit(x=[2018, 2050], y=[ad_2018, ad_2050], deg=1)
            degrade_df = pd.DataFrame(0, index=range(2014, 2061), columns=[
                'Total undegraded land at the start of the year',
                'Degraded land at the end of the year',
                'Total undegraded land at the end of the year', 'Constrained TLA'])
            for year in range(2014, 2061):
                if year == 2014:
                    undeg_start = tla_world_2050 - ad_2014
                else:
                    last = degrade_df.loc[year-1, 'Total undegraded land at the end of the year']
                    undeg_start = last - slope
                degrade_df.loc[year, 'Total undegraded land at the start of the year'] = undeg_start
                degraded_end = max(0, undeg_start * self.ac.degradation_rate)
                degrade_df.loc[year, 'Degraded land at the end of the year'] = degraded_end
                degrade_df.loc[year, 'Total undegraded land at the end of the year'] = (
                        undeg_start - degraded_end)
                degrade_df.loc[year, 'Constrained TLA'] = (tla_world_2050 -
                        degrade_df['Degraded land at the end of the year'].sum())
            return degrade_df['Constrained TLA'].min()

        # Data Source 1: Linear growth, conservative
        # SOURCE: Henwood, W. D. (2010). Toward a strategy for the conservation and
        # protection of the world's temperate grasslands. Great Plains Research, 121-134.
        ds1_commit_2014 = 0.25  # % commitment for protection of temperate grassland by 2014
        ds1_adoption_2050 = total_temperate_grassland * ds1_commit_2014
        ds1_constrained_tla = constrained_tla(ad_2050=ds1_adoption_2050)

        # Data Source 3: Linear growth, High
        # SOURCE: Henwood, W. D. (2010). Toward a strategy for the conservation and
        # protection of the world's temperate grasslands. Great Plains Research, 121-134.
        ds3_commit_2014 = 0.5  # % commitment for protection of temperate grassland by 2014
        ds3_adoption_2018 = self.ac.ref_base_adoption['World']
        ds3_adoption_2050 = total_temperate_grassland * ds3_commit_2014
        ds3_constrained_tla = constrained_tla(ad_2050=ds3_adoption_2050)

        # Data Source 4: Linear growth, High
        # SOURCE: Henwood, W. D. (2010). Toward a strategy for the conservation and
        # protection of the world's temperate grasslands. Great Plains Research, 121-134.
        ds4_commit_2014 = 1.0  # % commitment for protection of temperate grassland by 2014
        ds4_adoption_2018 = self.ac.ref_base_adoption['World']
        ds4_adoption_2050 = total_temperate_grassland * ds4_commit_2014
        ds4_constrained_tla = constrained_tla(ad_2050=ds4_adoption_2050)

        ca_pds_data_sources = [
            {'name': 'Linear growth, conservative', 'include': True, 'maximum': ds1_constrained_tla,
                'description': (
                    'The future adoption is projected based on the protection commitment made '
                    'for the temperate grassland, which is 10% of the total temperate grassland '
                    'area. Since, the current protection is much higher than the 10% commitment, '
                    'so 25% commitment target is considered for this projection. '
                    ),
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds1_adoption_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Exsisting progonostication', 'include': True, 'maximum': ds1_constrained_tla,
                'description': (
                    'The future adoption value was projected using the data interpolator and '
                    'adoption data sheet based on the data available on protected grassland area '
                    'globally in the temperate in the year 1994/2010 and 1996/2009. '
                    'NOTE: in actual implementation, this scenario is set equal to the "Linear '
                    'Growth, conservative" scenario not from adoption data.'
                    ),
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds1_adoption_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Linear growth, High', 'include': True, 'maximum': ds3_constrained_tla,
                'description': (
                    'The future adoption is projected based on the protection commitment made '
                    'for the temperate grassland, which is 10% of the total temperate grassland '
                    'area. Since, the current protection is much higher than the 10% commitment, '
                    'so 50% commitment target is considered for this projection. '
                    ),
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds3_adoption_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Max adoption, linear trend', 'include': True, 'maximum': ds4_constrained_tla,
                'description': (
                    'In this scenario, it is assumed that 100% of the grassland as per the TLA '
                    'will be protected by 2050 '
                    ),
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds4_adoption_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014, 'World'] = 132.860079407797
            df.loc[2015, 'World'] = 139.475887288368
            df.loc[2016, 'World'] = 146.114200458296
            df.loc[2017, 'World'] = 152.77501982823
            df.loc[2018, 'World'] = 159.457782791276

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
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            use_first_pds_datapoint_main=False,
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
            tot_red_in_deg_land=self.ua.cumulative_reduction_in_total_degraded_land(),
            pds_protected_deg_land=self.ua.pds_cumulative_degraded_land_protected(),
            ref_protected_deg_land=self.ua.ref_cumulative_degraded_land_protected(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)

