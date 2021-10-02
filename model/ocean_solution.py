
import os
import sys
from math import floor, ceil
from typing import Optional

import pandas as pd
import numpy as np
import json
import yaml

from model.ocean_scenario import OceanScenario
from model.new_unit_adoption import NewUnitAdoption as UnitAdoption
from model.ocean_tam import OceanTam
from model.solution import Solution

class OceanSolution(Solution):
    """Implement all the calculations required for solutions in the Ocean sector."""
    _config : dict
    scenario : OceanScenario
    _tam : OceanTam
    has_tam: bool
    has_grid_emissions_factors: bool

    def _load_config_file(self, file_name: str):
        
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

    def _load_adoption_scenario(self, adoption_input_file: str, adoption_scenario_name: str):
            
        try:
            ad_scenario = UnitAdoption(self.base_year, self.start_year, self.end_year, adoption_scenario_name, adoption_input_file)
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
    def __init__(self, configuration_file_name: str):
        """Read configuration file."""
        self._load_config_file(configuration_file_name)
        if sys.version_info < self.required_version_minimum:
            print(f'Warning - you are running python version {sys.version}. Version {self.required_version_minimum} or greater is required.')
        
        self.has_tam = self._config.get('TAM_data_file', False)
        if self.has_tam:
            # proceed to load the tam file
            tam_file = self._config['TAM_data_file']
            if not os.path.isfile(tam_file):
                msg = f'Cannot find file {tam_file}.'
                raise ValueError(msg)

            tam = OceanTam(self.base_year, self.start_year, self.end_year, tam_file)
            tam.apply_3d_poly()
            self._tam = tam
            self.has_tam = True

        self.has_grid_emissions_factors = self._config.get('grid_emissions_factors', False)
        if self.has_grid_emissions_factors:
            gef_file = self._config['grid_emissions_factors']
            if not os.path.isfile(gef_file):
                msg = f'Cannot find file {gef_file}.'
                raise ValueError(msg)

            stream = open(gef_file,'r')
            json_dict = json.load(stream)
            
            idx, vals = zip(*json_dict['data']) # list of two-element lists
            self._grid_emissions_factors = pd.Series(data=vals, index=idx)
            self.has_grid_emissions_factors = True
        
        return

    def set_up_area_units(self, unit_adoption: UnitAdoption) -> None:
        """Set up functional units. Can be land area, ocean area, units adopted."""
        # This should produce a flat line with y = constant = self.total_area
        unit_adoption.set_area_units_linear(
            total_area= self.scenario.current_area_world,
            change_per_period= self.scenario.change_per_period,
            total_area_as_of_period= self.scenario.total_area_as_of_period
            )

        unit_adoption.apply_clip(lower= None, upper= self.scenario.current_area_world)
        unit_adoption.apply_linear_regression()
        return

    def load_scenario(self, scenario_name: str) -> None:
        """Read the scenario inputs file. Load the pds scenario, ref scenario and set up the unit adoption."""
        print(f'Loading scenario {scenario_name}')

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
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

    def get_scenario_names(self):
        """Find all scenario names configure in the scenario inputs file."""
        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)
        
        return list(scen_dict.keys())

    def get_loaded_scenario_name(self):
        """Return the name of the loaded scenario."""
        return self.scenario.description
        
    # Unit Adoption functions:

    def get_adoption_unit_increase_pds_vs_ref_final_year(self) -> float:
        """Return the difference between the units adopted in the pds scenario and the reference scenario for the final year of the reporting period."""
        # Key Adoption Result
        # Presented on the "Advanced Controls" tab:
        # "Adoption Unit Increase in 2050 (PDS vs REF)"

        pds_series = self.pds_scenario.get_units_adopted() 
        ref_series = self.ref_scenario.get_units_adopted()
        net_series = pds_series.subtract(ref_series)
        return net_series.loc[self.end_year]
        
    def get_adoption_unit_increase_pds_final_year(self) -> float:
        """Return the functional units adopted in the pds scenario only, for the final year of the reporting period."""
        # Presented on the "Advanced Controls" tab:
        # "Global Units of Adoption in 2050"
        pds_series = self.pds_scenario.get_units_adopted() 
        return pds_series.loc[self.end_year]

    def get_global_percent_adoption_base_year(self) -> float:
        """ Return the world current adoption as a percentage of the total functional units adopted for the base year."""
        # Presented on the "Advanced Controls" tab:
        # "Global Percent Adoption in Base Year (2014)"
        adoption_base_year = self.scenario.current_adoption_world
        area_units_series = self.pds_scenario.get_area_units()
        area_units_base_year = area_units_series.loc[self.base_year+1]

        result  = adoption_base_year / area_units_base_year
        return result

    def get_percent_adoption_start_year(self) -> float:
        """ Return the functional units adopted for the start year as a percentage of the total area (or total addressable market if appropriate) for the start year of the reporting period."""
        # Presented on the "Advanced Controls" tab:
        # "Global Percent Adoption in Year 1: 2020"
        pds_series = self.pds_scenario.get_units_adopted()
        pds_start_year = pds_series.loc[self.start_year]

        if self.has_tam:
            area_units_series = self._tam.get_tam_series()
        else:
            area_units_series = self.pds_scenario.get_area_units()

        area_units_start_year = area_units_series.loc[self.start_year]
        result = pds_start_year / area_units_start_year
        return result
    

    def get_percent_adoption_end_year(self) -> float:
        """ Return the functional units adopted for the final year as a percentage of the total area (or total addressable market if appropriate) for the final year of the reporting period."""
        # Presented on the "Advanced Controls" tab:
        # "Global Percent Adoption in Year 2: 2050"
        pds_series = self.pds_scenario.get_units_adopted()
        pds_start_year = pds_series.loc[self.end_year]

        if self.has_tam:
            area_units_series = self._tam.get_tam_series()
        else:
            area_units_series = self.pds_scenario.get_area_units()

        area_units_start_year = area_units_series.loc[self.end_year]
        result = pds_start_year / area_units_start_year
        return result



    ### Financial functions:

    def get_annual_world_first_cost_series(self) -> pd.Series:
        """Calculates the annual cumulative first cost of the implementation of global units by multiplying global units (including any replacement units)
         installed by install cost per unit. Both PDS, Reference and conventional scenarios are calculated."""

        # pds_awfc corresponds to the "Annual World First Cost" column (solution-pds)
        # [First Cost]!$E$36
        pds_solution_awfc = self.pds_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)
        # ref_awfc corresponds to the "Annual World First Cost" column (solution-ref)
        # [First Cost]!$N$36
        ref_solution_awfc = self.ref_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)
        
        pds_units_adopted = self.pds_scenario.get_units_adopted()
        ref_units_adopted = self.ref_scenario.get_units_adopted()
        net_units_adopted = pds_units_adopted - ref_units_adopted
        
        net_units_adopted_lagged = net_units_adopted.loc[self.base_year-1:].diff()
        # conventional first cost removes negative values at the net level, so can't use self.pds/ref_scenario.get_annual_world_first_cost(...)
        net_units_adopted_lagged.clip(lower=0.0, inplace=True)

        conventional_lifetime = self.scenario.conventional_expected_lifetime/self.scenario.conventional_average_annual_use
        conventional_expected_lifetime = floor(0.5 + conventional_lifetime)
        conventional_shifted = net_units_adopted_lagged.shift(conventional_expected_lifetime+1).fillna(0.0)
        conventional_shifted.clip(lower=0.0, inplace=True)
        conventional_awfc = (net_units_adopted_lagged + conventional_shifted) * self.scenario.conventional_first_cost
        
        first_cost_awfc = ref_solution_awfc + conventional_awfc - pds_solution_awfc 
        first_cost_awfc = first_cost_awfc * self.scenario.unit_converting_factor

        return first_cost_awfc.loc[:self.end_year]

    def get_marginal_first_cost(self) -> float:
        """
        Return the Marginal First Cost for the emissions reduction calculated for the study period.

        The Marginal First Cost is the increase in first costs for the emissions reduction calculated for the study period.
        This reduction may be partly due to implementation units installed after the base year but before the study period, and hence the first costs of these units should be counted.
        It is the Cumulative First Cost of the PDS minus the Cumulative First Cost of the Reference Scenario(REF) or 
        the increase in installation costs of the PDS over the REF for the study period. (US$2014 bn).
        """
        ## Key Adoption Result ##
        # Presented on the "Advanced Controls" tab:
        # "Marginal First Cost 2015-2050"
        annual_world_first_cost_series = self.get_annual_world_first_cost_series()
        result = -1 * annual_world_first_cost_series.sum() / 1e9
        return result  # in billions

    
    def get_cumulative_first_cost_solution(self) -> float:
        """
        Return the Cumulative First Cost for the solution.
        
        The Cumulative First Cost is the total cost of installations that provide the emissions reduction calculated.
        As this includes implementation units installed prior to the start of the study period,
        we include the first costs of all units from the base year to the final year of analysis (inclusive) in US$2014 bn.
        """
        # Presented on the "Advanced Controls" tab.
        # "Cumulative First Cost 2015-2050"

        years = list(range(self.base_year, self.end_year +1))
        pds_fc = self.pds_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)
        result = pds_fc.loc[years]
        result = result * self.scenario.unit_converting_factor

        return result.sum() / 1e9  # in billions

    def get_operating_cost_series(self) -> pd.Series:
        """Return the time series of the contribution of each new set of SOLUTION implementation units installed over the lifetime of the units.

        Calculated only for new or replacement units installed during the analysis period. Fixed and Variable costs that are constant or changing over time are included.
        """
        # Each cell in ref_series should match SUM($C262:$AV262) in [Operating Cost] worksheet.
        pds_solution_series = self.pds_scenario.get_operating_cost(
                self.scenario.solution_expected_lifetime,
                self.scenario.solution_operating_cost
                ) * (1+ self.scenario.disturbance_rate)

        # Each cell in ref_series should match SUM($C403:$AV403) in [Operating Cost] worksheet.
        ref_solution_series = self.ref_scenario.get_operating_cost(
                self.scenario.solution_expected_lifetime,
                self.scenario.solution_operating_cost
                ) * (1+self.scenario.disturbance_rate)

        net_solution_series = pds_solution_series - ref_solution_series

        pds_conventional_series = self.pds_scenario.get_operating_cost(
                self.scenario.solution_expected_lifetime,
                self.scenario.conventional_operating_cost
                ) * (1+ self.scenario.disturbance_rate)
        
        ref_conventional_series = self.ref_scenario.get_operating_cost(
                self.scenario.solution_expected_lifetime,
                self.scenario.conventional_operating_cost
                ) * (1+self.scenario.disturbance_rate)

        net_conventional_series = pds_conventional_series - ref_conventional_series
        result = net_conventional_series - net_solution_series
        result = result * self.scenario.unit_converting_factor
        
        return result

    def get_operating_cost(self) -> float:
        """Return the operating cost (or operating savings) of all implementation units (end year minus start year of study period). (US$2014 bn)"""
        ## Key Financial Result ##
        # Presented on the "Advanced Controls" tab.
        # "Net Operating Savings 2020-2050
        operating_cost_series = self.get_operating_cost_series()
        cumulative = operating_cost_series.cumsum()
        result = cumulative.loc[self.end_year] - cumulative.loc[self.start_year]
        result = result / 1e9 # in billions
        return result

    def get_lifetime_operating_savings(self) -> float:
        """Return the sum of all operating cost (or operating savings) of all implementation units across the study period. (US$2014 bn)"""
        ## Key Financial Result ##
        # Presented on the "Advanced Controls" tab.
        #Lifetime Operating Savings 2020 - 2050
        operating_cost_series = self.get_operating_cost_series()
        result = operating_cost_series.sum()
        result = result / 1e9 # in billions 
        return result

    def get_lifetime_cashflow_npv_single_series(self, purchase_year: int, discount_rate: float, solution_only: Optional[bool] = False) -> pd.Series:
        """ Return the discounted cashflows time series (PDS relative to the Reference Scenario - first cost and operating cost)
         for the full lifetime of a single implementation unit."""
        discount_factor = 1/(1+discount_rate)
        
        # "result" should match time series in [Operating Cost]!$J$125 = "NPV of Single Cashflows (to 2014)"
        years_old_at_start =  purchase_year - self.base_year + 1

        if solution_only:
            first_val = -1 * self.scenario.solution_first_cost
        else:
            first_val = self.scenario.conventional_first_cost - self.scenario.solution_first_cost

        first_val = first_val * discount_factor**(years_old_at_start)

        results : list[float] = []
        to_append = first_val
        
        solution_lifetime = ceil(self.scenario.solution_expected_lifetime)

        for year in range(ceil(solution_lifetime)):
            effective_operating_cost = self.scenario.conventional_operating_cost - self.scenario.solution_operating_cost
            remaining_solution_life = self.scenario.solution_expected_lifetime - year
            remaining_conventional_life = self.scenario.conventional_expected_lifetime - year

            if not solution_only:
                if remaining_conventional_life < 1.0 and remaining_conventional_life > 0.0:
                    to_append += self.scenario.conventional_first_cost * min(1.0, (self.scenario.solution_expected_lifetime - year) / self.scenario.conventional_expected_lifetime)
                    to_append += self.scenario.conventional_operating_cost - self.scenario.solution_operating_cost
                    to_append *= discount_factor**(years_old_at_start + year + 1)
                    results.append(to_append)
                    to_append = 0.0
                    continue
                
            if remaining_solution_life < 1.0: 
                effective_operating_cost *= remaining_solution_life

            to_append += effective_operating_cost * discount_factor**(years_old_at_start + year)
            results.append(to_append)
            to_append = 0.0

        result = pd.Series(results,pd.RangeIndex(self.base_year, self.base_year + solution_lifetime))
        return result * self.scenario.unit_converting_factor

    def get_lifetime_cashflow_npv_single(self, purchase_year: Optional[int] = None) -> float:
        """Return the sum of the net present value of all cashflows (PDS relative to the Reference Scenario - first cost and operating cost)
            for the full lifetime of a single implementation unit. ($US2014 bn)
        """
        # Presented on the "Advanced Controls" tab.
        # "Lifetime Cashflow NPV of Single Implementation Unit (PDS compared to REF scenario)""
        if purchase_year is None:
            purchase_year = self.start_year -3 # apply default

        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, self.scenario.npv_discount_rate)
        result_sum = lifetime_cashflow_npv_series.sum()
        return result_sum / 1e9 # in Billions USD

    def get_lifetime_cashflow_npv_series(self) -> pd.Series:
        """Return the timeseries of all discounted cashflows (first cost and operating savings) for the full lifetime of all implementation units
        adopted during study period."""

        annual_world_first_cost_series = self.get_annual_world_first_cost_series()
        operating_cost_series = self.get_operating_cost_series()
        net_cash_flow = operating_cost_series.add(annual_world_first_cost_series, fill_value=0.0)
        rate = self.scenario.npv_discount_rate
        discount_factor = 1/(1+rate)
        num_rows = net_cash_flow.shape[0]
        discount_factors = [discount_factor**row for row in range(num_rows)]
        npv = net_cash_flow.multiply(discount_factors, axis='index')
        return npv

    def get_lifetime_cashflow_npv_all(self) -> float:
        """Return the sum of all discounted cashflows (first cost and operating savings) for the full lifetime of all implementation units
        adopted during study period. (US$2014 bn)"""
        # Presented on the "Detailed Results" tab:
        # "Lifetime Cashflow NPV of All Implementation Units (PDS compared to REF Scenario)"
        
        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_series()
        result_sum = lifetime_cashflow_npv_series.sum()
        return result_sum / 1e9


    def get_payback_period_solution_only(self, purchase_year: Optional[int] = None) -> int:
        """Return the length of time taken to recover all investments costs where cashflows are NOT discounted.

        If a decision maker is considering an outright investment in the solution technology, he would want to know
        the payback of the solution in the absence of any conventional comparator.
        Some payback analysis calls for discounting cashflows, others do not."""
        # Presented on the "Advanced Controls" tab:
        # "Payback Period Solution Alone"

        if purchase_year is None:
            purchase_year = self.start_year-3 # Apply default

        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, discount_rate=0.0, solution_only=True)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_series.cumsum()

        result: int =-1
        for year, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = year - self.base_year + 1
                break

        return result

    def get_payback_period_solution_only_npv(self, purchase_year: Optional[int] = None) -> int:
        """Return the length of time taken to recover all investments costs where cashflows ARE discounted.

        If a decision maker is considering an outright investment in the solution technology, he would want to know
        the payback of the solution in the absence of any conventional comparator.
        Some payback analysis calls for discounting cashflows, others do not."""
        # Presented on the "Advanced Controls" tab:
        # "Discounted Payback Period Solution Alone"

        if purchase_year is None:
            purchase_year = self.start_year-3 # Apply default

        lifetime_cashflow_npv_single_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, self.scenario.npv_discount_rate, solution_only=True)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_single_series.cumsum()

        result: int =-1
        for idx, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = idx - self.base_year + 1
                break

        return result


    def get_payback_period_solution_vs_conventional(self, purchase_year: Optional[int]  = None) -> int:
        """Return the length of time taken to recover all investments costs (above and beyond the conventional technology costs) where cashflows are NOT discounted.

        If a decision maker is comparing two projects, one with the conventional technology,and another with the solution technology, she would want to know the relative payback.
        Some Payback analysis calls for discounting cashflows, others do not."""
        # Presented on the "Advanced Controls" tab:
        # "Payback Period Solution Relative to Conventional"

        #$K$122 on Operating Cost spreadsheet tab.

        if purchase_year is None:
            purchase_year = self.start_year - 3 # apply default
 
        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, discount_rate=0.0)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_series.cumsum()

        result: int =-1
        for idx, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = idx - self.base_year + 1
                break

        return result


    def get_payback_period_solution_vs_conventional_npv(self, purchase_year: Optional[int] = None) -> int:
        """Return the length of time taken to recover all investments costs (above and beyond the conventional technology costs) where cashflows ARE discounted.

        If a decision maker is comparing two projects, one with the conventional technology,and another with the solution technology, she would want to know the relative payback.
        Some Payback analysis calls for discounting cashflows, others do not."""
        # Presented on the "Advanced Controls" tab:
        # "Discounted Payback Period Solution Relative to Conventional"

        if purchase_year is None:
            purchase_year = self.start_year - 3 # apply default
        
        #$K$122 on Operating Cost spreadsheet tab.

        if purchase_year is None:
            purchase_year = self.start_year - 3 # apply default
 
        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, discount_rate=self.scenario.npv_discount_rate)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_series.cumsum()

        result:int =-1
        for idx, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = idx - self.base_year + 1
                break

        return result

    def get_abatement_cost(self) -> float:
        """ Return the discounted lifetime cost of the solution.

            This is calculated as PDS - REF, including First Costs and Operating Savings, but only for those years of the analysis,
            divided by the total emissions reduction during those years.
         """
        # Presented on the "Advanced Controls" tab:
        # "Average Abatement Cost Across Reporting Period"

        total_co2_sequestered = self.get_total_co2_sequestered()
        emissions_reduction_series = self.get_emissions_reduction_series()
        total_emissions_reduction = emissions_reduction_series.loc[self.start_year:self.end_year].sum() / 1000
        total_co2_reduction = total_emissions_reduction + total_co2_sequestered

        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_series()
        npv_summed = lifetime_cashflow_npv_series.loc[self.start_year:self.end_year].sum()
        
        result = -1 * npv_summed/total_co2_reduction
        return result / 1e9

    def get_net_profit_margin_series(self) -> pd.Series:
        """Return the time series of Net Profit Margin of all implementation units across the study period."""
        pds_solution_margin_series = self.pds_scenario.get_net_profit_margin(self.scenario.solution_expected_lifetime, self.scenario.solution_net_profit_margin)
        pds_solution_margin_series *= (1- self.scenario.disturbance_rate)
        ref_solution_margin_series = self.ref_scenario.get_net_profit_margin(self.scenario.solution_expected_lifetime, self.scenario.solution_net_profit_margin)
        ref_solution_margin_series *= (1- self.scenario.disturbance_rate)
        net_solution_margin_series = pds_solution_margin_series - ref_solution_margin_series

        pds_conventional_margin_series = self.pds_scenario.get_net_profit_margin(self.scenario.conventional_expected_lifetime, self.scenario.conventional_net_profit_margin)
        pds_conventional_margin_series *= (1- self.scenario.disturbance_rate)
        ref_conventional_margin_series = self.ref_scenario.get_net_profit_margin(self.scenario.conventional_expected_lifetime, self.scenario.conventional_net_profit_margin)
        ref_conventional_margin_series *= (1- self.scenario.disturbance_rate)
        net_conventional_margin_series = pds_conventional_margin_series - ref_conventional_margin_series

        net_margin_series = net_solution_margin_series - net_conventional_margin_series

        return net_margin_series

    def get_net_profit_margin(self) -> float:
        """Return the Net Profit Margin of all implementation units during the study period only (value at end minus value at start)."""
        # Presented on the "Detailed Results" tab:
        # "Net Profit Margin 2020-2050"

        net_profit_margin_series = self.get_net_profit_margin_series()
        margin_series_cum = net_profit_margin_series.cumsum()
        end_year_val = margin_series_cum.loc[self.end_year]
        start_year_val = margin_series_cum.loc[self.start_year]
        result = end_year_val - start_year_val
        
        return result / 1_000 # express in billions of USD

    def get_lifetime_profit_margin(self) -> float:
        """ Return the Net Profit Margin for the full lifetime (to 2139) of all implementation units in use during study period.
        
        Note that this may include units adopted prior to the start year, and may extend past the end year."""
        # Presented on the "Detailed Results" tab:
        # "Lifetime Profit Margin"

        net_profit_margin_series = self.get_net_profit_margin_series()
        result  = net_profit_margin_series.sum()

        return result / 1_000 # express in billions of USD


### Start Emissions Reduction Calculations ###

    def get_emissions_reduction_series(self) -> pd.Series:
        """Return the time series of reduced emissions.
        
        Annual CO2 reductions by region and year are calculated by adding reduced emissions derived from the electric grid,
        the replaced emissions derived from clean renewables, the net direct emissions derived from non-electric/non-fuel consumption,
        and the reduced emissions derived from fuel efficiency, and then subtracting the net indirect emissions.
        Most solutions will not use all of the defined factors.

        The emissions values used are from the regional future grid BAU CO2 emission intensity values (by year) from the AMPERE 3 MESSAGE Base model
        used in the IPCC 5th Assessment Report WG3.

        """
        # CO2-eq MMT Reduced
        # Used to calculate [CO2 Calcs]!$B64

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

        pds_units = self.pds_scenario.get_units_adopted()
        
        if self.has_tam:
            # find element-wise min of pds_units and tam:
            pds_units = pd.concat([pds_units, self._tam.get_tam_series()]).min(level=0)

        ref_units = self.ref_scenario.get_units_adopted()
        net_units = pds_units - ref_units

        if self.has_grid_emissions_factors:
            replaced_grid_emissions = net_units * self._grid_emissions_factors
            emissions_reduction_series += replaced_grid_emissions

        direct_co2_emissions_saved = net_units * (self.scenario.conventional_direct_emissions - self.scenario.solution_direct_emissions) / 1_000_000
        indirect_co2_emissions = net_units * (self.scenario.solution_indirect_emissions - self.scenario.conventional_indirect_emissions) / 1_000_000
        reduced_fuel_emissions = net_units * self.scenario.conventional_fuel_consumed * \
            (self.scenario.conventional_fuel_emissions_factor - self.scenario.solution_fuel_emissions_factor * (1-self.scenario.solution_fuel_efficiency_factor)) / 1_000_000

        emissions_reduction_series = emissions_reduction_series + direct_co2_emissions_saved - indirect_co2_emissions + reduced_fuel_emissions
        result = emissions_reduction_series.loc[self.start_year: self.end_year]
        return result

    def get_total_emissions_reduction(self):
        """Return the sum of all emissions reduced in the PDS Scenario versus the REF Scenario over the study period. (Gt CO2)"""
        ## Key Climate Result ###
        # Presented on the "Advanced Controls" tab:
        # "Total Emissions Reduction"
        total_emissions_reduction = self.get_emissions_reduction_series()
        result = total_emissions_reduction.sum()
        return result / 1000

    def get_max_annual_emissions_reduction(self) -> float:
        """Return the maximum reduction of all years in the reporting period"""
        # Presented on the "Advanced Controls" tab:
        # "Max Annual Emissions Reduction"
        total_emissions_reduction = self.get_emissions_reduction_series()
        result = total_emissions_reduction.max()
        return result / 1000

    def get_emissions_reduction_final_year(self):
        """Return the reduction in the final year"""
        # Presented on the "Advanced Controls" tab:
        # "Emissions Reduction in 2050"
        total_emissions_reduction = self.get_emissions_reduction_series()
        result = total_emissions_reduction.loc[self.end_year]
        return result / 1000


### End Emissions Reduction Calculations ###


### Start Carbon Sequestration Calculations ###

    def get_carbon_sequestration_series(self):
        """Return a time series of the sequestration amount for each year in the reporting period"""
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
        return net_sequestration

    def get_total_co2_sequestered(self) -> float:
        """The total CO2-eq sequestered in the PDS but not in the REF Scenario."""
        ## Key Climate Result ##
        # Presented on the "Advanced Controls" tab:
        # "Total Additional CO2-eq Sequestered"        
        carbon_sequestration_series = self.get_carbon_sequestration_series()
        result = carbon_sequestration_series.loc[self.start_year + 1: self.end_year].sum()
        return result / 1_000 # express in billions of USD

    def get_max_annual_co2_sequestered(self) -> float:
        """Return the highest rate of sequestration during the period of analysis."""
        # Presented on the "Advanced Controls" tab:
        # "Max Annual CO2 Sequestered"
        carbon_sequestration_series = self.get_carbon_sequestration_series()
        result = max(carbon_sequestration_series.loc[self.start_year: self.end_year])
        return result / 1_000
    
    def get_co2_sequestered_final_year(self) -> float:
        """Return CO2 Sequestered in the final year of the reporting period."""
        # Presented on the "Advanced Controls" tab:
        # "CO2 Sequestered in 2050"
        carbon_sequestration_series = self.get_carbon_sequestration_series()        
        result = carbon_sequestration_series.loc[self.end_year]
        return result / 1_000

### End Carbon Sequestration Calculations ###


### Start PPM Equivalent Calculations ###

    def get_change_in_ppm_equivalent_series(self) -> pd.Series:
        """ Return the time series of reduced PPM of CO2 equivalent for each year in the reporting period.

            Each yearly reduction in CO2 (in million metric ton - MMT) is modeled as a discrete avoided pulse.
            A Simplified atmospheric lifetime function for CO2 is taken from Myhrvald and Caldeira (2012) based on the Bern Carbon Cycle model.
            Atmospheric tons of CO2 are converted to parts per million CO2 based on the molar mass of CO2 and the moles of atmosphere.
            CO2-eq emissions are treated as CO2 for simplicity and due to the lack of detailed information on emissions of other GHGs.
            If these other GHGs are a significant part of overall reductions, this model may not be appropriate.
        """
        # This is the implementation of the "CO2 PPM CALCULATOR" in [CO2 Calcs]!A169

        # get_carbon_sequestration returns series used to build [CO2 Calcs]!$B$120
        # to match [CO2 Calcs]!$B$120 ("Carbon Sequestration Calculations"), need to combine pds and ref at the ocean_solution level.
        # If ref_scenario.get_carbon_sequestration(...) is zero, then this function returns [CO2 Calcs]!$B$120.
        carbon_sequestration_series = self.get_carbon_sequestration_series()
         
        # following this function call, total_emissions_reduction should correspond to 'CO2-eq MMT Reduced', [CO2 Calcs]!$B$64.
        total_emissions_reduction = self.get_emissions_reduction_series()

        reduction_plus_sequestration = total_emissions_reduction.add(carbon_sequestration_series, fill_value=0.0)

        start_year = reduction_plus_sequestration.index.min()
        result_years = list(range(start_year, self.end_year+1))
        results = pd.Series(index = result_years, dtype=float)
        results = results.fillna(0.0)
        # (0.217 + 0.259*EXP(-(A173-$A$173+1)/172.9) + 0.338*EXP(-(A173-$A$173+1)/18.51) + 0.186*EXP(-(A173-$A$173+1)/1.186))
        # (0.217 + 0.259*EXP(-(current_year-year_zero+1)/172.9) + 0.338*EXP(-(current_year-year_zero+1)/18.51) + 0.186*EXP(-(current_year-year_zero+1)/1.186))

        for iter_year in result_years:
            year_results = []
            exponent= 0

            # When comparing to the CO2 Calcs tab on the spreadsheet, the following loop runs down each column.
            for _ in range(iter_year, result_years[-1] +1):
                year_net_adoption = reduction_plus_sequestration.loc[iter_year]
                exponent += 1
                val =  0.217 + 0.259*np.exp(-(exponent)/172.9) 
                val += 0.338*np.exp(-(exponent)/18.51) 
                val += 0.186*np.exp(-(exponent)/1.186)
                year_results.append(year_net_adoption * val)

            year_results_series = pd.Series(index = range(iter_year, self.end_year+1), dtype=float)
            year_results_series = year_results_series.fillna(0.0)
            year_results_series = year_results_series.add(year_results)

            results = results.add(year_results_series, fill_value=0.0)

        factor = (1_000_000 * 10**6 ) / 44.01
        factor = factor / (1.8 * 10**20)
        factor = factor * 10**6
        results = results * factor
        return results

    def get_change_in_ppm_equivalent(self) -> float:
        """Return the CO2 atmospheric concentration change (in parts-per-million) estimated as a result of the PDS scenario compared to the REF scenario, in the final year of the reporting period only."""
        # Presented on the "Advanced Controls" tab:
        # "Approximate PPM Equivalent Change"
        change_in_ppm_equivalent_series = self.get_change_in_ppm_equivalent_series()
        result = change_in_ppm_equivalent_series.loc[self.end_year]
        return result

    def get_change_in_ppm_equivalent_final_year(self) -> float:
        """Return the CO2 atmospheric concentration change (in Parts-per-Million) estimated as a result of the PDS scenario compared to the REF scenario, in the final year minus the penultimate year."""
        # Presented on the "Advanced Controls" tab:
        # "Approximate PPM rate in 2050"
        change_in_ppm_equivalent_series = self.get_change_in_ppm_equivalent_series()
        result = change_in_ppm_equivalent_series.loc[self.end_year] - change_in_ppm_equivalent_series.loc[self.end_year-1]
        return result
        
### End PPM Equivalent Calculations ###


### Start Protection Results ###

    def get_reduced_area_degradation(self) -> float:
        """Return the expected reduction in land/ocean degradation (of solution land/ocean type) as a result of the adoption of the solution over study period."""
        # Presented on the "Advanced Controls" tab:
        # "Reduced Land Degradation from 2020-2050"
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

    def get_carbon_under_protection_final_year(self) -> float:
        """"Calculate the sum of the increase in adoption in the final year and the degraded area under protection for the solution in the final year.
            Return this sum multiplied by the carbon storage in the protected area type."""
        # Presented on the "Advanced Controls" tab:
        # "Total Carbon Under Protection by 2050"
        cumulative_degraded_area_under_protection_pds = self.pds_scenario.get_cumulative_degraded_area_under_protection(
            self.scenario.delay_impact_of_protection_by_one_year,
            self.scenario.disturbance_rate
            )
        degraded_area_under_protection_end_year = cumulative_degraded_area_under_protection_pds.loc[self.end_year]
        adoption_unit_increase_pds_final_year = self.get_adoption_unit_increase_pds_final_year()        
        result = adoption_unit_increase_pds_final_year + degraded_area_under_protection_end_year
        result *= self.scenario.carbon_storage_in_protected_area_type
        return result / 1_000
    
    def get_co2_under_protection_final_year(self) -> float:
        """Return the carbon under protection in the final year multiplied by the carbon-to-co2 ratio (3.664)."""
        # Presented on the "Advanced Controls" tab:
        # Total CO2 Under Protection by 2050
        carbon_to_co2_ratio = 3.664
        result = self.get_carbon_under_protection_final_year()
        result *= carbon_to_co2_ratio
        return result

### End Protection Results ###

    def key_results(self) -> dict:
        """Define key results for ocean scenarios."""
        return {'adoption_unit_increase': self.get_adoption_unit_increase_pds_vs_ref_final_year(),
                'marginal_first_cost': self.get_marginal_first_cost(),
                'net_operating_savings': self.get_operating_cost(),
                'lifetime_operating_savings': self.get_lifetime_operating_savings(),
                'cumulative_emissions_reduced': self.get_total_emissions_reduction(),
                'total_additional_co2eq_sequestered': self.get_total_co2_sequestered()}
