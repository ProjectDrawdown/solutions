"""Mass Transit solution model.
   Excel filename: MassTransit-RRSv1.1b-4July2019.xlsm
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
        filename=None, use_weight=False),
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
        filename=None, use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Direct_Emissions_per_Functional_Unit.csv"),
        use_weight=True),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Direct_Emissions_per_Functional_Unit.csv"),
        use_weight=True),
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
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'Car Insurance Costs': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Car_Insurance_Costs.csv"),
        use_weight=False),
    'Car Purchase (First) Costs': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Car_Purchase_First_Costs.csv"),
        use_weight=True),
    'Car Occupancy Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Car_Occupancy_Rates.csv"),
        use_weight=False),
    'Car Lifetime in Vehicle-km': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Car_Lifetime_in_Vehicle_km.csv"),
        use_weight=False),
    'Discount Rates - Household': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rates_Household.csv"),
        use_weight=False),
    'Black Carbon GWP': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Black_Carbon_GWP.csv"),
        use_weight=False),
    'Diesel Share of Global Car Fleet': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Diesel_Share_of_Global_Car_Fleet.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "Urban trip",
    "functional unit": "Pkm (urban)",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Mass Transit'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-22p2050-Based on IEA 2DS"
PDS2 = "PDS2-35p2050-Based on ITDP/UCDavis"
PDS3 = "PDS3-45p2050-Linear to 45%"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    tam_ref_data_sources = {
            'Baseline Cases': {
                'Based on ETP 2016, URBAN 6 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ETP_2016_URBAN_6_DS_Nonmotorized_Travel_Adjustment.csv'),
                'Based on ICCT, 2012, "Global Transportation Roadmap Model" + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ICCT_2012_Global_Transportation_Roadmap_Model_Nonmotorized_Travel_Adjustment.csv'),
        },
            'Conservative Cases': {
                'Based on ETP 2016, URBAN 4 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ETP_2016_URBAN_4_DS_Nonmotorized_Travel_Adjustment.csv'),
                'Based on ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - Baseline Scenario': THISDIR.joinpath('tam', 'tam_based_on_ITDPUC_Davis_2014_A_Global_High_Shift_Scenario_Updated_Report_Data_Baseline_Scenario.csv'),
        },
            'Ambitious Cases': {
                'Based on ETP 2016, URBAN 2 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_based_on_ETP_2016_URBAN_2_DS_Nonmotorized_Travel_Adjustment.csv'),
                'Based on ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - HighShift Scenario': THISDIR.joinpath('tam', 'tam_based_on_ITDPUC_Davis_2014_A_Global_High_Shift_Scenario_Updated_Report_Data_HighShift_Scenario.csv'),
        },
            'Region: OECD90': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: Eastern Europe': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: Asia (Sans Japan)': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: Middle East and Africa': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: Latin America': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: China': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: India': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: EU': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
            'Region: USA': {
                'Baseline Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - URBAN MOBILITY- Baseline': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_d1c13e61.csv'),
            },
                'Ambitious Cases': {
                'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data -URBAN MOBILITY- High shift': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_URBAN_MOBILI_f5a37b66.csv'),
            },
        },
    }
    tam_pds_data_sources=tam_ref_data_sources


    def __init__(self, scenario=None):
        if isinstance(scenario, ac.AdvancedControls):
            self.scenario = scenario.name
            self.ac = scenario
        else:
            self.scenario = scenario or PDS2
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
            'Baseline Cases': {
                'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
            },
            'Conservative Cases': {
                'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
            },
            'Ambitious Cases': {
                'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
                'PDS2-Based on ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data (high shift) with recent historical data added': THISDIR.joinpath('ad', 'ad_PDS2based_on_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_128ccfca.csv'),
            },
            'Region: OECD90': {
                'Ambitious Cases': {
                  'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_High_shift.csv'),
              },
            },
            'Region: Eastern Europe': {
                'Ambitious Cases': {
                  'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_High_shift.csv'),
              },
            },
            'Region: Asia (Sans Japan)': {
                'Ambitious Cases': {
                  'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_High_shift.csv'),
              },
            },
            'Region: Middle East and Africa': {
                'Ambitious Cases': {
                  'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_High_shift.csv'),
              },
            },
            'Region: Latin America': {
                'Ambitious Cases': {
                  'ITDP - UC Davis (2015)  A Global High Shift Cycling Scenario Updated Report Data - High shift': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Updated_Report_Data_High_shift.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'Drawdown Book Edition 1 Scenario 1', 'include': True,
                'description': (
                    'This scenario fits a linear curve to data from the IEA 2DS projection of '
                    'mass transit adoption. The scenario was used in the Drawdown book edition '
                    '1, and has been updated. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_1.csv')},
            {'name': 'Drawdown Book Edition 1 Scenario 2', 'include': True,
                'description': (
                    'This scenario fits a 3rd degree polynomial curve to data from the '
                    'ITDP/UCDavis Global High Shift projection of mass transit adoption. The '
                    'scenario was used in the Drawdown book edition 1, and has been updated. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_2.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': 'Custom REF Adoption - Fixed Mass Transit Pass-km Annually', 'include': True,
                'description': (
                    'Taking the estimated passenger-km adoption value from 2014, we hold that '
                    'constant out to 2050 which assumes that the total amount of travel on urban '
                    'mass transit systems remains constant despite increasing populations. The '
                    'rapid rise in populations generally happens in developing countries, and as '
                    'these countries urbanise and get wealthier, there is a large trend towards '
                    'increased motorization following the historical patterns of Western '
                    'Nations. This then, although a pessimistic case, is not unrealistic. '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Custom_REF_Adoption_Fixed_Mass_Transit_Passkm_Annually.csv')},
            {'name': 'Adoption Based on IEA 6DS', 'include': True,
                'description': (
                    'This scenario uses the interpolated data from the IEA 6DS of the ETP 2016 '
                    'Report with a smoothening to the current and recent adoptions (2012-2018). '
                    'Since the standard Ref assumption of fixed % adoption is seen as  too '
                    'optimistic considering the trends in urban mobility of greatly increasing '
                    'car ownership in the developing world where large populations exist. '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Adoption_based_on_IEA_6DS.csv')},
        ]
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=ref_tam_per_region)

        ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

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
            use_first_pds_datapoint_main=False,
            copy_pds_to_ref=True, copy_ref_datapoint=False,
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

