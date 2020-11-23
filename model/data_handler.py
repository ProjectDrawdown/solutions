""" Super class to contain and manage data """
import pandas as pd
import numpy as np
import copy

class DataHandler:

    def clean_nan(dataframe):
        """ It replaces NaN values by 0 """
        if(dataframe is None):
            return {}

        dataframe = dataframe.fillna(0)
        return dataframe

    def to_json(self, clean_nan=clean_nan):
        outputs = dict()
        obj_vars = dir(self)
        for k in obj_vars:
            func = getattr(self, k)
            if hasattr(func, 'wrapped'):
                data = func()
                frame = {}
                if data is not None:
                    for level1 in data.keys():
                        if isinstance(level1, np.int64):
                            label = str(level1)
                            frame[label] = data[level1]
                    if len(frame.keys()) > 0:
                        data = frame
                outputs[k] = clean_nan(data)
        return outputs

    def make_str(x):
        if isinstance(x, np.int64):
            return str(x)
        return x
