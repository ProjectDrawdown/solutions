
from dataclasses import dataclass, field
from model.new_scenario import NewScenario
    
@dataclass
class SeafloorProtectionScenario(NewScenario):

    # General Ocean Inputs
    emissions_reduced_per_unit_area : float  = field(default=0.0, metadata={'Units': 't CO2-eq/ha'})
    growth_rate_of_ocean_degradation : float = field(default=0.0, metadata={'Units': 'years'})
    sequestration_rate_all_ocean : float  = field(default=0.0, metadata={'Units': 't C/ha/year'})
    carbon_storage_in_protected_area_type : float = field(default=0.0, metadata={'Units': 't C/ha/year'})
    current_adoption_world : float = field(default=0.0, metadata={'Units': 'million hectares'})
    current_area_world : float = field(default=0.0, metadata={'Units': 'million hectares'})
    future_ref_area : float = field(default=0.0, metadata={'Units': 'million hectares'})
    future_pds_area : float = field(default=0.0, metadata={'Units': 'million hectares'})

    # Ref Adoption Scenario Inputs:
    ref_scenario_name : str = field(default='')
