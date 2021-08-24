
from dataclasses import dataclass, field
from model.new_scenario import Scenario
    
@dataclass
class OceanScenario(NewScenario):

    sequestration_rate_all_ocean : float  = field(metadata={'Units': 't C/ha/year'})
    disturbance_rate : float = field(metadata={'Units': 'percentage lost annually'})

    # General Ocean Inputs
    new_growth_harvested_every : float = field(metadata={'Units': 'years'})
    allow_disturbance_to_increase_op_costs : bool

    # Current Adoption:
    adoption_value_world : float = field(metadata={'Units': 'Millions of Ha'})

    ## Following not defaulted - may be added after initialisation.

    # Ref Adoption Scenario Inputs:
    ref_scenario_name : str
    ref_base_custom_adoption_on : str
    ref_adoption_use_only_regional_data : bool

    disturbance_rate : float = field(default=0.0)
