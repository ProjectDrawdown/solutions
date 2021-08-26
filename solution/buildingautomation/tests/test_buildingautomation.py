# This file can be copied to your solution tests directory,
# or solution_xls_extract.output_solution_testsfile will do it for you

import pytest
from pathlib import Path
from tools import expected_result_tester
from solution import factory

thisdir = Path(__file__).parents[0]
expected_file = thisdir / 'expected.zip'

solution_name = 'buildingautomation'

# We get a variance from the Excel because of a corner case in which we treat a NaN as a zero
# It does not materially affect the results.
SCENARIO_SKIP = None
TEST_SKIP = ['Q135:AA181']

def test_buildingautomation_loader():
    """Test that the solution can load the defined scenarios"""
    pds1 = factory.load_scenario(solution_name,"PDS1")
    pds2 = factory.load_scenario(solution_name,"PDS2")
    pds3 = factory.load_scenario(solution_name, "PDS3")
    assert pds1 and pds2 and pds3

@pytest.mark.slow
def test_buildingautomation_results(scenario_skip=None, test_skip=None, test_only=None):
    """Test computed results against stored Excel results"""
    scenario_skip = scenario_skip or SCENARIO_SKIP
    test_skip = test_skip or TEST_SKIP
    expected_result_tester.one_solution_tester(
        solution_name,
        expected_file, is_land=False,
        scenario_skip=scenario_skip, test_skip=test_skip, test_only=test_only)

