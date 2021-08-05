
from dataclasses import dataclass, field
from dateutil import parser
import datetime

@dataclass
class AdoptionData:

    _first_cost : float = field(metadata={'Units':  'US$2014/ha'})
    _operating_cost :  float = field(metadata={'Units':  'US$2014/ha/year'})
    _net_profit_margin :  float = field(metadata={'Units':  'US$2014/ha/year'})
    _expected_lifetime :  float = field(metadata={'Units':  'years'})
    
@dataclass
class ScenarioData:

    # General:
    npv_discount_rate :  float = field(metadata={'Units':  'percentage'})

    # General Emissions Inputs:
    use_co2_equiv : bool
    use_aggregate_co2_equiv : bool
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

class Scenario:

    def __init__(self, SolutionData, ConventionalData, ScenarioData):
        self.SolutionData = SolutionData
        self.ConventionalData = ConventionalData
        self.ScenarioData = ScenarioData

    @classmethod
    def from_dict(cls, scenario_dict):
        
        soln_dict = {}
        conv_dict = {}

        remove_keys = []

        for k,v in scenario_dict.items():
            if k.startswith('soln_'):
                soln_dict['_' + k[5:]] = v
                remove_keys.append(k)
            elif k.startswith('conv_'):
                conv_dict['_' + k[5:]] = v
                remove_keys.append(k)
        
        for k in remove_keys:
            del scenario_dict[k]

        timestamp = parser.parse(scenario_dict['scenario_timestamp'])
        scenario_dict['scenario_timestamp'] = timestamp

        scen_data = ScenarioData(**scenario_dict)

        soln_data = AdoptionData(**soln_dict)
        conv_data = AdoptionData(**conv_dict)

        return cls( soln_data, conv_data, scen_data)

