""" Scratch file for running solutions in debug mode on Pycharm """

from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane

soln = LandfillMethane('PDS-0p2050-Plausible Book (Ed. 1)')
print(soln.oc.soln_vs_conv_single_iunit_cashflow())