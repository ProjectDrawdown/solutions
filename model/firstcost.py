"""First Cost module calculations."""

from functools import lru_cache
import math

import numpy as np
import pandas as pd


class FirstCost:
  """Implementation for the First Cost module.

  Arguments:
    ac = advanced_controls.py object, storing settings to control module operation.
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
    conv_ref_tot_iunits: total implementation units required each year in
      the Conventional Reference scenario, as a DataFrame with columns per region.
    soln_pds_new_iunits_reqd: new implementation units required each year in
      the Project Drawdown scenario, as a DataFrame with columns per region.
    soln_ref_new_iunits_reqd: new implementation units required each year in
      the Reference scenario, as a DataFrame with columns per region.
    conv_ref_new_iunits: new implementation units required each year in
      the Conventional Reference scenario, as a DataFrame with columns per region.
    fc_convert_iunit_factor: conversion factor from iunits to a more natural monetary
      unit.
    conv_ref_first_cost_uses_tot_units: Many RRS solutions use conv_ref_new_iunits to
      calculate conv_ref_annual_world_first_cost. Many Land solutions use the new
      conv_ref_tot_iunits year over year (which are land units, not iunits, in this case).
  """
  def __init__(self, ac, pds_learning_increase_mult,
      ref_learning_increase_mult, conv_learning_increase_mult,
      soln_pds_tot_iunits_reqd, soln_ref_tot_iunits_reqd, conv_ref_tot_iunits,
      soln_pds_new_iunits_reqd, soln_ref_new_iunits_reqd, conv_ref_new_iunits,
      fc_convert_iunit_factor=1.0, conv_ref_first_cost_uses_tot_units=False):
    self.ac = ac
    self.pds_learning_increase_mult = pds_learning_increase_mult
    self.ref_learning_increase_mult = ref_learning_increase_mult
    self.conv_learning_increase_mult = conv_learning_increase_mult
    self.soln_pds_tot_iunits_reqd = soln_pds_tot_iunits_reqd
    self.soln_ref_tot_iunits_reqd = soln_ref_tot_iunits_reqd
    self.conv_ref_tot_iunits = conv_ref_tot_iunits
    self.soln_pds_new_iunits_reqd = soln_pds_new_iunits_reqd
    self.soln_ref_new_iunits_reqd = soln_ref_new_iunits_reqd
    self.conv_ref_new_iunits = conv_ref_new_iunits
    self.fc_convert_iunit_factor = fc_convert_iunit_factor
    self.conv_ref_first_cost_uses_tot_units = conv_ref_first_cost_uses_tot_units

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

    world = self.soln_pds_tot_iunits_reqd.loc[:, 'World']
    result_per_iunit = (first_unit_cost * world ** parameter_b)
    # In Excel, NaN^0 == NaN. In Python, NaN^0 == 1.
    # We want to match the Excel behavior.
    result_per_iunit.mask(world.isna(), other=np.nan, inplace=True)
    result_display = result_per_iunit * self.fc_convert_iunit_factor

    if self.ac.soln_first_cost_below_conv:
      result = result_display
    else:
      conv = self.conv_ref_install_cost_per_iunit()
      result = result_display.combine(conv, lambda x1, x2: max(x1, x2))
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
    p = (1 / self.conv_ref_tot_iunits['World'][2014]) ** parameter_b
    first_unit_cost = self.ac.conv_2014_cost * p

    def calc(x):
      if x == 0 or parameter_b == 0:
        new_val = first_unit_cost
      elif pd.isna(x):
        new_val = np.nan
      else:
        new_val = first_unit_cost * x ** parameter_b
      return new_val * self.fc_convert_iunit_factor
    step1 = self.conv_ref_tot_iunits['World'].apply(calc)
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
      if x == 0 or parameter_b == 0:
        new_val = first_unit_cost
      elif pd.isna(x):
        new_val = np.nan
      else:
        new_val = first_unit_cost * x ** parameter_b
      return new_val * self.fc_convert_iunit_factor
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
    return result

  @lru_cache()
  def soln_ref_annual_world_first_cost(self):
    """Annual World First Cost (SOLUTION-REF)
       'First Cost'!N37:N82
    """
    result = self.soln_ref_new_iunits_reqd["World"] * self.soln_ref_install_cost_per_iunit()
    result.name = "soln_ref_annual_world_first_cost"
    return result

  @lru_cache()
  def conv_ref_annual_world_first_cost(self):
    """Annual World First Cost (CONVENTIONAL-REF)
       'First Cost'!Q37:Q82
    """
    if self.conv_ref_first_cost_uses_tot_units:
      result = self.conv_ref_tot_iunits["World"].diff() * self.conv_ref_install_cost_per_iunit()
    else:
      result = self.conv_ref_new_iunits["World"] * self.conv_ref_install_cost_per_iunit()
    result.name = "conv_ref_annual_world_first_cost"
    return result

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
    csum1 = self.conv_ref_annual_world_first_cost().fillna(0.0).clip(lower=0.0).cumsum()
    csum2 = self.soln_ref_annual_world_first_cost().fillna(0.0).clip(lower=0.0).cumsum()
    result = csum1.add(csum2)
    result.name = "ref_cumulative_install"
    return result
