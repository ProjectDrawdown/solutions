"""Total Addressable Market module."""
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import os.path  # by Denton Gentry
import pathlib  # by Denton Gentry
# by Denton Gentry
from model import interpolation  # by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry


# by Denton Gentry
# by Denton Gentry
class TAM:  # by Denton Gentry
    """Total Addressable Market module."""

    # by Denton Gentry
    def __init__(self, tamconfig, tam_ref_data_sources, tam_pds_data_sources,  # by Denton Gentry
                 world_includes_regional=None):  # by Denton Gentry
        """TAM module.  # by Denton Gentry
      # by Denton Gentry
           Arguments  # by Denton Gentry
           tamconfig: Pandas dataframe with columns:  # by Denton Gentry
              'source_until_2014', 'source_after_2014', 'trend', 'growth', 'low_sd_mult', 'high_sd_mult'  # by Denton Gentry
              and rows for each region:  # by Denton Gentry
              'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',  # by Denton Gentry
              'Latin America', 'China', 'India', 'EU', 'USA'  # by Denton Gentry
           tam_ref_data_sources: a dict() of group names which contain dicts of data source names.  # by Denton Gentry
             Used for Total Addressable Market and adoption calculations in the REF scenario.  # by Denton Gentry
             For example:  # by Denton Gentry
             {  # by Denton Gentry
               'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...}  # by Denton Gentry
               'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...}  # by Denton Gentry
               'Conservative Cases': {'Study Name E': 'filename E', 'Study Name F': 'filename F', ...}  # by Denton Gentry
             }  # by Denton Gentry
           tam_pds_data_sources: as tam_ref_data_sources, for the PDS scenario.  # by Denton Gentry
           world_includes_regional: boolean of whether the global min/max/sd should include  # by Denton Gentry
             data from the primary regions.  # by Denton Gentry
        """  # by Denton Gentry
        self.tamconfig = tamconfig  # by Denton Gentry
        self.tam_ref_data_sources = tam_ref_data_sources  # by Denton Gentry
        self.tam_pds_data_sources = tam_pds_data_sources  # by Denton Gentry
        self.world_includes_regional = world_includes_regional  # by Denton Gentry
        self._populate_forecast_data()  # by Denton Gentry

    # by Denton Gentry
    def _populate_forecast_data(self):  # by Denton Gentry
        """Read data files in self.tam_*_data_sources to populate forecast data."""  # by Denton Gentry
        self._forecast_data_global = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_global.name = 'forecast_data_global'  # by Denton Gentry
        self._forecast_data_oecd90 = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_oecd90.name = 'forecast_data_oecd90'  # by Denton Gentry
        self._forecast_data_eastern_europe = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_eastern_europe.name = 'forecast_data_eastern_europe'  # by Denton Gentry
        self._forecast_data_asia_sans_japan = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_asia_sans_japan.name = 'forecast_data_asia_sans_japan'  # by Denton Gentry
        self._forecast_data_middle_east_and_africa = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_middle_east_and_africa.name = 'forecast_data_middle_east_and_africa'  # by Denton Gentry
        self._forecast_data_latin_america = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_latin_america.name = 'forecast_data_latin_america'  # by Denton Gentry
        self._forecast_data_china = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_china.name = 'forecast_data_china'  # by Denton Gentry
        self._forecast_data_india = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_india.name = 'forecast_data_india'  # by Denton Gentry
        self._forecast_data_eu = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_eu.name = 'forecast_data_eu'  # by Denton Gentry
        self._forecast_data_usa = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_usa.name = 'forecast_data_usa'  # by Denton Gentry
        for (groupname, group) in self.tam_ref_data_sources.items():  # by Denton Gentry
            for (name, value) in group.items():  # by Denton Gentry
                if isinstance(value, str) or isinstance(value, pathlib.Path):  # by Denton Gentry
                    sources = {name: value}  # by Denton Gentry
                else:  # by Denton Gentry
                    sources = value  # by Denton Gentry
                for name, filename in sources.items():  # by Denton Gentry
                    df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,  # by Denton Gentry
                                     skip_blank_lines=True, comment='#')  # by Denton Gentry
                    self._forecast_data_global.loc[:, name] = df.loc[:, 'World']  # by Denton Gentry
                    self._forecast_data_oecd90.loc[:, name] = df.loc[:, 'OECD90']  # by Denton Gentry
                    self._forecast_data_eastern_europe.loc[:, name] = df.loc[:, 'Eastern Europe']  # by Denton Gentry
                    self._forecast_data_asia_sans_japan.loc[:, name] = df.loc[:,
                                                                       'Asia (Sans Japan)']  # by Denton Gentry
                    self._forecast_data_middle_east_and_africa.loc[:, name] = df.loc[:,
                                                                              'Middle East and Africa']  # by Denton Gentry
                    self._forecast_data_latin_america.loc[:, name] = df.loc[:, 'Latin America']  # by Denton Gentry
                    self._forecast_data_china.loc[:, name] = df.loc[:, 'China']  # by Denton Gentry
                    self._forecast_data_india.loc[:, name] = df.loc[:, 'India']  # by Denton Gentry
                    self._forecast_data_eu.loc[:, name] = df.loc[:, 'EU']  # by Denton Gentry
                    self._forecast_data_usa.loc[:, name] = df.loc[:, 'USA']  # by Denton Gentry
        self._forecast_data_pds_global = pd.DataFrame()  # by Denton Gentry
        self._forecast_data_pds_global.name = 'forecast_data_pds_global'  # by Denton Gentry
        for (groupname, group) in self.tam_pds_data_sources.items():  # by Denton Gentry
            for (name, value) in group.items():  # by Denton Gentry
                if isinstance(value, str) or isinstance(value, pathlib.Path):  # by Denton Gentry
                    sources = {name: value}  # by Denton Gentry
                else:  # by Denton Gentry
                    sources = value  # by Denton Gentry
                for name, filename in sources.items():  # by Denton Gentry
                    df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,  # by Denton Gentry
                                     skip_blank_lines=True, comment='#')  # by Denton Gentry
                    self._forecast_data_pds_global.loc[:, name] = df.loc[:, 'World']  # by Denton Gentry

    # by Denton Gentry
    def _min_max_sd(self, forecast, tamconfig, data_sources):  # by Denton Gentry
        """Return the min, max, and standard deviation for TAM data.  # by Denton Gentry
           Arguments:  # by Denton Gentry
             forecast: the TAM forecast dataframe for all sources.  # by Denton Gentry
             tamconfig: the row from self.tamconfig to use  # by Denton Gentry
             data_sources: dict of dicts of datasources, as described in tam_ref_data_sources in  # by Denton Gentry
               the constructor  # by Denton Gentry
        """  # by Denton Gentry
        source_until_2014 = tamconfig['source_until_2014']  # by Denton Gentry
        source_after_2014 = tamconfig['source_after_2014']  # by Denton Gentry
        # by Denton Gentry
        result = pd.DataFrame(np.nan, index=forecast.index.copy(), columns=['Min', 'Max', 'S.D'])  # by Denton Gentry
        result.loc[:, 'Min'] = forecast.dropna(axis='columns', how='all').min(axis=1)  # by Denton Gentry
        result.loc[:, 'Max'] = forecast.max(axis=1)  # by Denton Gentry
        if forecast.empty:  # by Denton Gentry
            # Some solutions provide no data sources for PDS  # by Denton Gentry
            result.loc[:, 'S.D'] = np.nan  # by Denton Gentry
        else:  # by Denton Gentry
            columns = interpolation.matching_data_sources(data_sources=data_sources,  # by Denton Gentry
                                                          name=source_until_2014, groups_only=True)  # by Denton Gentry
            # Excel STDDEV.P is a whole population stddev, ddof=0  # by Denton Gentry
            m = forecast.loc[:2014, columns].dropna(axis='columns', how='all').std(axis=1, ddof=0)  # by Denton Gentry
            m.name = 'S.D'  # by Denton Gentry
            result.update(m)  # by Denton Gentry
            columns = interpolation.matching_data_sources(data_sources=data_sources,  # by Denton Gentry
                                                          name=source_after_2014, groups_only=True)  # by Denton Gentry
            m = forecast.loc[2015:, columns].dropna(axis='columns', how='all').std(axis=1, ddof=0)  # by Denton Gentry
            m.name = 'S.D'  # by Denton Gentry
            result.update(m)  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    def _low_med_high(self, forecast, min_max_sd, tamconfig, data_sources):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
      # by Denton Gentry
           Arguments:  # by Denton Gentry
             forecast: DataFrame of all of the data sources, source name as the column name.  # by Denton Gentry
             min_max_sd: DataFrame with columns for the Minimum, Maxiumum, and Standard deviation.  # by Denton Gentry
             tamconfig: the row from self.tamconfig to use  # by Denton Gentry
             data_sources: dict of dicts of datasources, as described in tam_ref_data_sources in  # by Denton Gentry
               the constructor  # by Denton Gentry
        """  # by Denton Gentry
        result = pd.DataFrame(np.nan, index=forecast.index.copy(),
                              columns=['Low', 'Medium', 'High'])  # by Denton Gentry
        if forecast.empty:  # by Denton Gentry
            result.loc[:, 'Medium'] = np.nan  # by Denton Gentry
            result.loc[:, 'Low'] = np.nan  # by Denton Gentry
            result.loc[:, 'High'] = np.nan  # by Denton Gentry
            return result  # by Denton Gentry
        # by Denton Gentry
        columns = interpolation.matching_data_sources(data_sources=data_sources,  # by Denton Gentry
                                                      name=tamconfig['source_until_2014'],
                                                      groups_only=False)  # by Denton Gentry
        if columns and len(columns) > 1:  # by Denton Gentry
            # In Excel, the Mean computation is:  # by Denton Gentry
            # SUM($C521:$Q521)/COUNTIF($C521:$Q521,">0")  # by Denton Gentry
            #  # by Denton Gentry
            # The intent is to skip sources which are empty, but also means that  # by Denton Gentry
            # a source where the real data is 0.0 will not impact the Medium result.  # by Denton Gentry
            #  # by Denton Gentry
            # See this document for more information:  # by Denton Gentry
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.yvwwsbvutw2j  # by Denton Gentry
            #  # by Denton Gentry
            # We're matching the Excel behavior in the initial product. This decision can  # by Denton Gentry
            # be revisited later, when matching results from Excel is no longer required.  # by Denton Gentry
            # To revert, use:    m = forecast.loc[:2014, columns].mean(axis=1)  # by Denton Gentry
            # and:               m = forecast.loc[2015:, columns].mean(axis=1)  # by Denton Gentry
            m = forecast.loc[:2014, columns].mask(lambda f: f == 0.0, np.nan).mean(axis=1)  # by Denton Gentry
            m.name = 'Medium'  # by Denton Gentry
            result.update(m)  # by Denton Gentry
        elif columns and len(columns) == 1:  # by Denton Gentry
            m = forecast.loc[:2014, columns].mean(axis=1)  # by Denton Gentry
            m.name = 'Medium'  # by Denton Gentry
            result.update(m)  # by Denton Gentry
        # by Denton Gentry
        columns = interpolation.matching_data_sources(data_sources=data_sources,  # by Denton Gentry
                                                      name=tamconfig['source_after_2014'],
                                                      groups_only=False)  # by Denton Gentry
        if columns and len(columns) > 1:  # by Denton Gentry
            # see comment above about Mean and this lambda function  # by Denton Gentry
            m = forecast.loc[2015:, columns].mask(lambda f: f == 0.0, np.nan).mean(axis=1)  # by Denton Gentry
            m.name = 'Medium'  # by Denton Gentry
            result.update(m)  # by Denton Gentry
        elif columns and len(columns) == 1:  # by Denton Gentry
            m = forecast.loc[2015:, columns].mean(axis=1)  # by Denton Gentry
            m.name = 'Medium'  # by Denton Gentry
            result.update(m)  # by Denton Gentry
        # by Denton Gentry
        low_sd_mult = tamconfig['low_sd_mult']  # by Denton Gentry
        high_sd_mult = tamconfig['high_sd_mult']  # by Denton Gentry
        result.loc[:, 'Low'] = result.loc[:, 'Medium'] - (min_max_sd.loc[:, 'S.D'] * low_sd_mult)  # by Denton Gentry
        result.loc[:, 'High'] = result.loc[:, 'Medium'] + (min_max_sd.loc[:, 'S.D'] * high_sd_mult)  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    def _get_trend(self, trend, tamconfig, data_sources):  # by Denton Gentry
        """Decision tree to select between trend choices.  # by Denton Gentry
      # by Denton Gentry
           Arguments:  # by Denton Gentry
             trend: explicit trend to use, if any. Pass None to have tamconfig be used.  # by Denton Gentry
             tamconfig: the row from self.tamconfig to use  # by Denton Gentry
             data_sources: dict of dicts of datasources, as described in tam_ref_data_sources in  # by Denton Gentry
               the constructor  # by Denton Gentry
      # by Denton Gentry
           If a trend was explictly specified, use it.  # by Denton Gentry
           If there is only one data source, use that source without any curve fitting.  # by Denton Gentry
           Otherwise, use the curve fit algorithm specified in the tamconfig.  # by Denton Gentry
        """  # by Denton Gentry
        if trend:  # by Denton Gentry
            return trend  # by Denton Gentry
        if not interpolation.is_group_name(data_sources=data_sources,  # by Denton Gentry
                                           name=tamconfig['source_after_2014']):  # by Denton Gentry
            return 'single'  # by Denton Gentry
        else:  # by Denton Gentry
            return tamconfig['trend']  # by Denton Gentry

    # by Denton Gentry
    def _get_data_sources(self, data_sources, region):  # by Denton Gentry
        key = "Region: " + region  # by Denton Gentry
        return data_sources.get(key, data_sources)  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_global(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B45:Q94 """  # by Denton Gentry
        return self._forecast_data_global  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def _forecast_data_regional_sum(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!Q45:Q94 when B29:B30 are both 'Y' """  # by Denton Gentry
        regional = pd.DataFrame(columns=['OECD90', 'Eastern Europe', 'Asia (Sans Japan)',  # by Denton Gentry
                                         'Middle East and Africa', 'Latin America'])  # by Denton Gentry
        self._set_tam_one_region(result=regional, region='OECD90',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_oecd90(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_oecd90())  # by Denton Gentry
        self._set_tam_one_region(result=regional, region='Eastern Europe',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_eastern_europe(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_eastern_europe())  # by Denton Gentry
        self._set_tam_one_region(result=regional, region='Asia (Sans Japan)',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_asia_sans_japan(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_asia_sans_japan())  # by Denton Gentry
        self._set_tam_one_region(result=regional, region='Middle East and Africa',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_middle_east_and_africa(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_middle_east_and_africa())  # by Denton Gentry
        self._set_tam_one_region(result=regional, region='Latin America',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_latin_america(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_latin_america())  # by Denton Gentry
        regional_sum = regional.sum(axis=1)  # by Denton Gentry
        regional_sum.name = 'RegionalSum'  # by Denton Gentry
        return regional_sum  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_global(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V45:Y94 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,
                                              region='World')  # by Denton Gentry
        if self.world_includes_regional:  # by Denton Gentry
            forecast = self.forecast_data_global().copy()  # by Denton Gentry
            regional_sum = self._forecast_data_regional_sum()  # by Denton Gentry
            forecast.loc[:, 'RegionalSum'] = regional_sum  # by Denton Gentry
            data_sources = data_sources.copy()  # by Denton Gentry
            data_sources.update({'RegionalSum': {'RegionalSum': ''}})  # by Denton Gentry
        else:  # by Denton Gentry
            forecast = self.forecast_data_global()  # by Denton Gentry
        result = self._min_max_sd(forecast=forecast,  # by Denton Gentry
                                  tamconfig=self.tamconfig['World'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_global'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_global(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA45:AC94 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,
                                              region='World')  # by Denton Gentry
        if self.world_includes_regional:  # by Denton Gentry
            forecast = self.forecast_data_global().copy()  # by Denton Gentry
            forecast.loc[:, 'RegionalSum'] = np.nan  # by Denton Gentry
            regional_sum = self._forecast_data_regional_sum()  # by Denton Gentry
            tamconfig = self.tamconfig['World']  # by Denton Gentry
            if tamconfig['source_after_2014'] == 'ALL SOURCES':  # by Denton Gentry
                forecast.update(regional_sum.loc[2015:])  # by Denton Gentry
            if tamconfig['source_until_2014'] == 'ALL SOURCES':  # by Denton Gentry
                forecast.update(regional_sum.loc[:2014])  # by Denton Gentry
            data_sources = data_sources.copy()  # by Denton Gentry
            data_sources.update({'RegionalSum': {'RegionalSum': ''}})  # by Denton Gentry
        else:  # by Denton Gentry
            forecast = self.forecast_data_global()  # by Denton Gentry
        result = self._low_med_high(forecast=forecast, min_max_sd=self.forecast_min_max_sd_global(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['World'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_global'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_global(self, trend=None):  # by Denton Gentry
        """Forecast for the 'World' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX50:BZ96     Degree2: SolarPVUtil 'TAM Data'!CE50:CH96  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM50:CQ96    Exponential: SolarPVUtil 'TAM Data'!CV50:CX96  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'World']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='World')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['World'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_global().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_global_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_pds_global(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B45:Q94 """  # by Denton Gentry
        return self._forecast_data_pds_global  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_pds_global(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V45:Y94 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_pds_data_sources,  # by Denton Gentry
                                              region='World')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_pds_global(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['PDS World'], data_sources=data_sources)  # by Denton Gentry
        result[result.isnull()] = self.forecast_min_max_sd_global()  # by Denton Gentry
        result.name = 'forecast_min_max_sd_pds_global'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_pds_global(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA45:AC94 """  # by Denton Gentry
        # In Excel, the PDS TAM calculation:  # by Denton Gentry
        # + uses World data for 2012-2014, unconditionally. However, many solutions  # by Denton Gentry
        #   make a practice of using curated data for the years 2012-2014 and paste  # by Denton Gentry
        #   it across all sources, so PDS and World are often the same for 2012-2014.  # by Denton Gentry
        # + uses PDS data for 2015+ where it exists, and uses World data where no  # by Denton Gentry
        #   PDS data exists.  # by Denton Gentry
        #  # by Denton Gentry
        # We implement this by calculating the World lmh, then update it with PDS  # by Denton Gentry
        # results where they exist, then concatenate PDS data for 2015+ with  # by Denton Gentry
        # World data for 2012-2014.  # by Denton Gentry
        #  # by Denton Gentry
        # Note that PDS min/max/sd uses PDS data for 2012-2014, not World, and this  # by Denton Gentry
        # makes a difference in solutions which do not paste the same curated data  # by Denton Gentry
        # for 2012-2014 across all sources. So this handling only exists here, not  # by Denton Gentry
        # forecast_min_max_sd_pds_global.  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_pds_data_sources,  # by Denton Gentry
                                              region='World')  # by Denton Gentry
        result_world = self.forecast_low_med_high_global().copy(deep=True)  # by Denton Gentry
        result_pds = self._low_med_high(forecast=self.forecast_data_pds_global(),  # by Denton Gentry
                                        min_max_sd=self.forecast_min_max_sd_pds_global(),  # by Denton Gentry
                                        tamconfig=self.tamconfig['PDS World'],  # by Denton Gentry
                                        data_sources=data_sources)  # by Denton Gentry
        result_2014 = result_world.loc[:2014].copy()  # by Denton Gentry
        result_2015 = result_world.loc[2015:].copy()  # by Denton Gentry
        result_2015.update(other=result_pds, overwrite=True)  # by Denton Gentry
        result = pd.concat([result_2014, result_2015], sort=False)  # by Denton Gentry
        result.name = 'forecast_low_med_high_pds_global'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_pds_global(self, trend=None):  # by Denton Gentry
        """Forecast for the 'World' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX50:BZ96     Degree2: SolarPVUtil 'TAM Data'!CE50:CH96  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM50:CQ96    Exponential: SolarPVUtil 'TAM Data'!CV50:CX96  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'PDS World']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_pds_data_sources,  # by Denton Gentry
                                              region='PDS World')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['PDS World'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_pds_global().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result[result.isnull()] = self.forecast_trend_global(trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_pds_global_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_oecd90(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B163:Q212 """  # by Denton Gentry
        return self._forecast_data_oecd90  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_oecd90(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V163:Y212 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='OECD90')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_oecd90(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['OECD90'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_oecd90'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_oecd90(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA163:AC212 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='OECD90')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_oecd90(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_oecd90(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['OECD90'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_oecd90'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_oecd90(self, trend=None):  # by Denton Gentry
        """Forecast for the 'OECD90' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX168:BZ214     Degree2: SolarPVUtil 'TAM Data'!CE168:CH214  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM168:CQ214    Exponential: SolarPVUtil 'TAM Data'!CV168:CX214  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'OECD90']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='OECD90')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['OECD90'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_oecd90().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_oecd90_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_eastern_europe(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B227:Q276 """  # by Denton Gentry
        return self._forecast_data_eastern_europe  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_eastern_europe(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V227:Y276 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Eastern Europe')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_eastern_europe(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['Eastern Europe'],
                                  data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_eastern_europe'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_eastern_europe(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA227:AC276 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Eastern Europe')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_eastern_europe(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_eastern_europe(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['Eastern Europe'],
                                    data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_eastern_europe'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_eastern_europe(self, trend=None):  # by Denton Gentry
        """Forecast for the 'Eastern Europe' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX232:BZ278     Degree2: SolarPVUtil 'TAM Data'!CE232:CH278  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM232:CQ278    Exponential: SolarPVUtil 'TAM Data'!CV232:CX278  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'Eastern Europe']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Eastern Europe')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['Eastern Europe'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_eastern_europe().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_eastern_europe_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_asia_sans_japan(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B290:Q339 """  # by Denton Gentry
        return self._forecast_data_asia_sans_japan  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_asia_sans_japan(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V290:Y339 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Asia (Sans Japan)')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_asia_sans_japan(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['Asia (Sans Japan)'],
                                  data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_asia_sans_japan'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_asia_sans_japan(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA290:AC339 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Asia (Sans Japan)')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_asia_sans_japan(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_asia_sans_japan(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['Asia (Sans Japan)'],
                                    data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_asia_sans_japan'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_asia_sans_japan(self, trend=None):  # by Denton Gentry
        """Forecast for the 'Asia (Sans Japan)' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX295:BZ341     Degree2: SolarPVUtil 'TAM Data'!CE295:CH341  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM295:CQ341    Exponential: SolarPVUtil 'TAM Data'!CV295:CX341  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'Asia (Sans Japan)']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Asia (Sans Japan)')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['Asia (Sans Japan)'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_asia_sans_japan().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_asia_sans_japan_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_middle_east_and_africa(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B353:Q402 """  # by Denton Gentry
        return self._forecast_data_middle_east_and_africa  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_middle_east_and_africa(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V353:Y402 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Middle East and Africa')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_middle_east_and_africa(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['Middle East and Africa'],
                                  data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_middle_east_and_africa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_middle_east_and_africa(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA353:AC402 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Middle East and Africa')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_middle_east_and_africa(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_middle_east_and_africa(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['Middle East and Africa'],
                                    data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_middle_east_and_africa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_middle_east_and_africa(self, trend=None):  # by Denton Gentry
        """Forecast for the 'Middle East and Africa' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX358:BZ404     Degree2: SolarPVUtil 'TAM Data'!CE358:CH404  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM358:CQ404    Exponential: SolarPVUtil 'TAM Data'!CV358:CX404  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'Middle East and Africa']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Middle East and Africa')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['Middle East and Africa'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_middle_east_and_africa().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_middle_east_and_africa_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_latin_america(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B416:Q465 """  # by Denton Gentry
        return self._forecast_data_latin_america  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_latin_america(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V416:Y465 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Latin America')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_latin_america(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['Latin America'],
                                  data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_latin_america'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_latin_america(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA416:AC465 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Latin America')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_latin_america(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_latin_america(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['Latin America'],
                                    data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_latin_america'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_latin_america(self, trend=None):  # by Denton Gentry
        """Forecast for the 'Latin America' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX421:BZ467     Degree2: SolarPVUtil 'TAM Data'!CE421:CH467  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM421:CQ467    Exponential: SolarPVUtil 'TAM Data'!CV421:CX467  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'Latin America']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='Latin America')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['Latin America'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_latin_america().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_latin_america_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_china(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B479:Q528 """  # by Denton Gentry
        return self._forecast_data_china  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_china(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V479:Y528 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='China')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_china(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['China'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_china'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_china(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA479:AC528 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='China')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_china(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_china(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['China'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_china'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_china(self, trend=None):  # by Denton Gentry
        """Forecast for the 'China' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX484:BZ530     Degree2: SolarPVUtil 'TAM Data'!CE484:CH530  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM484:CQ530    Exponential: SolarPVUtil 'TAM Data'!CV484:CX530  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'China']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='China')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['China'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_china().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_china_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_india(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B543:Q592 """  # by Denton Gentry
        return self._forecast_data_india  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_india(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V543:Y592 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='India')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_india(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['India'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_india'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_india(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA543:AC592 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='India')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_india(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_india(),  # by Denton Gentry
                                    tamconfig=self.tamconfig['India'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_india'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_india(self, trend=None):  # by Denton Gentry
        """Forecast for the 'India' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX548:BZ594     Degree2: SolarPVUtil 'TAM Data'!CE548:CH594  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM548:CQ594    Exponential: SolarPVUtil 'TAM Data'!CV548:CX594  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'India']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='India')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['India'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_india().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_india_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_eu(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B607:Q656 """  # by Denton Gentry
        return self._forecast_data_eu  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_eu(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V607:Y656 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='EU')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_eu(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['EU'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_eu'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_eu(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA607:AC656 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='EU')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_eu(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_eu(), tamconfig=self.tamconfig['EU'],
                                    # by Denton Gentry
                                    data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_eu'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_eu(self, trend=None):  # by Denton Gentry
        """Forecast for the 'EU' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX612:BZ658     Degree2: SolarPVUtil 'TAM Data'!CE612:CH658  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM612:CQ658    Exponential: SolarPVUtil 'TAM Data'!CV612:CX658  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'EU']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='EU')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['EU'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_eu().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_eu_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_data_usa(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!B672:Q721 """  # by Denton Gentry
        return self._forecast_data_usa  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_min_max_sd_usa(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!V672:Y721 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='USA')  # by Denton Gentry
        result = self._min_max_sd(forecast=self.forecast_data_usa(),  # by Denton Gentry
                                  tamconfig=self.tamconfig['USA'], data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_min_max_sd_usa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_low_med_high_usa(self):  # by Denton Gentry
        """ SolarPVUtil 'TAM Data'!AA672:AC721 """  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='USA')  # by Denton Gentry
        result = self._low_med_high(forecast=self.forecast_data_usa(),  # by Denton Gentry
                                    min_max_sd=self.forecast_min_max_sd_usa(), tamconfig=self.tamconfig['USA'],
                                    # by Denton Gentry
                                    data_sources=data_sources)  # by Denton Gentry
        result.name = 'forecast_low_med_high_usa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def forecast_trend_usa(self, trend=None):  # by Denton Gentry
        """Forecast for the 'USA' region via one of several interpolation algorithms.  # by Denton Gentry
           Linear: SolarPVUtil 'TAM Data'!BX677:BZ723     Degree2: SolarPVUtil 'TAM Data'!CE677:CH723  # by Denton Gentry
           Degree3: SolarPVUtil 'TAM Data'!CM677:CQ723    Exponential: SolarPVUtil 'TAM Data'!CV677:CX723  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'USA']  # by Denton Gentry
        data_sources = self._get_data_sources(data_sources=self.tam_ref_data_sources,  # by Denton Gentry
                                              region='USA')  # by Denton Gentry
        trend = self._get_trend(trend=trend, tamconfig=self.tamconfig['USA'],  # by Denton Gentry
                                data_sources=data_sources)  # by Denton Gentry
        data = self.forecast_low_med_high_usa().loc[:, growth]  # by Denton Gentry
        result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        result.name = 'forecast_trend_usa_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    def _set_tam_one_region(self, result, region, forecast_trend, forecast_low_med_high):  # by Denton Gentry
        """Set a single column in ref_tam_per_region."""  # by Denton Gentry
        result[region] = forecast_trend.loc[:, 'adoption']  # by Denton Gentry
        first_year = result.first_valid_index()  # by Denton Gentry
        result.loc[first_year, region] = forecast_low_med_high.loc[first_year, 'Medium']  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_tam_per_region(self):  # by Denton Gentry
        """Compiles the TAM for each of the major regions into a single dataframe.  # by Denton Gentry
      # by Denton Gentry
           This isn't on the TAM Data tab of the Excel implementation, but is commonly used  # by Denton Gentry
           by reference from other tabs. For convenience, we supply it.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!A16:K63  # by Denton Gentry
        """  # by Denton Gentry
        result = pd.DataFrame(columns=['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',  # by Denton Gentry
                                       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                                       'USA'])  # by Denton Gentry
        self._set_tam_one_region(result=result, region='World',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_global(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_global())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='OECD90',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_oecd90(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_oecd90())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Eastern Europe',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_eastern_europe(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_eastern_europe())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Asia (Sans Japan)',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_asia_sans_japan(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_asia_sans_japan())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Middle East and Africa',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_middle_east_and_africa(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_middle_east_and_africa())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Latin America',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_latin_america(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_latin_america())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='China',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_china(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_china())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='India',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_india(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_india())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='EU',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_eu(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_eu())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='USA',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_usa(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_usa())  # by Denton Gentry
        result.name = "ref_tam_per_region"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def pds_tam_per_region(self):  # by Denton Gentry
        """Compiles the PDS TAM for each of the major regions into a single dataframe.  # by Denton Gentry
      # by Denton Gentry
           At the time of this writing (11/2018), only the World region has a PDS forecast.  # by Denton Gentry
           The other, smaller regions use the REF TAM.  # by Denton Gentry
      # by Denton Gentry
           This isn't on the TAM Data tab of the Excel implementation, but is commonly used  # by Denton Gentry
           by reference from other tabs. For convenience, we supply it.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!A68:K115  # by Denton Gentry
        """  # by Denton Gentry
        result = pd.DataFrame(columns=['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',  # by Denton Gentry
                                       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                                       'USA'])  # by Denton Gentry
        # by Denton Gentry
        result['World'] = self.forecast_trend_pds_global().loc[:, 'adoption']  # by Denton Gentry
        lmh = self.forecast_low_med_high_pds_global()  # by Denton Gentry
        if result.dropna(axis=1, how='all').empty or lmh.dropna(axis=1, how='all').empty:  # by Denton Gentry
            result['World'] = self.forecast_trend_global().loc[:, 'adoption']  # by Denton Gentry
            lmh = self.forecast_low_med_high_global()  # by Denton Gentry
        growth = self.tamconfig.loc['growth', 'PDS World']  # by Denton Gentry
        first_year = result.first_valid_index()  # by Denton Gentry
        result.loc[first_year, 'World'] = lmh.loc[first_year, 'Medium']  # by Denton Gentry
        # by Denton Gentry
        self._set_tam_one_region(result=result, region='OECD90',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_oecd90(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_oecd90())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Eastern Europe',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_eastern_europe(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_eastern_europe())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Asia (Sans Japan)',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_asia_sans_japan(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_asia_sans_japan())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Middle East and Africa',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_middle_east_and_africa(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_middle_east_and_africa())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='Latin America',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_latin_america(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_latin_america())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='China',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_china(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_china())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='India',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_india(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_india())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='EU',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_eu(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_eu())  # by Denton Gentry
        self._set_tam_one_region(result=result, region='USA',  # by Denton Gentry
                                 forecast_trend=self.forecast_trend_usa(),  # by Denton Gentry
                                 forecast_low_med_high=self.forecast_low_med_high_usa())  # by Denton Gentry
        result.name = "pds_tam_per_region"  # by Denton Gentry
        return result  # by Denton Gentry
