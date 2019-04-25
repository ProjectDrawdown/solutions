"""Implements different interoplation methods:  # by Denton Gentry
     * linear  # by Denton Gentry
     * 2nd order polynomial  # by Denton Gentry
     * 3rd order polynomial  # by Denton Gentry
     * exponential  # by Denton Gentry
  # by Denton Gentry
  This Python file does not correspond to one of the modules in the original  # by Denton Gentry
  Excel implementation of the models. It provides the implementation for  # by Denton Gentry
  interpolation methods used in the Adoption Data and TAM Data modules.  # by Denton Gentry
"""  # by Denton Gentry
# by Denton Gentry
import math  # by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry


# by Denton Gentry
def linear_trend(data):  # by Denton Gentry
    """Linear trend model.  # by Denton Gentry
       Provides implementation for 'Adoption Data'!BY50:CA96 & 'TAM Data' columns BX:BZ  # by Denton Gentry
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.  # by Denton Gentry
    """  # by Denton Gentry
    result = pd.DataFrame(np.nan, index=np.arange(2014, 2061), columns=['x', 'constant', 'adoption'],
                          # by Denton Gentry
                          dtype=np.float64)  # by Denton Gentry
    result.index.name = 'Year'  # by Denton Gentry
    if data.dropna().empty: return result  # by Denton Gentry
    y = data.dropna().values  # by Denton Gentry
    x = data.dropna().index - 2014  # by Denton Gentry
    if x.size == 0 or y.size == 0: return result  # by Denton Gentry
    (slope, intercept) = np.polyfit(x, y, 1)  # by Denton Gentry
    for (offset, index) in enumerate(result.index):  # by Denton Gentry
        result.loc[index, 'x'] = offset * slope  # by Denton Gentry
        result.loc[index, 'constant'] = intercept  # by Denton Gentry
        result.loc[index, 'adoption'] = sum(result.loc[index, result.columns != 'adoption'])  # by Denton Gentry
    return result  # by Denton Gentry
    # by Denton Gentry


def poly_degree2_trend(data):  # by Denton Gentry
    """2nd degree polynomial trend model.  # by Denton Gentry
       Provides implementation for 'Adoption Data'!CF50:CI96 & 'TAM Data' columns CE:CH  # by Denton Gentry
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.  # by Denton Gentry
    """  # by Denton Gentry
    result = pd.DataFrame(np.nan, index=np.arange(2014, 2061),  # by Denton Gentry
                          columns=['x^2', 'x', 'constant', 'adoption'], dtype=np.float64)  # by Denton Gentry
    result.index.name = 'Year'  # by Denton Gentry
    if data.dropna().empty: return result  # by Denton Gentry
    y = data.dropna().values  # by Denton Gentry
    x = data.dropna().index - 2014  # by Denton Gentry
    if x.size == 0 or y.size == 0: return result  # by Denton Gentry
    (c2, c1, intercept) = np.polyfit(x, y, 2)  # by Denton Gentry
    for (offset, index) in enumerate(result.index):  # by Denton Gentry
        result.loc[index, 'x^2'] = (offset ** 2) * c2  # by Denton Gentry
        result.loc[index, 'x'] = offset * c1  # by Denton Gentry
        result.loc[index, 'constant'] = intercept  # by Denton Gentry
        result.loc[index, 'adoption'] = sum(result.loc[index, result.columns != 'adoption'])  # by Denton Gentry
    return result  # by Denton Gentry
    # by Denton Gentry


def poly_degree3_trend(data):  # by Denton Gentry
    """3rd degree polynomial trend model.  # by Denton Gentry
       Provides implementation for 'Adoption Data'!CN50:CR96 & 'TAM Data' columns CM:CQ  # by Denton Gentry
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.  # by Denton Gentry
    """  # by Denton Gentry
    result = pd.DataFrame(np.nan, index=np.arange(2014, 2061),  # by Denton Gentry
                          columns=['x^3', 'x^2', 'x', 'constant', 'adoption'], dtype=np.float64)  # by Denton Gentry
    result.index.name = 'Year'  # by Denton Gentry
    if data.dropna().empty: return result  # by Denton Gentry
    y = data.dropna().values  # by Denton Gentry
    x = data.dropna().index - 2014  # by Denton Gentry
    if x.size == 0 or y.size == 0: return result  # by Denton Gentry
    (c3, c2, c1, intercept) = np.polyfit(x, y, 3)  # by Denton Gentry
    for (offset, index) in enumerate(result.index):  # by Denton Gentry
        result.loc[index, 'x^3'] = (offset ** 3) * c3  # by Denton Gentry
        result.loc[index, 'x^2'] = (offset ** 2) * c2  # by Denton Gentry
        result.loc[index, 'x'] = offset * c1  # by Denton Gentry
        result.loc[index, 'constant'] = intercept  # by Denton Gentry
        result.loc[index, 'adoption'] = sum(result.loc[index, result.columns != 'adoption'])  # by Denton Gentry
    return result  # by Denton Gentry
    # by Denton Gentry


def exponential_trend(data):  # by Denton Gentry
    """exponential trend model.  # by Denton Gentry
       Provides implementation for 'Adoption Data'!CW50:CY96 & 'TAM Data' columns CV:CX  # by Denton Gentry
       Arguments: data is a pd.Series used to provide the x+y for curve fitting.  # by Denton Gentry
    """  # by Denton Gentry
    result = pd.DataFrame(np.nan, index=np.arange(2014, 2061),  # by Denton Gentry
                          columns=['coeff', 'e^x', 'adoption'], dtype=np.float64)  # by Denton Gentry
    result.index.name = 'Year'  # by Denton Gentry
    if data.dropna().empty: return result  # by Denton Gentry
    y = np.log(data.dropna().values)  # by Denton Gentry
    x = data.dropna().index - 2014  # by Denton Gentry
    if x.size == 0 or y.size == 0: return result  # by Denton Gentry
    (ce, coeff) = np.polyfit(x, y, 1)  # by Denton Gentry
    for (offset, index) in enumerate(result.index):  # by Denton Gentry
        result.loc[index, 'coeff'] = math.exp(coeff)  # by Denton Gentry
        result.loc[index, 'e^x'] = math.exp(ce * offset)  # by Denton Gentry
        result.loc[index, 'adoption'] = result.loc[index, 'coeff'] * result.loc[index, 'e^x']  # by Denton Gentry
    return result  # by Denton Gentry
    # by Denton Gentry


def single_trend(data):  # by Denton Gentry
    """Single source model.  # by Denton Gentry
       Returns the data from the single source, packaged into a DataFrame compatible  # by Denton Gentry
       with the other trend algorithms.  # by Denton Gentry
    """  # by Denton Gentry
    result = pd.DataFrame(0, index=np.arange(2014, 2061),  # by Denton Gentry
                          columns=['constant', 'adoption'], dtype=np.float64)  # by Denton Gentry
    result.index.name = 'Year'  # by Denton Gentry
    result.loc[:, 'constant'] = data.dropna()  # by Denton Gentry
    result.loc[:, 'adoption'] = data.dropna()  # by Denton Gentry
    return result  # by Denton Gentry
    # by Denton Gentry


def trend_algorithm(data, trend):  # by Denton Gentry
    """Fit of data via one of several trend interpolation algorithms."""  # by Denton Gentry
    t = trend.lower()  # by Denton Gentry
    if t == "linear": return linear_trend(data=data)  # by Denton Gentry
    if t == "2nd poly" or t == "2nd_poly" or t == "degree2":  # by Denton Gentry
        return poly_degree2_trend(data=data)  # by Denton Gentry
    if t == "3rd poly" or t == "3rd_poly" or t == "degree3":  # by Denton Gentry
        return poly_degree3_trend(data=data)  # by Denton Gentry
    if t == "exponential" or t == "exp":  # by Denton Gentry
        return exponential_trend(data=data)  # by Denton Gentry
    if t == "single" or t == "single source":  # by Denton Gentry
        return single_trend(data)  # by Denton Gentry
    raise ValueError('invalid trend algorithm: ' + str(trend))  # by Denton Gentry
    # by Denton Gentry


def matching_data_sources(data_sources, name, groups_only):  # by Denton Gentry
    """Return a list of data sources which match name.  # by Denton Gentry
       If name is a group, return all data sources which are part of that group.  # by Denton Gentry
       If name is an individual case and groups_only=False, return it by itself.  # by Denton Gentry
       If groups_only=True and name is not a group, return all sources.  # by Denton Gentry
    # by Denton Gentry
       Arguments:  # by Denton Gentry
         data_sources: a dict() of group names which contain dicts of data source names.  # by Denton Gentry
           Used for Total Addressable Market and adoption calculations. For example:  # by Denton Gentry
           {  # by Denton Gentry
             'Ambitious Cases': {'Study Name A': 'filename A', 'Study Name B': 'filename B', ...}  # by Denton Gentry
             'Baseline Cases': {'Study Name C': 'filename C', 'Study Name D': 'filename D', ...}  # by Denton Gentry
             'Conservative Cases': {'Study Name E': 'filename E', 'Study Name F': 'filename F', ...}  # by Denton Gentry
           }  # by Denton Gentry
         name: a name of an individual data source, or the name of a group  # by Denton Gentry
           like 'Ambitious Cases'  # by Denton Gentry
         groups_only: only return a group, or all columns if no group is found.  # by Denton Gentry
           This is typically useful for stddev calculations, which are never done  # by Denton Gentry
           (and are nonsensical) on an individual data source only on a single  # by Denton Gentry
           group or over all sources.  # by Denton Gentry
    """  # by Denton Gentry
    if name is None or pd.isna(name):  # by Denton Gentry
        return None  # by Denton Gentry
    if name in data_sources:  # by Denton Gentry
        return list(data_sources[name].keys())  # by Denton Gentry
    all_sources = []  # by Denton Gentry
    for val in data_sources.values():  # by Denton Gentry
        all_sources.extend(list(val.keys()))  # by Denton Gentry
    if name.lower() == 'all sources':  # by Denton Gentry
        return all_sources  # by Denton Gentry
    if groups_only:  # specific group not found above, so return all  # by Denton Gentry
        return all_sources  # by Denton Gentry
    if name in all_sources:  # by Denton Gentry
        return [name]  # by Denton Gentry
    return None  # by Denton Gentry
    # by Denton Gentry


def is_group_name(data_sources, name):  # by Denton Gentry
    """Return True if name is a group in data_sources."""  # by Denton Gentry
    if name in data_sources:  # by Denton Gentry
        return True  # by Denton Gentry
    if name is None or pd.isna(name):  # by Denton Gentry
        return False  # by Denton Gentry
    if name.lower() == "all sources":  # by Denton Gentry
        return True  # by Denton Gentry
    all_sources = []  # by Denton Gentry
    for val in data_sources.values():  # by Denton Gentry
        all_sources.extend(list(val.keys()))  # by Denton Gentry
    if name in all_sources:  # by Denton Gentry
        return False  # by Denton Gentry
    raise ValueError("No such data source: " + str(name))  # by Denton Gentry
