"""
Silvopasture solution model (generated manually).
Excel filename: Silvopasture_L-Use_v1.1a_3Aug18.xlsm
"""

import pathlib
import numpy as np
import pandas as pd
from os import listdir
from model import adoptiondata, advanced_controls, ch4calcs, co2calcs, emissionsfactors, firstcost, helpertables, \
    operatingcost, unitadoption, vma, tla, aez, customadoption


scenarios = {  # just 1 for now
    'PDS-45p2050-Plausible-PDScustom-low-BookVersion1': advanced_controls.AdvancedControls(
        report_start_year=2020, report_end_year=2050,
        soln_pds_adoption_basis='Fully Customized PDS',
        pds_adoption_use_ref_years=[2015, 2016]
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

        # This solution has Custom PDS data
        ca_dir = thisdir.joinpath('ca_pds_data')
        source_filenames = [f for f in listdir(ca_dir) if f.endswith('.csv')]
        ca_data_sources = []
        for f in source_filenames:
            include = True
            if f == 'High growth, linear trend.csv':
                include = False
            ca_data_sources.append({'name': f, 'filename': f, 'include': include})
        self.ca = customadoption.CustomAdoption(
            data_sources=ca_data_sources,
            soln_adoption_custom_name='Low of All Custom Scenarios',
            filepath=ca_dir)

        # Current adoption data comes from VMA
        self.current_adoption_vma = vma.VMA(thisdir.joinpath('vma_data', 'Current Adoption.csv'))
        adoption = [self.current_adoption_vma.avg_high_low()[0]] + [0] * 9
        ht_ref_datapoints = pd.DataFrame([[2014] + adoption, [2050] + adoption],
                                         columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                                                  'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                                                  'USA']).set_index('Year')
        ht_pds_datapoints = pd.DataFrame([[2014] + adoption, [2050] + [0] * 10],
                                         columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                                                  'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                                                  'USA']).set_index('Year')
        self.ht = helpertables.HelperTables(
            ac=self.ac,
            adoption_data_per_region=self.ca.adoption_data_per_region(),
            ref_datapoints=ht_ref_datapoints,
            pds_datapoints=ht_pds_datapoints
        )

if __name__ == '__main__':
    sp = Silvopasture()
