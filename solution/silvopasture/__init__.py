"""
Silvopasture solution model (generated manually).
Excel filename: Silvopasture_L-Use_v1.1a_3Aug18.xlsm
"""

import pathlib
import numpy as np
import pandas as pd
from model import adoptiondata, advanced_controls, ch4calcs, co2calcs, emissionsfactors, firstcost, helpertables, \
    operatingcost, unitadoption, vma, tla, aez


scenarios = {  # just 1 for now
    'PDS-45p2050-Plausible-PDScustom-low-BookVersion1': advanced_controls.AdvancedControls(
        report_start_year=2020, report_end_year=2050,
    )}


class Silvopasture:
    name = 'Silvopasture'

    def __init__(self, scenario=None):
        datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))
        thisdir = pathlib.Path(__file__).parents[0]
        if scenario is None:
            scenario = 'PDS-45p2050-Plausible-PDScustom-low-BookVersion1'
        self.scenario = scenario
        self.ac = scenarios[scenario]

        # TLA
        self.ae = aez.AEZ(solution_name=self.name)

        # Current adoption data comes from VMA
        self.current_adoption_vma = vma.VMA(thisdir.joinpath('vma_data', 'Current Adoption.csv'))
        adoption = [self.current_adoption_vma.avg_high_low()[0]] + [0] * 9
        ht_ref_datapoints = pd.DataFrame([[2014] + adoption, [2050] + adoption], columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)','Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA']).set_index('Year')

        print(ht_ref_datapoints)
        # self.ht = helpertables.HelperTables()


if __name__ == '__main__':
    sp = Silvopasture()
