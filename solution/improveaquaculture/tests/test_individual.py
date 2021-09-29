import pytest
from os import path
import json
import pandas as pd
from  numpy import int64

from solution.improveaquaculture.improveaquaculture_solution import ImproveAquacultureSolution
from solution.seaweedfarming.seaweedfarming_solution import SeaweedFarmingSolution

@pytest.fixture
def scenario_name():
    return 'PDS-30p2050-Plausible'
    #return 'PDS-5p2050-Plausible NEW 240 TOA'

@pytest.fixture
def solution(scenario_name):
    solution = ImproveAquacultureSolution()
    #solution = SeaweedFarmingSolution()
    solution.load_scenario(scenario_name)
    return solution

@pytest.fixture
def expected_results(scenario_name):
    results_file = path.join('solution','improveaquaculture', 'tests', 'expected_results.json')
    #results_file = path.join('solution','seaweedfarming', 'tests', 'expected_results.json')
    stream = open(results_file,'r')
    results = json.load(stream)
    return results[scenario_name]


### Start Financial Calculation tests ###

def test_get_marginal_first_cost_across_reporting_period(solution, scenario_name, expected_results):
    result = solution.get_marginal_first_cost()
    expected_result = expected_results['Marginal First Cost Across Reporting Period']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}' 
        raise AssertionError(msg) from ae
        
def test_get_cumulative_first_cost_solution(solution, scenario_name, expected_results):
    result = solution.get_cumulative_first_cost_solution()
    expected_result = expected_results['Cumulative First Cost Across Reporting Period']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_net_operating_savings_across_reporting_period(solution, scenario_name, expected_results):
    result = solution.get_operating_cost()
    expected_result = expected_results['Net Operating Savings Across Reporting Period']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_lifetime_operating_savings_across_reporting_period(solution, scenario_name, expected_results):
    result = solution.get_lifetime_operating_savings()
    expected_result = expected_results['Lifetime Operating Savings Across Reporting Period']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_lifetime_cashflow_npv_single(solution, scenario_name, expected_results):
    result = solution.get_lifetime_cashflow_npv_single(purchase_year = 2017)
    expected_result = expected_results['Lifetime Cashflow NPV of Single Implementation Unit (PDS vs REF)']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

## seaweedfarming:


# def test_get_lifetime_cashflow_npv_all( solution, scenario_name, expected_results):
#     result = solution.get_lifetime_cashflow_npv_all()
#     expected_result = expected_results['Lifetime Cashflow NPV of All Implementation Units (PDS vs REF)']
#     try:
#         assert result == pytest.approx(expected_result)
#     except AssertionError as ae:
#         msg = f'Failed on scenario {scenario_name}'
#         raise AssertionError(msg) from ae
    
    

def test_get_abatement_cost(solution, scenario_name, expected_results):
    result = solution.get_abatement_cost()
    expected_result = expected_results['Average Abatement Cost Across Reporting Period']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_payback_period_solution_vs_conventional(solution, scenario_name, expected_results):
    result = solution.get_payback_period_solution_vs_conventional()
    result = max(result, -1)
    expected_result = expected_results['Payback Period Solution Relative to Conventional']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_payback_period_solution_vs_conventional_npv(solution, scenario_name, expected_results):
    result = solution.get_payback_period_solution_vs_conventional_npv()
    result = max(result, -1)
    expected_result = expected_results['Discounted Payback Period Solution Relative to Conventional']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae
    

def test_get_payback_period_solution_only(solution, scenario_name, expected_results):
    result = solution.get_payback_period_solution_only()
    result = max(result, -1) # -1 means "Never"
    expected_result = expected_results['Payback Period Solution Alone']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_payback_period_solution_only_npv(solution, scenario_name, expected_results):
    result = solution.get_payback_period_solution_only_npv()
    result = max(result, -1)
    expected_result = expected_results['Discounted Payback Period Solution Alone']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae


## End Financial Calculations

## Start Emissions Reduction tests ##
# Should match "CO2-eq MMT Reduced" on "CO2 Calcs" worksheet.
def test_get_emissions_reduction_series(solution, scenario_name, expected_results):
    expected_result_list = expected_results['Emissions Reduction Series']
    expected_result = pd.Series(expected_result_list)
    expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
    emissions_reduction_series = solution.get_emissions_reduction_series()

    try:
        pd.testing.assert_series_equal(emissions_reduction_series, expected_result, check_names = False)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

# def test_carbon_sequestration_series(solution, scenario_name, expected_results):
#     expected_result_list = expected_results['Carbon Sequestration Series']
#     expected_result = pd.Series(expected_result_list)
#     expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.

#     carbon_sequestration_series = solution.get_carbon_sequestration_series()

#     # Assume negative sequestration is noise.
#     expected_result.clip(lower=0.0, inplace=True)
#     carbon_sequestration_series.clip(lower=0.0, inplace=True)

#     min_idx = expected_result.index.min()
#     max_idx = expected_result.index.max()
#     carbon_sequestration_series = carbon_sequestration_series.loc[min_idx:max_idx]

#     try:
#         pd.testing.assert_series_equal(carbon_sequestration_series, expected_result, check_names = False)
#     except AssertionError as ae:
#         msg = f'Failed on scenario {scenario_name}'
#         raise AssertionError(msg) from ae

def test_change_in_ppm_equivalent_series(solution, scenario_name, expected_results):
    expected_result_list = expected_results['Change in PPM Equivalent Series']        
    expected_result = pd.Series(expected_result_list)
    expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
    
    change_in_ppm_equivalent_series = solution.get_change_in_ppm_equivalent_series()
    min_idx = expected_result.index.min()
    max_idx = expected_result.index.max()
    change_in_ppm_equivalent_series = change_in_ppm_equivalent_series.loc[min_idx:max_idx]
    
    try:
        pd.testing.assert_series_equal(change_in_ppm_equivalent_series, expected_result, check_names = False)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae