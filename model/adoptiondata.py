"""Adoption Data module."""

from functools import lru_cache
import math
import pathlib
import os

from model import interpolation
from model import metaclass_cache
import numpy as np
import pandas as pd
from statistics import mean

class AdoptionData(object, metaclass=metaclass_cache.MetaclassCache):
  REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
          'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA']

  """Implements Adoption Data module."""
  def __init__(self, ac, data_sources, adconfig):
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
    """
    self.ac = ac
    self.data_sources = data_sources
    self.adconfig = adconfig
    self._populate_adoption_data()

  def _populate_adoption_data(self):
    """Read data files in self.data_sources to populate adoption data."""
    self._adoption_data_global = pd.DataFrame()
    self._adoption_data_global.name = 'adoption_data_global'
    self._adoption_data_oecd90 = pd.DataFrame()
    self._adoption_data_oecd90.name = 'adoption_data_oecd90'
    self._adoption_data_eastern_europe = pd.DataFrame()
    self._adoption_data_eastern_europe.name = 'adoption_data_eastern_europe'
    self._adoption_data_asia_sans_japan = pd.DataFrame()
    self._adoption_data_asia_sans_japan.name = 'adoption_data_asia_sans_japan'
    self._adoption_data_middle_east_and_africa = pd.DataFrame()
    self._adoption_data_middle_east_and_africa.name = 'adoption_data_middle_east_and_africa'
    self._adoption_data_latin_america = pd.DataFrame()
    self._adoption_data_latin_america.name = 'adoption_data_latin_america'
    self._adoption_data_china = pd.DataFrame()
    self._adoption_data_china.name = 'adoption_data_china'
    self._adoption_data_india = pd.DataFrame()
    self._adoption_data_india.name = 'adoption_data_india'
    self._adoption_data_eu = pd.DataFrame()
    self._adoption_data_eu.name = 'adoption_data_eu'
    self._adoption_data_usa = pd.DataFrame()
    self._adoption_data_usa.name = 'adoption_data_usa'
    for (groupname, group) in self.data_sources.items():
      for (name, value) in group.items():
        if isinstance(value, str) or isinstance(value, pathlib.Path) or isinstance(value, pathlib.PurePath):
          sources = {name: value}
        else:
          sources = value
        for name, filename in sources.items():
          df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
            skip_blank_lines=True, comment='#')
          self._adoption_data_global.loc[:, name] = df.loc[:, 'World']
          self._adoption_data_oecd90.loc[:, name] = df.loc[:, 'OECD90']
          self._adoption_data_eastern_europe.loc[:, name] = df.loc[:, 'Eastern Europe']
          self._adoption_data_asia_sans_japan.loc[:, name] = df.loc[:, 'Asia (Sans Japan)']
          self._adoption_data_middle_east_and_africa.loc[:, name] = df.loc[:, 'Middle East and Africa']
          self._adoption_data_latin_america.loc[:, name] = df.loc[:, 'Latin America']
          self._adoption_data_china.loc[:, name] = df.loc[:, 'China']
          self._adoption_data_india.loc[:, name] = df.loc[:, 'India']
          self._adoption_data_eu.loc[:, name] = df.loc[:, 'EU']
          self._adoption_data_usa.loc[:, name] = df.loc[:, 'USA']

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
      medium = adoption_data.loc[:, columns].mean(axis=1)
      result.loc[:, 'Medium'] = medium
      result.loc[:, 'Low'] = medium - (min_max_sd.loc[:, 'S.D'] * adconfig.loc['low_sd_mult'])
      result.loc[:, 'High'] = medium + (min_max_sd.loc[:, 'S.D'] * adconfig.loc['high_sd_mult'])
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
  def adoption_data_global(self):
    """Return adoption data for the given solution in the 'World' region.
       SolarPVUtil 'Adoption Data'!B45:R94
    """
    return self._adoption_data_global

  @lru_cache()
  def adoption_min_max_sd_global(self):
    """Return the min, max, and standard deviation for the adoption data in the 'World' region.
       SolarPVUtil 'Adoption Data'!X45:Z94
    """
    result = self._min_max_sd(self.adoption_data_global(),
        source=self.ac.soln_pds_adoption_prognostication_source,
        data_sources=self._get_data_sources(region='World'))
    result.name = 'adoption_min_max_sd_global'
    return result

  @lru_cache()
  def adoption_low_med_high_global(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB45:AD94
    """
    result = self._low_med_high(self.adoption_data_global(),
        self.adoption_min_max_sd_global(), self.adconfig['World'],
        source=self.ac.soln_pds_adoption_prognostication_source,
        data_sources=self._get_data_sources(region='World'))
    result.name = 'adoption_low_med_high_global'
    return result

  @lru_cache()
  def adoption_trend_global(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'World' region.
       Linear: SolarPVUtil 'Adoption Data'!BY50:CA96     Degree2: 'Adoption Data'!CF50:CI96
       Degree3: SolarPVUtil 'Adoption Data'!CN50:CR96    Exponential: 'Adoption Data'!CW50:CY96
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'World']
    growth = self.ac.soln_pds_adoption_prognostication_growth
    result = self._adoption_trend(self.adoption_low_med_high_global(), growth, trend)
    result.name = 'adoption_trend_global_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_oecd90(self):
    """Return adoption data for the given solution in the 'OECD90' region.
       SolarPVUtil 'Adoption Data'!B105:R154
    """
    return self._adoption_data_oecd90

  @lru_cache()
  def adoption_min_max_sd_oecd90(self):
    """Return the min, max, and standard deviation for the adoption data in the 'OECD90' region.
       SolarPVUtil 'Adoption Data'!X105:Z154
    """
    result = self._min_max_sd(self.adoption_data_oecd90(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='OECD90'))
    result.name = 'adoption_min_max_sd_oecd90'
    return result

  @lru_cache()
  def adoption_low_med_high_oecd90(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB105:AD154
    """
    result = self._low_med_high(self.adoption_data_oecd90(),
        self.adoption_min_max_sd_oecd90(), self.adconfig['OECD90'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='OECD90'))
    result.name = 'adoption_low_med_high_oecd90'
    return result

  @lru_cache()
  def adoption_trend_oecd90(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'OECD90' region.
       Linear: SolarPVUtil 'Adoption Data'!BY110:CA156     Degree2: 'Adoption Data'!CF110:CI156
       Degree3: SolarPVUtil 'Adoption Data'!CN110:CR156    Exponential: 'Adoption Data'!CW110:CY156
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'OECD90']
    growth = self.adconfig.loc['growth', 'OECD90']
    result = self._adoption_trend(self.adoption_low_med_high_oecd90(), growth, trend)
    result.name = 'adoption_trend_oecd90_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_eastern_europe(self):
    """Return adoption data for the given solution in the 'Eastern Europe' region.
       SolarPVUtil 'Adoption Data'!B169:R218
    """
    return self._adoption_data_eastern_europe

  @lru_cache()
  def adoption_min_max_sd_eastern_europe(self):
    """Return the min, max, and standard deviation for the adoption data in the 'Eastern Europe' region.
       SolarPVUtil 'Adoption Data'!X169:Z218
    """
    result = self._min_max_sd(self.adoption_data_eastern_europe(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='Eastern Europe'))
    result.name = 'adoption_min_max_sd_eastern_europe'
    return result

  @lru_cache()
  def adoption_low_med_high_eastern_europe(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB169:AD218
    """
    result = self._low_med_high(self.adoption_data_eastern_europe(),
        self.adoption_min_max_sd_eastern_europe(), self.adconfig['Eastern Europe'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='Eastern Europe'))
    result.name = 'adoption_low_med_high_eastern_europe'
    return result

  @lru_cache()
  def adoption_trend_eastern_europe(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'Eastern Europe' region.
       Linear: SolarPVUtil 'Adoption Data'!BY174:CA220     Degree2: 'Adoption Data'!CF174:CI220
       Degree3: SolarPVUtil 'Adoption Data'!CN174:CR220    Exponential: 'Adoption Data'!CW174:CY220
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'Eastern Europe']
    growth = self.adconfig.loc['growth', 'Eastern Europe']
    result = self._adoption_trend(self.adoption_low_med_high_eastern_europe(), growth, trend)
    result.name = 'adoption_trend_eastern_europe_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_asia_sans_japan(self):
    """Return adoption data for the given solution in the 'Asia (Sans Japan)' region.
       SolarPVUtil 'Adoption Data'!B232:R281
    """
    return self._adoption_data_asia_sans_japan

  @lru_cache()
  def adoption_min_max_sd_asia_sans_japan(self):
    """Return the min, max, and standard deviation for the adoption data in the 'Asia (Sans Japan)' region.
       SolarPVUtil 'Adoption Data'!X232:Z281
    """
    result = self._min_max_sd(self.adoption_data_asia_sans_japan(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='Asia (Sans Japan)'))
    result.name = 'adoption_min_max_sd_asia_sans_japan'
    return result

  @lru_cache()
  def adoption_low_med_high_asia_sans_japan(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB232:AD281
    """
    result = self._low_med_high(self.adoption_data_asia_sans_japan(),
        self.adoption_min_max_sd_asia_sans_japan(), self.adconfig['Asia (Sans Japan)'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='Asia (Sans Japan)'))
    result.name = 'adoption_low_med_high_asia_sans_japan'
    return result

  @lru_cache()
  def adoption_trend_asia_sans_japan(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'Asia (Sans Japan)' region.
       Linear: SolarPVUtil 'Adoption Data'!BY237:CA283     Degree2: 'Adoption Data'!CF237:CI283
       Degree3: SolarPVUtil 'Adoption Data'!CN237:CR283    Exponential: 'Adoption Data'!CW237:CY283
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'Asia (Sans Japan)']
    growth = self.adconfig.loc['growth', 'Asia (Sans Japan)']
    result = self._adoption_trend(self.adoption_low_med_high_asia_sans_japan(), growth, trend)
    result.name = 'adoption_trend_asia_sans_japan_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_middle_east_and_africa(self):
    """Return adoption data for the given solution in the 'Middle East and Africa' region.
       SolarPVUtil 'Adoption Data'!B295:R344
    """
    return self._adoption_data_middle_east_and_africa

  @lru_cache()
  def adoption_min_max_sd_middle_east_and_africa(self):
    """Return the min, max, and standard deviation for the adoption data in the 'Middle East and Africa' region.
       SolarPVUtil 'Adoption Data'!X295:Z344
    """
    result = self._min_max_sd(self.adoption_data_middle_east_and_africa(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='Middle East and Africa'))
    result.name = 'adoption_min_max_sd_middle_east_and_africa'
    return result

  @lru_cache()
  def adoption_low_med_high_middle_east_and_africa(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB295:AD344
    """
    result = self._low_med_high(self.adoption_data_middle_east_and_africa(),
        self.adoption_min_max_sd_middle_east_and_africa(), self.adconfig['Middle East and Africa'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='Middle East and Africa'))
    result.name = 'adoption_low_med_high_middle_east_and_africa'
    return result

  @lru_cache()
  def adoption_trend_middle_east_and_africa(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'Middle East and Africa' region.
       Linear: SolarPVUtil 'Adoption Data'!BY300:CA346     Degree2: 'Adoption Data'!CF300:CI346
       Degree3: SolarPVUtil 'Adoption Data'!CN300:CR346    Exponential: 'Adoption Data'!CW300:CY346
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'Middle East and Africa']
    growth = self.adconfig.loc['growth', 'Middle East and Africa']
    result = self._adoption_trend(self.adoption_low_med_high_middle_east_and_africa(), growth, trend)
    result.name = 'adoption_trend_middle_east_and_africa_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_latin_america(self):
    """Return adoption data for the given solution in the 'Latin America' region.
       SolarPVUtil 'Adoption Data'!B358:R407
    """
    return self._adoption_data_latin_america

  @lru_cache()
  def adoption_min_max_sd_latin_america(self):
    """Return the min, max, and standard deviation for the adoption data in the 'Latin America' region.
       SolarPVUtil 'Adoption Data'!X358:Z407
    """
    result = self._min_max_sd(self.adoption_data_latin_america(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='Latin America'))
    result.name = 'adoption_min_max_sd_latin_america'
    return result

  @lru_cache()
  def adoption_low_med_high_latin_america(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB358:AD407
    """
    result = self._low_med_high(self.adoption_data_latin_america(),
        self.adoption_min_max_sd_latin_america(), self.adconfig['Latin America'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='Latin America'))
    result.name = 'adoption_low_med_high_latin_america'
    return result

  @lru_cache()
  def adoption_trend_latin_america(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'Latin America' region.
       Linear: SolarPVUtil 'Adoption Data'!BY363:CA409     Degree2: 'Adoption Data'!CF363:CI409
       Degree3: SolarPVUtil 'Adoption Data'!CN363:CR409    Exponential: 'Adoption Data'!CW363:CY409
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'Latin America']
    growth = self.adconfig.loc['growth', 'Latin America']
    result = self._adoption_trend(self.adoption_low_med_high_latin_america(), growth, trend)
    result.name = 'adoption_trend_latin_america_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_china(self):
    """Return adoption data for the given solution in the 'China' region.
       SolarPVUtil 'Adoption Data'!B421:R470
    """
    return self._adoption_data_china

  @lru_cache()
  def adoption_min_max_sd_china(self):
    """Return the min, max, and standard deviation for the adoption data in the 'China' region.
       SolarPVUtil 'Adoption Data'!X421:Z470
    """
    result = self._min_max_sd(self.adoption_data_china(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='China'))
    result.name = 'adoption_min_max_sd_china'
    return result

  @lru_cache()
  def adoption_low_med_high_china(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB421:AD470
    """
    result = self._low_med_high(self.adoption_data_china(),
        self.adoption_min_max_sd_china(), self.adconfig['China'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='China'))
    result.name = 'adoption_low_med_high_china'
    return result

  @lru_cache()
  def adoption_trend_china(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'China' region.
       Linear: SolarPVUtil 'Adoption Data'!BY426:CA472     Degree2: 'Adoption Data'!CF426:CI472
       Degree3: SolarPVUtil 'Adoption Data'!CN426:CR472    Exponential: 'Adoption Data'!CW426:CY472
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'China']
    growth = self.adconfig.loc['growth', 'China']
    result = self._adoption_trend(self.adoption_low_med_high_china(), growth, trend)
    result.name = 'adoption_trend_china_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_india(self):
    """Return adoption data for the given solution in the 'India' region.
       SolarPVUtil 'Adoption Data'!B485:R534
    """
    return self._adoption_data_india

  @lru_cache()
  def adoption_min_max_sd_india(self):
    """Return the min, max, and standard deviation for the adoption data in the 'India' region.
       SolarPVUtil 'Adoption Data'!X485:Z534
    """
    result = self._min_max_sd(self.adoption_data_india(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='India'))
    result.name = 'adoption_min_max_sd_india'
    return result

  @lru_cache()
  def adoption_low_med_high_india(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB485:AD534
    """
    result = self._low_med_high(self.adoption_data_india(),
        self.adoption_min_max_sd_india(), self.adconfig['India'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='India'))
    result.name = 'adoption_low_med_high_india'
    return result

  @lru_cache()
  def adoption_trend_india(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'India' region.
       Linear: SolarPVUtil 'Adoption Data'!BY490:CA536     Degree2: 'Adoption Data'!CF490:CI536
       Degree3: SolarPVUtil 'Adoption Data'!CN490:CR536    Exponential: 'Adoption Data'!CW490:CY536
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'India']
    growth = self.adconfig.loc['growth', 'India']
    result = self._adoption_trend(self.adoption_low_med_high_india(), growth, trend)
    result.name = 'adoption_trend_india_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_eu(self):
    """Return adoption data for the given solution in the 'EU' region.
       SolarPVUtil 'Adoption Data'!B549:R598
    """
    return self._adoption_data_eu

  @lru_cache()
  def adoption_min_max_sd_eu(self):
    """Return the min, max, and standard deviation for the adoption data in the 'EU' region.
       SolarPVUtil 'Adoption Data'!X549:Z598
    """
    result = self._min_max_sd(self.adoption_data_eu(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='EU'))
    result.name = 'adoption_min_max_sd_eu'
    return result

  @lru_cache()
  def adoption_low_med_high_eu(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB549:AD598
    """
    result = self._low_med_high(self.adoption_data_eu(),
        self.adoption_min_max_sd_eu(), self.adconfig['EU'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='EU'))
    result.name = 'adoption_low_med_high_eu'
    return result

  @lru_cache()
  def adoption_trend_eu(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'EU' region.
       Linear: SolarPVUtil 'Adoption Data'!BY554:CA600     Degree2: 'Adoption Data'!CF554:CI600
       Degree3: SolarPVUtil 'Adoption Data'!CN554:CR600    Exponential: 'Adoption Data'!CW554:CY600
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'EU']
    growth = self.adconfig.loc['growth', 'EU']
    result = self._adoption_trend(self.adoption_low_med_high_eu(), growth, trend)
    result.name = 'adoption_trend_eu_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_data_usa(self):
    """Return adoption data for the given solution in the 'USA' region.
       SolarPVUtil 'Adoption Data'!B614:R663
    """
    return self._adoption_data_usa

  @lru_cache()
  def adoption_min_max_sd_usa(self):
    """Return the min, max, and standard deviation for the adoption data in the 'USA' region.
       SolarPVUtil 'Adoption Data'!X614:Z663
    """
    result = self._min_max_sd(self.adoption_data_usa(), source="ALL SOURCES",
        data_sources=self._get_data_sources(region='USA'))
    result.name = 'adoption_min_max_sd_usa'
    return result

  @lru_cache()
  def adoption_low_med_high_usa(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       SolarPVUtil 'Adoption Data'!AB614:AD663
    """
    result = self._low_med_high(self.adoption_data_usa(),
        self.adoption_min_max_sd_usa(), self.adconfig['USA'],
        source="ALL SOURCES", data_sources=self._get_data_sources(region='USA'))
    result.name = 'adoption_low_med_high_usa'
    return result

  @lru_cache()
  def adoption_trend_usa(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'USA' region.
       Linear: SolarPVUtil 'Adoption Data'!BY619:CA665     Degree2: 'Adoption Data'!CF619:CI665
       Degree3: SolarPVUtil 'Adoption Data'!CN619:CR665    Exponential: 'Adoption Data'!CW619:CY665
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'USA']
    growth = self.adconfig.loc['growth', 'USA']
    result = self._adoption_trend(self.adoption_low_med_high_usa(), growth, trend)
    result.name = 'adoption_trend_usa_' + str(trend).lower()
    return result

  @lru_cache()
  def adoption_is_single_source(self):
    """Whether the source data selected is one source or multiple."""
    return not interpolation.is_group_name(data_sources=self.data_sources,
        name=self.ac.soln_pds_adoption_prognostication_source)

  @lru_cache()
  def adoption_data_per_region(self):
    """Return a dataframe of adoption data, one column per region."""
    growth = self.ac.soln_pds_adoption_prognostication_growth
    if growth is None:
      tmp = self.adoption_low_med_high_global()
      df = pd.DataFrame(np.nan, columns=self.REGIONS, index=tmp.index)
    else:
      df = pd.DataFrame(columns=self.REGIONS)
      df.loc[:, 'World'] = self.adoption_low_med_high_global()[growth]
      df.loc[:, 'OECD90'] = self.adoption_low_med_high_oecd90()[growth]
      df.loc[:, 'Eastern Europe'] = self.adoption_low_med_high_eastern_europe()[growth]
      df.loc[:, 'Asia (Sans Japan)'] = self.adoption_low_med_high_asia_sans_japan()[growth]
      df.loc[:, 'Middle East and Africa'] = self.adoption_low_med_high_middle_east_and_africa()[growth]
      df.loc[:, 'Latin America'] = self.adoption_low_med_high_latin_america()[growth]
      df.loc[:, 'China'] = self.adoption_low_med_high_china()[growth]
      df.loc[:, 'India'] = self.adoption_low_med_high_india()[growth]
      df.loc[:, 'EU'] = self.adoption_low_med_high_eu()[growth]
      df.loc[:, 'USA'] = self.adoption_low_med_high_usa()[growth]
    df.name = 'adoption_data_per_region'
    return df

  @lru_cache()
  def adoption_trend_per_region(self):
    """Return a dataframe of adoption trends, one column per region."""
    df = pd.DataFrame(columns=self.REGIONS)
    df['World'] = self.adoption_trend_global()['adoption']
    df['OECD90'] = self.adoption_trend_oecd90()['adoption']
    df['Eastern Europe'] = self.adoption_trend_eastern_europe()['adoption']
    df['Asia (Sans Japan)'] = self.adoption_trend_asia_sans_japan()['adoption']
    df['Middle East and Africa'] = self.adoption_trend_middle_east_and_africa()['adoption']
    df['Latin America'] = self.adoption_trend_latin_america()['adoption']
    df['China'] = self.adoption_trend_china()['adoption']
    df['India'] = self.adoption_trend_india()['adoption']
    df['EU'] = self.adoption_trend_eu()['adoption']
    df['USA'] = self.adoption_trend_usa()['adoption']
    return df
