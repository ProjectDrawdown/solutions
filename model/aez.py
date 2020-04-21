"""
AEZ Data module.
Mostly reproduces the corresponding xls sheet, with a few simplifications:
- All breakdowns by year have been removed as the TLA is assumed fixed for all years on all solutions.
- 'Solution land data' table has not been replicated as it has no function in the model.

Areas are pulled from CSVs in the 'land/world' directory, and allocations from the 'land/allocation'
directory. These in turn are generated from their corresponding spreadsheets in the 'land' directory. These
values are fixed across all solutions but if they do need updating the xls sheets can be changed and the CSVs
can be updated by running the relevant script in the 'tools' directory.
"""

import pathlib
import re

import pandas as pd
from model import dd
from model.metaclass_cache import MetaclassCache

LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land')


class AEZ(object, metaclass=MetaclassCache):
    """AEZ Data module.
       Args:
         solution_name: <soln file>.name
         ignore_allocation: optionally turn off land allocation to use max tla values
         cohort: whether to use 2018 or 2019 land allocations.
         regimes: list of string names of thermal moisture regimes
    """

    def __init__(self, solution_name, ignore_allocation=False, cohort=2018,
            regimes=dd.THERMAL_MOISTURE_REGIMES):
        self.solution_name = solution_name
        self.cohort = cohort
        self.regimes = regimes

        # AEZ data has a slightly different format for regions than the rest of the model. This
        # is in line with the xls version but should be changed later to keep regions consistent
        self.regions = dd.MAIN_REGIONS + ['Global'] + dd.SPECIAL_COUNTRIES

        self.ignore_allocation = ignore_allocation
        self._populate_solution_land_allocation()
        self._get_applicable_zones()
        self._populate_world_land_allocation()
        self._populate_solution_land_distribution()


    def get_land_distribution(self):
        """Returns relevant land data for Unit Adoption module"""
        return self.soln_land_dist_df


    def _to_filename(self, name):
        """Removes special characters and separates words with single underscores"""
        return re.sub(' +', '_', re.sub('[^a-zA-Z0-9' '\n]', ' ', name)).strip('_')


    def _populate_solution_land_allocation(self):
        """Calculates solution specific land allocation using values from 'allocation' directory.

           'AEZ Data'!A63:AD70
        """
        df = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_la_template.csv'), index_col=0)
        if self.ignore_allocation:
            self.soln_land_alloc_df = df.fillna(1)
            return
        else:
            df = df.fillna(0)

        for tmr in self.regimes:
            tmr_path = LAND_CSV_PATH.joinpath(f'allocation{self.cohort}', self._to_filename(tmr))
            for col in df:
                if col.startswith('AEZ29'):  # this zone is not included in land allocation
                    continue
                aez_path = tmr_path.joinpath(self._to_filename(col) + '.csv')
                la_df = pd.read_csv(aez_path, index_col=0)
                total_perc_allocated = la_df.loc[self.solution_name]['Total % allocated']
                if total_perc_allocated > 0:
                    df.at[tmr, col] = total_perc_allocated
        else:
            self.soln_land_alloc_df = df


    def _get_applicable_zones(self):
        """Gathers list of AEZs applicable to solution from lookup matrix in 'aez' directory.

           Note: DD land allocation already takes applicability into consideration, so
           applicable_zones will be redundant in solutions which use DD allocation.
           'AEZ Data'!A2:AD29
        """
        row = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_aez_matrix.csv'),
                index_col=0).loc[self.solution_name]
        self.applicable_zones = row[row].index.tolist()


    def _populate_world_land_allocation(self):
        """Combines world land area data with Drawdown's land allocation values.

           Creates a dict of DataFrames sorted by Thermal Moisture Region.
           'AEZ Data'!D353:AG610
        """
        self.world_land_alloc_dict = {}
        subdir = '2020' if len(self.regimes) == 8 else '2018'
        for tmr in self.regimes:
            df = pd.read_csv(LAND_CSV_PATH.joinpath('world', subdir,
                    self._to_filename(tmr) + '.csv'), index_col=0).drop('Total Area (km2)', 1)
            # apply fixed world fraction to each region
            self.world_land_alloc_dict[tmr] = df.mul(self.soln_land_alloc_df.loc[tmr],
                    axis=1) / 10000


    def _populate_solution_land_distribution(self):
        """Calculates total land distribution for solution by region, currently fixed for all years.

           'AEZ Data'!A47:H58 in Cohort 2018
           'AEZ Data'!A53:H64 in Cohort 2019
           'AEZ Data'!A53:J64 in the 3/2020 update which split Temperate from Boreal to make 8 TMRs
        """
        cols = self.regimes
        soln_df = pd.DataFrame(columns=cols, index=self.regions).fillna(0.)
        for reg in self.regions:
            for tmr, df in self.world_land_alloc_dict.items():
                if reg == 'Global':
                    soln_df.at[reg, tmr] = soln_df.loc[dd.MAIN_REGIONS, tmr].sum()
                else:
                    soln_df.at[reg, tmr] = df.loc[reg, self.applicable_zones].sum()

        soln_df['All'] = soln_df.sum(axis=1)
        soln_df.name = 'land_distribution'
        soln_df.index.name = 'Region'
        self.soln_land_dist_df = soln_df
