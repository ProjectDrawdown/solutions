
import os
import sys
from math import floor, ceil
from unittest import result
import pandas as pd
import numpy as np
import json
import yaml

from model.ocean_scenario import OceanScenario
from model.new_unit_adoption import NewUnitAdoption as UnitAdoption
from model.ocean_tam import OceanTam
from model.solution import Solution

class OceanSolution(Solution):
    """ This is the base class that each Ocean solution should inherit from.
    Contains all the calculations required for Ocean-based scenario results.
    """

    _config : dict
    scenario : OceanScenario
    _tam : OceanTam
    has_tam: bool
    has_grid_emissions_factors: bool

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
    def __init__(self, configuration_file_name):
        print('ocean_solution initializing...')
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

        print(f'Loading scenario {scenario_name}')

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        #print(scen_dict[scenario_name])

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
        
        area_units_series = self.pds_scenario.get_area_units()
        area_units_base_year = area_units_series.loc[self.base_year+1]

        result  = adoption_base_year / area_units_base_year
        return result


    def get_percent_adoption_start_year(self) -> np.float64:

        pds_series = self.pds_scenario.get_units_adopted()
        pds_start_year = pds_series.loc[self.start_year]

        if self.has_tam:
            area_units_series = self._tam.get_tam_series()
        else:
            area_units_series = self.pds_scenario.get_area_units()

        area_units_start_year = area_units_series.loc[self.start_year]

        result = pds_start_year / area_units_start_year
        return result
    

    def get_percent_adoption_end_year(self) -> np.float64:
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

    def get_marginal_first_cost(self) -> np.float64:

        annual_world_first_cost_series = self.get_annual_world_first_cost_series()
        
        result = -1 * annual_world_first_cost_series.sum() / 1e9

        return result  # in billions

    
    def get_cumulative_first_cost_solution(self) -> np.float64:

        years = list(range(self.base_year, self.end_year +1))

        pds_fc = self.pds_scenario.get_annual_world_first_cost(self.scenario.solution_expected_lifetime, self.scenario.solution_first_cost)

        result = pds_fc.loc[years]

        result = result * self.scenario.unit_converting_factor

        return result.sum() / 1e9  # in billions


    
    def get_operating_cost_series(self) -> pd.Series:

        # TODO: confirm start_year-1 is desired. Why does it start in 2019?

        pds_solution_series = self.pds_scenario.get_operating_cost(
                self.scenario.solution_expected_lifetime,
                self.scenario.solution_operating_cost
                ) * (1+ self.scenario.disturbance_rate)

        #pds_result = pds_series.cumsum().loc[self.end_year] - pds_series.cumsum().loc[self.start_year]

        # Each cell in ref_series should match SUM($C403:$AV403) in [Operating Cost] worksheet.
        ref_solution_series = self.ref_scenario.get_operating_cost(
                self.scenario.solution_expected_lifetime,
                self.scenario.solution_operating_cost
                ) * (1+self.scenario.disturbance_rate)

        # Each cell in net_solution_series should match SUM($C266:$AV266) in [Operating Cost] worksheet.
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

    def get_operating_cost(self) -> np.float64:
        operating_cost_series = self.get_operating_cost_series()
        cumulative = operating_cost_series.cumsum()
        result = cumulative.loc[self.end_year] - cumulative.loc[self.start_year]
        result = result / 1e9 # in billions
        return result

    
    def get_lifetime_operating_savings(self) -> np.float64:
        operating_cost_series = self.get_operating_cost_series()
        result = operating_cost_series.sum()
        result = result / 1e9 # in billions
        return result


    def get_first_cost_conventional_series(self) -> pd.Series:
        conventional_pds_install_cost_per_unit = self.pds_scenario.get_install_cost_per_land_unit(self.scenario.conventional_first_cost)
        conventional_ref_install_cost_per_unit = self.ref_scenario.get_install_cost_per_land_unit(self.scenario.conventional_first_cost)

        conventional_install_cost_per_unit = conventional_pds_install_cost_per_unit - conventional_ref_install_cost_per_unit
        return conventional_install_cost_per_unit


    def get_lifetime_cashflow_npv_single_series(self, purchase_year, discount_rate, solution_only = False) -> pd.Series:

        discount_factor = 1/(1+discount_rate)
        
        # "result" should match time series in [Operating Cost]!$J$125 = "NPV of Single Cashflows (to 2014)"
        years_old_at_start =  purchase_year - self.base_year + 1

        if solution_only:
            first_val = -1 * self.scenario.solution_first_cost
        else:
            first_val = self.scenario.conventional_first_cost - self.scenario.solution_first_cost

        first_val = first_val * discount_factor**(years_old_at_start)

        results = []
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

    def get_lifetime_cashflow_npv_single(self, purchase_year = None) -> np.float64:

        if purchase_year is None:
            purchase_year = self.start_year -3 # apply default

        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, self.scenario.npv_discount_rate)
        result_sum = lifetime_cashflow_npv_series.sum()
        
        return result_sum / 1e9 # in Billions USD


    def get_lifetime_cashflow_npv_series(self) -> pd.Series:
        
        annual_world_first_cost_series = self.get_annual_world_first_cost_series()

        operating_cost_series = self.get_operating_cost_series()

        net_cash_flow = operating_cost_series.add(annual_world_first_cost_series, fill_value=0.0)

        rate = self.scenario.npv_discount_rate
        discount_factor = 1/(1+rate)

        num_rows = net_cash_flow.shape[0]

        discount_factors = [discount_factor**row for row in range(num_rows)]

        npv = net_cash_flow.multiply(discount_factors, axis='index')

        return npv

    def get_lifetime_cashflow_npv_all(self) -> np.float64:
        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_series()
        result_sum = lifetime_cashflow_npv_series.sum()
        return result_sum / 1e9


    def get_payback_period_solution_only(self, purchase_year = None) -> np.float64:

        if purchase_year is None:
            purchase_year = self.start_year-3 # Apply default

        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, discount_rate=0.0, solution_only=True)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_series.cumsum()

        result=-1
        for idx, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = idx - self.base_year + 1
                break

        return result


    def get_payback_period_solution_only_npv(self, purchase_year = None) -> np.float64:
        
        if purchase_year is None:
            purchase_year = self.start_year-3 # Apply default

        lifetime_cashflow_npv_single_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, self.scenario.npv_discount_rate, solution_only=True)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_single_series.cumsum()

        result=-1
        for idx, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = idx - self.base_year + 1
                break

        return result


    def get_payback_period_solution_vs_conventional(self, purchase_year = None) -> np.float64:

        #$K$122 on Operating Cost spreadsheet tab.

        if purchase_year is None:
            purchase_year = self.start_year - 3 # apply default
 
        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, discount_rate=0.0)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_series.cumsum()

        result=-1
        for idx, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = idx - self.base_year + 1
                break

        return result


    def get_payback_period_solution_vs_conventional_npv(self, purchase_year = None) -> np.float64:

        if purchase_year is None:
            purchase_year = self.start_year - 3 # apply default
        
        #$K$122 on Operating Cost spreadsheet tab.

        if purchase_year is None:
            purchase_year = self.start_year - 3 # apply default
 
        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_single_series(purchase_year, discount_rate=self.scenario.npv_discount_rate)
        cumulative_lifetime_cashflow_npv_series = lifetime_cashflow_npv_series.cumsum()

        result=-1
        for idx, val in cumulative_lifetime_cashflow_npv_series.items():
            if val>0.0:
                result = idx - self.base_year + 1
                break

        return result

    def get_abatement_cost(self) -> np.float64:

        total_co2_sequestered = self.get_total_co2_sequestered()
        emissions_reduction_series = self.get_emissions_reduction_series()
        total_emissions_reduction = emissions_reduction_series.loc[self.start_year:self.end_year].sum() / 1000
        total_co2_reduction = total_emissions_reduction + total_co2_sequestered

        lifetime_cashflow_npv_series = self.get_lifetime_cashflow_npv_series()
        npv_summed = lifetime_cashflow_npv_series.loc[self.start_year:self.end_year].sum()
        
        result = -1 * npv_summed/total_co2_reduction
        return result / 1e9

    def get_net_profit_margin_series(self) -> pd.Series:

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


    def get_net_profit_margin(self) -> np.float64:
        net_profit_margin_series = self.get_net_profit_margin_series()

        margin_series_cum = net_profit_margin_series.cumsum()

        end_year_val = margin_series_cum.loc[self.end_year]
        start_year_val = margin_series_cum.loc[self.start_year]

        result = end_year_val - start_year_val
        
        return result / 1_000 # express in billions of USD


    def get_lifetime_profit_margin(self) -> np.float64:

        net_profit_margin_series = self.get_net_profit_margin_series()
        result  = net_profit_margin_series.sum()

        return result / 1_000 # express in billions of USD


### Start Emissions Reduction Calculations ###

    def get_emissions_reduction_series(self) -> pd.Series:

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

        return net_sequestration

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


    def get_change_in_ppm_equivalent_series(self) -> pd.Series:

        """
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
        results = pd.Series(index = result_years, dtype=np.float64)
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

            year_results_series = pd.Series(index = range(iter_year, self.end_year+1), dtype=np.float64)
            year_results_series = year_results_series.fillna(0.0)
            year_results_series = year_results_series.add(year_results)

            results = results.add(year_results_series, fill_value=0.0)

        factor = (1_000_000 * 10**6 ) / 44.01
        factor = factor / (1.8 * 10**20)
        factor = factor * 10**6
        results = results * factor
        return results

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

    def key_results(self) -> dict:
        """Define key results for ocean scenarios."""
        return {'adoption_unit_increase': self.get_adoption_unit_increase_pds_vs_ref_final_year(),
                'marginal_first_cost': self.get_marginal_first_cost(),
                'net_operating_savings': self.get_operating_cost(),  # TODO
                'lifetime_operating_savings': self.get_lifetime_operating_savings(),
                'cumulative_emissions_reduced': self.get_total_emissions_reduction(),
                'total_additional_co2eq_sequestered': self.get_total_co2_seq()}
