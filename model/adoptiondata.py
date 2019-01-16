"""Adoption Data module."""

from functools import lru_cache
import math
import os

from model import interpolation
import numpy as np
import pandas as pd
from statistics import mean

class AdoptionData:
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
    for (groupname, group) in self.data_sources.items():
      for (name, filename) in group.items():
        df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
          skip_blank_lines=True, comment='#')
        self._adoption_data_global.loc[:, name] = df.loc[:, 'World']

  @lru_cache()
  def adoption_data_global(self):
    """Return adoption data for the given solution in the 'World' region.
       'Adoption Data'!B45:R94
    """
    return self._adoption_data_global

  @lru_cache()
  def adoption_min_max_sd_global(self):
    """Return the min, max, and standard deviation for the adoption data in the 'World' region.
       'Adoption Data'!X45:Z94
    """
    adoption_data = self.adoption_data_global()
    result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Min', 'Max', 'S.D'])
    result.loc[:, 'Min'] = adoption_data.min(axis=1)
    result.loc[:, 'Max'] = adoption_data.max(axis=1)

    columns = interpolation.matching_data_sources(data_sources=self.data_sources,
        name=self.ac.soln_pds_adoption_prognostication_source, groups_only=False)
    # Excel STDDEV.P is a whole population stddev, ddof=0
    if len(columns) > 1:
      result.loc[:, 'S.D'] = adoption_data.loc[:, columns].std(axis=1, ddof=0)
    else:
      result.loc[:, 'S.D'] = adoption_data.std(axis=1, ddof=0)

    result.name = 'adoption_min_max_sd_global'
    return result

  @lru_cache()
  def adoption_low_med_high_global(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       'Adoption Data'!AB45:AD94
    """
    adoption_data = self.adoption_data_global()
    result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Low', 'Medium', 'High'])
    columns = interpolation.matching_data_sources(data_sources=self.data_sources,
        name=self.ac.soln_pds_adoption_prognostication_source, groups_only=False)

    medium = adoption_data.loc[:, columns].mean(axis=1)
    result.loc[:, 'Medium'] = medium

    low_sd_mult = self.adconfig.loc['low_sd_mult', 'World']
    high_sd_mult = self.adconfig.loc['high_sd_mult', 'World']
    adoption_min_max_sd = self.adoption_min_max_sd_global()
    result.loc[:, 'Low'] = medium - (adoption_min_max_sd.loc[:, 'S.D'] * low_sd_mult)
    result.loc[:, 'High'] = medium + (adoption_min_max_sd.loc[:, 'S.D'] * high_sd_mult)
    result.name = 'adoption_low_med_high_global'
    return result

  @lru_cache()
  def adoption_trend_global(self, trend=None):
    """Adoption prediction via one of several interpolation algorithms in the 'World' region.
       Linear: 'Adoption Data'!BY50:CA96     Degree2: 'Adoption Data'!CF50:CI96
       Degree3: 'Adoption Data'!CN50:CR96    Exponential: 'Adoption Data'!CW50:CY96
    """
    if not trend:
      trend = self.adconfig.loc['trend', 'World']
    data = self.adoption_low_med_high_global()[self.adconfig.loc['growth', 'World']]
    result = interpolation.trend_algorithm(data=data, trend=trend)
    result.name = 'adoption_trend_global_' + trend.lower()
    return result

  @lru_cache()
  def adoption_is_single_source(self):
    """Whether the source data selected is one source or multiple."""
    return not interpolation.is_group_name(data_sources=self.data_sources,
        name=self.ac.soln_pds_adoption_prognostication_source)

  def to_dict(self):
    """Return all fields as a dict, to be serialized to JSON."""
    rs = dict()
    rs['adoption_data_global'] = self.adoption_data_global()
    rs['adoption_min_max_sd_global'] = self.adoption_min_max_sd_global()
    rs['adoption_low_med_high_global'] = self.adoption_low_med_high_global()
    rs['adoption_trend_linear_global'] = self.adoption_trend_global(trend='Linear')
    rs['adoption_trend_poly_degree2_global'] = self.adoption_trend_global(trend='Degree2')
    rs['adoption_trend_poly_degree3_global'] = self.adoption_trend_global(trend='Degree3')
    rs['adoption_trend_exponential_global'] = self.adoption_trend_global(trend='Exponential')
    return rs
