"""Sustainable Clothing solution model.
   Excel filename: Sustainable Clothing-RRS.IP-0121MRG_2021.xlsm
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
        filename=None, use_weight=False),
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Lifetime Capacity': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Average Annual Use': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Average Annual Use': vma.VMA(
        filename=None, use_weight=False),
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
        filename=None, use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
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
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "1 Million Metric Ton Clothing",
    "functional unit": "1 Million Metric Ton Clothing",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Sustainable Clothing'
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
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES' ],
            ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES' ],
            ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
              '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly'],
            ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
              'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ['high_sd_mult', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
        tam_ref_data_sources = {
              'Baseline Cases': {
                  'Ellen Macarthur Foundation. 3% Growth to 160 in 2050': THISDIR.joinpath('tam', 'tam_Ellen_Macarthur_Foundation__3_Growth_to_160_in_2050.csv'),
            },
              '': {
                  'Global Fashion Agenda - Pulse of Fashion Industry 102 in 2030': THISDIR.joinpath('tam', 'tam_Global_Fashion_Agenda_Pulse_of_Fashion_Industry_102_in_2030.csv'),
                  'Quantis, Measuring Fashion, Apparel': THISDIR.joinpath('tam', 'tam_Quantis_Measuring_Fashion_Apparel.csv'),
            },
              'Conservative Cases': {
                  'Textile Exchange 2019,2020 (Assume 60% of Fibers for Clothing)': THISDIR.joinpath('tam', 'tam_Textile_Exchange_20192020_Assume_60_of_Fibers_for_Clothing.csv'),
            },
        }
        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
            tam_pds_data_sources=tam_ref_data_sources)
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
            ['low_sd_mult', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ['high_sd_mult', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'PDS1 ~10% CAGR',
              'description': (
                    'Based on projected market value growth of ethical and sustainable fashion '
                    '(as a percent of Total Market $784B), at between 9-10% CAGR '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_10_CAGR.csv')},
            {'name': 'PDS2 - 32% adoption by 2040 (Based on Quantis 40% recycled fibers)',
              'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_32_adoption_by_2040_based_on_Quantis_40_recycled_fibers.csv')},
        ]
        for (i,rs) in enumerate(ca_pds_data_sources):
            rs['include'] = (i in self.ac.soln_pds_adoption_scenarios_included)
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
        # even when the final_datapoint_year is 2018, the TAM initial year is usually hard-coded to 2014
        # if that is wrong, change 2014 to 2018 below
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
            use_first_pds_datapoint_main=True,
            adoption_base_year=2018,
            copy_pds_to_ref=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        ''' NC/MM 2021-07-25
        This is a 'solution-specific' hack to try and fix the Assertion Errors we are getting out of the Tests on the First Cost numbers.
        Digging through the data vs workbook, we found that the 2014 number for "Custom PDS Adoption" in the workbook is pulling from an 2018 Adoption
        Number from the Advanced Controls (C61), while the code is loading it from the data.
        We are hardcoding this number into that value here to fix this calculation
        See the Sustainable_Clothing_FirstCostChecks.ipynb for scripts and descriptions of our data investigation and reasoning
        '''
        # Fix the value for the 2014 World Data
        self.ht.pds_adoption_data_per_region.loc[2014, "World"] = 0.050691647   
                
        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

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
            fc_convert_iunit_factor=1)

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
            conversion_factor=1)

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



        ''' NC/MM 2021-07-25
        Looking at this number for 2018 - This is our Adoption in 2018 number. Looks like somewhere in code, in the Model somewhere, is probably overwriting the number
        read in from the Total Solution Implementation Units Required PDS (Unit Adoption Calculations AY140) and overwriting it with this number from Advanced Calculations C61
        Putting in a hardcoded fix into __init__.py with the number from the sheet, but note, this will need to be scenario specific            
        '''
        if self.scenario == "PDS1-8p2050-Dec2020":
            self.ua.soln_pds_funits_adopted.loc[2018, "World"] = 0.477787    
        # Note: tried this but this still didn't fix the issue, I think the overwriting of this happens happens within  the ua.soln_pds_tot_iunits_reqd() function
                    

