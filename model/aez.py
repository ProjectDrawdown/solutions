"""Project Drawdown Land Utilities for Solutions.
There are three kinds of land divisions recognized within Project Drawdown:

* Regions:  these are the geo-political regions such as OECD90 and Latin America
* Thermal-Moisture Regimes, aka TMR: designations such as Boreal-Humid, etc.
* AEZs: this is a custom PD analysis of land areas combining land type, soil quality and slope steepness
 
Geographical analysis to create a cross-correlation between these three dimensions has been done,
and the original work is available at [https://github.com/ProjectDrawdown/spatial-aez].

Land-type solutions are usually only applicable within certain TMRs.  Within a given TMR, multiple
land solutions might compete for the same land.  PD has established a priority between multiple solutions
within AEZ types, and from that prioritization, determined a maximum available land allocation for each
solution within each political region/TMR area.  This is known as the "Total Land Allocation" or TLA,
and it works analagously to the "Total Available Market" in other solutions.

The TLA is established by the integration process in `integrations\aez_land_integration.py`.  The integration
process is run periodically to create updated TLAs which are stored in the `data` directory.
Individuals may run the integration process themselves to replicate that work, or experiment with alternatives.

Currently PD models land types as unchanging over time.  Future research may include forecasts of land
changes over time, e.g. due to climate change modeling.

This module contains the classes for solution-specific land allocations.
See the module `world_land` for global land data.
"""
import pathlib
import re

import numpy as np
import pandas as pd
from model import dd
from model.metaclass_cache import MetaclassCache

from model.data_handler import DataHandler
from model.decorators import data_func

LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land')


class AEZ(DataHandler, object, metaclass=MetaclassCache):
    """The AEZ object holds various land-based information applicable to a solution, including the allocated TLA"""

    world_land_alloc_dict: dict[str, pd.DataFrame] = None
    """The most granular version of land allocation.  A dictionary mapping TMR names to
    Dataframes, which themselves are indexed by region and have AEZ zones as columns,
    and allocations for this solution as values.
    """
    # 'AEZ Data'!D353:AG610
   
    soln_land_dist_df: pd.DataFrame = None
    """Land allocation broken down by TMR and AEZ.
    """
    # 'AEZ Data'!A47:H58 in Cohort 2018
    # 'AEZ Data'!A53:H64 in Cohort 2019
    # 'AEZ Data'!A53:J64 in the 3/2020 update which split Temperate from Boreal to make 8 TMRs

    soln_land_alloc_df: pd.DataFrame = None
    """Land allocation broken down by region and TMR.  This is the result returned by `get_land_distribution` and
    commonly referred to as the TLA.
    """
    # 'AEZ Data'!A63:AD70   

    applicable_zones: list[str] = None
    """The AEZ zones in which this solution can be applied.  (Hard-coded list)
    """
    # 'AEZ Data'!A2:AD29

    def __init__(self, solution_name, cohort=2018, regimes=dd.THERMAL_MOISTURE_REGIMES, max_tla=False):
            # TODO: check if these are the right defaults?  We need the Excel tests to pass, which would
            # need the data at that time, but in normal cases we also want the most "up to date" data possible.
        """
        Args:
            solution_name: full name of the solution (as returned by scenario.name)
            cohort: which land allocation series to use, defaults to most recent
            regimes: list of string names of thermal moisture regimes to use, defaults to standard
            max_tla: If true, the maximum suitable land available is returned, instead of the allocated land
        """
        self.solution_name = solution_name
        self.cohort = cohort
        self.regimes = regimes

        # AEZ data has a slightly different format for regions than the rest of the model. This
        # is in line with the xls version but should be changed later to keep regions consistent
        self.regions = dd.MAIN_REGIONS + ['Global'] + dd.SPECIAL_COUNTRIES

        self.ignore_allocation = max_tla
        self._populate_solution_land_allocation()
        self._get_applicable_zones()
        self._populate_world_land_allocation()
        self._populate_solution_land_distribution()

    @data_func
    def get_land_distribution(self):
        """Returns relevant land data for Unit Adoption module"""
        return self.soln_land_dist_df

    def _to_filename(self, name):
        """Removes special characters and separates words with single underscores"""
        return re.sub(' +', '_', re.sub('[^a-zA-Z0-9' '\n]', ' ', name)).strip('_')

    def _populate_solution_land_allocation(self):
        """Calculates `self.soln_land_alloc_df` from values in the 'allocation' directory."""
        df = pd.DataFrame(np.nan, columns=dd.AEZS, index=self.regimes)
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
        """Calculates `self.applicable_zones` from the lookup matrix in 'aez' directory.
           Note: DD land allocation already takes applicability into consideration, so
           applicable_zones will be redundant in solutions which use DD allocation.
        """
        row = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_aez_matrix.csv'),
                index_col=0).loc[self.solution_name]
        self.applicable_zones = row[row].index.tolist()


    def _populate_world_land_allocation(self):
        """calculates `self.world_land_alloc_dict`."""
        self.world_land_alloc_dict = {}
        subdir = '2020' if len(self.regimes) == 8 else '2018'
        for tmr in self.regimes:
            df = pd.read_csv(LAND_CSV_PATH.joinpath('world', subdir,
                    self._to_filename(tmr) + '.csv'), index_col=0).drop('Total Area (km2)', 1)
            # apply fixed world fraction to each region
            self.world_land_alloc_dict[tmr] = df.mul(self.soln_land_alloc_df.loc[tmr],
                    axis=1) / 10000


    def _populate_solution_land_distribution(self):
        """Calculates `self.soln_land_dist_df`"""
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
