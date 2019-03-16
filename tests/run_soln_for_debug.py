""" Scratch file for running solutions in debug mode on Pycharm """

from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture

# soln = LandfillMethane('PDS-0p2050-Plausible Book (Ed. 1)')
soln = Silvopasture()
print(soln.tl)