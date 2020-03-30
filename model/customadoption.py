""" Custom PDS/REF Adoption module """

from functools import lru_cache
from model.metaclass_cache import MetaclassCache
import model.dd as dd
import pandas as pd
import numpy as np

pd.set_option('display.expand_frame_repr', False)
YEARS = list(range(2012, 2061))


def generate_df_template():
    """ Returns DataFrame to be populated by adoption data """
    df = pd.DataFrame(index=YEARS, columns=dd.REGIONS, dtype=np.float64)
    df.index = df.index.astype(int)
    df.index.name = 'Year'
    return df


class CustomAdoption(object, metaclass=MetaclassCache):
    """
    Equivalent to Custom PDS and REF Adoption sheets in xls. Allows user to input custom adoption
    scenarios. The data can be raw or generated from a script within the solution directory.

    Arguments:
         data_sources: a list of group names which contain dicts of data source names.
            For example:
                [
                  {'name': 'Study Name A', 'filename': 'filename A', 'include': boolean},
                  {'name': 'Study Name B', 'filename': 'filename B', 'include': boolean},
                  {'name': 'Study Name C', 'include': boolean,
                     'datapoints': pd.DataFrame([
                         [2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                         [2060, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
                         ], columns=ca_pds_columns).set_index('Year')
                  },
                  {'name': 'Study Name D', 'include': boolean, 'growth_rate': 0.0132,
                     'growth_initial': pd.DataFrame([
                         [2014, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
                         ], columns=ca_pds_columns).set_index('Year')
                  }

                  ...
                ]
                where ca_pds_columns = ['Year'] + dd.REGIONS

         soln_adoption_custom_name: from advanced_controls. Can be avg, high, low or a specific
            source. For example: 'Average of All Custom PDS Scenarios'
         low_sd_mult: std deviation multiplier for 'low' values
         high_sd_mult: std deviation multiplier for 'high' values
         total_adoption_limit: the total adoption possible, adoption can be no greater than this.
            For RRS solutions this is typically tam.py:{pds,ref}_tam_per_region. For Land solutions
            this is typically tla.py:tla_per_region.
            The columns in total_adoption_limit must match the columns in generate_df_template.
    Generates average/high/low of chosen scenarios to be used as adoption data for the solution.
    """

    def __init__(self, data_sources, soln_adoption_custom_name, low_sd_mult=1, high_sd_mult=1,
                 total_adoption_limit=None):
        self.low_sd_mult = low_sd_mult
        self.high_sd_mult = high_sd_mult
        self.total_adoption_limit = total_adoption_limit
        self.scenarios = {}
        for d in data_sources:
            name = d.get('name', 'noname')
            include = d.get('include', True)
            filename = d.get('filename', None)
            datapoints = d.get('datapoints', None)
            growth_rate = d.get('growth_rate', None)
            n = 0
            if filename is not None:
                df = self._read_csv(filename)
                n = n + 1
            if datapoints is not None:
                df = self._linear_forecast(datapoints=datapoints, start_year=2012, end_year=2060)
                n = n + 1
            if growth_rate is not None:
                growth_initial = d.get('growth_initial', None)
                df = self._growth_forecast(rate=growth_rate, initial=growth_initial,
                        start_year=2012, end_year=2060)
                n = n + 1
            assert n <= 1, "Only one of filename, datapoints, or growth_rate may be used"
            self.scenarios[name] = {'df': df, 'include': include}
        self.soln_adoption_custom_name = soln_adoption_custom_name


    def _read_csv(self, filename):
        """Read in a CSV file from filename."""
        df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
                         skip_blank_lines=True, comment='#', dtype=np.float64)
        df.index = df.index.astype(int)
        df.index.name = 'Year'
        assert list(df.columns) == dd.REGIONS, f"unknown columns: {list(df.columns)}"
        assert list(df.index) == YEARS, f"unknown index: {list(df.index)}"
        return df


    def _linear_forecast(self, datapoints, start_year, end_year):
        """Interpolates a line between datapoints, and fills in a dataframe.
           datapoints: a Pandas DataFrame with 2+ rows of adoption data, indexed by year.
             The columns are expected to be regions like 'World', 'EU', 'India', etc.
             The year+adoption data provide the X,Y coordinates for a line to interpolate.
           start_year: year the trend should begin, sometimes earlier than the first datapoint
           end_year: year the trend should extend to, usually past the last datapoint
        """
        df = pd.DataFrame(columns=datapoints.columns, dtype='float')
        for col in df.columns:
            for i in range(datapoints.index.size - 1):
                year1 = datapoints.index[i]
                year2 = datapoints.index[i+1]
                adopt1 = datapoints.loc[year1, col]
                adopt2 = datapoints.loc[year2, col]
                for year in range(year1, year2 + 1):
                    fract_year = (float(year) - float(year1)) / (float(year2) - float(year1))
                    fract_adopt = fract_year * (float(adopt2) - float(adopt1))
                    df.loc[year, col] = adopt1 + fract_adopt

        last_year = df.index[-1]
        year0 = datapoints.index[-2]
        year1 = datapoints.index[-1]
        adopt0 = datapoints.iloc[-2]
        adopt1 = datapoints.iloc[-1]
        adopt_per_year = (adopt1 - adopt0) / float(year1 - year0)
        for year in range(last_year + 1, end_year + 1):
            df.loc[year] = adopt1 + (float(year - year1) * adopt_per_year)

        first_year = df.index[0]
        year0 = datapoints.index[0]
        year1 = datapoints.index[1]
        adopt0 = datapoints.iloc[0]
        adopt1 = datapoints.iloc[1]
        adopt_per_year = (adopt1 - adopt0) / float(year1 - year0)
        for year in range(first_year - 1, start_year - 1, -1):
            df.loc[year] = (adopt0 - (float(year0 - year) * adopt_per_year)).clip(lower=0.0)

        if self.total_adoption_limit is not None:
            df = df.combine(self.total_adoption_limit, np.fmin)

        df.index = df.index.astype(int)
        df.index.name = 'Year'
        return df.sort_index()

    def _growth_forecast(self, rate, initial, start_year, end_year):
        """Computes a line from an initial datapoint, and fills in a dataframe.
           rate: floatng point number at which the initial dataframe should grow.
           initial: a Pandas DataFrame of adoption data, indexed by year.
             The columns are expected to be regions like 'World', 'EU', 'India', etc.
             This dataframe can contain multiple rows; only the first row will be used.
           start_year: year the trend should begin, sometimes earlier than the first datapoint
           end_year: year the trend should extend to, usually past the last datapoint
        """
        # In Excel, the first datapoint is always used as 2014 to compute the growth until 2060.
        # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.u0yuiva79mg1
        final = initial.copy()
        linear = initial.copy()
        for y in range(2015, 2051):
            final = final * (1 + rate)
        linear.loc[2050] = final.iloc[0]

        year1 = initial.index[0]
        df = self._linear_forecast(datapoints=linear, start_year=year1, end_year=end_year)

        # years prior to the initial datapoint are set equal to the initial datapoint
        for y in range(start_year, year1+1):
            df.loc[y] = initial.iloc[0]

        return df.sort_index()


    def _avg_high_low(self):
        """ Returns DataFrames of average, high and low scenarios. """
        regions_to_avg = {}
        for name, scen in self.scenarios.items():
            if scen['include']:
                scen_df = scen['df'].dropna(axis=1, how='all')  # ignore null columns (i.e. blank regional data)
                for reg in scen_df.columns:
                    if reg not in regions_to_avg:
                        regions_to_avg[reg] = pd.DataFrame({name: scen_df[reg]})
                    else:  # build regional df
                        regions_to_avg[reg][name] = scen_df[reg]
        avg_df, high_df, low_df = generate_df_template(), generate_df_template(), generate_df_template()
        for reg, reg_df in regions_to_avg.items():
            avg_df[reg] = avg_vals = reg_df.mean(axis=1)
            high_df[reg] = avg_vals + reg_df.std(axis=1, ddof=0) * self.high_sd_mult
            low_df[reg] = avg_vals - reg_df.std(axis=1, ddof=0) * self.low_sd_mult
        if self.total_adoption_limit is not None:
            idx = self.total_adoption_limit.first_valid_index()
            avg_df.loc[idx:, :] = avg_df.loc[idx:, :].combine(self.total_adoption_limit, np.minimum)
            high_df.loc[idx:, :] = high_df.loc[idx:, :].combine(self.total_adoption_limit, np.minimum)
            low_df.loc[idx:, :] = low_df.loc[idx:, :].combine(self.total_adoption_limit, np.minimum)
        return avg_df, high_df, low_df

    @lru_cache()
    def adoption_data_per_region(self):
        """ Return a dataframe of adoption data, one column per region. """
        if self.soln_adoption_custom_name.startswith('Average of All Custom'):
            (result, _, _) = self._avg_high_low()
        elif self.soln_adoption_custom_name.startswith('High of All Custom'):
            (_, result, _) = self._avg_high_low()
        elif self.soln_adoption_custom_name.startswith('Low of All Custom'):
            (_, _, result) = self._avg_high_low()
        elif self.soln_adoption_custom_name in self.scenarios:
            data = self.scenarios[self.soln_adoption_custom_name]
            result = data['df'].copy()
        else:
            raise ValueError('Unknown adoption name: ' + str(self.soln_adoption_custom_name))
        result.name = 'adoption_data_per_region'
        return result

    @lru_cache()
    def adoption_trend_per_region(self):
        """
        Return a dataframe of adoption trends, one column per region.

        For custom adoption data, no trend curve fitting is done.
        We return the custom data.
        """
        return self.adoption_data_per_region()

    def report(self, adoption_limits=None):
        """
        Provides information on two potential issues with the scenarios:
            1) Checks if any of the regions exceed their adoption limits
            2) Checks if the sum of the main regions matches the corresponding World value
        Args:
            adoption_limits: optionally input adoption limits for check #1

        Returns:
            A DataFrame summary of the checks for each scenario and a data dict.
            The data dict has the scenarios as keys and dicts of the following format as values:
               {'amount exceeded': DataFrame (rows = years, cols = regions) containing the amount each datapoint
                                   exceeds that region's limit (NaN if it is under the limit).
                'adoption ratio': Series (index = years) containing the sum of the main regional values divided
                                  by the corresponding World value for each year (should be 1). }
        """
        if adoption_limits is None:
            adoption_limits = self.total_adoption_limit
        report_data = {}  # dict of dataframes of detailed results
        report_summary = pd.DataFrame(
            columns=['Has regional data', 'Exceeds limits', 'Regions exceed world', 'World exceeds regions'])
        for name, scen in self.scenarios.items():
            report_data[name] = {}
            if not scen['include']:
                continue  # no need to check excluded scenarios
            df = scen['df'].loc[2020:, :]

            # check if any regional data
            has_regional_data = df.loc[2020:, dd.MAIN_REGIONS].any().any()
            report_summary.loc[name, 'Has regional data'] = has_regional_data

            # check which scenarios exceed the given regional adoption limits
            if adoption_limits is not None:
                # use slightly higher limits to avoid tiny amounts of overlap when data is clipped to limits
                limits_diff = (1.01 * adoption_limits - df).fillna(0)
                amount_exceeded = -limits_diff[limits_diff < 0]
                report_data[name]['amount exceeded'] = amount_exceeded
                report_summary.loc[name, 'Exceeds limits'] = True if amount_exceeded.any().any() else False

            # check ratio of the sum of the main regions to world region (should be ~1)
            if has_regional_data:
                adoption_ratio = df.loc[2020:, dd.MAIN_REGIONS].sum(axis=1) / df.loc[:, 'World']
                report_data[name]['adoption ratio'] = adoption_ratio
                # we allow a tolerance of 1%
                report_summary.loc[name, 'Regions exceed world'] = adoption_ratio[adoption_ratio > 1.01].any()
                report_summary.loc[name, 'World exceeds regions'] = adoption_ratio[adoption_ratio < 0.99].any()

        report_summary.index.rename('Custom adoption scenario', inplace=True)
        return report_summary, report_data
