import os
import json

from model.ocean_solution import OceanSolution
from solution.seaweedfarming.seaweedfarming_scenario import SeaweedFarmingScenario

class SeaweedFarmingSolution(OceanSolution):
    """ All calculations for seaweed farming currently implemented in the OceanSolution base class.
    """

    # Initialize from configuration file:
    def __init__(self, configuration_file_name = None):
        """
            Class constructor requires a configuration file named './seaweedfarming_solution_config.yaml'.
            This should be located in the same directory as the 'seaweedfarming_solution.py' module

        """

        if configuration_file_name is None:
            filename = os.path.basename(__file__)
            filename = filename.split('.')[0]
            configuration_file_name = os.path.join(os.path.dirname(__file__), filename + '_config.yaml')
        
        if not os.path.isfile(configuration_file_name):
            raise ValueError(f'Unable to find configuration file {configuration_file_name}.')
        
        super()._load_config_file(configuration_file_name)

    def load_scenario(self, scenario_name):

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        scenario = SeaweedFarmingScenario(**scen_dict[scenario_name])

        self.scenario = scenario

        super()._load_pds_scenario()
        
        self.set_tam()

        if self.scenario.ref_scenario_name:
            super()._load_ref_scenario()
        else:
            # creates a ref scenario with zeroes.
            super().ref_scenario = self.pds_scenario.get_skeleton()

        # Set scenario-specific data:
        
        self.disturbance_rate = self.scenario.disturbance_rate
        self.sequestration_rate_all_ocean = self.scenario.sequestration_rate_all_ocean
        self.npv_discount_rate = self.scenario.npv_discount_rate
    
    def set_tam(self):
        self.pds_scenario.set_tam_linear(total_area = self.total_area,
                        change_per_period = 0.0) # This should produce a flat line with y = constant = self.total_area
        return
