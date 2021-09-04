"""Solar Hot Water solution model.
   Excel filename: Drawdown-Solar Hot Water_RRS_v1.1_21Nov2018_PUBLIC.xlsm
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
      filename=None, use_weight=False),
  'SOLUTION First Cost per Implementation Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Lifetime Capacity': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Lifetime Capacity': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
      use_weight=False),
  'CONVENTIONAL Average Annual Use': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Average Annual Use': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
      use_weight=False),
  'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
      use_weight=True),
  'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
      use_weight=False),
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
  'Conversion factor for collector area to solar thermal capacity': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Conversion_factor_for_collector_area_to_solar_thermal_capacity.csv"),
      use_weight=False),
  'Natural Gas Share of Conventional Water Heating': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Natural_Gas_Share_of_Conventional_Water_Heating.csv"),
      use_weight=False),
  'Electricity Share of Conventional Water Heating': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Electricity_Share_of_Conventional_Water_Heating.csv"),
      use_weight=False),
  'Conventional Fuel HW Efficiency': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Conventional_Fuel_HW_Efficiency.csv"),
      use_weight=True),
  'Conventional Electricity HW Efficiency': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Conventional_Electricity_HW_Efficiency.csv"),
      use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": "TW",
  "functional unit": "TWh(th)",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Solar Hot Water'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-25p2050-Low of Custom Scen. (Book Ed.1)"
PDS2 = "PDS2-44p2050-Mean of Custom Scen. (Book Ed.1)"
PDS3 = "PDS3-62p2050-High of Custom Scen. (Book Ed.1)"

class Scenario(scenario.RRSScenario):
  name = name
  units = units
  vmas = VMAs
  solution_category = solution_category

  _ref_tam_sources = {
    'Baseline Cases': {
        'Custom calculated from (GBPN, Urge-Vorsatz Factored by IEA Building  Data)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_UrgeVorsatz_Factored_by_IEA_Building_Data.csv'),
        'IEA 6DS (2016), Residential & Commercial Water Heating': THISDIR.joinpath('tam', 'tam_IEA_6DS_2016_Residential_Commercial_Water_Heating.csv'),
        'GBPN Energy for water heating, Urban & Rural / All buildings, All Vintages, Frozen efficiency (Water Heating Thermal energy use in TWHth)': THISDIR.joinpath('tam', 'tam_GBPN_Energy_for_water_heating_Urban_Rural_All_buildings_All_Vintages_Frozen_efficiency_W_e86b69eb.csv'),
    },
    'Conservative Cases': {
        'Custom calculated from (GBPN and Urge-Vorsatz)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_and_UrgeVorsatz.csv'),
        'IEA 4DS (2016), Residential & Commercial Water Heating': THISDIR.joinpath('tam', 'tam_IEA_4DS_2016_Residential_Commercial_Water_Heating.csv'),
    },
    'Region: OECD90': {
      'Baseline Cases': {
        'Custom calculated from (GBPN, Urge-Vorsatz Factored by IEA Building  Data)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_UrgeVorsatz_Factored_by_IEA_Building_Data.csv'),
        'Custom calculated from (GBPN and Urge-Vorsatz)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_and_UrgeVorsatz.csv'),
        'GBPN Energy for water heating, Urban & Rural / All buildings, All Vintages, Frozen efficiency (Water Heating Thermal energy use in TWHth)': THISDIR.joinpath('tam', 'tam_GBPN_Energy_for_water_heating_Urban_Rural_All_buildings_All_Vintages_Frozen_efficiency_W_e86b69eb.csv'),
      },
    },
    'Region: Eastern Europe': {
      'Baseline Cases': {
        'Custom calculated from (GBPN, Urge-Vorsatz Factored by IEA Building  Data)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_UrgeVorsatz_Factored_by_IEA_Building_Data.csv'),
        'Custom calculated from (GBPN and Urge-Vorsatz)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_and_UrgeVorsatz.csv'),
        'GBPN Energy for water heating, Urban & Rural / All buildings, All Vintages, Frozen efficiency (Water Heating Thermal energy use in TWHth)': THISDIR.joinpath('tam', 'tam_GBPN_Energy_for_water_heating_Urban_Rural_All_buildings_All_Vintages_Frozen_efficiency_W_e86b69eb.csv'),
      },
    },
    'Region: Asia (Sans Japan)': {
      'Baseline Cases': {
        'Custom calculated from (GBPN, Urge-Vorsatz Factored by IEA Building  Data)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_UrgeVorsatz_Factored_by_IEA_Building_Data.csv'),
        'Custom calculated from (GBPN and Urge-Vorsatz)': THISDIR.joinpath('tam', 'tam_Custom_calculated_from_GBPN_and_UrgeVorsatz.csv'),
        'GBPN Energy for water heating, Urban & Rural / All buildings, All Vintages, Frozen efficiency (Water Heating Thermal energy use in TWHth)': THISDIR.joinpath('tam', 'tam_GBPN_Energy_for_water_heating_Urban_Rural_All_buildings_All_Vintages_Frozen_efficiency_W_e86b69eb.csv'),
      },
    },
  }
  _pds_tam_sources = {
    'Baseline Cases': {
        'Drawdown TAM: PDS1 - post-Low-Flow': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_PDS1_postLowFlow.csv'),
    },
    'Conservative Cases': {
        'Drawdown TAM: PDS2 - post-Low-Flow': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_PDS2_postLowFlow.csv'),
    },
    'Ambitious Cases': {
        'Drawdown TAM: PDS3 - post-Low-Flow': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_PDS3_postLowFlow.csv'),
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
      'Conservative Cases': {
          'IEA (2012) Technology Roadmap Solar Heating and Cooling - Cons': THISDIR.joinpath('ad', 'ad_IEA_2012_Technology_Roadmap_Solar_Heating_and_Cooling_Cons.csv'),
      },
      'Ambitious Cases': {
          'Solar Heat Worldwide http://www.iea-shc.org/solar-heat-worldwide': THISDIR.joinpath('ad', 'ad_Solar_Heat_Worldwide_httpwww_ieashc_orgsolarheatworldwide.csv'),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Conservative, based on IEA 2012', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Conservative_based_on_IEA_2012.csv')},
      {'name': 'Aggressive, High Growth, early', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Aggressive_High_Growth_early.csv')},
      {'name': 'Aggressive, High Growth, based on IEA', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Aggressive_High_Growth_based_on_IEA.csv')},
      {'name': 'Aggressive, High Growth, late', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Aggressive_High_Growth_late.csv')},
      {'name': 'Aggressive, V. High Growth, late', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Aggressive_V__High_Growth_late.csv')},
      {'name': 'Aggressive, V. High Growth', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Aggressive_V__High_Growth.csv')},
      {'name': 'Conservative Growth, late', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Conservative_Growth_late.csv')},
      {'name': 'Conservative Growth, early', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Conservative_Growth_early.csv')},
      {'name': 'Low Growth', 'include': True, 'bug_no_limit': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Low_Growth.csv')},
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
      [335.463, 56.493, 2.374, 240.305, 9.948,
       9.113, 231.838, 6.4350000000000005, 23.777, 17.233],
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
        fc_convert_iunit_factor=1000000000.0)

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
        conversion_factor=1000000000.0)

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

