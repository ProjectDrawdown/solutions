
from numpy import float64
import pandas as pd
from pandas.core.indexes.range import RangeIndex

import model.interpolation as interp

class OceanTam():
    _tam: pd.Series

    def __init__(self, base_year, last_year) -> None:
        
        self.base_year = base_year
        self.last_year = last_year
        
        series = pd.Series(index= RangeIndex(base_year, last_year), dtype=float64)
        self._tam = series
    
    def set_tam_linear(self, total_area, change_per_period, total_area_as_of_period = None) -> None:
        
        if total_area_as_of_period is None:
            total_area_as_of_period = self.base_year
        
        m = change_per_period
        c = total_area - m * total_area_as_of_period

        # self.tam_df[region] is a series. Convert this to a dataframe. Then apply a function using straight line formula y = m*x +c.
        # x.name returns index value (the year).
        s = pd.DataFrame(self._tam).apply(lambda x: m * x.name + c, axis='columns')

        self._tam = s
        return 

    def apply_linear_regression(self):

        df = interp.linear_trend(self._tam)

        # #TODO copied the s/sht here to match results. Get agreement on how to set base date.
        # x = np.array(self._tam.index-self.base_year-2).reshape(-1, 1)
        
        # y = np.array(self._tam)

        # model = LinearRegression()
        # model.fit(x, y)

        # y_predicted = model.predict(x)

        # # Write regressed values to the tam
        #column = self._tam.columns[0]
        self._tam = df['adoption'] # self._tam.assign(**{column:y_predicted})

        return
        
    
    def apply_clip(self, lower = None, upper = None):
        if lower == None and upper == None:
            print('Warning : Neither lower nor upper parameter supplied. No action taken.')
        self._tam.clip(lower=lower, upper=upper, inplace=True)

    def get_tam_units(self) -> pd.Series:
        return self._tam.copy()

