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
  y = data.values
  x = data.index.copy() - 2014
  (slope, intercept) = np.polyfit(x, y, 1)
  result = pd.DataFrame(0, index=np.arange(2014, 2061), columns=['x', 'constant', 'adoption'],
      dtype=np.float64)
  result.index.name = 'Year'
  for (offset, index) in enumerate(result.index):
    result.loc[index, 'x'] = offset * slope
    result.loc[index, 'constant'] = intercept
    result.loc[index, 'adoption'] = sum(result.loc[index])
  return result

def poly_degree2_trend(data):
  """2nd degree polynomial trend model.
     Provides implementation for 'Adoption Data'!CF50:CI96 & 'TAM Data' columns CE:CH
     Arguments: data is a pd.Series used to provide the x+y for curve fitting.
  """
  y = data.values
  x = data.index.copy() - 2014
  (c2, c1, intercept) = np.polyfit(x, y, 2)
  result = pd.DataFrame(0, index=np.arange(2014, 2061),
      columns=['x^2', 'x', 'constant', 'adoption'], dtype=np.float64)
  result.index.name = 'Year'
  for (offset, index) in enumerate(result.index):
    result.loc[index, 'x^2'] = (offset**2) * c2
    result.loc[index, 'x'] = offset * c1
    result.loc[index, 'constant'] = intercept
    result.loc[index, 'adoption'] = sum(result.loc[index])
  return result

def poly_degree3_trend(data):
  """3rd degree polynomial trend model.
     Provides implementation for 'Adoption Data'!CN50:CR96 & 'TAM Data' columns CM:CQ
     Arguments: data is a pd.Series used to provide the x+y for curve fitting.
  """
  y = data.values
  x = data.index.copy() - 2014
  (c3, c2, c1, intercept) = np.polyfit(x, y, 3)
  result = pd.DataFrame(0, index=np.arange(2014, 2061),
      columns=['x^3', 'x^2', 'x', 'constant', 'adoption'], dtype=np.float64)
  result.index.name = 'Year'
  for (offset, index) in enumerate(result.index):
    result.loc[index, 'x^3'] = (offset**3) * c3
    result.loc[index, 'x^2'] = (offset**2) * c2
    result.loc[index, 'x'] = offset * c1
    result.loc[index, 'constant'] = intercept
    result.loc[index, 'adoption'] = sum(result.loc[index])
  return result

def exponential_trend(data):
  """exponential trend model.
     Provides implementation for 'Adoption Data'!CW50:CY96 & 'TAM Data' columns CV:CX
     Arguments: data is a pd.Series used to provide the x+y for curve fitting.
  """
  y = np.log(data.values)
  x = data.index.copy() - 2014
  (ce, coeff) = np.polyfit(x, y, 1)
  result = pd.DataFrame(0, index=np.arange(2014, 2061),
      columns=['coeff', 'e^x', 'adoption'], dtype=np.float64)
  result.index.name = 'Year'
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
  result.loc[:, 'constant'] = data
  result.loc[:, 'adoption'] = data
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
