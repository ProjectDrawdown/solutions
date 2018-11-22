"""Adoption Data module."""

import math
import os

import data_sources
from model import interpolation
import numpy as np
import pandas as pd
from statistics import mean

class AdoptionData:
  """Implements Adoption Data module."""
  def __init__(self, ac, datadir, adconfig):
    """Arguments:
         ac: advanced_controls.py
         datadir: path name to the directory to find data files.
         adconfig: Pandas dataframe with columns:
           'trend', 'growth', 'low_sd_mult', 'high_sd_mult'
           and rows for each region:
           'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
           'Latin America', 'China', 'India', 'EU', 'USA'
    """
    self.ac = ac
    self.datadir = datadir
    self.adconfig = adconfig
    super()

  def adoption_data_global(self):
    """Return adoption data for the given solution in the 'World' region.
       'Adoption Data'!B45:R94
    """
    filename = os.path.join(self.datadir, 'adoption_data.csv')
    result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.index = result.index.astype(int)
    result.name = 'adoption_data_global'
    return result

  def adoption_min_max_sd_global(self):
    """Return the min, max, and standard deviation for the adoption data in the 'World' region.
       'Adoption Data'!X45:Z94
    """
    adoption_data = self.adoption_data_global()
    result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Min', 'Max', 'S.D'])
    result.loc[:, 'Min'] = adoption_data.min(axis=1)
    result.loc[:, 'Max'] = adoption_data.max(axis=1)
    # Excel STDDEV.P is a whole population stddev, ddof=0
    result.loc[:, 'S.D'] = adoption_data.std(axis=1, ddof=0)
    result.name = 'adoption_min_max_sd_global'
    return result

  def adoption_low_med_high_global(self):
    """Return the selected data sources as Medium, and N stddev away as Low and High.
       'Adoption Data'!AB45:AD94
    """
    adoption_data = self.adoption_data_global()
    result = pd.DataFrame(index=adoption_data.index.copy(), columns=['Low', 'Medium', 'High'])
    columns = data_sources.matching_columns(
        adoption_data.columns, self.ac.soln_pds_adoption_prognostication_source)
    medium = adoption_data.loc[:, columns].mean(axis=1)
    result.loc[:, 'Medium'] = medium

    low_sd_mult = self.adconfig.loc['low_sd_mult', 'World']
    high_sd_mult = self.adconfig.loc['high_sd_mult', 'World']
    adoption_min_max_sd = self.adoption_min_max_sd_global()
    result.loc[:, 'Low'] = medium - (adoption_min_max_sd.loc[:, 'S.D'] * low_sd_mult)
    result.loc[:, 'High'] = medium + (adoption_min_max_sd.loc[:, 'S.D'] * high_sd_mult)
    result.name = 'adoption_low_med_high_global'
    return result

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
