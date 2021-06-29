"""Return objects for solutions."""
import importlib
import pathlib
from functools import lru_cache

import pandas as pd

from model.advanced_controls import AdvancedControls


def all_solutions():
    path = pathlib.Path(__file__).parents[1].joinpath('data', 'overview', 'solutions.csv')
    overview = pd.read_csv(path, index_col=False, skipinitialspace=True, header=0,
            skip_blank_lines=True, comment='#')
    return sorted(overview['DirName'].dropna().tolist())

def import_scenario(importname: str):
    # TODO: in some cases, the scenarios in the module is being
    # overwritten to the base scenario instead of importing it
    # from the solutions.<importname>/ac
    return importlib.import_module(importname)

def one_solution_scenarios(solution, j=None):
    """Load the scenarios for a single solution, optionally overriding
    the advanced controls for a single scenario"""
    importname = 'solution.' + solution
    m = import_scenario(importname)
    if j is not None:
        # replace the configuration of scenario j.name with the values in j
        j['vmas'] = m.VMAs
        m.scenarios[j['name']] = AdvancedControls(**j)
    return (m.Scenario, list(m.scenarios.keys()))

def all_solutions_scenarios(scenarios):
    everything = {}
    for scenario in scenarios:
        solution_name = scenario['tech']
        everything[solution_name] = one_solution_scenarios(solution_name)
    return everything
