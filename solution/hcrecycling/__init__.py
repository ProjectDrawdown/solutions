"""Household & Commercial Recycling solution model.
   Excel filename: Recycling-HH&C-v1.1b-MRG2020_PostIntegration.xlsm
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=True),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=True),
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Direct_Emissions_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Direct_Emissions_per_Functional_Unit.csv"),
        use_weight=True),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=True),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Revenue_per_Functional_Unit.csv"),
        use_weight=True),
    'MSW Collection Operating Costs': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "MSW_Collection_Operating_Costs.csv"),
        use_weight=False),
    'Emissions from Collection': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Emissions_from_Collection.csv"),
        use_weight=False),
    'Replacement rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Replacement_rates.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "Facility for Million t of MSW / Yr",
    "functional unit": "Million Metric t of Recyclable MSW",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Household & Commercial Recycling'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-67p2050-postintegrationjune2020"
PDS2 = "PDS2-89p2050-postintegrationjune2020"
PDS3 = "PDS3-100p2050-postintegrationjune2020"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    _ref_tam_sources = {
        'Baseline Cases': {
                'Drawdown TAM': THISDIR.joinpath('tam', 'tam_Drawdown_TAM.csv'),
        },
            'Region: USA': {
                'Baseline Cases': {
                'Drawdown TAM': THISDIR.joinpath('tam', 'tam_Drawdown_TAM.csv'),
                'USEPA SMM': THISDIR.joinpath('tam', 'tam_USEPA_SMM.csv'),
            },
        },
    }
    _pds_tam_sources = {
        'Baseline Cases': {
                'Drawdown TAM: Integration TAM PDS1': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Integration_TAM_PDS1.csv'),
        },
        'Conservative Cases': {
                'Drawdown TAM: Integration TAM PDS2': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Integration_TAM_PDS2.csv'),
        },
        'Ambitious Cases': {
                'Drawdown TAM: Integration TAM PDS3': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Integration_TAM_PDS3.csv'),
        },
    }

    def __init__(self, scen=None):
        if isinstance(scen, ac.AdvancedControls):
            self.scenario = scen.name
            self.ac = scen
        else:
            self.scenario = scen or PDS2
            self.ac = scenarios[self.scenario]

        # TAM


        self.set_tam(
            interpolation_overrides = {
                'USA': THISDIR.joinpath('tam', 'tam_override_usa_region.csv')
            })
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        adconfig_list = [
            ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
             'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['trend', self.ac.soln_pds_adoption_prognostication_trend, '3rd Poly',
             '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
             '3rd Poly', '2nd Poly', '2nd Poly'],
            ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'High',
             'High', 'High', 'High', 'High', 'Medium',
             'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ['high_sd_mult', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
            'Baseline Cases': {
                'Calculated based on What a Waste and EU as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_and_OECD_ceiling.csv'),
            },
            '': {
                'Calculated based on What a Waste and Austria as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_Austria_as_PDS_Benchmark_and_OECD_ceiling.csv'),
                'Calculated based on What a Waste and USA as PDS Benchmark ceiling and EU as OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_ceiling_and_EU_as_OECD_ceiling.csv'),
            },
            'Region: OECD90': {
                'Baseline Cases': {
                  'Data from (Hoornweg & Bhata-Tata What a Waste World Bank 2012, Table 12, page 24)': THISDIR.joinpath('ad', 'ad_Data_from_Hoornweg_BhataTata_What_a_Waste_World_Bank_2012_Table_12_page_24.csv'),
              },
                '': {
                  'Calculated based on What a Waste and EU as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_and_OECD_ceiling.csv'),
                  'Calculated based on What a Waste and Austria as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_Austria_as_PDS_Benchmark_and_OECD_ceiling.csv'),
              },
                'Ambitious Cases': {
                  'OECD.Stats, MSW Treated - Recycled (retrieved on 7/16/16)': THISDIR.joinpath('ad', 'ad_OECD_Stats_MSW_Treated_Recycled_retrieved_on_71616.csv'),
              },
            },
            'Region: Middle East and Africa': {
                'Baseline Cases': {
                  'Calculated based on What a Waste and EU as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_and_OECD_ceiling.csv'),
              },
                '': {
                  'Calculated based on What a Waste and Austria as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_Austria_as_PDS_Benchmark_and_OECD_ceiling.csv'),
              },
                'Conservative Cases': {
                  'Calculated based on What a Waste and USA as PDS Benchmark ceiling and EU as OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_ceiling_and_EU_as_OECD_ceiling.csv'),
              },
            },
            'Region: China': {
                'Baseline Cases': {
                  'PDS % Recycled of Recycleable Benchmarked OEACD90 @ EU 2020 Target and all other regions at current OECD90 Adoption': THISDIR.joinpath('ad', 'ad_PDS_Recycled_of_Recycleable_Benchmarked_OEACD90_EU_2020_Target_and_all_other_regions_at__8a8e45f0.csv'),
              },
            },
            'Region: India': {
                'Baseline Cases': {
                  'PDS % Recycled of Recycleable Benchmarked OEACD90 @ EU 2020 Target and all other regions at current OECD90 Adoption': THISDIR.joinpath('ad', 'ad_PDS_Recycled_of_Recycleable_Benchmarked_OEACD90_EU_2020_Target_and_all_other_regions_at__8a8e45f0.csv'),
              },
            },
            'Region: EU': {
                'Baseline Cases': {
                  'PDS % Recycled of Recycleable Benchmarked OEACD90 @ EU 2020 Target and all other regions at current OECD90 Adoption': THISDIR.joinpath('ad', 'ad_PDS_Recycled_of_Recycleable_Benchmarked_OEACD90_EU_2020_Target_and_all_other_regions_at__8a8e45f0.csv'),
              },
                '': {
                  'PDS % Recycled of Recycleable Benchmarked Target at current Austria Adoption': THISDIR.joinpath('ad', 'ad_PDS_Recycled_of_Recycleable_Benchmarked_Target_at_current_Austria_Adoption.csv'),
                  'EuroStat 2015': THISDIR.joinpath('ad', 'ad_EuroStat_2015.csv'),
              },
                'Conservative Cases': {
                  'OECD.stats': THISDIR.joinpath('ad', 'ad_OECD_stats.csv'),
              },
            },
            'Region: USA': {
                'Baseline Cases': {
                  'OECD.Stats, MSW Treated - Recycled (retrieved on 7/16/16)': THISDIR.joinpath('ad', 'ad_OECD_Stats_MSW_Treated_Recycled_retrieved_on_71616.csv'),
              },
                'Conservative Cases': {
                  'Calculated based on What a Waste and EU as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_and_OECD_ceiling.csv'),
              },
                '': {
                  'Calculated based on What a Waste and Austria as PDS Benchmark and OECD ceiling': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_Austria_as_PDS_Benchmark_and_OECD_ceiling.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'Custom Scenario 1 (PDS2) - High of Existing Prognostications',
              'description': (
                    'The high growth of existing prognostications (Mean + 1 Standard deviation '
                    'each year) is used for this scenario. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Custom_Scenario_1_PDS2_High_of_Existing_Prognostications.csv')},
            {'name': 'Custom Scenario 2 (PDS3) - High of Existing Prognostications with Integration Constraints',
              'description': (
                    'The high growth of existing prognostications (Mean + 1 Standard deviation '
                    'each year) is used for this scenario. At higher years, restrictions are '
                    'applied due to reduction in Municipal Solid Waste Feedstocks caused by '
                    'other higher priority solutions (such as Reduced Food Waste and Compost). '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Custom_Scenario_2_PDS3_High_of_Existing_Prognostications_with_Integration_Constraints.csv')},
            {'name': 'PDS 1 Plausible Scenario Post Integration August 2019',
              'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_1_Plausible_Scenario_Post_Integration_August_2019.csv')},
            {'name': 'PDS 2 Drawdown Scenario Post Integration August 2019',
              'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_2_Drawdown_Scenario_Post_Integration_August_2019.csv')},
            {'name': 'PDS 3 Optimum Scenario Post Integration August 2019',
              'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_3_Optimum_Scenario_Post_Integration_August_2019.csv')},
            {'name': 'PDS1 JUNE 2020 - post integration',
              'description': (
                    'PDS1 % Recycled of Recycleable Benchmarked OEACD90 @ EU 2020 Target and all '
                    'other regions at current US adoption. Global adoption is limited by the '
                    'post-integration TAM. Regional adoption have not been updated. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_JUNE_2020_post_integration.csv')},
            {'name': 'PDS2 JUNE 2020 - post-integration',
              'description': (
                    'PDS2 % Recycled of Recycleable Benchmarked OEACD90 @ EU 2020 Target and all '
                    'other regions at current OECD90 Adoption (approximately Germany & Austria '
                    'adoption). Global adoption is limited by the post-integration TAM. Regional '
                    'adoption have not been updated. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_JUNE_2020_postintegration.csv')},
            {'name': 'PDS3 JUNE 2020 - Post-integration',
              'description': (
                    'PDS3 % Recycled of Recycleable Benchmarked OECD90 @ 80, all other regions '
                    'at 70%. Global adoption is limited by the post-integration TAM. Regional '
                    'adoption have not been updated. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS3_JUNE_2020_Postintegration.csv')},
        ]
        for (i,rs) in enumerate(ca_pds_data_sources):
            rs['include'] = (i in self.ac.soln_pds_adoption_scenarios_included)
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': 'Custom REF 1: Adoption at Base Year levels (2014)',
              'description': (
                    'Assume adoption % in 2014 remains constant '
                    ),
              'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Custom_REF_1_Adoption_at_Base_Year_levels_2014.csv')},
        ]
        # all sources are included in REF adoptions
        for rs in ca_ref_data_sources:
            rs['include'] = True
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1, low_sd_mult=1,
            total_adoption_limit=ref_tam_per_region)

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
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            copy_pds_to_ref=False,
            copy_ref_datapoint=False, copy_pds_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=4)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
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

