""" Super class to contain and manage data """
import pandas as pd
import numpy as np

class DataHandler:

    def to_json(self):
        var_keys = vars(self).keys()
        outputs = dict()
        obj_vars = dir(self)
        obj_vars.remove('to_json')
        for k in obj_vars:
            func = getattr(self, k)
            if(not k.startswith('__') and hasattr(func, 'wrapped')):
                outputs[k] = clean_nan(func())
        return outputs

def data_func(method):
    method.wrapped = True
    return method

def clean_nan(dataframe):
    for year in dataframe.keys():
        if (np.isnan(dataframe[year])):
            dataframe[year] = 0.0
    return dataframe
