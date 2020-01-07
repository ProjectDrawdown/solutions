"""Conservation Agriculture solution model.
   Excel filename: Drawdown-Conservation Agriculture_BioS.Agri_v1.1_2Jan2019_PUBLIC.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import aez
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
from model import tla
from solution import land

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
      use_weight=False),
  'CONVENTIONAL Operating Cost per Functional Unit per Annum': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
      use_weight=True),
  'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
      use_weight=True),
  'CONVENTIONAL Net Profit Margin per Functional Unit per Annum': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
      use_weight=True),
  'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
      use_weight=True),
  'Yield from CONVENTIONAL Practice': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Yield_from_CONVENTIONAL_Practice.csv"),
      use_weight=True),
  'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Yield_Gain_Increase_from_CONVENTIONAL_to_SOLUTION.csv"),
      use_weight=False),
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
  't CO2-eq (Aggregate emissions) Reduced per Land Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "t_CO2_eq_Aggregate_emissions_Reduced_per_Land_Unit.csv"),
      use_weight=False),
  't CO2 Reduced per Land Unit': vma.VMA(
      filename=None, use_weight=False),
  't N2O-CO2-eq Reduced per Land Unit': vma.VMA(
      filename=None, use_weight=False),
  't CH4-CO2-eq Reduced per Land Unit': vma.VMA(
      filename=None, use_weight=False),
  'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE': vma.VMA(
      filename=None, use_weight=False),
  'Indirect CO2 Emissions per  Implementation Unit - SOLUTION': vma.VMA(
      filename=None, use_weight=False),
  'Sequestration Rates': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
      use_weight=False),
  'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing': vma.VMA(
      filename=None, use_weight=False),
  'Disturbance Rate': vma.VMA(
      filename=None, use_weight=False),
  'Dataset to Use for Projecting Adoption': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Dataset_to_Use_for_Projecting_Adoption.csv"),
      use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": None,
  "functional unit": "Mha",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Conservation Agriculture'
solution_category = ac.SOLUTION_CATEGORY.LAND

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

    # TLA
    self.ae = aez.AEZ(solution_name=self.name)
    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Low,High Early Adoption, Polynomial Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_LowHigh_Early_Adoption_Polynomial_Trend.csv')},
      {'name': 'High,High Early Adoption, Polynomial Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_HighHigh_Early_Adoption_Polynomial_Trend.csv')},
      {'name': 'Max, Polynomial Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Max_Polynomial_Trend.csv')},
      {'name': 'High, Early Adoption, Polynomial Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_High_Early_Adoption_Polynomial_Trend.csv')},
      {'name': 'Low, Early Adoption, Polynomial Trend', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_Early_Adoption_Polynomial_Trend.csv')},
    ]
    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
        total_adoption_limit=self.tla_per_region)


    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [71.6843318543261, 21.7864515209236, 5.79724982776745, 7.68605153649748, 0.244451347436256,
       36.1701276217012, 0.0, 0.0, 0.0, 0.0],
       index=dd.REGIONS)
    ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial / self.tla_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
    ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
    ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        pds_adoption_data_per_region=pds_adoption_data_per_region,
        ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac,
        ref_total_adoption_units=self.tla_per_region, pds_total_adoption_units=self.tla_per_region,
        electricity_unit_factor=1000000.0,
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
        conv_ref_first_cost_uses_tot_units=True,
        fc_convert_iunit_factor=land.MHA_TO_HA)

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
        conversion_factor=land.MHA_TO_HA)

    self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

    self.c2 = co2calcs.CO2Calcs(ac=self.ac,
        ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
        soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
        soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
        soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),
        soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),
        soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),
        regime_distribution=self.ae.get_land_distribution())

