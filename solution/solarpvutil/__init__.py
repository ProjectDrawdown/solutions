"""Utility Scale Solar Photovoltaics solution model.
   Excel filename: SolarPVUtility_RRS_ELECGEN
"""

import pathlib

import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import ch4calcs
from model import co2calcs
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import tam
from model import unitadoption


class SolarPVUtil:
  def __init__(self):
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
        conv_indirect_co2_per_unit=0.0,
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

        emissions_use_co2eq=True,
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
    self.ht = helpertables.HelperTables(ac=self.ac,
        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        adoption_low_med_high_global=self.ad.adoption_low_med_high_global())
    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)
    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=datadir,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted())

    soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
    soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
    conv_ref_tot_iunits_reqd = self.ua.conv_ref_tot_iunits_reqd()
    soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()

    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
        ref_learning_increase_mult=2, conv_learning_increase_mult=2,
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
        conv_ref_tot_iunits_reqd=conv_ref_tot_iunits_reqd,
        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
        conv_ref_new_iunits_reqd=self.ua.conv_ref_new_iunits_reqd())
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
        conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit())
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
        conv_ref_new_iunits_reqd=self.ua.conv_ref_new_iunits_reqd(),
        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        fuel_in_liters=False)

  def to_dict(self):
    """Return all data as a dict, to be serialized to JSON."""
    rs = dict()
    rs['tam_data'] = self.tm.to_dict()
    rs['adoption_data'] = self.ad.to_dict()
    rs['helper_tables'] = self.ht.to_dict()
    rs['emissions_factors'] = self.ef.to_dict()
    rs['unit_adoption'] = self.ua.to_dict()
    rs['first_cost'] = self.fc.to_dict()
    rs['operating_cost'] = self.oc.to_dict()
    rs['ch4_calcs'] = self.c4.to_dict()
    rs['co2_calcs'] = self.c2.to_dict()
    return rs
