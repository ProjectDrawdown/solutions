
import pandas as pd
from pandas.core.indexes.range import RangeIndex

class OceanTam():
    _tam_df: pd.DataFrame

    def __init__(self, base_year, last_year, regions = ['World']) -> None:
        self.base_year = base_year
        self.last_year = last_year
        self.regions = regions

        df = pd.DataFrame(columns=regions, index= RangeIndex(base_year, last_year))
        self._tam_df = df
    
    def set_tam_linear(self, total_area, change_per_period, total_area_as_of_period = None, regions = 'World'):
        
        if regions is None:
            regions = self._tam_df.columns
            print(f'Warning, no explicit region supplied, using region {self.region}')

        if total_area_as_of_period is None:
            total_area_as_of_period = self.base_year
        
        m = change_per_period
        c = total_area - m * total_area_as_of_period

        # self.tam_df[region] is a series. Convert this to a dataframe. Then apply a function using straight line formula y = m*x +c.
        # x.name returns index value (the year).
        s = pd.DataFrame(self._tam_df[regions]).apply(lambda x: m * x.name + c, axis='columns')

        self._tam_df[regions] = pd.DataFrame(s)
    
    def apply_clip(self, lower = None, upper = None):
        if lower == None and upper == None:
            print('Warning : Neither lower nor upper parameter supplied. No action taken.')
        self._tam_df.clip(lower=lower, upper=upper)

    def get_tam_units(self, region = None) -> pd.DataFrame:
        if region is None:
            region = self._tam_df.columns[0]

        return self._tam_df.loc[:,region].copy()

