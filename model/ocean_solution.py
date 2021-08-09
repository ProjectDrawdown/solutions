import sys
import yaml

import numpy as np
import pandas as pd
from model.ocean_scenario import OceanScenario as Scenario
from model.ocean_unit_adoption import UnitAdoption

import json

class OceanSolution:

    ### Config data:

    start_year = None
    end_year = None
    base_year = None
    total_area = None # millions of hectares
    pds_adoption_file = ''
    ref_adoption_file = ''
    scenarios_file = ''
    required_version_minimum = ()
    
    ### End Config Data

    def _load_config_file(self, file_name):
        
        stream = open(file_name, 'r')
        config = yaml.load(stream, Loader=yaml.FullLoader)
        self.start_year = config['StartYear']
        self.end_year = config['EndYear']
        self.base_year = config['BaseYear']
        self.total_area = config['TotalArea']

        self.pds_adoption_file = config['PDSAdoptionFile']
        self.ref_adoption_file = config['REFAdoptionFile']
        self.scenarios_file = config['ScenariosFile']
        self.required_version_minimum = tuple(int(st) for st in str.split(config['RequiredVersionMinimum'], '.'))

    def _load_adoption_scenario(self, adoption_input_file, adoption_scenario_name):
            
        try:
            ad_scenario = UnitAdoption(self.base_year, adoption_scenario_name, adoption_input_file)
        except ValueError as ev:
            print(ev.args)
            raise ValueError(f"Unable to initialise {adoption_scenario_name}")
        
        return ad_scenario

    def _load_pds_scenario(self):
        
        self.pds_scenario = self._load_adoption_scenario(self.pds_adoption_file,
                        self.scenario.pds_scenario_name)

        self.pds_scenario.first_cost = self.scenario.soln_first_cost
        self.pds_scenario.expected_lifetime = self.scenario.soln_expected_lifetime
        self.pds_scenario.net_profit_margin = self.scenario.soln_net_profit_margin
        self.pds_scenario.operating_cost = self.scenario.soln_operating_cost

        
    def _load_ref_scenario(self):
        
        self.ref_scenario = self._load_adoption_scenario(self.ref_adoption_file,
                        self.scenario.ref_scenario_name)
        
        self.ref_scenario.first_cost = self.scenario.soln_first_cost
        self.ref_scenario.expected_lifetime = self.scenario.soln_expected_lifetime
        self.ref_scenario.net_profit_margin = self.scenario.soln_net_profit_margin
        self.ref_scenario.operating_cost = self.scenario.soln_operating_cost


    # Initialize from configuration file:
    def __init__(self, configuration_file_name):
        self._load_config_file(configuration_file_name)
        if sys.version_info < self.required_version_minimum:
            print(f'Warning - you are running python version {sys.version}. Version {self.required_version_minimum} or greater is required.')

    
    def get_scenario_names(self):

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)
        
        return list(scen_dict.keys())

    def load_scenario(self, scenario_name):

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        scenario = Scenario(**scen_dict[scenario_name])

        self.scenario = scenario

        self._load_pds_scenario()
        self._load_ref_scenario()

        # Set scenario-specific data:
        self.disturbance_rate = self.scenario.disturbance_rate
        self.sequestration_rate_all_ocean = self.scenario.sequestration_rate_all_ocean
        self.npv_discount_rate = self.scenario.npv_discount_rate

        # self.pds_scenario.operating_cost *= 1.1
        # self.ref_scenario.operating_cost *= 1.1

    
    def print_scenario_info(self):
        print('Loaded scenario name:', self.scenario.description)
        
    # Unit Adoption functions:

    def get_adoption_unit_increase_final_year(self, region) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted(region)
        ref_series = self.ref_scenario.get_units_adopted(region)

        net_series = pds_series.subtract(ref_series)

        return net_series.loc[self.end_year]


    def get_adoption_unit_pds_final_year(self, region) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted(region)
        return pds_series.loc[self.end_year]


    def get_global_percent_adoption_base_year(self, region) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted(region)
        result = pds_series.loc[self.base_year+1] / self.total_area
        return result
        
        
    def get_percent_adoption_start_year(self, region) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted(region)
        result = pds_series.loc[self.start_year] / self.total_area
        return result
    
    def get_percent_adoption_end_year(self, region) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted(region)
        result = pds_series.loc[self.end_year] / self.total_area
        return result
        
    # End of Unit Adoption functions

    ### Financial functions:

    def get_marginal_first_cost(self, region) -> np.float64:
        
        # pds_awfc corresponds to the "Annual World First Cost" column (solution-pds)
        # in [First Cost]!$E$36 in the spreadsheet.

        pds_awfc = self.pds_scenario.get_annual_world_first_cost(region)
        
        # ref_awfc corresponds to the "Annual World First Cost" column (solution-ref)
        # in [First Cost]!$N$36 in the spreadsheet.

        ref_awfc = self.ref_scenario.get_annual_world_first_cost(region)
        years = list(range(self.base_year, self.end_year +1))
        result = (pds_awfc - ref_awfc).loc[years]
        
        return result.sum() / 1000  # in billions

    
    def get_cumulative_first_cost_pds(self, region) -> np.float64:

        years = list(range(self.base_year, self.end_year +1))

        pds_fc = self.pds_scenario.get_annual_world_first_cost(region)

        result = pds_fc.loc[years]

        return result.sum() / 1000  # in billions


    
    def get_operating_cost(self, region) -> np.float64:

        # TODO: confirm start_year-1 is desired. Why does it start in 2019?

        pds_series = self.pds_scenario.get_operating_cost(region, self.end_year) * (1+ self.disturbance_rate)
        pds_result = pds_series.cumsum().loc[self.end_year] - pds_series.cumsum().loc[self.start_year]

        ref_series = self.ref_scenario.get_operating_cost(region, self.end_year) * (1+self.disturbance_rate)
        ref_result = ref_series.cumsum().loc[self.end_year] - ref_series.cumsum().loc[self.start_year]

        result = (ref_result - pds_result) / 1000 # in billions

        return result

    
    def get_lifetime_operating_savings(self, region) -> np.float64:

        
        pds_series = self.pds_scenario.get_lifetime_operating_savings(region, self.end_year) * (1+ self.disturbance_rate)

        # TODO: subtract this from conventional.

        result = - pds_series.sum()

        return result / 1_000 # express in billions of USD



    def get_lifetime_cashflow_npv_single(self, region, purchase_year) -> np.float64:

        discount_rate = self.npv_discount_rate
        pds_series = -1 * self.pds_scenario.get_lifetime_cashflow_npv(region, purchase_year, discount_rate)

        # s/sht claims this is solution relative to conventional - is it? -seems like it's only soluion
        result = pds_series.sum()

        return result / 1_000 # express in billions of USD

    def get_payback_period_soln_only(self, region, purchase_year) -> np.float64:

        discount_rate = self.npv_discount_rate
        pds_series = -1 * self.pds_scenario.get_lifetime_cashflow_npv(region, purchase_year, discount_rate)

        cumulative_sum = pds_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_payback_period_soln_only_npv(self, region, purchase_year) -> np.float64:

        discount_rate = self.npv_discount_rate

        pds_series = -1 * self.pds_scenario.get_lifetime_cashflow_npv(region, purchase_year, discount_rate)

        cumulative_sum = pds_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_payback_period_soln_to_conv(self, region, purchase_year) -> np.float64:

        #$K$122 on Operating Cost spreadsheet tab.

        # Use discount rate of 0.0 to avoid discounting.
        discount_rate = 0.0

        # Don't use ref_series here, use "conventional" series instead.
        # Since the "conventional" concept isn't applicable for seaweed farming, just use a zero timeseries.

        pds_series = self.pds_scenario.get_lifetime_cashflow_npv(region, purchase_year, discount_rate)

        net_series = -pds_series

        cumulative_sum = net_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_payback_period_soln_to_conv_npv(self, region, purchase_year) -> np.float64:

        discount_rate = self.npv_discount_rate

        # Don't use ref_series here, use "conventional" series instead.
        # Since the "conventional" concept isn't applicable for seaweed farming, just use a zero timeseries.

        pds_series = self.pds_scenario.get_lifetime_cashflow_npv(region, purchase_year, discount_rate)

        net_series =  -pds_series

        cumulative_sum = net_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_lifetime_cashflow_npv_all(self, region) -> np.float64:

        # calculation matches "NPV" timeseries from [Operating Cost]!$E$125

        # TODO fc should be fc diff, so do the same thing for ref scenario and find diff.
        ref_fc = self.ref_scenario.get_annual_world_first_cost(region)
        pds_fc = self.pds_scenario.get_annual_world_first_cost(region)

        net_fc = ref_fc - pds_fc

        # fc_clipped should match "Investment (Reference First Cost minus PDS First Cost)" timeseries from [Operating Cost]!$B$125
        fc_clipped = net_fc.loc[self.start_year-1:self.end_year]

        # TODO op_cost should be op_cost diff, so do the same thing for ref scenario and find diff.
        # op_cost matches "Difference in Operating Cost (ref - pds)"" timeseries from [Operating Cost]!$C$125

        op_cost = - self.pds_scenario.get_lifetime_operating_savings(region, self.end_year) * (1+ self.disturbance_rate)

        net_cash_flow = fc_clipped.add(op_cost, fill_value = 0.0)

        rate = self.npv_discount_rate
        discount_factor = 1/(1+rate)

        num_rows = net_cash_flow.shape[0]

        discount_factors = [discount_factor**(row+1) for row in range(num_rows)]

        npv = net_cash_flow.multiply(discount_factors)
        
        result = npv.sum()
        
        return result / 1_000 # express in billions of USD


    def get_abatement_cost(self, region) -> np.float64:

        total_co2_reduction = self.get_total_co2_seq(region)

        pds_fc = self.pds_scenario.get_annual_world_first_cost(region)
        ref_fc = self.ref_scenario.get_annual_world_first_cost(region)

        # following should be [(ref_fc + conv_fc) - pds_fc], however haven't implemented conventional yet (not relevant for seaweed farming).
        net_fc = ref_fc - pds_fc

        # after executing this next line, fc_clipped should match time series in [Operating Cost]!$B$125
        fc_clipped = net_fc.loc[self.start_year-1:self.end_year]

        pds_op_cost = self.pds_scenario.get_lifetime_operating_savings(region, self.end_year)
        ref_op_cost = self.ref_scenario.get_lifetime_operating_savings(region, self.end_year)

        # after executing this next line, net_op_cost should match time series in [Operating Cost]!$C$125
        net_op_cost = (ref_op_cost -pds_op_cost) * (1+ self.disturbance_rate)

        net_cash_flow = fc_clipped.add(net_op_cost, fill_value = 0.0)
        
        rate = self.npv_discount_rate
        discount_factor = 1/(1+rate)

        num_rows = net_cash_flow.shape[0]

        discount_factors = [discount_factor**(row+1) for row in range(num_rows)]

        npv = net_cash_flow.multiply(discount_factors)
        npv_summed = npv.loc[self.start_year: self.end_year].sum()

        result = -1 * npv_summed/total_co2_reduction

        return result / 1_000 # express in billions of USD


    def get_net_profit_margin(self, region):

        margin_series = self.pds_scenario.get_net_profit_margin(region, self.end_year) * (1- self.disturbance_rate)
        margin_series_cum = margin_series.cumsum()

        end_year_val = margin_series_cum.loc[self.end_year]
        start_year_val = margin_series_cum.loc[self.start_year]

        result = end_year_val - start_year_val
        
        return result / 1_000 # express in billions of USD


    def get_lifetime_profit_margin(self, region) -> np.float64:

        margin_series = self.pds_scenario.get_net_profit_margin(region, self.end_year) * (1- self.disturbance_rate)

        result  = margin_series.sum()

        return result / 1_000 # express in billions of USD


    def get_total_co2_seq(self, region) -> np.float64:

        pds_sequestration = self.pds_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)
        ref_sequestration = self.ref_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)

        net_sequestration = (pds_sequestration - ref_sequestration)

        result = net_sequestration.loc[self.start_year+1 : self.end_year].sum()

        return result / 1_000 # express in billions of USD


    def get_change_in_ppm_equiv_series(self, region) -> np.float64:

        pds_sequestration = self.pds_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)
        ref_sequestration = self.ref_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)

        net_sequestration = (pds_sequestration - ref_sequestration)

        result_years = list(range(self.start_year-1, self.end_year+1))
        results = pd.Series(index = result_years, dtype=np.float64)
        results = results.fillna(0.0)
        # (0.217 + 0.259*EXP(-(A173-$A$173+1)/172.9) + 0.338*EXP(-(A173-$A$173+1)/18.51) + 0.186*EXP(-(A173-$A$173+1)/1.186))
        # (0.217 + 0.259*EXP(-(current_year-year_zero+1)/172.9) + 0.338*EXP(-(current_year-year_zero+1)/18.51) + 0.186*EXP(-(current_year-year_zero+1)/1.186))

        for iter_year in result_years:
            year_results = []
            exponent=0

            for current_year in range(iter_year, result_years[-1] +1):
                year_net_adoption = net_sequestration.loc[iter_year]
                exponent += 1
                val =  0.217 + 0.259*np.exp(-(exponent)/172.9) 
                val += 0.338*np.exp(-(exponent)/18.51) 
                val += 0.186*np.exp(-(exponent)/1.186)
                year_results.append(year_net_adoption * val)

            year_results_series = pd.Series(index = range(iter_year, self.end_year+1), dtype=np.float64)
            year_results_series = year_results_series.fillna(0.0)
            year_results_series = year_results_series.add(year_results)

            results = results.add(year_results_series, fill_value=0.0)

        factor = (1_000_000 * 10**6 ) / 44.01
        factor = factor / (1.8 * 10**20)
        factor = factor * 10**6
        results = results * factor
        return results


    def get_change_in_ppm_equiv(self,region) -> np.float64:
        series = self.get_change_in_ppm_equiv_series(region)
        return series.loc[self.end_year]



    def get_change_in_ppm_equiv_final_year(self, region) -> np.float64:
        series = self.get_change_in_ppm_equiv_series(region)
        return series.loc[self.end_year] - series.loc[self.end_year-1]
        

    def get_max_annual_co2_sequestered(self, region) -> np.float64:

        pds_sequestration = self.pds_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)
        ref_sequestration = self.ref_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)

        net_sequestration = (pds_sequestration - ref_sequestration)

        result = max(net_sequestration.loc[self.start_year:self.end_year])

        return result / 1_000


    def get_co2_sequestered_final_year(self, region) -> np.float64:

        pds_sequestration = self.pds_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)
        ref_sequestration = self.ref_scenario.get_carbon_sequestration(region, self.sequestration_rate_all_ocean, self.disturbance_rate)

        net_sequestration = (pds_sequestration - ref_sequestration)

        result = net_sequestration.loc[self.end_year]

        return result / 1_000


