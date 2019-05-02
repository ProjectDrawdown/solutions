""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
# from solution.solarpvutil import SolarPVUtil
# from solution.landfillmethane import LandfillMethane
# from solution.silvopasture import Silvopasture
from solution.bottomtrawling import LimitingBottomTrawling

soln = LimitingBottomTrawling()

# print(soln.ua.net_annual_land_units_adopted())
print(soln.c2.co2eq_mmt_reduced())