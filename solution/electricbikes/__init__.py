"""Electric Bicycles solution model.
   Excel filename: Ebike-RRSv1.1b-9Apr20.xlsm
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
        use_weight=True),
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
        use_weight=True),
    'SOLUTION Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
        use_weight=True),
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
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=True),
    'Indirect CO2 Emissions per SOLUTION Unit (Select on Advanced Controls)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Indirect_CO2_Emissions_per_SOLUTION_Unit_Select_on_Advanced_Controls.csv"),
        use_weight=True),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'Average Car Occupancy': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Car_Occupancy.csv"),
        use_weight=False),
    'Average Car Lifetime': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Car_Lifetime.csv"),
        use_weight=False),
    'Discount Rates - Households': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rates_Households.csv"),
        use_weight=False),
    'Average Annual Passenger-km per Car': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Annual_Passenger_km_per_Car.csv"),
        use_weight=False),
    'First Cost of ICE Car': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "First_Cost_of_ICE_Car.csv"),
        use_weight=True),
    'Average Bike Pass-km per Year': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Average_Bike_Pass_km_per_Year.csv"),
        use_weight=False),
    'E-bike Battery Size': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "E_bike_Battery_Size.csv"),
        use_weight=True),
    'E-bike Work Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "E_bike_Work_Rate.csv"),
        use_weight=False),
    'Percentage of E-bike Rides with 2 Riders': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Percentage_of_E_bike_Rides_with_2_Riders.csv"),
        use_weight=False),
    'Fuel Consumed per pkm - CONVENTIONAL': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Fuel_Consumed_per_pkm_CONVENTIONAL.csv"),
        use_weight=False),
    'Car Maintenance  Cost per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Car_Maintenance_Cost_per_Functional_Unit.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "MWh of Batteries",
    "functional unit": "Billion PKM",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Electric Bicycles'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-3p2050_Based on Navigant, Bloomberg (Book Ed.1)"
PDS2 = "PDS2-5p2050_Based on ITDP/UCD (Book Ed.1)"
PDS3 = "PDS3-6p2050_Growth to 6.5% (Book Ed.1)"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    _ref_tam_sources = {
        'Baseline Cases': {
            'ETP 2016, URBAN 6 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ETP_2016_URBAN_6_DS_Nonmotorized_Travel_Adjustment.csv'),
            'ICCT, 2012, "Global Transportation Roadmap Model" + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ICCT_2012_Global_Transportation_Roadmap_Model_Nonmotorized_Travel_Adjustment.csv'),
        },
        'Conservative Cases': {
            'ETP 2016, URBAN 4 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ETP_2016_URBAN_4_DS_Nonmotorized_Travel_Adjustment.csv'),
            'ITDP/UC Davis 2014 Global High Shift Baseline': THISDIR.joinpath('tam', 'tam_ITDPUC_Davis_2014_Global_High_Shift_Baseline.csv'),
        },
        'Ambitious Cases': {
            'ETP 2016, URBAN 2 DS + Non-motorized Travel Adjustment': THISDIR.joinpath('tam', 'tam_ETP_2016_URBAN_2_DS_Nonmotorized_Travel_Adjustment.csv'),
            'ITDP/UC Davis 2014 Global High Shift HighShift': THISDIR.joinpath('tam', 'tam_ITDPUC_Davis_2014_Global_High_Shift_HighShift.csv'),
        },
        'Region: OECD90': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: Eastern Europe': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: Asia (Sans Japan)': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: Middle East and Africa': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: Latin America': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: China': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: India': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: EU': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
        'Region: USA': {
            'Baseline Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Ambitious Cases': {
                'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('tam', 'tam_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
            },
        },
    }
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
            'Baseline Cases': {
                'ITDP and UCD (2015) "A Global Highshift Cycling Scenario" - Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_and_UCD_2015_A_Global_Highshift_Cycling_Scenario_Baseline_Scenario.csv'),
            },
            'Conservative Cases': {
                'Drawdown Team based on Data from Navigant, Bloomberg and other Sources': THISDIR.joinpath('ad', 'ad_Drawdown_Team_based_on_Data_from_Navigant_Bloomberg_and_other_Sources.csv'),
            },
            'Ambitious Cases': {
                'ITDP and UCD (2015) "A Global Highshift Cycling Scenario" - Highshift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_and_UCD_2015_A_Global_Highshift_Cycling_Scenario_Highshift_Scenario.csv'),
            },
            'Region: OECD90': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Conservative Cases': {
                  'Drawdown Team based on Data from Navigant, Bloomberg and other Sources': THISDIR.joinpath('ad', 'ad_Drawdown_Team_based_on_Data_from_Navigant_Bloomberg_and_other_Sources.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: Eastern Europe': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Conservative Cases': {
                  'Drawdown Team based on Data from Navigant, Bloomberg and other Sources': THISDIR.joinpath('ad', 'ad_Drawdown_Team_based_on_Data_from_Navigant_Bloomberg_and_other_Sources.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: Asia (Sans Japan)': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Conservative Cases': {
                  'Drawdown Team based on Data from Navigant, Bloomberg and other Sources': THISDIR.joinpath('ad', 'ad_Drawdown_Team_based_on_Data_from_Navigant_Bloomberg_and_other_Sources.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: Middle East and Africa': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Conservative Cases': {
                  'Drawdown Team based on Data from Navigant, Bloomberg and other Sources': THISDIR.joinpath('ad', 'ad_Drawdown_Team_based_on_Data_from_Navigant_Bloomberg_and_other_Sources.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: Latin America': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Conservative Cases': {
                  'Drawdown Team based on Data from Navigant, Bloomberg and other Sources': THISDIR.joinpath('ad', 'ad_Drawdown_Team_based_on_Data_from_Navigant_Bloomberg_and_other_Sources.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: China': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: India': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: EU': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
            'Region: USA': {
                'Baseline Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, Baseline Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_Baseline_Scenario.csv'),
              },
                'Ambitious Cases': {
                  'ITDP, UC Davis (2015) A Global High Shift Cycling Scenario, High shift Scenario': THISDIR.joinpath('ad', 'ad_ITDP_UC_Davis_2015_A_Global_High_Shift_Cycling_Scenario_High_shift_Scenario.csv'),
              },
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_data_sources = [
            {'name': 'Book Ed.1 Scenario 1', 'include': True,
                'description': (
                    'Using estimated projections of e-bike sales from Navigant, and Bloomberg, '
                    'along with estimated growth rates of sales for missing years, and assumed '
                    'bike lifetimes (really battery lifetimes as these dominate), estimated '
                    'e-bike stocks are developed for each Drawdown region (OECD90, Eastern '
                    'Europe, Asia sans Japan, Middle East and Africa and Latin America). These '
                    'are assumed to each have a fixed number of passenger-km per year based on '
                    '10 km per workday and 5km per weekend day with a ridership of 1.05 '
                    'considering the popularity of multiple riders on Chinese e-bikes. the '
                    'resulting passenger-km are summed for global results. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_1.csv')},
            {'name': 'Book Ed.1 Scenario 2', 'include': True,
                'description': (
                    'Using estimated projections of e-bike pass-km of ITDP/UCD, best fit curves '
                    'were developed using 3rd degree polynomial functions. '
                    ),
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_2.csv')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': 'Book Reference Scenario', 'include': True,
                'description': (
                    'The previously developed Reference scenario, as with most Drawdown models, '
                    'is based on the TAM data and modeling. Therefore as thse inputs have '
                    'changed in the new model, the Reference adoption is also different. The '
                    'previous reference adoption is recorded here for the Book Scenarios. '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Book_Reference_Scenario.csv')},
            {'name': 'Default REF Projection with Adjustment for Recent Historical Adoptions', 'include': True,
                'description': (
                    'We take the Default Project Drawdown REF adoption using Average Baseline '
                    'TAM data and then adjust the years 2012-2018 to be the estimated historical '
                    'adoptions from the Modeshare URBAN tab. '
                    ),
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Default_REF_Projection_with_Adjustment_for_Recent_Historical_Adoptions.csv')},
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
            copy_pds_to_ref=False, copy_ref_datapoint=False,
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

