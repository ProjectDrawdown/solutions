"""Truck Fuel Efficiency solution model.
   Excel filename: TruckFuelEfficiency-RRS-v1.1c-22Oct19.xlsm
"""

import pathlib

import numpy as np
import pandas as pd
import xlrd

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
from model import unitadoption
from model import vma
from model import tam
from solution import rrs

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
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
        use_weight=False),
    'SOLUTION Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
        use_weight=False),
    'CONVENTIONAL Average Annual Use': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
        use_weight=False),
    'SOLUTION Average Annual Use': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
        use_weight=False),
    'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fuel_Consumed_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Fuel_Efficiency_Factor.csv"),
        use_weight=False),
    'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=None, use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'Average Utilization Rate (by Weight)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Utilization_Rate_by_Weight.csv"),
        use_weight=False),
    'Average Long Haul Truck Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Long_Haul_Truck_Capacity.csv"),
        use_weight=False),
    'Average Truck Lifetime': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Truck_Lifetime.csv"),
        use_weight=False),
    'Discount Rate: Commercial / Industry': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rate_Commercial_Industry.csv"),
        use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "Truck",
    "functional unit": "Mt-km",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Truck Fuel Efficiency'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

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

        # TAM
        tamconfig_list = [
            ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
            ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
            ['trend', '3rd Poly', '3rd Poly',
                '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
                '3rd Poly', '3rd Poly', '3rd Poly'],
            ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
                'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0],
            dtype=np.object).set_index('param')
        tam_ref_data_sources = {
              'Baseline Cases': {
                  'Based on: IEA ETP 2014 6DS': THISDIR.joinpath('tam', 'tam_based_on_IEA_ETP_2014_6DS.csv'),
            },
              'Conservative Cases': {
                  'Based on: IEA ETP 2014 4DS': THISDIR.joinpath('tam', 'tam_based_on_IEA_ETP_2014_4DS.csv'),
            },
              'Ambitious Cases': {
                  'Based on: IEA ETP 2014 2DS': THISDIR.joinpath('tam', 'tam_based_on_IEA_ETP_2014_2DS.csv'),
            },
        }
        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
            tam_pds_data_sources=tam_ref_data_sources)
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        # Custom PDS Data
        wb = xlrd.open_workbook(filename=THISDIR.joinpath('trucksdata.xlsx'))
        adoption1 = pd.read_excel(io=wb, sheet_name='AdoptionFactoring1', header=0, index_col=0,
                usecols='B:C', dtype='float', engine='xlrd', skiprows=11, nrows=51)
        adoption2 = pd.read_excel(io=wb, sheet_name='AdoptionFactoring2', header=0, index_col=0,
                usecols='B:H,J:M', dtype='float', engine='xlrd', skiprows=10, nrows=50)
        adoption3 = pd.read_excel(io=wb, sheet_name='AdoptionFactoring3', header=0, index_col=0,
                usecols='B:D', dtype='float', engine='xlrd', skiprows=9, nrows=51)

        ds1_df = pd.DataFrame(index=range(2012, 2061), columns=dd.REGIONS)
        ds1_df['World'] = adoption1.loc[2014:, 'Global']

        ds2_df = adoption2.loc[2012:2060].dropna(axis=0).rename(axis='columns', mapper={
            'Asia (sans Japan)': 'Asia (Sans Japan)',
            'Middle East & Africa': 'Middle East and Africa',
            'OECD': 'OECD90', 'EU27': 'EU'}).fillna(0.0)
        ds2_df.index = ds2_df.index.astype(int)

        ds3_df = pd.DataFrame(index=range(2012, 2061), columns=dd.REGIONS)
        ds3_df['World'] = adoption3['Adoption tonne-km']

        # Excel Custom PDS Adoption overrides these with real data
        for df in [ds1_df, ds2_df, ds3_df]:
            df.loc[2014, 'World'] = 304732.461811978
            df.loc[2015, 'World'] = 475099.277763475
            df.loc[2016, 'World'] = 660286.809851347
            df.loc[2017, 'World'] = 853343.225192547
            df.loc[2018, 'World'] = 1055789.45303526

        ca_pds_data_sources = [
            {'name': 'PDS1 - Based on ICCT+RMI Freight Work Adoption estimates', 'include': True,
                'description': (
                    'ICCT estimates the total freight work each five years, and RMI estimates '
                    'that by 2050 50% of trucks globally may have efficient technologies. We '
                    "therefore interpolate and extrapolate ICCT's freight work data and project "
                    'linear adoption globally from current adoption of truck freight work '
                    "(approximately 5%) to RMI's projection in 2050. "
                    ),
                'dataframe': ds1_df},
            {'name': 'PDS2 - Based on an ICCT Truck Sales extrapolation', 'include': True,
                'description': (
                    "We use the number of truck sales estimated for each of ICCT's 16 regions "
                    '(interpolated and extrapolated for each) to estimate the number of truck '
                    'with efficiency packages installed. ICCT has an estimate of the year when '
                    'truck fuel efficiency legislation becomes mandatory for each region. '
                    ),
                'dataframe': ds2_df},
            {'name': 'PDS3 - Based on IEA Freight Work - 100% Adoption of Trucks by 2035', 'include': True,
                'description': (
                    "IEA's estimated Truck freight work data are interpolated and extrapolated "
                    'and we apply an increasing fraction of adoption rising to 100% in 2050. '
                    ),
                'dataframe': ds3_df},
            {'name': 'Book Ed.1 Scenario 1', 'include': False,
                'description': (
                    'ICCT estimates the total freight work each five years, and RMI estimates '
                    'that by 2050 50% of trucks globally may have efficient technologies. We '
                    "therefore interpolate and extrapolate ICCT's freight work data and project "
                    'linear adoption globally from current adoption of truck freight work '
                    "(approximately 5%) to RMI's projection in 2050. "
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_1.csv')},
            {'name': 'Book Ed.1 Scenario 3', 'include': False,
                'description': (
                    'IEA"s estimated Truck freight work data are interpolated and extrapolated '
                    'and we apply an increasing fraction of adoption rising to 100% (of global '
                    'truck freight market only) in 2050. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_3.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': 'Drawdown Book Reference Scenario', 'include': True,
                'description': (
                    'This scenario uses the inputs that were used for the Scenario developed for '
                    'the Drawdown Book Edition 1. The scenario assumes a fixed percent of the '
                    'TAM is adopted for Efficient trucks as the TAM grows. '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Drawdown_Book_Reference_Scenario.csv')},
            {'name': 'Efficient Truck Share of Market is Fixed', 'include': True,
                'description': (
                    'Drawdown calculations for REF adoption of Efficient Trucks based on fixed '
                    'percent of growth of trucking. The 2014 - 2018 values are taken from '
                    'estimates of historical data '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Efficient_Truck_Share_of_Market_is_Fixed.csv')},
        ]
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=ref_tam_per_region)

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
            ref_tam_per_region.loc[2014])
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
            copy_pds_to_ref=True, copy_ref_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=3)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            repeated_cost_for_iunits=False,
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

