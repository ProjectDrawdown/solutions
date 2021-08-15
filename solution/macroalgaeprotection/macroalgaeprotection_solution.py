
import os
import json

from model.ocean_solution import OceanSolution
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
        
        OceanSolution._load_config_file(self, configuration_file_name)
        self.total_area_as_of_period = self.config['TotalAreaAsOfPeriod']
        self.change_per_period = self.config['ChangePerPeriod']
        

    def load_scenario(self, scenario_name):

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

        # Set scenario-specific data:
        
        self.sequestration_rate_all_ocean = self.scenario.sequestration_rate_all_ocean
        self.npv_discount_rate = self.scenario.npv_discount_rate
        self.disturbance_rate = 0.0

    
    def set_tam(self):
        self.set_tam_linear(total_area = self.total_area, 
            change_per_period = self.change_per_period, total_area_as_of_period = self.total_area_as_of_period, region = None)
        return
