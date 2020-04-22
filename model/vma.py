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


def populate_fixed_summaries(vma_dict, filename):
    """
    Convenience function for use by solution classes.
    Args:
        vma_dict: dict indexed by VMA Title
        filename: VMA_info CSV file with fixed summary data for Mean, High, Low
    Modifies the given vma_dict according to the title in the 'Title on xls'
    row of the 'filename' CSV, populating the vma.fixed_summary field.
    """
    vma_info_df = pd.read_csv(filename, index_col=0)
    for _, row in vma_info_df.iterrows():
        title = row['Title on xls']
        fixed_mean = row.get('Fixed Mean', np.nan)
        fixed_high = row.get('Fixed High', np.nan)
        fixed_low = row.get('Fixed Low', np.nan)
        fixed_summary = check_fixed_summary(fixed_mean, fixed_high, fixed_low)
        if fixed_summary is not None:
            vma_dict[title].fixed_summary = fixed_summary


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
        return float(val.strip('%')) / 100.0
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

    def __init__(self, filename, title=None, low_sd=1.0, high_sd=1.0,
                 discard_multiplier=3, stat_correction=None, use_weight=False,
                 fixed_summary=None):
        self.filename = filename
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

        if filename:
            # Turn strings into pathlib
            if isinstance(filename, str):
                filename = pathlib.Path(filename)

            # Instantiate VMA with various file types
            if isinstance(filename, io.StringIO):
                self._read_csv(filename=filename)
            elif filename.suffix == '.xlsx' or filename.suffix == '.xlsm':
                self._read_xls(filename=filename, title=title)
            else:
                # Fall back on this as the default behavior, there are a
                # variety of use cases that have been built-in, they do not
                # all end with '.csv'
                self._read_csv(filename=filename)

        else:
            self.source_data = pd.DataFrame()

    def _read_csv(self, filename):
        """
        Read a properly formatted CSV file (e.g. as is produced by
        solution_xls_extract) to instantiate this VMA.

        Arguments:
            filename: pathlib.Path to a CSV file

        Populates self.source_data and self.df
        """
        csv_df = pd.read_csv(filename, index_col=False, skipinitialspace=True, skip_blank_lines=True)
        self._convert_from_human_readable(csv_df)

    def _read_xls(self, filename, title):
        """
        Read a properly formatted xlsx/xlsm file (with a Variable
        Meta-analysis sheet) to instantiate this VMA.

        Arguments:
            filename: pathlib.Path to an Excel file
            title: string matching VMA name in the Variable Meta-analysis sheet

        Populates self.source_data, self.df, and self.fixed_summary if the
        required values are present.
        """
        workbook = xlrd.open_workbook(filename=filename)
        vma_reader = VMAReader(workbook)
        if 'Variable Meta-analysis-DD' in workbook.sheet_names():
            alt_vma = True
        else:
            alt_vma = False

        # Pull the desired table from this workbook
        try:
            (xl_df, use_weight, summary) = \
                vma_reader.xls_df_dict(alt_vma=alt_vma, title=title)[title]
        except KeyError:
            # The title wasn't available in the given workbook. Read all titles
            # to give the user a hint.
            full_dict = vma_reader.xls_df_dict(alt_vma=alt_vma)
            raise ValueError(
                "Title {!r} not available in {}.".format(title, filename) + \
                "\nOptions:\n\t" + "\n\t".join(full_dict.keys())
            )

        self._convert_from_human_readable(xl_df)

        # Populate the self.fixed_summary field if the values are valid
        fixed_summary = check_fixed_summary(*summary)
        if fixed_summary is not None:
            self.fixed_summary = fixed_summary

    def _convert_from_human_readable(self, readable_df):
        """
        Converts a known set of readable column names to a known column set. A
        few data cleanups are also performed, such as converting percentages
        and filling NaN values.

        Arguments:
            readable_df: dataframe (from CSV or Excel file) using the standard
                long-form column names

        Populates self.source_data with readable_df directly. Populates self.df
        with a series of renamed columns, along with a few data cleanup steps.
        """
        if readable_df is None:
            if self.title is None:
                source = "\n\tFile: {}\n".format(self.filename)
            else:
                source = "\n\tFile: {}\n\tTitle: {!r}\n".format(self.filename,
                                                                self.title)
            raise ValueError("Dataframe from" + source + "is None, is that VMA empty?")
        self.source_data = readable_df
        if self.use_weight:
            assert not all(pd.isnull(readable_df['Weight'])), "'Use weight' selected but no weights to use"
        self.df['Weight'] = readable_df['Weight'].apply(convert_percentages)
        self.df['Raw'] = readable_df['Raw Data Input'].apply(convert_percentages)
        self.df['Units'] = readable_df['Original Units']
        self.df['Value'] = readable_df['Conversion calculation']
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
                mean = (df['Value'] * weights).sum() / total_weights
                if M == 0.0:
                    sd = 0.0
                else:
                    # A weighted standard deviation is not the same as stddev()
                    numerator = (weights * ((df['Value'] - mean) ** 2)).sum()
                    # when Excel is deprecated, remove all_weights and use: M = (weights != 0).sum()
                    denominator = ((M - 1) / M) * total_weights
                    sd = math.sqrt(numerator / denominator)
            else:
                mean = df['Value'].mean()
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

    def write_to_file(self, new_df):
        new_df.to_csv(path_or_buf=self.filename, index=False)
        self._read_csv(filename=self.filename)

    def reload_from_file(self):
        self._read_csv(filename=self.filename)
