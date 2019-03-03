"""
TLA Data module.
Note: in the spreadsheet most of this module is a relic of the TAM module in the RRS model.
All the statistical analysis is unused as TLA remains constant and has already been allocated by
Drawdown. The only real function of the TLA tab is to provide a place to input custom TLA data, which
can be used instead of Drawdown's allocations. Thus, this class is named CustomTLA.
"""

from functools import lru_cache
import pandas as pd

def tla_per_region(land_dist):
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
    Returns:
        df: DataFrame for use with UnitAdoption
    """
    regions = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA']
    index = pd.Index(data=list(range(2014, 2061)), name='Year')
    df = pd.DataFrame(index=index)
    for region in regions:
        col = region
        if region == 'World':
            col = 'Global'
        # if region == 'Middle East and Africa':
        #     col = 'Middle East & Africa'
        df[region] = land_dist.at[col, 'All']
    return df


class CustomTLA:

    def __init__(self, tla_data_source):
        """
        Converts Custom TLA data for years 2012 - 2060 into a df.
        tla_data_source is a dict:
            {'Source Name': 'Source Filename'}
        May later be expanded to a dict of multiple sources.
        """
        self.tla_data_source = tla_data_source
        self._populate_tla_data()

    def _populate_tla_data(self):
        """Read data files in."""
        self.regions = {
            'global': pd.DataFrame(),
            'oecd90': pd.DataFrame(),
            'eastern_europe': pd.DataFrame(),
            'asia_sans_japan': pd.DataFrame(),
            'middle_east_and_africa': pd.DataFrame(),
            'latin america': pd.DataFrame(),
            'china': pd.DataFrame(),
            'india': pd.DataFrame(),
            'eu': pd.DataFrame(),
            'usa': pd.DataFrame()
        }

        for (name, filename) in self.tla_data_source.items():   # leave this in in case we want multiple sources later
            df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
                             skip_blank_lines=True, comment='#')

            self.regions['global'].loc[:, name] = df.loc[:, 'World']
            self.regions['oecd90'].loc[:, name] = df.loc[:, 'OECD90']
            self.regions['eastern_europe'].loc[:, name] = df.loc[:, 'Eastern Europe']
            self.regions['asia_sans_japan'].loc[:, name] = df.loc[:, 'Asia (Sans Japan)']
            self.regions['middle_east_and_africa'].loc[:, name] = df.loc[:, 'Middle East and Africa']
            self.regions['latin america'].loc[:, name] = df.loc[:, 'Latin America']
            self.regions['china'].loc[:, name] = df.loc[:, 'China']
            self.regions['india'].loc[:, name] = df.loc[:, 'India']
            self.regions['eu'].loc[:, name] = df.loc[:, 'EU']
            self.regions['usa'].loc[:, name] = df.loc[:, 'USA']

        for (region, region_df) in self.regions.items():
            region_df.name = 'source_data_{}'.format(region)

            # copy the source column to use as final TLA, so we have a TLA column for unit adoption to locate
            # later this column could be a statistical combination of multiple sources
            region_df.loc[:, 'TLA'] = region_df.iloc[:, 0]

    @lru_cache()
    def tla_data_global(self):
        """ 'TLA Data'!A644:M693 """
        return self.regions['global']


if __name__ == '__main__':
    pass

