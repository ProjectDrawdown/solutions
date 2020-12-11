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
            if hasattr(func, 'data_func'):
                data = func()
                if data is not None and (isinstance(data, pd.DataFrame) or isinstance(data, pd.Series)):
                    for l in data.keys():
                        if isinstance(l, np.int64):
                            label = str(l)
                            data[label] = data[l]
                            del data[l]
                    outputs[k] = clean_nan(data)
                else:
                    outputs[k] = data
        return outputs
