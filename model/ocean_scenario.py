
from dataclasses import dataclass, field

from importlib_metadata import metadata
from model.new_scenario import NewScenario
    
@dataclass
class OceanScenario(NewScenario):

    conventional_first_cost: float=field(default=0.0, metadata={'Units': 'US$2014/ha', 'Description': 'Set-up cost of the conventional technology.'}),
    conventional_operating_cost: float=field(default=0.0, metadata={'Units': 'US$2014/ha/year', 'Description': 'Operating cost of the conventional technology.'}),
    conventional_net_profit_margin: float=field(default=0.0, metadata={'Units': 'US$2014/ha/year', 'Description': 'Net profit margin of the conventional technology.'}),
    conventional_expected_lifetime: float=field(default=0.0, metadata={'Units': 'years', 'Description': 'Expected lifetime of one unit of conventional technology.'}),
    
    solution_first_cost: float=field(default=0.0, metadata={'Units': 'US$2014/ha', 'Description': 'Set-up cost of the solution\'s technology.'}),
    solution_operating_cost: float=field(default=0.0, metadata={'Units': 'US$2014/ha/year', 'Description': 'Operating cost of the solution\'s technology.'}),
    solution_net_profit_margin: float=field(default=0.0, metadata={'Units': 'US$2014/ha/year', 'Description': 'Net profit margin of the solution\'s technology.'}),
    solution_expected_lifetime: float=field(default=0.0, metadata={'Units': 'years', 'Description': 'Expected lifetime of one unit of the solution\'s technology.'}),

    npv_discount_rate: float=field(default=0.0, metadata={'Units': 'US$2014/ha', 'Description': 'Discount rate applied to capture cost of financing.'}),

    # General Ocean Inputs
    allow_disturbance_to_increase_op_costs : bool = field(default = True)
    carbon_storage_in_protected_area_type : float = field(default=0.0, metadata={'Units': 't C/ha/year'})
    current_adoption_world : float = field(default=0.0, metadata={'Units': 'million hectares'})
    
    disturbance_rate : float = field(default=0.0, metadata={'Units': 'percentage lost annually'})
    emissions_reduced_per_unit_area : float  = field(default=0.0, metadata={'Units': 't CO2-eq/ha'})
    future_ref_area : float = field(default=0.0, metadata={'Units': 'million hectares'})
    future_pds_area : float = field(default=0.0, metadata={'Units': 'million hectares'})
    growth_rate_of_ocean_degradation : float = field(default=0.0, metadata={'Units': 'years'})
    sequestration_rate_all_ocean : float  = field(default=0.0, metadata={'Units': 't C/ha/year'})

    # Current Adoption:
    adoption_value_world : float = field(default=0.0, metadata={'Units': 'Millions of Ha'})

    # Ref Adoption Scenario Inputs:
    ref_scenario_name : str = field(default='')

    current_area_world: float = field(default=0.0, metadata={'Units': 'Millions of Ha', 'Description': 'The total land area or total ocean area covered by the solution.'})
    total_area_as_of_period: int = field(default= 2018, metadata={'Description': 'The year that the total area number applies to.'})
    change_per_period: float = field(default = 0.0, metadata={'Description': 'How the total area changes each year.'})

    delay_impact_of_protection_by_one_year: bool = field(default=True, metadata={'Description': 'Newly implemented policies take approximately one year to have an effect.'})
    delay_regrowth_of_degraded_land_by_one_year: bool = field(default=True, metadata={'Description': 'Regrowth takes approximately one year to have an effect.'})
    use_aggregate_CO2_equivalent_instead_of_individual_GHG: bool = field(default=True, metadata={'Description': 'Set to False to break down GHG emissions into CH4, N2O etc.'})
    use_adoption_for_carbon_sequestration_calculation: bool = field(default=False, metadata={'Description': 'Set to True to use a reference adoption scenario. Set to False to use total area.'})

    direct_emissions_are_annual: bool = field(default=True, metadata={'Description': 'Set to False for a one-time effect, set to True to repeat emssion each year.'})
