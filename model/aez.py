"""
AEZ Data module.
Mostly reproduces the corresponding xls sheet, with a few simplifications:
- All breakdowns by year have been removed as the TLA is assumed fixed for all years on all solutions.
- 'Solution land data' table has not been replicated as it has no function in the model.

Land areas are pulled from CSVs in the 'land/world' directory, and land allocations from the 'land/allocation'
directory. These in turn are generated from their corresponding spreadsheets in the 'land' directory. These
values are fixed across all solutions but if they do need updating the xls sheets can be changed and the CSVs
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
        self.thermal_moisture_regimes = ['Tropical-Humid', 'Temperate/Boreal-Humid', 'Tropical-Semi-Arid',
                                         'Temperate/Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']
        self.regions = ['OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America',
                        'Global', 'China', 'India', 'EU', 'USA']
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
        # TODO: drawdown allocation yes/no toggle
        df = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_la_template.csv'), index_col=0)
        df = df.fillna(0)
        for tmr in self.thermal_moisture_regimes:
            tmr_path = LAND_CSV_PATH.joinpath('allocation', tmr.replace('/', '_'))
            for col in df:
                if col.startswith('AEZ29'):  # this zone is not included in land allocation
                    continue
                aez_path = tmr_path.joinpath(col +'.csv')
                la_df = pd.read_csv(aez_path, index_col=0)
                total_perc_allocated = la_df.loc[self.solution]['Total % allocated']
                if total_perc_allocated > 0:
                    df.at[tmr, col] = total_perc_allocated
        self.soln_land_alloc_df = df

    def _get_applicable_zones(self):
        """
        'AEZ Data'!A2:AD29
        Gathers list of AEZs applicable to solution from lookup matrix in 'aez' directory.
        """
        df = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_aez_matrix.csv'), index_col=0)
        self.applicable_zones = []
        for col, val in df.loc[self.solution].iteritems():
            if val == 'yes':
                self.applicable_zones.append(col)
            elif val != 'no':
                raise ValueError('cells in matrix should be "yes" or "no"')

    def _populate_world_land_allocation(self):
        """
        'AEZ Data'!D353:AG610
        Combines world land area data with Drawdown's land allocation values. Creates a dict of
        DataFrames sorted by Thermal Moisture Region.
        """
        self.world_land_alloc_dict = {}
        for tmr in self.thermal_moisture_regimes:
            df = pd.read_csv(LAND_CSV_PATH.joinpath('world', tmr.replace('/', '_') + '.csv'), index_col=0).drop('Total Area (km2)', 1)
            self.world_land_alloc_dict[tmr] = df.mul(self.soln_land_alloc_df.loc[tmr], axis=1) / 10000

    def _populate_solution_land_distribution(self):
        """
        'AEZ Data'!A47:H58
        Calculates total land distribution for solution by region (currently fixed for all years).
        """
        cols = self.thermal_moisture_regimes
        soln_df = pd.DataFrame(columns=cols, index=self.regions).fillna(0.)
        for reg in self.regions:
            for tmr, df in self.world_land_alloc_dict.items():
                if reg == 'Global':  # we will sum these later
                    soln_df.at[reg, tmr] = sum(soln_df[tmr].values[:5])
                else:
                    total_area = 0
                    for col in df.columns:
                        if col in self.applicable_zones:
                            total_area += df.loc[reg, col]
                    soln_df.at[reg, tmr] = total_area

        soln_df['All'] = soln_df.sum(axis=1)
        self.soln_land_dist_df = soln_df


if __name__ == '__main__':
    pass
