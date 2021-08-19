"""Improved Cattle Feed Quality solution model.
   Excel filename: ImprovedCattleFeed_Apr2021.xlsm
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue from Increased Milk Yield': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Revenue_from_Increased_Milk_Yield.csv"),
        use_weight=True),
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
        use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CH4_CO2eq_Tons_Reduced.csv"),
        use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Milk Yield': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Milk_Yield.csv"),
        use_weight=False),
    'SOLUTION Increased Milk Yield': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Increased_Milk_Yield.csv"),
        use_weight=False),

    # This is a manually added VMA to get around an issue with importing this solution module: During import, function
    # _substitute_vma() in model/advanced_controls.py throws an exception because this VMA is not generated here by
    # the model extraction notebook Improved_Cattle_Feed_Extraction.ipynb. The source of that issue should be found so
    # that this potentially dangerous work-around can be removed.
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=None, use_weight=False, fixed_summary=(1e-20, 1e-20, 1e-20)),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "kg of protein",
    "functional unit": "kg of protein",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Improved Cattle Feed Quality'
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
        import pdb
        pdb.set_trace()
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
                  'Reference 1': THISDIR.joinpath('tam', 'tam_Reference_1.csv'),
            },
              '': {
                  'Reference 2': THISDIR.joinpath('tam', 'tam_Reference_2.csv'),
            },
              'Conservative Cases': {
                  'Plausible': THISDIR.joinpath('tam', 'tam_Plausible.csv'),
            },
              'Ambitious Cases': {
                  'Drawdown': THISDIR.joinpath('tam', 'tam_Drawdown.csv'),
            },
              'Maximum Cases': {
                  'Optimum': THISDIR.joinpath('tam', 'tam_Optimum.csv'),
            },
        }
        tam_pds_data_sources = {
            'Baseline Cases': {
                    'Drawdown TAM: Reference 1': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Reference_1.csv'),
            },
            '': {
                    'Drawdown TAM: Reference 2': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Reference_2.csv'),
            },
            'Conservative Cases': {
                    'Drawdown TAM: Plausible': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Plausible.csv'),
            },
            'Ambitious Cases': {
                    'Drawdown TAM: Drawdown': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Drawdown.csv'),
            },
            'Maximum Cases': {
                    'Drawdown TAM: Optimum': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Optimum.csv'),
            },
        }
        print('p1')
        print(self.ac.pds_source_post_2014)
        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
            main_includes_regional=True,
            tam_pds_data_sources=tam_pds_data_sources)
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        adconfig_list = [
            ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
             'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['trend', self.ac.soln_pds_adoption_prognostication_trend, 'Linear',
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
            {'name': 'LimitedAdoption26%',
              'description': (
                    'Adoption of the solution is STAGNANT in developing countries (8% Asia, 7% '
                    'Middle East and Africa, 8% Latin America), but there is some LIMITED '
                    'adoption within developed countries (44% OECD90 and 41% Eastern Europe). '
                    'Total Global Adoption is 26% of TAM in 2050 using a linear trend from 21% '
                    'global adoption in 2014. Limited adoption assumes grazing and mixed systems '
                    'can improve adoption by 10%. And feedlots by 5%. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_LimitedAdoption26.csv')},
            {'name': 'LimitedAdoption31%',
              'description': (
                    'Adoption of the solution is LIMITED in developing countries (27% Asia, 26% '
                    'Middle East and Africa, 27% Latin America), but STAGNANT within developed '
                    'countries (35% OECD90 and 32% Eastern Europe). Total Global Adoption is 31% '
                    'of TAM in 2050 using a linear trend from 21% global adoption in 2014. '
                    'Limited adoption assumes grazing and mixed systems can improve adoption by '
                    '20%. And feedlots by 10%. This essentially fills the gap between Developing '
                    'Nations and those that are already Developed. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_LimitedAdoption31.csv')},
            {'name': 'MediumAdoption35%',
              'description': (
                    'Adoption of the solution is LIMITED  in developing countries (27% Asia, 26% '
                    'Middle East and Africa, 27% Latin America), and also LIMITED within '
                    'developed countries (44% OECD90 and 41% Eastern Europe). Total Global '
                    'Adoption is 35% of TAM in 2050 using a linear trend from 21% global '
                    'adoption in 2014. Limited adoption assumes grazing and mixed systems can '
                    'improve adoption by 20% and feedlots by 10% in Developing Nations. Limited '
                    'adoption assumes grazing and mixed systems can improve adoption by 10% and '
                    'feedlots by 5% in Developed Nations. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_MediumAdoption35.csv')},
            {'name': 'MediumAdoption45%',
              'description': (
                    'Adoption of the solution is LIMITED  in developing countries (27% Asia, 26% '
                    'Middle East and Africa, 27% Latin America), but AMBITIOUS within developed '
                    'countries (63% OECD90 and 61% Eastern Europe). Total Global Adoption is 45% '
                    'of TAM in 2050 using a linear trend from 21% global adoption in 2014. '
                    'Limited adoption assumes grazing and mixed systems can improve adoption by '
                    '20% and feedlots by 10% in Developing Nations. Ambitious adoption assumes '
                    'grazing and mixed systems can improve adoption by 30% and feedlots by 15% '
                    'in Developed Nations. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_MediumAdoption45.csv')},
            {'name': 'HighAdoption48%',
              'description': (
                    'Adoption of the solution is AMBITIOUS  in developing countries (52% Asia, '
                    '51% Middle East and Africa, 52% Latin America), but LIMITED within '
                    'developed countries (44% OECD90 and 41% Eastern Europe). Total Global '
                    'Adoption is 48% of TAM in 2050 using a linear trend from 21% global '
                    'adoption in 2014. Ambitious adoption assumes grazing and mixed systems can '
                    'improve adoption by 45% and feedlots by 25% in Developing Nations. Limited '
                    'adoption assumes grazing and mixed systems can improve adoption by 10% and '
                    'feedlots by 5% in Developed Nations. However, no system can exceed 75% '
                    'adoption. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_HighAdoption48.csv')},
            {'name': 'HighAdoption57%',
              'description': (
                    'Adoption of the solution is AMBITIOUS  in developing countries (52% Asia, '
                    '51% Middle East and Africa, 52% Latin America), and AMBITIOUS within '
                    'developed countries (63% OECD90 and 61% Eastern Europe). Total Global '
                    'Adoption is 57% of TAM in 2050 using a linear trend from 21% global '
                    'adoption in 2014. Ambitious adoption assumes grazing and mixed systems can '
                    'improve adoption by 45% and feedlots by 25% in Developing Nations. '
                    'Ambitious adoption assumes grazing and mixed systems can improve adoption '
                    'by 30% and feedlots by 15% in Developed Nations. However, no system can '
                    'exceed 75% adoption. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_HighAdoption57.csv')},
            {'name': 'MaxAdoption75%',
              'description': (
                    'Adoption of the solution is at its maximum. Total Global Adoption is 75% of '
                    'TAM in 2050 using a linear trend from 21% global adoption in 2014. We '
                    'assume a maximum of 75% because sources suggest at least 20-25% of the '
                    'cattle diet should come from high-fiber roughages to maintain the animals '
                    'digestive health. This 25% wont be addressable with an improved feed '
                    'quality solution. '
                    ),
              'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_MaxAdoption75.csv')},
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
            ref_tam_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
            use_first_pds_datapoint_main=True,
            adoption_base_year=2014,
            copy_pds_to_ref=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

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

