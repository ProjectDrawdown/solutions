import pytest
from pathlib import Path
import pandas as pd
import numpy as np
from integrations import integration_base

@pytest.fixture
def with_testmode():
    store = (integration_base.testmode, integration_base.integration_name)
    integration_base.testmode = True
    integration_base.integration_name = "waste"  # just use this one...
    yield
    integration_base.testmode = store[0]
    integration_base.integration_name = store[1]

def test_audit():
    fn = integration_base.start_audit("testaudit")
    auditable = pd.DataFrame({'A': [0,1,2,3], 'B': [0,1,2,3]})
    fn("my stuff", auditable)
    auditable['A'][0] = 40
    lookup = integration_base.get_logitem("my stuff")
    assert lookup['A'][0] == 0, "changed variable does not affect audited value"
    lookup2 = integration_base.get_logitem("my","testaudit")
    assert lookup is lookup2, "lookup via prefix returns same result"
    assert integration_base.get_logitem("foo") is None, "lookup non-existent key returns None"

    fn = integration_base.start_audit("testaudit")
    assert integration_base.get_logitem("my stuff") is None, "log starts empty"


def test_load_adoption_live():
    a = integration_base.load_solution_adoptions("afforestation")
    assert (a.columns == ["PDS1","PDS2","PDS3"]).all()
    assert len(a["PDS1"]) > 40

def test_load_adoption_testmode_miss(with_testmode):
    a = integration_base.load_solution_adoptions("ships")  # waste doesn't have this one
    assert (a.columns == ["PDS1","PDS2","PDS3"]).all()
    assert len(a["PDS1"]) > 40

def test_load_adoption_testmode_hit(with_testmode):
    a = integration_base.load_solution_adoptions("bioplastic")  # waste does have this one
    assert a.loc[2033,"PDS1"] == pytest.approx(18.94589724)


def test_load_solution_file_live():
     data = integration_base.load_solution_file("airplanes","vma_data/Average_Cruise_Speed_Single_Aisle.csv")
     assert "Geographic Location" in data   


def test_demand_adjustment_1d_no_adjustment(capsys):
    supply = pd.DataFrame({'A': [0, 1, 2, 3]})
    demand = pd.DataFrame({'A': [0, 1, 1, 1]})
    result = integration_base.demand_adjustment("a title", demand, supply)
    assert demand.shape == result.shape
    assert (demand==result).all(axis=None), f"expected {demand} but got {result} instead"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"

def test_demand_adjustment_2d_with_adjustment(capsys):
    supply = pd.DataFrame({'A': [0, 1, 2, 3], 'B': [10, 10, 10, 10]})
    demand = pd.DataFrame({'A': [10, 1, 1, 1], 'B': [1, 1, 1, 1]})
    result = integration_base.demand_adjustment("a title", demand, supply)
    assert result['A'][0] == 0, "check adjustment was made"
    printed = capsys.readouterr().out
    assert " 1/8 items" in printed, "check printed count is correct"
    assert "max 10" in printed, "output has correct adjustment amount"

    demand2 = pd.DataFrame({'A': [10, 1, 1, 1], 'B': [1, 1, 1, 30]})
    result = integration_base.demand_adjustment("foo", demand2, supply)
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
    result = integration_base.demand_adjustment("a title", demand, supply)
    assert result['A'][0] == 10, "check no adjustment was made"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"  

    # Nan in the demand
    supply = pd.DataFrame({'A': [0, 1, 2, 3], 'B': [10, 10, 10, 10]})
    demand = pd.DataFrame({'A': [np.nan, 1, 1, 1], 'B': [1, 1, 1, 1]})
    result = integration_base.demand_adjustment("a title", demand, supply)
    assert np.isnan(result['A'][0]), "check no adjustment was made"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"  

    # matching nans
    supply = pd.DataFrame({'A': [np.nan, 1, 2, 3], 'B': [10, 10, 10, 10]})
    demand = pd.DataFrame({'A': [np.nan, 1, 1, 1], 'B': [1, 1, 1, 1]})
    result = integration_base.demand_adjustment("a title", demand, supply)
    assert np.isnan(result['A'][0]), "check no adjustment was made"
    printed = capsys.readouterr().out
    assert len(printed) == 0, "check nothing printed"  

def test_demand_adjustment_with_negatives():
    supply = pd.DataFrame({'A': [0, -1, -2, -3], 'B': [10, -10, 10, 10]})
    demand = pd.DataFrame({'A': [10, 1, 1, 1], 'B': [-1, -1, 1, 1]})
    result = integration_base.demand_adjustment("a title", demand, supply)
    expected = pd.DataFrame({'A': [0, -1, -2, -3], 'B': [-1, -10, 1, 1]})
    assert (result==expected).all(axis=None), "expected {expected}, got {result}"

  
    