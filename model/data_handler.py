""" Super class to contain and manage data """
import pandas as pd
import numpy as np

class DataHandler:

    def clean_nan(dataframe):
        if(dataframe is None):
            return {}
        for level1 in dataframe.keys():
            print("Type dataframe")
            print(type(dataframe[level1]))
            if isinstance(dataframe[level1], pd.Series):
                print("Series!")
                for level2 in dataframe[level1].keys():
                    if np.isnan(dataframe[level1][level2]):
                        dataframe[level1][level2] = 0.0
            else:
                if np.isnan(dataframe[level1]):
                    dataframe[level1] = 0.0
        return dataframe

    def to_json(self, clean_nan=clean_nan):
        var_keys = vars(self).keys()
        outputs = dict()
        obj_vars = dir(self)
        for k in obj_vars:
            func = getattr(self, k)
            if hasattr(func, 'wrapped'):
                outputs[k] = clean_nan(func())
        return outputs
