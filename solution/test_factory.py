"""Test solution classes."""
import pytest
from . import factory

def test_all_solutions():
    result = factory.all_solutions()
    assert 'solarpvutil' in result
    assert 'silvopasture' in result

def test_all_solutions_scenarios():
    result = factory.all_solutions_scenarios()
    assert 'solarpvutil' in result.keys()
    assert 'silvopasture' in result.keys()

def test_one_solution_scenarios():
    (constructor, scenarios) = factory.one_solution_scenarios('solarpvutil')
    assert constructor is not None
    assert len(scenarios) > 0

def test_solution_pds_type():
    result = factory.solution_pds_type("solarpvutil","PDS1")
    assert result is not None
    with pytest.raises(Exception):
        result = factory.solution_pds_type("solarpvutil","NOT GOOD")

# We don't do a test of all_solutions_scenario_type because it will fail if
# any solution is missing the required scenario type, and we'd rather find that
# out by testing the solutions.
