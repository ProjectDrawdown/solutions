import pytest
from pathlib import Path
from tools import expected_result_tester
from solution import factory

thisdir = Path(__file__).parents[0]
expected_file = thisdir / 'expected.zip'

# If there are long-running test failures that should be skipped, you can indicate them here.
# Health checker will check these.
SCENARIO_SKIP = None
TEST_SKIP = None

def test_afforestation_loader():
    """Test that the solution can load a single scenario"""
    (constructor,scenarios) = factory.one_solution_scenarios('afforestation')
    assert len(scenarios) > 0
    ascenario = constructor(scenarios[0])
    assert ascenario is not None

@pytest.mark.slow
def test_Afforestation_LAND(scenario_skip=None, test_skip=None, test_only=None):
    """Test computed results against stored Excel results"""
    scenario_skip = scenario_skip or SCENARIO_SKIP
    test_skip = test_skip or TEST_SKIP
    expected_result_tester.one_solution_tester(
        'afforestation', 
        expected_file, is_land=True,
        scenario_skip=scenario_skip, test_skip=test_skip, test_only=test_only)