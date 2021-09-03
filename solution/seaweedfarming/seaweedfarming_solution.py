from model.new_unit_adoption import NewUnitAdoption
import os
import json
import numpy as np

from model.ocean_solution import OceanSolution
from solution.seaweedfarming.seaweedfarming_scenario import SeaweedFarmingScenario

class SeaweedFarmingSolution(OceanSolution):
    """ All calculations for seaweed farming currently implemented in the OceanSolution base class.
    """

    # Initialize from configuration file:
    def __init__(self, configuration_file_name = None):
        """
            Configuration file name defaults to './seaweedfarming_solution_config.yaml'.
            This should be located in the same directory as the 'seaweedfarming_solution.py' module

        """

        if configuration_file_name is None:
            filename = os.path.basename(__file__)
            filename = filename.split('.')[0]
            configuration_file_name = os.path.join(os.path.dirname(__file__), filename + '_config.yaml')
        
        if not os.path.isfile(configuration_file_name):
            raise ValueError(f'Unable to find configuration file {configuration_file_name}.')

        super().__init__(configuration_file_name)

        # Now set seaweed_farming-specific config values:
        self.total_area = self._config['TotalArea']


    def load_scenario(self, scenario_name) -> None:

        print('Loading scenario file from ', os.getcwd(), self.scenarios_file)

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        scenario = SeaweedFarmingScenario(**scen_dict[scenario_name])

        self.scenario = scenario

        super()._load_pds_scenario()

        if self.scenario.ref_scenario_name:
            super()._load_ref_scenario()
        else:
            # creates a ref scenario with zeroes.
            super().ref_scenario = self.pds_scenario.get_skeleton()

        # Set scenario-specific data:
        
        self.disturbance_rate = self.scenario.disturbance_rate
        self.sequestration_rate_all_ocean = self.scenario.sequestration_rate_all_ocean
        self.npv_discount_rate = self.scenario.npv_discount_rate
        self.growth_rate_of_ocean_degradation = self.scenario.__dict__.get('growth_rate_of_ocean_degradation', 0.0)
        self.delay_impact_of_protection_by_one_year = self.scenario.__dict__.get('delay_impact_of_protection_by_one_year', False)
        self.delay_regrowth_of_degraded_land_by_one_year = self.scenario.__dict__.get('delay_regrowth_of_degraded_land_by_one_year', False)

        # PDS and REF have a similar area_units structure:
        self.set_up_area_units(self.pds_scenario)
        self.set_up_area_units(self.ref_scenario)
    

    def set_up_area_units(self, unit_adoption: NewUnitAdoption) -> None:
        unit_adoption.set_area_units_linear(total_area = self.total_area, change_per_period = 0.0) # This should produce a flat line with y = constant = self.total_area
        unit_adoption.apply_clip(lower=None, upper=self.total_area)
        return
