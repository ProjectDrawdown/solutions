"""Composting solution model.
   Excel filename: Drawdown-Composting_RRS_v1.1_18Nov2018_PUBLIC.xlsm
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
  'PDS1-49p2050-Existing Prognostications (Book Ed.1)': advanced_controls.AdvancedControls(
      # Taking the average projected adoption of Composting worldwide across sources,
      # and average composting revenues from sources collected, we estimate the
      # adoption, emissions and financial impact. This scenario uses inputs calculated
      # for the Drawdown book edition 1, some of which have updated.

      # general
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Existing Adoption Prognostications', 
      soln_pds_adoption_prognostication_source='ALL SOURCES', 
      soln_pds_adoption_prognostication_trend='3rd Poly', 
      soln_pds_adoption_prognostication_growth='Medium', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Ambitious Cases', 
      pds_source_post_2014='Ambitious Cases', 
      pds_base_adoption=[('World', 120.0), ('OECD90', 69.02), ('Eastern Europe', 4.13), ('Asia (Sans Japan)', 13.0), ('Middle East and Africa', 5.66), ('Latin America', 14.0), ('China', 2.75), ('India', 7.29), ('EU', 36.8), ('USA', 20.84)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=161236682.14665875, ref_2014_cost=161236682.14665875, 
      conv_2014_cost=265859166.33454278, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.064, 
      soln_lifetime_capacity=30.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=30.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=128605038.54475701, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=121382547.05072224, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=468619.23333333334, soln_emissions_per_funit=203388.7650793651, 

    ),
  'PDS2-66p2050-Existing Projections + Rapid growth (Book Ed.1)': advanced_controls.AdvancedControls(
      # This scenario uses mainly the high growth prognostication from existing sources,
      # (See Adoption Data sheet for the Mean+1 SD projection). The adoption is limited
      # for later years by feedstocks however. This is a result of integration with
      # other solutions in Project Drawdown. This scenario uses inputs calculated for
      # the Drawdown book edition 1, some of which have updated.

      # general
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Customized Scenario 1', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Ambitious Cases', 
      pds_source_post_2014='Ambitious Cases', 
      pds_base_adoption=[('World', 120.0), ('OECD90', 69.02), ('Eastern Europe', 4.13), ('Asia (Sans Japan)', 13.0), ('Middle East and Africa', 5.66), ('Latin America', 14.0), ('China', 2.75), ('India', 7.29), ('EU', 36.8), ('USA', 20.84)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=161236682.14665875, ref_2014_cost=161236682.14665875, 
      conv_2014_cost=265859166.33454278, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.064, 
      soln_lifetime_capacity=30.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=30.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=98474740.8333385, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=121382547.05072224, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=468619.23333333334, soln_emissions_per_funit=203388.7650793651, 

    ),
  'PDS3-73p2050-Optimum (Book ed.1)': advanced_controls.AdvancedControls(
      # This scenario uses mainly the high growth prognostication from existing sources
      # until 2029, (See Adoption Data sheet for the Mean+1 SD projection) then is
      # optimized to approach 98% of the organic feedstock by 2060 (using integrated
      # data across all Materials and Food solutions in Project Drawdown's Solution
      # Set). This scenario uses inputs calculated for the Drawdown book edition 1, some
      # of which have updated.

      # general
      vmas=VMAs,
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Fully Customized PDS', 
      soln_pds_adoption_custom_name='Drawdown Customized Scenario 2', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='Ambitious Cases', 
      pds_source_post_2014='Ambitious Cases', 
      pds_base_adoption=[('World', 120.0), ('OECD90', 69.02), ('Eastern Europe', 4.13), ('Asia (Sans Japan)', 13.0), ('Middle East and Africa', 5.66), ('Latin America', 14.0), ('China', 2.75), ('India', 7.29), ('EU', 36.8), ('USA', 20.84)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=161236682.14665875, ref_2014_cost=161236682.14665875, 
      conv_2014_cost=265859166.33454278, 
      soln_first_cost_efficiency_rate=0.0, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.064, 
      soln_lifetime_capacity=30.0, soln_avg_annual_use=1.0, 
      conv_lifetime_capacity=30.0, conv_avg_annual_use=1.0, 

      soln_var_oper_cost_per_funit=98474740.8333385, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=121382547.05072224, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=0.0, 
      conv_indirect_co2_per_unit=0.0, 
      conv_indirect_co2_is_iunits=False, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.0, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=0.0, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=468619.23333333334, soln_emissions_per_funit=203388.7650793651, 

    ),
}

class Composting:
  name = 'Composting'
  units = {
    "implementation unit": "MMt",
    "functional unit": "MMt",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-49p2050-Existing Prognostications (Book Ed.1)'
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
      ['growth', 'Low', 'Low', 'Medium', 'Medium',
       'Low', 'Medium', 'Medium', 'Low', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')
    tam_ref_data_sources = {
      'Baseline Cases': {
          'What a Waste Solid Waste Management Static': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Static.csv'),
          'What a Waste Solid Waste Management Dynamic': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic.csv'),
          'What a Waste Solid Waste Management Dynamic Organic Fraction': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic_Organic_Fraction.csv'),
      },
      'Conservative Cases': {
          'Bahor et al (2009) DOI: 10.1177/0734242X09350485 - interpolated and organic fraction from What a  Waste applied': THISDIR.joinpath('tam', 'tam_Bahor_et_al_2009_DOI_10_11770734242X09350485_interpolated_and_organic_fraction_from_What_95c7eead.csv'),
          'IPCC, 2006 - Calculated based on bottom up analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_bottom_up_analysis.csv'),
          'IPCC, 2006 - Calculated based on top down analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_top_down_analysis.csv'),
      },
      'Ambitious Cases': {
          'Hoornweg et al 2015': THISDIR.joinpath('tam', 'tam_Hoornweg_et_al_2015.csv'),
      },
      'Region: OECD90': {
        'Baseline Cases': {
          'What a Waste Solid Waste Management Static': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Static.csv'),
          'What a Waste Solid Waste Management Dynamic': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic.csv'),
          'Hoornweg et al 2015': THISDIR.joinpath('tam', 'tam_Hoornweg_et_al_2015.csv'),
        },
        'Conservative Cases': {
          'Bahor et al (2009) DOI: 10.1177/0734242X09350485 - interpolated and organic fraction from What a  Waste applied': THISDIR.joinpath('tam', 'tam_Bahor_et_al_2009_DOI_10_11770734242X09350485_interpolated_and_organic_fraction_from_What_95c7eead.csv'),
          'OECD Data. http://www.eea.europa.eu/data-and-maps/figures/municipal-waste-generation-within-the-oecd-area': THISDIR.joinpath('tam', 'tam_OECD_Data__httpwww_eea_europa_eudataandmapsfiguresmunicipalwastegenerationwithintheoecdarea.csv'),
        },
        'Ambitious Cases': {
          'What a Waste Solid Waste Management Dynamic Organic Fraction': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic_Organic_Fraction.csv'),
          'IPCC, 2006 - Calculated based on bottom up analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_bottom_up_analysis.csv'),
          'IPCC, 2006 - Calculated based on top down analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_top_down_analysis.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Baseline Cases': {
          'What a Waste Solid Waste Management Static': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Static.csv'),
          'What a Waste Solid Waste Management Dynamic Organic Fraction': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic_Organic_Fraction.csv'),
          'Bahor et al (2009) DOI: 10.1177/0734242X09350485 - interpolated and organic fraction from What a  Waste applied': THISDIR.joinpath('tam', 'tam_Bahor_et_al_2009_DOI_10_11770734242X09350485_interpolated_and_organic_fraction_from_What_95c7eead.csv'),
        },
        'Conservative Cases': {
          'What a Waste Solid Waste Management Dynamic': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic.csv'),
        },
        'Ambitious Cases': {
          'Hoornweg et al 2015': THISDIR.joinpath('tam', 'tam_Hoornweg_et_al_2015.csv'),
          'IPCC, 2006 - Calculated based on bottom up analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_bottom_up_analysis.csv'),
          'IPCC, 2006 - Calculated based on top down analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_top_down_analysis.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'What a Waste Solid Waste Management Static': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Static.csv'),
          'Bahor et al (2009) DOI: 10.1177/0734242X09350485 - interpolated and organic fraction from What a  Waste applied': THISDIR.joinpath('tam', 'tam_Bahor_et_al_2009_DOI_10_11770734242X09350485_interpolated_and_organic_fraction_from_What_95c7eead.csv'),
          'Hoornweg et al 2015': THISDIR.joinpath('tam', 'tam_Hoornweg_et_al_2015.csv'),
        },
        'Conservative Cases': {
          'IPCC, 2006 - Calculated based on top down analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_top_down_analysis.csv'),
          'IPCC, 2006 - Calculated based on bottom up analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_bottom_up_analysis.csv'),
          'Bahor et al (2009) DOI: 10.1177/0734242X09350485 - interpolated and organic fraction from What a  Waste applied.1': THISDIR.joinpath('tam', 'tam_Bahor_et_al_2009_DOI_10_11770734242X09350485_interpolated_and_organic_fraction_from_What_35ed52f6.csv'),
        },
        'Ambitious Cases': {
          'What a Waste Solid Waste Management Dynamic': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          'What a Waste Solid Waste Management Static': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Static.csv'),
          'What a Waste Solid Waste Management Dynamic': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic.csv'),
          'Bahor et al (2009) DOI: 10.1177/0734242X09350485 - interpolated and organic fraction from What a  Waste applied': THISDIR.joinpath('tam', 'tam_Bahor_et_al_2009_DOI_10_11770734242X09350485_interpolated_and_organic_fraction_from_What_95c7eead.csv'),
        },
        'Conservative Cases': {
          'What a Waste Solid Waste Management Dynamic Organic Fraction': THISDIR.joinpath('tam', 'tam_What_a_Waste_Solid_Waste_Management_Dynamic_Organic_Fraction.csv'),
        },
        'Ambitious Cases': {
          'IPCC, 2006 - Calculated based on top down analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_top_down_analysis.csv'),
          'IPCC, 2006 - Calculated based on bottom up analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_bottom_up_analysis.csv'),
          'Hoornweg et al 2015': THISDIR.joinpath('tam', 'tam_Hoornweg_et_al_2015.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'World Bank': THISDIR.joinpath('tam', 'tam_World_Bank.csv'),
        },
        'Conservative Cases': {
          'What a Waste': THISDIR.joinpath('tam', 'tam_What_a_Waste.csv'),
          'IPCC, 2006 - Calculated based on bottom up analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_bottom_up_analysis.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'Kumar, Sunil. Municipal Solid Waste Management in India: Present Practices and Future Challenge. Clean Development Mechanism, United Nations Framework Convention on Climate Change': THISDIR.joinpath('tam', 'tam_Kumar_Sunil__Municipal_Solid_Waste_Management_in_India_Present_Practices_and_Future_Chal_a1d3f433.csv'),
          'IPCC, 2006 - Calculated based on bottom up analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_bottom_up_analysis.csv'),
          'IPCC, 2006 - Calculated based on top down analysis': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated_based_on_top_down_analysis.csv'),
        },
        'Maximum Cases': {
          'CPCB, Satus of MSW India, 2000': THISDIR.joinpath('tam', 'tam_CPCB_Satus_of_MSW_India_2000.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'IPCC, 2006 Calculated': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated.csv'),
        },
        'Maximum Cases': {
          'EUROSTAT, Municipal Solid Waste Statistics, 2016': THISDIR.joinpath('tam', 'tam_EUROSTAT_Municipal_Solid_Waste_Statistics_2016.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'EPA, Municipal Solid Waste Generation, Recycling, and Disposal in the United States: Facts and Figures for 2012': THISDIR.joinpath('tam', 'tam_EPA_Municipal_Solid_Waste_Generation_Recycling_and_Disposal_in_the_United_States_Facts_a_7fa2141a.csv'),
        },
        'Ambitious Cases': {
          'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW)': THISDIR.joinpath('tam', 'tam_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW.csv'),
        },
        'Maximum Cases': {
          'IPCC, 2006 Calculated': THISDIR.joinpath('tam', 'tam_IPCC_2006_Calculated.csv'),
        },
      },
    }
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
      world_includes_regional=True,
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
      'Baseline Cases': {
          'Calculated based on What a Waste and USA as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
      },
      'Conservative Cases': {
          'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
      },
      'Ambitious Cases': {
          'Calculated based on What a Waste and EU as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
      },
      'Region: OECD90': {
        'Baseline Cases': {
          'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW)': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW.csv'),
        },
        'Conservative Cases': {
          'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
        },
        'Ambitious Cases': {
          'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW).1': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW_1.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
        },
        'Conservative Cases': {
          'Calculated based on What a Waste and USA as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
        },
        'Ambitious Cases': {
          'Calculated based on What a Waste and EU as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
          'Calculated based on What a Waste and USA as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_USA_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
        },
        'Ambitious Cases': {
          'Calculated based on What a Waste and EU as PDS Benchmark (See Adoption Factoring)': THISDIR.joinpath('ad', 'ad_Calculated_based_on_What_a_Waste_and_EU_as_PDS_Benchmark_See_Adoption_Factoring.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'Song, L. et al. Study on the Current Situation of Municipal Solid Waste Composting in China and Development Trend. 2012': THISDIR.joinpath('ad', 'ad_Song_L__et_al__Study_on_the_Current_Situation_of_Municipal_Solid_Waste_Composting_in_Chi_f57570b9.csv'),
        },
        'Conservative Cases': {
          'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'Kharvel, R. Sustainable Solid Waste Management in Inidia. SEAS, Columbia Thesis. 2012': THISDIR.joinpath('ad', 'ad_Kharvel_R__Sustainable_Solid_Waste_Management_in_Inidia__SEAS_Columbia_Thesis__2012.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'EUROSTAT, 2016. http://ec.europa.eu/eurostat/statistics-explained/index.php/Municipal_waste_statistics': THISDIR.joinpath('ad', 'ad_EUROSTAT_2016__httpec_europa_eueurostatstatisticsexplainedindex_phpMunicipal_waste_statistics.csv'),
          'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW)': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'EPA, MSW trends, 2012 https://www.epa.gov/sites/production/files/2015-09/documents/2012_msw_fs.pdf': THISDIR.joinpath('ad', 'ad_EPA_MSW_trends_2012_httpswww_epa_govsitesproductionfiles201509documents2012_msw_fs_pdf.csv'),
          'IPCC, 2006 Calculated': THISDIR.joinpath('ad', 'ad_IPCC_2006_Calculated.csv'),
          'OECD.stat (http://stats.oecd.org/Index.aspx?DataSetCode=MUNW)': THISDIR.joinpath('ad', 'ad_OECD_stat_httpstats_oecd_orgIndex_aspxDataSetCodeMUNW.csv'),
        },
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        world_includes_regional=True,
        adconfig=adconfig)

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Drawdown Customized Scenario 1', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_1.csv')},
      {'name': 'Drawdown Customized Scenario 2', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_2.csv')},
      {'name': 'Drawdown Customized Scenario 3', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_3.csv')},
      {'name': 'Drawdown Customized Scenario 4', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Customized_Scenario_4.csv')},
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
      [120.0, 69.02, 4.13, 13.0, 5.66,
       14.0, 2.75, 7.29, 36.8, 20.84],
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

