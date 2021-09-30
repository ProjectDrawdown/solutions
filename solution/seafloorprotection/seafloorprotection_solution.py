
from os import path
from typing import Optional

from model.ocean_solution import OceanSolution
from model.new_unit_adoption import NewUnitAdoption


class SeafloorProtectionSolution(OceanSolution):
    """ All calculations for Seafloor Protection currently implemented in the OceanSolution base class.
    """

    # Initialize from configuration file:
    def __init__(self, configuration_file_name:Optional[str] = None):
        """
            Constructor requires a configuration file named 'seafloorprotection_solution_config.yaml'.
            This should be located in the same directory as the 'seafloorprotection_solution.py' module

        """

        if configuration_file_name is None:
            filename = path.basename(__file__)
            filename = filename.split('.')[0]
            configuration_file_name = path.join(path.dirname(__file__), filename + '_config.yaml')
        
        if not path.isfile(configuration_file_name):
            raise ValueError(f'Unable to find configuration file {configuration_file_name}.')

        super().__init__(configuration_file_name)
        
