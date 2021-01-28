"""Implementation of the Variable Meta-Analysis module."""

import io
import math
import pathlib

import numpy as np
import pandas as pd
import xlrd

import model.dd
from tools.vma_xls_extract import VMAReader


VMA_columns = ['Value', 'Units', 'Raw', 'Weight', 'Exclude?', 'Region', 'Main Region', 'TMR']


def check_fixed_summary(*values):
    """Checks that there are no NaN/None values in the given summary.
    Arguments:
        values: individually given values, e.g. check_fixed(1, 2, None)
    Returns:
        None if any value is NaN/None, otherwise a tuple of the given iterable
    """
    if any([pd.isna(value) for value in values]):
        return None
    else:
        return tuple(values)


def convert_percentages(val):
    """pd.apply() functions to convert percentages"""
    if isinstance(val, str) and val.endswith('%'):
        try:
            return float(val.strip('%')) / 100.0
        except ValueError:
            return np.inf
    try:
        return float(val)
    except ValueError:
        return np.inf


def convert_NaN(val):
    """pd.apply() functions to convert NaN"""
    if isinstance(val, str) and val.lower() == 'nan':
        return np.nan
    if pd.isna(val):
        return np.nan
    return val


class VMA:
    """Meta-analysis of multiple data sources to a summary result.
       Arguments:
         filename: (string, pathlib.Path, or io.StringIO) Can be either
           * Path to a CSV file containing data sources. The CSV file must
             contain columns named "Raw Data Input", "Weight", and "Original
             Units". It can contain additional columns, which will be ignored.
           * The xlsx/xlsm file needs to have columns structured in a certain
             way, see VMAReader.df_template for more information.
           * io.StringIO objects are processed as if they are opened CSV files
         title: string, name of the VMA to extract from an Excel file. This
           value is unused if filename is a CSV. Will raise an AssertionError
           if the title is not available in the Excel file.
         low_sd: number of multiples of the stddev to use for the low result.
         high_sd: number of multiples of the stddev to use for the high result.
         discard_multiplier: discard outlier values more than this many multiples of the
           stddev away from the mean.
         stat_correction: discard outliers more than discard_multiplier stddev away from the mean.
         fixed_summary: if present, should be a tuple to use for (mean, high, low) instead
           of calculating those values
    """

    def __init__(self, vma_data_csv: bytes, title=None, low_sd=1.0, high_sd=1.0,
                 discard_multiplier=3, stat_correction=None, use_weight=False,
                 fixed_summary=None):
        self.vma_data_csv = vma_data_csv
        self.title = title
        self.low_sd = low_sd
        self.high_sd = high_sd
        self.discard_multiplier = discard_multiplier
        self.stat_correction = stat_correction
        self.use_weight = use_weight
        if stat_correction is None:
            # Excel does not discard outliers if weights are used, we do the same by default.
            self.stat_correction = not use_weight
        else:
            self.stat_correction = stat_correction
        self.fixed_summary = fixed_summary
        self.df = pd.DataFrame(columns=VMA_columns)

        csv_df = pd.read_csv(io.BytesIO(vma_data_csv), index_col=False, skipinitialspace=True, skip_blank_lines=True)
        self._convert_from_human_readable(csv_df)

    def _convert_from_human_readable(self, readable_df):
        """
        Converts a known set of readable column names to a known column set. A
        few data cleanups are also performed, such as converting percentages
        and filling NaN values.

        Arguments:
            readable_df: dataframe (from CSV or Excel file) using the standard
                long-form column names
            filename: pathlib.Path to source file, passed through for error
                transparency purposes

        Populates self.source_data with readable_df directly. Populates self.df
        with a series of renamed columns, along with a few data cleanup steps.
        """
        self._validate_readable_df(readable_df)
        self.source_data = readable_df
        if self.use_weight:
            err = f"'Use weight' selected but no weights to use"
            assert not all(pd.isnull(readable_df['Weight'])), err
        self.df['Weight'] = readable_df['Weight'].apply(convert_percentages)
        self.df['Raw'] = readable_df['Raw Data Input'].apply(convert_percentages)
        self.df['Units'] = readable_df['Original Units']
        self.df['Value'] = readable_df['Conversion calculation'].apply(convert_NaN)
        self.df['Exclude?'] = readable_df['Exclude Data?'].fillna(False)
        # correct some common typos and capitalization differences from Excel files.
        normalized_region = (readable_df['World / Drawdown Region']
                .replace('Middle East & Africa', 'Middle East and Africa')
                .replace('Asia (sans Japan)', 'Asia (Sans Japan)'))
        readable_df['World / Drawdown Region'] = normalized_region.astype(model.dd.rgn_cat_dtype)
        self.df['Region'] = readable_df['World / Drawdown Region']
        main_region = normalized_region.copy()
        for k, v in model.dd.COUNTRY_REGION_MAP.items():
            main_region.replace(k, v, inplace=True)
        self.df['Main Region'] = main_region
        if 'Thermal-Moisture Regime' in readable_df.columns:
            dft = readable_df['Thermal-Moisture Regime'].astype(model.dd.tmr_cat_dtype)
            readable_df['Thermal-Moisture Regime'] = dft
            self.df['TMR'] = readable_df['Thermal-Moisture Regime'].fillna('')
        self.df['Value'].fillna(self.df['Raw'], inplace=True)

    def _validate_readable_df(self, readable_df):
        if readable_df is None:
            raise ValueError("Dataframe is that VMA empty?")

    def _discard_outliers(self):
        """Discard outlier values beyond a multiple of the stddev."""
        df = self.df
        mean = df['Value'].astype('float64').mean(skipna=True)
        sd = df['Value'].std(ddof=0)
        if pd.isna(mean) or pd.isna(sd):
            return df
        valid = df['Value'] <= (mean + (self.discard_multiplier * sd))
        df = df[valid]
        valid = df['Value'] >= (mean - (self.discard_multiplier * sd))
        df = df[valid]
        return df

    def avg_high_low(self, key=None, regime=None, region=None):
        """
        Args:
          key: (optional) specify 'mean', 'high' or 'low' to get single value
          regime: string name of the thermal moisture regime to select sources for.
          region: string name of the world region to select sources for.

        Returns:
          By default returns (mean, high, low) using low_sd/high_sd.
          If key is specified will return associated value only
        """
        if self.use_weight:
            # Sum the weights before discarding outliers, to match Excel.
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.qkdzs364y2t2
            # Once reproducing Excel results is no longer essential, total_weight computation
            # can be moved down to the second use_weight conditional below. That way the sum
            # of the weights will only include sources which are being included in the mean.
            total_weights = self.df['Weight'].fillna(1.0).sum()
            total_weights = total_weights if total_weights != 0.0 else 1.0
            all_weights = self.df['Weight'].fillna(1.0)
            M = (all_weights != 0).sum()

        if self.fixed_summary is not None:
            (mean, high, low) = self.fixed_summary
        elif self.df.empty:
            mean = high = low = np.nan
        else:
            df = self._discard_outliers() if self.stat_correction else self.df
            df = df.loc[df['Exclude?'] == False]
            if regime:
                df = df.loc[df['TMR'] == regime]
            if region in model.dd.SPECIAL_COUNTRIES:
                df = df.loc[df['Region'] == region]
            elif region in model.dd.MAIN_REGIONS:
                # include values for special countries in corresponding main regions' statistics
                df = df.loc[df['Main Region'] == region]

            if self.use_weight:
                weights = df['Weight'].fillna(1.0)
                mean = (df['Value'] * weights).sum(skipna=True) / total_weights
                if M == 0.0:
                    sd = 0.0
                else:
                    # A weighted standard deviation is not the same as stddev()
                    numerator = (weights * ((df['Value'] - mean) ** 2)).sum()
                    # when Excel is deprecated, remove all_weights and use: M = (weights != 0).sum()
                    denominator = ((M - 1) / M) * total_weights
                    sd = math.sqrt(numerator / denominator)
            else:
                mean = df['Value'].mean(skipna=True)
                # whole population stddev, ddof=0
                sd = df['Value'].std(ddof=0)

            high = mean + (self.high_sd * sd)
            low = mean - (self.low_sd * sd)

        if key is None:
            return mean, high, low
        elif key == 'high':
            return high
        elif key == 'mean' or key == 'average' or key == 'avg':
            return mean
        elif key == 'low':
            return low
        else:
            raise ValueError(f"invalid key: {key}. key must be 'mean', 'high', 'low' or None")
