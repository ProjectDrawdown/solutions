"""Total Land Area module."""

from functools import lru_cache
import os.path
import pathlib

from model import interpolation
import pandas as pd


class TLA:

    def __init__(self, tlaconfig, tla_ref_data_sources):
        """TLA module.

           Arguments
           tlaconfig: Pandas dataframe with columns:
              'source_until_2014', 'source_after_2014', 'trend', 'growth', 'low_sd_mult', 'high_sd_mult'
              and rows for each region:
              'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
              'Latin America', 'China', 'India', 'EU', 'USA'
            tla_ref_data_sources: a dict() of data source names.
            Used for TLA.
            For example:
            {
              'Source A name: 'filename A'
              'Source B name: 'filename B'
              ...
            }
              tam_pds_data_sources: as tam_ref_data_sources, for the PDS scenario.
        """
        self.tlaconfig = tlaconfig
        self.tla_ref_data_sources = tla_ref_data_sources
        self._populate_forecast_data()

    def _populate_forecast_data(self):
        """Read data files in self.tla_*_data_sources to populate forecast data."""
        self._forecast_data_global = pd.DataFrame()
        self._forecast_data_global.name = 'forecast_data_global'
        self._forecast_data_oecd90 = pd.DataFrame()
        self._forecast_data_oecd90.name = 'forecast_data_oecd90'
        self._forecast_data_eastern_europe = pd.DataFrame()
        self._forecast_data_eastern_europe.name = 'forecast_data_eastern_europe'
        self._forecast_data_asia_sans_japan = pd.DataFrame()
        self._forecast_data_asia_sans_japan.name = 'forecast_data_asia_sans_japan'
        self._forecast_data_middle_east_and_africa = pd.DataFrame()
        self._forecast_data_middle_east_and_africa.name = 'forecast_data_middle_east_and_africa'
        self._forecast_data_latin_america = pd.DataFrame()
        self._forecast_data_latin_america.name = 'forecast_data_latin_america'
        self._forecast_data_china = pd.DataFrame()
        self._forecast_data_china.name = 'forecast_data_china'
        self._forecast_data_india = pd.DataFrame()
        self._forecast_data_india.name = 'forecast_data_india'
        self._forecast_data_eu = pd.DataFrame()
        self._forecast_data_eu.name = 'forecast_data_eu'
        self._forecast_data_usa = pd.DataFrame()
        self._forecast_data_usa.name = 'forecast_data_usa'

        for (name, filename) in self.tla_ref_data_sources.items():
            df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
                             skip_blank_lines=True, comment='#')
            self._forecast_data_global.loc[:, name] = df.loc[:, 'World']
            self._forecast_data_oecd90.loc[:, name] = df.loc[:, 'OECD90']
            self._forecast_data_eastern_europe.loc[:, name] = df.loc[:, 'Eastern Europe']
            self._forecast_data_asia_sans_japan.loc[:, name] = df.loc[:, 'Asia (Sans Japan)']
            self._forecast_data_middle_east_and_africa.loc[:, name] = df.loc[:, 'Middle East and Africa']
            self._forecast_data_latin_america.loc[:, name] = df.loc[:, 'Latin America']
            self._forecast_data_china.loc[:, name] = df.loc[:, 'China']
            self._forecast_data_india.loc[:, name] = df.loc[:, 'India']
            self._forecast_data_eu.loc[:, name] = df.loc[:, 'EU']
            self._forecast_data_usa.loc[:, name] = df.loc[:, 'USA']

    @lru_cache()
    def forecast_data_global(self):
        """ 'TLA Data'!A644:M693 """
        return self._forecast_data_global


if __name__ == '__main__':
    tlaconfig_list = [
        ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
         'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
        ['source_until_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
         'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],

        # Not sure about this
        # ['source_after_2014', 'Baseline Cases',
        #   'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario', 'ALL SOURCES',
        #   'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
        #   'ALL SOURCES', 'ALL SOURCES'],

        # (placeholder)
        ['source_after_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
         'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],

        ['trend', '3rd Poly', '3rd Poly', 'Linear', 'Linear', 'Linear', 'Linear', 'Linear',
         'Linear', 'Linear', 'Linear', 'Linear'],
        ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
         'Medium', 'Medium', 'Medium'],
        ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
    g_tlaconfig = pd.DataFrame(tlaconfig_list[1:], columns=tlaconfig_list[0]).set_index('param')

    datadir = pathlib.Path(__file__).parents[1]

    g_tla_ref_data_sources = {
        'Based on- WRI 2016': str(
            datadir.joinpath('solution', 'tropicalforests', 'tla_based_on_WRI_2016_widescale_reforestation.csv')),
    }
    tla = TLA(g_tlaconfig, g_tla_ref_data_sources)

    print(tla._forecast_data_global)
    print(tla._forecast_data_oecd90)

