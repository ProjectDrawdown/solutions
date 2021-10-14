"""Car Fuel Efficiency solution model.
   Excel filename: HybridCars-RRSv1.1b-Nov2019.xlsm
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
from model import interpolation
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
    "implementation unit": "Car",
    "functional unit": "passenger-km",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Car Fuel Efficiency'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-11p2050-using IEA 2DS (Integrated)"
PDS2 = "PDS2-4p2050-Transition to EV's (Integrated)"
PDS3 = "PDS3-1p2050-Transition to EV's (Integrated)"

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
        self._pds_ca_sources = scenario.load_sources(THISDIR/'ca_pds_data'/'ca_pds_sources.json', 'filename')
        self._pds_ad_sources = scenario.load_sources(THISDIR/'ad'/'ad_sources.json', '*')

        wb = openpyxl.load_workbook(filename=THISDIR.joinpath('hybridcarsdata.xlsx'), data_only=True)
        raw_sales = pd.read_excel(wb, sheet_name='HEV Sales', header=0, index_col=0,
                usecols='A:K', dtype='float', engine='openpyxl', skiprows=7, nrows=43)
        hev_sales = raw_sales.rename(axis='columns', mapper={
            'World ': 'World',
            'OECD90 (US, EU Japan, Canada)': 'OECD90',
            'Asia sans Japan (China, India & Other.)': 'Asia (Sans Japan)',
            'Middle East & Africa': 'Middle East and Africa'}).fillna(0.0)
        lifetime = int(np.ceil(self.ac.soln_lifetime_replacement))
        sales_extended = hev_sales.copy()
        for year in range(2019, 2061):
            sales_extended.loc[year, :] = 0.0
        vehicle_retirements = sales_extended.shift(periods=lifetime, fill_value=0.0)
        hev_stock = (hev_sales - vehicle_retirements).cumsum()
        pass_km_adoption = hev_stock * self.ac.soln_avg_annual_use

        # HybridCars.xlsm 'Data Interpolator'!H1582, Adoption Data
        # Project Drawdown Analysis based on Market Reports and a Drop in HEV
        # in later years (replaced by EVs) - PDS2
        predict = pd.read_csv(
                THISDIR.joinpath('ca_pds_data', 'pass_km_datapoints_PDS2.csv'),
                skipinitialspace=True, comment='#', index_col=0, squeeze=True)
        pass_km_predicted = interpolation.poly_degree3_trend(predict)['adoption']
        pass_km_predicted.update(predict.loc[:2018])  # Early years adjusted to be actual values
        integration_pds2 = pd.read_csv(THISDIR.joinpath('tam', 'integration_PDS2.csv'),
                skipinitialspace=True, comment='#', index_col=0)
        tam_limit_pds2 = 0.95 * (integration_pds2['URBAN'] + integration_pds2['NONURBAN']) * 1e9
        world = pd.concat([pass_km_adoption.loc[2012:2016, 'World'], pass_km_predicted.loc[2017:]])
        ds1_df = pd.DataFrame(0, columns=dd.REGIONS, index=range(2012, 2061))
        ds1_df['World'] = world.clip(upper=tam_limit_pds2, lower=0.0, axis=0)

        # Data Source 2
        predict = pd.read_csv(
                THISDIR.joinpath('ca_pds_data', 'pass_km_datapoints_PDS3.csv'),
                skipinitialspace=True, comment='#', index_col=0, squeeze=True)
        pass_km_predicted = interpolation.poly_degree3_trend(predict)['adoption']
        pass_km_predicted.update(predict.loc[:2018])  # Early years adjusted to be actual values
        integration_pds3 = pd.read_csv(THISDIR.joinpath('tam', 'integration_PDS3.csv'),
                skipinitialspace=True, comment='#', index_col=0)
        intg_limit = (integration_pds3['URBAN'] + integration_pds3['NONURBAN']) * 1e9
        tam_limit_pds3 = pd.concat([(intg_limit.loc[:2035] * 0.95), (intg_limit.loc[2036:] * 0.9)])
        world = pd.concat([pass_km_adoption.loc[2012:2016, 'World'], pass_km_predicted.loc[2017:]])
        ds2_df = pd.DataFrame(0, columns=dd.REGIONS, index=range(2012, 2061))
        ds2_df['World'] = world.clip(upper=tam_limit_pds3, lower=0.0, axis=0)

        # #BEGIN COMMENT BLOCK
        ca_pds_data_sources = scenario.load_sources(THISDIR/'ca_pds_data'/'ca_pds_sources.json', 'filename')
        ca_pds_data_sources[0]['dataframe'] = ds1_df
        ca_pds_data_sources[1]['dataframe'] = ds2_df
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

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
            use_first_pds_datapoint_main=False,
            copy_pds_to_ref=False,
            copy_ref_datapoint=False, copy_pds_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=3)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
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