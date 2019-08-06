"""Return objects for solutions."""

import importlib
import os
import pathlib

import pandas as pd

def all_solutions():
    path = pathlib.Path(__file__).parents[1].joinpath('data', 'overview', 'solutions.csv')
    overview = pd.read_csv(path, index_col=False, skipinitialspace=True, header=0,
            skip_blank_lines=True, comment='#')
    return sorted(overview['DirName'].dropna().tolist())


def one_solution_scenarios(solution):
    importname = 'solution.' + solution
    m = importlib.import_module(importname)
    return (m.Scenario, list(m.scenarios.keys()))


def all_solutions_scenarios():
    everything = {}
    for solution in all_solutions():
        everything[solution] = one_solution_scenarios(solution)
    return everything
