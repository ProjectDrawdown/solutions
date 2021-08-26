"""LED Commercial Lighting solution model.
   Excel filename: Drawdown-LED Commercial Lighting_RRS_v1.1_19Nov2018_PUBLIC.xlsm
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
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
      use_weight=True),
  'SOLUTION First Cost per Implementation Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Lifetime Capacity': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
      use_weight=True),
  'SOLUTION Lifetime Capacity': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
      use_weight=False),
  'CONVENTIONAL Average Annual Use': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
      use_weight=False),
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
      use_weight=True),
  'SOLUTION Energy Efficiency Factor': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Energy_Efficiency_Factor.csv"),
      use_weight=False),
  'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Fuel Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Indirect_CO2_Emissions_per_Unit.csv"),
      use_weight=True),
  'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
      use_weight=False),
  'CH4-CO2eq Tons Reduced': vma.VMA(
      filename=None, use_weight=False),
  'N2O-CO2eq Tons Reduced': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": "Petalumen (Plm)",
  "functional unit": "Petalumen hours (Plmh)",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'LED Commercial Lighting'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-82p2050-E18.8% (Book Ed.1)"
PDS2 = "PDS2-90p2050-E18.2%-Linear 90% (Book Ed.1)"
PDS3 = "PDS3-95p2050-E17.3%-Linear 95% (Book Ed.1)"

class Scenario(scenario.RRSScenario):
  name = name
  units = units
  vmas = VMAs
  solution_category = solution_category

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
  tam_pds_data_sources = tam_ref_data_sources

  def __init__(self, scenario=None):
    if isinstance(scenario, ac.AdvancedControls):
        self.scenario = scenario.name
        self.ac = scenario
    else:
        self.scenario = scenario or PDS2
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
       'Medium', 'Low', 'Medium', 'Medium', 'Medium',
       'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
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

