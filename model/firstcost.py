"""First Cost module calculations."""

from functools import lru_cache
import math

import numpy as np
import pandas as pd

TERAWATT_TO_KILOWATT = 10**9


class FirstCost:
  """Implementation for the First Cost module.

  Arguments:
    ac = advanced_cost.py object, storing settings to control module operation.
    pds_learning_increase_mult = multiplicative factor for the PDS learning
      rate. This is typically 2 or 4.
    ref_learning_increase_mult = multiplicative factor for the reference
      solution learning rate. This is typically 2 or 4.
    conv_learning_increase_mult = multiplicative factor for the Conventional
      learning rate. This is typically 2 or 4.
    soln_pds_tot_iunits_reqd: total implementation units required each year in
      the Project Drawdown scenario, as a DataFrame with columns per region.
    soln_ref_tot_iunits_reqd: total implementation units required each year in
      the Reference scenario, as a DataFrame with columns per region.
    conv_ref_tot_iunits_reqd: total implementation units required each year in
      the Conventional Reference scenario, as a DataFrame with columns per region.
    soln_pds_new_iunits_reqd: new implementation units required each year in
      the Project Drawdown scenario, as a DataFrame with columns per region.
    soln_ref_new_iunits_reqd: new implementation units required each year in
      the Reference scenario, as a DataFrame with columns per region.
    conv_ref_new_iunits_reqd: new implementation units required each year in
      the Conventional Reference scenario, as a DataFrame with columns per region.
  """
  def __init__(self, ac, pds_learning_increase_mult,
      ref_learning_increase_mult, conv_learning_increase_mult,
      soln_pds_tot_iunits_reqd, soln_ref_tot_iunits_reqd, conv_ref_tot_iunits_reqd,
      soln_pds_new_iunits_reqd, soln_ref_new_iunits_reqd, conv_ref_new_iunits_reqd):
    self.ac = ac
    self.pds_learning_increase_mult = pds_learning_increase_mult
    self.ref_learning_increase_mult = ref_learning_increase_mult
    self.conv_learning_increase_mult = conv_learning_increase_mult
    self.soln_pds_tot_iunits_reqd = soln_pds_tot_iunits_reqd
    self.soln_ref_tot_iunits_reqd = soln_ref_tot_iunits_reqd
    self.conv_ref_tot_iunits_reqd = conv_ref_tot_iunits_reqd
    self.soln_pds_new_iunits_reqd = soln_pds_new_iunits_reqd
    self.soln_ref_new_iunits_reqd = soln_ref_new_iunits_reqd
    self.conv_ref_new_iunits_reqd = conv_ref_new_iunits_reqd

  @lru_cache()
  def soln_pds_install_cost_per_iunit(self):
    """Install cost per implementation unit in Solution-PDS
       'First Cost'!C37:C82
    """
    log_learning_rate = math.log10(self.ac.soln_first_cost_learning_rate)
    log_learning_mult = math.log10(self.pds_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    p = (1 / self.soln_pds_tot_iunits_reqd['World'][2015]) ** parameter_b
    first_unit_cost = self.ac.pds_2014_cost * p

    result_per_tW = (first_unit_cost * self.soln_pds_tot_iunits_reqd.loc[:, 'World'] ** parameter_b)
    result_per_kW = result_per_tW * TERAWATT_TO_KILOWATT

    if self.ac.soln_first_cost_below_conv:
      result = result_per_kW
    else:
      conv = self.conv_ref_install_cost_per_iunit()
      result = result_per_kW.combine(conv, lambda x1, x2: max(x1, x2))
    result.name = "soln_pds_install_cost_per_iunit"
    return result

  @lru_cache()
  def conv_ref_install_cost_per_iunit(self):
    """Install cost per implementation unit in Conventional-REF
       'First Cost'!O37:O82
    """
    log_learning_rate = math.log10(self.ac.conv_first_cost_learning_rate)
    log_learning_mult = math.log10(self.conv_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    # Excel implementation referenced the cell for 2014, not 2015, so we
    # do the same here. Normally, we base calculations from 2015.
    p = (1 / self.conv_ref_tot_iunits_reqd['World'][2014]) ** parameter_b
    first_unit_cost = self.ac.conv_2014_cost * p

    def calc(x):
      if x == 0 and parameter_b == 0:
        new_val = first_unit_cost
      else:
        new_val = first_unit_cost * x ** parameter_b
      return new_val * TERAWATT_TO_KILOWATT
    step1 = self.conv_ref_tot_iunits_reqd['World'].apply(calc)
    # The model postulates that conventional technologies decrease
    # in cost only slowly, and never increase in cost. We walk back
    # through the array comparing each year to the previous year.
    step2 = step1.rolling(2).apply(lambda x: min(x[0], x[1]), raw=True)
    first = step1.first_valid_index()
    step2[first] = step1[first]  # no min() for first item
    step2.name = "conv_ref_install_cost_per_iunit"
    return step2

  @lru_cache()
  def soln_ref_install_cost_per_iunit(self):
    """Install cost per implementation unit in Solution-REF
       'First Cost'!L37:L82
    """
    log_learning_rate = math.log10(self.ac.soln_first_cost_learning_rate)
    log_learning_mult = math.log10(self.ref_learning_increase_mult)
    parameter_b = log_learning_rate / log_learning_mult

    if self.soln_ref_tot_iunits_reqd['World'][2015] == 0:
      first_unit_cost = self.ac.ref_2014_cost
    else:
      p = (1 / self.soln_ref_tot_iunits_reqd['World'][2015]) ** parameter_b
      first_unit_cost = self.ac.ref_2014_cost * p

    def calc(x):
      if x == 0 and parameter_b == 0:
        new_val = first_unit_cost
      else:
        new_val = first_unit_cost * x ** parameter_b
      return new_val * TERAWATT_TO_KILOWATT
    step1 = self.soln_ref_tot_iunits_reqd.loc[:, 'World'].apply(calc)
    if self.ac.soln_first_cost_below_conv:
      result = step1
    else:
      conv = self.conv_ref_install_cost_per_iunit()
      result = step1.combine(conv, lambda x1, x2: max(x1, x2))
    result.name = "soln_ref_install_cost_per_iunit"
    return result

  @lru_cache()
  def soln_pds_annual_world_first_cost(self):
    """Annual World First Cost (SOLUTION-PDS)
       'First Cost'!E37:E82
    """
    result = self.soln_pds_new_iunits_reqd["World"] * self.soln_pds_install_cost_per_iunit()
    result.name = "soln_pds_annual_world_first_cost"
    return result.dropna()

  @lru_cache()
  def soln_ref_annual_world_first_cost(self):
    """Annual World First Cost (SOLUTION-REF)
       'First Cost'!N37:N82
    """
    result = self.soln_ref_new_iunits_reqd["World"] * self.soln_ref_install_cost_per_iunit()
    result.name = "soln_ref_annual_world_first_cost"
    return result.dropna()

  @lru_cache()
  def conv_ref_annual_world_first_cost(self):
    """Annual World First Cost (SOLUTION-REF)
       'First Cost'!Q37:Q82
    """
    result = self.conv_ref_new_iunits_reqd["World"] * self.conv_ref_install_cost_per_iunit()
    result.name = "conv_ref_annual_world_first_cost"
    return result.dropna()

  @lru_cache()
  def soln_pds_cumulative_install(self):
    """Cumulative Install/Implementation (SOLUTION-PDS)
       'First Cost'!F37:F82
    """
    result = self.soln_pds_annual_world_first_cost().cumsum()
    result.name = "soln_pds_cumulative_install"
    return result

  @lru_cache()
  def ref_cumulative_install(self):
    """Cumulative Install / Implementation (CONVENTIONAL-REF + SOLUTION-REF)
       'First Cost'!R37:R82
    """
    csum1 = self.conv_ref_annual_world_first_cost().cumsum()
    csum2 = self.soln_ref_annual_world_first_cost().cumsum()
    result = csum1.add(csum2)
    result.name = "ref_cumulative_install"
    return result

  def to_dict(self):
    """Return all fields as a dict, to be serialized to JSON."""
    rs = dict()
    rs['soln_pds_install_cost_per_iunit'] = self.soln_pds_install_cost_per_iunit()
    rs['conv_ref_install_cost_per_iunit'] = self.conv_ref_install_cost_per_iunit()
    rs['soln_ref_install_cost_per_iunit'] = self.soln_ref_install_cost_per_iunit()
    rs['soln_pds_annual_world_first_cost'] = self.soln_pds_annual_world_first_cost()
    rs['soln_ref_annual_world_first_cost'] = self.soln_ref_annual_world_first_cost()
    rs['conv_ref_annual_world_first_cost'] = self.conv_ref_annual_world_first_cost()
    rs['soln_pds_cumulative_install'] = self.soln_pds_cumulative_install()
    rs['ref_cumulative_install'] = self.ref_cumulative_install()
    return rs
