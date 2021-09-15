import pandas as pd
from numpy import int64
import pytest

class TestOceanSolutionFinancials():

    def test_load(self, solution, scenario_name, scenario_results):
        print('\nloading', scenario_name)
        solution.load_scenario(scenario_name)
        
    ### Start Financial Calculation tests ###

    def test_get_marginal_first_cost(self, solution, scenario_name, scenario_results):
        result = solution.get_marginal_first_cost()
        expected_result = scenario_results['Marginal First Cost Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_operating_cost(self, solution, scenario_name, scenario_results):
        result = solution.get_operating_cost()
        expected_result = scenario_results['Net Operating Savings Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_lifetime_operating_savings(self, solution, scenario_name, scenario_results):
        result = solution.get_lifetime_operating_savings()
        expected_result = scenario_results['Lifetime Operating Savings Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_get_cumulative_first_cost_pds(self, solution, scenario_name, scenario_results):
        result = solution.get_cumulative_first_cost_pds()
        expected_result = scenario_results['Cumulative First Cost Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_lifetime_cashflow_npv_single(self, solution, scenario_name, scenario_results):
        result = solution.get_lifetime_cashflow_npv_single(purchase_year = 2017)
        expected_result = scenario_results['Lifetime Cashflow NPV of Single Implementation Unit (PDS vs REF)']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

        
    def test_get_lifetime_cashflow_npv_all(self, solution, scenario_name, scenario_results):
        result = solution.get_lifetime_cashflow_npv_all()
        expected_result = scenario_results['Lifetime Cashflow NPV of All Implementation Units (PDS vs REF)']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_get_payback_period_soln_to_conv(self, solution, scenario_name, scenario_results):
        result = solution.get_payback_period_soln_to_conv(purchase_year = 2017)
        result = max(result, -1)
        expected_result = scenario_results['Payback Period Solution Relative to Conventional']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_get_payback_period_soln_to_conv_npv(self, solution, scenario_name, scenario_results):
        result = solution.get_payback_period_soln_to_conv_npv(purchase_year = 2017)
        result = max(result, -1)
        expected_result = scenario_results['Discounted Payback Period Solution Relative to Conventional']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_get_payback_period_soln_only(self, solution, scenario_name, scenario_results):
        result = solution.get_payback_period_soln_only(purchase_year = 2017)
        result = max(result, -1)
        expected_result = scenario_results['Payback Period Solution Alone']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_payback_period_soln_only_npv(self, solution, scenario_name, scenario_results):
        result = solution.get_payback_period_soln_only_npv(purchase_year = 2017)
        result = max(result, -1)
        expected_result = scenario_results['Discounted Payback Period Solution Alone']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_abatement_cost(self, solution, scenario_name, scenario_results):
        result = solution.get_abatement_cost()
        expected_result = scenario_results['Average Abatement Cost Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_net_profit_margin(self, solution, scenario_name, scenario_results):
        result = solution.get_net_profit_margin()
        expected_result = scenario_results['Net Profit Margin Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_get_lifetime_profit_margin(self, solution, scenario_name, scenario_results):
        result = solution.get_lifetime_profit_margin()
        expected_result = scenario_results['Lifetime Profit Margin']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        

    ### End Financial Calculation tests ###




class TestOceanSolution():

    def test_load(self, solution, scenario_name, scenario_results):
        print('\nloading', scenario_name)
        solution.load_scenario(scenario_name)

    ### Start - Unit Adoption tests ###
    def test_adoption_unit_increase_pds_vs_ref_final_year(self, solution, scenario_name, scenario_results):
        result = solution.get_adoption_unit_increase_pds_vs_ref_final_year()
        expected_result = scenario_results['Adoption Unit Increase in Final Year (PDS vs REF)']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
    
    def test_adoption_unit_increase_pds_final_year(self, solution, scenario_name, scenario_results):
        result = solution.get_adoption_unit_increase_pds_final_year()
        expected_result = scenario_results['Global Units of Adoption in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_global_percent_adoption_base_year(self, solution, scenario_name, scenario_results):
        result = solution.get_global_percent_adoption_base_year()
        expected_result = scenario_results['Global Percent Adoption in Base Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_percent_adoption_start_year(self, solution, scenario_name, scenario_results):
        result = solution.get_percent_adoption_start_year()
        expected_result = scenario_results['Global Percent Adoption in Start Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_get_percent_adoption_end_year(self, solution, scenario_name, scenario_results):
        result = solution.get_percent_adoption_end_year()
        expected_result = scenario_results['Global Percent Adoption in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ### End - Unit Adoption tests ###


    ## Start Emissions Reduction tests ##
    # Should match "CO2-eq MMT Reduced" on "CO2 Calcs" worksheet.
    def test_emissions_reduction_series(self, solution, scenario_name, scenario_results):
        expected_result_list = scenario_results['Emissions Reduction Series']        
        expected_result = pd.Series(expected_result_list)
        expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
        emissions_reduction_series = solution.get_emissions_reduction_series()

        try:
            pd.testing.assert_series_equal(emissions_reduction_series, expected_result, check_names = False)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    # if test_emissions_reduction_series() above passes then this section will too.

    def test_total_emissions_reduction(self, solution, scenario_name, scenario_results):
        result = solution.get_total_emissions_reduction()
        expected_result = scenario_results['Total Emissions Reduction']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    def test_max_annual_emissions_reduction(self, solution, scenario_name, scenario_results):
        result = solution.get_max_annual_emissions_reduction()
        expected_result = scenario_results['Max Annual Emissions Reduction']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_emissions_reduction_final_year(self, solution, scenario_name, scenario_results):
        result = solution.get_emissions_reduction_final_year()
        expected_result = scenario_results['Emissions Reduction in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ## End Emissions Reduction tests ##


    ## Start Carbon Sequestration tests ##

    # Should match "Carbon Sequestration Calculations" on "CO2 Calcs" worksheet.
    def test_carbon_sequestration_series(self, solution, scenario_name, scenario_results):
        expected_result_list = scenario_results['Carbon Sequestration Series']
        expected_result = pd.Series(expected_result_list)
        expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
        
        carbon_sequestration_series = solution.get_carbon_sequestration_series()
        try:
            pd.testing.assert_series_equal(carbon_sequestration_series, expected_result, check_names = False)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
            
    # if test_carbon_sequestration_series() above passes then this section will too.

    def test_total_co2_sequestered(self, solution, scenario_name, scenario_results):
        result = solution.get_total_co2_sequestered()
        expected_result = scenario_results['Total Additional CO2-eq Sequestered']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_max_annual_co2_sequestered(self, solution, scenario_name, scenario_results):
        result = solution.get_max_annual_co2_sequestered()
        expected_result = scenario_results['Max Annual CO2 Sequestered']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_co2_sequestered_final_year(self, solution, scenario_name, scenario_results):
        result = solution.get_co2_sequestered_final_year()
        expected_result = scenario_results['CO2 Sequestered in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae


    ## End Carbon Sequestration tests ##

    ## Start PPM Equivalent tests ##

    # Should match "CO2 PPM Calculator" on "CO2 Calcs" worksheet.
    def test_change_in_ppm_equivalent_series(self, solution, scenario_name, scenario_results):
        expected_result_list = scenario_results['Change in PPM Equivalent Series']        
        expected_result = pd.Series(expected_result_list)
        expected_result.index = expected_result.index.map(int64) # index is read with string datatype so convert to int64.
        
        change_in_ppm_equivalent_series = solution.get_change_in_ppm_equivalent_series()
        
        try:
            pd.testing.assert_series_equal(change_in_ppm_equivalent_series, expected_result, check_names = False)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae
        
    # if test_change_in_ppm_equivalent_series() above passes then this section will too.

    def test_change_in_ppm_equivalent(self, solution, scenario_name, scenario_results):
        result = solution.get_change_in_ppm_equivalent()
        expected_result = scenario_results['Approximate PPM Equivalent Change']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_change_in_ppm_equivalent_final_year(self, solution, scenario_name, scenario_results):
        result = solution.get_change_in_ppm_equivalent_final_year()
        expected_result = scenario_results['Approximate PPM rate in Final Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ## End PPM Equivalent tests ##

    ## Start Unit Area tests ##

    def test_reduced_area_degradation(self, solution, scenario_name, scenario_results):
        result = solution.get_reduced_area_degradation()
        result = max(result, 0.0) # If not relevant for the solution, this will return a negative number.
        expected_result = scenario_results['Reduced Area Degradation Across Reporting Period']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    def test_co2_under_protection_final_year(self, solution, scenario_name, scenario_results):
        result = solution.get_co2_under_protection_final_year()
        result = max(result, 0.0)
        expected_result = scenario_results['Total CO2 Under Protection by End Year']
        try:
            assert result == pytest.approx(expected_result)
        except AssertionError as ae:
            msg = f'Failed on scenario {scenario_name}'
            raise AssertionError(msg) from ae

    ## End Unit Area tests ##
