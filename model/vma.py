"""Implementation of the Variable Meta-Analysis module."""

import math
import numpy as np
import pandas as pd




def generate_vma_dict(path_to_vma_data):
    """
    Convenience function for use by solution classes.
    Reads 'VMA_info.csv' file in solution's 'vma_data' dir. Generates dict of VMAs where data
    exists for input into AdvancedControls object.
    NOTE: this will set input args of each VMA object to default values. If any VMA objects
    need non-default args, they must be generated manually and inserted into the dict.
    Args:
      path_to_vma_data: path to 'vma_data' dir (pathlib object)

    Returns:
      dict for input to AdvancedControls() 'vnas' attribute
    """
    vma_info_df = pd.read_csv(path_to_vma_data.joinpath('VMA_info.csv'), index_col=0)
    vma_dict = {}
    for _, row in vma_info_df.iterrows():
        if row['Has data?']:
            use_weight = row.get('Use weight?', False)
            fixed_mean = row.get('Fixed Mean', np.nan)
            fixed_high = row.get('Fixed High', np.nan)
            fixed_low = row.get('Fixed Low', np.nan)
            fixed_summary = None
            if not pd.isna(fixed_mean) and not pd.isna(fixed_high) and not pd.isna(fixed_low):
                fixed_summary = (fixed_mean, fixed_high, fixed_low)
            vma_dict[row['Title on xls']] = VMA(path_to_vma_data.joinpath(row['Filename'] + '.csv'),
                                                use_weight=use_weight, fixed_summary=fixed_summary)
    return vma_dict


def convert_percentages(val):
    """pd.apply() functions to convert percentages"""
    if isinstance(val, str) and val.endswith('%'):
        return float(val.strip('%')) / 100.0
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
         fixed_summary: if present, should be a tuple to use for (mean, high, low) instead
           of calculating those values
    """

    def __init__(self, filename, low_sd=1.0, high_sd=1.0, discard_multiplier=3, use_weight=False,
                 postprocess=None, fixed_summary=None):
        df = pd.read_csv(filename, index_col=False, skipinitialspace=True, skip_blank_lines=True)
        self.source_data = df
        self.low_sd = low_sd
        self.high_sd = high_sd
        self.discard_multiplier = discard_multiplier
        self.postprocess = postprocess
        self.fixed_summary = fixed_summary
        if use_weight:
            assert not all(pd.isnull(df['Weight'])), "'Use weight' selected but no weights to use"
        self.use_weight = use_weight
        weight = df['Weight'].apply(convert_percentages)
        weight.name = 'Weight'
        raw = df['Raw Data Input'].apply(convert_percentages)
        raw.name = 'Raw'
        units = df['Original Units']
        units.name = 'Units'
        value = df['Conversion calculation']
        value.name = 'Value'
        exclude = df['Exclude Data?'].fillna(False)
        exclude.name = 'Exclude?'
        tmr = df['Thermal-Moisture Regime'].fillna(False)
        tmr.name = 'TMR'
        self.df = pd.concat([value, units, raw, weight, exclude, tmr], axis=1)
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


    def avg_high_low(self, key=None, regime=None):
        """
        Args:
          key: (optional) specify 'mean', 'high' or 'low' to get single value
          regime: string name of the thermal moisture regime to select sources for.

        Returns:
          By default returns (mean, high, low) using low_sd/high_sd.
          If key is specified will return associated value only
        """
        df = self._discard_outliers()
        df = df.loc[df['Exclude?'] == False]
        if regime:
            df = df.loc[df['TMR'] == regime]

        if self.use_weight:
            weights = df['Weight'].fillna(1.0)
            total_weights = weights.sum() if weights.sum() != 0.0 else 1.0
            mean = (df['Value'] * weights).sum() / total_weights
            M = (weights != 0).sum()
            if M == 0.0:
                sd = 0.0
            else:
                # A weighted standard deviation is not the same as stddev()
                numerator = (weights * ((df['Value'] - mean) ** 2)).sum()
                denominator = ((M - 1) / M) * total_weights
                sd = math.sqrt(numerator / denominator)
        else:
            mean = df['Value'].mean()
            # whole population stddev, ddof=0
            sd = df['Value'].std(ddof=0)

        if self.fixed_summary is not None:
            (mean, high, low) = self.fixed_summary
        else:
            high = mean + (self.high_sd * sd)
            low = mean - (self.low_sd * sd)

        if self.postprocess:
            return self.postprocess(mean, high, low)
        else:
            if key is None:
                return mean, high, low
            elif key == 'high':
                return high
            elif key == 'mean' or key == 'average' or key == 'avg':
                return mean
            elif key == 'low':
                return low
            else:
                raise ValueError("invalid key: {}. key must be 'mean', 'high', 'low' or None")
