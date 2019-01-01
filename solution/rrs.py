"""Features shared by most or all of the
   Reduction and Replacement Solution (RRS) implementations.
"""

import pathlib
import pandas as pd
from model import vma


datadir = pathlib.Path(__file__).parents[1]
tam_ref_data_sources = {
    'Baseline Cases': {
      'Baseline: Based on- IEA ETP 2016 6DS': str(datadir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_6DS.csv')),
      'Baseline: Based on- AMPERE MESSAGE-MACRO Reference': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_Reference.csv')),
      'Baseline: Based on- AMPERE GEM E3 Reference': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_Reference.csv')),
      'Baseline: Based on- AMPERE IMAGE/TIMER Reference': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_Reference.csv')),
      },
    'Conservative Cases': {
      'Conservative: Based on- IEA ETP 2016 4DS': str(datadir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_4DS.csv')),
      'Conservative: Based on- AMPERE MESSAGE-MACRO 550': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_550.csv')),
      'Conservative: Based on- AMPERE GEM E3 550': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_550.csv')),
      'Conservative: Based on- AMPERE IMAGE/TIMER 550': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_550.csv')),
      'Conservative: Based on- Greenpeace 2015 Reference': str(datadir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Reference.csv')),
      },
    'Ambitious Cases': {
      'Ambitious: Based on- IEA ETP 2016 2DS': str(datadir.joinpath(
        'data', 'energy', 'IEA_ETP_2016_2DS.csv')),
      'Ambitious: Based on- AMPERE MESSAGE-MACRO 450': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_MESSAGE_MACRO_450.csv')),
      'Ambitious: Based on- AMPERE GEM E3 450': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_GEM_E3_450.csv')),
      'Ambitious: Based on- AMPERE IMAGE/TIMER 450': str(datadir.joinpath(
        'data', 'energy', 'AMPERE_2014_IMAGE_TIMER_450.csv')),
      'Ambitious: Based on- Greenpeace Energy [R]evolution': str(datadir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Energy_Revolution.csv')),
      },
    '100% RES2050 Case': {
      '100% REN: Based on- Greenpeace Advanced [R]evolution': str(datadir.joinpath(
        'data', 'energy', 'Greenpeace_2015_Advanced_Revolution.csv')),
      },
}
tam_pds_data_sources = {
    'Ambitious Cases': {
      'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario': str(datadir.joinpath(
        'data', 'energy', 'PDS_plausible_scenario.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario': str(datadir.joinpath(
        'data', 'energy', 'PDS_drawdown_scenario.csv')),
      'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario': str(datadir.joinpath(
        'data', 'energy', 'PDS_optimum_scenario.csv')),
      },
}

vma_oil_plant_efficiency = vma.AvgHighLow(pd.DataFrame([
  # 'Variable Meta-analysis'!C995:X1024, VMA #27
  ['Hondo (2005) Oil fired powerplant',
      'http://www.univie.ac.at/photovoltaik/umwelt/LCA_japanstudy.pdf',
      'OECD90', 'Japan', '', '2005', '', '39%', '%', ''],
  ], columns=['Source ID', 'Link', 'Region', 'Specific Geographic Location',
    'Source Validation Code', 'Year', 'License Code', 'Raw Data Input',
    'Original Units', 'Weight']),
  low_sd=1.0, high_sd=1.0, use_weight=False)

# For the IEA data, minimum and maximum lower heating values (LHV) are included.
# The average EIA data from 2004-2014 is reported in Btu/kWh, and this average
# is converted to an efficiency measure by dividing the equivalent Btu content
# of a kWh of electricity (which is 3,412 Btu) by the raw data input (see:
# https://www.eia.gov/tools/faqs/faq.cfm?id=667&t=2). For the IPCC data,
# minimum, median, and maximum values are included. NOTE: the IPCC uses the
# following sources for calculating minimum, median, and maximum fixed annual
# opeartion and maintenance costs for coal and natural gas:
# Coal PC (Pulverized Coal): Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
#   IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
# Gas Combined Cycle: Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
#   IEA (2011),IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
vma_natural_gas_plant_efficiency = vma.AvgHighLow(pd.DataFrame([
    # 'Variable Meta-analysis'!C960:X989, VMA #26
    ['IPCC WG3 AR5, min  (Table A.III.2)',
      'https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf',
      'World', '', '', '2014', '', '41%', '%', ''],
    #['IPCC WG3 AR5, median  (Table A.III.2)',
    #  'https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf',
    #  'World', '', '', '2014', '', '55%', '%', ''],
    ['IPCC WG3 AR5, max  (Table A.III.2)',
      'https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf',
      'World', '', '', '2014', '', '60%', '%', ''],
    ['IEA 2010, ETSAP, OCGT, lower heating value, min',
      'http://www.iea-etsap.org/web/e-techds/pdf/e02-gas_fired_power-gs-ad-gct.pdf',
      'World', '', '', '2010', '', '35%', '%', ''],
    ['IEA 2010, ETSAP, OCGT, lower heating value, max',
      'http://www.iea-etsap.org/web/e-techds/pdf/e02-gas_fired_power-gs-ad-gct.pdf',
      'World', '', '', '2010', '', '42%', '%', ''],
    ['IEA 2010, ETSAP, CCGT, lower heating value, min',
      'http://www.iea-etsap.org/web/e-techds/pdf/e02-gas_fired_power-gs-ad-gct.pdf',
      'World', '', '', '2010', '', '52%', '%', ''],
    ['IEA 2010, ETSAP, CCGT, lower heating value, max',
      'http://www.iea-etsap.org/web/e-techds/pdf/e02-gas_fired_power-gs-ad-gct.pdf',
      'World', '', '', '2010', '', '60%', '%', ''],
    ['US EIA, Average 2004-2014',
      'http://www.eia.gov/electricity/annual/html/epa_08_01.html',
      'World', '', '', '2015', '', '8251.636364', 'Btu/kWh', '41.35%'],
  ], columns=['Source ID', 'Link', 'Region', 'Specific Geographic Location',
    'Source Validation Code', 'Year', 'License Code', 'Raw Data Input',
    'Original Units', 'Weight']),
  low_sd=1.0, high_sd=1.0, use_weight=False)

# For the IEA data, a lower heating value (LHV) is used. The average EIA data
# from 2004-2014 is reported in Btu/kWh, and this average is converted to an
# efficiency measure by dividing the equivalent Btu content of a kWh of
# electricity (which is 3,412 Btu) by the raw data input (see:
# https://www.eia.gov/tools/faqs/faq.cfm?id=667&t=2). For the IPCC data,
# minimum, median, and maximum values are included.NOTE: the IPCC uses the
# following sources for calculating minimum, median, and maximum fixed annual
# opeartion and maintenance costs for coal and natural gas:
# Coal PC (Pulverized Coal): Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
#    IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
# Gas Combined Cycle: Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
#    IEA (2011),IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
vma_coal_plant_efficiency = vma.AvgHighLow(pd.DataFrame([
    # 'Variable Meta-analysis'!C926:X955, VMA #25
    ['IPCC WG3 AR5, min  (Table A.III.2)',
      'https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf',
      'World', '', '', '2014', '', '33%', '%', ''],
    #['IPCC WG3 AR5, median  (Table A.III.2)',
    #  'https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf',
    #  'World', '', '', '2014', '', '39%', '%', ''],
    ['IPCC WG3 AR5, max  (Table A.III.2)',
      'https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf',
      'World', '', '', '2014', '', '48%', '%', ''],
    ['IEA 2010, Power Generation from Coal (p. 61), lower heating value (LHV)',
      'https://www.iea.org/ciab/papers/power_generation_from_coal.pdf',
      'World', '', '', '2010', '', '33%', '%', ''],
    ['US EIA, Average 2004-2014',
      'http://www.eia.gov/electricity/annual/html/epa_08_01.html',
      'USA', '', '', '2015', '', '10406', 'BTU/kWh', ''],
  ], columns=['Source ID', 'Link', 'Region', 'Specific Geographic Location',
    'Source Validation Code', 'Year', 'License Code', 'Raw Data Input',
    'Original Units', 'Weight']),
  low_sd=1.0, high_sd=1.0, use_weight=False)

(oil_efficiency, _, _) = vma_oil_plant_efficiency.avg_high_low()
(natural_gas_efficiency, _, _) = vma_natural_gas_plant_efficiency.avg_high_low()
(coal_efficiency, _, _) = vma_coal_plant_efficiency.avg_high_low()

class RRS:
  def __init__(self, total_energy_demand):
    """Data structures to support the Reduction and Replacement Solutions.
       Arguments:
         total_energy_demand: in Terawatt-Hours (TWh), value typically supplied by tam.py
    """
    self.total_energy_demand = total_energy_demand
    self.energy_adoption_mix = {
      # source for coal, natural gas, nuclear, and oil:
      # The World Bank Data in The Shift Project Data Portal
      # http://www.tsp-data-portal.org/Breakdown-of-Electricity-Generation-by-Energy-Source#tspQvChart
      'Coal': 8726.0 / total_energy_demand,
      'Natural gas': 4933.0 / total_energy_demand,
      'Nuclear': 2417.0 / total_energy_demand,
      'Oil': 1068.0 / total_energy_demand,
      # source for remaining data:
      # IRENA (2016) Renewable Energy Statistics
      # http://www.irena.org/DocumentDownloads/Publications/IRENA_RE_Statistics_2016.pdf
      'Hydroelectric': 4019.0 / total_energy_demand,
      'Solar Photovoltaic': 188.073 / total_energy_demand,
      'Wave and Tidal': 0.954 / total_energy_demand,
      'Wind Onshore': 688.956 / total_energy_demand,
      'Wind Offshore': 24.89 / total_energy_demand,
      'Biomass and Waste': 399.496 / total_energy_demand,
      'Concentrated Solar Power': 8.735 / total_energy_demand,
      'Geothermal': 74.195 / total_energy_demand,
    }

    # This variable creates a weighted average CONVENTIONAL Plant Efficiency by
    # applying a weight to averaged plant efficiency data for coal and natural
    # gas (see two variables below). The weights are based on the percentage, for
    # the given technology, of total global generation. These values (TWh) are
    # based on the IEA 2016 Energy Technology Perspectives (ETP) scenario.
    self.vma_conv_ref_plant_efficiency = vma.AvgHighLow(pd.DataFrame([
        # 'Variable Meta-analysis'!C926:X955, VMA #25
        ['From vma_coal_plant_efficiency variable', '', 'World', '', '',
          'Various', '', '37.1577551412647%', '%', self.energy_adoption_mix['Coal']],
        ['From vma_natural_gas_plant_efficiency variable', '', 'World', '', '',
          'Various', '', '48.2936717783726%', '%', self.energy_adoption_mix['Natural gas']],
        ['From vma_oil_plant_efficiency variable', '', 'OECD90', 'Japan', '',
          '2005', '', '39%', '%', self.energy_adoption_mix['Oil']],

        # 'Advanced Controls'!D111:F111 do not link to the results from the VMA tab,
        # instead there are fixed values which are similar to but not especially close
        # to the VMA values. It looks like a snapshot from some time ago, when the
        # data sources might have been different.
        # To match the results from Excel, we use the same values above, where the constants
        # come from SolarPVUtility 'Advanced Controls'!D111:F111. Once we retire
        # Excel and no longer need to match its results, the three rows above should be
        # deleted and use the calculated values below. TODO.
        #['From vma_coal_plant_efficiency variable', '', 'World', '', '',
        #  'Various', '', coal_efficiency, '', ''],
        #['From vma_natural_gas_plant_efficiency variable', '', 'World', '', '',
        #  'Various', '', natural_gas_efficiency, '', ''],
        #['From vma_oil_plant_efficiency variable', '', 'OECD90', 'Japan', '',
        #  '2005', '', oil_efficiency, '', '4.74%'],
      ], columns=['Source ID', 'Link', 'Region', 'Specific Geographic Location',
        'Source Validation Code', 'Year', 'License Code', 'Raw Data Input',
        'Original Units', 'Weight']),
      low_sd=1.0, high_sd=1.0, use_weight=True)


