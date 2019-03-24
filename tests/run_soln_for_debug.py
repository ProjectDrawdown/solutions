""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture

# soln = LandfillMethane('PDS-0p2050-Plausible Book (Ed. 1)')
soln = Silvopasture(scenario='PDS-54p2050-Drawdown-PDScustom-high-basedonpasture-BookVersion1')
# print(soln.ua.soln_pds_net_grid_electricity_units_used())
# print(soln.ua.soln_net_annual_funits_adopted())
# print(soln.c2.co2eq_mmt_reduced())