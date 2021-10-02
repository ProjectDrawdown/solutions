
import json
import pandas as pd
from typing import Optional

import model.interpolation as interp

class OceanTam():
    _tam_series: pd.Series

    def __init__(self, base_year: int, start_year: int, end_year: int, tam_input_file: str) -> None:
        
        self.base_year = base_year
        self.start_year = start_year
        self.end_year = end_year

        stream = open(tam_input_file,'r')
        json_dict = json.load(stream)
        
        idx, vals = zip(*json_dict['data']) # list of two-element lists
        self._tam_series = pd.Series(data=vals, index=idx)
        return
    
    def set_tam_linear(self, total_area: float, change_per_period: float, total_area_as_of_period: Optional[int] = None) -> None:
        
        if total_area_as_of_period is None:
            total_area_as_of_period = self.base_year
        
        m = change_per_period
        c = total_area - m * total_area_as_of_period

        # self.tam_df[region] is a series. Convert this to a dataframe. Then apply a function using straight line formula y = m*x +c.
        # x.name returns index value (the year).
        series = pd.DataFrame(self._tam_series).apply(lambda x: m * x.name + c, axis='columns')

        self._tam_series = series
        return 

    def apply_linear_regression(self):

        df = interp.linear_trend(self._tam)
        self._tam_series = df['adoption']

        return
        
    def apply_3d_poly(self):
        df = interp.poly_degree3_trend(self._tam_series)
        self._tam_series = df['adoption']


    def apply_clip(self, lower = None, upper = None) -> None:
        if lower == None and upper == None:
            print('Warning : Neither lower nor upper parameter supplied. No action taken.')
        self._tam_series.clip(lower=lower, upper=upper, inplace=True)

    def get_tam_series(self) -> pd.Series:
        return self._tam_series.copy()

