"""Test solution classes."""
import dataclasses
from . import factory
from model import scenario
from model import advanced_controls as ac

def test_all_solutions():
    result = factory.all_solutions()
    assert 'solarpvutil' in result
    assert 'silvopasture' in result

def test_list_scenarios():
    result = factory.list_scenarios('silvopasture')
    assert len(result) > 0

def test_load_PDS_scenario():
    result = factory.load_scenario('peatlands','PDS2')
    assert result and isinstance(result, scenario.Scenario)

def test_load_named_scenario():
    scenarios = factory.list_scenarios('geothermal')
    result = factory.load_scenario('geothermal', scenarios[0])
    assert result and isinstance(result, scenario.Scenario)

def test_load_custom_scenario():
    onescenario = factory.load_scenario('hybridcars')
    
    # Make a new Advanced Controls by dumping one and tweaking it
    oneac = dataclasses.asdict(onescenario.ac)
    oneac['name'] = "Change the Name"
    twoac = ac.AdvancedControls(**oneac)

    result = factory.load_scenario('hybridcars',twoac)
    assert result.scenario == "Change the Name"
