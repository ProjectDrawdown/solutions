"""Test solution classes."""

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


