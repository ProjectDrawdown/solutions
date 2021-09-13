"""High-Performance Glass (Commercial) solution model.
   Excel filename: Glass_RRS_Model_Commercial-Nov19.xlsm
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
        use_weight=False),
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Total_Energy_Used_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Total_Energy_Used_per_Functional_Unit.csv"),
        use_weight=False),
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
    'Heating Energy Efficiency': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Heating_Energy_Efficiency.csv"),
        use_weight=False),
    'Cooling Energy Efficiency': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Cooling_Energy_Efficiency.csv"),
        use_weight=False),
    'Average Energy for Space Cooling per Floor Area': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Energy_for_Space_Cooling_per_Floor_Area.csv"),
        use_weight=False),
    'Average Energy for Space Heating per Floor Area': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Energy_for_Space_Heating_per_Floor_Area.csv"),
        use_weight=False),
    'Discount Rate: Commercial / Industry': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rate_Commercial_Industry.csv"),
        use_weight=False),
    'Commercial Window to Floor Ratio': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Commercial_Window_to_Floor_Ratio.csv"),
        use_weight=True),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "million sq-meters",
    "functional unit": "million sq-meters",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'High-Performance Glass (Commercial)'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-89p2050-Based on 2.75% Retrofit Rate"
PDS2 = "PDS2-95p2050-Based on 5% Retrofit Rate"
PDS3 = "PDS3-98p2050-Based on 8% Retrofit Rate"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem
    
    def __init__(self, scen=None):
        if scen is None:
            scen = list(scens.keys())[0]
        self.scenario = scen
        self.ac = scenarios[scen]

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
                  'Drawdown Buildings Sector Integrated TAM - Commercial Average': THISDIR.joinpath('tam', 'tam_Drawdown_Buildings_Sector_Integrated_TAM_Commercial_Average.csv'),
            },
              '': {
                  'Drawdown Buildings Sector Integrated TAM - Commercial Average without OECD90 Region': THISDIR.joinpath('tam', 'tam_Drawdown_Buildings_Sector_Integrated_TAM_Commercial_Average_without_OECD90_Region.csv'),
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
            {'name': '2.75% building stock retrofit rate',
              'description': (
                    'This model is for Commercial buildings in the non-OECD countries since the '
                    'OECD countries already have a high adoption of high performance static '
                    'glass, and is included in the Smart Glass model only. The difficulty in '
                    'collecting data for non-OECD countries raises the need for some '
                    'assumptions. In this case, we take the latest data from available countries '
                    '(China and India), and assume that the adoption rate is fixed for all the '
                    'historical years in the analysis (2014- current year). The future years '
                    'have been projected by splitting the current unadopted (single pane) Market '
                    '(TAM) each year into 1. the existing area from the previous years , 2. new '
                    'growth in the TAM. The existing area is assumed to be converted to High '
                    'performance at the rate of retrofit, the new growth is converted at a '
                    'higher rate according to data on sales. Click to Jump to the Custom PDS '
                    'Adoption. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_2_75_building_stock_retrofit_rate.csv')},
            {'name': '5.0% building stock retrofit rate',
              'description': (
                    'This model is for Commercial buildings in the non-OECD countries since the '
                    'OECD countries already have a high adoption of high performance static '
                    'glass, and is included in the Smart Glass model only. The difficulty in '
                    'collecting data for non-OECD countries raises the need for some '
                    'assumptions. In this case, we take the latest data from available countries '
                    '(China and India), and assume that the adoption rate is fixed for all the '
                    'historical years in the analysis (2014- current year). The future years '
                    'have been projected by splitting the current unadopted (single pane) Market '
                    '(TAM) each year into 1. the existing area from the previous years , 2. new '
                    'growth in the TAM. The existing area is assumed to be converted to High '
                    'performance at the rate of retrofit, the new growth is converted at a '
                    'higher rate according to data on sales. Click to Jump to the Custom PDS '
                    'Adoption. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_5_0_building_stock_retrofit_rate.csv')},
            {'name': '8.0% building stock retrofit rate',
              'description': (
                    'This model is for Commercial buildings in the non-OECD countries since the '
                    'OECD countries already have a high adoption of high performance static '
                    'glass, and is included in the Smart Glass model only. The difficulty in '
                    'collecting data for non-OECD countries raises the need for some '
                    'assumptions. In this case, we take the latest data from available countries '
                    '(China and India), and assume that the adoption rate is fixed for all the '
                    'historical years in the analysis (2014- current year). The future years '
                    'have been projected by splitting the current unadopted (single pane) Market '
                    '(TAM) each year into 1. the existing area from the previous years , 2. new '
                    'growth in the TAM. The existing area is assumed to be converted to High '
                    'performance at the rate of retrofit, the new growth is converted at a '
                    'higher rate according to data on sales. Click to Jump to the Custom PDS '
                    'Adoption. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_8_0_building_stock_retrofit_rate.csv')},
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

        ht_ref_adoption_initial = pd.Series(
            list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        # even when the final_datapoint_year is 2018, the TAM initial year is usually hard-coded to 2014
        # if that is wrong, change 2014 to 2018 below
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
            use_first_pds_datapoint_main=True,
            use_first_ref_datapoint_main=False,                                 
            copy_pds_to_ref=False,
            copy_ref_datapoint=False, copy_pds_datapoint='Ref Table',
            copy_datapoint_to_year=2014,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=4)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            repeated_cost_for_iunits=False,
                                            bug_cfunits_double_count=False,
                                            replacement_period_offset=0)
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

