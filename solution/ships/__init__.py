"""Oceanic Freight Improvements solution model.
   Excel filename: OceanFreight-RRSv1.1b-23Jan20.xlsm
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
        use_weight=False),
    'SOLUTION Average Annual Use': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
        use_weight=False),
    'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
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
    'Discount Rate: Commercial / Industry': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rate_Commercial_Industry.csv"),
        use_weight=False),
    'Learning Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Learning_Rate.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "Ship",
    "functional unit": "Billion Ton - nmiles",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Oceanic Freight Improvements'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-57p2050-Avg_EEOI"
PDS2 = "PDS2-78p2050-1StDev_below_Mean_EEOI"
PDS3 = "PDS3-97p2050-Lowest_EEOI"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    _ref_tam_sources = scenario.load_sources(THISDIR/'tam'/'tam_ref_sources.json','*')
    _pds_tam_sources=_ref_tam_sources

    def __init__(self, scen=None):
        if isinstance(scen, ac.AdvancedControls):
            self.scenario = scen.name
            self.ac = scen
        else:
            self.scenario = scen or PDS2
            self.ac = scenarios[self.scenario]

        # TAM
        self.set_tam()
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
        ca_pds_data_sources = [
            {'name': 'PDS1 - Drawdown Team Calculations based on Projections from Smith et al (2014) - 3rd GHG Report of the IMO - Mean of projected EEOI values', 'include': True,
                'description': (
                    'We take the mean estimates of EEOI (Energy Efficiency Operations Index in '
                    'gCO2/ton-nmile) as projected by  several studies referenced in the 3rd GHG '
                    'IMO Study (Smith et al, 2014), interpolate for missing years and convert '
                    'them to Estimated ton-nautical mile adoptions assuming that an efficient '
                    'ship is one that adopts a fixed set of 17 technologies and slow steaming, '
                    'and a conventional (non-efficient) ship is one that has average efficiency '
                    'in 2014. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_Drawdown_Team_Calculations_based_on_Projections_from_Smith_et_al_2014_3rd_GHG_Repor_3eb1a907.csv')},
            {'name': 'PDS2 - Drawdown Team Calculations based on Projections from Smith et al (2014) - 3rd GHG Report of the IMO - 1 StDev more Ambitious than mean in EEOI terms', 'include': True,
                'description': (
                    'We take (1 standard deviation below the mean of) the estimates of EEOI '
                    '(Energy Efficiency Operations Index in gCO2/ton-nmile) as projected by '
                    'several studies referenced in the 3rd GHG IMO Study (Smith et al, 2014), '
                    'interpolate for missing years and convert them to Estimated ton-nautical '
                    'mile adoptions assuming that an efficient ship is one that adopts a fixed '
                    'set of 17 technologies and slow steaming, and a conventional (non- '
                    'efficient) ship is one that has average efficiency in 2014. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_Drawdown_Team_Calculations_based_on_Projections_from_Smith_et_al_2014_3rd_GHG_Repor_e1bf2fbd.csv')},
            {'name': 'PDS3 - Drawdown Team Calculations based on Projections from Smith et al (2014) - 3rd GHG Report of the IMO - most ambitious values from all scenarios', 'include': True,
                'description': (
                    'We take the lowest estimates of EEOI (Energy Efficiency Operations Index in '
                    'gCO2/ton-nmile) as projected by  several studies referenced in the 3rd GHG '
                    'IMO Study (Smith et al, 2014), interpolate for missing years and convert '
                    'them to Estimated ton-nautical mile adoptions assuming that an efficient '
                    'ship is one that adopts a fixed set of 17 technologies and slow steaming, '
                    'and a conventional (non-efficient) ship is one that has average efficiency '
                    'in 2014. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS3_Drawdown_Team_Calculations_based_on_Projections_from_Smith_et_al_2014_3rd_GHG_Repor_40d75a6d.csv')},
            {'name': 'Drawdown Book Edition 1 Scenario 1', 'include': False,
                'description': (
                    'We take the mean estimates of EEOI (Energy Efficiency Operations Index in '
                    'gCO2/ton-nmile) as projected by  several studies referenced in the 3rd GHG '
                    'IMO Study (Smith et al, 2014), interpolate for missing years and convert '
                    'them to Estimated ton-nautical mile adoptions assuming that an efficient '
                    'ship is one that adopts a fixed set of 17 technologies and slow steaming, '
                    'and a conventional (non-efficient) ship is one that has average efficiency '
                    'in 2008. This scenario follows the same process as PDS 1 above, but uses '
                    'the inputs from the model of the Drawdown Book edition 1, hence gets '
                    'different results. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_1.csv')},
            {'name': 'Drawdown Book Edition 1 Scenario 2', 'include': False,
                'description': (
                    'We take (1 standard deviation below the mean of) the estimates of EEOI '
                    '(Energy Efficiency Operations Index in gCO2/ton-nmile) as projected by '
                    'several studies referenced in the 3rd GHG IMO Study (Smith et al, 2014), '
                    'interpolate for missing years and convert them to Estimated ton-nautical '
                    'mile adoptions assuming that an efficient ship is one that adopts a fixed '
                    'set of 17 technologies and slow steaming, and a conventional (non- '
                    'efficient) ship is one that has average efficiency in 2008. This scenario '
                    'follows the same process as PDS 1 above, but uses the inputs from the model '
                    'of the Drawdown Book edition 1, hence gets different results. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_2.csv')},
            {'name': 'Drawdown Book Edition 1 Scenario 3', 'include': False,
                'description': (
                    'We take the lowest estimates of EEOI (Energy Efficiency Operations Index in '
                    'gCO2/ton-nmile) as projected by  several studies referenced in the 3rd GHG '
                    'IMO Study (Smith et al, 2014), interpolate for missing years and convert '
                    'them to Estimated ton-nautical mile adoptions assuming that an efficient '
                    'ship is one that adopts a fixed set of 17 technologies and slow steaming, '
                    'and a conventional (non-efficient) ship is one that has average efficiency '
                    'in 2008. This scenario follows the same process as PDS 1 above, but uses '
                    'the inputs from the model of the Drawdown Book edition 1, hence gets '
                    'different results. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_3.csv')},
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
            copy_pds_to_ref=True,
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
