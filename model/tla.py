"""
TLA Data module.
Note: in the spreadsheet most of this module is a relic of the TAM module in the RRS model.
All the statistical analysis is unused as TLA remains constant and has already been allocated by
DD. The only real function of the TLA tab is to provide a place to input custom TLA data, which
can be used instead of DD's allocations. Thus, this class is named CustomTLA.
"""

from functools import lru_cache
import os.path
import pathlib

from model import interpolation
import pandas as pd


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
            region_df.loc[:, 'TLA'] = region_df.ix[:, 0]

    @lru_cache()
    def tla_data_global(self):
        """ 'TLA Data'!A644:M693 """
        return self.regions['global']


if __name__ == '__main__':
    datadir = pathlib.Path(__file__).parents[1]

    g_tla_ref_data_source = {
        'Based on- WRI 2016': str(
            datadir.joinpath('solution', 'tropicalforests', 'tla_based_on_WRI_2016_widescale_reforestation.csv')),
    }
    tl = CustomTLA(g_tla_ref_data_source)
    print(tl.tla_data_global())

