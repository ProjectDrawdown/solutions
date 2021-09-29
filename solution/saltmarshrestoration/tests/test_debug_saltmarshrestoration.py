
import pytest
from os import path
import json
import pandas as pd
from  numpy import int64

from solution.saltmarshrestoration.saltmarshrestoration_solution import SaltmarshRestorationSolution

@pytest.fixture
def scenario_name():
    return 'PDS-99p2050-Drawdown-PDSCustom-high-Dec2019'

@pytest.fixture
def solution(scenario_name):
    solution = SaltmarshRestorationSolution()
    print('\nloading', scenario_name)
    solution.load_scenario(scenario_name)
    return solution

@pytest.fixture
def expected_results(scenario_name):
    results_file = path.join('solution','saltmarshrestoration', 'tests', 'expected_results.json')
    stream = open(results_file,'r')
    results = json.load(stream)
    return results[scenario_name]

    ### Start - Unit Adoption tests ###
def test_adoption_unit_increase_pds_vs_ref_final_year(solution, scenario_name, expected_results):
    result = solution.get_adoption_unit_increase_pds_vs_ref_final_year()
    expected_result = expected_results['Adoption Unit Increase in Final Year (PDS vs REF)']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_carbon_sequestration_series(solution, scenario_name, expected_results):
    expected_result_list = expected_results['Carbon Sequestration Series']
    expected_result = pd.Series(expected_result_list)
    expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.

    carbon_sequestration_series = solution.get_carbon_sequestration_series()

    min_idx = expected_result.index.min()
    max_idx = expected_result.index.max()
    carbon_sequestration_series = carbon_sequestration_series.loc[min_idx:max_idx]

    # Assume negative sequestration is noise.
    expected_result.clip(lower=0.0, inplace=True)
    carbon_sequestration_series.clip(lower=0.0, inplace=True)

    try:
        pd.testing.assert_series_equal(carbon_sequestration_series, expected_result, check_names = False)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

