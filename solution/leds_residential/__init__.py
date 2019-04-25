"""Residential LED Lighting solution model.
   Excel filename: Drawdown-Residential LED Lighting_RRS_v1.1_19Nov2018_PUBLIC.xlsm
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

from model import tam
from solution import rrs

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA']

scenarios = {
  'PDS1-90p2050-linear (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take a linear growth to 90% adoption by 2050. This scenario uses inputs
      # calculated for the Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.9), ('OECD90', 0.9), ('Eastern Europe', 0.9), ('Asia (Sans Japan)', 0.9), ('Middle East and Africa', 0.9), ('Latin America', 0.9), ('China', 0.9), ('India', 0.9), ('EU', 0.9), ('USA', 0.9)], 

      # financial
      pds_2014_cost=19.47968745713601, ref_2014_cost=19.47968745713601, 
      conv_2014_cost=4.695343157987457, 
      soln_first_cost_efficiency_rate=0.08309247995716584, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=50000.0, soln_avg_annual_use=1000.0, 
      conv_lifetime_capacity=7058.394160583942, conv_avg_annual_use=1000.0, 

      soln_var_oper_cost_per_funit=0.0019107061503416854, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.00399955250933941, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=588343.040378007, 
      conv_indirect_co2_per_unit=705295.0910883629, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=13.66742596810934, conv_annual_energy_used=29.32867666808501, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS2-95p2050-linear (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take a linear growth to 95% adoption by 2050. This scenario uses inputs
      # calculated for the Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 0.95), ('OECD90', 0.95), ('Eastern Europe', 0.95), ('Asia (Sans Japan)', 0.95), ('Middle East and Africa', 0.95), ('Latin America', 0.95), ('China', 0.95), ('India', 0.95), ('EU', 0.95), ('USA', 0.95)], 

      # financial
      pds_2014_cost=19.47968745713601, ref_2014_cost=19.47968745713601, 
      conv_2014_cost=4.695343157987457, 
      soln_first_cost_efficiency_rate=0.08309247995716584, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=50000.0, soln_avg_annual_use=1000.0, 
      conv_lifetime_capacity=7058.394160583942, conv_avg_annual_use=1000.0, 

      soln_var_oper_cost_per_funit=0.0019107061503416854, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.00399955250933941, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=588343.040378007, 
      conv_indirect_co2_per_unit=705295.0910883629, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=13.66742596810934, conv_annual_energy_used=29.32867666808501, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
  'PDS3-100p2050-linear (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take a linear growth to 100% adoption by 2050. This scenario uses inputs
      # calculated for the Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_adoption_final_percentage=[('World', 1.0), ('OECD90', 1.0), ('Eastern Europe', 1.0), ('Asia (Sans Japan)', 1.0), ('Middle East and Africa', 1.0), ('Latin America', 1.0), ('China', 1.0), ('India', 1.0), ('EU', 1.0), ('USA', 1.0)], 

      # financial
      pds_2014_cost=19.47968745713601, ref_2014_cost=19.47968745713601, 
      conv_2014_cost=4.695343157987457, 
      soln_first_cost_efficiency_rate=0.08309247995716584, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.04, 
      soln_lifetime_capacity=50000.0, soln_avg_annual_use=1000.0, 
      conv_lifetime_capacity=7058.394160583942, conv_avg_annual_use=1000.0, 

      soln_var_oper_cost_per_funit=0.0019107061503416854, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.00399955250933941, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=588343.040378007, 
      conv_indirect_co2_per_unit=705295.0910883629, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=13.66742596810934, conv_annual_energy_used=29.32867666808501, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 


      # sequestration
    ),
}

class ResidentialLEDLighting:
  name = 'Residential LED Lighting'
  units = {
    "implementation unit": "Petalumens (Plm)",
    "functional unit": "Petalumen hours (Plmh)",
    "first cost": "US$B",
    "operating cost": "US$B",
  }


  def __init__(self, scenario=None):
    datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))
    parentdir = pathlib.Path(__file__).parents[1]
    thisdir = pathlib.Path(__file__).parents[0]
    if scenario is None:
      scenario = 'PDS1-90p2050-linear (Book Ed.1)'
    self.scenario = scenario
    self.ac = scenarios[scenario]

    tamconfig_list = [
      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
      ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
       'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
      ['trend', '2nd Poly', '2nd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
       '3rd Poly', '3rd Poly', '3rd Poly'],
      ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    tam_ref_data_sources = {
      'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'Calculations on the basis of floor space (m2, Urge-Vorsats et al. 2013 data), average illuminance (lm/m2) and annual operating time (constant 1000 h/a)': thisdir.joinpath('tam_Calculations_on_the_basis_of_floor_space_m2_UrgeVorsats_et_al__98738cf3.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
      },
      'Region: OECD90': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'Calculations on the basis of floor space (m2, Hong et al. 2014 data), average illuminance (lm/m2) and annual operating time (constant 1000 h/a)': thisdir.joinpath('tam_Calculations_on_the_basis_of_floor_space_m2_Hong_et_al__2014_da4b48c2ca.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'VITO 2015 Task 7, corrected': thisdir.joinpath('tam_VITO_2015_Task_7_corrected.csv'),
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'Navigant Consulting 2010 http://apps1.eere.energy.gov/buildings/publications/pdfs/ssl/ssl_energy-savings-report_10-30.pdf, growth rate 1.31% in http://apps1.eere.energy.gov/buildings/publications/pdfs/ssl/energysavingsforecast14.pdf': thisdir.joinpath('tam_Navigant_Consulting_2010_httpapps1_eere_energy_govbuildingspuble1ec448a.csv'),
          'US DOE 2014 Energy saving forecast (total Tlmh lighting in Figure 3.2) & US DOE 2012 (2010 US Lighting Market) for 8% residential lighting, assumed to be constant': thisdir.joinpath('tam_US_DOE_2014_Energy_saving_forecast_total_Tlmh_lighting_in_Figur61f74442.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': thisdir.joinpath('tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_204510d02.csv'),
        },
        'Conservative Cases': {
          'Calculations, see sheet "IEA 2006 TAM" for details': thisdir.joinpath('tam_Calculations_see_sheet_IEA_2006_TAM_for_details.csv'),
        },
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
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources, adconfig=adconfig)

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()
    elif self.ac.soln_pds_adoption_basis == 'Linear':
      pds_adoption_data_per_region = None
      pds_adoption_trend_per_region = None
      pds_adoption_is_single_source = False

    ht_ref_adoption_initial = pd.Series(
      [0.6794492428871898, 0.3191954710617667, 0.10696600912194591, 0.14940816617982913, 0.05052731382746539,
       0.028682249324419262, 0.27338382605688477, 0.06226876414656746, 0.08601359398921465, 0.12076301805261236],
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
                                        ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
                                        pds_adoption_data_per_region=pds_adoption_data_per_region,
                                        pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                                        pds_adoption_is_single_source=pds_adoption_is_single_source)

    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=datadir,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
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
        fc_convert_iunit_factor=1000000000000.0)

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
        conversion_factor=1000000000000.0)

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

    self.VMAs = []

