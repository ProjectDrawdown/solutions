"""Adoption Data module."""

from functools import lru_cache
import pathlib
import re

from model import interpolation
from model import metaclass_cache
import model.dd as dd
import numpy as np
import pandas as pd


class AdoptionData(object, metaclass=metaclass_cache.MetaclassCache):
    """Implements Adoption Data module."""

    def __init__(self, ac, data_sources, adconfig, main_includes_regional=None):
        """Arguments:
             ac: advanced_controls.py
             data_sources: a dict() of group names which contain dicts of data source names.
               For example:
               {
                 'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...}
                 'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...}
                 'Conservative Cases': {'Study Name E': 'filename E', 'Study Name F': 'filename F', ...}
               }
             adconfig: Pandas dataframe with columns:
               'trend', 'growth', 'low_sd_mult', 'high_sd_mult'
               and rows for each region:
               'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
               'Latin America', 'China', 'India', 'EU', 'USA'
             main_includes_regional: boolean of whether the global min/max/sd should include
               data from the primary regions.
        """
        self.ac = ac
        self.data_sources = data_sources
        self.adconfig = adconfig
        self.main_includes_regional = main_includes_regional
        self._populate_adoption_data()


    def _name_to_identifier(self, name):
        """Convert names like "Middle East and Africa" to "middle_east_and_africa"."""
        x = re.sub(r"[()]", "", name.lower())
        return re.sub(r" ", "_", x)


    def _populate_adoption_data(self):
        """Read data files in self.tam_*_data_sources to populate forecast data."""
        df_per_region = {}
        main_region = dd.REGIONS[0]
        main_region_pds = 'PDS ' + main_region
        for region in dd.REGIONS + [main_region_pds]:
            df = pd.DataFrame()
            df.name = 'forecast_data_' + self._name_to_identifier(region)
            df_per_region[region] = df
        for (groupname, group) in self.data_sources.items():
            for (name, value) in group.items():
                if (isinstance(value, str) or isinstance(value, pathlib.Path) or
                        isinstance(value, pathlib.PurePath)):
                    sources = {name: value}
                else:
                    sources = value
                for name, filename in sources.items():
                    df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
                            skip_blank_lines=True, comment='#')
                    for region in dd.REGIONS:
                        df_per_region[region].loc[:, name] = df.loc[:, region]
        self._adoption_data = df_per_region


    def _min_max_sd(self, adoption_data, source, data_sources):
        """Return the min, max, and standard deviation for adoption data."""
        result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Min', 'Max', 'S.D'])
        result.loc[:, 'Min'] = adoption_data.min(axis=1)
        result.loc[:, 'Max'] = adoption_data.max(axis=1)

        columns = interpolation.matching_data_sources(data_sources=data_sources,
                                                      name=source, groups_only=False)
        if columns is None:
            result.loc[:, 'S.D'] = np.nan
        elif len(columns) > 1:
            # Excel STDDEV.P is a whole population stddev, ddof=0
            result.loc[:, 'S.D'] = adoption_data.loc[:, columns].std(axis=1, ddof=0)
        else:
            result.loc[:, 'S.D'] = adoption_data.std(axis=1, ddof=0)
        return result


    def _low_med_high(self, adoption_data, min_max_sd, adconfig, source, data_sources):
        """Return the selected data sources as Medium, and N stddev away as Low and High."""
        result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Low', 'Medium', 'High'])
        columns = interpolation.matching_data_sources(data_sources=data_sources,
                                                      name=source, groups_only=False)
        if columns is None:
            result.loc[:, 'Medium'] = np.nan
            result.loc[:, 'Low'] = np.nan
            result.loc[:, 'High'] = np.nan
        else:
            # In Excel, the Mean computation is:
            # SUM($C46:$Q46)/COUNTIF($C46:$Q46,">0")
            #
            # The intent is to skip sources which are empty, but also means that
            # a source where the real data is 0.0 will not impact the Medium result.
            #
            # See this document for more information:
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.yvwwsbvutw2j
            #
            # We're matching the Excel behavior in the initial product. This decision can
            # be revisited later, when matching results from Excel is no longer required.
            # To revert, use:    medium = adoption_data.loc[:, columns].mean(axis=1)
            medium = adoption_data.loc[:, columns].mask(lambda f: f == 0.0, np.nan).mean(axis=1)
            result.loc[:, 'Medium'] = medium
            result.loc[:, 'Low'] = medium - (min_max_sd.loc[:, 'S.D'] * adconfig.loc['low_sd_mult'])
            result.loc[:, 'High'] = medium + (
                min_max_sd.loc[:, 'S.D'] * adconfig.loc['high_sd_mult'])
        return result


    def _adoption_trend(self, low_med_high, growth, trend):
        """Adoption prediction via one of several interpolation algorithms."""
        if growth is None or trend is None:
            result = pd.DataFrame(np.nan, index=low_med_high.index.copy(), columns=['adoption'])
        else:
            data = low_med_high[growth]
            result = interpolation.trend_algorithm(data=data, trend=trend)
        return result


    def _get_data_sources(self, region):
        key = "Region: " + region
        return self.data_sources.get(key, self.data_sources)


    @lru_cache()
    def adoption_data(self, region):
        """Return adoption data for the given solution in the 'World' region.
           World: SolarPVUtil 'Adoption Data'!B45:R94
           OECD90: SolarPVUtil 'Adoption Data'!B105:R154
           Eastern Europe: SolarPVUtil 'Adoption Data'!B169:R218
           Asia (Sans Japan): SolarPVUtil 'Adoption Data'!B232:R281
           Middle East and Africa: SolarPVUtil 'Adoption Data'!B295:R344
           Latin America: SolarPVUtil 'Adoption Data'!B358:R407
           China: SolarPVUtil 'Adoption Data'!B421:R470
           India: SolarPVUtil 'Adoption Data'!B485:R534
           EU: SolarPVUtil 'Adoption Data'!B549:R598
           USA: SolarPVUtil 'Adoption Data'!B614:R663
        """
        return self._adoption_data[region]


    @lru_cache()
    def adoption_data_main_with_regional(self):
        """Return adoption data for the 'World' region with regional data added in.
           SolarPVUtil 'Adoption Data'!B45:R94 when B30:B31 are both 'Y' """
        main_region = dd.REGIONS[0]
        regional = pd.DataFrame(columns=dd.MAIN_REGIONS)
        for region in regional.columns:
            regional[region] = self.adoption_trend(region=region).loc[:, 'adoption']
        regional_sum = regional.sum(axis=1)
        regional_sum.name = 'RegionalSum'
        adoption = self.adoption_data(region=main_region).copy()
        adoption.loc[:, 'RegionalSum'] = np.nan
        adconfig = self.adconfig[main_region]
        if self.ac.soln_pds_adoption_prognostication_source == 'ALL SOURCES':
            adoption.update(regional_sum)
        return adoption


    @lru_cache()
    def adoption_min_max_sd(self, region):
        """Return the min, max, and standard deviation for the adoption data in the 'World' region.
           World: SolarPVUtil 'Adoption Data'!X45:Z94
           OECD90: SolarPVUtil 'Adoption Data'!X105:Z154
           Eastern Europe: SolarPVUtil 'Adoption Data'!X169:Z218
           Asia (Sans Japan): SolarPVUtil 'Adoption Data'!X232:Z281
           Middle East and Africa: SolarPVUtil 'Adoption Data'!X295:Z344
           Latin America: SolarPVUtil 'Adoption Data'!X358:Z407
           China: SolarPVUtil 'Adoption Data'!X421:Z470
           India: SolarPVUtil 'Adoption Data'!X485:Z534
           EU: SolarPVUtil 'Adoption Data'!X549:Z598
           USA: SolarPVUtil 'Adoption Data'!X614:Z663
        """
        data_sources = self._get_data_sources(region=region)
        main_region = dd.REGIONS[0]  # first columns, ex: 'World'
        if region == main_region:
            if self.main_includes_regional:
                adoption = self.adoption_data_main_with_regional()
                data_sources = data_sources.copy()
                data_sources.update({'RegionalSum': {'RegionalSum': ''}})
            else:
                adoption = self.adoption_data(region)
            source = self.ac.soln_pds_adoption_prognostication_source
        else:
            adoption = self.adoption_data(region)
            source = "ALL SOURCES"
        result = self._min_max_sd(adoption_data=adoption, source=source, data_sources=data_sources)
        result.name = 'adoption_min_max_sd_' + self._name_to_identifier(region)
        return result


    @lru_cache()
    def adoption_low_med_high(self, region):
        """Return the selected data sources as Medium, and N stddev away as Low and High.
           World: SolarPVUtil 'Adoption Data'!AB45:AD94
           OECD90: SolarPVUtil 'Adoption Data'!AB105:AD154
           Eastern Europe: SolarPVUtil 'Adoption Data'!AB169:AD218
           Asia (Sans Japan): SolarPVUtil 'Adoption Data'!AB232:AD281
           Middle East and Africa: SolarPVUtil 'Adoption Data'!AB295:AD344
           Latin America: SolarPVUtil 'Adoption Data'!AB358:AD407
           China: SolarPVUtil 'Adoption Data'!AB421:AD470
           India: SolarPVUtil 'Adoption Data'!AB485:AD534
           EU: SolarPVUtil 'Adoption Data'!AB549:AD598
           USA: SolarPVUtil 'Adoption Data'!AB614:AD663
        """
        data_sources = self._get_data_sources(region=region)
        main_region = dd.REGIONS[0]  # first columns, ex: 'World'
        if region == main_region:
            if self.main_includes_regional:
                adoption = self.adoption_data_main_with_regional()
                data_sources = data_sources.copy()
                data_sources.update({'RegionalSum': {'RegionalSum': ''}})
            else:
                adoption = self.adoption_data(region)
            source = self.ac.soln_pds_adoption_prognostication_source
        else:
            adoption = self.adoption_data(region=region)
            source = "ALL SOURCES"
        result = self._low_med_high(adoption_data=adoption,
                min_max_sd=self.adoption_min_max_sd(region), adconfig=self.adconfig[region],
                source=source, data_sources=data_sources)
        result.name = 'adoption_low_med_high_' + self._name_to_identifier(region)
        return result


    @lru_cache()
    def adoption_trend(self, region, trend=None):
        """Adoption prediction via one of several interpolation algorithms in the region.

           World:
           Linear: SolarPVUtil 'Adoption Data'!BY50:CA96     Degree2: 'Adoption Data'!CF50:CI96
           Degree3: SolarPVUtil 'Adoption Data'!CN50:CR96    Exponential: 'Adoption Data'!CW50:CY96

           OECD90:
           Linear: SolarPVUtil 'Adoption Data'!BY110:CA156     Degree2: 'Adoption Data'!CF110:CI156
           Degree3: SolarPVUtil 'Adoption Data'!CN110:CR156    Exponential: 'Adoption Data'!CW110:CY156

           Eastern Europe:
           Linear: SolarPVUtil 'Adoption Data'!BY174:CA220     Degree2: 'Adoption Data'!CF174:CI220
           Degree3: SolarPVUtil 'Adoption Data'!CN174:CR220    Exponential: 'Adoption Data'!CW174:CY220

           Asia (Sans Japan):
           Linear: SolarPVUtil 'Adoption Data'!BY237:CA283     Degree2: 'Adoption Data'!CF237:CI283
           Degree3: SolarPVUtil 'Adoption Data'!CN237:CR283    Exponential: 'Adoption Data'!CW237:CY283

           Latin America:
           Linear: SolarPVUtil 'Adoption Data'!BY363:CA409     Degree2: 'Adoption Data'!CF363:CI409
           Degree3: SolarPVUtil 'Adoption Data'!CN363:CR409    Exponential: 'Adoption Data'!CW363:CY409

           China:
           Linear: SolarPVUtil 'Adoption Data'!BY426:CA472     Degree2: 'Adoption Data'!CF426:CI472
           Degree3: SolarPVUtil 'Adoption Data'!CN426:CR472    Exponential: 'Adoption Data'!CW426:CY472

           India:
           Linear: SolarPVUtil 'Adoption Data'!BY490:CA536     Degree2: 'Adoption Data'!CF490:CI536
           Degree3: SolarPVUtil 'Adoption Data'!CN490:CR536    Exponential: 'Adoption Data'!CW490:CY536

           EU:
           Linear: SolarPVUtil 'Adoption Data'!BY554:CA600     Degree2: 'Adoption Data'!CF554:CI600
           Degree3: SolarPVUtil 'Adoption Data'!CN554:CR600    Exponential: 'Adoption Data'!CW554:CY600

           USA:
           Linear: SolarPVUtil 'Adoption Data'!BY619:CA665     Degree2: 'Adoption Data'!CF619:CI665
           Degree3: SolarPVUtil 'Adoption Data'!CN619:CR665    Exponential: 'Adoption Data'!CW619:CY665

        """
        main_region = dd.REGIONS[0]  # first columns, ex: 'World'
        if not trend:
            trend = self.adconfig.loc['trend', region]
        if region == main_region:
            growth = self.ac.soln_pds_adoption_prognostication_growth
        else:
            growth = self.adconfig.loc['growth', region]
        result = self._adoption_trend(self.adoption_low_med_high(region), growth, trend)
        result.name = 'adoption_trend_' + self._name_to_identifier(region) + '_' + str(trend).lower()
        return result

    @lru_cache()
    def adoption_is_single_source(self):
        """Whether the source data selected is one source or multiple."""
        return not interpolation.is_group_name(data_sources=self.data_sources,
                                               name=self.ac.soln_pds_adoption_prognostication_source)

    def _set_adoption_one_region(self, result, region, adoption_trend, adoption_low_med_high):
        result[region] = adoption_trend.loc[:, 'adoption']
        first_year = result.first_valid_index()
        result.loc[first_year, region] = adoption_low_med_high.loc[first_year, 'Medium']

    @lru_cache()
    def adoption_data_per_region(self):
        """Return a dataframe of adoption data, one column per region."""
        growth = self.ac.soln_pds_adoption_prognostication_growth
        main_region = dd.REGIONS[0]
        if growth is None:
            tmp = self.adoption_low_med_high(region=main_region)
            df = pd.DataFrame(np.nan, columns=dd.REGIONS, index=tmp.index)
        else:
            df = pd.DataFrame(columns=dd.REGIONS)
            for region in df.columns:
                df.loc[:, region] = self.adoption_low_med_high(region)[growth]
        df.name = 'adoption_data_per_region'
        return df

    @lru_cache()
    def adoption_trend_per_region(self):
        """Return a dataframe of adoption trends, one column per region."""
        df = pd.DataFrame(columns=dd.REGIONS)
        for region in df.columns:
            df[region] = self.adoption_trend(region=region)['adoption']
        return df
