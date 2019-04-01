""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture
from solution.tropicalforests import TropicalForests, scenarios

# scen = 'PDS-58p2050-Plausible-PDScustom-avg-BookVersion1'
scen = 'PDS-58p2050-Plausible-PDScustomadoption-avg'
# soln = LandfillMethane('PDS-0p2050-Plausible Book (Ed. 1)')
# soln = TropicalForests(scenario=scen)

# print('avg: {}'.format(soln.pds_ca.adoption_data_per_region().at[2015, 'World']))
# print(soln.pds_ca.scenarios.keys())
# print(scenarios.keys())
