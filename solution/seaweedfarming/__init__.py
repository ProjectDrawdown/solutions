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
# THISDIR = pathlib.Path(__file__).parents[0]


# create a list of valid scenario objects
# -- make csvs from excel model
# -- each named scenario will: 
# ---- import named scenario's data from csv
# ---- load data into data frame
# ---- each object instantiates AdvancedControls


# Note from actual implementation: 
# > wanted to do 'PDS-5p2050-PDS custom 2020-Avg of All' but the year-by-year table was empty, skipped
DEV_DEFAULT_SCENARIO_NAME = 'PDS-4p2050- Plausible PDS custom- Avg of All'

scenarios = {
    'PDS-4p2050- Plausible PDS custom- Avg of All': advanced_controls.AdvancedControls(

        # general
        solution_category=SOLUTION_CATEGORY.OCEAN,
        # vmas=VMAs,
        report_start_year=2019, report_end_year=2060, # TODO Started in 2019 because that's the first year that there is data
        # TODO idea: why not have them start at year 0 and count up, so that the plan cannot become outdated in this way? 'within 5 lyears, xyz effects"
         #Alyssa -- left off here Sat pm

        # adoption
        # soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,
        soln_pds_adoption_basis='Linear',
        # soln_pds_adoption_custom_name='Average of All Custom Scenarios',
        pds_adoption_final_percentage=[
            ('World', 1.0), ('OECD90', 1.0), ('Eastern Europe', 1.0), ('Asia (Sans Japan)', 1.0),
            ('Middle East and Africa', 1.0), ('Latin America', 1.0), ('ABNJ', 1.0),
            ('China', 1.0), ('India', 1.0), ('EU', 1.0), ('USA', 1.0)],

        # financial
        pds_2014_cost=0.0, ref_2014_cost=0.0,
        conv_2014_cost=0.0,
        soln_first_cost_efficiency_rate=0.0,
        conv_first_cost_efficiency_rate=0.0,
        npv_discount_rate=0.1,
        soln_expected_lifetime=30.0,
        conv_expected_lifetime=30.0,
        yield_from_conv_practice=0.0,
        yield_gain_from_conv_to_soln=0.0,

        soln_fixed_oper_cost_per_iunit=0.0,
        conv_fixed_oper_cost_per_iunit=0.0,

        # emissions
        soln_indirect_co2_per_iunit=0.0,
        conv_indirect_co2_per_unit=0.0,
        soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,

        tco2eq_reduced_per_land_unit=5.0,
        tco2eq_rplu_rate='One-time',

        emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
        emissions_use_co2eq=True,
        emissions_use_agg_co2eq=True,

        # sequestration
        seq_rate_global=0.,
        disturbance_rate=0.02,
    )
}




# create a Scenario class for this Solution
# -- write functions which translate each table in the excel model
# ---- objects/ data types MOST LIKELY correspond to existing data types in the imports