"""Aircraft Fuel Efficiency solution model.
   Excel filename: Drawdown-Aircraft Fuel Efficiency_RRS_v1.1_5Dec2018_PUBLIC.xlsm
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
      use_weight=True),
  'SOLUTION Average Annual Use': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
      use_weight=True),
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
  'Average Seat Capacity - Single Aisle': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_Seat_Capacity_Single_Aisle.csv"),
      use_weight=False),
  'Average Stage Length Flown of Total Operating Fleet in the world (Distances traveled from takeoff to landing)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_Stage_Length_Flown_of_Total_Operating_Fleet_in_the_world_Distances_traveled_from_takeoff_to_landing.csv"),
      use_weight=False),
  'Average fleet-wide working hours per day': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_fleet_wide_working_hours_per_day.csv"),
      use_weight=False),
  'Average time (hrs) between consecutive flights)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_time_hrs_between_consecutive_flights.csv"),
      use_weight=False),
  'Average Cruise Speed - Single Aisle': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_Cruise_Speed_Single_Aisle.csv"),
      use_weight=False),
  'Solution Load Factor': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Solution_Load_Factor.csv"),
      use_weight=False),
  'Discount Rate - Commercial': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Discount_Rate_Commercial.csv"),
      use_weight=False),
  'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'Average Seat Capacity - Twin Aisle': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_Seat_Capacity_Twin_Aisle.csv"),
      use_weight=False),
  'Average Cruise Speed - Twin Aisle': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_Cruise_Speed_Twin_Aisle.csv"),
      use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": "Aircraft",
  "functional unit": "Billion passenger km",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Aircraft Fuel Efficiency'
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
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    tam_ref_data_sources = {
      'Baseline Cases': {
          'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('tam', 'tam_based_on_IEA_ETP_2016_6DS.csv'),
          'ICCT (2012) Global Roadmap Model': THISDIR.joinpath('tam', 'tam_ICCT_2012_Global_Roadmap_Model.csv'),
      },
      'Conservative Cases': {
          'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('tam', 'tam_based_on_IEA_ETP_2016_4DS.csv'),
      },
      'Ambitious Cases': {
          'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('tam', 'tam_based_on_IEA_ETP_2016_2DS.csv'),
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
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0], dtype=np.object).set_index('param')
    ad_data_sources = {
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'PDS1 - Drawdown Projection of Production of Efficient Aircraft of Airbus and Boeing and Third Manufacturer at 13%', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_Drawdown_Projection_of_Production_of_Efficient_Aircraft_of_Airbus_and_Boeing_and_Th_0625227c.csv')},
      {'name': 'PDS2 - Drawdown Projection of Production of Efficient Aircraft of Airbus and Boeing and Third Manufacturer at 18%', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_Drawdown_Projection_of_Production_of_Efficient_Aircraft_of_Airbus_and_Boeing_and_Th_c6a70599.csv')},
      {'name': 'PDS3 - Drawdown Projection of Production of Efficient Aircraft of Airbus and Boeing and Third Manufacturer at 20%', 'include': False,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS3_Drawdown_Projection_of_Production_of_Efficient_Aircraft_of_Airbus_and_Boeing_and_Th_42d0f286.csv')},
      {'name': 'Book Ed.1 Scenario 1', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_1.csv')},
      {'name': 'Book Ed.1 Scenario 2', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Book_Ed_1_Scenario_2.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
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
      [490.5239834755743, 0.0, 0.0, 0.0, 0.0,
       0.0, 0.0, 0.0, 0.0, 0.0],
       index=dd.REGIONS)
    ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=pds_tam_per_region,
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

