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
    """Operating costs broken out per year for Solution-PDS
       This table calculates the contribution of each new set of SOLUTION
       implementation units installed over the lifetime of the units, but only
       for new or replacement units installed during our analysis period.
       Fixed and Variable costs that are constant or changing over time are included.
       'Operating Cost'!B262:AV386
    """
    return self._annual_breakout(new_funits_per_year=soln_new_funits_per_year,
        new_annual_iunits_reqd=soln_pds_new_annual_iunits_reqd,
        lifetime_replacement=self.ac.soln_lifetime_replacement,
        var_oper_cost_per_funit=self.ac.soln_var_oper_cost_per_funit,
        fuel_cost_per_funit=self.ac.soln_fuel_cost_per_funit,
        fixed_oper_cost_per_iunit=self.ac.soln_fixed_oper_cost_per_iunit)

  def conv_ref_new_annual_iunits_reqd(self, conv_ref_net_annual_iunits_reqd):
    """New implementation units required each year.
       'Operating Cost'!L531:L576
    """
    delta = conv_ref_net_annual_iunits_reqd.diff().dropna()
    delta.name = 'New Annual Implementation Units (CONVENTIONAL-REF)'
    delta.index.name = 'Year'
    return delta

  def conv_ref_annual_breakout(self, conv_new_funits_per_year, conv_ref_new_annual_iunits_reqd):
    """Operating costs broken out per year for Conventional-REF
       This table calculates the contribution of each new set of CONVENTIONAL
       implementation units installed over the lifetime of the units, but only
       for new or replacement units installed during our analysis period.
       Fixed and Variable costs that are constant or changing over time are included.
       'Operating Cost'!B399:AV523
    """
    return self._annual_breakout(new_funits_per_year=conv_new_funits_per_year,
        new_annual_iunits_reqd=conv_ref_new_annual_iunits_reqd,
        lifetime_replacement=self.ac.soln_lifetime_replacement,
        var_oper_cost_per_funit=self.ac.conv_var_oper_cost_per_funit,
        fuel_cost_per_funit=self.ac.conv_fuel_cost_per_funit,
        fixed_oper_cost_per_iunit=self.ac.conv_fixed_oper_cost_per_iunit)

  def _annual_breakout(self, new_funits_per_year, new_annual_iunits_reqd,
      lifetime_replacement, var_oper_cost_per_funit, fuel_cost_per_funit,
      fixed_oper_cost_per_iunit):
    """Breakout of operating cost per year, including replacements.
       Supplies calculations for:
       'Operating Cost'!B262:AV386 for soln_pds
    """
    first_year = 2015
    last_year = self.ac.report_end_year
    last_column = 2060
    last_row = 2139
    breakout = pd.DataFrame(0, index=np.arange(first_year, last_row + 1),
        columns=np.arange(first_year, last_column + 1), dtype='float')
    breakout.index.name = 'Year'
    breakout.index = breakout.index.astype(int)

    for year in range(first_year, last_year + 1):
      # within the years of interest, assume replacement of worn out equipment.
      lifetime = lifetime_replacement
      while math.ceil(lifetime) < (last_year + 1 - year):
        lifetime += lifetime_replacement

      cost = var_oper_cost_per_funit + fuel_cost_per_funit
      total = new_funits_per_year.loc[year] * cost * TERAWATT_TO_KILOWATT
      cost = fixed_oper_cost_per_iunit
      total += new_annual_iunits_reqd.loc[year] * cost * TERAWATT_TO_KILOWATT

      # for each year, add in operating costs for equipment purchased in that
      # starting year through the year where it wears out.
      for row in range(year, last_row + 1):
        remaining_lifetime = np.clip(lifetime, 0, 1)
        breakout.loc[row, year] = total * remaining_lifetime
        lifetime -= 1
        if lifetime <= 0:
          break
    return breakout

  def lifetime_cost_forecast(self, soln_ref_annual_world_first_cost,
      conv_ref_annual_world_first_cost, soln_pds_annual_world_first_cost,
      conv_ref_annual_breakout, soln_pds_annual_breakout):
    """Monetary fields:
       Marginal First Cost
       Marginal Operating Cost Savings
       Net Cash Flow
       Net Present Value
       'Operating Cost'!A126:E250
    """
    marginal_first_cost = soln_ref_annual_world_first_cost + conv_ref_annual_world_first_cost
    marginal_first_cost -= soln_pds_annual_world_first_cost
    first_row = soln_ref_annual_world_first_cost.first_valid_index()
    last_row = self.ac.report_end_year
    marginal_first_cost = marginal_first_cost.reindex(range(first_row, last_row + 1)).dropna()

    conv_ref_lifetime_cost = conv_ref_annual_breakout.sum(axis=1)
    soln_pds_lifetime_cost = soln_pds_annual_breakout.sum(axis=1)
    marginal_operating_cost_savings = conv_ref_lifetime_cost - soln_pds_lifetime_cost

    idx = marginal_operating_cost_savings.index
    # align index + zero-fill for net_cash_flow calculation
    marginal_first_cost = marginal_first_cost.reindex(idx).fillna(0)
    net_cash_flow = marginal_first_cost + marginal_operating_cost_savings

    npv = []
    for n in range(len(net_cash_flow.index)):
      l = [0] * (n+1) + [net_cash_flow.iloc[n]]
      npv.append(np.npv(rate=self.ac.npv_discount_rate, values=l))
    npv_series = pd.Series(npv, index=net_cash_flow.index)

    investment = pd.concat([marginal_first_cost, marginal_operating_cost_savings,
      net_cash_flow, npv_series], axis=1)
    investment.index.name = 'Year'
    investment.columns = ['Investment (Marginal First Cost)', 'Marginal Operating Cost Savings',
        'Net Cash Flow', 'NPV in $2014']

    first_row = investment.first_valid_index()
    last_row = 2139
    return investment.reindex(range(first_row, last_row + 1)).fillna(value=0)
