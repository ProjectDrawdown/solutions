
import os
import pandas as pd
from numpy import int64
import pytest
import json

class TestOceanSolution():
    # These two to be defined by subclasses
    scenario_names = []
    solution_name = ''
    scenario_solutions ={}
    scenario_results = {}


    ### Start - Unit Adoption tests ###
    def test_adoption_unit_increase_pds_vs_ref_final_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_adoption_unit_increase_pds_vs_ref_final_year()
            expected_result = self.scenario_results[scen]['Adoption Unit Increase in Final Year (PDS vs REF)']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae
        
    def test_adoption_unit_increase_pds_final_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_adoption_unit_increase_pds_final_year()
            expected_result = self.scenario_results[scen]['Global Units of Adoption in Final Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae
        
    def test_global_percent_adoption_base_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_global_percent_adoption_base_year()
            expected_result = self.scenario_results[scen]['Global Percent Adoption in Base Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae

    def test_percent_adoption_start_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_percent_adoption_start_year()
            expected_result = self.scenario_results[scen]['Global Percent Adoption in Start Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae
        
    def test_get_percent_adoption_end_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_percent_adoption_end_year()
            expected_result = self.scenario_results[scen]['Global Percent Adoption in Final Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae


    ### End - Unit Adoption tests ###


    # ## Start Emissions Reduction tests ##

    def test_emissions_reduction_series(self):
        for scen, soln in self.scenario_solutions.items():
            expected_result_list = self.scenario_results[scen]['Emissions Reduction Series']        
            expected_result = pd.Series(expected_result_list)
            expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
            emissions_reduction_series = soln.get_emissions_reduction_series()

            try:
                pd.testing.assert_series_equal(emissions_reduction_series, expected_result, check_names = False)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae

    # # if test_co2_eq_MMT_reduced() above passes then this section will too.

    def test_total_emissions_reduction(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_total_emissions_reduction()
            expected_result = self.scenario_results[scen]['Total Emissions Reduction']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae
        
    def test_max_annual_emissions_reduction(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_max_annual_emissions_reduction()
            expected_result = self.scenario_results[scen]['Max Annual Emissions Reduction']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae

    def test_emissions_reduction_final_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_emissions_reduction_final_year()
            expected_result = self.scenario_results[scen]['Emissions Reduction in Final Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae

    # ## End Emissions Reduction tests ##


    # ## Start Carbon Sequestration tests ##
        
    def test_carbon_sequestration_series(self):
        for scen, soln in self.scenario_solutions.items():
            expected_result_list = self.scenario_results[scen]['Carbon Sequestration Series']        
            expected_result = pd.Series(expected_result_list)
            expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
            
            carbon_sequestration_series = soln.get_carbon_sequestration_series()
            try:
                pd.testing.assert_series_equal(carbon_sequestration_series, expected_result, check_names = False)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae
            
    # if test_carbon_sequestration_series() above passes then this section will too.

    def test_total_co2_sequestered(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_total_co2_sequestered()
            expected_result = self.scenario_results[scen]['Total Additional CO2-eq Sequestered']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae


    def test_max_annual_co2_sequestered(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_max_annual_co2_sequestered()
            expected_result = self.scenario_results[scen]['Max Annual CO2 Sequestered']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae


    def test_co2_sequestered_final_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_co2_sequestered_final_year()
            expected_result = self.scenario_results[scen]['CO2 Sequestered in Final Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae


    # ## End Carbon Sequestration tests ##

    # ## Start PPM Equivalent tests ##

    def test_change_in_ppm_equivalent_series(self):
        for scen, soln in self.scenario_solutions.items():
            expected_result_list = self.scenario_results[scen]['Change in PPM Equivalent Series']        
            expected_result = pd.Series(expected_result_list)
            expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
            
            change_in_ppm_equivalent_series = soln.get_change_in_ppm_equivalent_series()
            
            try:
                pd.testing.assert_series_equal(change_in_ppm_equivalent_series, expected_result, check_names = False)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae
        
    # # if test_change_in_ppm_equivalent_series() above passes then this section will too.

    def test_change_in_ppm_equivalent(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_change_in_ppm_equivalent()
            expected_result = self.scenario_results[scen]['Approximate PPM Equivalent Change']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae

    def test_change_in_ppm_equivalent_final_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_change_in_ppm_equivalent_final_year()
            expected_result = self.scenario_results[scen]['Approximate PPM rate in Final Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae

    # ## End PPM Equivalent tests ##

    # ## Start Unit Area tests ##

    def test_reduced_area_degradation(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_reduced_area_degradation()
            expected_result = self.scenario_results[scen]['Reduced Area Degradation Across Reporting Period']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae

    def test_co2_under_protection_final_year(self):
        for scen, soln in self.scenario_solutions.items():
            result = soln.get_co2_under_protection_final_year()
            expected_result = self.scenario_results[scen]['Total CO2 Under Protection by End Year']
            try:
                assert result == pytest.approx(expected_result)
            except AssertionError as ae:
                msg = f'Failed on scenario {scen}'
                raise AssertionError(msg) from ae


    # ## End Unit Area tests ##

