"""Electric Vehicles solution model.
   Excel filename: EVs-Modelv1.1c-Apr2020.xlsm
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
        use_weight=True),
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
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Total_Energy_Used_per_Functional_Unit.csv"),
        use_weight=True),
    'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fuel_Consumed_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Fuel_Efficiency_Factor.csv"),
        use_weight=True),
    'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=True),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Car Occupancy': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Car_Occupancy.csv"),
        use_weight=False),
    'Fraction of BEV+PHEV market that is BEV': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Fraction_of_BEV_PHEV_market_that_is_BEV.csv"),
        use_weight=False),
    'Discount Rates - Households': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rates_Households.csv"),
        use_weight=False),
    'CONVENTIONAL Car Occupancy': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Car_Occupancy.csv"),
        use_weight=False),
    'EV Learning Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "EV_Learning_Rate.csv"),
        use_weight=False),
    'Average Annual EV Car Vehicle km': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Annual_EV_Car_Vehicle_km.csv"),
        use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "vehicle",
    "functional unit": "billion passenger-km",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Electric Vehicles'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-16p2050-with IEA 2DS (Integrated)"
PDS2 = "PDS2-23p2050-using IEA B2DS (Integrated)"
PDS3 = "PDS3-18p2050-Survival Analysis (Integrated)"

class Scenario(scenario.Scenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    def __init__(self, scenario=None):
        if isinstance(scenario, ac.AdvancedControls):
            self.scenario = scenario.name
            self.ac = scenario
        else:
            self.scenario = scenario or PDS2
            self.ac = scenarios[self.scenario]

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
            'Baseline Cases': {
                'Based on IEA Reference Tech Scenario- 2017': THISDIR.joinpath('ad', 'ad_based_on_IEA_Reference_Tech_Scenario_2017.csv'),
            },
            'Conservative Cases': {
                'Based on OPEC World Energy Outlook 2016': THISDIR.joinpath('ad', 'ad_based_on_OPEC_World_Energy_Outlook_2016.csv'),
                'Based on The Paris Declaration as Cited in (IEA, 2017- EV Outlook)': THISDIR.joinpath('ad', 'ad_based_on_The_Paris_Declaration_as_Cited_in_IEA_2017_EV_Outlook.csv'),
            },
            'Ambitious Cases': {
                'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                'Based on Bloomberg New Energy Finance - EV Outlook 2017': THISDIR.joinpath('ad', 'ad_based_on_Bloomberg_New_Energy_Finance_EV_Outlook_2017.csv'),
                'Based on IEA Beyond 2DS/B2DS Scenario': THISDIR.joinpath('ad', 'ad_based_on_IEA_Beyond_2DSB2DS_Scenario.csv'),
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data

        # Data about EV Sales comes from sheets from the original Excel implementation
        wb = openpyxl.load_workbook(filename=THISDIR.joinpath('electricvehicledata.xlsx'), data_only=True)
        raw_sales = pd.read_excel(wb, sheet_name='EV Sales', header=0, index_col=0,
                usecols='A:K', dtype='float', engine='openpyxl', skiprows=7, nrows=43)
        ev_sales = raw_sales.rename(axis='columns', mapper={
            'World ': 'World',
            'OECD90 (US, EU Japan, Canada)': 'OECD90',
            'Asia sans Japan (China, India & Other.)': 'Asia (Sans Japan)',
            'Middle East & Africa': 'Middle East and Africa'}).fillna(0.0)
        lifetime = int(np.ceil(self.ac.soln_lifetime_replacement))
        sales_extended = ev_sales.copy()
        for year in range(2051, 2061):
            sales_extended.loc[year, :] = 0.0
        vehicle_retirements = sales_extended.shift(periods=lifetime, fill_value=0.0)
        ev_stock = (ev_sales - vehicle_retirements).cumsum()
        pass_km_adoption = ev_stock * self.ac.soln_avg_annual_use

        # Data Source 1
        # EVs.xlsm 'Data Interpolation'!H1181, Adoption Data
        # Based on IEA EV Outlook, 2017 - B2DS Scenario
        predict = pd.Series([16.7014449161593, 35.1749574468086, 49.2449404255312,
                635.494231205675, 2239.47229078014, 5072.22886382977],
                index=[2014, 2015, 2016, 2020, 2025, 2030])
        pass_km_predicted = interpolation.poly_degree3_trend(predict)['adoption']
        pass_km_predicted.update(predict)
        integration_pds2 = pd.read_csv(THISDIR.joinpath('tam', 'integration_PDS2.csv'),
                skipinitialspace=True, comment='#', index_col=0)
        tam_limit_pds2 = integration_pds2['URBAN'] + (0.3 * integration_pds2['NONURBAN'])
        world = pd.concat([pass_km_adoption.loc[2012:2019, 'World'], pass_km_predicted.loc[2020:]])
        ds1_df = pd.DataFrame(0, columns=dd.REGIONS, index=range(2012, 2061))
        ds1_df['World'] = world.clip(upper=tam_limit_pds2, axis=0)

        # Data Source 2
        raw = pd.read_excel(wb, sheet_name='Vehicle Survival', header=0, index_col=None,
                usecols='D:AR', dtype='float', engine='openpyxl', skiprows=8, nrows=5).T
        survival_ds2 = pd.concat([ev_stock.loc[:2019, 'World'], raw[3]])
        capture_pct_ds2 = raw[4]
        car_usage = 15765.0  # https://theicct.org/global-transportation-roadmap-model (now 404s)
        car_occupancy = self.ac.lookup_vma(vma_title='Current Average Car Occupancy')
        survival_ad_ds2 = survival_ds2 * car_usage * car_occupancy / 1e9
        replace_ds2 = (survival_ds2 * capture_pct_ds2).cumsum().subtract(vehicle_retirements['World'], fill_value=0.0)
        pass_km_potential_ds2 = replace_ds2 * self.ac.conv_avg_annual_use
        adoption_ds2 = pd.concat([survival_ad_ds2.loc[:2019], pass_km_potential_ds2.loc[2020:]])
        integration_pds3 = pd.read_csv(THISDIR.joinpath('tam', 'integration_PDS3.csv'),
                skipinitialspace=True, comment='#', index_col=0)
        tam_limit_pds3 = integration_pds3['URBAN'] + (0.3 * integration_pds3['NONURBAN'])
        ds2_df = pd.DataFrame(0, columns=dd.REGIONS, index=range(2012, 2061))
        ds2_df['World'] = adoption_ds2.clip(upper=tam_limit_pds3, axis=0)

        ca_pds_data_sources = [
            {'name': 'PDS2-Based on IEA (2017) B2DS', 'include': True,
                'description': (
                    'In this Scenario, we incorporate the highest published stock scenario of '
                    "EV's currently in the literature: the IEA B2DS scenario of 2017. We take the "
                    "Beyond 2 Degree Scenario projections from the IEA of number of EV's in the "
                    'global fleet, convert to estimated passenger-km with a fixed factor and we '
                    'interpolate and extrapolate to estimate missing years with a 3rd degree '
                    'polynomial curve fit. We then limit this to the total projected TAM each '
                    'year after higher priority solutions have supplied their full projection in '
                    'PDS2 (Higher priority solutions are: Walkable Cities, Bike Infrastructure, '
                    'E-Bikes, Mass Transit and Carsharing/Ridesharing) '
                    ),
                'dataframe': ds1_df},
            {'name': 'PDS3-Based on Replacing All Retired Cars from Survival Analysis', 'include': True,
                'description': (
                    'In this Optimum Scenario, to estimate the Fastest that a New Car Technology '
                    'can Diffuse into the Global Fleet - assuming that from time of car '
                    'replacement, new technology is used. Weibull distributions are assumed '
                    'using the Weibull Survival data from ICCT Global Roadmap model v1.0 for 6 '
                    'countries (China, USA, Canada, Brazil, Mexico and India). Using these, we '
                    'estimate the proportion of cars in each country that are scrapped or '
                    'retired X years after purchase date (0 <= X <= 40). Combining this with '
                    'vehicle sales data for each of the selected countries (mainly from OICA '
                    'database), we estimate how many cars should be retiring each year. Assuming '
                    'the average retiring rate of these selected countries applies to entire '
                    'world, we scale up the retired cars to global fleet and then convert from '
                    'cars to pass-km. We then limit this to the total projected TAM each year '
                    'after higher priority solutions have supplied their full projection in PDS3 '
                    '(Higher priority solutions are: Walkable Cities, Bike Infrastructure, '
                    'E-Bikes, Mass Transit and Carsharing/Ridesharing) '
                    ),
                'dataframe': ds2_df},
            {'name': 'Book Ed.1 Scenario 1', 'include': False,
                'description': (
                    'Starting with the IEA 2DS Projection of EV in the Global stock, we '
                    'interpolate and apply a fixed car occupancy to 2050. Minor adjustments are '
                    'made to early years to ensure smoothness of the adoption curve. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_1.csv')},
            {'name': 'Book Ed.1 Scenario 2', 'include': False,
                'description': (
                    "Using the IEA's Energy Technology Perspectives 2012 projections of EV "
                    "sales' growth, we project the sales and then global EV stock. Assuming the "
                    "ICCT's global car occupancy average and a 50% growth in this occupancy by "
                    '2050, we estimate the total passenger-km of EV during the period of '
                    'analysis. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_2.csv')},
            {'name': 'Book Ed.1 Scenario 3', 'include': False,
                'description': (
                    "Using the IEA's Energy Technology Perspectives 2012 projections of EV "
                    "sales' growth, we project the sales and then global EV stock. Assuming "
                    "twice the ICCT's global car occupancy average, we estimate the total "
                    "passenger-km of EV during the period of analysis. "
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_3.csv')},
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
            copy_pds_to_ref=True, copy_ref_datapoint=False, copy_pds_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=3)

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

