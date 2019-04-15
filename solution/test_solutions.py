"""Test solution classes."""

import pytest
import solution.factory

solutions = solution.factory.all_solutions_scenarios()

@pytest.mark.parametrize("name,constructor,scenarios",
    [(name,) + solutions[name] for name in solutions.keys()],
    ids=list(solutions.keys())
)
def test_solutions(name, constructor, scenarios):
    scenario = scenarios[0]
    obj = constructor(scenario=scenario)
    assert obj.scenario == scenario
    assert obj.name

def test_sane_number_of_solutions():
    assert len(list(solutions.keys())) >= 35
