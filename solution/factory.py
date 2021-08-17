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


@lru_cache()
def one_solution_scenarios(solution):
    importname = 'solution.' + solution
    m = importlib.import_module(importname)
    return (m.Scenario, list(m.scenarios.keys()))


def solution_pds_type(solution, pds_type):
    """Return the standard scenario for solution of type pds_type, where pds_type is one of
    'PDS1', 'PDS2', 'PDS3'"""
    importname = 'solution.' + solution
    m = importlib.import_module(importname)       
    if pds_type == "PDS1":
        return m.Scenario(m.PDS1)
    if pds_type == "PDS2":
        return m.Scenario(m.PDS2)
    if pds_type == "PDS3":
        return m.Scenario(m.PDS3)
    raise ValueError("Scenario type not one of 'PDS1', 'PDS2' or 'PDS3'")


def all_solutions_scenarios():
    everything = {}
    for solution in all_solutions():
        everything[solution] = one_solution_scenarios(solution)
    return everything


def all_solutions_scenario_type(scenario_type):
    everything = {}
    for solution in all_solutions():
        everything[solution] = solution_pds_type(scenario_type)
    return everything
