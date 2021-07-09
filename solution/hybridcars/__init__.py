"""Car Fuel Efficiency solution model.
   Excel filename: HybridCars-RRSv1.1b-Nov2019.xlsm
"""

import pathlib

import numpy as np
import pandas as pd
import openpyxl

from model import adoptiondata
from model import advanced_controls as ac
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import dd
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import interpolation
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
        use_weight=True),
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
        use_weight=False),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fixed_Operating_Cost_FOM.csv"),
        use_weight=False),
    'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Fixed_Operating_Cost_FOM.csv"),
        use_weight=False),
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'Urban Travel TAM - Current': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Urban_Travel_TAM_Current.csv"),
        use_weight=False),
    'Urban Travel TAM - Projected': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Urban_Travel_TAM_Projected.csv"),
        use_weight=False),
    'Interurban Travel TAM - Current': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Interurban_Travel_TAM_Current.csv"),
        use_weight=False),
    'Interurban Travel TAM - Projected': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Interurban_Travel_TAM_Projected.csv"),
        use_weight=False),
    'Average Global Car Occupancy - Conventional': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Global_Car_Occupancy_Conventional.csv"),
        use_weight=False),
    'Discount Rate: Households': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rate_Households.csv"),
        use_weight=False),
    'Learning Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Learning_Rate.csv"),
        use_weight=False),
    'Average Global Car Occupancy - Solution': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Global_Car_Occupancy_Solution.csv"),
        use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "Car",
    "functional unit": "passenger-km",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Car Fuel Efficiency'
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
        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
        tam_ref_data_sources = {
              'Baseline Cases': {
                  'Based on IEA (2016), "Energy Technology Perspectives - 6DS", IEA/OECD': THISDIR.joinpath('tam', 'tam_based_on_IEA_2016_Energy_Technology_Perspectives_6DS_IEAOECD.csv'),
                  'Based on ICCT (2012) "Global Transport Roadmap Model", http://www.theicct.org/global-transportation-roadmap-model': THISDIR.joinpath('tam', 'tam_based_on_ICCT_2012_Global_Transport_Roadmap_Model_httpwww_theicct_orgglobaltransportatio_8916596a.csv'),
            },
              'Conservative Cases': {
                  'Based on IEA (2016), "Energy Technology Perspectives - 4DS", IEA/OECD': THISDIR.joinpath('tam', 'tam_based_on_IEA_2016_Energy_Technology_Perspectives_4DS_IEAOECD.csv'),
            },
              'Ambitious Cases': {
                  'Based on IEA (2016), "Energy Technology Perspectives - 2DS", IEA/OECD': THISDIR.joinpath('tam', 'tam_based_on_IEA_2016_Energy_Technology_Perspectives_2DS_IEAOECD.csv'),
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
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
            'Conservative Cases': {
                'Navigant Research': THISDIR.joinpath('ad', 'ad_Navigant_Research.csv'),
                'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
                'Based on Clean Energy Manufacturing Analysis Center': THISDIR.joinpath('ad', 'ad_based_on_Clean_Energy_Manufacturing_Analysis_Center.csv'),
            },
            'Ambitious Cases': {
                'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                'Interpolation Based on World Energy Council 2011 - Global Transport Scenarios 2050': THISDIR.joinpath('ad', 'ad_Interpolation_based_on_World_Energy_Council_2011_Global_Transport_Scenarios_2050.csv'),
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        wb = openpyxl.load_workbook(filename=THISDIR.joinpath('hybridcarsdata.xlsx'), data_only=True)
        raw_sales = pd.read_excel(wb, sheet_name='HEV Sales', header=0, index_col=0,
                usecols='A:K', dtype='float', engine='openpyxl', skiprows=7, nrows=43)
        hev_sales = raw_sales.rename(axis='columns', mapper={
            'World ': 'World',
            'OECD90 (US, EU Japan, Canada)': 'OECD90',
            'Asia sans Japan (China, India & Other.)': 'Asia (Sans Japan)',
            'Middle East & Africa': 'Middle East and Africa'}).fillna(0.0)
        lifetime = int(np.ceil(self.ac.soln_lifetime_replacement))
        sales_extended = hev_sales.copy()
        for year in range(2019, 2061):
            sales_extended.loc[year, :] = 0.0
        vehicle_retirements = sales_extended.shift(periods=lifetime, fill_value=0.0)
        hev_stock = (hev_sales - vehicle_retirements).cumsum()
        pass_km_adoption = hev_stock * self.ac.soln_avg_annual_use

        # HybridCars.xlsm 'Data Interpolator'!H1582, Adoption Data
        # Project Drawdown Analysis based on Market Reports and a Drop in HEV
        # in later years (replaced by EVs) - PDS2
        predict = pd.read_csv(
                THISDIR.joinpath('ca_pds_data', 'pass_km_datapoints_PDS2.csv'),
                skipinitialspace=True, comment='#', index_col=0, squeeze=True)
        pass_km_predicted = interpolation.poly_degree3_trend(predict)['adoption']
        pass_km_predicted.update(predict.loc[:2018])  # Early years adjusted to be actual values
        integration_pds2 = pd.read_csv(THISDIR.joinpath('tam', 'integration_PDS2.csv'),
                skipinitialspace=True, comment='#', index_col=0)
        tam_limit_pds2 = 0.95 * (integration_pds2['URBAN'] + integration_pds2['NONURBAN']) * 1e9
        world = pd.concat([pass_km_adoption.loc[2012:2016, 'World'], pass_km_predicted.loc[2017:]])
        ds1_df = pd.DataFrame(0, columns=dd.REGIONS, index=range(2012, 2061))
        ds1_df['World'] = world.clip(upper=tam_limit_pds2, lower=0.0, axis=0)

        # Data Source 2
        predict = pd.read_csv(
                THISDIR.joinpath('ca_pds_data', 'pass_km_datapoints_PDS3.csv'),
                skipinitialspace=True, comment='#', index_col=0, squeeze=True)
        pass_km_predicted = interpolation.poly_degree3_trend(predict)['adoption']
        pass_km_predicted.update(predict.loc[:2018])  # Early years adjusted to be actual values
        integration_pds3 = pd.read_csv(THISDIR.joinpath('tam', 'integration_PDS3.csv'),
                skipinitialspace=True, comment='#', index_col=0)
        intg_limit = (integration_pds3['URBAN'] + integration_pds3['NONURBAN']) * 1e9
        tam_limit_pds3 = pd.concat([(intg_limit.loc[:2035] * 0.95), (intg_limit.loc[2036:] * 0.9)])
        world = pd.concat([pass_km_adoption.loc[2012:2016, 'World'], pass_km_predicted.loc[2017:]])
        ds2_df = pd.DataFrame(0, columns=dd.REGIONS, index=range(2012, 2061))
        ds2_df['World'] = world.clip(upper=tam_limit_pds3, lower=0.0, axis=0)

        ca_pds_data_sources = [
            {'name': 'PDS2-Transition to EVs in Cities', 'include': True,
                'description': (
                    'Considering that Electric Vehicles (BEV or PHEV)  are a better technology '
                    'from a lifetime emissions perspective, HEV are considered as a transition '
                    'technology in the PDS2  where the target is drawdown by 2050 particularly '
                    'within cities where there is minimal range anxiety. In this Drawdown '
                    'scenario, then, the focus is on growing EV after all higher priority '
                    'solutions (like non-motorized transportation) in cities are grown to their '
                    "maximum potential. For HEV's then, the adoption is projected to only occur "
                    'where BEV or PHEV cars cannot easily be used, such as for long distance '
                    'intercity trips until perhaps around 2025 when EV battery technology can be '
                    'assumed to be adequate enough to eliminate all range anxiety. The HEV '
                    'adoption is projected to continue its growth until around 2025 when it '
                    'starts to decline and trend to zero by or before 2050. Sales data for '
                    'multiple key countries and regions were used to estimate the actual global '
                    "sales. Using the model's lifetime data, the older HEVs are removed from the "
                    'fleet while aggregating the total sales to get the total stock per year. '
                    'With these, the projected sales from IEA are used to project increments to '
                    'the existing stock to 2050 (latest data vailable). Stock data are converted '
                    "to usage with model's Advanced Controls input.  All scenarios are limited "
                    'by integrated TAM after removing adoptions of higher priority solutions. '
                    ),
                'dataframe': ds1_df},
            {'name': 'PDS3-Transition to EVs', 'include': True,
                'description': (
                    'Considering that Electric Vehicles (BEV or PHEV)  are a better technology '
                    'from a lifetime emissions perspective, HEV are considered as a transition '
                    'technology in the PDS3  where the target is maximizing emissions reduction. '
                    'In this scenario, then, the focus is on growing EV after all higher '
                    'priority solutions (like non-motorized transportation)  are grown to their '
                    'maximum potential. As soon as possible, HEV sales will rapidly decline. '
                    'Sales data for multiple key countries and regions were used to estimate the '
                    "actual global sales. Using the model's lifetime data, the older HEVs are "
                    'removed from the fleet while aggregating the total sales to get the total '
                    "stock per year.  Stock data are converted to usage with model's Advanced "
                    'Controls input.  All scenarios are limited by integrated TAM after removing '
                    'adoptions of higher priority solutions. '
                    ),
                'dataframe': ds2_df},
            {'name': 'Drawdown Book - Edition 1- Quick Doubling of Hybrid Car Occupancy', 'include': True,
                'description': (
                    'We take the Average of two Ambitious adoption scenarios (on Adoption Data '
                    'tab): Interpolation of IEA 2016 ETP 2DS(2016), and World Energy Council '
                    '(2011) (both with annual use of ICCT Roadmap Model). We then double the HEV '
                    'car occupancy from 2017 and interpolate back to current adoption for 2014. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Quick_Doubling_of_Hybrid_Car_Occupancy.csv')},
            {'name': 'PDS1 - Aggressive Growth from Existing Stock  based on  IEA 2DS', 'include': True,
                'description': (
                    'Sales data for multiple key countries and regions were used to estimate the '
                    "global sales. Using the model's lifetime data, the older HEVs are removed "
                    'from the fleet while aggregating the total sales to get the total stock per '
                    'year. With these, the projected sales from IEA are used to project '
                    'increments to the existing stock to 2050 (latest data vailable). Stock data '
                    "are converted to usage with model's Advanced Controls input. All scenarios "
                    'are limited by integrated TAM after removing adoptions of higher priority '
                    'solutions. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_Aggressive_Growth_from_Existing_Stock_based_on_IEA_2DS.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': 'Default REF Projection with Adjustment for Recent Historical Adoptions', 'include': True,
                'description': (
                    'We take the Default Project Drawdown REF adoption using Average Baseline '
                    'TAM data and then adjust the years 2012-2018 to be the estimated historical '
                    'adoptions from the HEV Pass-Km tab. '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Default_REF_Projection_with_Adjustment_for_Recent_Historical_Adoptions.csv')},
        ]
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
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
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            use_first_pds_datapoint_main=False,
            copy_pds_to_ref=False,
            copy_ref_datapoint=False, copy_pds_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=3)

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

