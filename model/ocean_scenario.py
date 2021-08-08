
from dataclasses import dataclass, field
import datetime
from model.scenario import Scenario
    
@dataclass
class OceanScenario(Scenario):

    sequestration_rate_all_ocean : float  = field(metadata={'Units': 't C/ha/year'})
    disturbance_rate : float = field(metadata={'Units': 'percentage lost annually'})

    # General Ocean Inputs
    new_growth_harvested_every : float = field(metadata={'Units': 'years'})
    allow_disturbance_to_increase_op_costs : bool

    # Current Adoption:
    adoption_value_world : float = field(metadata={'Units': 'Millions of Ha'})

    ## Following not defaulted - may be added after initialisation.

    scenario_timestamp: datetime
    scenario_description: str

    # PDS Adoption Scenario Inputs:
    pds_scenario_description : str

    # Fully Customized PDS:
    pds_scenario_name : str
    pds_custom_scenarios_included : str
    
    # Ref Adoption Scenario Inputs:
    ref_scenario_name : str
    ref_base_custom_adoption_on : str
    ref_adoption_use_only_regional_data : bool
