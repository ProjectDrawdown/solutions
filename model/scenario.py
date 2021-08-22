"""Base class of all scenario objects"""

# Extended this class with some properties that should be common to scenarios from most of the solutions.
# OceanScenario subclasses this, adding extra properties.
from dataclasses import dataclass, field
import datetime

@dataclass
class Scenario:
    
    # Conventional Solution
    conv_first_cost : float = field(metadata={'Units':  'US$2014/ha'})
    conv_operating_cost :  float = field(metadata={'Units':  'US$2014/ha/year'})
    conv_net_profit_margin :  float = field(metadata={'Units':  'US$2014/ha/year'})
    conv_expected_lifetime :  float = field(metadata={'Units':  'years'})

    # pds Solution
    soln_first_cost : float = field(metadata={'Units':  'US$2014/ha'})
    soln_operating_cost :  float = field(metadata={'Units':  'US$2014/ha/year'})
    soln_net_profit_margin :  float = field(metadata={'Units':  'US$2014/ha/year'})
    soln_expected_lifetime :  float = field(metadata={'Units':  'years'})

    # General:
    npv_discount_rate :  float = field(metadata={'Units':  'percentage'})

    # General Emissions Inputs:
    use_co2_equiv : bool
    use_aggregate_co2_equiv : bool

    scenario_timestamp: datetime
    scenario_description: str

    # PDS Adoption Scenario Name, also acts as a key into the dictionary of pds scenarios (from custom_pds_adoption.json).
    pds_scenario_name : str
    disturbance_rate : float = field(default = 0.0, init= False) # Set init= False so that subclasses can have non-defaulted fields.
    