"""Test solution classes."""

import os
import pandas as pd
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

def test_all_solutions_present():
    all_solutions = pd.read_csv(os.path.join('data', 'overview', 'solutions.csv'),
            index_col=False, skipinitialspace=True, header=0,
            skip_blank_lines=True, comment='#')
    factory_solutions = factory.all_solutions_scenarios()
    for (_, val) in all_solutions['DirName'].dropna().iteritems():
        assert val in factory_solutions.keys()
