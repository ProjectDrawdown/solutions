"""
TOA Data Module. Similar to the python implementation of TLA.
Forecasting functionality has not been implemented as TOA currently stays constant for all years.
"""

import pandas as pd
from model.dd import OCEAN_REGIONS


def toa_per_region(ocean_dist):
    """
    A utility function to convert the ocean distribution output from DEZ Data into a dataframe broken
    out by region and years. Having the data in this format is not useful for the researcher but does
    allow compatibility with functions in other modules that take TAM dataframes as input for RRS
    solutions.
    Args:
        ocean_dist: output of get_land_distribution() from aez.AEZ
    Returns:
        df: DataFrame for use with UnitAdoption
    """
    regions = OCEAN_REGIONS
    index = pd.Index(data=list(range(2014, 2061)), name='Year')
    df = pd.DataFrame(index=index)
    for region in regions:
        col = region
        if region == 'World':
            col = 'Global'
        df[region] = ocean_dist.at[col, 'All']
    return df
