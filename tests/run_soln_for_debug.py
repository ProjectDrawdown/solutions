""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
# from solution.solarpvutil import SolarPVUtil
# from solution.landfillmethane import LandfillMethane
# from solution.silvopasture import Silvopasture
from solution.tropicaltreestaples import TropicalTreeStaples

soln = TropicalTreeStaples()
print(soln.ae.get_land_distribution())
