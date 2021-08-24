"""Return objects for solutions."""

import importlib
from pathlib import Path
from functools import lru_cache

def all_solutions():
    # Find all the directories containing an __init__.py
    # The __init__.py check is needed because git doesn't remove empty directories, so if you switch
    # to a branch that doesn't have the solution, you end up with an empty directory.
    # Checking that there is an __init__.py file fixes that case.
    candidates = [ d.name for d in Path(__file__).parent.glob('*') if d.is_dir() and (d/'__init__.py').is_file() ]
   
    # The above test is sufficient, but to be nice, allow for two more ways to make something not a solution
    return [ name for name in candidates if not name.startswith('_') and not name.startswith('test') ]

def list_scenarios(solution):
    """Return a list of scenarios for this solution"""
    m = _load_module(solution)
    return list(m.scenarios.keys())

def load_scenario(solution, scenario=None):
    """Load a scenario for the requested solution.  Scenario may be one of the following:
     * None (the default): return the PDS2 scenario for this solution
     * `PDS`, `PDS2` or `PDS3`:  get the most recent scenario of the requested type
     * a scenario name:  load the scenario with that name
     * an Advanced_Controls object:  load a completely custom scenario based on the data in the object"""
    m = _load_module(solution)
    if scenario in ['PDS1','PDS2','PDS3']:
        md = {'PDS1': m.PDS1, 'PDS2': m.PDS2, 'PDS3': m.PDS3}
        scenario = md[scenario]
    return m.Scenario(scenario)

@lru_cache()
def _load_module(solution):
    """Return the Scenario class and list of scenarios."""
    importname = 'solution.' + solution
    m = importlib.import_module(importname)
    return m

def all_solutions_scenarios():
    everything = {}
    for solution in all_solutions():
        everything[solution] = list_scenarios(solution)
    return everything
