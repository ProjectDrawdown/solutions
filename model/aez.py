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

import pandas as pd
import pathlib
from model.dd import THERMAL_MOISTURE_REGIMES, REGIONS
from tools.util import to_filename

LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land')
pd.set_option('display.expand_frame_repr', False)


class AEZ:
    """
    AEZ Data module.
    Args:
        solution_name: <soln file>.name
        ignore_allocation: optionally turn off land allocation to use max tla values
    """

    def __init__(self, solution_name, ignore_allocation=False):
        self.solution_name = solution_name
        self.regimes = THERMAL_MOISTURE_REGIMES

        # AEZ data has a slightly different format for regions than the rest of the model.
        # This is in line with the xls version but should be changed later to keep regions consistent
        self.regions = REGIONS[1:6] + ['Global'] + REGIONS[6:]

        self.ignore_allocation = ignore_allocation
        self._populate_solution_land_allocation()
        self._get_applicable_zones()
        self._populate_world_land_allocation()
        self._populate_solution_land_distribution()

    def get_land_distribution(self):
        """ Returns relevant land data for Unit Adoption module"""
        return self.soln_land_dist_df

    def _populate_solution_land_allocation(self):
        """
        'AEZ Data'!A63:AD70
        Calculates solution specific Drawdown land allocation using values from 'allocation' directory.
        """
        df = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_la_template.csv'), index_col=0)
        if self.ignore_allocation:
            self.soln_land_alloc_df = df.fillna(1)
            return
        else:
            df = df.fillna(0)

        for tmr in self.regimes:
            tmr_path = LAND_CSV_PATH.joinpath('allocation', to_filename(tmr))
            for col in df:
                if col.startswith('AEZ29'):  # this zone is not included in land allocation
                    continue
                aez_path = tmr_path.joinpath(to_filename(col) + '.csv')
                la_df = pd.read_csv(aez_path, index_col=0)
                total_perc_allocated = la_df.loc[self.solution_name]['Total % allocated']
                if total_perc_allocated > 0:
                    df.at[tmr, col] = total_perc_allocated
        else:
            self.soln_land_alloc_df = df

    def _get_applicable_zones(self):
        """
        'AEZ Data'!A2:AD29
        Gathers list of AEZs applicable to solution from lookup matrix in 'aez' directory.

        Note: DD land allocation already takes applicability into consideration, so applicable_zones
        will be redundant in solutions which use DD allocation.
        """
        row = pd.read_csv(
            LAND_CSV_PATH.joinpath('aez', 'solution_aez_matrix.csv'), index_col=0).loc[self.solution_name]
        self.applicable_zones = row[row].index.tolist()

    def _populate_world_land_allocation(self):
        """
        'AEZ Data'!D353:AG610
        Combines world land area data with Drawdown's land allocation values. Creates a dict of
        DataFrames sorted by Thermal Moisture Region.
        """
        self.world_land_alloc_dict = {}
        for tmr in self.regimes:
            df = pd.read_csv(LAND_CSV_PATH.joinpath('world', to_filename(tmr) + '.csv'), index_col=0).drop(
                'Total Area (km2)', 1)
            self.world_land_alloc_dict[tmr] = df.mul(self.soln_land_alloc_df.loc[tmr], axis=1) / 10000

    def _populate_solution_land_distribution(self):
        """
        'AEZ Data'!A47:H58
        Calculates total land distribution for solution by region (currently fixed for all years).
        """
        cols = self.regimes
        soln_df = pd.DataFrame(columns=cols, index=self.regions).fillna(0.)
        for reg in self.regions:
            for tmr, df in self.world_land_alloc_dict.items():
                if reg == 'Global':
                    soln_df.at[reg, tmr] = sum(soln_df[tmr].values[:5])  # sum from soln_df rather than read from df
                else:
                    soln_df.at[reg, tmr] = df.loc[reg, self.applicable_zones].sum()

        soln_df['All'] = soln_df.sum(axis=1)
        self.soln_land_dist_df = soln_df

