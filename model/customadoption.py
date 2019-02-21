""" Custom PDS/REF Adoption module """

import pandas as pd
import numpy as np
pd.set_option('display.expand_frame_repr', False)

REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China',
           'India', 'EU', 'USA']
YEARS = list(range(2012, 2061))


def generate_df_template():
    """ Returns DataFrame to be populated by adoption data """
    df = pd.DataFrame(index=YEARS, columns=REGIONS, dtype=np.float64)
    df.index = df.index.astype(int)
    df.index.name = 'Year'
    return df


class CustomAdoption:
    """
    Related to Custom PDS and REF Adoption sheets in xls. Allows user to input custom adoption
    scenarios. The data can be raw or generated from a script within the solution directory.

    Generates average/high/low of chosen scenarios to be used as adoption data for the solution.
    """
    def __init__(self):
        self.scenarios = []

    def add_scenario(self, name, adoption_df, include=True):
        """
        Use generate_df_template() to generate a DataFrame with the correct fields (years, regions).
        Regional data can be left as NaNs if not applicable (do not set as 0!). If adoption data is
        generated from assumptions, include these and your calculations in the solution directory.

        This function also validates scenarios to prevent errors in calculating stats later.

        Set include to False if you don't want to include this data in the adoption calculation.
        """
        assert list(adoption_df.columns) == REGIONS
        assert list(adoption_df.index) == YEARS
        self.scenarios.append({'name': name, 'df': adoption_df, 'include': include})

    def _avg_high_low(self, num_sds=1):
        """
        Returns DataFrames of average, high and low scenarios.
        num_sds is the number of standard deviations for the high/low values.
        """
        regions_to_avg = {}
        for scen in self.scenarios:
            if scen['include']:
                scen_df = scen['df'].dropna(axis=1)  # ignore null columns (i.e. blank regional data)
                for reg in scen_df.columns:
                    if reg not in regions_to_avg:
                        regions_to_avg[reg] = pd.DataFrame({scen['name']: scen_df[reg]})
                    else:  # build regional df
                        regions_to_avg[reg][scen['name']] = scen_df[reg]

        avg_df, high_df, low_df = generate_df_template(), generate_df_template(), generate_df_template()
        for reg, reg_df in regions_to_avg.items():
            avg_df[reg] = avg_vals = reg_df.mean(axis=1)
            offset = reg_df.std(axis=1, ddof=0) * num_sds
            high_df[reg] = avg_vals + offset
            low_df[reg] = avg_vals - offset
        return avg_df, high_df, low_df

