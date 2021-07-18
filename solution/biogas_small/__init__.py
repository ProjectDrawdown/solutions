"""Small Biogas Digesters solution model.
   Excel filename: Drawdown-Small Biogas Digesters_RRS_v1.1_28Nov2018_PUBLIC.xlsm
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
      use_weight=True),
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
      filename=None, use_weight=False),
  'SOLUTION Energy Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fuel_Consumed_per_Functional_Unit.csv"),
      use_weight=True),
  'SOLUTION Fuel Efficiency Factor': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Direct_Emissions_per_Functional_Unit.csv"),
      use_weight=True),
  'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "SOLUTION_Direct_Emissions_per_Functional_Unit.csv"),
      use_weight=False),
  'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
      filename=None, use_weight=False),
  'CH4-CO2eq Tons Reduced': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "CH4_CO2eq_Tons_Reduced.csv"),
      use_weight=False),
  'N2O-CO2eq Tons Reduced': vma.VMA(
      filename=None, use_weight=False),
  'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'SOLUTION Revenue per Functional Unit': vma.VMA(
      filename=None, use_weight=False),
  'tCO2/yr per digester': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "tCO2_yr_per_digester.csv"),
      use_weight=False),
  'Black carbon GWP': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Black_carbon_GWP.csv"),
      use_weight=False),
  't CO2 eq per Metric ton of fuel': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "t_CO2_eq_per_Metric_ton_of_fuel.csv"),
      use_weight=True),
  'Average Household Biodigester Production per year': vma.VMA(
      filename=THISDIR.joinpath("vma_data", "Average_Household_Biodigester_Production_per_year.csv"),
      use_weight=False),
  'Kerosene (Heating Oil) Spot Price': vma.VMA(
      filename=DATADIR.joinpath(*('energy', 'vma_Kerosene_Heating_Oil_Spot_Price.csv')),
      use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
  "implementation unit": "Biogas plant",
  "functional unit": "TWh (therms)",
  "first cost": "US$B",
  "operating cost": "US$B",
}

name = 'Small Biogas Digesters'
solution_category = ac.SOLUTION_CATEGORY.NOT_APPLICABLE

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
       'Low', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
      ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
      ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
    tam_ref_data_sources = {
      'Baseline Cases': {
          'Calculated  from 2 sources - World Bank (2015) The State of the global Clean and Improved Cooking Sector, https://openknowledge.worldbank.org/bitstream/handle/10986/21878/96499.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_World_Bank_2015_The_State_of_the_global_Clean_and_Improved_Coo_bef286f6.csv'),
          'Calculated  from 2 sources - REN21 (2015) Renewables 2015 - Global Status Report, http://www.ren21.net/wp-content/uploads/2015/07/REN12-GSR2015_Onlinebook_low1.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_REN21_2015_Renewables_2015_Global_Status_Report_httpwww_ren21__ee9a59ea.csv'),
          'Drawdown Summation: Regional Sum': THISDIR.joinpath('tam', 'tam_Drawdown_Summation_Regional_Sum.csv'),
      },
      'Conservative Cases': {
          'IEA (2013)': THISDIR.joinpath('tam', 'tam_IEA_2013.csv'),
      },
      'Region: Asia (Sans Japan)': {
        'Baseline Cases': {
          'Calculated  from summing India and China from 2 sources - World Bank (2015) The State of the global Clean and Improved Cooking Sector, https://openknowledge.worldbank.org/bitstream/handle/10986/21878/96499.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_summing_India_and_China_from_2_sources_World_Bank_2015_The_State_of_the__778b8aac.csv'),
          'Calculated  from 2 sources - World Bank (2015) The State of the global Clean and Improved Cooking Sector, https://openknowledge.worldbank.org/bitstream/handle/10986/21878/96499.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_World_Bank_2015_The_State_of_the_global_Clean_and_Improved_Coo_bef286f6.csv'),
          'Calculated  from 2 sources - REN21 (2015) Renewables 2015 - Global Status Report, http://www.ren21.net/wp-content/uploads/2015/07/REN12-GSR2015_Onlinebook_low1.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_REN21_2015_Renewables_2015_Global_Status_Report_httpwww_ren21__ee9a59ea.csv'),
        },
        'Conservative Cases': {
          'Based on IEA (2013) World Energy Outlook': THISDIR.joinpath('tam', 'tam_based_on_IEA_2013_World_Energy_Outlook.csv'),
        },
      },
      'Region: Middle East and Africa': {
        'Baseline Cases': {
          'Based on Ibitoye, F. I. (2013). The millennium development goals and household energy requirements in Nigeria. SpringerPlus, 2(1), 529.': THISDIR.joinpath('tam', 'tam_based_on_Ibitoye_F__I__2013__The_millennium_development_goals_and_household_energy_requi_26c73895.csv'),
          'Calculated  from 2 sources - World Bank (2015) The State of the global Clean and Improved Cooking Sector, https://openknowledge.worldbank.org/bitstream/handle/10986/21878/96499.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_World_Bank_2015_The_State_of_the_global_Clean_and_Improved_Coo_bef286f6.csv'),
          'Calculated  from 2 sources - REN21 (2015) Renewables 2015 - Global Status Report, http://www.ren21.net/wp-content/uploads/2015/07/REN12-GSR2015_Onlinebook_low1.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_REN21_2015_Renewables_2015_Global_Status_Report_httpwww_ren21__ee9a59ea.csv'),
        },
        'Conservative Cases': {
          'Based on IEA (2013) World Energy Outlook': THISDIR.joinpath('tam', 'tam_based_on_IEA_2013_World_Energy_Outlook.csv'),
        },
      },
      'Region: Latin America': {
        'Baseline Cases': {
          'Calculated  from 2 sources - World Bank (2015) The State of the global Clean and Improved Cooking Sector, https://openknowledge.worldbank.org/bitstream/handle/10986/21878/96499.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_World_Bank_2015_The_State_of_the_global_Clean_and_Improved_Coo_bef286f6.csv'),
          'Calculated  from 2 sources - REN21 (2015) Renewables 2015 - Global Status Report, http://www.ren21.net/wp-content/uploads/2015/07/REN12-GSR2015_Onlinebook_low1.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_REN21_2015_Renewables_2015_Global_Status_Report_httpwww_ren21__ee9a59ea.csv'),
        },
        'Conservative Cases': {
          'Based on IEA (2013) World Energy Outlook': THISDIR.joinpath('tam', 'tam_based_on_IEA_2013_World_Energy_Outlook.csv'),
        },
      },
      'Region: China': {
        'Baseline Cases': {
          'Calculated  from 2 sources - World Bank (2015) The State of the global Clean and Improved Cooking Sector, https://openknowledge.worldbank.org/bitstream/handle/10986/21878/96499.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_World_Bank_2015_The_State_of_the_global_Clean_and_Improved_Coo_bef286f6.csv'),
          'Calculated  from 2 sources - REN21 (2015) Renewables 2015 - Global Status Report, http://www.ren21.net/wp-content/uploads/2015/07/REN12-GSR2015_Onlinebook_low1.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_REN21_2015_Renewables_2015_Global_Status_Report_httpwww_ren21__ee9a59ea.csv'),
        },
        'Conservative Cases': {
          'Based on Yuan, Y., & Zhao, I. (2013). Energy in Rural Areas of Northern China. Journal of Applied Sciences, 13(9), 1449-1454.': THISDIR.joinpath('tam', 'tam_based_on_Yuan_Y__Zhao_I__2013__Energy_in_Rural_Areas_of_Northern_China__Journal_of_Appli_91a28afa.csv'),
        },
        'Ambitious Cases': {
          'Based on IEA (2013) World Energy Outlook': THISDIR.joinpath('tam', 'tam_based_on_IEA_2013_World_Energy_Outlook.csv'),
          'Based on Mainali, B., Pachauri, S., & Nagai, Y. (2012). Analyzing cooking fuel and stove choices in China till 2030. Journal of Renewable and Sustainable Energy, 4(3), 031805.': THISDIR.joinpath('tam', 'tam_based_on_Mainali_B__Pachauri_S__Nagai_Y__2012__Analyzing_cooking_fuel_and_stove_choices__e3f8fc59.csv'),
        },
      },
      'Region: India': {
        'Baseline Cases': {
          'Based on Nakagami, H., Murakoshi, C., & Iwafune, Y. (2008). International comparison of household energy consumption and its indicator. Proceedings of the 2008 ACEEE Summer Study on Energy Efficiency in Buildings, 214-224.': THISDIR.joinpath('tam', 'tam_based_on_Nakagami_H__Murakoshi_C__Iwafune_Y__2008__International_comparison_of_household_58b0d8c2.csv'),
          'Calculated  from 2 sources - World Bank (2015) The State of the global Clean and Improved Cooking Sector, https://openknowledge.worldbank.org/bitstream/handle/10986/21878/96499.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_World_Bank_2015_The_State_of_the_global_Clean_and_Improved_Coo_bef286f6.csv'),
          'Calculated  from 2 sources - REN21 (2015) Renewables 2015 - Global Status Report, http://www.ren21.net/wp-content/uploads/2015/07/REN12-GSR2015_Onlinebook_low1.pdf AND Daioglou, V., Van Ruijven, B. J., & Van Vuuren, D. P. (2012). Model projections for household energy use in developing countries. Energy, 37(1), 601-615.': THISDIR.joinpath('tam', 'tam_Calculated_from_2_sources_REN21_2015_Renewables_2015_Global_Status_Report_httpwww_ren21__ee9a59ea.csv'),
        },
        'Conservative Cases': {
          'Based on IEA (2013) World Energy Outlook': THISDIR.joinpath('tam', 'tam_based_on_IEA_2013_World_Energy_Outlook.csv'),
        },
        'Maximum Cases': {
          'Based on Venkataraman, C., Sagar, A. D., Habib, G., Lam, N., & Smith, K. R. (2010). The Indian national initiative for advanced biomass cookstoves: the benefits of clean combustion. Energy for Sustainable Development, 14(2), 63-72.': THISDIR.joinpath('tam', 'tam_based_on_Venkataraman_C__Sagar_A__D__Habib_G__Lam_N__Smith_K__R__2010__The_Indian_nation_114cfe53.csv'),
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
    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
    ad_data_sources = {
      'Baseline Cases': {
          'Project Drawdown Assumption of all Regions Growing to Asias Current Percent Adoption': THISDIR.joinpath('ad', 'ad_Project_Drawdown_Assumption_of_all_Regions_Growing_to_Asias_Current_Percent_Adoption.csv'),
      },
      'Ambitious Cases': {
          'Project Drawdown Assumption of all Regions Growing to Chinas Current Percent Adoption': THISDIR.joinpath('ad', 'ad_Project_Drawdown_Assumption_of_all_Regions_Growing_to_Chinas_Current_Percent_Adoption.csv'),
      },
      'Maximum Cases': {
          'Project Drawdown Assumption of all Regions Growing to 100 Percent Adoption': THISDIR.joinpath('ad', 'ad_Project_Drawdown_Assumption_of_all_Regions_Growing_to_100_Percent_Adoption.csv'),
      },
    }
    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
        adconfig=adconfig)

    # Custom REF Data
    ca_ref_data_sources = [
      {'name': 'Drawdown Book Edition 1 REF Scenario', 'include': False,
          'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Drawdown_Book_Edition_1_REF_Scenario.csv')},
    ]
    self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
        soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
        high_sd_mult=1.0, low_sd_mult=1.0,
        total_adoption_limit=ref_tam_per_region)

    ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

    if False:
      # One may wonder why this is here. This file was code generated.
      # This 'if False' allows subsequent conditions to all be elif.
      pass
    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      pds_adoption_data_per_region = self.ad.adoption_data_per_region()
      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
      pds_adoption_is_single_source = self.ad.adoption_is_single_source()

    ht_ref_adoption_initial = pd.Series(
      [86.0, 0.0, 0.0, 25.04194984517459, 5.337266131329677,
       36.925127117549664, 0.0, 0.0, 0.0, 0.0],
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
        ref_adoption_data_per_region=ref_adoption_data_per_region,
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

