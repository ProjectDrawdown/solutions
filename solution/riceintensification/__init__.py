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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'CONVENTIONAL Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=True),
    'Yield from CONVENTIONAL Practice': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_from_CONVENTIONAL_Practice.csv"),
        use_weight=True),
    'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_Gain_Increase_from_CONVENTIONAL_to_SOLUTION.csv"),
        use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    't CO2-eq (Aggregate emissions) Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_CO2_eq_Aggregate_emissions_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    't CO2 Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_CO2_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    't N2O-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_N2O_CO2_eq_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    't CH4-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_CH4_CO2_eq_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2 Emissions per  Implementation Unit - SOLUTION': vma.VMA(
        filename=None, use_weight=False),
    'Sequestration Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
        use_weight=False),
    'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing': vma.VMA(
        filename=None, use_weight=False),
    'Disturbance Rate': vma.VMA(
        filename=None, use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'SRI'
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
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

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
            'Raw Data for ALL LAND TYPES': {
                'Norman Uphoff (Personal Comunication)': THISDIR.joinpath('ad', 'ad_Norman_Uphoff_Personal_Comunication.csv'),
            },
            'Region: Asia (Sans Japan)': {
                'Raw Data for ALL LAND TYPES': {
                  'IRIN (Adoption of SRI in China)': THISDIR.joinpath('ad', 'ad_IRIN_Adoption_of_SRI_in_China.csv'),
                  'IRIN (Adoption of SRI in India)': THISDIR.joinpath('ad', 'ad_IRIN_Adoption_of_SRI_in_India.csv'),
                  'IRIN (Adoption of SRI in Indonesia)': THISDIR.joinpath('ad', 'ad_IRIN_Adoption_of_SRI_in_Indonesia.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
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
            use_first_pds_datapoint_main=False,
            adoption_base_year=2018,
            copy_pds_to_ref=copy_pds_to_ref,
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
            annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)

