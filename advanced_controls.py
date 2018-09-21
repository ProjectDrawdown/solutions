"""Implements the Advanced Controls, settings which have a default
   but can be overridden to fit particular needs.
"""

class AdvancedControls:
  """Advanced Controls tab, with defaults set for SolarPVUtility."""
  def __init__(self,
               pds_2014_cost=1444.93954421485,
               conv_2014_cost=2010.03170851964,
               pds_first_cost_efficiency_rate=0.196222222222222,
               pds_first_cost_below_conv=True,
               conv_first_cost_efficiency_rate=0.02):
    self.pds_2014_cost = pds_2014_cost
    self.conv_2014_cost = conv_2014_cost
    self.pds_first_cost_efficiency_rate = pds_first_cost_efficiency_rate
    self.pds_first_cost_below_conv = pds_first_cost_below_conv
    self.conv_first_cost_efficiency_rate = conv_first_cost_efficiency_rate

  @property
  def pds_first_cost_learning_rate(self):
    return 1.0 - self.pds_first_cost_efficiency_rate

  @property
  def conv_first_cost_learning_rate(self):
    return 1.0 - self.conv_first_cost_efficiency_rate
