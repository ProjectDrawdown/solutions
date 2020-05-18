"""Composting solution model.
   Excel filename: Composting-v1.1b-MRG2020-UpdatedScenarios.xlsm
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=True),
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
        use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Revenue_per_Functional_Unit.csv"),
        use_weight=False),
    'COLLECTION COSTS': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "COLLECTION_COSTS.csv"),
        use_weight=False),
    'SOLUTION Market Breakdown - % in-vessel': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Market_Breakdown_in_vessel.csv"),
        use_weight=False),
    'SOLUTION - Capacities of composters': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Capacities_of_composters.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "MMt",
    "functional unit": "MMt",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Composting'
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
            ['growth', 'Low', 'Low', 'Medium', 'Medium',
                'Low', 'Medium', 'Medium', 'Low', 'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0],
            dtype=np.object).set_index('param')
        tam_ref_data_sources = {
              'Baseline Cases': {
                  'Organic Fraction of MSW - From Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_From_Waste_TAM.csv'),
            },
              'Region: OECD90': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
              'Region: Eastern Europe': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
              'Region: Asia (Sans Japan)': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
              'Region: Middle East and Africa': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
              'Region: Latin America': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
              'Region: China': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
              'Region: India': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
              'Region: EU': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
                  'European Commission DG Environment - Arcadis': THISDIR.joinpath('tam', 'tam_European_Commission_DG_Environment_Arcadis.csv'),
              },
            },
              'Region: USA': {
                  'Baseline Cases': {
                  'Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_Organic_Fraction_of_MSW_Waste_TAM.csv'),
              },
            },
        }
        tam_pds_data_sources = {
            'Baseline Cases': {
                    'Drawdown TAM: Organic Fraction of MSW - Waste TAM': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Organic_Fraction_of_MSW_Waste_TAM.csv'),
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
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0],
            dtype=np.object).set_index('param')
        ad_data_sources = {
            'Baseline Cases': {
                'Calculated based on What a Waste and USA as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
            },
            'Conservative Cases': {
                'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
            },
            'Ambitious Cases': {
                'Calculated based on What a Waste and EU as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
            },
            'Region: OECD90': {
                'Baseline Cases': {
                  'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW)': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW.csv'),
              },
                'Conservative Cases': {
                  'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
              },
                'Ambitious Cases': {
                  'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW).1': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW_1.csv'),
              },
            },
            'Region: Asia (Sans Japan)': {
                'Baseline Cases': {
                  'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
              },
                'Conservative Cases': {
                  'Calculated based on What a Waste and USA as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
              },
                'Ambitious Cases': {
                  'Calculated based on What a Waste and EU as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
              },
            },
            'Region: Middle East and Africa': {
                'Baseline Cases': {
                  'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
                  'Calculated based on What a Waste and USA as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
              },
                'Ambitious Cases': {
                  'Calculated based on What a Waste and EU as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
              },
            },
            'Region: China': {
                'Baseline Cases': {
                  'Song, L. et al. Study on the Current Situation of Municipal Solid Waste Composting in China and Development Trend. 2012': THISDIR.joinpath('ad', 'ad_Song_L__et_al__Study_on_the_Current_Situation_of_Municipal_Solid_Waste_Composting_in_Chi_f57570b9.csv'),
              },
                'Conservative Cases': {
                  'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
              },
            },
            'Region: India': {
                'Baseline Cases': {
                  'Kharvel, R. Sustainable Solid Waste Management in Inidia. SEAS, Columbia Thesis. 2012': THISDIR.joinpath('ad', 'ad_Kharvel_R__Sustainable_Solid_Waste_Management_in_Inidia__SEAS_Columbia_Thesis__2012.csv'),
              },
            },
            'Region: EU': {
                'Baseline Cases': {
                  'EUROSTAT, 2016. http://ec.europa.eu/eurostat/statistics-explained/index.php/Municipal_waste_statistics': THISDIR.joinpath('ad', 'ad_EUROSTAT_2016__httpec_europa_eueurostatstatisticsexplainedindex_phpMunicipal_waste_statistics.csv'),
                  'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW)': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW.csv'),
              },
            },
            'Region: USA': {
                'Baseline Cases': {
                  'EPA, MSW trends, 2012 https://www.epa.gov/sites/production/files/2015-09/documents/2012_msw_fs.pdf': THISDIR.joinpath('ad', 'ad_EPA_MSW_trends_2012_httpswww_epa_govsitesproductionfiles201509documents2012_msw_fs_pdf.csv'),
                  'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
                  'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW)': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'Drawdown Customized Scenario 1', 'include': True,
                'description': (
                    'This scenario uses mainly the high growth prognostication from existing '
                    'sources, (See Adoption Data sheet for the Mean+1 SD projection). The '
                    'adoption is limited for later years by feedstocks however. This is a result '
                    'of integration with other solutions in Project Drawdown. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_1.csv')},
            {'name': 'Drawdown Customized Scenario 2', 'include': True,
                'description': (
                    'This scenario uses mainly the high growth prognostication from existing '
                    'sources until 2029, (See Adoption Data sheet for the Mean+1 SD projection) '
                    'then is optimized to approach 98% of the organic feedstock by 2060 (using '
                    'integrated data across all Materials and Food solutions in Project '
                    "Drawdown's Solution Set). "
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_2.csv')},
            {'name': 'Drawdown Customized Scenario 3', 'include': True,
                'description': (
                    'This scenario considers the total current USA portion of solid waste as '
                    'calculated by taking the reliable EPA data from 2014 and dividing it by the '
                    "2014 TAM derived from the multiple TAM sources on 'TAM Data.'  This USA "
                    'percentage is considered the "optimistic and plausible ceiling" for '
                    'adoption of composting of MSW and for each region, the current 2014 % '
                    'adoption of compost of organic MSW is taken as the base and a linear '
                    'increase in adoption is forecast until it reaches the USA percentage in '
                    '2050.  The resulting percentages for each year are multiplied against the '
                    'TAM (Organic fraction MSW) to derive a schedule of forecast values of MMT '
                    'of  Composted MSW for each Drawdown region and summed for the World.  This '
                    'provides another projection which is more conservative than the EU ceiling '
                    'scenario. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_3.csv')},
            {'name': 'Drawdown Customized Scenario 4', 'include': True,
                'description': (
                    'This scenario considers the total current EU portion of solid waste as '
                    'calculated by taking the reliable Eurostat data from 2014 and dividing it '
                    "by the 2014 TAM derived from the multiple TAM sources on 'TAM Data.'  This "
                    'EU percentage is considered the "optimistic and plausible ceiling" for '
                    'adoption of composting of MSW and for each region the current 2014 % '
                    'adoption of compost of organic MSW is taken as the base and a linear '
                    'increase in adoption is forecast until it reaches the EU percentage in '
                    '2050.  The resulting percentages for each year are multiplied against the '
                    'TAM (Organic fraction MSW) to derive a schedule of forecast values of MMT '
                    'of  Composted MSW for each Drawdown region and summed for the World. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_4.csv')},
            {'name': 'PDS 1 Post Integration Aug 2019', 'include': True,
                'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_1_Post_Integration_Aug_2019.csv')},
            {'name': 'PDS 2 Post Integration Aug 2019', 'include': True,
                'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_2_Post_Integration_Aug_2019.csv')},
            {'name': 'PDS 3 Post Integration Aug 2019', 'include': True,
                'description': (
                    '[PLEASE DESCRIBE IN DETAIL  THE METHODOLOGY YOU USED IN THIS ANALYSIS. BE '
                    'SURE TO INCLUDE ANY ADDITIONAL EQUATIONS YOU UTILIZED] '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS_3_Post_Integration_Aug_2019.csv')},
            {'name': 'PDS1-US Growth Path, May2020', 'include': True,
                'description': (
                    'All regions follow the growth path of the US starting with their 2016 '
                    'adoption % rate '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1US_Growth_Path_May2020.csv')},
            {'name': 'PDS2-EU Growth Path, May 2020', 'include': True,
                'description': (
                    'All regions follow the EU growth path starting with their 2016 adoption '
                    'percent '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2EU_Growth_Path_May_2020.csv')},
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
            ref_tam_per_region.loc[2016])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2016] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2016] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
            use_first_pds_datapoint_main=False,
            copy_pds_to_ref=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

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

