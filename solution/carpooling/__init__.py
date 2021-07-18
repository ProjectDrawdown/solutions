"""Ridesharing & Carpooling solution model.
   Excel filename: Carpool-RRSv1.1b-Jan2020.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

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
VMAs = {
    'Current Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
        use_weight=True),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=False),
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
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'Average Ridesharing Car Occupancy': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Ridesharing_Car_Occupancy.csv"),
        use_weight=True),
    'Average Car Lifetime': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Car_Lifetime.csv"),
        use_weight=False),
    'Discount Rates - Households': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rates_Households.csv"),
        use_weight=False),
    'Current Average Car Occupancy': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Average_Car_Occupancy.csv"),
        use_weight=True),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "trip",
    "functional unit": "passenger-km",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Ridesharing & Carpooling'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

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
        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
        tam_ref_data_sources = {
              'Baseline Cases': {
                  'Based on ETP 2016, URBAN 6 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ETP_2016_URBAN_6_DS_Nonmotorized_Travel_Adjustment.csv'),
                  'Based on ICCT, 2012, "Global Transportation Roadmap Model" + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ICCT_2012_Global_Transportation_Roadmap_Model_Nonmotorized_Travel_Adjustment.csv'),
            },
              'Conservative Cases': {
                  'Based on ETP 2016, URBAN 4 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ETP_2016_URBAN_4_DS_Nonmotorized_Travel_Adjustment.csv'),
                  'Based on ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - Baseline Scenario': THISDIR.joinpath('tam', 'tam_based_on_ITDPUC_Davis_2014_A_Global_High_Shift_Scenario_Updated_Report_Data_Baseline_Scenario.csv'),
            },
              'Ambitious Cases': {
                  'Based on ETP 2016, URBAN 2 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ETP_2016_URBAN_2_DS_Nonmotorized_Travel_Adjustment.csv'),
                  'Based on ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - HighShift Scenario': THISDIR.joinpath('tam', 'tam_based_on_ITDPUC_Davis_2014_A_Global_High_Shift_Scenario_Updated_Report_Data_HighShift_Scenario.csv'),
            },
        }
        tam_pds_data_sources = {
            'Ambitious Cases': {
                    'Drawdown TAM: Integrated Urban TAM post Non-Car Solutions for PDS1': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Integrated_Urban_TAM_post_NonCar_Solutions_for_PDS1.csv'),
                    'Drawdown TAM: Integrated Urban TAM post Non-Car Solutions for PDS2': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Integrated_Urban_TAM_post_NonCar_Solutions_for_PDS2.csv'),
            },
            'Maximum Cases': {
                    'Drawdown TAM: Integrated Urban TAM post Non-Car Solutions for PDS3': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Integrated_Urban_TAM_post_NonCar_Solutions_for_PDS3.csv'),
            },
        }
        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
            tam_pds_data_sources=tam_pds_data_sources)
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        adconfig_list = [
            ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
             'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['trend', self.ac.soln_pds_adoption_prognostication_trend, '3rd Poly',
             '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
             '3rd Poly', '3rd Poly', '3rd Poly'],
            ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'Medium',
             'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
             'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        car_occ = self.ac.lookup_vma(vma_title='Current Average Car Occupancy')
        ride_occ = self.ac.lookup_vma(vma_title='Average Ridesharing Car Occupancy')
        ad_2018 = (car_occ - 1) / (ride_occ - 1)

        def global_load_df(ad_2018, ad_2050):
            """Compute increasing car occupancy over time as a percentage of TAM."""
            occ = pd.DataFrame(columns=dd.REGIONS, dtype='float')
            coeff = np.polyfit(x=[2018, 2050], y=[ad_2018, ad_2050], deg=1)
            for year in range(2017, 2011, -1):
                occ.loc[year, 'World'] = np.polyval(p=coeff, x=year)
            for year in range(2018, 2061):
                occ.loc[year, 'World'] = np.polyval(p=coeff, x=year)
            df = occ.fillna(0.0) * pds_tam_per_region
            # Hard-coded values in Excel for these years.
            df.loc[2014, 'World'] = 3146198294784.37
            df.loc[2015, 'World'] = 3237108104808.58
            df.loc[2016, 'World'] = 3330046150206.16
            df.loc[2017, 'World'] = 3422733823378.58
            df.loc[2018, 'World'] = 3515221717452.8
            return df

        ds4_ad_2050 = (1.75 - 1) / (ride_occ - 1)
        ds4_df = global_load_df(ad_2018=ad_2018, ad_2050=ds4_ad_2050)
        ds5_ad_2050 = (2.0 - 1) / (ride_occ - 1)
        ds5_df = global_load_df(ad_2018=ad_2018, ad_2050=ds5_ad_2050)
        ds6_ad_2050 = (3.0 - 1) / (ride_occ - 1)
        ds6_df = global_load_df(ad_2018=ad_2018, ad_2050=ds6_ad_2050)

        ca_pds_data_sources = [
            {'name': 'PDS1 (15%) - Drawdown Book Edition 1', 'include': True,
                'description': (
                    'PDS1 - Drawdown Team Calculations based on: 15% adoption by Car commuters '
                    'in 2050 '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_15_Drawdown_Book_Edition_1.csv')},
            {'name': 'PDS2 (20%) - Drawdown Book Edition 1', 'include': True,
                'description': (
                    'PDS2 - Drawdown Team Calculations based on: 20% adoption by Car commuters '
                    'in 2050 '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_20_Drawdown_Book_Edition_1.csv')},
            {'name': 'PDS3 (30%) - Drawdown Book Edition 1', 'include': True,
                'description': (
                    'PDS3 -  Drawdown Team Calculations based on: 30% adoption by Car commuters '
                    'in 2050 '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS3_30_Drawdown_Book_Edition_1.csv')},
            {'name': 'PDS1 - With Global Load Factor of 1.75 person per vehicle per trip by 2050', 'include': True,
                'description': (
                    'We take a relatively high average car load factor from data from several '
                    'countries and assume that it can be the 2050 global average load factor. We '
                    'assume that that figure is out of a maximum as entered on Advanced Controls '
                    '(~3 persons per trip) and estimate what effective adoption share the target '
                    'load factor represents (assuming that all trips are either single occupancy '
                    'or the maximum entered. This load factor in 2050 and that in 2014 (current '
                    'value) are interpolated to get the load factor each year which is used to '
                    'estimate the adoption. Recent Historical adoptions were estimated by '
                    'assuming that the average load factors calculated from the weighted '
                    'available data are applied to the total urban mobility each year after '
                    'applying the car mode share (assumed fixed) '
                    ),
                'dataframe': ds4_df},
            {'name': 'PDS2 - With Global Load Factor of 2 person per vehicle per trip by 2050', 'include': True,
                'description': (
                    'We take a relatively high average car load factor from data from several '
                    'countries and assume that it can be the 2050 global average load factor. We '
                    'assume that that figure is out of a maximum as entered on Advanced Controls '
                    '(~3 persons per trip) and estimate what effective adoption share the target '
                    'load factor represents (assuming that all trips are either single occupancy '
                    'or the maximum entered. This load factor in 2050 and that in 2014 (current '
                    'value) are interpolated to get the load factor each year which is used to '
                    'estimate the adoption. Recent Historical adoptions were estimated by '
                    'assuming that the average load factors calculated from the weighted '
                    'available data are applied to the total urban mobility each year after '
                    'applying the car mode share (assumed fixed) '
                    ),
                'dataframe': ds5_df},
            {'name': 'PDS3- With Global Load Factor of 3 person per vehicle per trip by 2050', 'include': True,
                'description': (
                    'We take a very high load factor average, which is close to the maximum and '
                    'assume that it can be the 2050 global average load factor. We assume that '
                    'that figure is out of a maximum as entered on Advanced Controls (~3 persons '
                    'per trip) and estimate what effective adoption share the target load factor '
                    'represents (assuming that all trips are either single occupancy or the '
                    'maximum entered. This load factor in 2050 and that in 2014 (current value) '
                    'are interpolated to get the load factor each year which is used to estimate '
                    'the adoption. Recent Historical adoptions were estimated by assuming that '
                    'the average load factors calculated from the weighted available data are '
                    'applied to the total urban mobility each year after applying the car mode '
                    'share (assumed fixed) '
                    ),
                'dataframe': ds6_df},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

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
            use_first_pds_datapoint_main=False,
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

