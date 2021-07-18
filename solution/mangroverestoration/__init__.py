"""Mangrove Protection solution model.
   Excel filename: Drawdown_RRS-BIOSEQProtect_Model_v1.1b_Coastal_Wetlands(Mangroves)_Mar2020.xlsm
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
        filename=None, use_weight=False),
    't CO2 Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_CO2_Reduced_per_Land_Unit.csv"),
        use_weight=False),
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
    'Total Available Land': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Total_Available_Land.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Mangrove Protection'
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
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'Constant degradation rate, 100% adoption by 2050, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 100% of the '
                    'remaining wetlands in 2050 were protected.  This adoption is less than 100% '
                    'of the wetlands in 2014. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Constant_degradation_rate_100_adoption_by_2050_linear.csv')},
            {'name': 'Constant degradation rate, 80% adoption by 2050, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 80% of the '
                    'remaining wetlands in 2050 were protected.  This is the same as Scenario 1 '
                    'except for a smaller percentage protected by 2050. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Constant_degradation_rate_80_adoption_by_2050_linear.csv')},
            {'name': 'Constant degradation rate, 100% adoption by 2030, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 100% of the '
                    'remaining wetlands in 2030 were protected.  Because there is 100% '
                    'protection in 2030, all values after that are constant. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Constant_degradation_rate_100_adoption_by_2030_linear.csv')},
            {'name': 'Constant degradation rate, 80% adoption by 2030, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 80% of the '
                    'remaining wetlands in 2030 were protected.  Because there is only 80% '
                    'protection in 2030 linear interpolation was used to bridge the 2014, 2030, '
                    'and 2050 values. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Constant_degradation_rate_80_adoption_by_2030_linear.csv')},
            {'name': 'Variable degradation rate, 100% adoption by 2050, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 100% of the '
                    'remaining wetlands in 2050 were protected.  This adoption is less than 100% '
                    'of the wetlands in 2014.  This is the same as Scenario 1 except an annual '
                    'reduction in degradation rate is applied. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Variable_degradation_rate_100_adoption_by_2050_linear.csv')},
            {'name': 'Variable degradation rate, 80% adoption by 2050, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 80% of the '
                    'remaining wetlands in 2050 were protected.  This is the same as Scenario 5 '
                    'except for a smaller percentage protected by 2050. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Variable_degradation_rate_80_adoption_by_2050_linear.csv')},
            {'name': 'Variable degradation rate, 100% adoption by 2030, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 100% of the '
                    'remaining wetlands in 2030 were protected.  Because there is 100% '
                    'protection in 2030, all values after that are constant. This is the same as '
                    'Scenario 3 except a variable degradation rate is used. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Variable_degradation_rate_100_adoption_by_2030_linear.csv')},
            {'name': 'Variable degradation rate, 80% adoption by 2030, linear', 'include': True,
                'description': (
                    'The TLA_Envelope sheet was used to compute the annual degradation of the '
                    'wetland.  The annual protection rate was adjusted so that 80% of the '
                    'remaining wetlands in 2030 were protected.  Because there is only 80% '
                    'protection in 2030 linear interpolation was used to bridge the 2014, 2030, '
                    'and 2050 values.  This scenario is the same as Scenario 4 except a variable '
                    'degradation rate is used. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Variable_degradation_rate_80_adoption_by_2030_linear.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

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
            tot_red_in_deg_land=self.ua.cumulative_reduction_in_total_degraded_land(),
            pds_protected_deg_land=self.ua.pds_cumulative_degraded_land_protected(),
            ref_protected_deg_land=self.ua.ref_cumulative_degraded_land_protected(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)

