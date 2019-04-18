""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture
from solution.peatlands import Peatlands

soln = Peatlands()

# print(soln.ua.direct_ch4_co2_emissions_saved_land())
print(soln.c2.co2eq_mmt_reduced())
# print(soln.oc.soln_pds_annual_breakout())

