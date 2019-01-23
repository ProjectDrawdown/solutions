"""
AEZ Data module.
Mostly reproduces the corresponding xls sheet, with a few simplifications. All breakdowns by year have
been removed as the TLA is assumed fixed for all years on all solutions. Land areas are pulled from
csvs in the 'land/world' directory, and land allocations from the 'land/allocation' directory.
These in turn are generated from their corresponding spreadsheets in the 'land' directory. These values
are fixed across all solutions but if they do need updating the xls sheets can be changed and the CSVs
can be updated by running the relevant script in the 'tools' directory.
"""

import pandas as pd
import pathlib

LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land')
pd.set_option('display.expand_frame_repr', False)


class AEZ:
    """ AEZ Data module """
    def __init__(self, solution):
        self.solution = solution
        self.thermal_moisture_regimes = ['Tropical-Humid', 'Temperate_Boreal-Humid', 'Tropical-Semi-Arid',
                                    'Temperate_Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']
        self._populate_solution_la()
        self._get_applicable_zones()
        self._populate_world_la()

    def _populate_solution_la(self):
        # TODO: drawdown allocation toggle
        df = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_la_template.csv'), index_col=0)
        df = df.fillna(0)
        for tmr in df.index:
            tmr_path = LAND_CSV_PATH.joinpath('allocation', tmr.replace('/', '_'))
            for col in df:
                if col.startswith('AEZ29'):  # this zone is not included in land allocation
                    continue
                aez_path = tmr_path.joinpath(col +'.csv')
                la_df = pd.read_csv(aez_path, index_col=0)
                total_perc_allocated = la_df.loc[self.solution]['Total % allocated']
                if total_perc_allocated > 0:
                    df.at[tmr, col] = total_perc_allocated
        self.solution_la_df = df

    def _get_applicable_zones(self):
        df = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_aez_matrix.csv'), index_col=0)
        self.applicable_zones = []
        for col, val in df.loc[self.solution].iteritems():
            if val == 'yes':
                self.applicable_zones.append(col)
            elif val != 'no':
                raise ValueError('cells in matrix should be "yes" or "no"')

    def _populate_world_la(self):
        """
        'AEZ Data'!D353:AG610
        Combines world land area data with Drawdown's land allocation values. Creates a dict of
        DataFrames sorted by Thermal Moisture Region.
        """
        self.world_la_dict = {}
        for tmr in self.thermal_moisture_regimes:
            df = pd.read_csv(LAND_CSV_PATH.joinpath('world', tmr + '.csv'), index_col=0).drop('Total Area (km2)', 1)
            self.world_la_dict[tmr] = df.mul(self.solution_la_df.loc[tmr.replace('_', '/')], axis=1) / 10000


if __name__ == '__main__':
    aez = AEZ('Tropical Forest Restoration')
