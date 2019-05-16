""" Scratch file for running solutions in debug mode on Pycharm """

import pandas as pd
from model.aez import LAND_CSV_PATH, AEZ
from model.tla import tla_per_region
# from solution.solarpvutil import SolarPVUtil
# from solution.landfillmethane import LandfillMethane
from solution.silvopasture import Silvopasture
# from solution.bottomtrawling import LimitingBottomTrawling
from solution.forestprotection import ForestProtection
from solution.bamboo import Bamboo
from solution.tropicalforests import TropicalForests, scenarios
from solution.irrigationefficiency import IrrigationEfficiency

# soln = LimitingBottomTrawling()
# soln = ForestProtection()
# soln = Bamboo()
soln = IrrigationEfficiency()

ca = soln.pds_ca.adoption_data_per_region()
tla = soln.tla_per_region

res = (tla - ca).fillna(0)
# res = ca
# print(ca)
# res = res[res > 0].any().any()

print(res)

# print(ca)


# ae = AEZ(soln.name, ignore_allocation=False)
# print(ae.get_land_distribution())