"""Health & Education solution model
   Excel filename: CORE_PopulationChange_29Jan2020 (version 1.4).xlsx
"""
import pathlib

import numpy as np
import pandas as pd

# import solarpvutil
import electricity_cluster

DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]


class Scenario:
    name = name
    # solution_category = solution_category

    def __init__(self, scenario=None):

        self.elec = electricity_cluster.Scenario()

