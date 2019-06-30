"""
TLA Data module.
Note: in the spreadsheet most of this module is a relic of the TAM module in the RRS model.
All the statistical analysis is unused as TLA remains constant and has already been allocated by
Drawdown. The only real function of the TLA tab is to provide a place to input custom TLA data, which
can be used instead of Drawdown's allocations. Thus, this class is named CustomTLA.
"""

from functools import lru_cache
import pandas as pd
import warnings
from model.dd import REGIONS


def tla_per_region(land_dist, custom_world_values=None):
    """
    A utility function to convert the land distribution output from AEZ Data into a dataframe broken
    out by region and years. Having the data in this format is not useful for the researcher but does
    allow compatibility with functions in other modules that take TAM dataframes as input for RRS
    solutions.
    Also note that while regional TLA has been included, it will not be tested as the Excel
    implementation has some issues with regional data. Information on issues can be found here:
    https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit?usp=sharing
    Args:
        land_dist: output of get_land_distribution() from aez.AEZ
        custom_world_values: df of custom values to be substituted into the 'World' column. Intended
            to be the output of CustomTLA.get_world_values().
    Returns:
        df: DataFrame for use with UnitAdoption
    """
    regions = REGIONS
    index = pd.Index(data=list(range(2014, 2061)), name='Year')
    df = pd.DataFrame(index=index)
    for region in regions:
        col = region
        if region == 'World':
            if custom_world_values is not None:
                df[region] = custom_world_values.loc[2014:, :]
                continue
            else:
                col = 'Global'
        df[region] = land_dist.at[col, 'All']
    return df


class CustomTLA:
    def __init__(self, filename):
        """
        Class for Custom TLA data
        Args:
            filename: path to 'custom_tla_data.csv' file
        """
        self.df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True, skip_blank_lines=True)

    def _avg_high_low(self):
        # This is not yet implemented as the only solution that uses Custom TLA so far (Tropical Forests)
        # uses only one source. The implementation of Custom TLA is likely to change as the python model
        # moves away from Excel due to the issue reported here (see 'Custom TLA Regional Data (LAND)'):
        # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#
        # Thus, we will only implement the statistical calcs if a solution calls for it
        return self.df

    @lru_cache()
    def get_world_values(self):
        return self._avg_high_low()
