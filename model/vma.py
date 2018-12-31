"""Implementation of the Variable Meta-Analysis module."""

import math
import pandas as pd


def get_value(val):
  """pd.apply() fcn for floating point numbers and percentages."""
  if isinstance(val, str) and val.endswith('%'):
    return float(val.strip('%'))/100.0
  return val


# Simple conversions, multiply raw data by this factor and return.
conversions = {
    # Source: http://inflationdata.com/Inflation/Consumer_Price_Index/CurrentCPI.asp
    'US$2017/kW': 0.96579634465,        'US$2017/MW': 0.00096579634465,
    'US$2016/kW': 0.986885218565795,    'US$2016/MW': 0.000986885218565795,
    'US$2015/kW': 0.99881,              'US$2015/MW': 0.00099881,
    'US$2014/kW': 1.00,                 'US$2014/MW': 0.001,
    'US$2013/kW': 1.02,                 'US$2013/MW': 0.00102,
    'US$2012/kW': 1.03,                 'US$2012/MW': 0.00103,
    'US$2011/kW': 1.05,                 'US$2011/MW': 0.00105,
    'US$2010/kW': 1.09,                 'US$2010/MW': 0.00109,
    'US$2009/kW': 1.10,                 'US$2009/MW': 0.00110,
    'US$2008/kW': 1.10,                 'US$2008/MW': 0.00110,
    'US$2007/kW': 1.14,                 'US$2007/MW': 0.00114,
    'US$2006/kW': 1.17,                 'US$2006/MW': 0.00117,
    'US$2005/kW': 1.21,                 'US$2005/MW': 0.00121,
    'US$2004/kW': 1.25,                 'US$2004/MW': 0.00125,
    'US$2003/kW': 1.29,                 'US$2003/MW': 0.00129,
    'US$2002/kW': 1.32,                 'US$2002/MW': 0.00132,
    'US$2001/kW': 1.34,                 'US$2001/MW': 0.00134,
    'US$2000/kW': 1.37,                 'US$2000/MW': 0.00137,

    '€2013/kW': 1.02 * 1.328464,        '€2013/MW': 0.00102 * 1.328464,
    '€2012/kW': 1.03 * 1.285697,        '€2012/MW': 0.00103 * 1.285697,
    '€2011/kW': 1.05 * 1.392705,        '€2011/MW': 0.00105 * 1.392705,

    'g-CO2eq/kWh': 1000.0,              'kg-CO2eq/kWh': 1000000.0,
}


def convert_units(row):
  raw = row['Raw Data Input']
  units = row['Original Units']
  if not units:
    return float(raw)
  if units == '%':
    return float(raw.strip('%'))/100.0
  if units in conversions:
    return float(raw) * conversions[units]
  raise ValueError("Unknown unit conversion=" + str(units))


class AvgHighLow:
  def __init__(self, df, low_sd, high_sd, use_weight=False):
    self.low_sd = low_sd
    self.high_sd = high_sd
    self.use_weight = use_weight
    weight = df['Weight'].apply(get_value)
    weight.name = 'Weight'
    raw = df['Raw Data Input'].apply(get_value)
    raw.name = 'Raw'
    units = df['Original Units']
    units.name = 'Units'
    value = df.apply(convert_units, axis=1)
    value.name = 'Value'
    new_df = pd.concat([value, weight], axis=1)
    self.df = new_df

  def avg_high_low(self):
    """Return (mean, high, low) using low_sd/high_sd."""
    if self.use_weight:
      weights = self.df['Weight']
      mean = (self.df['Value'] * weights).sum() / weights.sum()
      # A weighted standard deviation is not the same as stddev()
      numerator = (weights * ((self.df['Value'] - mean) ** 2)).sum()
      M = (weights != 0).sum()
      denominator = ((M - 1) / M) * weights.sum()
      sd = math.sqrt(numerator / denominator)
    else:
      mean = self.df['Value'].mean()
      # whole population stddev, ddof=0
      sd = self.df['Value'].std(ddof=0)
    high = mean + (self.high_sd * sd)
    low = mean - (self.low_sd * sd)
    return (mean, high, low)
