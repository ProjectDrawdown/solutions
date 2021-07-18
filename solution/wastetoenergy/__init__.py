"""Waste to Energy solution model.
   Excel filename: WastetoEnergy_RRS_ELECGEN_v1.1b_24Oct18.xlsm
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
      filename=DATADIR.joinpath(*('energy', 'vma_CONVENTIONAL_First_Cost_per_Implementation_Unit.csv')),
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
      use_weight=True),
  'SOLUTION Average Annual Use': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
      use_weight=False),
  'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
      filename=DATADIR.joinpath(*('energy', 'vma_CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit_2.csv')),
      use_weight=True),
  'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fixed_Operating_Cost_FOM.csv"),
      use_weight=True),
  'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Energy Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'Total Energy Used per SOLUTION functional unit': vma.VMA(
      filename=None, use_weight=False),
  'Fuel Consumed per CONVENTIONAL Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Fuel Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Direct_Emissions_per_Functional_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
      use_weight=False),
  'CH4-CO2eq Tons Reduced': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CH4_CO2eq_Tons_Reduced.csv"),
      use_weight=False),
  'N2O-CO2eq Tons Reduced': vma.VMA(
      filename=None, use_weight=False),
  '2005-2014 Average CONVENTIONAL Fuel Price per functional unit': vma.VMA(
      filename=DATADIR.joinpath(*('energy', 'vma_2005_2014_Average_CONVENTIONAL_Fuel_Price_per_functional_unit_2.csv')),
      use_weight=True),
  'Weighted Average CONVENTIONAL Plant Efficiency': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Weighted_Average_CONVENTIONAL_Plant_Efficiency.csv"),
      use_weight=True),
  'Coal Plant Efficiency': vma.VMA(
      filename=DATADIR.joinpath(*('energy', 'vma_Coal_Plant_Efficiency_2.csv')),
      use_weight=False),
  'Natural Gas Plant Efficiency': vma.VMA(
      filename=DATADIR.joinpath('energy', "vma_data", "Natural_Gas_Plant_Efficiency.csv"),
      use_weight=False),
  'Oil Plant Efficiency': vma.VMA(
      filename=DATADIR.joinpath(*('energy', 'vma_Oil_Plant_Efficiency_2.csv')),
      use_weight=False),
  'Net Electrical Effciency (%)': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Net_Electrical_Effciency.csv"),
      use_weight=False),
  'tN2O - CO2-eq - Emitted from Incineration': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "tN2O_CO2_eq_Emitted_from_Incineration.csv"),
      use_weight=False),
  'tCH4-CO2-eq - Emitted from Incineration': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "tCH4_CO2_eq_Emitted_from_Incineration.csv"),
      use_weight=False),
  'tCO2 per TWh - emitted from combustion': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "tCO2_per_TWh_emitted_from_combustion.csv"),
      use_weight=False),
  'Metal Recycling tCO2-eq/TWh reduced': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Metal_Recycling_tCO2_eq_TWh_reduced.csv"),
      use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": "TW",
  "functional unit": "TWh",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Waste to Energy'
solution_category = ac.SOLUTION_CATEGORY.REPLACEMENT

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)


class Scenario(scenario.Scenario):
  name = name
  units = units
  vmas = VMAs
  solution_category = solution_category

  def __init__(self, scenario=None):
    if scenario is None:
      scenario = list(scenarios.keys())[0]
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
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.energy_tam_1_ref_data_sources,
      tam_pds_data_sources=rrs.energy_tam_1_pds_data_sources)
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
      'Region: OECD90': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
        },
      },
      'Region: Eastern Europe': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
        },
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
          'Based on Greenpeace (2015) Reference Scen- CHP Electricity Included - Modified to include Renewable and NonRenewable Waste by Erika Boeing, 2016 - See Adoption Factoring!': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Reference_Scen_CHP_Electricity_Included_Modified_to_include_Ren_ceb5044c.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
          'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
        },
        '100% RES2050 Case': {
          'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
          'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
          'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
        },
        '100% RES2050 Case': {
          'Based on: Greenpeace 2015 Advanced Revolution.1': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution_1.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
          'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
          'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
          'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
          'Based on IEA (2016) 2DS  Modified to include Renewable and NonRenewable Waste by Erika Boeing, 2016, see Adoption_Factoring!': THISDIR.joinpath('ad', 'ad_based_on_IEA_2016_2DS_Modified_to_include_Renewable_and_NonRenewable_Waste_by_Erika_Boei_c94b414a.csv'),
          'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
        },
        '100% RES2050 Case': {
          'Based on: Greenpeace 2015 Advanced Revolution.1': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution_1.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
          'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
          'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
          'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
          'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
          'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
        },
        '100% RES2050 Case': {
          'Based on: Greenpeace 2015 Advanced Revolution.1': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution_1.csv'),
        },
      },
      'Region: EU': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
          'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
          'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
          'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
          'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
          'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
        },
        '100% RES2050 Case': {
          'Based on: Greenpeace 2015 Advanced Revolution.1': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution_1.csv'),
        },
      },
      'Region: USA': {
        'Baseline Cases': {
          'Monni et al Methodology,Decreasing Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_MethodologyDecreasing_Cap_Customized_Prognostication_by_Erika_Boeing_2016_Se_e9ca4246.csv'),
          'Based on: IEA ETP 2016 6DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_6DS.csv'),
        },
        'Conservative Cases': {
          'Monni et al Methodology, 48.2% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_48_2_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_was_85599acc.csv'),
          'Based on: IEA ETP 2016 4DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_4DS.csv'),
          'Based on: Greenpeace 2015 Energy Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
        },
        'Ambitious Cases': {
          'Monni et al Methodology, 75% Cap, Customized Prognostication by Erika Boeing, 2016, See waste_toWTE and wte_electricity tabs': THISDIR.joinpath('ad', 'ad_Monni_et_al_Methodology_75_Cap_Customized_Prognostication_by_Erika_Boeing_2016_See_waste_8d463c6a.csv'),
          'Based on: IEA ETP 2016 2DS': THISDIR.joinpath('ad', 'ad_based_on_IEA_ETP_2016_2DS.csv'),
          'Based on: Greenpeace 2015 Advanced Revolution': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
        },
        '100% RES2050 Case': {
          'Based on: Greenpeace 2015 Advanced Revolution.1': THISDIR.joinpath('ad', 'ad_based_on_Greenpeace_2015_Advanced_Revolution_1.csv'),
        },
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    # Custom PDS Data
    ca_pds_data_sources = [
      {'name': 'Baseline Case_ Monni et al Methodology,Decreasing Cap', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Baseline_Case__Monni_et_al_MethodologyDecreasing_Cap.csv')},
      {'name': 'Based on: IEA ETP 2016 6DS', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_based_on_IEA_ETP_2016_6DS.csv')},
      {'name': 'Drawdown Scenario Integrated Adoption', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Drawdown_Scenario_Integrated_Adoption.csv')},
      {'name': 'Optimum Scenario Integrated Adoption', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Optimum_Scenario_Integrated_Adoption.csv')},
      {'name': 'Monni et al Methodology, 48.2% Cap,', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Monni_et_al_Methodology_48_2_Cap.csv')},
      {'name': 'Based on: IEA ETP 2016 4DS', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_based_on_IEA_ETP_2016_4DS.csv')},
      {'name': 'Based on: Greenpeace 2015 Reference', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_based_on_Greenpeace_2015_Reference.csv')},
      {'name': 'Monni et al Methodology, 75% Cap,', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Monni_et_al_Methodology_75_Cap.csv')},
      {'name': 'Based on: IEA ETP 2016 Annex', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_based_on_IEA_ETP_2016_Annex.csv')},
      {'name': 'Based on: IEA ETP 2016 2DS', 'include': True,
          'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_based_on_IEA_ETP_2016_2DS.csv')},
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
      [87.6267887442796, 51.17031245078304, 2.2000998651967416, 29.05180238687869, 2.1836150772536023,
       10.670422548840941, 12.355592643914243, 4.801134096492596, 74.56251675648713, 27.036465455169868],
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
        fc_convert_iunit_factor=rrs.TERAWATT_TO_KILOWATT)

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
        conversion_factor=rrs.TERAWATT_TO_KILOWATT)

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

