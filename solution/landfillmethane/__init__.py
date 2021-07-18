"""Landfill Methane Capture solution model.
   Excel filename: LandfillMethane_RRS_ELECGEN_v1.1c_18Jan2020.xlsm
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
        use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
        use_weight=True),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
        use_weight=True),
    'SOLUTION Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
        use_weight=False),
    'CONVENTIONAL Average Annual Use': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
        use_weight=True),
    'SOLUTION Average Annual Use': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
        use_weight=False),
    'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=True),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "CONVENTIONAL_Fixed_Operating_Cost_FOM.csv"),
        use_weight=True),
    'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Fixed_Operating_Cost_FOM.csv"),
        use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'Total Energy Used per SOLUTION functional unit': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Consumed per CONVENTIONAL Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Direct_Emissions_per_Functional_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CH4_CO2eq_Tons_Reduced.csv"),
        use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    '2005-2014 Average CONVENTIONAL Fuel Price per functional unit': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "2005_2014_Average_CONVENTIONAL_Fuel_Price_per_functional_unit.csv"),
        use_weight=True),
    'Weighted Average CONVENTIONAL Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "Weighted_Average_CONVENTIONAL_Plant_Efficiency.csv"),
        use_weight=True),
    'Coal Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath(*('energy', 'vma_Coal_Plant_Efficiency_2.csv')),
        use_weight=False),
    'Natural Gas Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "Natural_Gas_Plant_Efficiency.csv"),
        use_weight=False),
    'Oil Plant Efficiency': vma.VMA(
        filename=DATADIR.joinpath(*('energy', 'vma_Oil_Plant_Efficiency_2.csv')),
        use_weight=False),
    'tCO2 from Landfill Gas Burning': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "tCO2_from_Landfill_Gas_Burning.csv"),
        use_weight=False),
    'tCH4-CO2-eq from Landfill Gas Burning': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "tCH4_CO2_eq_from_Landfill_Gas_Burning.csv"),
        use_weight=False),
    'tN2O-CO2-eq from Landfill Gas Burning': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "tN2O_CO2_eq_from_Landfill_Gas_Burning.csv"),
        use_weight=False),
    'Discount Rate: Commercial / Industry': vma.VMA(
        filename=DATADIR.joinpath('energy', "vma_data", "Discount_Rate_Commercial_Industry.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "TW",
    "functional unit": "TWh",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Landfill Methane Capture'
solution_category = ac.SOLUTION_CATEGORY.REPLACEMENT

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
        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.energy_tam_2_ref_data_sources,
            tam_pds_data_sources=rrs.energy_tam_2_pds_data_sources)
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
            'Baseline Cases': {
                'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
                'Based on: AMPERE 2014 MESSAGE MACRO 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
                'Based on: AMPERE 2014 MESSAGE MACRO 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
                'Based on: AMPERE 2014 MESSAGE MACRO Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
            },
            'Conservative Cases': {
                'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
                'Based on: Greenpeace 2015 Reference': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Reference.csv'),
                'Based on: AMPERE 2014 GEM E3 Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
                'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
            },
            'Ambitious Cases': {
                'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                'Based on: AMPERE 2014 IMAGE TIMER 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
                'Based on: AMPERE 2014 GEM E3 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
                'Based on: AMPERE 2014 IMAGE TIMER 450': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
                'Based on: AMPERE 2014 GEM E3 550': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
                'Based on: AMPERE 2014 IMAGE TIMER Reference': THISDIR.joinpath('ad', 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
            },
            '100% RES2050 Case': {
                'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
            },
            'Region: Middle East and Africa': {
                'Conservative Cases': {
                  'Based on: Greenpeace 2015 Reference': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Reference.csv'),
              },
                'Ambitious Cases': {
                  'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
              },
                '100% RES2050 Case': {
                  'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
              },
            },
            'Region: India': {
                'Baseline Cases': {
                  'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
              },
                'Conservative Cases': {
                  'Based on: Greenpeace 2015 Reference': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Reference.csv'),
                  'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
              },
                'Ambitious Cases': {
                  'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
                  'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
              },
                '100% RES2050 Case': {
                  'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
              },
            },
            'Region: EU': {
                'Baseline Cases': {
                  'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
              },
                'Conservative Cases': {
                  'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
              },
                'Ambitious Cases': {
                  'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
              },
            },
            'Region: USA': {
                'Baseline Cases': {
                  'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
              },
                'Conservative Cases': {
                  'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
                  'Baeed on: Greenpeace Reference Scenario': THISDIR.joinpath('ad', 'ad_Baeed_on_Greenpeace_Reference_Scenario.csv'),
              },
                'Ambitious Cases': {
                  'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                  'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
              },
                '100% RES2050 Case': {
                  'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'PDS 1 Baseline _Integrated with Waste Model on feedstock availability', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_1_Baseline__Integrated_with_Waste_Model_on_feedstock_availability.csv')},
            {'name': 'PDS 2 Baseline _Integrated with Waste Model on feedstock availability', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_2_Baseline__Integrated_with_Waste_Model_on_feedstock_availability.csv')},
            {'name': 'PDS 3 Baseline _Integrated with Waste Model on feedstock availability', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_3_Baseline__Integrated_with_Waste_Model_on_feedstock_availability.csv')},
            {'name': 'PDS 1 - CONSERVATIVE LANDFILL METHANE IF. CONSERVATIVE W2E (Integrated in Waste Model)', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_1_CONSERVATIVE_LANDFILL_METHANE_IF__CONSERVATIVE_W2E_Integrated_in_Waste_Model.csv')},
            {'name': 'PDS 2 - CONSERVATIVE LANDFILL METHANE IF. CONSERVATIVE W2E (Integrated in Waste Model)', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_2_CONSERVATIVE_LANDFILL_METHANE_IF__CONSERVATIVE_W2E_Integrated_in_Waste_Model.csv')},
            {'name': 'PDS 3 - CONSERVATIVE LANDFILL METHANE IF. CONSERVATIVE W2E (Integrated in Waste Model)', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_3_CONSERVATIVE_LANDFILL_METHANE_IF__CONSERVATIVE_W2E_Integrated_in_Waste_Model.csv')},
            {'name': 'PDS 1 - AMBITIOUS LANDFILL METHANE IF AMBITIOUS W2E (Integrated in Waste Model)', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_1_AMBITIOUS_LANDFILL_METHANE_IF_AMBITIOUS_W2E_Integrated_in_Waste_Model.csv')},
            {'name': 'PDS 2 - AMBITIOUS LANDFILL METHANE IF AMBITIOUS W2E (Integrated in Waste Model)', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_2_AMBITIOUS_LANDFILL_METHANE_IF_AMBITIOUS_W2E_Integrated_in_Waste_Model.csv')},
            {'name': 'PDS 3 - AMBITIOUS LANDFILL METHANE IF AMBITIOUS W2E (Integrated in Waste Model)', 'include': True,
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_3_AMBITIOUS_LANDFILL_METHANE_IF_AMBITIOUS_W2E_Integrated_in_Waste_Model.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
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

        ht_ref_adoption_initial = pd.Series(list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
        ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
            use_first_pds_datapoint_main=False,
            adoption_base_year=2018, copy_pds_to_ref=True,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=2)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=pds_tam_per_region,
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
            fc_convert_iunit_factor=rrs.TERAWATT_TO_KILOWATT)

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
            conversion_factor=rrs.TERAWATT_TO_KILOWATT)

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

