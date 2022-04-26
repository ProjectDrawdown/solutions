"""Improved Rice solution model.
   Excel filename: Drawdown_RRS-BIOSEQAgri_Model_v1.1_Improved Rice_Mar2020.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import aez
from model import ch4calcs
from model import co2calcs
from model import n2ocalcs
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
VMAs = vma.VMA.load_vma_directory(THISDIR/'vma_data/vma_sources.json')

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Improved Rice'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-84p2050-Plausible-customPDS-avg-Jan2020"
PDS2 = "PDS-100p2050-Drawdown-customPDS-high-Jan2020"
PDS3 = "PDS-100p2050-Optimum-PDSCustom-highearly-Nov2019"

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
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

        # ADOPTION
        self._ref_ca_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')
        self._pds_ad_sources = scenario.load_sources(THISDIR/'ad'/'ad_sources.json', '*')

        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_2050 = self.tla_per_region.loc[2050, 'World']
        ad_2018 = self.ac.ref_base_adoption['World']

        # 2050 adoption based on Project Drawdown 2018 Direct Seeded
        # Rice Area (2nd order Polynomial Growth); Refer "Adoption Data" sheet
        ad_2050_2ndpoly = 69.9380489958066000

        # 2050 adoption based on Project Drawdown 2018_Rice Area under water
        # management (Linear Growth); Refer "Adoption Data" sheet
        ad_2050_linear = 170.3736841446970000

        # 2050 adoption based on Project Drawdown 2018_Rice Area under water
        # management (Linear Growth, divided by 2); Refer "Adoption Data" sheet
        ad_2050_linear_half = 85.1868420723484000

        ad_2050_avg = (ad_2050_2ndpoly + ad_2050_linear + ad_2050_linear_half) / 3.0
        ad_2050_min = min([ad_2050_2ndpoly, ad_2050_linear, ad_2050_linear_half])
        ad_2050_max = max([ad_2050_2ndpoly, ad_2050_linear, ad_2050_linear_half])

        ca_pds_data_sources = [
            {'name': 'Medium Growth', 'include': True,
                'description': (
                    'Future adoption of improved rice cultivation is projected based on the '
                    'historical growth rate of direct seeded rice and water management available '
                    'in the literature (refer "Current Adoption_LR" sheet). The historical data '
                    'was interpolated, a 2nd order polynomial growth was considered for direct '
                    'seeded rice data and linear growth for the water management, The '
                    'interpolated data is then placed in the "adoption data" sheet. The future '
                    'adoption in the present scenario is based on the "average adoption value '
                    'projected for the year 2050" based on the given data set. '
                    ),
             'datapoints': pd.DataFrame([
                [2018, ad_2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2050, ad_2050_avg, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Low Growth', 'include': True,
                'description': (
                    'Future adoption of improved rice cultivation is projected based on the '
                    'historical growth rate of direct seeded rice and water management available '
                    'in the literature (refer "Current Adoption_LR" sheet). The historical data '
                    'was interpolated, a 2nd order polynomial growth was considered for direct '
                    'seeded rice data and linear growth for the water management, The '
                    'interpolated data is then placed in the "adoption data" sheet. The future '
                    'adoption in the present scenario is based on the "minimum adoption value '
                    'projected for the year 2050" based on the given data set. '
                    ),
             'datapoints': pd.DataFrame([
                [2018, ad_2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2050, ad_2050_min, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High Growth', 'include': True,
                'description': (
                    'Future adoption of improved rice cultivation is projected based on the '
                    'historical growth rate of direct seeded rice and water management available '
                    'in the literature (refer "Current Adoption_LR" sheet). The historical data '
                    'was interpolated, a 2nd order polynomial growth was considered for direct '
                    'seeded rice data and linear growth for the water management, The '
                    'interpolated data is then placed in the "adoption data" sheet. The future '
                    'adoption in the present scenario is based on the "maximum adoption value '
                    'projected for the year 2050" based on the given data set. '
                    ),
             'datapoints': pd.DataFrame([
                [2018, ad_2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2050, ad_2050_max, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium Growth, Early Adoption', 'include': True,
                'description': (
                    'Future adoption of improved rice cultivation is projected based on the '
                    'historical growth rate of direct seeded rice and water management available '
                    'in the literature (refer "Current Adoption_LR" sheet). The historical data '
                    'was interpolated, a 2nd order polynomial growth was considered for direct '
                    'seeded rice data and linear growth for the water management, The '
                    'interpolated data is then placed in the "adoption data" sheet. The future '
                    'adoption in the present scenario is based on the "average adoption value '
                    'projected for the year 2050" based on the given data set. In addition, it '
                    'is also assumed that 75% of the projected adoption for the year 2050 will '
                    'be achieved by 2030. '
                    ),
             'datapoints': pd.DataFrame([
                [2018, ad_2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2030, 0.75 * ad_2050_avg, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2050, ad_2050_avg, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Low Growth, Early Adoption', 'include': True,
                'description': (
                    'Future adoption of improved rice cultivation is projected based on the '
                    'historical growth rate of direct seeded rice and water management available '
                    'in the literature (refer "Current Adoption_LR" sheet). The historical data '
                    'was interpolated, a 2nd order polynomial growth was considered for direct '
                    'seeded rice data and linear growth for the water management, The '
                    'interpolated data is then placed in the "adoption data" sheet. The future '
                    'adoption in the present scenario is based on the "minimum adoption value '
                    'projected for the year 2050" based on the given data set. In addition, it '
                    'is also assumed that 75% of the projected adoption for the year 2050 will '
                    'be achieved by 2030. '
                    ),
             'datapoints': pd.DataFrame([
                [2018, ad_2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2030, 0.75 * ad_2050_min, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2050, ad_2050_min, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High Growth, Early Adoption', 'include': False,
                'description': (
                    'Future adoption of improved rice cultivation is projected based on the '
                    'historical growth rate of direct seeded rice and water management available '
                    'in the literature (refer "Current Adoption_LR" sheet). The historical data '
                    'was interpolated, a 2nd order polynomial growth was considered for direct '
                    'seeded rice data and linear growth for the water management, The '
                    'interpolated data is then placed in the "adoption data" sheet. The future '
                    'adoption in the present scenario is based on the "maximum adoption value '
                    'projected for the year 2050" based on the given data set. In addition, it '
                    'is also assumed that 75% of the projected adoption for the year 2050 will '
                    'be achieved by 2030. '
                    ),
             'datapoints': pd.DataFrame([
                [2018, ad_2018, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2030, 0.75 * ad_2050_max, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [2050, ad_2050_max, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014, 'World'] = 31.2753335238409000
            df.loc[2015, 'World'] = 33.6257358946259000
            df.loc[2016, 'World'] = 35.9761382654110000
            df.loc[2017, 'World'] = 38.3265406361960000
            df.loc[2018, 'World'] = 40.6769430069810000


        self.initialize_adoption_bases()
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
            copy_pds_world_too=False,
            copy_through_year=2018,
            copy_pds_to_ref=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=1)

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

        self.n2o = n2ocalcs.N2OCalcs(ac=self.ac,
            soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)


        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            ch4_megatons_avoided_or_reduced=self.c4.ch4_megatons_avoided_or_reduced(),
            n2o_megatons_avoided_or_reduced=self.n2o.n2o_megatons_avoided_or_reduced(),
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
