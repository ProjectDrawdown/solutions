"""Return objects for solutions."""

import importlib
import os
import pandas as pd

def all_solutions():
    overview = pd.read_csv(os.path.join('data', 'overview', 'solutions.csv'),
            index_col=False, skipinitialspace=True, header=0, skip_blank_lines=True, comment='#')
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
