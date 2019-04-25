""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
# from solution.solarpvutil import SolarPVUtil
# from solution.landfillmethane import LandfillMethane
# from solution.silvopasture import Silvopasture
from solution.afforestation import Afforestation

soln = Afforestation()

# print(soln.tla_per_region)
print(soln.c2.co2eq_mmt_reduced())
