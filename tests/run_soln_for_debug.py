""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture
from solution.tropicaltreestaples import TropicalTreeStaples

soln = TropicalTreeStaples()
print(soln.ac.vmas['SOLUTION Operating Cost per Functional Unit per Annum'].df)
print(soln.ac.soln_fixed_oper_cost_per_iunit)
# print(soln.oc.soln_pds_annual_breakout())

