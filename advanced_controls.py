"""Implements the Advanced Controls, settings which have a default
   but can be overridden to fit particular needs.
"""

class AdvancedControls:
  """Advanced Controls tab, with defaults set for SolarPVUtility.
  pds_2014_cost: US$2014 cost to acquire + install, per implementation
     unit (ex: kW for energy scenarios), for the Project Drawdown
     Solution (PDS).
  conv_2014_cost: US$2014 cost to acquire + install, per implementation
     unit, for the conventional technology.
  pds_first_cost_efficiency_rate: rate that the modelled solution improves /
     lowers in cost per year. In calculations this is usually converted
     to the learning rate, which is 1/efficiency_rate.
  conv_first_cost_efficiency_rate: rate that the conventional technology
     improves / lowers in cost each year. Efficiency rates for the
     conventional technology are typically close to zero, these technologies
     have already had many years of development and maturation.
     In calculations this is usually converted to the learning rate,
     which is 1/efficiency_rate.
  pds_first_cost_below_conv (boolean): The solution first cost may decline
     below that of the Conventional due to the learning rate chosen. This may
     be acceptable in some cases for instance when the projections in the
     literature indicate so. In other cases, it may not be likely for the
     Solution to become cheaper than the Conventional.
  """
  def __init__(self,
               pds_2014_cost=1444.93954421485,
               conv_2014_cost=2010.03170851964,
               pds_first_cost_efficiency_rate=0.196222222222222,
               conv_first_cost_efficiency_rate=0.02,
               pds_first_cost_below_conv=True):
    self.pds_2014_cost = pds_2014_cost
    self.conv_2014_cost = conv_2014_cost
    self.pds_first_cost_efficiency_rate = pds_first_cost_efficiency_rate
    self.conv_first_cost_efficiency_rate = conv_first_cost_efficiency_rate
    self.pds_first_cost_below_conv = pds_first_cost_below_conv

  @property
  def pds_first_cost_learning_rate(self):
    return 1.0 - self.pds_first_cost_efficiency_rate

  @property
  def conv_first_cost_learning_rate(self):
    return 1.0 - self.conv_first_cost_efficiency_rate
