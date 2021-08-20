# This file can be copied to your solution tests directory,
# or solution_xls_extract.output_solution_testsfile will do it for you

import pytest
from pathlib import Path
from tools import expected_result_tester
from solution import factory

thisdir = Path(__file__).parents[0]
expected_file = thisdir / 'expected.zip'

solution_name = 'waterefficiency'

# If there are long-running test failures that should be skipped, you can indicate them here.
# Someday we'll have a scanner that will check for these
SCENARIO_SKIP = None
TEST_SKIP = None

def test_waterefficiency_loader():
    """Test that the solution can load the defined scenarios"""
    pds1 = factory.solution_pds_type(solution_name,"PDS1")
    pds2 = factory.solution_pds_type(solution_name,"PDS2")
    pds3 = factory.solution_pds_type(solution_name, "PDS3")
    assert pds1 and pds2 and pds3

@pytest.mark.slow
def test_waterefficiency_results(scenario_skip=None, test_skip=None, test_only=None):
    """Test computed results against stored Excel results"""
    scenario_skip = scenario_skip or SCENARIO_SKIP
    test_skip = test_skip or TEST_SKIP
    expected_result_tester.one_solution_tester(
        solution_name,
        expected_file, is_land=False,
        scenario_skip=scenario_skip, test_skip=test_skip, test_only=test_only)

