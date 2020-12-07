""" Super class to contain and manage data """
import pandas as pd
import numpy as np
import copy

class DataHandler:

    def clean_nan(dataframe):
        """ It replaces NaN values by 0 """
        if(dataframe is None):
            return {}

        dataframe = dataframe.replace([np.inf, -np.inf], np.nan)
        dataframe = dataframe.fillna(0)
        return dataframe

    def to_json(self, clean_nan=clean_nan):
        outputs = dict()
        obj_vars = dir(self)
        for k in obj_vars:
            func = getattr(self, k)
            if hasattr(func, 'wrapped'):
                data = func()
                if data is not None:
                    for level1 in data.keys():
                        if isinstance(level1, np.int64):
                            label = str(level1)
                            data[label] = data[level1]
                            del data[level1]
                outputs[k] = clean_nan(data)

        return outputs

    def make_str(x):
        if isinstance(x, np.int64):
            return str(x)
        return x
