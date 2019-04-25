"""Adoption Data module."""  # by Denton Gentry
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import math  # by Denton Gentry
import pathlib  # by Denton Gentry
import os  # by Denton Gentry
# by Denton Gentry
from model import interpolation  # by Denton Gentry
from model import metaclass_cache  # by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry
from statistics import mean  # by Denton Gentry


# by Denton Gentry
class AdoptionData(object, metaclass=metaclass_cache.MetaclassCache):  # by Denton Gentry
    REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',  # by Denton Gentry
               'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA']  # by Denton Gentry
    # by Denton Gentry
    """Implements Adoption Data module."""  # by Denton Gentry

    def __init__(self, ac, data_sources, adconfig, world_includes_regional=None):  # by Denton Gentry
        """Arguments:  # by Denton Gentry
             ac: advanced_controls.py  # by Denton Gentry
             data_sources: a dict() of group names which contain dicts of data source names.  # by Denton Gentry
               For example:  # by Denton Gentry
               {  # by Denton Gentry
                 'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...}  # by Denton Gentry
                 'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...}  # by Denton Gentry
                 'Conservative Cases': {'Study Name E': 'filename E', 'Study Name F': 'filename F', ...}  # by Denton Gentry
               }  # by Denton Gentry
             adconfig: Pandas dataframe with columns:  # by Denton Gentry
               'trend', 'growth', 'low_sd_mult', 'high_sd_mult'  # by Denton Gentry
               and rows for each region:  # by Denton Gentry
               'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',  # by Denton Gentry
               'Latin America', 'China', 'India', 'EU', 'USA'  # by Denton Gentry
             world_includes_regional: boolean of whether the global min/max/sd should include  # by Denton Gentry
               data from the primary regions.  # by Denton Gentry
        """  # by Denton Gentry
        self.ac = ac  # by Denton Gentry
        self.data_sources = data_sources  # by Denton Gentry
        self.adconfig = adconfig  # by Denton Gentry
        self.world_includes_regional = world_includes_regional  # by Denton Gentry
        self._populate_adoption_data()  # by Denton Gentry

    # by Denton Gentry
    def _populate_adoption_data(self):  # by Denton Gentry
        """Read data files in self.data_sources to populate adoption data."""  # by Denton Gentry
        self._adoption_data_global = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_global.name = 'adoption_data_global'  # by Denton Gentry
        self._adoption_data_oecd90 = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_oecd90.name = 'adoption_data_oecd90'  # by Denton Gentry
        self._adoption_data_eastern_europe = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_eastern_europe.name = 'adoption_data_eastern_europe'  # by Denton Gentry
        self._adoption_data_asia_sans_japan = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_asia_sans_japan.name = 'adoption_data_asia_sans_japan'  # by Denton Gentry
        self._adoption_data_middle_east_and_africa = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_middle_east_and_africa.name = 'adoption_data_middle_east_and_africa'  # by Denton Gentry
        self._adoption_data_latin_america = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_latin_america.name = 'adoption_data_latin_america'  # by Denton Gentry
        self._adoption_data_china = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_china.name = 'adoption_data_china'  # by Denton Gentry
        self._adoption_data_india = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_india.name = 'adoption_data_india'  # by Denton Gentry
        self._adoption_data_eu = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_eu.name = 'adoption_data_eu'  # by Denton Gentry
        self._adoption_data_usa = pd.DataFrame()  # by Denton Gentry
        self._adoption_data_usa.name = 'adoption_data_usa'  # by Denton Gentry
        for (groupname, group) in self.data_sources.items():  # by Denton Gentry
            for (name, value) in group.items():  # by Denton Gentry
                if isinstance(value, str) or isinstance(value, pathlib.Path) or isinstance(value,
                                                                                           pathlib.PurePath):  # by Denton Gentry
                    sources = {name: value}  # by Denton Gentry
                else:  # by Denton Gentry
                    sources = value  # by Denton Gentry
                for name, filename in sources.items():  # by Denton Gentry
                    df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,  # by Denton Gentry
                                     skip_blank_lines=True, comment='#')  # by Denton Gentry
                    self._adoption_data_global.loc[:, name] = df.loc[:, 'World']  # by Denton Gentry
                    self._adoption_data_oecd90.loc[:, name] = df.loc[:, 'OECD90']  # by Denton Gentry
                    self._adoption_data_eastern_europe.loc[:, name] = df.loc[:, 'Eastern Europe']  # by Denton Gentry
                    self._adoption_data_asia_sans_japan.loc[:, name] = df.loc[:,
                                                                       'Asia (Sans Japan)']  # by Denton Gentry
                    self._adoption_data_middle_east_and_africa.loc[:, name] = df.loc[:,
                                                                              'Middle East and Africa']  # by Denton Gentry
                    self._adoption_data_latin_america.loc[:, name] = df.loc[:, 'Latin America']  # by Denton Gentry
                    self._adoption_data_china.loc[:, name] = df.loc[:, 'China']  # by Denton Gentry
                    self._adoption_data_india.loc[:, name] = df.loc[:, 'India']  # by Denton Gentry
                    self._adoption_data_eu.loc[:, name] = df.loc[:, 'EU']  # by Denton Gentry
                    self._adoption_data_usa.loc[:, name] = df.loc[:, 'USA']  # by Denton Gentry

    # by Denton Gentry
    def _min_max_sd(self, adoption_data, source, data_sources):  # by Denton Gentry
        """Return the min, max, and standard deviation for adoption data."""  # by Denton Gentry
        result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Min', 'Max', 'S.D'])  # by Denton Gentry
        result.loc[:, 'Min'] = adoption_data.min(axis=1)  # by Denton Gentry
        result.loc[:, 'Max'] = adoption_data.max(axis=1)  # by Denton Gentry
        # by Denton Gentry
        columns = interpolation.matching_data_sources(data_sources=data_sources,  # by Denton Gentry
                                                      name=source, groups_only=False)  # by Denton Gentry
        if columns is None:  # by Denton Gentry
            result.loc[:, 'S.D'] = np.nan  # by Denton Gentry
        elif len(columns) > 1:  # by Denton Gentry
            # Excel STDDEV.P is a whole population stddev, ddof=0  # by Denton Gentry
            result.loc[:, 'S.D'] = adoption_data.loc[:, columns].std(axis=1, ddof=0)  # by Denton Gentry
        else:  # by Denton Gentry
            result.loc[:, 'S.D'] = adoption_data.std(axis=1, ddof=0)  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    def _low_med_high(self, adoption_data, min_max_sd, adconfig, source, data_sources):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High."""  # by Denton Gentry
        result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Low', 'Medium', 'High'])  # by Denton Gentry
        columns = interpolation.matching_data_sources(data_sources=data_sources,  # by Denton Gentry
                                                      name=source, groups_only=False)  # by Denton Gentry
        if columns is None:  # by Denton Gentry
            result.loc[:, 'Medium'] = np.nan  # by Denton Gentry
            result.loc[:, 'Low'] = np.nan  # by Denton Gentry
            result.loc[:, 'High'] = np.nan  # by Denton Gentry
        else:  # by Denton Gentry
            # In Excel, the Mean computation is:  # by Denton Gentry
            # SUM($C46:$Q46)/COUNTIF($C46:$Q46,">0")  # by Denton Gentry
            #  # by Denton Gentry
            # The intent is to skip sources which are empty, but also means that  # by Denton Gentry
            # a source where the real data is 0.0 will not impact the Medium result.  # by Denton Gentry
            #  # by Denton Gentry
            # See this document for more information:  # by Denton Gentry
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.yvwwsbvutw2j  # by Denton Gentry
            #  # by Denton Gentry
            # We're matching the Excel behavior in the initial product. This decision can  # by Denton Gentry
            # be revisited later, when matching results from Excel is no longer required.  # by Denton Gentry
            # To revert, use:    medium = adoption_data.loc[:, columns].mean(axis=1)  # by Denton Gentry
            medium = adoption_data.loc[:, columns].mask(lambda f: f == 0.0, np.nan).mean(axis=1)  # by Denton Gentry
            result.loc[:, 'Medium'] = medium  # by Denton Gentry
            result.loc[:, 'Low'] = medium - (min_max_sd.loc[:, 'S.D'] * adconfig.loc['low_sd_mult'])  # by Denton Gentry
            result.loc[:, 'High'] = medium + (
                min_max_sd.loc[:, 'S.D'] * adconfig.loc['high_sd_mult'])  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    def _adoption_trend(self, low_med_high, growth, trend):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms."""  # by Denton Gentry
        if growth is None or trend is None:  # by Denton Gentry
            result = pd.DataFrame(np.nan, index=low_med_high.index.copy(), columns=['adoption'])  # by Denton Gentry
        else:  # by Denton Gentry
            data = low_med_high[growth]  # by Denton Gentry
            result = interpolation.trend_algorithm(data=data, trend=trend)  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    def _get_data_sources(self, region):  # by Denton Gentry
        key = "Region: " + region  # by Denton Gentry
        return self.data_sources.get(key, self.data_sources)  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_global(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'World' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B45:R94  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_global  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_global_with_regional(self):  # by Denton Gentry
        """Return adoption data for the 'World' region with regional data added in.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B45:R94 when B30:B31 are both 'Y' """  # by Denton Gentry
        regional = pd.DataFrame(columns=['OECD90', 'Eastern Europe', 'Asia (Sans Japan)',  # by Denton Gentry
                                         'Middle East and Africa', 'Latin America'])  # by Denton Gentry
        regional['OECD90'] = self.adoption_trend_oecd90().loc[:, 'adoption']  # by Denton Gentry
        regional['Eastern Europe'] = self.adoption_trend_eastern_europe().loc[:, 'adoption']  # by Denton Gentry
        regional['Asia (Sans Japan)'] = self.adoption_trend_asia_sans_japan().loc[:, 'adoption']  # by Denton Gentry
        regional['Middle East and Africa'] = self.adoption_trend_middle_east_and_africa().loc[:,
                                             'adoption']  # by Denton Gentry
        regional['Latin America'] = self.adoption_trend_latin_america().loc[:, 'adoption']  # by Denton Gentry
        regional_sum = regional.sum(axis=1)  # by Denton Gentry
        regional_sum.name = 'RegionalSum'  # by Denton Gentry
        adoption = self.adoption_data_global().copy()  # by Denton Gentry
        adoption.loc[:, 'RegionalSum'] = np.nan  # by Denton Gentry
        adconfig = self.adconfig['World']  # by Denton Gentry
        if self.ac.soln_pds_adoption_prognostication_source == 'ALL SOURCES':  # by Denton Gentry
            adoption.update(regional_sum)  # by Denton Gentry
        adoption.name = 'adoption_data_global'  # by Denton Gentry
        return adoption  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_global(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'World' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X45:Z94  # by Denton Gentry
        """  # by Denton Gentry
        data_sources = self._get_data_sources(region='World')  # by Denton Gentry
        if self.world_includes_regional:  # by Denton Gentry
            adoption = self.adoption_data_global_with_regional()  # by Denton Gentry
            data_sources = data_sources.copy()  # by Denton Gentry
            data_sources.update({'RegionalSum': {'RegionalSum': ''}})  # by Denton Gentry
        else:  # by Denton Gentry
            adoption = self.adoption_data_global()  # by Denton Gentry
        result = self._min_max_sd(adoption_data=adoption,  # by Denton Gentry
                                  source=self.ac.soln_pds_adoption_prognostication_source,
                                  data_sources=data_sources)  # by Denton Gentry
        result.name = 'adoption_min_max_sd_global'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_global(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB45:AD94  # by Denton Gentry
        """  # by Denton Gentry
        data_sources = self._get_data_sources(region='World')  # by Denton Gentry
        if self.world_includes_regional:  # by Denton Gentry
            adoption = self.adoption_data_global_with_regional()  # by Denton Gentry
            data_sources = data_sources.copy()  # by Denton Gentry
            data_sources.update({'RegionalSum': {'RegionalSum': ''}})  # by Denton Gentry
        else:  # by Denton Gentry
            adoption = self.adoption_data_global()  # by Denton Gentry
        result = self._low_med_high(adoption_data=adoption,  # by Denton Gentry
                                    min_max_sd=self.adoption_min_max_sd_global(), adconfig=self.adconfig['World'],
                                    # by Denton Gentry
                                    source=self.ac.soln_pds_adoption_prognostication_source,
                                    data_sources=data_sources)  # by Denton Gentry
        result.name = 'adoption_low_med_high_global'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_global(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'World' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY50:CA96     Degree2: 'Adoption Data'!CF50:CI96  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN50:CR96    Exponential: 'Adoption Data'!CW50:CY96  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'World']  # by Denton Gentry
        growth = self.ac.soln_pds_adoption_prognostication_growth  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_global(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_global_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_oecd90(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'OECD90' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B105:R154  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_oecd90  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_oecd90(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'OECD90' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X105:Z154  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_oecd90(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='OECD90'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_oecd90'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_oecd90(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB105:AD154  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_oecd90(),  # by Denton Gentry
                                    self.adoption_min_max_sd_oecd90(), self.adconfig['OECD90'],  # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='OECD90'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_oecd90'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_oecd90(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'OECD90' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY110:CA156     Degree2: 'Adoption Data'!CF110:CI156  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN110:CR156    Exponential: 'Adoption Data'!CW110:CY156  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'OECD90']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'OECD90']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_oecd90(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_oecd90_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_eastern_europe(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'Eastern Europe' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B169:R218  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_eastern_europe  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_eastern_europe(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'Eastern Europe' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X169:Z218  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_eastern_europe(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='Eastern Europe'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_eastern_europe'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_eastern_europe(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB169:AD218  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_eastern_europe(),  # by Denton Gentry
                                    self.adoption_min_max_sd_eastern_europe(), self.adconfig['Eastern Europe'],
                                    # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='Eastern Europe'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_eastern_europe'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_eastern_europe(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'Eastern Europe' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY174:CA220     Degree2: 'Adoption Data'!CF174:CI220  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN174:CR220    Exponential: 'Adoption Data'!CW174:CY220  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'Eastern Europe']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'Eastern Europe']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_eastern_europe(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_eastern_europe_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_asia_sans_japan(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'Asia (Sans Japan)' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B232:R281  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_asia_sans_japan  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_asia_sans_japan(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'Asia (Sans Japan)' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X232:Z281  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_asia_sans_japan(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='Asia (Sans Japan)'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_asia_sans_japan'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_asia_sans_japan(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB232:AD281  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_asia_sans_japan(),  # by Denton Gentry
                                    self.adoption_min_max_sd_asia_sans_japan(), self.adconfig['Asia (Sans Japan)'],
                                    # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='Asia (Sans Japan)'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_asia_sans_japan'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_asia_sans_japan(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'Asia (Sans Japan)' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY237:CA283     Degree2: 'Adoption Data'!CF237:CI283  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN237:CR283    Exponential: 'Adoption Data'!CW237:CY283  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'Asia (Sans Japan)']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'Asia (Sans Japan)']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_asia_sans_japan(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_asia_sans_japan_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_middle_east_and_africa(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'Middle East and Africa' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B295:R344  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_middle_east_and_africa  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_middle_east_and_africa(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'Middle East and Africa' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X295:Z344  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_middle_east_and_africa(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(
                                      region='Middle East and Africa'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_middle_east_and_africa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_middle_east_and_africa(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB295:AD344  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_middle_east_and_africa(),  # by Denton Gentry
                                    self.adoption_min_max_sd_middle_east_and_africa(),
                                    self.adconfig['Middle East and Africa'],  # by Denton Gentry
                                    source="ALL SOURCES", data_sources=self._get_data_sources(
                region='Middle East and Africa'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_middle_east_and_africa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_middle_east_and_africa(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'Middle East and Africa' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY300:CA346     Degree2: 'Adoption Data'!CF300:CI346  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN300:CR346    Exponential: 'Adoption Data'!CW300:CY346  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'Middle East and Africa']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'Middle East and Africa']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_middle_east_and_africa(), growth,
                                      trend)  # by Denton Gentry
        result.name = 'adoption_trend_middle_east_and_africa_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_latin_america(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'Latin America' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B358:R407  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_latin_america  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_latin_america(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'Latin America' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X358:Z407  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_latin_america(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='Latin America'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_latin_america'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_latin_america(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB358:AD407  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_latin_america(),  # by Denton Gentry
                                    self.adoption_min_max_sd_latin_america(), self.adconfig['Latin America'],
                                    # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='Latin America'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_latin_america'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_latin_america(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'Latin America' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY363:CA409     Degree2: 'Adoption Data'!CF363:CI409  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN363:CR409    Exponential: 'Adoption Data'!CW363:CY409  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'Latin America']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'Latin America']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_latin_america(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_latin_america_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_china(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'China' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B421:R470  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_china  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_china(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'China' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X421:Z470  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_china(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='China'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_china'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_china(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB421:AD470  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_china(),  # by Denton Gentry
                                    self.adoption_min_max_sd_china(), self.adconfig['China'],  # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='China'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_china'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_china(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'China' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY426:CA472     Degree2: 'Adoption Data'!CF426:CI472  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN426:CR472    Exponential: 'Adoption Data'!CW426:CY472  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'China']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'China']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_china(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_china_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_india(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'India' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B485:R534  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_india  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_india(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'India' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X485:Z534  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_india(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='India'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_india'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_india(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB485:AD534  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_india(),  # by Denton Gentry
                                    self.adoption_min_max_sd_india(), self.adconfig['India'],  # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='India'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_india'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_india(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'India' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY490:CA536     Degree2: 'Adoption Data'!CF490:CI536  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN490:CR536    Exponential: 'Adoption Data'!CW490:CY536  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'India']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'India']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_india(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_india_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_eu(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'EU' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B549:R598  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_eu  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_eu(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'EU' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X549:Z598  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_eu(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='EU'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_eu'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_eu(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB549:AD598  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_eu(),  # by Denton Gentry
                                    self.adoption_min_max_sd_eu(), self.adconfig['EU'],  # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='EU'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_eu'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_eu(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'EU' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY554:CA600     Degree2: 'Adoption Data'!CF554:CI600  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN554:CR600    Exponential: 'Adoption Data'!CW554:CY600  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'EU']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'EU']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_eu(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_eu_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_usa(self):  # by Denton Gentry
        """Return adoption data for the given solution in the 'USA' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!B614:R663  # by Denton Gentry
        """  # by Denton Gentry
        return self._adoption_data_usa  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_min_max_sd_usa(self):  # by Denton Gentry
        """Return the min, max, and standard deviation for the adoption data in the 'USA' region.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!X614:Z663  # by Denton Gentry
        """  # by Denton Gentry
        result = self._min_max_sd(self.adoption_data_usa(), source="ALL SOURCES",  # by Denton Gentry
                                  data_sources=self._get_data_sources(region='USA'))  # by Denton Gentry
        result.name = 'adoption_min_max_sd_usa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_low_med_high_usa(self):  # by Denton Gentry
        """Return the selected data sources as Medium, and N stddev away as Low and High.  # by Denton Gentry
           SolarPVUtil 'Adoption Data'!AB614:AD663  # by Denton Gentry
        """  # by Denton Gentry
        result = self._low_med_high(self.adoption_data_usa(),  # by Denton Gentry
                                    self.adoption_min_max_sd_usa(), self.adconfig['USA'],  # by Denton Gentry
                                    source="ALL SOURCES",
                                    data_sources=self._get_data_sources(region='USA'))  # by Denton Gentry
        result.name = 'adoption_low_med_high_usa'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_usa(self, trend=None):  # by Denton Gentry
        """Adoption prediction via one of several interpolation algorithms in the 'USA' region.  # by Denton Gentry
           Linear: SolarPVUtil 'Adoption Data'!BY619:CA665     Degree2: 'Adoption Data'!CF619:CI665  # by Denton Gentry
           Degree3: SolarPVUtil 'Adoption Data'!CN619:CR665    Exponential: 'Adoption Data'!CW619:CY665  # by Denton Gentry
        """  # by Denton Gentry
        if not trend:  # by Denton Gentry
            trend = self.adconfig.loc['trend', 'USA']  # by Denton Gentry
        growth = self.adconfig.loc['growth', 'USA']  # by Denton Gentry
        result = self._adoption_trend(self.adoption_low_med_high_usa(), growth, trend)  # by Denton Gentry
        result.name = 'adoption_trend_usa_' + str(trend).lower()  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_is_single_source(self):  # by Denton Gentry
        """Whether the source data selected is one source or multiple."""  # by Denton Gentry
        return not interpolation.is_group_name(data_sources=self.data_sources,  # by Denton Gentry
                                               name=self.ac.soln_pds_adoption_prognostication_source)  # by Denton Gentry

    # by Denton Gentry
    def _set_adoption_one_region(self, result, region, adoption_trend, adoption_low_med_high):  # by Denton Gentry
        result[region] = adoption_trend.loc[:, 'adoption']  # by Denton Gentry
        first_year = result.first_valid_index()  # by Denton Gentry
        result.loc[first_year, region] = adoption_low_med_high.loc[first_year, 'Medium']  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_data_per_region(self):  # by Denton Gentry
        """Return a dataframe of adoption data, one column per region."""  # by Denton Gentry
        growth = self.ac.soln_pds_adoption_prognostication_growth  # by Denton Gentry
        if growth is None:  # by Denton Gentry
            tmp = self.adoption_low_med_high_global()  # by Denton Gentry
            df = pd.DataFrame(np.nan, columns=self.REGIONS, index=tmp.index)  # by Denton Gentry
        else:  # by Denton Gentry
            df = pd.DataFrame(columns=self.REGIONS)  # by Denton Gentry
            df.loc[:, 'World'] = self.adoption_low_med_high_global()[growth]  # by Denton Gentry
            df.loc[:, 'OECD90'] = self.adoption_low_med_high_oecd90()[growth]  # by Denton Gentry
            df.loc[:, 'Eastern Europe'] = self.adoption_low_med_high_eastern_europe()[growth]  # by Denton Gentry
            df.loc[:, 'Asia (Sans Japan)'] = self.adoption_low_med_high_asia_sans_japan()[growth]  # by Denton Gentry
            df.loc[:, 'Middle East and Africa'] = self.adoption_low_med_high_middle_east_and_africa()[
                growth]  # by Denton Gentry
            df.loc[:, 'Latin America'] = self.adoption_low_med_high_latin_america()[growth]  # by Denton Gentry
            df.loc[:, 'China'] = self.adoption_low_med_high_china()[growth]  # by Denton Gentry
            df.loc[:, 'India'] = self.adoption_low_med_high_india()[growth]  # by Denton Gentry
            df.loc[:, 'EU'] = self.adoption_low_med_high_eu()[growth]  # by Denton Gentry
            df.loc[:, 'USA'] = self.adoption_low_med_high_usa()[growth]  # by Denton Gentry
        df.name = 'adoption_data_per_region'  # by Denton Gentry
        return df  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def adoption_trend_per_region(self):  # by Denton Gentry
        """Return a dataframe of adoption trends, one column per region."""  # by Denton Gentry
        df = pd.DataFrame(columns=self.REGIONS)  # by Denton Gentry
        df['World'] = self.adoption_trend_global()['adoption']  # by Denton Gentry
        df['OECD90'] = self.adoption_trend_oecd90()['adoption']  # by Denton Gentry
        df['Eastern Europe'] = self.adoption_trend_eastern_europe()['adoption']  # by Denton Gentry
        df['Asia (Sans Japan)'] = self.adoption_trend_asia_sans_japan()['adoption']  # by Denton Gentry
        df['Middle East and Africa'] = self.adoption_trend_middle_east_and_africa()['adoption']  # by Denton Gentry
        df['Latin America'] = self.adoption_trend_latin_america()['adoption']  # by Denton Gentry
        df['China'] = self.adoption_trend_china()['adoption']  # by Denton Gentry
        df['India'] = self.adoption_trend_india()['adoption']  # by Denton Gentry
        df['EU'] = self.adoption_trend_eu()['adoption']  # by Denton Gentry
        df['USA'] = self.adoption_trend_usa()['adoption']  # by Denton Gentry
        return df  # by Denton Gentry
