import os

from model.ocean_solution import OceanSolution

class SeaweedFarmingSolution(OceanSolution):

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