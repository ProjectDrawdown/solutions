"""Adoption Data module.

   Implements different interoplation methods:
     * linear
     * 2nd order polynomial
     * 3rd order polynomial
     * exponential
"""

import math
import os
import numpy as np
import pandas as pd
from statistics import mean

model_dir = os.path.dirname(__file__)
solution_dir = os.path.join(os.path.dirname(model_dir), 'solution')

def adoption(adoption_data_filename):
  """Return adoption data for the given solution.
     'Adoption Data'!B45:R94
  """
  filename = os.path.join(solution_dir, adoption_data_filename)
  result = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True, comment='#')
  result.index = result.index.astype(int)
  return result

def adoption_min_max_sd(adoption):
  """Return the min, max, and standard deviation for the adoption data.
     'Adoption Data'!X45:Z94
  """
  result = pd.DataFrame(index=adoption.index.copy(), columns=['Min', 'Max', 'S.D'])
  result.loc[:, 'Min'] = adoption.min(axis=1)
  result.loc[:, 'Max'] = adoption.max(axis=1)
  # Excel STDDEV.P is a whole population stddev, ddof=0
  result.loc[:, 'S.D'] = adoption.std(axis=1, ddof=0)
  return result

def adoption_low_med_high(adoption, adoption_prognostication_source,
    adoption_min_max_sd, low_sd, high_sd):
  """Return the selected data sources as Medium, and N stddev away as Low and High.
     'Adoption Data'!AB45:AD94

     adoption: DataFrame of all of the data sources, source name as the column name.
     adoption_prognostication_source: list of column names from adoption[] to use.
     adoption_min_max_sd: DataFrame with columns for the Minimum, Maxiumum, and Standard deviation.
     low_sd, high_sd: number of standard deviations away for Low and High.
  """
  result = pd.DataFrame(index=adoption.index.copy(), columns=['Low', 'Medium', 'High'])
  result.loc[:, 'Medium'] = adoption.loc[:, adoption_prognostication_source]
  result.loc[:, 'Low'] = result.loc[:, 'Medium'] - (adoption_min_max_sd.loc[:, 'S.D'] * low_sd)
  result.loc[:, 'High'] = result.loc[:, 'Medium'] + (adoption_min_max_sd.loc[:, 'S.D'] * high_sd)
  return result
