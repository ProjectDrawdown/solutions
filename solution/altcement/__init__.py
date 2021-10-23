"""Alternative Cements solution model.
   Excel filename: AlternativeCements_v1.1c_IntegrationJune2020.xlsm
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
    "implementation unit": "MMt",
    "functional unit": "MMt Cement",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Alternative Cements'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-100p2050-0.6Clinker/Cement-postintJune2020"
PDS2 = "PDS2-100p2050-0.46clinker/cement-postintjune2020"
PDS3 = "PDS-100p2050-0.27clinker/cement-postintjune2020"

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


        # Custom PDS Data
        wb = openpyxl.load_workbook(filename=THISDIR.joinpath('data.xlsx'), data_only=True, keep_links=False)
        def isint(x):
            try:
                int(x)
                return True
            except ValueError:
                return False
        def demangle(name):
            # Pandas tries to be helpful by mangling duplicate column names, so the first
            # read_excel returns 'Latin America' and the second 'Latin America.1'
            if not '.' in name:
                return name
            new, suffix = name.rsplit('.', 1)
            return new if isint(suffix) else name
        clinker_pct = self.ac.lookup_vma(vma_title='Clinker to Cement Ratio in Year 2')

        # Data Source 1
        #breakpoint()
        hvfac_mmt_pds1 = pd.read_excel(wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='B:L', dtype='float', engine='openpyxl', skiprows=62, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_pds1.index.name = 'Year'
        hvfac_mmt_pds1.loc[2014] = 0.0
        ds1_df = hvfac_mmt_pds1.sort_index() / clinker_pct

        # Data Source 2
        hvfac_mmt_pds2 = pd.read_excel(wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='O:Y', dtype='float', engine='openpyxl', skiprows=62, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_pds2.index.name = 'Year'
        hvfac_mmt_pds2.loc[2014] = 0.0
        ds2_df = hvfac_mmt_pds2.sort_index() / clinker_pct

        # Data Source 3
        hvfac_mmt_pds3 = pd.read_excel(wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='AB:AL', dtype='float', engine='openpyxl', skiprows=62, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_pds3.index.name = 'Year'
        hvfac_mmt_pds3.loc[2014] = 0.0
        ds3_df = hvfac_mmt_pds3.sort_index() / clinker_pct

        # Data Source 4
        filename_ds4 = THISDIR.joinpath('ca_pds_data', 'pds_adoption_scenario_4.csv')
        book_mmt = pd.read_csv(filename_ds4, header=0, index_col=0, skipinitialspace=True,
                         skip_blank_lines=True, comment='#', dtype=np.float64)
        book_mmt.index = book_mmt.index.astype(int)
        ds4_df = book_mmt / clinker_pct

        ca_pds_data_sources = scenario.load_sources(THISDIR/'ca_pds_data'/'ca_pds_sources.json', 'filename')
        ca_pds_data_sources[0]['dataframe'] = ds1_df
        ca_pds_data_sources[1]['dataframe'] = ds2_df
        ca_pds_data_sources[2]['dataframe'] = ds3_df
        ca_pds_data_sources[3]['dataframe'] = ds4_df
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        # Data Source 1
        hvfac_mmt_ref = pd.read_excel(io=wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='B:L', dtype='float', engine='openpyxl', skiprows=113, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_ref.index.name = 'Year'
        hvfac_mmt_ref.loc[2014] = 0.0
        ref1_df = hvfac_mmt_ref.sort_index() / clinker_pct

        # Data Source 2
        filename_ref2 = THISDIR.joinpath('ca_ref_data', 'ref_adoption_scenario_2.csv')
        book_ref_mmt = pd.read_csv(filename_ref2, header=0, index_col=0, skipinitialspace=True,
                         skip_blank_lines=True, comment='#', dtype=np.float64)
        book_ref_mmt.index = book_ref_mmt.index.astype(int)
        ref2_df = book_ref_mmt / clinker_pct

        ca_ref_data_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')
        ca_ref_data_sources[0]['dataframe'] = ref1_df
        ca_ref_data_sources[1]['dataframe'] = ref2_df
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=ref_tam_per_region)

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
        elif self.ac.soln_pds_adoption_basis == 'Linear':
            pds_adoption_data_per_region = None
            pds_adoption_trend_per_region = None
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
            copy_pds_to_ref=False, copy_ref_datapoint=False, copy_pds_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=4)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            repeated_cost_for_iunits=True,
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