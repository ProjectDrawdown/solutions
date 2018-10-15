"""Operating Cost module calculations."""

import math

import advanced_controls
import numpy as np
import pandas as pd

TERAWATT_TO_KILOWATT = 10**9


class OperatingCost:
  """Implementation for the Operating Cost module.

  Arguments:
  ac = advanced_cost.py object, storing settings to control
    model operation.
  """
  def __init__(self, ac):
    self.ac = ac

  def soln_new_funits_per_year(self, soln_net_annual_funits_adopted):
    """New functional units required each year.
       'Operating Cost'!F19:F64
    """
    growth = soln_net_annual_funits_adopted.diff().dropna()
    growth.name = 'New Functional Units each Year'
    growth.index.name = 'Year'
    first_year = soln_net_annual_funits_adopted.first_valid_index()
    growth = growth.append(soln_net_annual_funits_adopted.iloc[0, :])
    return growth.sort_index()

  def soln_pds_net_annual_iunits_reqd(self, soln_pds_tot_iunits_reqd, soln_ref_tot_iunits_reqd):
    """Total implementation units required each year.
       'Operating Cost'!I531:I576
    """
    result = soln_pds_tot_iunits_reqd - soln_ref_tot_iunits_reqd
    result.name = 'Net Annual Implementation Units Required (SOLUTION-PDS)'
    result.index.name = 'Year'
    return result

  def soln_pds_new_annual_iunits_reqd(self, soln_pds_net_annual_iunits_reqd):
    """New implementation units required each year.
       'Operating Cost'!K531:K576
    """
    delta = soln_pds_net_annual_iunits_reqd.diff().dropna()
    delta.name = 'New Annual Implementation Units (SOLUTION-PDS)'
    delta.index.name = 'Year'
    return delta

  def soln_pds_annual_breakout(self, soln_new_funits_per_year, soln_pds_new_annual_iunits_reqd):
    """Breakout of operating cost per year, including replacements.
       'Operating Cost'!B262:AV386
    """
    first_year = 2015
    last_year = self.ac.report_end_year
    last_column = 2060
    last_row = 2139
    breakout = pd.DataFrame(0, index=np.arange(first_year, last_row + 1),
        columns=np.arange(first_year, last_column + 1), dtype='float')
    breakout.index.name = 'Year'
    breakout.index = breakout.index.astype(int)

    for col in range(first_year, last_year + 1):
      # within the years of interest, assume replacement of worn out equipment.
      lifetime = self.ac.soln_lifetime_replacement
      while math.ceil(lifetime) < (last_year + 1 - col):
        lifetime += self.ac.soln_lifetime_replacement

      cost = self.ac.soln_var_oper_cost_per_funit + self.ac.soln_fuel_cost_per_funit
      total = soln_new_funits_per_year.loc[col].values[0] * cost * TERAWATT_TO_KILOWATT
      cost = self.ac.soln_fixed_oper_cost_per_iunit
      total += soln_pds_new_annual_iunits_reqd.loc[col].values[0] * cost * TERAWATT_TO_KILOWATT

      # for each year, add in operating costs for equipment purchased in that
      # starting year through the year where it wears out.
      for row in range(col, last_row + 1):
        remaining_lifetime = np.clip(lifetime, 0, 1)
        breakout.loc[row, col] = total * remaining_lifetime
        lifetime -= 1
        if lifetime <= 0:
          break
    return breakout
