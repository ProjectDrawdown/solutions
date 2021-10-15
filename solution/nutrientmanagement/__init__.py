"""Nutrient Management solution model.
   Excel filename: Drawdown_RRS-BIOSEQ_Model_v1.1_MASTER_Nutrient_Management_Mar2020.truncated.xlsm
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

name = 'Nutrient Management'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-25p2050-Plauisble-PDScustom-agglowlineartrend-Mar2020"
PDS2 = "PDS-56p2050-Drawdown-PDScustom-avg-Mar2020"
PDS3 = "PDS-86p2050-Optimum-PDSCustom-high-Nov2019"

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


        # ADOPTION
        self._pds_ad_sources = scenario.load_sources(THISDIR/'ad'/'ad_sources.json', '*')

        ca_pds_columns = ['Year'] + dd.REGIONS
        adoption_2014 = self.ac.ref_base_adoption['World']
        tla_2050 = self.tla_per_region.loc[2050, 'World']
        area_N_eff_1990_1995 = 225.049083333333
        area_N_eff_1996_2000 = 89.7290333333333
        area_N_eff_2001_2005 = 42.7382
        area_N_eff_2006_2010 = 98.7301833333333

        ds1_o90_2050 = 0.46568375652467 * self.tla_per_region.loc[2050, 'OECD90']
        ds1_ee_2050 = 0.169344179047277 * self.tla_per_region.loc[2050, 'Eastern Europe']
        ds1_asj_2050 = 0.194261406995049 * self.tla_per_region.loc[2050, 'Asia (Sans Japan)']
        ds1_mea_2050 = 0.141859451675443 * self.tla_per_region.loc[2050, 'Middle East and Africa']
        ds1_la_2050 = 0.712235299292505 * self.tla_per_region.loc[2050, 'Latin America']
        ds1_world_2050 = ds1_o90_2050 + ds1_ee_2050 + ds1_asj_2050 + ds1_mea_2050 + ds1_la_2050

        ds2_o90_2050 = 0.791283756524669 * self.tla_per_region.loc[2050, 'OECD90']
        ds2_ee_2050 = 0.494944179047277 * self.tla_per_region.loc[2050, 'Eastern Europe']
        ds2_asj_2050 = 0.51986140699505 * self.tla_per_region.loc[2050, 'Asia (Sans Japan)']
        ds2_mea_2050 = 0.467459451675442 * self.tla_per_region.loc[2050, 'Middle East and Africa']
        ds2_la_2050 = 1.03783529929251 * self.tla_per_region.loc[2050, 'Latin America']
        ds2_world_2050 = ds2_o90_2050 + ds2_ee_2050 + ds2_asj_2050 + ds2_mea_2050 + ds2_la_2050

        ds3_o90_2050 = 1.0 * self.tla_per_region.loc[2050, 'OECD90']
        ds3_ee_2050 = 1.0 * self.tla_per_region.loc[2050, 'Eastern Europe']
        ds3_asj_2050 = 1.0 * self.tla_per_region.loc[2050, 'Asia (Sans Japan)']
        ds3_mea_2050 = 1.0 * self.tla_per_region.loc[2050, 'Middle East and Africa']
        ds3_la_2050 = 1.0 * self.tla_per_region.loc[2050, 'Latin America']
        ds3_world_2050 = ds3_o90_2050 + ds3_ee_2050 + ds3_asj_2050 + ds3_mea_2050 + ds3_la_2050

        ds_2018 = [self.ac.ref_base_adoption['World'], self.ac.ref_base_adoption['OECD90'],
                self.ac.ref_base_adoption['Eastern Europe'],
                self.ac.ref_base_adoption['Asia (Sans Japan)'],
                self.ac.ref_base_adoption['Middle East and Africa'],
                self.ac.ref_base_adoption['Latin America']]

        ca_pds_data_sources = [
            {'name': 'Aggressive-Low, Linear Trend', 'include': True,
             # The future adoption of nutrient management is build on the extent of the future
             # adoption of Conservation Agrculture (CA). Nutrient management is one of the
             # integral component of CA, thus, it is assumed that the adoption of nutrient
             # management will follow the similar trend of CA. This scenario projects the
             # future adoption of the solution based on the average annual future growth rate
             # of conservation agriculture.
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2050, ds1_world_2050, ds1_o90_2050, ds1_ee_2050, ds1_asj_2050, ds1_mea_2050,
                    ds1_la_2050, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Aggressive-High, Linear Trend', 'include': True,
             # The future adoption of nutrient management is build on the extent of the future
             # adoption of Conservation Agrculture (CA). Nutrient management is one of the integral
             # component of CA, thus, it is assumed that the adoption of nutrient management will
             # follow the similar trend of CA. This scenario projects the future adoption of the
             # solution based on the high annual future growth rate of conservation agriculture.
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2050, ds2_world_2050, ds2_o90_2050, ds2_ee_2050, ds2_asj_2050, ds2_mea_2050,
                    ds2_la_2050, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Aggressive-Max, Linear Trend', 'include': True,
             # This is an aggressive scenario assumes adoption of the solution in 100% of the TLA
             # by 2050 in all regions.
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2050, ds3_world_2050, ds3_o90_2050, ds3_ee_2050, ds3_asj_2050, ds3_mea_2050,
                    ds3_la_2050, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Aggressive-High, high early growth', 'include': False,
             # This scenario is assuming 60% of the total adoption will be achieved by 2030.
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2030, 0.6 * ds2_world_2050, 0.6 * ds2_o90_2050, 0.6 * ds2_ee_2050,
                    0.6 * ds2_asj_2050, 0.6 * ds2_mea_2050, 0.6 * ds2_la_2050, 0.0, 0.0, 0.0, 0.0],
                [2050, ds2_world_2050, ds2_o90_2050, ds2_ee_2050, ds2_asj_2050, ds2_mea_2050,
                    ds2_la_2050, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Aggressive-Low, high early growth', 'include': False,
             # "This is scenario 1, assuming 60% of the total adoption will be achieved by 2030.
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2030, 0.6 * ds1_world_2050, 0.6 * ds1_o90_2050, 0.6 * ds1_ee_2050,
                    0.6 * ds1_asj_2050, 0.6 * ds1_mea_2050, 0.6 * ds1_la_2050, 0.0, 0.0, 0.0, 0.0],
                [2050, ds1_world_2050, ds1_o90_2050, ds1_ee_2050, ds1_asj_2050, ds1_mea_2050,
                    ds1_la_2050, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Lassaletta et al 2014, conservative growth', 'include': True,
             # Future adoption is projected based on the maximum global area reported under
             # Nitrogen Use Efficiency in the past by Lassaletta et al 2014. 
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2050, area_N_eff_1990_1995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Lassaletta et al 2014, moderate growth', 'include': True,
             # Future adoption is projected based on the maximum global area reported under
             # Nitrogen Use Efficiency in the past by Lassaletta et al 2014. 
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2050, 2 * area_N_eff_1990_1995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Lassaletta et al 2014, high growth', 'include': True,
             # Future adoption is projected based on the maximum global area reported under
             # Nitrogen Use Efficiency in the past by Lassaletta et al 2014. 
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2050, 4 * area_N_eff_1990_1995, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},

            {'name': 'Sutton et al 2013, linear trend', 'include': True,
             # Future adoption is projected based on the projected global area under
             # Nitrogen Use Efficiency by 2020 by Sutton et al 2013. 
             'datapoints': pd.DataFrame([
                [2018] + ds_2018 + [0.0, 0.0, 0.0, 0.0],
                [2020, 335.92674, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        # Manual adjustment made in spreadsheet for Drawdown 2020.
        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2012:2018, 'World'] = 139.129613374975

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
        ht_pds_datapoints.loc[2018] = ht_pds_adoption_initial
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