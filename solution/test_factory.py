"""Test solution classes."""

import pytest
import factory

def test_all_solutions_scenarios():
    result = factory.all_solutions_scenarios()
    assert 'solarpvutil' in result.keys()
    assert 'silvopasture' in result.keys()
