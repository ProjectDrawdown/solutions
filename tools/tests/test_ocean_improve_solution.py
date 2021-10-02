import pandas as pd
from numpy import int64
import pytest

class TestOceanImproveSolutionAdoption():

    def test_load(self, solution, scenario_name, expected_results):
        print('\nloading', scenario_name)
        solution.load_scenario(scenario_name)

    ### Start - Unit Adoption tests ###

# Following test errors in spreadsheet for improve fishery biomass. Commenting out until resolved in spreadsheet.

    # def test_get_implementation_unit_adoption_increase_final_year(self, solution, scenario_name, expected_results):
    #     result = solution.get_adoption_unit_increase_pds_vs_ref_final_year()
    #     expected_result = expected_results['Implementation Unit Adoption Increase in Final Year (PDS vs REF)']
    #     try:
    #         assert result == pytest.approx(expected_result)
    #     except AssertionError as ae:
    #         msg = f'Failed on scenario {scenario_name}'
    #         raise AssertionError(msg) from ae

    def test_get_functional_unit_adoption_increase_final_year(self, solution, scenario_name, expected_results):
        result = solution.get_adoption_unit_increase_pds_vs_ref_final_year()
        expected_result = expected_results['Functional Unit Adoption Increase in Final Year (PDS vs REF)']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

# Following test errors in spreadsheet for improve fishery biomass. Commenting out until resolved in spreadsheet.

    # def test_get_global_solution_implementation_units_final_year(self, solution, scenario_name, expected_results):
    #     result = solution.get_adoption_unit_increase_pds_final_year()
    #     expected_result = expected_results['Global Solution Implementation Units in Final Year']
    #     try:
    #         assert result == pytest.approx(expected_result)
    #     except AssertionError as ae:
    #         msg = f'Failed on scenario {scenario_name}'
    #         raise AssertionError(msg) from ae

    def test_get_global_solution_functional_units_final_year(self, solution, scenario_name, expected_results):
        result = solution.get_adoption_unit_increase_pds_final_year()
        expected_result = expected_results['Global Solution Functional Units in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_global_solution_adoption_share_base_year(self, solution, scenario_name, expected_results):
        result = solution.get_global_percent_adoption_base_year()
        expected_result = expected_results['Global Solution Adoption Share in Base Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_global_solution_adoption_share_start_year(self, solution, scenario_name, expected_results):
        result = solution.get_percent_adoption_start_year()
        expected_result = expected_results['Global Solution Adoption Share in Start Year']
        try:
            assert result == pytest.approx(expected_result, rel=1e-4)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_get_global_solution_adoption_share_final_year(self, solution, scenario_name, expected_results):
        result = solution.get_percent_adoption_end_year()
        expected_result = expected_results['Global Solution Adoption Share in Final Year']
        try:
            assert result == pytest.approx(expected_result, rel=1e-5)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ### End - Unit Adoption tests ###

class TestOceanImproveSolutionFinancials():

    def test_load(self, solution, scenario_name, expected_results):
        print('\nloading', scenario_name)
        solution.load_scenario(scenario_name)

    ### Start Financial Calculation tests ###

    def test_get_marginal_first_cost_across_reporting_period(self, solution, scenario_name, expected_results):
        result = solution.get_marginal_first_cost()
        expected_result = expected_results['Marginal First Cost Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_cumulative_first_cost_solution(self, solution, scenario_name, expected_results):
        result = solution.get_cumulative_first_cost_solution()
        expected_result = expected_results['Cumulative First Cost Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_net_operating_savings_across_reporting_period(self, solution, scenario_name, expected_results):
        result = solution.get_operating_cost()
        expected_result = expected_results['Net Operating Savings Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_lifetime_operating_savings_across_reporting_period(self, solution, scenario_name, expected_results):
        result = solution.get_lifetime_operating_savings()
        expected_result = expected_results['Lifetime Operating Savings Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_lifetime_cashflow_npv_single(self, solution, scenario_name, expected_results):
        result = solution.get_lifetime_cashflow_npv_single(purchase_year = 2017)
        expected_result = expected_results['Lifetime Cashflow NPV of Single Implementation Unit (PDS vs REF)']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_abatement_cost(self, solution, scenario_name, expected_results):
        result = solution.get_abatement_cost()
        expected_result = expected_results['Average Abatement Cost Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_payback_period_solution_vs_conventional(self, solution, scenario_name, expected_results):
        result = solution.get_payback_period_solution_vs_conventional(purchase_year = 2017)
        result = max(result, -1)
        expected_result = expected_results['Payback Period Solution Relative to Conventional']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_payback_period_solution_vs_conventional_npv(self, solution, scenario_name, expected_results):
        result = solution.get_payback_period_solution_vs_conventional_npv(purchase_year = 2017)
        result = max(result, -1)
        expected_result = expected_results['Discounted Payback Period Solution Relative to Conventional']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    
    def test_get_payback_period_solution_only(self, solution, scenario_name, expected_results):
        result = solution.get_payback_period_solution_only(purchase_year = 2017)
        result = max(result, -1)
        expected_result = expected_results['Payback Period Solution Alone']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_payback_period_solution_only_npv(self, solution, scenario_name, expected_results):
        result = solution.get_payback_period_solution_only_npv(purchase_year = 2017)
        result = max(result, -1)
        expected_result = expected_results['Discounted Payback Period Solution Alone']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ## End Financial Calculations

class TestOceanImproveSolutionClimate():
    
    def test_load(self, solution, scenario_name, expected_results):
        print('\nloading', scenario_name)
        solution.load_scenario(scenario_name)
        
    ## Start Emissions Reduction tests ##
    # Should match "CO2-eq MMT Reduced" on "CO2 Calcs" worksheet.
    def test_get_emissions_reduction_series(self, solution, scenario_name, expected_results):
        expected_result_list = expected_results['Emissions Reduction Series']
        expected_result = pd.Series(expected_result_list)
        expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
        emissions_reduction_series = solution.get_emissions_reduction_series()

        try:
            pd.testing.assert_series_equal(emissions_reduction_series, expected_result, check_names = False)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    # if test_emissions_reduction_series() above passes then this section will too.

    def test_get_total_emissions_reduction(self, solution, scenario_name, expected_results):
        result = solution.get_total_emissions_reduction()
        expected_result = expected_results['Total Emissions Reduction']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_get_max_annual_emissions_reduction(self, solution, scenario_name, expected_results):
        result = solution.get_max_annual_emissions_reduction()
        expected_result = expected_results['Max Annual Emissions Reduction']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_emissions_reduction_final_year(self, solution, scenario_name, expected_results):
        result = solution.get_emissions_reduction_final_year()
        expected_result = expected_results['Emissions Reduction in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ## End Emissions Reduction tests ##


    ## Start Carbon Sequestration tests ##

    # # Should match "Carbon Sequestration Calculations" on "CO2 Calcs" worksheet.
    # def test_get_carbon_sequestration_series(self, solution, scenario_name, expected_results):
    #     expected_result_list = expected_results['Carbon Sequestration Series']
    #     expected_result = pd.Series(expected_result_list)
    #     expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.

    #     carbon_sequestration_series = solution.get_carbon_sequestration_series()

    #     # Assume negative sequestration is noise.
    #     expected_result.clip(lower=0.0, inplace=True)
    #     carbon_sequestration_series.clip(lower=0.0, inplace=True)

    #     try:
    #         pd.testing.assert_series_equal(carbon_sequestration_series, expected_result, check_names = False)
    #     except AssertionError as ae:
    #         msg = f'Failed on scenario {scenario_name}'
    #         raise AssertionError(msg) from ae

    # ## End Carbon Sequestration tests ##

    ## Start PPM Equivalent tests ##

    # Should match "CO2 PPM Calculator" on "CO2 Calcs" worksheet.
    def test_change_in_ppm_equivalent_series(self, solution, scenario_name, expected_results):
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
        
    # if test_change_in_ppm_equivalent_series() above passes then this section will too.

    def test_change_in_ppm_equivalent(self, solution, scenario_name, expected_results):
        result = solution.get_change_in_ppm_equivalent()
        expected_result = expected_results['Approximate PPM Equivalent Change']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_change_in_ppm_equivalent_final_year(self, solution, scenario_name, expected_results):
        result = solution.get_change_in_ppm_equivalent_final_year()
        expected_result = expected_results['Approximate PPM rate in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ## End PPM Equivalent tests ##
