"""SRI solution model.
   Excel filename: Drawdown_RRS-BIOSEQAgri_Model_v1.1_SRI_Mar2020.xlsm
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

name = 'SRI'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-77p2050-Plausible-customPDS-avg-Jan2020"
PDS2 = "PDS-100p2050-Drawdown-customPDS-high-Jan2020"
PDS3 = "PDS-100p2050-Optimum-CustomPDS-highearly-Jan2020"

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
        tla_world_2050 = self.tla_per_region.loc[2050, 'World']
        irin_sri_adopt_fname = THISDIR.joinpath('ca_pds_data', 'IRIN_SRI_Adoption.csv')
        irin_sri_adopt = pd.read_csv(str(irin_sri_adopt_fname), header=0, comment='#',
                skipinitialspace=True, skip_blank_lines=True, dtype=np.float64)
        irin_avg = irin_sri_adopt.mean().mean()
        irin_high = irin_sri_adopt.max().max()
        irin_mid = (irin_avg + irin_high) / 2.0

        ca_pds_data_sources = [
            {'name': 'Average, Linear Trend', 'include': True, 'maximum': tla_world_2050,
                'description': (
                    'The future area under SRI is projected based on the adoption projections '
                    'given for China, India, and Indonesia by IRIN. The data interpolator was '
                    'used to extrapolate the data and the average and high adoption value for '
                    'the year 2050 is summarized in the given assumptions. This scenario assumes '
                    'that the area will increase by average growth. '
                    ),
                'datapoints': pd.DataFrame([
                    [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, irin_avg, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High, Linear Trend', 'include': False, 'maximum': tla_world_2050,
                'description': (
                    'The future area under SRI is projected based on the adoption projections '
                    'given for China, India, and Indonesia by IRIN. The data interpolator was '
                    'used to extrapolate the data and the average and high adoption value for '
                    'the year 2050 is summarized in the given assumptions. This scenario assumes '
                    'that the area will increase by maximum growth. '
                    ),
                'datapoints': pd.DataFrame([
                    [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, irin_high, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Average, Linear Trend, Early Growth', 'include': False,
                'maximum': tla_world_2050,
                'description': (
                    'This is scenario 1 with 100% adoption by 2030 '
                    ),
                'datapoints': pd.DataFrame([
                    [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2030, irin_avg, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, irin_avg, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High, Linear Trend, Early Growth', 'include': False,
                'description': (
                    'This is scenario 2 with 100% adoption by 2030 '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2030, irin_high, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, irin_high, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium, Linear Trend', 'include': False,
                'description': (
                    ' The future area under SRI is projected based on the adoption projections '
                    'given for China, India, and Indonesia by IRIN. The data interpolator was '
                    'used to extrapolate the data and the average and high adoption value for '
                    'the year 2050 is summarized in the given assumptions. This scenario assumes '
                    'that the area will increase by average growth based on assumption 1 and 2. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, irin_mid, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium, Linear Trend, Early Growth', 'include': False,
                'description': (
                    'This is scenario 5 with 100% adoption by 2030 '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2030, irin_mid, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, irin_mid, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'World Adoption, linear trend', 'include': False,
                'description': (
                    'The future growth is projected based on the world adoption of SRI in 2013 '
                    'and 2018, based on the information received from personal communication '
                    'through Prof. Norman Uphoff, Cornell University '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2013, 3.5, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2018, 6.7, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2012, 'World'] = 2.86
            df.loc[2013, 'World'] = 3.5
            df.loc[2014, 'World'] = 4.15259261268174
            df.loc[2015, 'World'] = 4.79610333421305
            df.loc[2016, 'World'] = 5.44024605689438
            df.loc[2017, 'World'] = 6.08503665221758
            df.loc[2018, 'World'] = 6.73044601473859

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

        copy_pds_to_ref = (len(self.ac.pds_adoption_use_ref_years) == 0)

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
            copy_pds_to_ref=copy_pds_to_ref,
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