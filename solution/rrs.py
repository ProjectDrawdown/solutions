"""Features shared by most or all of the
   Reduction and Replacement Solution (RRS) implementations.
"""

import pathlib
import pandas as pd
from model import vma


thisdir = pathlib.Path(__file__).parents[0]
parentdir = pathlib.Path(__file__).parents[1]
tam_ref_data_sources = {
    'Baseline Cases': {
      'Baseline: Based on- IEA ETP 2016 6DS': str(parentdir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_6DS.csv')),
      'Baseline: Based on- AMPERE MESSAGE-MACRO Reference': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_Reference.csv')),
      'Baseline: Based on- AMPERE GEM E3 Reference': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_Reference.csv')),
      'Baseline: Based on- AMPERE IMAGE/TIMER Reference': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_Reference.csv')),
      },
    'Conservative Cases': {
      'Conservative: Based on- IEA ETP 2016 4DS': str(parentdir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_4DS.csv')),
      'Conservative: Based on- AMPERE MESSAGE-MACRO 550': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_550.csv')),
      'Conservative: Based on- AMPERE GEM E3 550': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_550.csv')),
      'Conservative: Based on- AMPERE IMAGE/TIMER 550': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_550.csv')),
      'Conservative: Based on- Greenpeace 2015 Reference': str(parentdir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Reference.csv')),
      },
    'Ambitious Cases': {
      'Ambitious: Based on- IEA ETP 2016 2DS': str(parentdir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_2DS.csv')),
      'Ambitious: Based on- AMPERE MESSAGE-MACRO 450': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_450.csv')),
      'Ambitious: Based on- AMPERE GEM E3 450': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_450.csv')),
      'Ambitious: Based on- AMPERE IMAGE/TIMER 450': str(parentdir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_450.csv')),
      'Ambitious: Based on- Greenpeace Energy [R]evolution': str(parentdir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Energy_Revolution.csv')),
      },
    '100% RES2050 Case': {
      '100% REN: Based on- Greenpeace Advanced [R]evolution': str(parentdir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Advanced_Revolution.csv')),
      },
}
tam_pds_data_sources = {
    'Ambitious Cases': {
      'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_plausible_scenario.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_drawdown_scenario.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario': str(parentdir.joinpath(
        'data', 'energy', 'PDS_optimum_scenario.csv')),
      },
}


class RRS:
  def __init__(self, total_energy_demand, soln_avg_annual_use):
    """Data structures to support the Reduction and Replacement Solutions.
       Arguments:
         total_energy_demand: in Terawatt-Hours (TWh), value typically supplied by tam.py
         soln_avg_annual_use: average annual usage of the solution in hours.
    """
    self.substitutions = {
        '@soln_avg_annual_use@': soln_avg_annual_use,

        # source for energy mix coal, natural gas, nuclear, and oil:
        # The World Bank Data in The Shift Project Data Portal
        # http://www.tsp-data-portal.org/Breakdown-of-Electricity-Generation-by-Energy-Source#tspQvChart
        '@energy_mix_coal@': 8726.0 / total_energy_demand,
        '@energy_mix_natural_gas@': 4933.0 / total_energy_demand,
        '@energy_mix_nuclear@': 2417.0 / total_energy_demand,
        '@energy_mix_oil@': 1068.0 / total_energy_demand,

        # source for remaining energy mix data:
        # IRENA (2016) Renewable Energy Statistics
        # http://www.irena.org/DocumentDownloads/Publications/IRENA_RE_Statistics_2016.pdf
        '@energy_mix_hydroelectric@': 4019.0 / total_energy_demand,
        '@energy_mix_solar@': 188.073 / total_energy_demand,
        '@energy_mix_wave@': 0.954 / total_energy_demand,
        '@energy_mix_wind_onshore@': 688.956 / total_energy_demand,
        '@energy_mix_wind_offshore@': 24.89 / total_energy_demand,
        '@energy_mix_biomass@': 399.496 / total_energy_demand,
        '@energy_mix_concentrated_solar@': 8.735 / total_energy_demand,
        '@energy_mix_geothermal@': 74.195 / total_energy_demand,
        }

    # WindOnshore_RRS_ELECGEN 'Variable Meta-analysis'!C995:X1024, VMA #27
    self.oil_plant_efficiency_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_oil_plant_efficiency.csv')))
    (self.oil_efficiency, _, _) = self.oil_plant_efficiency_vma.avg_high_low()

    # WindOnshore_RRS_ELECGEN 'Variable Meta-analysis'!C960:X989, VMA #26
    self.natural_gas_plant_efficiency_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_natural_gas_plant_efficiency.csv')))
    (self.natural_gas_efficiency, _, _) = self.natural_gas_plant_efficiency_vma.avg_high_low()

    # WindOnshore_RRS_ELECGEN 'Variable Meta-analysis'!C926:X955, VMA #25
    self.coal_plant_efficiency_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_coal_plant_efficiency.csv')))
    (self.coal_efficiency, _, _) = self.coal_plant_efficiency_vma.avg_high_low()

    # WindOnshore_RRS_ELECGEN Variable Meta-analysis!C926:X955, VMA #25
    self.conv_ref_plant_efficiency_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_conv_ref_plant_efficiency.csv')))
    (self.conv_ref_plant_efficiency, _, _) = self.conv_ref_plant_efficiency_vma.avg_high_low()

    # WindOnshore_RRS_ELECGEN 'Variable Meta-analysis'!C84:X106, VMA #2
    self.conv_2014_cost_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_conv_2014_cost.csv')))
    (self.conv_2014_cost, _, _) = self.conv_2014_cost_vma.avg_high_low()

    # WindOnshore_RRS_ELECGEN 'Variable Meta-analysis'!C175:X185, VMA #4
    self.conv_lifetime_years_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_conv_lifetime_years.csv')))
    (self.conv_lifetime_years, _, _) = self.conv_lifetime_years_vma.avg_high_low()

    # WindOnshore_RRS_ELECGEN 'Variable Meta-analysis'!C246:X268, VMA #6
    self.conv_avg_annual_use_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_conv_avg_annual_use.csv')))
    (self.conv_avg_annual_use, _, _) = self.conv_avg_annual_use_vma.avg_high_low()

    # WindOnshore_RRS_ELECGEN 'Variable Meta-analysis'!C319:X339, VMA #8
    self.conv_vom_per_funit_vma = vma.VMA(substitutions=self.substitutions,
        final_units='US$2014/kWh',
        filename=str(parentdir.joinpath('solution', 'vma_conv_vom_per_funit.csv')))
    (self.conv_vom_per_funit, _, _) = self.conv_vom_per_funit_vma.avg_high_low()

    #  SolarPVUtility_RRS_ELECGEN 'Variable Meta-analysis'!C389:X404, VMA #10
    self.conv_fom_per_funit_vma = vma.VMA(substitutions=self.substitutions,
        filename=str(parentdir.joinpath('solution', 'vma_conv_fom_per_funit.csv')))
    (self.conv_fom_per_funit, _, _) = self.conv_fom_per_funit_vma.avg_high_low()
