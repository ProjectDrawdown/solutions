"""Implementation of the Variable Meta-Analysis module."""

import math
import pandas as pd


def convert_percentages(val):
  """pd.apply() functions to convert percentages"""
  if isinstance(val, str) and val.endswith('%'):
    return float(val.strip('%'))/100.0
  return val


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
       postprocess: function to pass (mean, high, low) to before returning.
  """
  def __init__(self, filename, low_sd=1.0, high_sd=1.0, discard_multiplier=3, postprocess=None):
    df = pd.read_csv(filename, index_col=False, skipinitialspace=True, skip_blank_lines=True, comment='#')
    self.source_data = df
    self.low_sd = low_sd
    self.high_sd = high_sd
    self.discard_multiplier = discard_multiplier
    self.postprocess = postprocess
    self.use_weight = not all(pd.isnull(df['Weight']))
    weight = df['Weight'].apply(convert_percentages)
    weight.name = 'Weight'
    # note: string has trailing space when pasted manually from xls
    raw = df['Raw Data Input '].apply(convert_percentages)
    raw.name = 'Raw'
    units = df['Original Units']
    units.name = 'Units'
    value = df['Conversion calculation**']
    value.name = 'Value'
    self.df = pd.concat([value, units, raw, weight], axis=1)
    self.df['Value'].fillna(self.df['Raw'], inplace=True)

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

  def avg_high_low(self, key=None):
    """
    Args:
      key: (optional) specify 'mean', 'high' or 'low' to get single value

    Returns:
      By default returns (mean, high, low) using low_sd/high_sd.
      If key is specified will return associated value only
    """
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
      if key is None: return mean, high, low
      elif key == 'high': return high
      elif key == 'mean' or key == 'average' or key =='avg': return mean
      elif key == 'low': return low
      else:
        raise ValueError("invalid key: {}. key must be 'mean', 'high', 'low' or None")
