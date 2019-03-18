""" Scratch file for running solutions in debug mode on Pycharm """

from solution.solarpvutil import SolarPVUtil
from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture

# soln = LandfillMethane('PDS-0p2050-Plausible Book (Ed. 1)')
soln = Silvopasture()
# print(soln.ua.soln_pds_net_grid_electricity_units_used())
print(soln.c2.conv_ref_grid_CO2_per_KWh)