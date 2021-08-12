# This file can be copied to your solution tests directory,
# or solution_xls_extract.output_solution_testsfile will do it for you

import pytest
from pathlib import Path
from tools import expected_result_tester
from solution import factory

thisdir = Path(__file__).parents[0]
expected_file = thisdir / 'expected.zip'

solution_name = 'household_commercial_recycling'

# If there are long-running test failures that should be skipped, you can indicate them here.
# Someday we'll have a scanner that will check for these
SCENARIO_SKIP = None
# We are skipping these tests because we are providing overridden TAM
# trends for the 3rd poly case only, so skip Linear, Degree 2 and 
# Exponential forecasts.
TEST_SKIP = ['BT677:BV723','CA677:CD723','CR677:CT723']

def test_hcr_loader():
    """Test that the solution can load a single scenario"""
    (constructor,scenarios) = factory.one_solution_scenarios(solution_name)
    assert len(scenarios) > 0
    ascenario = constructor(scenarios[0])
    assert ascenario is not None

@pytest.mark.slow
def test_hcr_results(scenario_skip=None, test_skip=None, test_only=None):
    """Test computed results against stored Excel results"""
    scenario_skip = scenario_skip or SCENARIO_SKIP
    test_skip = test_skip or TEST_SKIP
    expected_result_tester.one_solution_tester(
        solution_name,
        expected_file, is_land=False,
        scenario_skip=scenario_skip, test_skip=test_skip, test_only=test_only)

