
import sys
import pandas as pd
import numpy as np
import json
import yaml

from model.ocean_scenario import OceanScenario
from model.new_unit_adoption import NewUnitAdoption as UnitAdoption
from model.solution import Solution

class OceanSolution(Solution):
    """ This is the base class that each Ocean solution should inherit from.
    Contains all the calculations required for Ocean-based scenario results.
    """

    config : dict
    scenario : OceanScenario

    def _load_config_file(self, file_name):
        
        stream = open(file_name, 'r')
        config = yaml.load(stream, Loader=yaml.FullLoader)
        self.start_year = config['start_year']
        self.end_year = config['end_year']
        self.base_year = config['base_year']

        self.pds_adoption_file = config['PDS_adoption_file']
        self.ref_adoption_file = config['REF_adoption_file']
        self.scenarios_file = config['scenarios_file']

        self.required_version_minimum = tuple(int(st) for st in str.split(config['required_python_version_minimum'], '.'))
        self._config = config

    def _load_adoption_scenario(self, adoption_input_file, adoption_scenario_name):
            
        try:
            ad_scenario = UnitAdoption(self.base_year,self.start_year, self.end_year, adoption_scenario_name, adoption_input_file)
        except ValueError as ev:
            print(ev.args)
            raise ValueError(f"Unable to initialise {adoption_scenario_name}")
        
        return ad_scenario

    def _load_pds_scenario(self):
        self.pds_scenario = self._load_adoption_scenario(self.pds_adoption_file,
                        self.scenario.pds_scenario_name)
        
    def _load_ref_scenario(self):
        self.ref_scenario = self._load_adoption_scenario(self.ref_adoption_file,
                        self.scenario.ref_scenario_name)

    # Initialize from configuration file:
    def __init__(self, configuration_file_name):
        print('ocean_solution initializing...')
        self._load_config_file(configuration_file_name)
        if sys.version_info < self.required_version_minimum:
            print(f'Warning - you are running python version {sys.version}. Version {self.required_version_minimum} or greater is required.')

    def set_up_area_units(self, unit_adoption: UnitAdoption) -> None:
        # This should produce a flat line with y = constant = self.total_area
        unit_adoption.set_area_units_linear(
            total_area= self.scenario.current_area_world,
            change_per_period= self.scenario.change_per_period,
            total_area_as_of_period= self.scenario.total_area_as_of_period
            )

        unit_adoption.apply_clip(lower= None, upper= self.scenario.current_area_world)
        unit_adoption.apply_linear_regression()

    def load_scenario(self, scenario_name: str) -> None:

        print(f'Loading scenario {scenario_name}')

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        print(scen_dict[scenario_name])

        scenario = OceanScenario(**scen_dict[scenario_name])

        self.scenario = scenario

        self._load_pds_scenario()
        
        if self.scenario.ref_scenario_name:
            self._load_ref_scenario()
        else:
            # creates a ref scenario with zeroes.
            self.ref_scenario = self.pds_scenario.get_skeleton()

        # PDS and REF have a similar area_units structure.
    
        self.set_up_area_units(self.pds_scenario)
        self.set_up_area_units(self.ref_scenario)
        
        return

    def get_scenario_names(self):

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)
        
        return list(scen_dict.keys())
    

    def get_loaded_scenario_name(self):
        return self.scenario.description

    
        
    # Unit Adoption functions:

    def get_adoption_unit_increase_pds_vs_ref_final_year(self) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted() 
        ref_series = self.ref_scenario.get_units_adopted()

        net_series = pds_series.subtract(ref_series)

        return net_series.loc[self.end_year]
        
    def get_adoption_unit_increase_pds_final_year(self) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted() 
        return pds_series.loc[self.end_year]


    def get_global_percent_adoption_base_year(self) -> np.float64:
        # Adoption for base year, as a percentage of TOA.
        
        adoption_base_year = self.scenario.current_adoption_world
        
        area_units_series = self.pds_scenario.get_area_units_units()
        area_units_base_year = area_units_series.loc[self.base_year+1]
        result  = adoption_base_year / area_units_base_year
        return result


    def get_percent_adoption_start_year(self) -> np.float64:

        pds_series = self.pds_scenario.get_units_adopted()
        area_units_series = self.pds_scenario.get_area_units_units()

        pds_start_year = pds_series.loc[self.start_year]
        area_units_start_year = area_units_series.loc[self.start_year]

        result = pds_start_year / area_units_start_year
        return result
    

    def get_percent_adoption_end_year(self) -> np.float64:
        pds_series = self.pds_scenario.get_units_adopted()
        area_units_series = self.pds_scenario.get_area_units_units()
        
        pds_start_year = pds_series.loc[self.end_year]
        area_units_start_year = area_units_series.loc[self.end_year]

        result = pds_start_year / area_units_start_year
        return result



    ### Financial functions:

    def get_marginal_first_cost(self) -> np.float64:
        
        # pds_awfc corresponds to the "Annual World First Cost" column (solution-pds)
        # in [First Cost]!$E$36 in the spreadsheet.

        pds_awfc = self.pds_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)
        
        # ref_awfc corresponds to the "Annual World First Cost" column (solution-ref)
        # in [First Cost]!$N$36 in the spreadsheet.

        ref_awfc = self.ref_scenario.get_annual_world_first_cost(self.scenario.conventional_expected_lifetime, self.scenario.conventional_first_cost)

        net_awfc = pds_awfc - ref_awfc

        result = net_awfc.loc[self.start_year-1: self.end_year]
        # years = list(range(self.base_year, self.end_year +1))
        # result = (pds_awfc - ref_awfc).loc[years]
        
        return result.sum() / 1000  # in billions

    
    def get_cumulative_first_cost_pds(self) -> np.float64:

        years = list(range(self.base_year, self.end_year +1))

        pds_fc = self.pds_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)

        result = pds_fc.loc[years]

        return result.sum() / 1000  # in billions


    
    def get_operating_cost(self) -> np.float64:

        # TODO: confirm start_year-1 is desired. Why does it start in 2019?

        # Each cell in pds_series should match SUM($C266:$AV266) in [Operating Cost] worksheet.

        pds_series = self.pds_scenario.get_operating_cost(
                self.scenario.solution_expected_lifetime,
                self.scenario.solution_operating_cost
                ) * (1+ self.scenario.disturbance_rate)
        pds_result = pds_series.cumsum().loc[self.end_year] - pds_series.cumsum().loc[self.start_year]

        # Each cell in ref_series should match SUM($C403:$AV403) in [Operating Cost] worksheet.
        ref_series = self.ref_scenario.get_operating_cost(
                self.scenario.conventional_expected_lifetime,
                self.scenario.conventional_operating_cost
                ) * (1+self.scenario.disturbance_rate)

        ref_result = ref_series.cumsum().loc[self.end_year] - ref_series.cumsum().loc[self.start_year]

        result = (ref_result - pds_result) / 1000 # in billions

        # result should match "Difference in Operating Cost (Reference - PDS)". [Operating Cost]!$C$125

        return result

    
    def get_lifetime_operating_savings(self) -> np.float64:
        
        # pds_series should match [Operating Cost]!$C$125 = "Difference in Operating Cost (Reference minus PDS)"
        pds_series = self.pds_scenario.get_lifetime_operating_savings(self.scenario.solution_expected_lifetime, self.scenario.solution_operating_cost)

        pds_series *= (1+ self.scenario.disturbance_rate)


        # TODO: subtract this from conventional.

        result = - pds_series.sum()

        return result / 1_000 # express in billions of USD



    def get_lifetime_cashflow_npv_single(self, purchase_year) -> np.float64:

        discount_rate = self.scenario.npv_discount_rate
        pds_series = -1 * self.pds_scenario.get_lifetime_cashflow_npv(
            purchase_year,
            discount_rate,
            self.scenario.solution_expected_lifetime,
            self.scenario.solution_operating_cost,
            self.scenario.solution_first_cost
            )

        result = pds_series.sum()

        return result / 1_000 # express in billions of USD


    def get_payback_period_soln_only(self, purchase_year) -> np.float64:

        pds_series = -1 * self.pds_scenario.get_lifetime_cashflow_npv(
            purchase_year,
            self.scenario.npv_discount_rate,
            self.scenario.solution_expected_lifetime,
            self.scenario.solution_operating_cost,
            self.scenario.solution_first_cost)

        cumulative_sum = pds_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_payback_period_soln_only_npv(self, purchase_year) -> np.float64:


        pds_series = -1 * self.pds_scenario.get_lifetime_cashflow_npv(
            purchase_year,
            self.scenario.npv_discount_rate,
            self.scenario.solution_expected_lifetime,
            self.scenario.solution_operating_cost,
            self.scenario.solution_first_cost)

        cumulative_sum = pds_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_payback_period_soln_to_conv(self, purchase_year) -> np.float64:

        #$K$122 on Operating Cost spreadsheet tab.

        # Use discount rate of 0.0 to avoid discounting.
        discount_rate = 0.0

        # Don't use ref_series here, use "conventional" series instead.
        # Since the "conventional" concept isn't applicable for seaweed farming, just use a zero timeseries.

        pds_series = self.pds_scenario.get_lifetime_cashflow_npv(
            purchase_year,
            self.scenario.npv_discount_rate,
            self.scenario.solution_expected_lifetime,
            self.scenario.solution_operating_cost,
            self.scenario.solution_first_cost
            )

        net_series = -pds_series

        cumulative_sum = net_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_payback_period_soln_to_conv_npv(self, purchase_year) -> np.float64:

        
        # Don't use ref_series here, use "conventional" series instead.
        # Since the "conventional" concept isn't applicable for seaweed farming, just use a zero timeseries.

        pds_series = self.pds_scenario.get_lifetime_cashflow_npv(
            purchase_year,
            self.scenario.npv_discount_rate,
            self.scenario.solution_expected_lifetime,
            self.scenario.solution_operating_cost,
            self.scenario.solution_first_cost)

        net_series =  -pds_series

        cumulative_sum = net_series.cumsum()

        max_val_index = cumulative_sum.argmax()
        max_val = cumulative_sum.iloc[max_val_index]

        return max_val


    def get_lifetime_cashflow_npv_all(self) -> np.float64:
        
        # calculation matches "NPV" timeseries from [Operating Cost]!$E$125

        pds_fc = self.pds_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)
        ref_fc = self.ref_scenario.get_annual_world_first_cost(self.scenario.conventional_expected_lifetime, self.scenario.conventional_first_cost)

        net_fc = ref_fc - pds_fc

        # fc_clipped should match "Investment (Reference First Cost minus PDS First Cost)" timeseries from [Operating Cost]!$B$125
        fc_clipped = net_fc.loc[self.start_year-1:self.end_year]

        # TODO op_cost should be op_cost diff, so do the same thing for ref scenario and find diff.
        # op_cost matches "Difference in Operating Cost (ref - pds)"" timeseries from [Operating Cost]!$C$125

        op_cost = - self.pds_scenario.get_lifetime_operating_savings(self.scenario.solution_expected_lifetime, self.scenario.solution_operating_cost)
        op_cost *= (1+ self.scenario.disturbance_rate)

        net_cash_flow = fc_clipped.add(op_cost, fill_value = 0.0)

        rate = self.scenario.npv_discount_rate
        discount_factor = 1/(1+rate)

        num_rows = net_cash_flow.shape[0]

        discount_factors = [discount_factor**(row+1) for row in range(num_rows)]

        npv = net_cash_flow.multiply(discount_factors, axis = 'index')
        
        result = npv.sum()
        
        return result / 1_000 # express in billions of USD


    def get_abatement_cost(self) -> np.float64:

        total_co2_reduction = self.get_total_co2_sequestered()

        pds_fc = self.pds_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)
        ref_fc = self.ref_scenario.get_annual_world_first_cost(self.scenario.conventional_expected_lifetime, self.scenario.conventional_first_cost)

        # following should be [(ref_fc + conv_fc) - pds_fc], however haven't implemented conventional yet (not relevant for seaweed farming).
        net_fc = ref_fc - pds_fc

        # after executing this next line, fc_clipped should match time series in [Operating Cost]!$B$125
        fc_clipped = net_fc.loc[self.start_year-1:self.end_year]

        pds_op_cost = self.pds_scenario.get_lifetime_operating_savings(self.scenario.solution_expected_lifetime, self.scenario.solution_operating_cost)
        ref_op_cost = self.ref_scenario.get_lifetime_operating_savings(self.scenario.conventional_expected_lifetime, self.scenario.conventional_operating_cost)

        # after executing this next line, net_op_cost should match time series in [Operating Cost]!$C$125
        net_op_cost = (ref_op_cost -pds_op_cost) * (1+ self.scenario.disturbance_rate)

        net_cash_flow = fc_clipped.add(net_op_cost).fillna(0.0)
        
        rate = self.scenario.npv_discount_rate
        discount_factor = 1/(1+rate)

        num_rows = net_cash_flow.shape[0]

        discount_factors = [discount_factor**(row+1) for row in range(num_rows)]

        npv = net_cash_flow.multiply(discount_factors, axis='index')
        npv_summed = npv.loc[self.start_year: self.end_year].sum()

        result = -1 * npv_summed/total_co2_reduction

        return result / 1_000 # express in billions of USD


    def get_net_profit_margin(self) -> np.float64:

        margin_series = self.pds_scenario.get_net_profit_margin(self.scenario.solution_expected_lifetime, self.scenario.solution_net_profit_margin)
        margin_series *= (1- self.scenario.disturbance_rate)
        margin_series_cum = margin_series.cumsum()

        end_year_val = margin_series_cum.loc[self.end_year]
        start_year_val = margin_series_cum.loc[self.start_year]

        result = end_year_val - start_year_val
        
        return result / 1_000 # express in billions of USD


    def get_lifetime_profit_margin(self) -> np.float64:

        margin_series = self.pds_scenario.get_net_profit_margin(self.scenario.solution_expected_lifetime, self.scenario.solution_net_profit_margin)
        margin_series *= (1- self.scenario.disturbance_rate)

        result  = margin_series.sum()

        return result / 1_000 # express in billions of USD


### Start Emissions Reduction Calculations ###

    def get_emissions_reduction_series(self) -> pd.Series:
        
        emissions_reduction_series_pds =self.pds_scenario.get_emissions_reduction_series(
            self.scenario.disturbance_rate,
            self.scenario.growth_rate_of_ocean_degradation,
            self.scenario.delay_impact_of_protection_by_one_year,
            self.scenario.emissions_reduced_per_unit_area,
            self.scenario.use_aggregate_CO2_equivalent_instead_of_individual_GHG)

        emissions_reduction_series_ref = self.ref_scenario.get_emissions_reduction_series(
            self.scenario.disturbance_rate,
            self.scenario.growth_rate_of_ocean_degradation,
            self.scenario.delay_impact_of_protection_by_one_year,
            self.scenario.emissions_reduced_per_unit_area,
            self.scenario.use_aggregate_CO2_equivalent_instead_of_individual_GHG)

        emissions_reduction_series = emissions_reduction_series_pds - emissions_reduction_series_ref

        result = emissions_reduction_series.loc[self.start_year: self.end_year]
        
        return result


    def get_total_emissions_reduction(self):

        total_emissions_reduction = self.get_emissions_reduction_series()
        result = total_emissions_reduction.sum()

        return result / 1000


    def get_emissions_reduction_final_year(self):

        total_emissions_reduction = self.get_emissions_reduction_series()
        result = total_emissions_reduction.loc[self.end_year]
        
        return result / 1000


    def get_max_annual_emissions_reduction(self) -> np.float64:
        total_emissions_reduction = self.get_emissions_reduction_series()
        result = total_emissions_reduction.max()
        
        return result / 1000


### End Emissions Reduction Calculations ###


### Start Carbon Sequestration Calculations ###

    def get_carbon_sequestration_series(self):
        # Should match "Carbon Sequestration Calculations" on "CO2 Calcs" worksheet.
        pds_sequestration = self.pds_scenario.get_carbon_sequestration(
                    self.scenario.sequestration_rate_all_ocean,
                    self.scenario.disturbance_rate,
                    self.scenario.growth_rate_of_ocean_degradation,
                    self.scenario.delay_impact_of_protection_by_one_year,
                    self.scenario.delay_regrowth_of_degraded_land_by_one_year,
                    self.scenario.use_adoption_for_carbon_sequestration_calculation)

        ref_sequestration = self.ref_scenario.get_carbon_sequestration(
                    self.scenario.sequestration_rate_all_ocean,
                    self.scenario.disturbance_rate,
                    self.scenario.growth_rate_of_ocean_degradation,
                    self.scenario.delay_impact_of_protection_by_one_year,
                    self.scenario.delay_regrowth_of_degraded_land_by_one_year,
                    self.scenario.use_adoption_for_carbon_sequestration_calculation)
        
        # net_sequestration should equal 'CO2-eq PPM Calculator' on tab [CO2 Calcs]!$B$224
        net_sequestration = (pds_sequestration - ref_sequestration)

        return net_sequestration.loc[self.start_year:self.end_year]

    def get_total_co2_sequestered(self) -> np.float64:
        
        carbon_sequestration_series = self.get_carbon_sequestration_series()

        result = carbon_sequestration_series.loc[self.start_year + 1: self.end_year].sum()

        return result / 1_000 # express in billions of USD

    def get_max_annual_co2_sequestered(self) -> np.float64:

        carbon_sequestration_series = self.get_carbon_sequestration_series()
        
        result = max(carbon_sequestration_series.loc[self.start_year: self.end_year])

        return result / 1_000

    
    def get_co2_sequestered_final_year(self) -> np.float64:

        carbon_sequestration_series = self.get_carbon_sequestration_series()
        
        result = carbon_sequestration_series.loc[self.end_year]

        return result / 1_000

### End Carbon Sequestration Calculations ###


### Start PPM Equivalent Calculations ###

    def get_change_in_ppm_equivalent_series(self) -> np.float64:
        
        pds_sequestration = self.pds_scenario.get_change_in_ppm_equivalent_series(
            self.scenario.sequestration_rate_all_ocean,
            self.scenario.disturbance_rate,
            self.scenario.growth_rate_of_ocean_degradation,
            self.scenario.delay_impact_of_protection_by_one_year,
            self.scenario.emissions_reduced_per_unit_area,
            self.scenario.delay_regrowth_of_degraded_land_by_one_year,
            self.scenario.use_adoption_for_carbon_sequestration_calculation,
            self.scenario.use_aggregate_CO2_equivalent_instead_of_individual_GHG)

        ref_sequestration = self.ref_scenario.get_change_in_ppm_equivalent_series(
            self.scenario.sequestration_rate_all_ocean,
            self.scenario.disturbance_rate,
            self.scenario.growth_rate_of_ocean_degradation,
            self.scenario.delay_impact_of_protection_by_one_year,
            self.scenario.emissions_reduced_per_unit_area,
            self.scenario.delay_regrowth_of_degraded_land_by_one_year,
            self.scenario.use_adoption_for_carbon_sequestration_calculation,
            self.scenario.use_aggregate_CO2_equivalent_instead_of_individual_GHG)
        
        net_sequestration = (pds_sequestration - ref_sequestration)
        
        return net_sequestration.loc[self.start_year:self.end_year]

    def get_change_in_ppm_equivalent(self) -> np.float64:
        
        change_in_ppm_equivalent_series = self.get_change_in_ppm_equivalent_series()

        result = change_in_ppm_equivalent_series.loc[self.end_year]

        return result

    def get_change_in_ppm_equivalent_final_year(self) -> np.float64:
                
        change_in_ppm_equivalent_series = self.get_change_in_ppm_equivalent_series()

        result = change_in_ppm_equivalent_series.loc[self.end_year] - change_in_ppm_equivalent_series.loc[self.end_year-1]

        return result
        
### End PPM Equivalent Calculations ###


### Start Area Calculations ###

    def get_reduced_area_degradation(self) -> np.float64:
        total_undegraded_area_pds = self.pds_scenario.get_total_undegraded_area(
            self.scenario.growth_rate_of_ocean_degradation,
            self.scenario.disturbance_rate,
            self.scenario.delay_impact_of_protection_by_one_year
            )
        total_undegraded_area_ref = self.ref_scenario.get_total_undegraded_area(
            self.scenario.growth_rate_of_ocean_degradation,
            self.scenario.disturbance_rate,
            self.scenario.delay_impact_of_protection_by_one_year
            )
 
        total_undegraded_area = total_undegraded_area_pds - total_undegraded_area_ref

        result = total_undegraded_area.loc[self.end_year] - total_undegraded_area.loc[self.start_year - 1]

        return result


    def get_carbon_under_protection_final_year(self) -> np.float64:

        cumulative_degraded_area_under_protection_pds = self.pds_scenario.get_cumulative_degraded_area_under_protection(
            self.scenario.delay_impact_of_protection_by_one_year,
            self.scenario.disturbance_rate
            )

        degraded_area_under_protection_end_year = cumulative_degraded_area_under_protection_pds.loc[self.end_year]

        adoption_unit_increase_pds_final_year = self.get_adoption_unit_increase_pds_final_year()
        
        result = adoption_unit_increase_pds_final_year + degraded_area_under_protection_end_year

        result *= self.scenario.carbon_storage_in_protected_area_type

        return result / 1_000

    
    def get_co2_under_protection_final_year(self) -> np.float64:
        carbon_to_co2_ratio = 3.664
        result = self.get_carbon_under_protection_final_year()
        result *= carbon_to_co2_ratio
        return result
