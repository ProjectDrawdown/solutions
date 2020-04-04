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

    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ["x", "constant", "adoption"]
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = data_clean.values
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (slope, intercept) = np.polyfit(x, y, 1)

    n_years = len(years)
    offsets = np.arange(n_years)

    x = offsets * slope
    constant = np.full(n_years, intercept)
    adoption = x + constant

    return pd.DataFrame(np.column_stack([x,constant, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)

def poly_degree2_trend(data):
    """2nd degree polynomial trend model.
       Provides implementation for 'Adoption Data'!CF50:CI96 & 'TAM Data' columns CE:CH
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.
    """

    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ['x^2', 'x', 'constant', 'adoption']
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = data_clean.values
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (c2, c1, intercept) = np.polyfit(x, y, 2)
    n_years = len(years)
    offsets = np.arange(n_years)

    x2 = (offsets ** 2) * c2
    x = offsets * c1
    constant = np.full(n_years, intercept)
    adoption = x + x2 + constant

    return pd.DataFrame(np.column_stack([x2, x, constant, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)



def poly_degree3_trend(data):
    """3rd degree polynomial trend model.
       Provides implementation for 'Adoption Data'!CN50:CR96 & 'TAM Data' columns CM:CQ
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.
    """

    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ['x^3', 'x^2', 'x', 'constant', 'adoption']
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = data_clean.values
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (c3, c2, c1, intercept) = np.polyfit(x, y, 3)
    n_years = len(years)
    offsets = np.arange(n_years)

    x3 = (offsets ** 3) * c3
    x2 = (offsets ** 2) * c2
    x = offsets * c1
    constant = np.full(n_years, intercept)
    adoption = x + x2 + x3 + constant

    return pd.DataFrame(np.column_stack([x3, x2, x, constant, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)



def exponential_trend(data):
    """exponential trend model.
       Provides implementation for 'Adoption Data'!CW50:CY96 & 'TAM Data' columns CV:CX
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.
    """
    years = np.arange(2014, 2061)
    years_idx = pd.Index(years, name="Year")
    columns = ['coeff', 'e^x', 'adoption']
    data_clean = data.dropna()

    if data_clean.empty: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    y = np.log(data_clean.values)
    x = data_clean.index - 2014

    if x.size == 0 or y.size == 0: 
        return pd.DataFrame(np.nan, columns=columns, dtype=np.float64, index=years_idx)

    (ce, coeff) = np.polyfit(x, y, 1)
    n_years = len(years)
    offsets = np.arange(n_years)

    ex = np.exp(offsets * ce)
    coeff = np.full(n_years, np.exp(coeff))
    adoption = ex * coeff

    return pd.DataFrame(np.column_stack([coeff, ex, adoption]), columns=columns,
                                  dtype=np.float64, index=years_idx)



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


def matching_data_sources(data_sources, name, groups_only, region_key=None):
    """Return a list of data sources which match name.
       If name is a group, return all data sources which are part of that group.
       If name is an individual case and groups_only=False, return it by itself.
       If groups_only=True and name is not a group, return all sources.

       Arguments:
         data_sources: a dict() of group names which contain dicts of data source names.
           Used for Total Addressable Market and adoption calculations. For example:
           {
             'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...},
             'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...},
             'Conservative Cases': {'Study Name E': 'filename E', ...},
             'Region: OECD90': {
                 'Ambitious Cases': {'Study Name F': 'filename F', 'Study Name A': 'filename A'}
             }
           }
         name: a name of an individual data source, or the name of a group
           like 'Ambitious Cases'
         groups_only: only return a group, or all columns if no group is found.
           This is typically useful for stddev calculations, which are never done
           (and are nonsensical) on an individual data source only on a single
           group or over all sources.
         region_key: if present, will consider only a subset of the data_sources matching that
           region.  The region_key argument is expected to match the key in data_sources
           (i.e. pass in 'Region: OECD90' not just 'OECD90')
           If a given region_key does not have an entry in data_sources, we continue on with the
           sources in the top level of data_sources. This may seem odd but it really is what we
           want, the common case is a single set of sources which have a column for each region.
           Having a distinct set of sources for a given region is the uncommon case.
           If region_key is None, we consider *only* the top level sources.
    """
    if name is None or pd.isna(name):
        return None
    if region_key is not None and region_key in data_sources:
        data_sources = data_sources[region_key]
    else:
        # only use top level sources
        data_sources = {k:v for (k,v) in data_sources.items() if not k.startswith('Region:')}
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
    return None


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
