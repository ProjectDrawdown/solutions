"""Return objects for solutions."""

import importlib
from pathlib import Path
from functools import lru_cache

def all_solutions():
    candidates = [ d.name for d in Path(__file__).parent.glob('*') if d.is_dir() ]
    return [ name for name in candidates if not name.startswith('_') and not name.startswith('test') ]


@lru_cache()
def one_solution_scenarios(solution):
    importname = 'solution.' + solution
    m = importlib.import_module(importname)
    return (m.Scenario, list(m.scenarios.keys()))


def all_solutions_scenarios():
    everything = {}
    for solution in all_solutions():
        everything[solution] = one_solution_scenarios(solution)
    return everything
