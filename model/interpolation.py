"""Implements different interoplation methods:
     * linear
     * 2nd order polynomial
     * 3rd order polynomial
     * exponential

  This Python file does not correspond to one of the modules in the original
  Excel implementation of the models. It provides the implementation for
  interpolation methods used in the Adoption Data and TAM Data modules.
"""

import math
import numpy as np
import pandas as pd

def linear_trend(data):
  """Linear trend model.
     Provides implementation for 'Adoption Data'!BY50:CA96 & 'TAM Data' columns BX:BZ
     Arguments: data is a pd.Series used to provide the x+y for curve fitting.
  """
  result = pd.DataFrame(np.nan, index=np.arange(2014, 2061), columns=['x', 'constant', 'adoption'],
      dtype=np.float64)
  result.index.name = 'Year'
  if data.dropna().empty: return result
  y = data.dropna().values
  x = data.dropna().index - 2014
  if x.size == 0 or y.size == 0: return result
  (slope, intercept) = np.polyfit(x, y, 1)
  for (offset, index) in enumerate(result.index):
    result.loc[index, 'x'] = offset * slope
    result.loc[index, 'constant'] = intercept
    result.loc[index, 'adoption'] = sum(result.loc[index, result.columns != 'adoption'])
  return result

def poly_degree2_trend(data):
  """2nd degree polynomial trend model.
     Provides implementation for 'Adoption Data'!CF50:CI96 & 'TAM Data' columns CE:CH
     Arguments: data is a pd.Series used to provide the x+y for curve fitting.
  """
  result = pd.DataFrame(np.nan, index=np.arange(2014, 2061),
      columns=['x^2', 'x', 'constant', 'adoption'], dtype=np.float64)
  result.index.name = 'Year'
  if data.dropna().empty: return result
  y = data.dropna().values
  x = data.dropna().index - 2014
  if x.size == 0 or y.size == 0: return result
  (c2, c1, intercept) = np.polyfit(x, y, 2)
  for (offset, index) in enumerate(result.index):
    result.loc[index, 'x^2'] = (offset**2) * c2
    result.loc[index, 'x'] = offset * c1
    result.loc[index, 'constant'] = intercept
    result.loc[index, 'adoption'] = sum(result.loc[index, result.columns != 'adoption'])
  return result

def poly_degree3_trend(data):
  """3rd degree polynomial trend model.
     Provides implementation for 'Adoption Data'!CN50:CR96 & 'TAM Data' columns CM:CQ
     Arguments: data is a pd.Series used to provide the x+y for curve fitting.
  """
  result = pd.DataFrame(np.nan, index=np.arange(2014, 2061),
      columns=['x^3', 'x^2', 'x', 'constant', 'adoption'], dtype=np.float64)
  result.index.name = 'Year'
  if data.dropna().empty: return result
  y = data.dropna().values
  x = data.dropna().index - 2014
  if x.size == 0 or y.size == 0: return result
  (c3, c2, c1, intercept) = np.polyfit(x, y, 3)
  for (offset, index) in enumerate(result.index):
    result.loc[index, 'x^3'] = (offset**3) * c3
    result.loc[index, 'x^2'] = (offset**2) * c2
    result.loc[index, 'x'] = offset * c1
    result.loc[index, 'constant'] = intercept
    result.loc[index, 'adoption'] = sum(result.loc[index, result.columns != 'adoption'])
  return result

def exponential_trend(data):
  """exponential trend model.
     Provides implementation for 'Adoption Data'!CW50:CY96 & 'TAM Data' columns CV:CX
     Arguments: data is a pd.Series used to provide the x+y for curve fitting.
  """
  result = pd.DataFrame(np.nan, index=np.arange(2014, 2061),
      columns=['coeff', 'e^x', 'adoption'], dtype=np.float64)
  result.index.name = 'Year'
  if data.dropna().empty: return result
  y = np.log(data.dropna().values)
  x = data.dropna().index - 2014
  if x.size == 0 or y.size == 0: return result
  (ce, coeff) = np.polyfit(x, y, 1)
  for (offset, index) in enumerate(result.index):
    result.loc[index, 'coeff'] = math.exp(coeff)
    result.loc[index, 'e^x'] = math.exp(ce * offset)
    result.loc[index, 'adoption'] = result.loc[index, 'coeff'] * result.loc[index, 'e^x']
  return result

def single_trend(data):
  """Single source model.
     Returns the data from the single source, packaged into a DataFrame compatible
     with the other trend algorithms.
  """
  result = pd.DataFrame(0, index=np.arange(2014, 2061),
      columns=['constant', 'adoption'], dtype=np.float64)
  result.index.name = 'Year'
  result.loc[:, 'constant'] = data.dropna()
  result.loc[:, 'adoption'] = data.dropna()
  return result

def trend_algorithm(data, trend):
  """Fit of data via one of several trend interpolation algorithms."""
  t = trend.lower()
  if t == "linear": return linear_trend(data=data)
  if t == "2nd poly" or t == "2nd_poly" or t == "degree2":
    return poly_degree2_trend(data=data)
  if t == "3rd poly" or t == "3rd_poly" or t == "degree3":
    return poly_degree3_trend(data=data)
  if t == "exponential" or t == "exp":
    return exponential_trend(data=data)
  if t == "single" or t == "single source":
    return single_trend(data)
  raise ValueError('invalid trend algorithm: ' + str(trend))

def matching_data_sources(data_sources, name, groups_only):
  """Return a list of data sources which match name.
     If name is a group, return all data sources which are part of that group.
     If name is an individual case and groups_only=False, return it by itself.
     If groups_only=True and name is not a group, return all sources.

     Arguments:
       data_sources: a dict() of group names which contain dicts of data source names.
         Used for Total Addressable Market and adoption calculations. For example:
         {
           'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...}
           'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...}
           'Conservative Cases': {'Study Name E': 'filename E', 'Study Name F': 'filename F', ...}
         }
       name: a name of an individual data source, or the name of a group
         like 'Ambitious Cases'
       groups_only: only return a group, or all columns if no group is found.
         This is typically useful for stddev calculations, which are never done
         (and are nonsensical) on an individual data source only on a single
         group or over all sources.
  """
  if name is None or pd.isna(name):
    return None
  if name in data_sources:
    return list(data_sources[name].keys())
  all_sources = []
  for val in data_sources.values():
    all_sources.extend(list(val.keys()))
  if name.lower() == 'all sources':
    return all_sources
  if groups_only:  # specific group not found above, so return all
    return all_sources
  if name in all_sources:
    return [name]
  raise ValueError("No such data source: " + str(name))

def is_group_name(data_sources, name):
  """Return True if name is a group in data_sources."""
  if name in data_sources:
    return True
  if name is None or pd.isna(name):
    return False
  if name.lower() == "all sources":
    return True
  all_sources = []
  for val in data_sources.values():
    all_sources.extend(list(val.keys()))
  if name in all_sources:
    return False
  raise ValueError("No such data source: " + str(name))
