""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture
from solution.tropicalforests import TropicalForests, scenarios
from solution.forestprotection import ForestProtection

# scen = 'PDS-58p2050-Plausible-PDScustom-avg-BookVersion1'
# scen = 'PDS-58p2050-Plausible-PDScustomadoption-avg'
# soln = LandfillMethane('PDS-0p2050-Plausible Book (Ed. 1)')
# soln = TropicalForests(scenario=scen)

soln = ForestProtection()
# df = soln.ua.cumulative_reduction_in_total_degraded_land()

# print(soln.ua.annual_reduction_in_total_degraded_land())
print(soln.c2.co2_sequestered_global())
print(soln.c2.co2eq_mmt_reduced())


