# give it a descriptive name
'''
Model for the Ocean sector's Seaweed Farming solution  
'''

# import useful things -- see bottomtrawling/init for list
import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import dez
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
from model.dd import OCEAN_REGIONS

from model import toa
from solution import land

# The time will come for these when I start importing things. Which will probably be like five minutes
# DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))
THISDIR = pathlib.Path(__file__).parents[0]
YIELD_DATA_FILE = THISDIR.joinpath('OceanInputsDataFrame.csv')

yield_df = pd.read_csv(YIELD_DATA_FILE)
yield_series = yield_df['Conversion calculation**']
# print(yield_df)
carbon_content_of_algae_biomass_avg = 0.284687
farm_biomass_export_avg = 0.55
pct_longterm_sequestration_from_exported_carbon_in_farms_avg = 0.372239
# todo calculate these averages from raw data (see advanced controls row 208)

carbon_sequestration = (yield_df['Conversion calculation**'] / (1-farm_biomass_export_avg))*farm_biomass_export_avg*carbon_content_of_algae_biomass_avg*pct_longterm_sequestration_from_exported_carbon_in_farms_avg


print(type(carbon_sequestration))
print(carbon_sequestration)
print("Mean:")
print(np.mean(carbon_sequestration))
# create a list of valid scenario objects
# -- make csvs from excel model
# -- each named scenario will: 
# ---- import named scenario's data from csv
# ---- load data into data frame
# ---- each object instantiates AdvancedControls


# Note from actual implementation: 
# > wanted to do 'PDS-5p2050-PDS custom 2020-Avg of All' but the year-by-year table was empty, skipped

scenarios = {'PDS-4p2050- Plausible PDS custom- Avg of All': advanced_controls.AdvancedControls()}

"""
 Note that for seaweed farming we don't have CONVENTIONAL data sets, only SOLUTIONs.
"""
VMAs = {
    'Current Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data","Current_Adoption.csv"),
        use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'Sequestration Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rate.csv"),
        use_weight=False),
    'Carbon Content Dry Biomass': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Carbon_Content_Dry_Biomass.csv"),
        use_weight=False),
    'Wet Dry Conversion': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Wet_Dry_Conversion.csv"),
        use_weight=False),
    'Farm Biomass Export': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Farm_Biomass_Export.csv"),
        use_weight=False),
    'Long Term Sequestration Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Long_Term_Sequestration_Rate.csv"),
        use_weight=False),
    'Yield Dry Weight': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_Dry_Weight.csv"),
        use_weight=False)
}

# for vma in VMAs:
#   print(vma + "\n")

print(VMAs)





# create a Scenario class for this Solution
# -- write functions which translate each table in the excel model
# ---- objects/ data types MOST LIKELY correspond to existing data types in the imports