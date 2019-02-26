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
        pds_adoption_use_ref_years=[2015, 2016],
        expected_lifetime=30
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

        self.ua = unitadoption.UnitAdoption(
            ac=self.ac,
            datadir=datadir,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted())

        # print(self.ua.soln_pds_new_iunits_reqd())
        sp = [0, 0, 1.49643489480934, 3.42983761673287, 3.40777131208006, 3.3853509490275, 3.36260182010352, 3.3395514466838,
         3.31622945888586, 3.29266744308518, 3.26889875807274, 2.61251683499262, 3.24583933270031, 3.22374782069915,
         3.20156976815986, 3.17933454067742, 3.15707188573589, 3.13481173478948, 3.1125840024759, 3.09041838609068,
         3.06834416845413, 2.95854426200356, 3.02978268035292, 3.00834944629167, 2.98710624970022, 2.96607716645508,
         2.94528498898256, 2.92475112400388, 2.90449550819716, 2.88453654207888, 2.86489104204179, 2.57664981813053,
         2.85665924514041, 4.33489812403127, 6.25041698217706, 6.2107886876006, 6.28096212022842, 6.10645576424633,
         6.06670797541483, 6.02707271316069, 5.98758372231941, 5.94827534797025, 5.27674091268659, 5.89529695122053,
         5.8588229736597, 5.8226435345909]

        sp = np.array(sp)
        np.testing.assert_array_almost_equal(sp, self.ua.soln_pds_new_iunits_reqd()['World'].values)

if __name__ == '__main__':
    sp = Silvopasture()
