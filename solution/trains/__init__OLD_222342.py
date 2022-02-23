"""Train Fuel Efficiency solution model.
   Excel filename: TrainFE-RRSv1.1b_23Oct19.xlsm
"""

import pathlib

import numpy as np
import pandas as pd
import openpyxl

from model import adoptiondata
from model import advanced_controls as ac
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
from model import tam
from solution import rrs

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = vma.VMA.load_vma_directory(THISDIR/'vma_data/vma_sources.json')

units = {
    "implementation unit": "km of track converted",
    "functional unit": "Mt-km",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Train Fuel Efficiency'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-5p2050-with UIC Electrification Rate"
PDS2 = "PDS2-8p2050-with IEA 2DS"
PDS3 = "PDS3-9p2050-Complete Electrification"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TAM
        self._ref_tam_sources = scenario.load_sources(THISDIR/'tam'/'tam_ref_sources.json','*')
        self._pds_tam_sources = self._ref_tam_sources
        self.set_tam()
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        # ADOPTION
        self._ref_ca_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')

        wb = openpyxl.load_workbook(filename=THISDIR.joinpath('trainsdata.xlsx'), data_only=True)
        adoption1 = pd.read_excel(wb, sheet_name='Adoption1', header=0, index_col=0,
                usecols='A:C', dtype='float', engine='openpyxl', skiprows=12, nrows=47)
        adoption2 = pd.read_excel(wb, sheet_name='Adoption2', header=0, index_col=0,
                usecols='A:B', dtype='float', engine='openpyxl', skiprows=12, nrows=47)
        adoption3 = pd.read_excel(wb, sheet_name='Adoption3', header=0, index_col=0,
                usecols='A:C', dtype='float', engine='openpyxl', skiprows=12, nrows=47)

        ds1_df = pd.DataFrame(index=range(2012, 2061), columns=dd.REGIONS)
        ds1_df['World'] = adoption2['Electrified Freight million tonne-km']

        ds2_df = pd.DataFrame(index=range(2012, 2061), columns=dd.REGIONS)
        ds2_df['World'] = adoption1['Electrified']

        ds3_df = pd.DataFrame(index=range(2012, 2061), columns=dd.REGIONS)
        ds3_df['World'] = adoption3['Electrified']

        ca_pds_data_sources = [
            {'name': 'PDS2 - Doubling of Historical Electrification Rate (UIC data)', 'include': True,
                'description': (
                    'Electrified railway tkms increase at TWICE the historical average annual '
                    'rate of track electrification. Using UIC data, we estimate the average '
                    'electrification rate at 1.4% annually. We double this and use this rate as '
                    'the optimistically plausible electrification rate. This is reasonable since '
                    "it still remains below the annual rate of many year's growth according to "
                    'UIC data below. This may come from increased track length and uniform '
                    'usage, or higher usage of electrified tracks versus other tracks. '
                    ),
                'dataframe': ds1_df},
            {'name': 'PDS1 - Linear projection of Electricity-powered rail freight from 27% of rail freight in 2014 to 40% in 2050 (IEA 2DS projection)', 'include': True,
                'description': (
                    'UIC data for 2014 indicates 27% electrification of rails. The IEA 2DS '
                    'scenario projects that 40% of rail freight can be powered by electricity by '
                    '2050. We linearly interpolate between these two percentages. We also use an '
                    'annual average use rate that is 25% higher for the electrified tracks than '
                    'the conventional. '
                    ),
                'dataframe': ds2_df},
            {'name': 'PDS3 - Linear projection of Electricity-powered rail freight from 27% of rail freight in 2014 to 100% in 2050', 'include': True,
                'description': (
                    'UIC data for 2014 indicates 27% electrification of rails. The IEA 2DS '
                    'scenario projects that 40% of rail freight can be powered by electricity by '
                    '2050. We examine the impact of making this target 100% in 2050 by linearly '
                    'interpolating between these two percentages. We also assume a doubling of '
                    'the electrified track usage versus the conventional. '
                    ),
                'dataframe': ds3_df},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        self.initialize_adoption_bases()
        ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

        if False:
            # One may wonder why this is here. This file was code generated.
            # This 'if False' allows subsequent conditions to all be elif.
            pass
        elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
            pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
            pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
            pds_adoption_is_single_source = None

        ht_ref_adoption_initial = pd.Series(
            list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial /
            ref_tam_per_region.loc[2018])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2018] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            copy_pds_world_too=False,
            copy_pds_to_ref=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=3)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
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
            fc_convert_iunit_factor=1.0)

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
            conversion_factor=1.0)

        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
            soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
            soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),
            soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
            conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            fuel_in_liters=False)

        self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],
            soln_avg_annual_use=self.ac.soln_avg_annual_use,
            conv_avg_annual_use=self.ac.conv_avg_annual_use)