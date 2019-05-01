"""Smart Glass solution model.
   Excel filename: Drawdown-Smart Glass_RRS_v1.1_21Nov2018_PUBLIC.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import unitadoption
from model import vma
from model.advanced_controls import SOLUTION_CATEGORY

from model import tam
from solution import rrs

DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = vma.generate_vma_dict(THISDIR.joinpath('vma_data'))

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

scenarios = {
  'PDS1-29p2050-EE21.3% based on Navigant (Book Ed.1)': advanced_controls.AdvancedControls(
      # After integrating building solutions, energy efficiency of smart glass adjusted
      # to 21.3%. For near term forecasts to 2022, we use the historical and trend data
      # estimated by Navigant Research (2012). For the far future, we use the World's
      # Green Buildings Council target of 100% net zero buildings by 2050 (all buildings
      # consume net zero energy/produce onsite or produce net zero carbon emissions). We
      # take a more conservative number of 30% smart glass adoption since some buildings
      # in colder climates wouldn't gain significantly from smart windows, and others
      # may use diferent technologies. These data points (in m2 of smart glass area) are
      # interpolated using a 3rd degree polynomial curve (on Data Interpolator). They
      # are then converted to m2 of commercial floor area using the Window-to-floor area
      # ratio on this sheet. This scenario uses inputs calculated for the Drawdown book
      # edition 1, some of which have been updated since publication.

      # general
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='PDS1 - Adoption based on Navigant Sales and World Green Buildings Council Targets', 
      source_until_2014='IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='Drawdown TAM: Adjusted GBPN Data - Commercial Floor Area', 
      pds_base_adoption=[('World', 1.9734999131249993), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=830796327.2727273, ref_2014_cost=830796327.2727273, 
      conv_2014_cost=293361977.2875817, 
      soln_first_cost_efficiency_rate=0.08, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=88.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=88.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=4947443.08559757, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=7136457.23592277, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.052298552701877, conv_annual_energy_used=0.0754382371662026, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS2-48p2050-EE21.3% based on Navigant (Book Ed.1)': advanced_controls.AdvancedControls(
      # The integrated energy efficiency of the glass is assumed to be 21.3% after other
      # building solutions are applied. For near term forecasts to 2022, we use the
      # historical and trend data estimated by Navigant Research (2012). For the far
      # future, we use the World's Green Buildings Council target of 100% net zero
      # buildings by 2050 (all buildings consume net zero energy/produce onsite or
      # produce net zero carbon emissions). We take a more conservative number of 50%
      # smart glass adoption in this scenario for illustration of the potential of Smart
      # glass. These data points (in m2 of smart glass area) are interpolated using a
      # 3rd degree polynomial curve (on Data Interpolator). They are then converted to
      # m2 of commercial floor area using the Window-to-floor area ratio on this sheet.
      # This scenario uses inputs calculated for the Drawdown book edition 1, some of
      # which have been updated since publication.

      # general
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='PDS2 - Adoption based on Navigant Sales and World Green Buildings Council Targets', 
      source_until_2014='IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='Drawdown TAM: Adjusted GBPN Data - Commercial Floor Area', 
      pds_base_adoption=[('World', 1.9734999131249993), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=830796327.2727273, ref_2014_cost=830796327.2727273, 
      conv_2014_cost=293361977.2875817, 
      soln_first_cost_efficiency_rate=0.08, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=88.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=88.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=4947443.08559757, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=7136457.23592277, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.052298552701877, conv_annual_energy_used=0.0754382371662026, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS3-75p2050-EE21.3% based on Navigant (Book Ed.1)': advanced_controls.AdvancedControls(
      # After integrating building solutions, smart glass Energy Efficiency adjusted to
      # 21.35. For near term forecasts to 2022, we use the historical and trend data
      # estimated by Navigant Research (2012). For the far future, we use the World's
      # Green Buildings Council target of 100% net zero buildings by 2050 (all buildings
      # consume net zero energy/produce onsite or produce net zero carbon emissions). We
      # take a more conservative but still rather ambitious number of 75% smart glass
      # adoption in this scenario for illustration of the potential of Smart glass.
      # These data points (in m2 of smart glass area) are interpolated using a 3rd
      # degree polynomial curve (on Data Interpolator). They are then converted to m2 of
      # commercial floor area using the Window-to-floor area ratio on this sheet. This
      # scenario uses inputs calculated for the Drawdown book edition 1, some of which
      # have been updated since publication.

      # general
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Book (Edition 1) Scenario 3', 
      source_until_2014='IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='Drawdown TAM: Adjusted GBPN Data - Commercial Floor Area', 
      pds_base_adoption=[('World', 1.9734999131249993), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=830796327.2727273, ref_2014_cost=830796327.2727273, 
      conv_2014_cost=293361977.2875817, 
      soln_first_cost_efficiency_rate=0.08, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.0922, 
      soln_lifetime_capacity=88.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=88.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=0.0, soln_fuel_cost_per_funit=4947443.08559757, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.0, conv_fuel_cost_per_funit=7136457.23592277, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.052298552701877, conv_annual_energy_used=0.0754382371662026, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
}

class SmartGlass:
  name = 'Smart Glass'
  units = {
    "implementation unit": "Mm²",
    "functional unit": "Mm²",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-29p2050-EE21.3% based on Navigant (Book Ed.1)'
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
          'IEA, 2013, "Transition to Sustainable Buildings" – see TAM Factoring': THISDIR.joinpath('tam', 'tam_IEA_2013_Transition_to_Sustainable_Buildings_see_TAM_Factoring.csv'),
          'Ürge-Vorsatz et al. (2015) – see TAM Factoring': THISDIR.joinpath('tam', 'tam_ÜrgeVorsatz_et_al__2015_see_TAM_Factoring.csv'),
      },
      'Region: USA': {
        'Baseline Cases': {
          'Annual Energy Outlook 2016, U.S. Energy Information Administration, 2016.': THISDIR.joinpath('tam', 'tam_Annual_Energy_Outlook_2016_U_S__Energy_Information_Administration_2016_.csv'),
        },
      },
    }
    tam_pds_data_sources = {
      'Baseline Cases': {
          'Drawdown TAM: Adjusted GBPN Data - Commercial Floor Area': THISDIR.joinpath('tam', 'tam_pds_Drawdown_TAM_Adjusted_GBPN_Data_Commercial_Floor_Area.csv'),
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      tam_pds_data_sources=tam_pds_data_sources)
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
      {'name': 'PDS1 - Adoption based on Navigant Sales and World Green Buildings Council Targets', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS1_Adoption_based_on_Navigant_Sales_and_World_Green_Buildings_Council_Targets.csv')},
      {'name': 'PDS2 - Adoption based on Navigant Sales and World Green Buildings Council Targets', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS2_Adoption_based_on_Navigant_Sales_and_World_Green_Buildings_Council_Targets.csv')},
      {'name': 'PDS3 - Adoption based on Navigant Sales and World Green Buildings Council Targets', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_PDS3_Adoption_based_on_Navigant_Sales_and_World_Green_Buildings_Council_Targets.csv')},
      {'name': 'Drawdown Book (Edition 1) Scenario 3', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Book_Edition_1_Scenario_3.csv')},
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
      [1.9734999131249993, 0.0, 0.0, 0.0, 0.0,
       0.0, 0.0, 0.0, 0.0, 0.0],
       index=REGIONS)
    ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
    ht_ref_datapoints = pd.DataFrame(columns=REGIONS)
    ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
    ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
    ht_pds_adoption_initial = ht_ref_adoption_initial
    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
    ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
    ht_pds_datapoints = pd.DataFrame(columns=REGIONS)
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
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
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

