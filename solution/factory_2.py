"""Return objects for solutions."""
import importlib
import pathlib

import pandas as pd

from model.advanced_controls import AdvancedControls

def all_solutions():
    path = pathlib.Path(__file__).parents[1].joinpath('data', 'overview', 'solutions.csv')
    overview = pd.read_csv(path, index_col=False, skipinitialspace=True, header=0,
            skip_blank_lines=True, comment='#')
    return sorted(overview['DirName'].dropna().tolist())

def one_solution_scenarios(solution, j):
    importname = 'solution.' + solution
    m = importlib.import_module(importname)
    if len(m.scenarios) > 1:
        replacement_scenarios = {}
        j['vmas'] = m.VMAs
        # j['js'] = j
        # j['jsfile'] = str(filename)
        replacement_scenarios[j['name']] = AdvancedControls(**j)
        m.scenarios = replacement_scenarios
    return (m.Scenario, list(m.scenarios.keys()))

def all_solutions_scenarios(scenarios):
    everything = {}
    for scenario in scenarios:
        solution_name = scenario['tech']
        everything[solution_name] = one_solution_scenarios(solution_name, scenario['json'])
    return everything
