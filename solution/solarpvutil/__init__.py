"""Utility Scale Solar Photovoltaics solution model.
   solarpvutil_*
"""

import pathlib

import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import ch4calcs
from model import co2calcs
from model import firstcost
from model import helpertables
from model import operatingcost
from model import tam
from model import unitadoption


class SolarPVUtil:
  def __init__(self):
    super()
    soln_funit_adoption_2014 = pd.DataFrame([[112.63303333333, 75.00424555556, 0.33238333333,
      21.07250444444, 1.57507777778, 14.65061888889, 14.97222222222, 2.74830111111, 55.27205444444,
      13.12465000000]],
      columns=['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
        'Latin America', 'China', 'India', 'EU', 'USA'], index=[2014])
    soln_funit_adoption_2014.index.name = 'Year'

    self.ac = advanced_controls.AdvancedControls(
        pds_2014_cost=1444.93954421485,
        ref_2014_cost=1444.93954421485,
        conv_2014_cost=2010.03170851964,
        soln_first_cost_efficiency_rate=0.196222222222222,
        soln_first_cost_below_conv=True,
        conv_first_cost_efficiency_rate=0.02,
        soln_funit_adoption_2014=soln_funit_adoption_2014,
        ch4_is_co2eq=True,
        n2o_is_co2eq=True,
        co2eq_conversion_source="AR5 with feedback",
        soln_indirect_co2_per_iunit=47157.2222222222,
        conv_indirect_co2_is_iunits=False,

        soln_lifetime_capacity=48343.8,
        soln_avg_annual_use=1841.66857142857,
        conv_lifetime_capacity=182411.275767661,
        conv_avg_annual_use=4946.840187342,

        report_start_year=2020,
        report_end_year=2050,

        soln_var_oper_cost_per_funit=0.0,
        soln_fuel_cost_per_funit=0.0,
        soln_fixed_oper_cost_per_iunit=23.18791293579,
        conv_var_oper_cost_per_funit=0.00375269040,
        conv_fuel_cost_per_funit=0.0731,
        conv_fixed_oper_cost_per_iunit=32.95140431108,

        npv_discount_rate=0.094,

        emissions_grid_source="ipcc_only",
        emissions_grid_range="mean",

        soln_ref_adoption_regional_data=False,
        soln_pds_adoption_regional_data=False,
        soln_pds_adoption_basis='Existing Adoption Prognostications',
        soln_pds_adoption_prognostication_source='Based on: Greenpeace (2015) Advanced Energy Revolution',
        soln_pds_adoption_prognostication_trend='3rd Poly',
        soln_pds_adoption_prognostication_growth='Medium',
        solution_category='REPLACEMENT'
        )

    tamconfig_list = [
      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
        'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['source_until_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['source_after_2014', 'Baseline Cases',
        'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario', 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
        'ALL SOURCES', 'ALL SOURCES'],
      ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
        '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
        'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')

    adconfig_list = [
      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
        'Latin America', 'China', 'India', 'EU', 'USA'],
      ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
        '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
        'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')

    ht_ref_datapoints = pd.DataFrame([
      [2014, 112.63303333333, 75.00424555556, 0.33238333333, 21.07250444444, 1.57507777778,
          14.65061888889, 14.97222222222, 2.74830111111, 55.27205444444, 13.12465000000],
      [2050, 272.41409799109, 97.40188603589, 0.52311962553, 60.19386560477, 6.43555351544,
          42.24551570326, 31.56519386433, 14.33357622563, 72.82702319498, 16.41524405748]],
      columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
          "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")
    ht_pds_datapoints = pd.DataFrame([
      [2014, 112.633033, 75.0042456, 0.332383, 21.072504, 1.575078, 14.650619,
        14.972222, 2.748301, 55.272054, 13.12465],
      [2050, 2603.660640, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
      columns=["Year", "World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
          "Middle East and Africa", "Latin America", "China", "India", "EU", "USA"]).set_index("Year")

    datadir = str(pathlib.Path(__file__).parents[0])
    self.tm = tam.TAM(datadir=datadir, tamconfig=tamconfig)
    ref_tam_per_region=self.tm.ref_tam_per_region()
    pds_tam_per_region=self.tm.pds_tam_per_region()

    self.ad = adoptiondata.AdoptionData(ac=self.ac, datadir=datadir, adconfig=adconfig)
    self.ht = helpertables.HelperTables(ac=self.ac, ref_datapoints=ht_ref_datapoints,
        pds_datapoints=ht_pds_datapoints)
    soln_ref_funits_adopted = self.ht.soln_ref_funits_adopted(
        ref_tam_per_region=ref_tam_per_region)
    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=datadir,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=soln_ref_funits_adopted,
        soln_pds_funits_adopted=None)

    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
        ref_learning_increase_mult=2, conv_learning_increase_mult=2)
    self.oc = operatingcost.OperatingCost(ac=self.ac)
    self.c2 = co2calcs.CO2Calcs(ac=self.ac)
    self.c4 = ch4calcs.CH4Calcs(ac=self.ac)
