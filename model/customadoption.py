""" Custom PDS/REF Adoption module """

from functools import lru_cache
from model import metaclass_cache
from model.dd import REGIONS
import pandas as pd
import numpy as np

pd.set_option('display.expand_frame_repr', False)
YEARS = list(range(2012, 2061))


def generate_df_template():
    """ Returns DataFrame to be populated by adoption data """
    df = pd.DataFrame(index=YEARS, columns=REGIONS, dtype=np.float64)
    df.index = df.index.astype(int)
    df.index.name = 'Year'
    return df


class CustomAdoption:
    """
    Equivalent to Custom PDS and REF Adoption sheets in xls. Allows user to input custom adoption
    scenarios. The data can be raw or generated from a script within the solution directory.

    Arguments:
         data_sources: a list of group names which contain dicts of data source names.
            For example:
                [
                  {'name': 'Study Name A', 'filename': 'filename A', 'include': boolean},
                  {'name': 'Study Name B',{'filename': 'filename B', 'include': boolean},
                  ...
                ]
         soln_adoption_custom_name: from advanced_controls. Can be avg, high, low or a specific source.
            For example: 'Average of All Custom PDS Scenarios'
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
            filename = d.get('filename', 'no_such_file')
            include = d.get('include', True)
            df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
                             skip_blank_lines=True, comment='#', dtype=np.float64)
            df.index = df.index.astype(int)
            df.index.name = 'Year'
            assert list(df.columns) == REGIONS
            assert list(df.index) == YEARS
            self.scenarios[name] = {'df': df, 'include': include}
        self.soln_adoption_custom_name = soln_adoption_custom_name

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
            avg_df = avg_df.combine(self.total_adoption_limit, np.fmin)
            high_df = high_df.combine(self.total_adoption_limit, np.fmin)
            low_df = low_df.combine(self.total_adoption_limit, np.fmin)
        return avg_df, high_df, low_df

    @lru_cache()
    def adoption_data_per_region(self):
        """ Return a dataframe of adoption data, one column per region. """

        if self.soln_adoption_custom_name.startswith('Average of All Custom'):
            (result, _, _) = self._avg_high_low()
        elif self.soln_adoption_custom_name.startswith('Low of All Custom'):
            (_, _, result) = self._avg_high_low()
        elif self.soln_adoption_custom_name.startswith('High of All Custom'):
            (_, result, _) = self._avg_high_low()
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
