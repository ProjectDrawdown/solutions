"""
DEZ Data module. Similar to aez.py, kept separate here in to imitate xls model.
Mostly reproduces the corresponding xls sheet, with a few simplifications:
- All breakdowns by year have been removed as the TOA is assumed fixed for all years on all solutions.
- 'Solution ocean data' table has not been replicated as it has no function in the model.

Areas are pulled from CSVs in the 'ocean/world' directory, and allocations from the 'ocean/allocation'
directory. These in turn are generated from their corresponding spreadsheets in the 'ocean' directory. These
values are fixed across all solutions but if they do need updating the xls sheets can be changed and the CSVs
can be updated by running the relevant script in the 'tools' directory.
"""

import pathlib
import re

import pandas as pd
from model import dd
from model.metaclass_cache import MetaclassCache

from model.data_handler import DataHandler
from model.decorators import data_func

OCEAN_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean')


class DEZ(DataHandler, object, metaclass=MetaclassCache):
    """ DEZ Data module """

    def __init__(self, solution_name):
        self.solution_name = solution_name
        self.regimes = dd.THERMAL_DYNAMICAL_REGIMES

        # AEZ data has a slightly different format for regions than the rest of the model.
        # This is in line with the xls version but should be changed later to keep regions consistent
        self.regions = dd.OCEAN_REGIONS[1:7] + ['Global'] + dd.OCEAN_REGIONS[7:]

        self._populate_solution_ocean_allocation()
        self._get_applicable_zones()
        self._populate_world_ocean_allocation()
        self._populate_solution_ocean_distribution()

    @data_func
    def get_ocean_distribution(self):
        """ Returns relevant ocean data for Unit Adoption module"""
        return self.soln_ocean_dist_df

    def _to_filename(self, name):
        """Removes special characters and separates words with single underscores"""
        return re.sub(' +', '_', re.sub('[^a-zA-Z0-9' '\n]', ' ', name)).strip('_')

    def _populate_solution_ocean_allocation(self):
        """
        'DEZ Data'!A63:AD70
        Calculates solution specific Drawdown ocean allocation using values from 'allocation' directory.
        """
        df = pd.read_csv(OCEAN_CSV_PATH.joinpath('dez', 'solution_oa_template.csv'), index_col=0)
        df = df.fillna(0)
        for tdr in self.regimes:
            tdr_path = OCEAN_CSV_PATH.joinpath('allocation', self._to_filename(tdr))
            for col in df:
                dez_path = tdr_path.joinpath(self._to_filename(col) + '.csv')
                oa_df = pd.read_csv(dez_path, index_col=0)
                total_perc_allocated = oa_df.loc[self.solution_name]['Total % allocated']
                if total_perc_allocated > 0:
                    df.at[tdr, col] = total_perc_allocated
        self.soln_ocean_alloc_df = df

    def _get_applicable_zones(self):
        """
        'DEZ Data'!A2:AD29
        Gathers list of DEZs applicable to solution from lookup matrix in 'dez' directory.

        NOTE: this matrix is in development and WILL change. Make sure to update accordingly.
        """
        row = pd.read_csv(OCEAN_CSV_PATH.joinpath('dez', 'solution_dez_matrix.csv'),
                index_col=0).loc[self.solution_name]
        self.applicable_zones = row[row].index.tolist()

    def _populate_world_ocean_allocation(self):
        """
        'DEZ Data'!D353:AG610
        Combines world ocean area data with Drawdown's ocean allocation values. Creates a dict of
        DataFrames sorted by Thermal Dynamical Regime.
        """
        self.world_ocean_alloc_dict = {}
        for tdr in self.regimes:
            df = pd.read_csv(OCEAN_CSV_PATH.joinpath('world', self._to_filename(tdr) + '.csv'),
                    index_col=0).drop('Total Area (Mha)', 1)
            self.world_ocean_alloc_dict[tdr] = df.mul(self.soln_ocean_alloc_df.loc[tdr], axis=1)

    def _populate_solution_ocean_distribution(self):
        """
        'DEZ Data'!A47:H58
        Calculates total ocean distribution for solution by region (currently fixed for all years).
        """
        cols = self.regimes
        soln_df = pd.DataFrame(columns=cols, index=self.regions).fillna(0.)
        for reg in self.regions:
            for tmr, df in self.world_ocean_alloc_dict.items():
                if reg == 'Global':
                    soln_df.at[reg, tmr] = sum(
                        soln_df[tmr].values[:6])  # sum from soln_df rather than read from df
                else:
                    soln_df.at[reg, tmr] = df.loc[reg, self.applicable_zones].sum()

        soln_df['All'] = soln_df.sum(axis=1)
        self.soln_ocean_dist_df = soln_df
