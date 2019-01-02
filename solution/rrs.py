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


oil_plant_efficiency_vma = vma.AvgHighLow(pd.DataFrame([
  # 'Variable Meta-analysis'!C995:X1024, VMA #27
  ['Hondo (2005) Oil fired powerplant',
      'http://www.univie.ac.at/photovoltaik/umwelt/LCA_japanstudy.pdf',
      'OECD90', 'Japan', '', '2005', '', '39%', '%', ''],
  ], columns=vma.columns), low_sd=1.0, high_sd=1.0, use_weight=False)

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
natural_gas_plant_efficiency_vma = vma.AvgHighLow(pd.DataFrame([
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
  ], columns=vma.columns), low_sd=1.0, high_sd=1.0, use_weight=False)

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
coal_plant_efficiency_vma = vma.AvgHighLow(pd.DataFrame([
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
  ], columns=vma.columns), low_sd=1.0, high_sd=1.0, use_weight=False)

(oil_efficiency, _, _) = oil_plant_efficiency_vma.avg_high_low()
(natural_gas_efficiency, _, _) = natural_gas_plant_efficiency_vma.avg_high_low()
(coal_efficiency, _, _) = coal_plant_efficiency_vma.avg_high_low()


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
    self.conv_ref_plant_efficiency_vma = vma.AvgHighLow(pd.DataFrame([
        # 'Variable Meta-analysis'!C926:X955, VMA #25
        ['From coal_plant_efficiency_vma variable', '', 'World', '', '',
          'Various', '', '37.1577551412647%', '%', self.energy_adoption_mix['Coal']],
        ['From natural_gas_plant_efficiency_vma variable', '', 'World', '', '',
          'Various', '', '48.2936717783726%', '%', self.energy_adoption_mix['Natural gas']],
        ['From oil_plant_efficiency_vma variable', '', 'OECD90', 'Japan', '',
          '2005', '', '39%', '%', self.energy_adoption_mix['Oil']],

        # 'Advanced Controls'!D111:F111 do not link to the results from the VMA tab,
        # instead there are fixed values which are similar to but not especially close
        # to the VMA values. It looks like a snapshot from some time ago, when the
        # data sources might have been different.
        # To match the results from Excel, we use the same values above, where the constants
        # come from SolarPVUtility 'Advanced Controls'!D111:F111. Once we retire
        # Excel and no longer need to match its results, the three rows above should be
        # deleted and use the calculated values below. TODO.
        #['From coal_plant_efficiency_vma variable', '', 'World', '', '',
        #  'Various', '', coal_efficiency, '', ''],
        #['From natural_gas_plant_efficiency_vma variable', '', 'World', '', '',
        #  'Various', '', natural_gas_efficiency, '', ''],
        #['From oil_plant_efficiency_vma variable', '', 'OECD90', 'Japan', '',
        #  '2005', '', oil_efficiency, '', self.energy_adoption_mix['Oil']],
      ], columns=vma.columns), low_sd=1.0, high_sd=1.0, use_weight=True)

    # The value for CONVENTIONAL First Cost is calculated by taking the weighted
    # average of first cost values for conventional electricity generating
    # technologies that will be directly replaced by the solution. The weight is
    # the percentage share, for the given technology, of total global generatiion
    # in 2014. These figures on historical generation were collected from The World
    # Bank Data in The Shift Project Data Portal
    # (http://www.tsp-data-portal.org/Breakdown-of-Electricity-Generation-by-Energy-Source#tspQvChart).
    # NOTE: the IPCC uses the following sources for calculating minimum, median,
    # and maximum First Cost for coal and natural gas:
    # Coal PC (Pulverized Coal): Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
    #   IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
    # Gas Combined Cycle: Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
    #   IEA (2011),IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
    # NOTE: Lazard's LCOE Analysis Version 10.0 includes carbon capture and storage
    # coal technology in its ""high estimate"" for costs, which is why these are not
    # included.
    self.conv_2014_cost_vma = vma.AvgHighLow(pd.DataFrame([
        # 'Variable Meta-analysis'!C84:X106, VMA #2
        ["IPCC WG3 AR5, Coal - PC, min   (Table A.III.1)",
          "https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf",
          "World ", "", "1  - Peer Reviewed", "2014", "", 380, "US$2010/kW",
          self.energy_adoption_mix['Coal']],
        ["IPCC WG3 AR5, Coal - PC, max  (Table A.III.1)",
          "https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf",
          "World ", "", "1  - Peer Reviewed", "2014", "", 3900, "US$2010/kW",
          self.energy_adoption_mix['Coal']],
        ["IPCC WG3 AR5, Natural Gas - CCGT, min  (Table A.III.1)",
          "https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf",
          "World ", "", "1  - Peer Reviewed", "2014", "", 550, "US$2010/kW",
          self.energy_adoption_mix['Natural gas']],
        ["IPCC WG3 AR5, Natural Gas - CCGT, max  (Table A.III.1)",
          "https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf",
          "World ", "", "1  - Peer Reviewed", "2014", "", 2100, "US$2010/kW",
          self.energy_adoption_mix['Natural gas']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, coal, low estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "", 3000, "US$2016/kW",
          self.energy_adoption_mix['Coal']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, natural gas (Combined Cycle), low estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "", 1000, "US$2016/kW",
          self.energy_adoption_mix['Natural gas']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, natural gas (Combined Cycle), high estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "", 1300, "US$2016/kW",
          self.energy_adoption_mix['Natural gas']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, Diesel Reciprocrating Engine Low Estimtae",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "", 500, "US$2016/kW",
          self.energy_adoption_mix['Oil']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, Diesel Reciprocrating Engine High estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "", 800, "US$2016/kW",
          self.energy_adoption_mix['Oil']],
        ["IEA (2010) Projected Costs of generating Electricity (oil plants)",
          "http://www.worldenergyoutlook.org/media/weowebsite/energymodel/ProjectedCostsofGeneratingElectricity2010.pdf",
          "Middle East and Africa", "South Africa", "2 - Public Sector/ Multilateral Agency",
          "2010", "", 461, "US$2010/kW", self.energy_adoption_mix['Oil']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing the costs of photovoltaic and wind power in six developing countries. Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - natural gas combined cycle",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "", 700000, "€2012/MW",
          self.energy_adoption_mix['Natural gas']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing the costs of photovoltaic and wind power in six developing countries. Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - sub critical hard coal",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "", 1400000, "€2012/MW",
          self.energy_adoption_mix['Coal']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing the costs of photovoltaic and wind power in six developing countries.Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - light fuel oil based generation",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "", 700000, "€2012/MW",
          self.energy_adoption_mix['Oil']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing the costs of photovoltaic and wind power in six developing countries. Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - heavy fuel oil based generation",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "", 750000, "€2012/MW",
          self.energy_adoption_mix['Oil']],
        ["OECD/NEA 2015 -  Combined Cycle natural gas (Minimum)",
          "https://www.oecd-nea.org/ndd/pubs/2015/7057-proj-costs-electricity-2015.pdf",
          "World ", "", "2 - Public Sector/ Multilateral Agency", "2015", "", 627,
          "US$2015/kW", self.energy_adoption_mix['Natural gas']],
        ["OECD/NEA 2015 - Combined Cycle natural gas (Maximum)",
          "https://www.oecd-nea.org/ndd/pubs/2015/7057-proj-costs-electricity-2015.pdf",
          "World", "", "2 - Public Sector/ Multilateral Agency", "2015", "", 1289,
          "US$2015/kW", self.energy_adoption_mix['Natural gas']],
        ["OECD/NEA 2015 - Pulverised Coal fired technology (minimum)",
            "https://www.oecd-nea.org/ndd/pubs/2015/7057-proj-costs-electricity-2015.pdf",
            "World", "", "2 - Public Sector/ Multilateral Agency", "2015", "", 813,
            "US$2015/kW", self.energy_adoption_mix['Coal']],
        ["OECD/NEA 2015 - Pulverised Coal fired technology (Maximum)",
            "https://www.oecd-nea.org/ndd/pubs/2015/7057-proj-costs-electricity-2015.pdf",
            "World", "", "2 - Public Sector/ Multilateral Agency", "2015", "", 3067,
            "US$2015/kW", self.energy_adoption_mix['Coal']],
        ["US EIA (2013) Conventional Natural gas Combined Cycle",
            "https://www.eia.gov/outlooks/capitalcost/pdf/updated_capcost.pdf",
            "USA", "", "2 - Public Sector/ Multilateral Agency", "2012", "", 917,
            "US$2012/kW", self.energy_adoption_mix['Natural gas']],
        ["US EIA (2013) Coal Dual Unit IGCC",
            "https://www.eia.gov/outlooks/capitalcost/pdf/updated_capcost.pdf",
            "USA", "", "2 - Public Sector/ Multilateral Agency", "2012", "", 4440,
            "US$2012/kW", self.energy_adoption_mix['Coal']],
        ["EnergyNet.DK - advanced pulverized coal fired powerplant",
            "https://energiatalgud.ee/img_auth.php/4/42/Energinet.dk._Technology_Data_for_Energy_Plants._2012.pdf",
            "EU", "Denmark", "2 - Public Sector/ Multilateral Agency", "2012", "", 2040,
            "€2011/kW", self.energy_adoption_mix['Coal']],
        ["EnergyNet.DK - gas turbine combined cycle (back pressure)",
            "https://energiatalgud.ee/img_auth.php/4/42/Energinet.dk._Technology_Data_for_Energy_Plants._2012.pdf",
            "EU", "Denmark", "2 - Public Sector/ Multilateral Agency", "2012", "", 1350,
            "€2011/kW", self.energy_adoption_mix['Natural gas']],
      ], columns=vma.columns), low_sd=1.0, high_sd=1.0, use_weight=True)
    (self.conv_2014_cost, _, _) = self.conv_2014_cost_vma.avg_high_low()

    # The value for Lifetime Capacity - Conventional is calculated by taking the weighted
    # average of lifetime capacity values (kWh/kW) for conventional electricity generating
    # technologies that will be directly replaced by the solution. Raw data inputs in
    # years are converted to kWh/kW by multiplying by the Average Annual Use - Conventional
    # variable. The weight is the percentage share, for the given technology, of total
    # global generation. These figures on historical generation were collected from
    # The World Bank Data in The Shift Project Data Portal
    # (http://www.tsp-data-portal.org/Breakdown-of-Electricity-Generation-by-Energy-Source#tspQvChart).
    # NOTE: the IPCC uses the following sources for Lifetime Capacity for coal and natural gas:
    #   Coal PC (Pulverized Coal): Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
    #     IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
    #   Gas Combined Cycle: Black and Veatch (2012), DEA (2012), IEA/NEA (2010),
    #     IEA (2011),IEA (2013a), IEA-RETD (2013), Schmidt et al. (2012), US EIA (2013).
    self.conv_lifetime_years_vma = vma.AvgHighLow(pd.DataFrame([
        # 'Variable Meta-analysis'!C84:X106, VMA #2
        ["IPCC WG3 AR5, Coal  (Table A.III.1)",
          "https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf",
          "World", "", "1  - Peer Reviewed", "2014", "",
          40, "years", self.energy_adoption_mix['Coal']],
        ["IPCC WG3 AR5, Natural Gas  (Table A.III.1)",
          "https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf",
          "World", "", "1  - Peer Reviewed", "2014", "",
          30, "years", self.energy_adoption_mix['Natural gas']],
        ["IEA Technology Roadmap 2012, Coal",
          "http://www.iea.org/publications/freepublications/publication/TechnologyRoadmapHighEfficiencyLowEmissionsCoalFiredPowerGeneration_WEB_Updated_March2013.pdf",
          "World", "", "2 - Public Sector/ Multilateral Agency", "2012", "",
          50, "years", self.energy_adoption_mix['Coal']],
        ["IEA, ETSAP, 2010, Natural Gas",
          "http://www.iea-etsap.org/web/e-techds/pdf/e02-gas_fired_power-gs-ad-gct.pdf",
          "World", "", "2 - Public Sector/ Multilateral Agency", "2010", "",
          30, "years", self.energy_adoption_mix['Natural gas']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, coal",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          40, "years", self.energy_adoption_mix['Coal']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, natural gas (Combined Cycle)",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          20, "years", self.energy_adoption_mix['Natural gas']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, Diesel reciprocating engine",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          20, "years", self.energy_adoption_mix['Oil']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing  the  costs  of  photovoltaic and wind power in six developing countries. Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - natural gas combined cycle",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "",
          25, "years", self.energy_adoption_mix['Natural gas']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing  the  costs  of  photovoltaic and wind power in six developing countries. Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - sub critical hard coal",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "",
          40, "years", self.energy_adoption_mix['Coal']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing  the  costs  of  photovoltaic and wind power in six developing countries. Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - light fuel oil based generation",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "",
          25, "years", self.energy_adoption_mix['Oil']],
        ["Schmidt T. S., R. Born, and M. Schneider (2012). Assessing  the  costs  of  photovoltaic and wind power in six developing countries. Nature Climate Change 2, 548 – 553.  doi:  10.1038 / nclimate1490. - light fuel oil based generation",
          "http://www.nature.com/nclimate/journal/v2/n7/full/nclimate1490.html?foxtrotcallback=true",
          "World", "", "1  - Peer Reviewed", "2012", "",
          30, "years", self.energy_adoption_mix['Oil']],
      ], columns=vma.columns), low_sd=1.0, high_sd=1.0, use_weight=True)
    (self.conv_lifetime_years, _, _) = self.conv_lifetime_years_vma.avg_high_low()

    # The raw data input for Average Annual Use - Conventional is a capacity factor
    # value that is converted to average annual use (TWh/TW/) by multiplying capacity
    # factor by total hours/year (8760). A weight is then applied in order to create
    # a weighted average value for all conventional sources that will be replaced by
    # this solution. The weight is the percentage share, for the given technology, of
    # total global generation. These figures on historical generation were collected
    # from The World Bank Data in The Shift Project Data Portal
    # (http://www.tsp-data-portal.org/Breakdown-of-Electricity-Generation-by-Energy-Source#tspQvChart).
    self.conv_avg_annual_use_vma = vma.AvgHighLow(pd.DataFrame([
        # 'Variable Meta-analysis'!C246:X268, VMA #6
        ["EIA 2016, Electric Power Monthly, Coal (2013)  (Table 6.7.A)",
          "http://www.eia.gov/electricity/monthly/epm_table_grapher.cfm?t=epmt_6_07_a",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "59.7%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["EIA 2016, Electric Power Monthly, Coal (2014)  (Table 6.7.A) ",
          "http://www.eia.gov/electricity/monthly/epm_table_grapher.cfm?t=epmt_6_07_a",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "61.0%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["EIA 2016, Electric Power Monthly, Coal (2015)  (Table 6.7.A) ",
          "http://www.eia.gov/electricity/monthly/epm_table_grapher.cfm?t=epmt_6_07_a",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "54.6%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["EIA 2016, Electric Power Monthly, Natural Gas CCGT (2013)  (Table 6.7.A) ",
          "http://www.eia.gov/electricity/monthly/epm_table_grapher.cfm?t=epmt_6_07_a",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "48.2%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["EIA 2016, Electric Power Monthly, Natural Gas CCGT (2013)  (Table 6.7.A) ",
          "http://www.eia.gov/electricity/monthly/epm_table_grapher.cfm?t=epmt_6_07_a",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "48.3%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["EIA 2016, Electric Power Monthly, Natural Gas CCGT (2013)  (Table 6.7.A) ",
          "http://www.eia.gov/electricity/monthly/epm_table_grapher.cfm?t=epmt_6_07_a",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "56.3%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["IEA ETP 2016, Natural Gas (in 2013)  (Ch. 2 Figure 2.14)",
          "http://www.iea.org/etp/etp2016/secure/",
          "OECD90", "Australia", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "35.41%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["IEA ETP 2016, Natural Gas (in 2013)  (Ch. 2 Figure 2.14)",
          "http://www.iea.org/etp/etp2016/secure/",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "31.087%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["IEA ETP 2016, Natural Gas (in 2013)  (Ch. 2 Figure 2.14)",
          "http://www.iea.org/etp/etp2016/secure/",
          "EU", "Portugal", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "17.84%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["IEA ETP 2016, Natural Gas (in 2013)  (Ch. 2 Figure 2.14)",
          "http://www.iea.org/etp/etp2016/secure/",
          "OECD90", "Japan", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "98.239%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["IEA ETP 2016, Natural Gas (in 2013)  (Ch. 2 Figure 2.14)",
          "http://www.iea.org/etp/etp2016/secure/",
          "EU", "United Kingom", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "31.054%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["IEA ETP 2016, Natural Gas (in 2013)  (Ch. 2 Figure 2.14)",
          "http://www.iea.org/etp/etp2016/secure/",
          "EU", "Italy", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "37.143%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["IEA ETP 2016, Coal (in 2013)", "http://www.iea.org/etp/etp2016/secure/",
          "World", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "59.017%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["IEA ETP 2016, Coal (in 2013)", "http://www.iea.org/etp/etp2016/secure/",
          "OECD90", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "61.913%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["IEA ETP 2016, Coal (in 2013)", "http://www.iea.org/etp/etp2016/secure/",
          "China", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "57.13%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["IEA ETP 2016, Coal (in 2013)", "http://www.iea.org/etp/etp2016/secure/",
          "EU", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "54.061%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["IEA ETP 2016, Coal (in 2013)", "http://www.iea.org/etp/etp2016/secure/",
          "India", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "63.665%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["IEA ETP 2016, Coal (in 2013)", "http://www.iea.org/etp/etp2016/secure/",
          "USA", "", "2 - Public Sector/ Multilateral Agency", "2016", "",
          "60.683%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, coal, low estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          "93.0%", "Capacity factor (%)", self.energy_adoption_mix['Coal']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, natural gas (Combined Cycle), low estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          "80.0%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, natural gas (Combined Cycle), high estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          "40.0%", "Capacity factor (%)", self.energy_adoption_mix['Natural gas']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, diesel reciprocating engine lhigh estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          "10.0%", "Capacity factor (%)", self.energy_adoption_mix['Oil']],
        ["Lazard's LCOE Analysis–Version 10.0, 2016, diesel reciprocating engine low estimate",
          "https://www.lazard.com/perspective/levelized-cost-of-energy-analysis-100/",
          "USA", "", "3 - For Profit", "2016", "",
          "95.0%", "Capacity factor (%)", self.energy_adoption_mix['Oil']],
      ], columns=vma.columns), low_sd=1.0, high_sd=1.0, use_weight=True)
    (self.conv_avg_annual_use, _, _) = self.conv_avg_annual_use_vma.avg_high_low()
