""" Scratch file for running solutions in debug mode on Pycharm """

from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane

soln = LandfillMethane('PDS-0p2050-Plausible Book (Ed. 1)')
print(soln.fc.soln_pds_install_cost_per_iunit())