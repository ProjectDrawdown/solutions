"""First Cost module calculations."""

import math

import advanced_controls
import numpy as np
import pandas as pd

TERAWATT_TO_KILOWATT = 10**9


class FirstCost:
  """Implementation for the First Cost module.

  Arguments:
  ac = advanced_cost.py object, storing settings to control
    model operation.
  pds_learning_increase_mult = multiplicative factor for the PDS learning
    rate. This is typically 2 or 4.
  conv_learning_increase_mult = multiplicative factor for the Conventional
    learning rate. This is typically 2 or 4.
  """
  def __init__(self, ac, pds_learning_increase_mult,
      ref_learning_increase_mult, conv_learning_increase_mult):
    self.ac = ac
    self.pds_learning_increase_mult = pds_learning_increase_mult
    self.ref_learning_increase_mult = ref_learning_increase_mult
    self.conv_learning_increase_mult = conv_learning_increase_mult

  def soln_pds_install_cost_per_iunit(self, soln_pds_tot_iunits_reqd,
      conv_ref_tot_iunits_reqd):
    log_learning_rate = math.log10(self.ac.soln_first_cost_learning_rate)
    log_learning_mult = math.log10(self.pds_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    p = (1 / soln_pds_tot_iunits_reqd['World'][2015]) ** parameter_b
    first_unit_cost = self.ac.pds_2014_cost * p

    result_per_tW = (first_unit_cost * soln_pds_tot_iunits_reqd.loc[:, 'World'] ** parameter_b)
    result_per_kW = result_per_tW * TERAWATT_TO_KILOWATT

    if self.ac.soln_first_cost_below_conv:
      return result_per_kW
    else:
      conv = self.conv_ref_install_cost_per_iunit(conv_ref_tot_iunits_reqd)
      return result_per_kW.combine(conv, lambda x1, x2: max(x1, x2))

  def conv_ref_install_cost_per_iunit(self, conv_ref_tot_iunits_reqd):
    log_learning_rate = math.log10(self.ac.conv_first_cost_learning_rate)
    log_learning_mult = math.log10(self.conv_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    # Excel implementation referenced the cell for 2014, not 2015, so we
    # do the same here. Normally, we base calculations from 2015.
    p = (1 / conv_ref_tot_iunits_reqd['World'][2014]) ** parameter_b
    first_unit_cost = self.ac.conv_2014_cost * p

    def calc(x):
      if x == 0 and parameter_b == 0:
        new_val = first_unit_cost
      else:
        new_val = first_unit_cost * x ** parameter_b
      return new_val * TERAWATT_TO_KILOWATT
    step1 = conv_ref_tot_iunits_reqd['World'].apply(calc)
    # The model postulates that conventional technologies decrease
    # in cost only slowly, and never increase in cost. We walk back
    # through the array comparing each year to the previous year.
    step2 = step1.rolling(2).apply(lambda x: min(x[0], x[1]), raw=True)
    first = step1.first_valid_index()
    step2[first] = step1[first]  # no min() for first item
    return step2

  def soln_ref_install_cost_per_iunit(self, soln_ref_tot_iunits_reqd,
      conv_ref_tot_iunits_reqd):
    log_learning_rate = math.log10(self.ac.soln_first_cost_learning_rate)
    log_learning_mult = math.log10(self.ref_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    if soln_ref_tot_iunits_reqd['World'][2015] == 0:
      first_unit_cost = self.ac.ref_2014_cost
    else:
      p = (1 / soln_ref_tot_iunits_reqd['World'][2015]) ** parameter_b
      first_unit_cost = self.ac.ref_2014_cost * p

    def calc(x):
      if x == 0 and parameter_b == 0:
        new_val = first_unit_cost
      else:
        new_val = first_unit_cost * x ** parameter_b
      return new_val * TERAWATT_TO_KILOWATT
    step1 = soln_ref_tot_iunits_reqd.loc[:, 'World'].apply(calc)
    if self.ac.soln_first_cost_below_conv:
      return step1
    else:
      conv = self.conv_ref_install_cost_per_iunit(conv_ref_tot_iunits_reqd)
      return step1.combine(conv, lambda x1, x2: max(x1, x2))

  def soln_pds_annual_world_first_cost(self, soln_pds_new_iunits_reqd,
      soln_pds_install_cost_per_iunit):
    result = soln_pds_new_iunits_reqd["World"] * soln_pds_install_cost_per_iunit
    return result.dropna()

  def soln_pds_cumulative_install(self, soln_pds_annual_world_first_cost):
    return soln_pds_annual_world_first_cost.cumsum()

  def soln_ref_annual_world_first_cost(self, soln_ref_new_iunits_reqd,
      soln_ref_install_cost_per_iunit):
    result = soln_ref_new_iunits_reqd["World"] * soln_ref_install_cost_per_iunit
    return result.dropna()

  def conv_ref_annual_world_first_cost(self, conv_ref_new_iunits_reqd,
      conv_ref_install_cost_per_iunit):
    result = conv_ref_new_iunits_reqd["World"] * conv_ref_install_cost_per_iunit
    return result.dropna()

  def ref_cumulative_install(self, conv_ref_annual_world_first_cost,
      soln_ref_annual_world_first_cost):
    csum1 = conv_ref_annual_world_first_cost.cumsum()
    csum2 = soln_ref_annual_world_first_cost.cumsum()
    return csum1.add(csum2)
