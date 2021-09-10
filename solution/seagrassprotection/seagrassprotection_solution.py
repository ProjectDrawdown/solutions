
import os
import json

from model.ocean_solution import OceanSolution
from model.new_unit_adoption import NewUnitAdoption
from solution.seagrassprotection.seagrassprotection_scenario import SeagrassProtectionScenario

class SeagrassProtectionSolution(OceanSolution):
    """ All calculations for Seagrass Protection currently implemented in the OceanSolution base class.
    """

    # Initialize from configuration file:
    def __init__(self, configuration_file_name = None):
        """
            Constructor requires a configuration file named 'seagrassprotection_solution_config.yaml'.
            This should be located in the same directory as the 'seagrassprotection_solution.py' module

        """

        if configuration_file_name is None:
            filename = os.path.basename(__file__)
            filename = filename.split('.')[0]
            configuration_file_name = os.path.join(os.path.dirname(__file__), filename + '_config.yaml')
        
        if not os.path.isfile(configuration_file_name):
            raise ValueError(f'Unable to find configuration file {configuration_file_name}.')

        super().__init__(configuration_file_name)
        
        # Now set macroalgaeRestoration-specific config values:
        self.total_area = self._config['TotalArea']
        self.total_area_as_of_period = self._config['TotalAreaAsOfPeriod']
        self.change_per_period = self._config['ChangePerPeriod']
        
        self.delay_impact_of_protection_by_one_year= self._config['DelayImpactOfProtectionByOneYear']
        self.delay_regrowth_of_degraded_land_by_one_year= self._config['DelayRegrowthOfDegradedLandByOneYear']


    def set_up_area_units(self, unit_adoption: NewUnitAdoption) -> None:
        # This should produce a flat line with y = constant = self.total_area
        unit_adoption.set_area_units_linear(total_area= self.total_area, change_per_period= self.change_per_period, total_area_as_of_period= self.total_area_as_of_period)
        unit_adoption.apply_clip(lower= None, upper= self.total_area)
        unit_adoption.apply_linear_regression()


    def load_scenario(self, scenario_name: str) -> None:

        print(f'Loading scenario {scenario_name}')

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        scenario = SeagrassProtectionScenario(**scen_dict[scenario_name])

        self.scenario = scenario

        super()._load_pds_scenario()
        
        if self.scenario.ref_scenario_name:
            self._load_ref_scenario()
        else:
            # creates a ref scenario with zeroes.
            self.ref_scenario = self.pds_scenario.get_skeleton()

        self.pds_scenario.use_area_units_for_co2_calcs = False
        self.ref_scenario.use_area_units_for_co2_calcs = False

        # Set scenario-specific data:        
        self.sequestration_rate_all_ocean = self.scenario.sequestration_rate_all_ocean
        self.npv_discount_rate = self.scenario.npv_discount_rate
        self.growth_rate_of_ocean_degradation = self.scenario.growth_rate_of_ocean_degradation
        self.disturbance_rate = 0.0
        self.carbon_storage_in_protected_area_type = self.scenario.carbon_storage_in_protected_area_type

        # PDS and REF have a similar area_units structure. For MARS area_units is flat ocean area:
        self.set_up_area_units(self.pds_scenario)
        self.set_up_area_units(self.ref_scenario)
        
        return
