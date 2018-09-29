"""First Cost model calculations."""

import math

import advanced_controls
import pandas as pd

TERAWATT_TO_KILOWATT = 10**9


class FirstCost:
  """Implementation for the First Cost model.

  Arguments:
  ac = advanced_cost.py object, storing settings to control
    model operation.
  pds_learning_increase_mult = multiplicative factor for the PDS learning
    rate. This is typically 2 or 4.
  conv_learning_increase_mult = multiplicative factor for the Conventional
    learning rate. This is typically 2 or 4.
  """
  def __init__(self, ac, pds_learning_increase_mult,
      conv_learning_increase_mult):
    self.ac = ac
    self.pds_learning_increase_mult = pds_learning_increase_mult
    self.conv_learning_increase_mult = conv_learning_increase_mult

  def pds_install_cost_per_iunit(self, pds_tot_soln_iunits_req,
      ref_tot_conv_iunits_req):
    cumulative_units_adoption_2015 = pds_tot_soln_iunits_req[1]

    log_learning_rate = math.log10(self.ac.pds_first_cost_learning_rate)
    log_learning_mult = math.log10(self.pds_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    p = (1 / cumulative_units_adoption_2015) ** parameter_b
    first_unit_cost = self.ac.pds_2014_cost * p

    result_per_tW = (first_unit_cost * pds_tot_soln_iunits_req ** parameter_b)
    result_per_kW = result_per_tW * TERAWATT_TO_KILOWATT

    if self.ac.pds_first_cost_below_conv:
      return result_per_kW
    else:
      conv = self.conv_install_cost_per_iunit(ref_tot_conv_iunits_req)
      result = []
      for i, pds in enumerate(result_per_kW):
        result[i] = max(pds, conv[i])
      return pd.Series(result)


  def conv_install_cost_per_iunit(self, ref_tot_conv_iunits_req):
    # TODO: Excel implementation referenced the cell for 2014, not 2015, so we
    # do the same here. To correct this, use ref_tot_conv_iunits_req[1]
    cumulative_units_adoption_2015 = ref_tot_conv_iunits_req[0]

    log_learning_rate = math.log10(self.ac.conv_first_cost_learning_rate)
    log_learning_mult = math.log10(self.conv_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    p = (1 / cumulative_units_adoption_2015) ** parameter_b
    first_unit_cost = self.ac.conv_2014_cost * p

    result = []
    prev_val = 0
    for i, val in enumerate(ref_tot_conv_iunits_req):
      calc = first_unit_cost * ref_tot_conv_iunits_req[i] ** parameter_b
      calc_invalid = (ref_tot_conv_iunits_req[i] == 0) and (parameter_b == 0)
      if calc_invalid:
        new_val = first_unit_cost
      else:
        new_val = first_unit_cost * ref_tot_conv_iunits_req[i] ** parameter_b
      new_val = new_val * TERAWATT_TO_KILOWATT
      result.append(min(prev_val, new_val))
      prev_val = new_val
    return pd.Series(result)
