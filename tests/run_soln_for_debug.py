""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
# from solution.solarpvutil import SolarPVUtil
# from solution.landfillmethane import LandfillMethane
# from solution.silvopasture import Silvopasture
from solution.peatlands import Peatlands

soln = Peatlands()

# print(soln.ac.vmas['Growth Rate of Land Degradation'].df)
# print(soln.ac.vmas['Growth Rate of Land Degradation'].avg_high_low())
# print(soln.ua.soln_net_annual_funits_adopted())
# print(soln.ac.seq_rate_global)
print(soln.c4.avoided_direct_emissions_ch4_land())
# print(soln.c2.co2eq_ppm_calculator())

# print(soln.oc.soln_pds_annual_breakout())
