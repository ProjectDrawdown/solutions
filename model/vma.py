"""Implementation of the Variable Meta-Analysis module."""

import math
import re
import pandas as pd


def get_value(val, substitutions):
  """pd.apply() functions to convert percentages and substitutions."""
  if val in substitutions:
    val = substitutions[val]
  if isinstance(val, str) and val.endswith('%'):
    return float(val.strip('%'))/100.0
  return val


# Simple conversions, multiply raw data by this factor and return.
conversions = {
    # Source: http://inflationdata.com/Inflation/Consumer_Price_Index/CurrentCPI.asp
    'us$2017/kw': 0.96579634465,        'us$2017/mw': 0.00096579634465,
    'us$2016/kw': 0.986885218565795,    'us$2016/mw': 0.000986885218565795,
    'us$2015/kw': 0.99881,              'us$2015/mw': 0.00099881,
    'us$2014/kw': 1.00,                 'us$2014/mw': 0.001,
    'us$2013/kw': 1.02,                 'us$2013/mw': 0.00102,
    'us$2012/kw': 1.03,                 'us$2012/mw': 0.00103,
    'us$2011/kw': 1.05,                 'us$2011/mw': 0.00105,
    'us$2010/kw': 1.09,                 'us$2010/mw': 0.00109,
    'us$2009/kw': 1.10,                 'us$2009/mw': 0.00110,
    'us$2008/kw': 1.10,                 'us$2008/mw': 0.00110,
    'us$2007/kw': 1.14,                 'us$2007/mw': 0.00114,
    'us$2006/kw': 1.17,                 'us$2006/mw': 0.00117,
    'us$2005/kw': 1.21,                 'us$2005/mw': 0.00121,
    'us$2004/kw': 1.25,                 'us$2004/mw': 0.00125,
    'us$2003/kw': 1.29,                 'us$2003/mw': 0.00129,
    'us$2002/kw': 1.32,                 'us$2002/mw': 0.00132,
    'us$2001/kw': 1.34,                 'us$2001/mw': 0.00134,
    'us$2000/kw': 1.37,                 'us$2000/mw': 0.00137,

    '€2013/kw': 1.02 * 1.328464,        '€2013/mw': 0.00102 * 1.328464,
    '€2012/kw': 1.03 * 1.285697,        '€2012/mw': 0.00103 * 1.285697,
    '€2011/kw': 1.05 * 1.392705,        '€2011/mw': 0.00105 * 1.392705,

    'g-co2eq/kwh': 1000.0,              'kg-co2eq/kwh': 1000000.0,
}


def _convert(raw, units, conversions, substitutions):
  units = units.lower()

  # Allow ex: usd2011/tw to alias us$2011/tw
  units = re.sub(r'usd(\d{4})/([kmgt])w', r'us$\1/\2w', units)

  if units == 'btu/kwh': return 0.00341214163 * 1000000 / float(raw)
  if units == 'btu/mwh': return 3.41214163 * 1000000 / float(raw)
  if units == 'btu/gwh': return 3412.14163 * 1000000 / float(raw)
  if units == 'btu/twh': return 3412141.63 * 1000000 / float(raw)
  if units in conversions:
    return float(raw) * conversions[units]
  if units == 'years': return float(raw)
  if units == 'kwh/kw': return float(raw)
  if units == 'capacity factor (%)':
    if isinstance(raw, str) and raw.endswith('%'):
      v = float(raw.strip('%'))/100.0
    else:
      v = float(raw)
    return v * 365 * 24

  # ex: US$2016/MWh-US$2014/kWh
  m = re.match(r'((?:us\$|€)\d{4}/[kmgt]w)h-us\$2014/kwh', units)
  if m:
    return float(raw) * conversions[m.group(1)]

  # ex: US$2016/MWh-US$2014/kW
  m = re.match(r'((?:us\$|€)\d{4}/[kmgt]w)h-us\$2014/kw', units)
  if m:
    return float(raw) * conversions[m.group(1)] * substitutions['@soln_avg_annual_use@']

  return None


def convert_units(row, conversions, substitutions, final_units):
  raw = row['Raw Data Input']
  units = row['Original Units']
  units = '' if pd.isnull(units) else units

  if units == '%' or (not units and isinstance(raw, str) and raw.endswith('%')):
    return float(raw.strip('%'))/100.0
  if not units:
    return float(raw)

  val = _convert(raw=raw, units=units, conversions=conversions, substitutions=substitutions)
  if val == None and final_units:
    units = units + "-" + str(final_units)
    val = _convert(raw=raw, units=units, conversions=conversions, substitutions=substitutions)
  if val != None:
    return val

  raise ValueError("Unknown unit conversion=" + str(row['Original Units']))


class VMA:
  """Meta-analysis of multiple data sources to a summary result.
     Arguments:
       filename: a CSV file containing data sources. This file must contain columns
         named "Raw Data Input", "Weight", and "Original Units". It can contain additional
         columns, which will be ignored.
       low_sd: number of multiples of the stddev to use for the low result.
       high_sd: number of multiples of the stddev to use for the high result.
       discard_multiplier: discard outlier values more than this many multiples of the
         stddev away from the mean.
       final_units: specify the unit to convert to. Most of the time this is not necessary,
         there is only one rational choice for conversion.
       substitutions: substitute occurrences of the keys in this dict with the value
         from the dict, for any entries in the 'Raw Data Input' and 'Weight' columns
         of the CSV file.
       postprocess: function to pass (mean, high, low) to before returning.
  """
  def __init__(self, filename, low_sd=1.0, high_sd=1.0, discard_multiplier=3,
      final_units=None, substitutions={}, postprocess=None):
    df = pd.read_csv(filename, index_col=False, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    self.source_data = df
    self.low_sd = low_sd
    self.high_sd = high_sd
    self.discard_multiplier = discard_multiplier
    self.final_units = final_units
    self.substitutions = substitutions
    self.postprocess = postprocess
    self.use_weight = not all(pd.isnull(df['Weight']))
    weight = df['Weight'].apply(get_value, substitutions=substitutions)
    weight.name = 'Weight'
    raw = df['Raw Data Input'].apply(get_value, substitutions=substitutions)
    raw.name = 'Raw'
    units = df['Original Units']
    units.name = 'Units'
    value = df.apply(convert_units, axis=1, conversions=conversions,
        substitutions=substitutions, final_units=self.final_units)
    value.name = 'Value'
    self.df = pd.concat([value, units, raw, weight], axis=1)

  def _discard_outliers(self):
    """Discard outlier values beyond a multiple of the stddev."""
    df = self.df
    mean = df['Value'].mean()
    sd = df['Value'].std(ddof=0)
    valid = df['Value'] <= (mean + (self.discard_multiplier * sd))
    df = df[valid]
    mean = df['Value'].mean()
    sd = df['Value'].std(ddof=0)
    valid = df['Value'] >= (mean - (self.discard_multiplier * sd))
    df = df[valid]
    return df

  def avg_high_low(self):
    """Return (mean, high, low) using low_sd/high_sd."""
    df = self._discard_outliers()
    if self.use_weight:
      weights = df['Weight'].fillna(1.0)
      mean = (df['Value'] * weights).sum() / weights.sum()
      # A weighted standard deviation is not the same as stddev()
      numerator = (weights * ((df['Value'] - mean) ** 2)).sum()
      M = (weights != 0).sum()
      denominator = ((M - 1) / M) * weights.sum()
      sd = math.sqrt(numerator / denominator)
    else:
      mean = df['Value'].mean()
      # whole population stddev, ddof=0
      sd = df['Value'].std(ddof=0)
    high = mean + (self.high_sd * sd)
    low = mean - (self.low_sd * sd)
    if self.postprocess:
      return self.postprocess(mean, high, low)
    else:
      return (mean, high, low)
