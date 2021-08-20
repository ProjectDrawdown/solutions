
import os
import json
import pandas as pd
import numpy as np

from model.ocean_solution import OceanSolution
from model.ocean_unit_adoption import UnitAdoption
from solution.macroalgaeprotection.macroalgaeprotection_scenario import MacroalgaeProtectionScenario

class MacroalgaeProtectionSolution(OceanSolution):
    """ All calculations for Macroalgae protection currently implemented in the OceanSolution base class.
    """

    # Initialize from configuration file:
    def __init__(self, configuration_file_name = None):
        """
            Constructor requires a configuration file named 'macroalgaeprotection_solution_config.yaml'.
            This should be located in the same directory as the 'macroalgaeprotection_solution.py' module

        """

        if configuration_file_name is None:
            filename = os.path.basename(__file__)
            filename = filename.split('.')[0]
            configuration_file_name = os.path.join(os.path.dirname(__file__), filename + '_config.yaml')
        
        if not os.path.isfile(configuration_file_name):
            raise ValueError(f'Unable to find configuration file {configuration_file_name}.')

        super().__init__(configuration_file_name)
        
        # Now set macroalgaeprotection-specific config values:
        self.total_area = self._config['TotalArea']
        self.total_area_as_of_period = self._config['TotalAreaAsOfPeriod']
        self.change_per_period = self._config['ChangePerPeriod']

        # Delay Regrowth of Degraded Land by 1 Year?
        self.delay_regrowth_by_one_year = True

    def set_up_tam(self, unit_adoption: UnitAdoption) -> None:
        # This should produce a flat line with y = constant = self.total_area
        unit_adoption.set_tam_linear(total_area= self.total_area, change_per_period= self.change_per_period, total_area_as_of_period= self.total_area_as_of_period)
        unit_adoption.apply_clip(lower= None, upper= self.total_area)
        unit_adoption.apply_linear_regression()
        unit_adoption.tam_build_cumulative_unprotected_area(self.new_growth_harvested_every)


    def load_scenario(self, scenario_name: str) -> None:

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        scenario = MacroalgaeProtectionScenario(**scen_dict[scenario_name])

        self.scenario = scenario

        super()._load_pds_scenario()
        
        if self.scenario.ref_scenario_name:
            self._load_ref_scenario()
        else:
            # creates a ref scenario with zeroes.
            self.ref_scenario = self.pds_scenario.get_skeleton()

        self.pds_scenario.use_tam_for_co2_calcs = True
        self.ref_scenario.use_tam_for_co2_calcs = True

        # Set scenario-specific data:        
        self.sequestration_rate_all_ocean = self.scenario.sequestration_rate_all_ocean
        self.npv_discount_rate = self.scenario.npv_discount_rate
        self.new_growth_harvested_every = self.scenario.new_growth_harvested_every
        self.disturbance_rate = 0.0

        # PDS and REF have a similar TAM structure:
        self.set_up_tam(self.pds_scenario)
        self.set_up_tam(self.ref_scenario)
        
        return


    def get_total_co2_seq(self) -> np.float64:

        # reduction degraded area = (total at risk area pds) - (total at risk area ref)
        
        tara_pds = self.pds_scenario.total_at_risk_area
        tara_ref = self.ref_scenario.total_at_risk_area

        tara = tara_pds - tara_ref

        co2_sequestered = tara * 3.666 * self.sequestration_rate_all_ocean

        start = self.start_year
        end = self.end_year

        if self.delay_regrowth_by_one_year:
            start -= 1
            end -= 1

        result = co2_sequestered.loc[start: end].sum()
        return result / 1000


    def get_change_in_ppm_equiv(self, delay_period = 0) -> np.float64:
        
        pds_sequestration = self.pds_scenario.get_change_in_ppm_equiv_series()
        ref_sequestration = self.ref_scenario.get_change_in_ppm_equiv_series()

        net_sequestration = (pds_sequestration - ref_sequestration)
        # net_sequestration should now equal 'CO2-eq PPM Calculator' on tab [CO2 Calcs]!$B$224

        end = self.end_year
        if delay_period > 0:
            end -= delay_period
        result = net_sequestration.loc[end]

        return result


    def get_change_in_ppm_equiv_final_year(self, delay_period = 0) -> np.float64:
                
        pds_sequestration = self.pds_scenario.get_change_in_ppm_equiv_series()
        ref_sequestration = self.ref_scenario.get_change_in_ppm_equiv_series()

        # net_sequestration should equal 'CO2-eq PPM Calculator' on tab [CO2 Calcs]!$B$224
        net_sequestration = (pds_sequestration - ref_sequestration)

        end = self.end_year
        if delay_period > 0:
            end -= delay_period
        
        result = net_sequestration.loc[end] - net_sequestration.loc[end-1]

        return result
        