"""Implements the Advanced Controls, settings which have a default
   but can be overridden to fit particular needs.
"""

import pandas as pd
from model import emissions_factors

class AdvancedControls:
  """Advanced Controls tab, with defaults set for SolarPVUtility.
  pds_2014_cost: US$2014 cost to acquire + install, per implementation
     unit (ex: kW for energy scenarios), for the Project Drawdown
     Solution (PDS).
  ref_2014_cost: US$2014 cost to acquire + install, per implementation
     unit, for the reference technology.
  conv_2014_cost: US$2014 cost to acquire + install, per implementation
     unit, for the conventional technology.
  soln_first_cost_efficiency_rate: rate that the modelled solution improves /
     lowers in cost per year. In calculations this is usually converted
     to the learning rate, which is 1/efficiency_rate.
  conv_first_cost_efficiency_rate: rate that the conventional technology
     improves / lowers in cost each year. Efficiency rates for the
     conventional technology are typically close to zero, these technologies
     have already had many years of development and maturation.
     In calculations this is usually converted to the learning rate,
     which is 1/efficiency_rate.
  soln_first_cost_below_conv (boolean): The solution first cost may decline
     below that of the Conventional due to the learning rate chosen. This may
     be acceptable in some cases for instance when the projections in the
     literature indicate so. In other cases, it may not be likely for the
     Solution to become cheaper than the Conventional.
  soln_funit_adoption_2014 (pd.dataframe): vector of the functional unit adoption
     in 2014 for each region.
     "Advanced Controls"!C61:C70
  conv_ref_avg_annual_use (float): average annual use of the technology/practice,
     in functional units per implementation unit. This will likely differ
     significantly based on location, be sure to note which region the data is
     coming from. If data varies substantially by region, a weighted average may
     need to be used.
     E.g. the average annual number of passenger kilometers (pkm) traveled per
     conventional vehicle.
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
     "Advanced Controls"!C159
  conv_annual_energy_used (float): for solutions that reduce electricity
     consumption per functional unit, enter the average electricity used per
     functional unit of the conventional technologies/practices.
     "Advanced Controls"!B159
  soln_annual_energy_used (float): This refers to the units of average energy
     used per year per functional unit installed.

     This is an optional variable to be used in cases where a) the literature
     reports the energy use of the solution rather than energy efficiency; or
     b) the solution uses more electricity than the conventional
     technologies/practices.

     E.g. electric vehicles use energy from the electric grid, whereas
     conventional vehicles use only fuel)
     "Advanced Controls"!D159
  conv_emissions_per_funit (float): This represents the direct CO2-eq emissions
     that result per functional unit that are not accounted for by use of the
     electric grid or fuel consumption.
     "Advanced Controls"!C174
  soln_emissions_per_funit (float): This represents the direct CO2-eq emissions
     that result per functional unit that are not accounted for by use of the
     electric grid or fuel consumption.
     "Advanced Controls"!D174

  ch4_is_co2eq (boolean): True if CH4 emissions measurement is in terms of CO2
     equivalent, False if measurement is in units of CH4 mass.
     derived from "Advanced Controls"!I182
  n2o_is_co2eq (boolean): True if N2O emissions measurement is in terms of CO2
     equivalent, False if measurement is in units of N2O mass.
     derived from "Advanced Controls"!J182
  co2eq_conversion_source (string): One of the conversion_source names
     defined in model/emissions_factors.py like "AR5 with feedback" or "AR4"
  ch4_co2_per_twh (float): CO2-equivalent CH4 emitted per TWh, in tons.
  n2o_co2_per_twh (float): CO2-equivalent N2O emitted per TWh, in tons.

  soln_lifetime_capacity (float): This is the average expected number of
     functional units generated by the SOLUTION throughout their lifetime
     before replacement is required.  If no replacement time is discovered or
     applicable the fellow will default to 100 years.

     E.g. an electric vehicle will have an average number of passenger kilometers
     it can travel until it can no longer be used and a new vehicle is required.
     Another example would be an efficient HVAC system, which can only service a
     certain amount of floor space over a period of time before it will require
     replacement.
  soln_avg_annual_use (float): Average Annual Use is the average annual use of
     the technology/practice, in functional units per implementation unit. This
     will likely differ significantly based on location, be sure to note which
     region the data is coming from. If data varies substantially by region, a
     weighted average may need to be used.

     E.g. the average annual number of passenger kilometers (pkm) traveled per
     electric vehicle.

  report_start_year (int): first year of results to report (typically 2020).
  report_end_year (int): last year of results to report (typically 2050).
  """
  def __init__(self,
               pds_2014_cost=None,
               ref_2014_cost=None,
               conv_2014_cost=None,

               soln_first_cost_efficiency_rate=None,
               conv_first_cost_efficiency_rate=None,
               soln_first_cost_below_conv=None,

               soln_funit_adoption_2014=None,
               conv_ref_avg_annual_use=None,

               soln_energy_efficiency_factor=None,
               conv_annual_energy_used=None,
               soln_annual_energy_used=None,

               conv_fuel_consumed_per_funit=None,
               soln_fuel_efficiency_factor=None,

               conv_emissions_per_funit=None,
               soln_emissions_per_funit=None,

               ch4_is_co2eq=None,
               n2o_is_co2eq=None,
               co2eq_conversion_source=None,
               ch4_co2_per_twh=None,
               n2o_co2_per_twh=None,

               soln_lifetime_capacity=None,
               soln_avg_annual_use=None,
               report_start_year=None,
               report_end_year=None
               ):
    self.pds_2014_cost = pds_2014_cost
    self.ref_2014_cost = ref_2014_cost
    self.conv_2014_cost = conv_2014_cost
    self.soln_first_cost_efficiency_rate = soln_first_cost_efficiency_rate
    self.conv_first_cost_efficiency_rate = conv_first_cost_efficiency_rate
    self.soln_first_cost_below_conv = soln_first_cost_below_conv
    if type(soln_funit_adoption_2014) == list:
      s = soln_funit_adoption_2014
      self.soln_funit_adoption_2014 = pd.DataFrame(s[1:], columns=s[0], index=[2014])
      self.soln_funit_adoption_2014.index.name = 'Year'
    else:
      self.soln_funit_adoption_2014 = soln_funit_adoption_2014
    self.conv_ref_avg_annual_use = conv_ref_avg_annual_use
    self.soln_energy_efficiency_factor = self.value_or_zero(soln_energy_efficiency_factor)
    self.conv_annual_energy_used = self.value_or_zero(conv_annual_energy_used)
    self.soln_annual_energy_used = self.value_or_zero(soln_annual_energy_used)
    self.conv_fuel_consumed_per_funit = self.value_or_zero(conv_fuel_consumed_per_funit)
    self.soln_fuel_efficiency_factor = self.value_or_zero(soln_fuel_efficiency_factor)
    self.conv_emissions_per_funit = self.value_or_zero(conv_emissions_per_funit)
    self.soln_emissions_per_funit = self.value_or_zero(soln_emissions_per_funit)
    self.ch4_is_co2eq = ch4_is_co2eq
    self.n2o_is_co2eq = n2o_is_co2eq
    self.co2eq_conversion_source = None
    if co2eq_conversion_source:
      self.co2eq_conversion_source = emissions_factors.string_to_conversion_source(
          co2eq_conversion_source)
    self.ch4_co2_per_twh = self.value_or_zero(ch4_co2_per_twh)
    self.n2o_co2_per_twh = self.value_or_zero(n2o_co2_per_twh)
    self.soln_lifetime_capacity = soln_lifetime_capacity
    self.soln_avg_annual_use = soln_avg_annual_use
    self.report_start_year = report_start_year
    self.report_end_year = report_end_year

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
