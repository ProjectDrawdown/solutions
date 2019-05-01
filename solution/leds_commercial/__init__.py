"""LED Commercial Lighting solution model.
   Excel filename: Drawdown-LED Commercial Lighting_RRS_v1.1_19Nov2018_PUBLIC.xlsm
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
  'PDS1-82p2050-E18.8% (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take the average of published adoption projections from several sources and
      # use the average energy efficiency after other Building solutions have been
      # applied through Project Drawdown's integration process. This scenario uses
      # inputs calculated for the Drawdown book edition 1, some of which have been
      # updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='Existing Adoption Prognostications', 
      soln_pds_adoption_prognostication_source='ALL SOURCES', 
      soln_pds_adoption_prognostication_trend='3rd Poly', 
      soln_pds_adoption_prognostication_growth='Medium', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_base_adoption=[('World', 2.0559386403033844), ('OECD90', 1.203539561682151), ('Eastern Europe', 0.17104652142368798), ('Asia (Sans Japan)', 0.5420894798241899), ('Middle East and Africa', 0.15340928478053964), ('Latin America', 0.12392820164125475), ('China', 0.3234205780581264), ('India', 0.07626534974849451), ('EU', 0.3954239644503743), ('USA', 0.8447244056291314)], 
      pds_adoption_final_percentage=[('World', 0.0), ('OECD90', 0.0), ('Eastern Europe', 0.0), ('Asia (Sans Japan)', 0.0), ('Middle East and Africa', 0.0), ('Latin America', 0.0), ('China', 0.0), ('India', 0.0), ('EU', 0.0), ('USA', 0.0)], 

      # financial
      pds_2014_cost=64.0177777777778, ref_2014_cost=64.0177777777778, 
      conv_2014_cost=49.5887068333939, 
      soln_first_cost_efficiency_rate=0.0831, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.094, 
      soln_lifetime_capacity=50000.0, soln_avg_annual_use=3635.85, 
      conv_lifetime_capacity=18587.628865979383, conv_avg_annual_use=3635.85, 

      soln_var_oper_cost_per_funit=0.00166026455054077, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.00206359259555884, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=466307.05230240553, 
      conv_indirect_co2_per_unit=197474.2757220778, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.188, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=16.56247833674782, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS3-95p2050-E17.3%-Linear 95% (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take the energy efficiency after integrating LED's with other building
      # solutions in Project Drawdown's Integrated Sector model. We also assume a linear
      # growth in adoption to 95% of the TAM. This scenario uses inputs calculated for
      # the Drawdown book edition 1, some of which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_base_adoption=[('World', 2.0559386403033844), ('OECD90', 1.203539561682151), ('Eastern Europe', 0.17104652142368798), ('Asia (Sans Japan)', 0.5420894798241899), ('Middle East and Africa', 0.15340928478053964), ('Latin America', 0.12392820164125475), ('China', 0.3234205780581264), ('India', 0.07626534974849451), ('EU', 0.3954239644503743), ('USA', 0.8447244056291314)], 
      pds_adoption_final_percentage=[('World', 0.95), ('OECD90', 0.95), ('Eastern Europe', 0.95), ('Asia (Sans Japan)', 0.95), ('Middle East and Africa', 0.95), ('Latin America', 0.95), ('China', 0.95), ('India', 0.95), ('EU', 0.95), ('USA', 0.95)], 

      # financial
      pds_2014_cost=64.0177777777778, ref_2014_cost=64.0177777777778, 
      conv_2014_cost=49.5887068333939, 
      soln_first_cost_efficiency_rate=0.0831, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.094, 
      soln_lifetime_capacity=50000.0, soln_avg_annual_use=3635.85, 
      conv_lifetime_capacity=18587.628865979383, conv_avg_annual_use=3635.85, 

      soln_var_oper_cost_per_funit=0.00166026455054077, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.00206359259555884, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=466307.05230240553, 
      conv_indirect_co2_per_unit=197474.2757220778, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.173, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=16.56247833674782, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
  'PDS2-90p2050-E18.2%-Linear 90% (Book Ed.1)': advanced_controls.AdvancedControls(
      # We take the Energy Efficiency estimated after other Project Drawdown solutions
      # have been integrated into the building sector model, which is slightly reduced
      # to that of the Plausible Scenario since other solutions have already reduced
      # total energy usage. The adoption is assumed to grow linearly to 90% of the TAM.
      # This scenario uses inputs calculated for the Drawdown book edition 1, some of
      # which have been updated.

      # general
      report_start_year=2020, report_end_year=2050, 

      # adoption
      soln_ref_adoption_basis='Default', 
      soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False, 
      soln_pds_adoption_basis='DEFAULT Linear', 
      source_until_2014='ALL SOURCES', 
      ref_source_post_2014='ALL SOURCES', 
      pds_source_post_2014='ALL SOURCES', 
      pds_base_adoption=[('World', 2.0559386403033844), ('OECD90', 1.203539561682151), ('Eastern Europe', 0.17104652142368798), ('Asia (Sans Japan)', 0.5420894798241899), ('Middle East and Africa', 0.15340928478053964), ('Latin America', 0.12392820164125475), ('China', 0.3234205780581264), ('India', 0.07626534974849451), ('EU', 0.3954239644503743), ('USA', 0.8447244056291314)], 
      pds_adoption_final_percentage=[('World', 0.9), ('OECD90', 0.9), ('Eastern Europe', 0.9), ('Asia (Sans Japan)', 0.9), ('Middle East and Africa', 0.9), ('Latin America', 0.9), ('China', 0.9), ('India', 0.9), ('EU', 0.9), ('USA', 0.9)], 

      # financial
      pds_2014_cost=64.0177777777778, ref_2014_cost=64.0177777777778, 
      conv_2014_cost=49.5887068333939, 
      soln_first_cost_efficiency_rate=0.0831, 
      conv_first_cost_efficiency_rate=0.0, 
      soln_first_cost_below_conv=True, 
      npv_discount_rate=0.094, 
      soln_lifetime_capacity=50000.0, soln_avg_annual_use=3635.85, 
      conv_lifetime_capacity=18587.628865979383, conv_avg_annual_use=3635.85, 

      soln_var_oper_cost_per_funit=0.00166026455054077, soln_fuel_cost_per_funit=0.0, 
      soln_fixed_oper_cost_per_iunit=0.0, 
      conv_var_oper_cost_per_funit=0.00206359259555884, conv_fuel_cost_per_funit=0.0, 
      conv_fixed_oper_cost_per_iunit=0.0, 

      # emissions
      ch4_is_co2eq=False, n2o_is_co2eq=False, 
      co2eq_conversion_source='AR5 with feedback', 
      soln_indirect_co2_per_iunit=466307.05230240553, 
      conv_indirect_co2_per_unit=197474.2757220778, 
      conv_indirect_co2_is_iunits=True, 
      ch4_co2_per_twh=0.0, n2o_co2_per_twh=0.0, 

      soln_energy_efficiency_factor=0.182, 
      soln_annual_energy_used=0.0, conv_annual_energy_used=16.56247833674782, 
      conv_fuel_consumed_per_funit=0.0, soln_fuel_efficiency_factor=0.0, 
      conv_fuel_emissions_factor=0.0, soln_fuel_emissions_factor=0.0, 

      emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean', 
      emissions_use_co2eq=True, 
      conv_emissions_per_funit=0.0, soln_emissions_per_funit=0.0, 

    ),
}

class LEDCommercialLighting:
  name = 'LED Commercial Lighting'
  units = {
    "implementation unit": "Petalumen (Plm)",
    "functional unit": "Petalumen hours (Plmh)",
    "first cost": "US$B",
    "operating cost": "US$B",
  }

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = 'PDS1-82p2050-E18.8% (Book Ed.1)'
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
          'IEA 2006 Lights Labours Lost for 2005 & GDP growth rate as future forecast, see IEA 2006 sheet': THISDIR.joinpath('tam', 'tam_IEA_2006_Lights_Labours_Lost_for_2005_GDP_growth_rate_as_future_forecast_see_IEA_2006_sheet.csv'),
          'IEA 2006 Lights Labours Lost for 2030 (current policy) & GDP growth rate as past estimate/future forecast, see IEA 2006 sheet': THISDIR.joinpath('tam', 'tam_IEA_2006_Lights_Labours_Lost_for_2030_current_policy_GDP_growth_rate_as_past_estimatefut_0d9e2767.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
      },
      'Conservative Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'EIA IEO energy; average efficacy estimated, interpolated': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated.csv'),
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd order polynomial': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_order_polynomial.csv'),
      },
      'Ambitious Cases': {
          'IEA 2006 Lights Labours Lost for 2030 (least life cycle cost scenario)& GDP growth rate as past estimate/future forecast, see IEA 2006 sheet': THISDIR.joinpath('tam', 'tam_IEA_2006_Lights_Labours_Lost_for_2030_least_life_cycle_cost_scenario_GDP_growth_rate_as__a7eda2ee.csv'),
          'Floor space :Urge Vorsats et al. 2015; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_Urge_Vorsats_et_al__2015_Average_illuminance_see_Lux_lm_per_m2_Average_opera_7fac112b.csv'),
      },
      'Maximum Cases': {
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_05cb930f.csv'),
      },
      'Region: OECD90': {
        'Baseline Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Conservative Cases': {
          'EIA IEO energy; average efficacy estimated, interpolated, 2nd order': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated_2nd_order.csv'),
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd order': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_order.csv'),
        },
        'Maximum Cases': {
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_05cb930f.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Baseline Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'EIA IEO energy; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated_2nd_poly.csv'),
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_poly.csv'),
        },
        'Maximum Cases': {
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data, 2nd order': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_7c1f094c.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'EIA IEO energy; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated_2nd_poly.csv'),
        },
        'Conservative Cases': {
          'EIA IEO electricity; average efficacy estimated, interpolated': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated.csv'),
        },
        'Ambitious Cases': {
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Maximum Cases': {
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data, 2nd poly': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_0f701d19.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'EIA IEO energy; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated_2nd_poly.csv'),
        },
        'Conservative Cases': {
          'EIA IEO electricity; average efficacy estimated, interpolated': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated.csv'),
        },
        'Ambitious Cases': {
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Maximum Cases': {
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_05cb930f.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'EIA IEO energy; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated_2nd_poly.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Conservative Cases': {
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_poly.csv'),
        },
        'Maximum Cases': {
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_05cb930f.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'EIA IEO energy; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated_2nd_poly.csv'),
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_poly.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Conservative Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
        },
        'Ambitious Cases': {
          'Floor space: Hong et al.; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_Hong_et_al__Average_illuminance_see_Lux_lm_per_m2_Average_operating_hours_ha_cd4d6751.csv'),
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data, 2nd poly (declines at the end)': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_14adb205.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'EIA IEO energy; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated_2nd_poly.csv'),
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_poly.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Conservative Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
        },
        'Maximum Cases': {
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_05cb930f.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data, 2nd poly': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_0f701d19.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Conservative Cases': {
          'EIA IEO energy; average efficacy estimated, interpolated': THISDIR.joinpath('tam', 'tam_EIA_IEO_energy_average_efficacy_estimated_interpolated.csv'),
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_poly.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'IEA 2006 (Mlmh/capita and population data) and GDP growth': THISDIR.joinpath('tam', 'tam_IEA_2006_Mlmhcapita_and_population_data_and_GDP_growth.csv'),
          'EIA IEO electricity; average efficacy estimated, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_EIA_IEO_electricity_average_efficacy_estimated_interpolated_2nd_poly.csv'),
          'ETP2016 6 DS; average efficacy flat at 2014 level; interpolated, 2nd poly; see ETP2016 TAM sheet': THISDIR.joinpath('tam', 'tam_ETP2016_6_DS_average_efficacy_flat_at_2014_level_interpolated_2nd_poly_see_ETP2016_TAM_sheet.csv'),
        },
        'Conservative Cases': {
          'US DOE/ Navigant 2014 , No LED scenario, interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_US_DOE_Navigant_2014_No_LED_scenario_interpolated_2nd_poly.csv'),
          'US DOE /Navigant 2012 (2010 US lighting market characterization), interpolated, 2nd poly': THISDIR.joinpath('tam', 'tam_US_DOE_Navigant_2012_2010_US_lighting_market_characterization_interpolated_2nd_poly.csv'),
          'US EIA Annual energy outlook 2015': THISDIR.joinpath('tam', 'tam_US_EIA_Annual_energy_outlook_2015.csv'),
        },
        'Ambitious Cases': {
          'Floor space: EIA AEO 2016; Average illuminance see Lux (lm per m2); Average operating hours (h/a)': THISDIR.joinpath('tam', 'tam_Floor_space_EIA_AEO_2016_Average_illuminance_see_Lux_lm_per_m2_Average_operating_hours_ha.csv'),
          'Floor space: IEA floor space data; Average illuminance see Lux (lm per m2); Average operating hours (h/a); interpolated data': THISDIR.joinpath('tam', 'tam_Floor_space_IEA_floor_space_data_Average_illuminance_see_Lux_lm_per_m2_Average_operating_05cb930f.csv'),
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
       'Medium', 'Low', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0], dtype=np.object).set_index('param')
    ad_data_sources = {
      'Baseline Cases': {
          'US DOE 2015 SSL R&D Plan (original source: P. Smallwood, in Strategies in Light Conference, Las Vegas, February 2015), estimates 3% installed base penetration in 2014, 33% in 2020 and 88% in 2030. not sector specific but for all general lighting. Used as a proxy for commercial lighting. Interpolated, linear': THISDIR.joinpath('ad', 'ad_US_DOE_2015_SSL_RD_Plan_original_source_P__Smallwood_in_Strategies_in_Light_Conference_L_7315fa9a.csv'),
          'US DOE 2013 (MYPP) http://apps1.eere.energy.gov/buildings/publications/pdfs/ssl/ssl_mypp2013_web.pdf': THISDIR.joinpath('ad', 'ad_US_DOE_2013_MYPP_httpapps1_eere_energy_govbuildingspublicationspdfssslssl_mypp2013_web_pdf.csv'),
          'Navigant / US DOE 2015: http://energy.gov/sites/prod/files/2015/07/f24/led-adoption-report_2015.pdf': THISDIR.joinpath('ad', 'ad_Navigant_US_DOE_2015_httpenergy_govsitesprodfiles201507f24ledadoptionreport_2015_pdf.csv'),
      },
      'Conservative Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
      },
      'Region: OECD90': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'Bergesen et al. HighLED scenario (currently likely)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__HighLED_scenario_currently_likely.csv'),
        },
        'Conservative Cases': {
          'Bergesen et al. Likely LED (currently conservative)': THISDIR.joinpath('ad', 'ad_Bergesen_et_al__Likely_LED_currently_conservative.csv'),
        },
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    ref_adoption_data_per_region = None

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
      pds_adoption_is_single_source = None

    ht_ref_adoption_initial = pd.Series(
      [2.0559386403033844, 1.203539561682151, 0.17104652142368798, 0.5420894798241899, 0.15340928478053964,
       0.12392820164125475, 0.3234205780581264, 0.07626534974849451, 0.3954239644503743, 0.8447244056291314],
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

