"""Implements the Advanced Controls, settings which have a default
   but can be overridden to fit particular needs.
"""

import enum
import pandas as pd
from model import emissionsfactors as ef
from model import helpertables as ht
from model import interpolation


SOLUTION_CATEGORY = enum.Enum('SOLUTION_CATEGORY', 'REPLACEMENT REDUCTION NOT_APPLICABLE LAND')
translate_adoption_bases = { "DEFAULT Linear": "Linear", "DEFAULT S-Curve": "S-Curve" }
valid_adoption_bases = {'Linear', 'S-Curve', 'Existing Adoption Prognostications',
    'Customized S-Curve Adoption', 'Fully Customized PDS', None}
valid_adoption_growth = {'High', 'Medium', 'Low', None}

class AdvancedControls:
  """Advanced Controls module, with settings impacting other modules.
  pds_2014_cost: US$2014 cost to acquire + install, per implementation
     unit (ex: kW for energy scenarios), for the Project Drawdown
     Solution (PDS).  SolarPVUtil "Advanced Controls"!B128
  ref_2014_cost: US$2014 cost to acquire + install, per implementation
     unit, for the reference technology.
     SolarPVUtil "Advanced Controls"!B128 (same as PDS)
  conv_2014_cost: US$2014 cost to acquire + install, per implementation
     unit, for the conventional technology.
     SolarPVUtil "Advanced Controls"!B95
  soln_first_cost_efficiency_rate: rate that the modelled solution improves /
     lowers in cost per year. In calculations this is usually converted
     to the learning rate, which is 1/efficiency_rate.
     SolarPVUtil "Advanced Controls"!C128
  conv_first_cost_efficiency_rate: rate that the conventional technology
     improves / lowers in cost each year. Efficiency rates for the
     conventional technology are typically close to zero, these technologies
     have already had many years of development and maturation.
     In calculations this is usually converted to the learning rate,
     which is 1/efficiency_rate.  SolarPVUtil "Advanced Controls"!C95
  soln_first_cost_below_conv (boolean): The solution first cost may decline
     below that of the Conventional due to the learning rate chosen. This may
     be acceptable in some cases for instance when the projections in the
     literature indicate so. In other cases, it may not be likely for the
     Solution to become cheaper than the Conventional.
     SolarPVUtil "Advanced Controls"!C132
  soln_energy_efficiency_factor (float): Units of energy reduced per year per
     functional unit installed.

     FOR CLEAN RENEWABLE ENERGY SOLUTIONS: enter 0 (e.g. implementing solar PV
     fully replaces existing fossil fuel-based generation, but does not reduce
     the amount of energy generated)

     FOR ENERGY EFFICIENCY SOLUTIONS: enter positive number representing total
     energy reduced, 0 < X < 1 (e.g. HVAC efficiencies reduce the average annual
     energy consumption of buildings, by square meters of floor space; they still
     use the electric grid, but significantly less)

     FOR SOLUTIONS THAT CONSUME MORE ENERGY THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:
     Use the next input, Total Annual Energy Used SOLUTION (e.g. electric vehicles
     use energy from the electric grid, whereas conventional vehicles use only fuel)
     SolarPVUtil "Advanced Controls"!C159
  conv_annual_energy_used (float): for solutions that reduce electricity
     consumption per functional unit, enter the average electricity used per
     functional unit of the conventional technologies/practices.
     SolarPVUtil "Advanced Controls"!B159
  soln_annual_energy_used (float): This refers to the units of average energy
     used per year per functional unit installed.

     This is an optional variable to be used in cases where a) the literature
     reports the energy use of the solution rather than energy efficiency; or
     b) the solution uses more electricity than the conventional
     technologies/practices.

     E.g. electric vehicles use energy from the electric grid, whereas
     conventional vehicles use only fuel)
     SolarPVUtil "Advanced Controls"!D159

  conv_fuel_consumed_per_funit (float): This refers to the unit (default is Liters)
     of FUEL used per year per cumulative unit installed. The equation may need to
     be edited if your energy savings depend on the marginal unit installed rather
     than the cumulative units. SolarPVUtil "Advanced Controls"!F159
  soln_fuel_efficiency_factor (float): This refers to the % fuel reduced by the
     SOLUTION relative to the CONVENTIONAL mix of technologies/practices. The
     Percent reduction is assumed to apply to the Conventional Fuel Unit, if
     different to the Solution Fuel Unit.

     FOR REPLACEMENT SOLUTIONS: enter 1 (e.g. electric vehicles fully replace fuel
     consumption with electricity use -- but be sure to add a negative value for
     Annual Energy Reduced from Electric Grid Mix!)

     FOR FUEL EFFICIENCY SOLUTIONS: enter positive number representing total fuel
     reduced, 0 < X < 1  (e.g. hybrid-electric vehicles partially replace fuel
     consumption with electricity use, it thus uses less fuel compared to conventional
     vehicles)

     FOR SOLUTIONS THAT CONSUME MORE FUEL THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:
     enter negative number representing total additional fuel used, X < 0 (e.g. we
     hope solutions do not actually consume more fuel than the conventional practice,
     check with the senior research team if you run into this)
     SolarPVUtil "Advanced Controls"!G159

  fuel_emissions_factor (float):
     SolarPVUtil "Advanced Controls"!I159
  fuel_emissions_factor_2 (float):
     SolarPVUtil "Advanced Controls"!I163

  conv_emissions_per_funit (float): This represents the direct CO2-eq emissions
     that result per functional unit that are not accounted for by use of the
     electric grid or fuel consumption.
     SolarPVUtil "Advanced Controls"!C174
  soln_emissions_per_funit (float): This represents the direct CO2-eq emissions
     that result per functional unit that are not accounted for by use of the
     electric grid or fuel consumption.
     SolarPVUtil "Advanced Controls"!D174

  ch4_is_co2eq (boolean): True if CH4 emissions measurement is in terms of CO2
     equivalent, False if measurement is in units of CH4 mass.
     derived from SolarPVUtil "Advanced Controls"!I184
  n2o_is_co2eq (boolean): True if N2O emissions measurement is in terms of CO2
     equivalent, False if measurement is in units of N2O mass.
     derived from SolarPVUtil "Advanced Controls"!J184
  co2eq_conversion_source (string): One of the conversion_source names
     defined in model/emissions_factors.py like "AR5 with feedback" or "AR4"
     SolarPVUtil "Advanced Controls"!I185
  ch4_co2_per_twh (float): CO2-equivalent CH4 emitted per TWh, in tons.
     SolarPVUtil "Advanced Controls"!I174
  n2o_co2_per_twh (float): CO2-equivalent N2O emitted per TWh, in tons.
     SolarPVUtil "Advanced Controls"!J174
  soln_indirect_co2_per_iunit (float): CO2-equivalent indirect emissions per
     iunit, in tons.  SolarPVUtil "Advanced Controls"!G174
  conv_indirect_co2_per_unit (float): CO2-equivalent indirect emissions per
     unit (func or impl depending on conv_indirect_co2_in_iunits).
     SolarPVUtil "Advanced Controls"!F174
  conv_indirect_co2_is_iunits (boolean): whether conv_indirect_co2_per_unit is
     iunits (True) or funits (False).  SolarPVUtil "Advanced Controls"!F184

  soln_lifetime_capacity (float): This is the average expected number of
     functional units generated by the SOLUTION throughout their lifetime
     before replacement is required.  If no replacement time is discovered or
     applicable the fellow will default to 100 years.

     E.g. an electric vehicle will have an average number of passenger kilometers
     it can travel until it can no longer be used and a new vehicle is required.
     Another example would be an efficient HVAC system, which can only service a
     certain amount of floor space over a period of time before it will require
     replacement.  SolarPVUtil "Advanced Controls"!E128
  soln_avg_annual_use (float): Average Annual Use is the average annual use of
     the technology/practice, in functional units per implementation unit. This
     will likely differ significantly based on location, be sure to note which
     region the data is coming from. If data varies substantially by region, a
     weighted average may need to be used.

     E.g. the average annual number of passenger kilometers (pkm) traveled per
     electric vehicle.  SolarPVUtil "Advanced Controls"!F128
  conv_lifetime_capacity (float): as soln_lifetime_capacity but for the conventional
     technology.  SolarPVUtil "Advanced Controls"!E95
  conv_avg_annual_use (float): as soln_avg_annual_use but for the conventional
     technology.  SolarPVUtil "Advanced Controls"!F95

  report_start_year (int): first year of results to report (typically 2020).
     SolarPVUtil "Advanced Controls"!H4
  report_end_year (int): last year of results to report (typically 2050).
     SolarPVUtil "Advanced Controls"!I4

  soln_var_oper_cost_per_funit (float): This is the annual operating cost per functional
     unit, derived from the SOLUTION.  In most cases this will be expressed as a
     cost per 'some unit of energy'.

     E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this
     can be considered the weighted average price of fuel per passenger kilometer.
     SolarPVUtil "Advanced Controls"!H128
  soln_fixed_oper_cost_per_iunit (float): This is the annual operating cost per
     implementation unit, derived from the SOLUTION.  In most cases this will be
     expressed as a cost per 'some unit of installation size'

     E.g., $10,000 per kw. In terms of transportation, this can be considered the
     total insurance, and maintenance cost per car.

     Purchase costs can be amortized here or included as a first cost, but not both.
     SolarPVUtil "Advanced Controls"!I128
  soln_fuel_cost_per_funit (float): Fuel/consumable cost per functional unit.
     SolarPVUtil "Advanced Controls"!K128
  conv_var_oper_cost_per_funit (float): as soln_var_oper_cost_per_funit.
     SolarPVUtil "Advanced Controls"!H95
  conv_fixed_oper_cost_per_iunit (float): as soln_fixed_oper_cost_per_funit.
     SolarPVUtil "Advanced Controls"!I95
  conv_fuel_cost_per_funit (float): as soln_fuel_cost_per_funit.
     SolarPVUtil "Advanced Controls"!K95

  npv_discount_rate (float): discount rate for Net Present Value calculations.
     SolarPVUtil "Advanced Controls"!B141

  emissions_use_co2eq (boolean): whether to use CO2-equivalent for ppm calculations.
     SolarPVUtil "Advanced Controls"!B189
  emissions_grid_source (string): "IPCC Only" or "Meta Analysis" of multiple studies.
     SolarPVUtil "Advanced Controls"!C189
  emissions_grid_range (string): "mean", "low" or "high" for which estimate to use.
     SolarPVUtil "Advanced Controls"!D189

  soln_ref_adoption_regional_data (boolean): whether funit adoption should add the regional data
     to estimate the World, or perform a separate estimate for the world.
     SolarPVUtil "Advanced Controls"!B284
  soln_pds_adoption_regional_data (boolean): as soln_ref_adoption_regional_data.
     SolarPVUtil "Advanced Controls"!B246
  soln_pds_adoption_basis (string): the type of interpolation to fill in adoption data for
     each year. Must be one of valid_adoption_bases. SolarPVUtil "Advanced Controls"!B243
  soln_pds_adoption_prognostication_source (string): the name of one specific data source, or the
     name of a class of sources (like "Conservative Cases" or "Ambitious Cases"), or "ALL SOURCES"
     to take the average of all sources. SolarPVUtil "Advanced Controls"!B265
  soln_pds_adoption_prognostication_trend (string): the type of curve fit
     to use like 2nd order polynomial or exponential. SolarPVUtil "Advanced Controls"!B270
  soln_pds_adoption_prognostication_growth (string): High, Medium, or Low projected growth.
     SolarPVUtil "Advanced Controls"!C270
  pds_source_post_2014 (string): The name of the data source to use for the PDS case for
     years after 2014. SolarPVUtil "Advanced Controls"!B55
  ref_source_post_2014 (string): The name of the data source to use for the REF case for
     years after 2014. SolarPVUtil "Advanced Controls"!B54
  source_until_2014 (string): The name of the data source to use for all cases for years
     2014 and before. SolarPVUtil "Advanced Controls"!B53
  ref_adoption_use_pds_years (list of int): years for which the Helpertables REF adoption
     for 'World' should use the PDS adoption values. SolarPVUtil "ScenarioRecord"! offset 218
  pds_adoption_use_ref_years (list of int): years for which the Helpertables PDS adoption
     for 'World' should use the REF adoption values. SolarPVUtil "ScenarioRecord"! offset 219

  solution_category (SOLUTION_CATEGORY): Whether the solution is primarily REDUCTION of
     emissions from an existing technology, REPLACEMENT of a technology to one with lower
     emissions, or NOT_APPLICABLE for something else entirely.  'Advanced Controls'!A159

  seq_rate_global (float): carbon sequestration rate for All Land or All of Special Land.
    TropicalForests "Advanced Controls"!B173 (Land models)
  disturbance_rate (float): disturbance rate TropicalForests "Advanced Controls"!I173 (Land models)
  """
  def __init__(self,
               pds_2014_cost=None,
               ref_2014_cost=None,
               conv_2014_cost=None,

               soln_first_cost_efficiency_rate=None,
               conv_first_cost_efficiency_rate=None,
               soln_first_cost_below_conv=None,

               soln_energy_efficiency_factor=None,
               conv_annual_energy_used=None,
               soln_annual_energy_used=None,

               conv_fuel_consumed_per_funit=None,
               soln_fuel_efficiency_factor=None,
               fuel_emissions_factor=None,
               fuel_emissions_factor_2=None,

               conv_emissions_per_funit=None,
               soln_emissions_per_funit=None,

               ch4_is_co2eq=None,
               n2o_is_co2eq=None,
               co2eq_conversion_source=None,
               ch4_co2_per_twh=None,
               n2o_co2_per_twh=None,
               soln_indirect_co2_per_iunit=None,
               conv_indirect_co2_per_unit=None,
               conv_indirect_co2_is_iunits=None,

               soln_lifetime_capacity=None,
               soln_avg_annual_use=None,
               conv_lifetime_capacity=None,
               conv_avg_annual_use=None,

               report_start_year=2020,
               report_end_year=2050,

               soln_var_oper_cost_per_funit=None,
               soln_fixed_oper_cost_per_iunit=None,
               soln_fuel_cost_per_funit=None,
               conv_var_oper_cost_per_funit=None,
               conv_fixed_oper_cost_per_iunit=None,
               conv_fuel_cost_per_funit=None,

               npv_discount_rate=None,

               emissions_use_co2eq=None,
               emissions_grid_source=None,
               emissions_grid_range=None,

               soln_ref_adoption_regional_data=None,
               soln_pds_adoption_regional_data=None,
               soln_pds_adoption_basis=None,
               soln_pds_adoption_prognostication_source=None,
               soln_pds_adoption_prognostication_trend=None,
               soln_pds_adoption_prognostication_growth=None,
               pds_source_post_2014=None,
               ref_source_post_2014=None,
               source_until_2014=None,
               ref_adoption_use_pds_years=set(),
               pds_adoption_use_ref_years=set(),

               solution_category=None,

               # land only
               seq_rate_global=None,
               disturbance_rate=None
               ):

    self.pds_2014_cost = pds_2014_cost
    self.ref_2014_cost = ref_2014_cost
    self.conv_2014_cost = conv_2014_cost
    self.soln_first_cost_efficiency_rate = soln_first_cost_efficiency_rate
    self.conv_first_cost_efficiency_rate = conv_first_cost_efficiency_rate
    self.soln_first_cost_below_conv = soln_first_cost_below_conv
    self.soln_energy_efficiency_factor = self.value_or_zero(soln_energy_efficiency_factor)
    self.conv_annual_energy_used = self.value_or_zero(conv_annual_energy_used)
    self.soln_annual_energy_used = self.value_or_zero(soln_annual_energy_used)
    self.conv_fuel_consumed_per_funit = self.value_or_zero(conv_fuel_consumed_per_funit)
    self.soln_fuel_efficiency_factor = self.value_or_zero(soln_fuel_efficiency_factor)
    self.fuel_emissions_factor = self.value_or_zero(fuel_emissions_factor)
    self.fuel_emissions_factor_2 = self.value_or_zero(fuel_emissions_factor_2)
    self.conv_emissions_per_funit = self.value_or_zero(conv_emissions_per_funit)
    self.soln_emissions_per_funit = self.value_or_zero(soln_emissions_per_funit)

    self.ch4_is_co2eq = ch4_is_co2eq
    self.n2o_is_co2eq = n2o_is_co2eq
    self.co2eq_conversion_source = co2eq_conversion_source
    if isinstance(co2eq_conversion_source, str):
      self.co2eq_conversion_source = ef.string_to_conversion_source(co2eq_conversion_source)
    self.ch4_co2_per_twh = self.value_or_zero(ch4_co2_per_twh)
    self.n2o_co2_per_twh = self.value_or_zero(n2o_co2_per_twh)
    self.soln_indirect_co2_per_iunit = soln_indirect_co2_per_iunit
    self.conv_indirect_co2_per_unit = conv_indirect_co2_per_unit
    self.conv_indirect_co2_is_iunits = conv_indirect_co2_is_iunits

    self.soln_lifetime_capacity = soln_lifetime_capacity
    self.soln_avg_annual_use = soln_avg_annual_use
    self.conv_lifetime_capacity = conv_lifetime_capacity
    self.conv_avg_annual_use = conv_avg_annual_use
    self.report_start_year = report_start_year
    self.report_end_year = report_end_year
    self.soln_var_oper_cost_per_funit = soln_var_oper_cost_per_funit
    self.soln_fixed_oper_cost_per_iunit = soln_fixed_oper_cost_per_iunit
    self.soln_fuel_cost_per_funit = soln_fuel_cost_per_funit
    self.conv_var_oper_cost_per_funit = conv_var_oper_cost_per_funit
    self.conv_fixed_oper_cost_per_iunit = conv_fixed_oper_cost_per_iunit
    self.conv_fuel_cost_per_funit = conv_fuel_cost_per_funit
    self.npv_discount_rate = npv_discount_rate

    self.emissions_use_co2eq = emissions_use_co2eq
    self.emissions_grid_source = emissions_grid_source
    if isinstance(emissions_grid_source, str):
      self.emissions_grid_source = ef.string_to_emissions_grid_source(emissions_grid_source)
    self.emissions_grid_range = emissions_grid_range
    if isinstance(emissions_grid_range, str):
      self.emissions_grid_range = ef.string_to_emissions_grid_range(emissions_grid_range)

    self.soln_ref_adoption_regional_data = soln_ref_adoption_regional_data
    self.soln_pds_adoption_regional_data = soln_pds_adoption_regional_data
    soln_pds_adoption_basis = translate_adoption_bases.get(soln_pds_adoption_basis,
        soln_pds_adoption_basis)
    if soln_pds_adoption_basis not in valid_adoption_bases:
      raise ValueError("invalid adoption basis name=" + str(soln_pds_adoption_basis))
    self.soln_pds_adoption_basis = soln_pds_adoption_basis
    self.soln_pds_adoption_prognostication_source = soln_pds_adoption_prognostication_source
    self.soln_pds_adoption_prognostication_trend = soln_pds_adoption_prognostication_trend
    if soln_pds_adoption_prognostication_growth not in valid_adoption_growth:
      g = soln_pds_adoption_prognostication_growth
      raise ValueError("invalid adoption prognostication growth name=" + str(g))
    self.soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth
    self.pds_source_post_2014 = pds_source_post_2014
    self.ref_source_post_2014 = ref_source_post_2014
    self.source_until_2014 = source_until_2014

    self.ref_adoption_use_pds_years = ref_adoption_use_pds_years
    self.pds_adoption_use_ref_years = pds_adoption_use_ref_years
    intersect = set(ref_adoption_use_pds_years) & set(pds_adoption_use_ref_years)
    if intersect:
      err = "cannot be in both ref_adoption_use_pds_years and pds_adoption_use_ref_years:" + str(intersect)
      raise ValueError(err)

    self.solution_category = solution_category
    if isinstance(solution_category, str):
      self.solution_category = self.string_to_solution_category(solution_category)

    # Land only
    self.seq_rate_global = seq_rate_global
    self.disturbance_rate = disturbance_rate

  def value_or_zero(self, val):
    """Allow a blank space or empty string to mean zero.
       Useful for advanced controls like conv_average_electricity_used."""
    try:
      return float(val)
    except (ValueError, TypeError):
      return 0.0

  @property
  def soln_first_cost_learning_rate(self):
    return 1.0 - self.soln_first_cost_efficiency_rate

  @property
  def conv_first_cost_learning_rate(self):
    return 1.0 - self.conv_first_cost_efficiency_rate

  @property
  def soln_fuel_learning_rate(self):
    return 1.0 - self.soln_fuel_efficiency_factor

  @property
  def soln_lifetime_replacement(self):
    return self.soln_lifetime_capacity / self.soln_avg_annual_use

  @property
  def conv_lifetime_replacement(self):
    return self.conv_lifetime_capacity / self.conv_avg_annual_use

  def string_to_solution_category(self, text):
    ltext = str(text).lower()
    if ltext == "replacement":
      return SOLUTION_CATEGORY.REPLACEMENT
    elif ltext == "reduction":
      return SOLUTION_CATEGORY.REDUCTION
    elif ltext == 'land':
      return SOLUTION_CATEGORY.LAND
    elif ltext == "not_applicable" or ltext == "not applicable" or ltext == "na":
      return SOLUTION_CATEGORY.NOT_APPLICABLE
    raise ValueError("invalid solution category: " + str(text))
