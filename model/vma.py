"""Implementation of the Variable Meta-Analysis module."""

import math
from pathlib import Path
import re
import numpy as np
import pandas as pd
import json
import warnings
import model.dd

VMA_columns = ['Value', 'Raw', 'Raw Units', 'Weight', 'Exclude?', 'Region', 'Main Region', 'TMR']


# Stuff that would be interesting to do:
# (5) Instead of mean/+sd/-sd, it seems like what we really want is median/80-percentile/20-percentile
# Then you don't need all this standard deviation and outlier management?   Weighting is still possible.
# (6) Add all the Excel columns into the python datastructure, and create a decent in-python (in-Jupyter) browsing/editing
# experience for it.
# (7) Along with ^^^, allow the attachment of real conversion functions.
# (8) Enable automatic conversion of standard types units
# (9) Enable caching of computed conversions and summaries (with save)


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

def normalize_units(val):
    # There's lots to do here, potentially, but just build this out as needed
    if val:
        val = str(val).strip()
        val = re.sub(r'\s+',' ', val)         # collapse multiple spaces
        val = re.sub(r'\s*/\s*', '/', val)    # normalize to no spaces aroud '/'
    
    # Probably end up splitting on '/' and normalizing each part individually then putting the result back together
    return val


class VMA:
    """Meta-analysis of multiple data sources to a summary result."""

    title : str = None
    filename : str = None
    df : pd.DataFrame = None
    """The source data for this VMA."""
    units : str = None

    def __init__(self, filename, title=None, low_sd=1.0, high_sd=1.0,
                 discard_multiplier=3, stat_correction=None, use_weight=False,
                 bound_correction=None,
                 description=None, units=None):
        """Arguments:
         filename: (string, pathlib.Path, or io.StringIO) Can be either
           * Path to a CSV file containing data sources. The CSV file must
             contain columns named "Raw Data Input", "Weight", and "Original
             Units". It can contain additional columns, which will be ignored.
           * io.StringIO objects are processed as if they are opened CSV files
         title: string, name of the VMA to extract from an Excel file. This
           value is unused if filename is a CSV. Will raise an AssertionError
           if the title is not available in the Excel file.
         low_sd: number of multiples of the stddev to use for the low result.
         high_sd: number of multiples of the stddev to use for the high result.
         discard_multiplier: discard outlier values more than this many multiples of the
           stddev away from the mean.
         stat_correction: discard outliers more than discard_multiplier stddev away from the mean.
         use_weight: if true, use weights provided with the VMA to bias the mean.
         bound_correction: if true, and the low value calculated with standard deviation would be negative, 
         use min instead of sd on on the lower value.
         description: optional description of what this VMA describes
         units: the units to use for this VMA; retrieved from datafile by default
        """
        self.filename = filename
        self.title = title
        self.low_sd = low_sd
        self.high_sd = high_sd
        self.discard_multiplier = discard_multiplier
        self.stat_correction = stat_correction
        self.use_weight = use_weight
        self.bound_correction = bound_correction
        self.description = description
        self.units = normalize_units(units)

        # COMMENT: this initialization condition below is weird, since it defaults to making stat_correction True
        # if neither stat_correction nor use_weight are specified.  This isn't an abvious conclusion from the 
        # argument definitions, and also doesn't match the default setting for stat_correction in the Excel VMA template.
        # I would simplify this to just:    self.stat_correction = stat_correction
        # since if use_weight is specified as True, then the default (False) state of stat_correction is what you 
        # will get anyway. 
        #
        # The reason I don't simply make this change is because it would mean reviewing every single 
        # VMA initialization in the existing code to determine if they are using the "trick" to set stat_correction 
        # to True, instead of explicitly setting stat_correction directly.  (Given that I never see stat_correction
        # in initializers, I expect this is happening a lot.)
        #
        # Update: the reason this is probably done this way is because the setting for stat_correction isn't on the
        # VMA page, it is on the AC page where the VMA is used.  Complex to update the code to extract this properly for now.
        
        if stat_correction is None:
            # Excel does not discard outliers if weights are used, we do the same by default.
            self.stat_correction = not use_weight
        else:
            self.stat_correction = stat_correction

        self.df = pd.DataFrame(columns=VMA_columns)

        if filename:
            if isinstance(filename,str):   # don't convert StringIO!
                filename = Path(filename)
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
        csv_df = pd.read_csv(filename, index_col=False, skipinitialspace=True, skip_blank_lines=True,
                             na_values=['#DIV/0!', '#REF!'])
        self._convert_from_human_readable(csv_df, filename)

 
    def _convert_from_human_readable(self, readable_df, filename):
        """
        Converts a known set of readable column names to a known column set. A
        few data cleanups are also performed, such as converting percentages
        and filling NaN values.

        Arguments:
            readable_df: dataframe (from CSV or Excel file) using the standard
                long-form column names
            filename: Path to source file, passed through for error
                transparency purposes

        Populates self.source_data with readable_df directly. Populates self.df
        with a series of renamed columns, along with a few data cleanup steps.
        """
        self._validate_readable_df(readable_df)
        self.source_data = readable_df
        if self.use_weight:
            err = f"'Use weight' selected but no weights to use in {filename}"
            assert not all(pd.isnull(readable_df['Weight'])), err
        self.df['Weight'] = readable_df['Weight'].apply(convert_percentages)
        self.df['Raw'] = readable_df['Raw Data Input'].apply(convert_percentages)
        self.df['Raw Units'] = readable_df['Original Units']
        
        self.df['Value'] = readable_df['Conversion calculation'].apply(convert_NaN)
        self.df['Value'].fillna(self.df['Raw'], inplace=True)
        if self.units is None:
            aunit = readable_df['Common Units'].first_valid_index()
            if aunit is not None:
                self.units = normalize_units( readable_df['Common Units'].loc[ aunit ] )
 
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


    def _validate_readable_df(self, readable_df):
        if readable_df is None:
            if self.title is None:
                source = f"\n\tFile: {self.filename}\n"
            else:
                source = f"\n\tFile: {self.filename}\n\tTitle: {self.title!r}\n"
            raise ValueError("Dataframe from" + source + "is None, is that VMA empty?")

    def _discard_outliers(self, discard_multiplier):
        """Discard outlier values beyond a multiple of the stddev."""
        df = self.df
        mean = df['Value'].astype('float64').mean(skipna=True)
        sd = df['Value'].std(ddof=0)
        if pd.isna(mean) or pd.isna(sd):
            return df
        valid = df['Value'] <= (mean + (discard_multiplier * sd))
        df = df[valid]
        valid = df['Value'] >= (mean - (discard_multiplier * sd))
        df = df[valid]
        return df

    def avg_high_low(self, statistic=None, regime=None, region=None,
                    low_sd=None, high_sd=None, discard_multiplier=None, 
                    stat_correction=None, use_weight=None, bound_correction=None):
        """
        Args:
          statistic: (optional) specify 'mean', 'high' or 'low' to get single value
          regime: string name of the thermal moisture regime to select sources for.
          region: string name of the world region to select sources for.
          Other parameters: explicitly override the default parameters for this VMA.

        Returns:
          By default returns (mean, high, low) using low_sd/high_sd.
          If statistic is specified will return associated value only
        """
        # Use the parameters if provided, our defaults if not.
        low_sd = self.low_sd if low_sd is None else low_sd
        high_sd = self.high_sd if high_sd is None else high_sd
        discard_multiplier = self.discard_multiplier if discard_multiplier is None else discard_multiplier
        stat_correction = self.stat_correction if stat_correction is None else stat_correction
        use_weight = self.use_weight if use_weight is None else use_weight
        bound_correction = self.bound_correction if bound_correction is None else bound_correction

        if use_weight:
            # Sum the weights before discarding outliers, to match Excel.
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.qkdzs364y2t2
            # Once reproducing Excel results is no longer essential, total_weight computation
            # can be moved down to the second use_weight conditional below. That way the sum
            # of the weights will only include sources which are being included in the mean.
            total_weights = self.df['Weight'].fillna(1.0).sum()
            total_weights = total_weights if total_weights != 0.0 else 1.0
            all_weights = self.df['Weight'].fillna(1.0)
            M = (all_weights != 0).sum()

        if self.df.empty:
            mean = high = low = np.nan
        else:
            df = self._discard_outliers(discard_multiplier) if stat_correction else self.df
            df = df.loc[df['Exclude?'] == False]
            if regime:
                df = df.loc[df['TMR'] == regime]
            if region in model.dd.SPECIAL_COUNTRIES:
                df = df.loc[df['Region'] == region]
            elif region in model.dd.MAIN_REGIONS:
                # include values for special countries in corresponding main regions' statistics
                df = df.loc[df['Main Region'] == region]

            if use_weight:
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

            high = mean + (high_sd * sd)
            low = mean - (low_sd * sd)
            if low < 0 and bound_correction:
                low = min( df['Value'] )

        if statistic is None:
            return mean, high, low
        elif statistic == 'high':
            return high
        elif statistic == 'mean' or statistic == 'average' or statistic == 'avg':
            return mean
        elif statistic == 'low':
            return low
        else:
            raise ValueError(f"invalid statistic: {statistic}. key must be 'mean', 'high', 'low' or None")

    def write_to_file(self, new_df):
        new_df.to_csv(path_or_buf=self.filename, index=False, encoding='utf-8')
        self._read_csv(filename=self.filename)

    def reload_from_file(self):
        self._read_csv(filename=self.filename)
    
    def essential_parameters(self):
        """Return a dictionary of "essential" parameters, that is parameters whose value differs from the default"""
        result = {}
        result['title'] = self.title
        if isinstance(self.filename, Path): result['filename'] = str(self.filename)
        if self.low_sd != 1.0: result['low_sd'] = self.low_sd
        if self.high_sd != 1.0: result['high_sd'] = self.high_sd
        if self.discard_multiplier != 3: result['discard_multiplier'] = self.discard_multiplier
        # Currently skip this since it is *always* calculated indirectly (and probalby sometimes wrongly)
        # if self.stat_correction: result['stat_correction'] = True
        if self.use_weight: result['use_weight'] = True
        if self.bound_correction: result['bound_correction'] = True
        if self.description is not None and self.description != "": result['description'] = self.description
        if self.units is not None and self.units != "": result['units'] = self.units
        return result
 

    @classmethod
    def load_vma_directory(cls, directoryfile):
        """Load and return an array of VMAs that are defined in a directory json-file"""
        directoryfile = Path(directoryfile)
        directorycontent = json.loads(directoryfile.read_text(encoding='utf-8'))
        result = {}
        for vmatitle in directorycontent.keys():
            vmargs = directorycontent[vmatitle]
            if not vmargs.get('filename',False):
                warnings.warn(f"Skipping VMA {vmatitle} because no filename found")
                continue
            vmargs['filename'] = directoryfile.with_name(vmargs['filename'])
            vmargs['title']=vmatitle
            vma = cls(**vmargs)
            result[vmatitle]=vma
        return result

    @classmethod
    def write_vma_directory(cls, vmacollection, directory):
        """Write out the directory file for this collection of VMAs.  The directory file will only
        have entries for VMAs that have files _in this directory_.  Global VMAs, if present, will be omitted (and a warning will be issued)."""
        directory = Path(directory).resolve()
        directoryinfo = {}
        for title, vma in vmacollection.items():
            params = vma.essential_parameters()
            if 'filename' not in params:
                continue
            filename = Path(params['filename'])
            if filename.parent.resolve() != directory:
                warnings.warn(f"Skipping VMA {title} that is in {filename.parent.resolve()}")
                continue
            params['filename'] = filename.name # remove directory info
            if not params.get('title',False):
                params['title'] = title
            directoryinfo[title] = params
        directoryfile = Path(directory)/"vma_sources.json"
        directoryfile.write_text(json.dumps(directoryinfo, indent=2))

