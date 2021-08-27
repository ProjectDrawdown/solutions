
from dataclasses import dataclass, field
from model.new_scenario import NewScenario
    
@dataclass
class SeafloorProtectionScenario(NewScenario):

    # Current Adoption:
    adoption_value_world : float = field(metadata={'Units': 'Millions of Ha'})

    # General Ocean Inputs
    emissions_reduced_per_land_unit : float  = field(metadata={'Units': 't CO2-eq/ha'})
    growth_rate_of_ocean_degradation : float = field(metadata={'Units': 'years'})
    sequestration_rate_all_ocean : float  = field(metadata={'Units': 't C/ha/year'})
    
    ## Following not defaulted - may be added after initialisation.

    # Ref Adoption Scenario Inputs:
    ref_scenario_name : str    
    ref_adoption_use_only_regional_data : bool

