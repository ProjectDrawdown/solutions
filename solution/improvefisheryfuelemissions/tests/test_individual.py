import pytest
from os import path
import json
import pandas as pd
from  numpy import int64

from solution.improvefisheryfuelemissions.improvefisheryfuelemissions_solution import ImproveFisheryFuelEmissionsSolution

@pytest.fixture
def scenario_name():
    return 'PDS-63p2050-Plausible'

@pytest.fixture
def solution(scenario_name):
    solution = ImproveFisheryFuelEmissionsSolution()
    solution.load_scenario(scenario_name)
    return solution

@pytest.fixture
def expected_results(scenario_name):
    results_file = path.join('solution','improvefisheryfuelemissions', 'tests', 'expected_results.json')
    stream = open(results_file,'r')
    results = json.load(stream)
    return results[scenario_name]


### Start - Unit Adoption tests ###

# Following test errors in spreadsheet for improve fishery biomass. Commenting out until resolved in spreadsheet.

# def test_get_implementation_unit_adoption_increase_final_year(solution, scenario_name, expected_results):
#     result = solution.get_adoption_unit_increase_pds_vs_ref_final_year()
#     expected_result = expected_results['Implementation Unit Adoption Increase in Final Year (PDS vs REF)']
#     try:
#         assert result == pytest.approx(expected_result)
#     except AssertionError as ae:
#         msg = f'Failed on scenario {scenario_name}'
#         raise AssertionError(msg) from ae

def test_get_functional_unit_adoption_increase_final_year(solution, scenario_name, expected_results):
    result = solution.get_adoption_unit_increase_pds_vs_ref_final_year()
    expected_result = expected_results['Functional Unit Adoption Increase in Final Year (PDS vs REF)']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

# Following test errors in spreadsheet for improve fishery biomass. Commenting out until resolved in spreadsheet.

# def test_get_global_solution_implementation_units_final_year(solution, scenario_name, expected_results):
#     result = solution.get_adoption_unit_increase_pds_final_year()
#     expected_result = expected_results['Global Solution Implementation Units in Final Year']
#     try:
#         assert result == pytest.approx(expected_result)
#     except AssertionError as ae:
#         msg = f'Failed on scenario {scenario_name}'
#         raise AssertionError(msg) from ae

def test_get_global_solution_functional_units_final_year(solution, scenario_name, expected_results):
    result = solution.get_adoption_unit_increase_pds_final_year()
    expected_result = expected_results['Global Solution Functional Units in Final Year']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_global_solution_adoption_share_base_year(solution, scenario_name, expected_results):
    result = solution.get_global_percent_adoption_base_year()
    expected_result = expected_results['Global Solution Adoption Share in Base Year']
    try:
        assert result == pytest.approx(expected_result)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

def test_get_global_solution_adoption_share_start_year(solution, scenario_name, expected_results):
    result = solution.get_percent_adoption_start_year()
    expected_result = expected_results['Global Solution Adoption Share in Start Year']
    try:
        assert result == pytest.approx(expected_result, rel=1e-4)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae
    
def test_get_global_solution_adoption_share_final_year(solution, scenario_name, expected_results):
    result = solution.get_percent_adoption_end_year()
    expected_result = expected_results['Global Solution Adoption Share in Final Year']
    try:
        assert result == pytest.approx(expected_result, rel=1e-5)
    except AssertionError as ae:
        msg = f'Failed on scenario {scenario_name}'
        raise AssertionError(msg) from ae

    ### End - Unit Adoption tests ###
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