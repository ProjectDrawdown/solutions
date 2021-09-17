from pathlib import Path
import pandas as pd
import numpy as np
from integrations.integration_base import *

def test_audit():
    fn = start_audit("testaudit")
    auditable = pd.DataFrame({'A': [0,1,2,3], 'B': [0,1,2,3]})
    fn("my stuff", auditable)
    auditable['A'][0] = 40
    lookup = log_item("my stuff")
    assert lookup['A'][0] == 0, "changed variable does not affect audited value"
    lookup2 = log_item("my","testaudit")
    assert lookup is lookup2, "lookup via prefix returns same result"
    assert log_item("foo") is None, "lookup non-existent key returns None"

    fn = start_audit("testaudit")
    assert log_item("my stuff") is None, "log starts empty"

def test_demand_adjustment_1d_no_adjustment(capsys):
    supply = pd.DataFrame({'A': [0, 1, 2, 3]})
    demand = pd.DataFrame({'A': [0, 1, 1, 1]})
    result = demand_adjustment("a title", demand, supply)
    assert demand.shape == result.shape
    assert (demand==result).all(axis=None), f"expected {demand} but got {result} instead"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"

def test_demand_adjustment_2d_with_adjustment(capsys):
    supply = pd.DataFrame({'A': [0, 1, 2, 3], 'B': [10, 10, 10, 10]})
    demand = pd.DataFrame({'A': [10, 1, 1, 1], 'B': [1, 1, 1, 1]})
    result = demand_adjustment("a title", demand, supply)
    assert result['A'][0] == 0, "check adjustment was made"
    printed = capsys.readouterr().out
    assert " 1/8 items" in printed, "check printed count is correct"
    assert "max 10" in printed, "output has correct adjustment amount"

    demand2 = pd.DataFrame({'A': [10, 1, 1, 1], 'B': [1, 1, 1, 30]})
    result = demand_adjustment("foo", demand2, supply)
    assert result['B'][3] == 10
    printed = capsys.readouterr().out
    assert " 2/8 items" in printed, "check printed count is correct"
    assert "max 20" in printed, "output has correct adjustment amound"

def test_demand_adjustment_with_nan(capsys):
    #Nan in the supply
    supply = pd.DataFrame({'A': [np.nan, 1, 2, 3], 'B': [10, 10, 10, 10]})
    demand = pd.DataFrame({'A': [10, 1, 1, 1], 'B': [1, 1, 1, 1]})
    assert not (demand>supply).any(axis=None)
    # See!  (demand>supply) is False, so why doesn't it work inside mask()?
    result = demand_adjustment("a title", demand, supply)
    assert result['A'][0] == 10, "check no adjustment was made"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"  

    # Nan in the demand
    supply = pd.DataFrame({'A': [0, 1, 2, 3], 'B': [10, 10, 10, 10]})
    demand = pd.DataFrame({'A': [np.nan, 1, 1, 1], 'B': [1, 1, 1, 1]})
    result = demand_adjustment("a title", demand, supply)
    assert np.isnan(result['A'][0]), "check no adjustment was made"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"  

    # matching nans
    supply = pd.DataFrame({'A': [np.nan, 1, 2, 3], 'B': [10, 10, 10, 10]})
    demand = pd.DataFrame({'A': [np.nan, 1, 1, 1], 'B': [1, 1, 1, 1]})
    result = demand_adjustment("a title", demand, supply)
    assert np.isnan(result['A'][0]), "check no adjustment was made"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"  

def test_demand_adjustment_with_negatives():
    supply = pd.DataFrame({'A': [0, -1, -2, -3], 'B': [10, -10, 10, 10]})
    demand = pd.DataFrame({'A': [10, 1, 1, 1], 'B': [-1, -1, 1, 1]})
    result = demand_adjustment("a title", demand, supply)
    expected = pd.DataFrame({'A': [0, -1, -2, -3], 'B': [-1, -10, 1, 1]})
    assert (result==expected).all(axis=None), "expected {expected}, got {result}"

  
    