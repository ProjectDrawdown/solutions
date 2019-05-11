""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
# from solution.solarpvutil import SolarPVUtil
# from solution.landfillmethane import LandfillMethane
# from solution.silvopasture import Silvopasture
from solution.bottomtrawling import LimitingBottomTrawling
from solution.forestprotection import ForestProtection

soln = LimitingBottomTrawling()
# soln = ForestProtection()
print(soln.de.get_ocean_distribution())
# print(soln.ae.get_land_distribution())
print(soln.c2.co2_sequestered_global())
