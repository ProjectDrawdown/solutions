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
print(yield_df)
# create a list of valid scenario objects
# -- make csvs from excel model
# -- each named scenario will: 
# ---- import named scenario's data from csv
# ---- load data into data frame
# ---- each object instantiates AdvancedControls


# Note from actual implementation: 
# > wanted to do 'PDS-5p2050-PDS custom 2020-Avg of All' but the year-by-year table was empty, skipped

scenarios = {'PDS-4p2050- Plausible PDS custom- Avg of All': advanced_controls.AdvancedControls()}






# create a Scenario class for this Solution
# -- write functions which translate each table in the excel model
# ---- objects/ data types MOST LIKELY correspond to existing data types in the imports