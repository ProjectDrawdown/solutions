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

  def soln_pds_annual_operating_cost(self, soln_pds_annual_breakout):
    """Total operating cost per year.
       'Operating Cost'!D19:D64
    """
    result = soln_pds_annual_breakout.sum(axis=1)
    result.name = 'soln_pds_annual_operating_cost'
    return result

  def soln_pds_cumulative_operating_cost(self, soln_pds_annual_operating_cost):
    """Cumulative operating cost.
       'Operating Cost'!E19:E64
    """
    result = soln_pds_annual_operating_cost.cumsum()
    result.name = 'soln_pds_cumulative_operating_cost'
    return result

  def conv_ref_annual_operating_cost(self, conv_ref_annual_breakout):
    """Total operating cost per year.
       'Operating Cost'!K19:K64
    """
    result = conv_ref_annual_breakout.sum(axis=1)
    result.name = 'conv_ref_annual_operating_cost'
    return result

  def conv_ref_cumulative_operating_cost(self, conv_ref_annual_operating_cost):
    """Cumulative operating cost.
       'Operating Cost'!L19:L64
    """
    result = conv_ref_annual_operating_cost.cumsum()
    result.name = 'conv_ref_cumulative_operating_cost'
    return result

  def marginal_annual_operating_cost(self, soln_pds_annual_operating_cost,
      conv_ref_annual_operating_cost):
    """Marginal operating cost, difference between soln_pds and conv_ref.
       'Operating Cost'!D69:D114
    """
    result = conv_ref_annual_operating_cost - soln_pds_annual_operating_cost
    result.name = 'marginal_annual_operating_cost'
    return result.dropna()

  def soln_new_funits_per_year(self, soln_net_annual_funits_adopted):
    """New functional units required each year.
       'Operating Cost'!F19:F64
    """
    growth = soln_net_annual_funits_adopted.diff().dropna()
    growth.name = 'soln_new_funits_per_year'
    first_year = soln_net_annual_funits_adopted.first_valid_index()
    growth = growth.append(soln_net_annual_funits_adopted.iloc[0, :])
    return growth.sort_index()

  def soln_pds_net_annual_iunits_reqd(self, soln_pds_tot_iunits_reqd, soln_ref_tot_iunits_reqd):
    """Total implementation units required each year.
       'Operating Cost'!I531:I576
    """
    result = soln_pds_tot_iunits_reqd - soln_ref_tot_iunits_reqd
    result.name = 'soln_pds_net_annual_iunits_reqd'
    return result

  def soln_pds_new_annual_iunits_reqd(self, soln_pds_net_annual_iunits_reqd):
    """New implementation units required each year.
       'Operating Cost'!K531:K576
    """
    delta = soln_pds_net_annual_iunits_reqd.diff().dropna()
    delta.name = 'soln_pds_new_annual_iunits_reqd'
    return delta

  def soln_pds_annual_breakout(self, soln_new_funits_per_year, soln_pds_new_annual_iunits_reqd):
    """Operating costs broken out per year for Solution-PDS
       This table calculates the contribution of each new set of SOLUTION
       implementation units installed over the lifetime of the units, but only
       for new or replacement units installed during our analysis period.
       Fixed and Variable costs that are constant or changing over time are included.
       'Operating Cost'!B262:AV386
    """
    result = self._annual_breakout(new_funits_per_year=soln_new_funits_per_year,
        new_annual_iunits_reqd=soln_pds_new_annual_iunits_reqd,
        lifetime_replacement=self.ac.soln_lifetime_replacement,
        var_oper_cost_per_funit=self.ac.soln_var_oper_cost_per_funit,
        fuel_cost_per_funit=self.ac.soln_fuel_cost_per_funit,
        fixed_oper_cost_per_iunit=self.ac.soln_fixed_oper_cost_per_iunit)
    result.name = 'soln_pds_annual_breakout'
    return result

  def conv_ref_new_annual_iunits_reqd(self, conv_ref_net_annual_iunits_reqd):
    """New implementation units required each year.
       'Operating Cost'!L531:L576
    """
    delta = conv_ref_net_annual_iunits_reqd.diff().dropna()
    delta.name = 'conv_ref_new_annual_iunits_reqd'
    return delta

  def conv_ref_annual_breakout(self, conv_new_funits_per_year, conv_ref_new_annual_iunits_reqd):
    """Operating costs broken out per year for Conventional-REF
       This table calculates the contribution of each new set of CONVENTIONAL
       implementation units installed over the lifetime of the units, but only
       for new or replacement units installed during our analysis period.
       Fixed and Variable costs that are constant or changing over time are included.
       'Operating Cost'!B399:AV523
    """
    result = self._annual_breakout(new_funits_per_year=conv_new_funits_per_year,
        new_annual_iunits_reqd=conv_ref_new_annual_iunits_reqd,
        lifetime_replacement=self.ac.soln_lifetime_replacement,
        var_oper_cost_per_funit=self.ac.conv_var_oper_cost_per_funit,
        fuel_cost_per_funit=self.ac.conv_fuel_cost_per_funit,
        fixed_oper_cost_per_iunit=self.ac.conv_fixed_oper_cost_per_iunit)
    result.name = 'conv_ref_annual_breakout'
    return result

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
    investment.name = 'lifetime_cost_forecast'
    investment.index.name = 'Year'
    investment.columns = ['Investment (Marginal First Cost)', 'Marginal Operating Cost Savings',
        'Net Cash Flow', 'NPV in $2014']

    first_row = investment.first_valid_index()
    last_row = 2139
    return investment.reindex(range(first_row, last_row + 1)).fillna(value=0)

  def soln_vs_conv_single_iunit_cashflow(self, single_iunit_purchase_year,
      soln_pds_install_cost_per_iunit, conv_ref_install_cost_per_iunit):
    """Estimate the cash flows for a single solution implementation unit while matching
       the output of that unit (in functional units) with the equivalent output of a
       conventional implementation unit. This takes into account:
         + changes in first cost due to learning
         + differences in functional unit output of the solution and conventional unit
         + differences in lifetime of the solution and implementation unit (scaling
           appropriately in each case).
       'Operating Cost'!I126:I250
    """
    first_year = 2015
    last_year = self.ac.report_end_year
    last_row = 2139
    result = pd.Series(0, index=np.arange(first_year, last_row + 1), dtype='float')
    result.index.name = 'Year'
    result.index = result.index.astype(int)
    result.name = 'soln_vs_conv_single_iunit_cashflow'

    soln_lifetime = self.ac.soln_lifetime_replacement
    conv_lifetime = 0
    conv_usage_mult = self.ac.soln_avg_annual_use / self.ac.conv_avg_annual_use
    for year in range(first_year, last_year + 1):
      cost = 0;
      if soln_lifetime <= 0:
        break
      if conv_lifetime <= 1:
        # A new conventional iunit is costed as many times as needed to cover the
        # lifetime and output of a solution iunit.
        conv_lifetime = self.ac.conv_lifetime_replacement
        soln_first_cost = (soln_lifetime - (year - first_year) + 0) / conv_lifetime
        cost_year = min(2060, year + (single_iunit_purchase_year - 2015))
        cost += conv_ref_install_cost_per_iunit[cost_year] * conv_usage_mult * min(1, soln_first_cost)

      if year == first_year:
        # account for the cost of the solution iunit in the first year.
        cost -= soln_pds_install_cost_per_iunit.loc[single_iunit_purchase_year]

      # Difference in fixed operating cost of conventional versus that of solution
      cost += (self.ac.conv_fixed_oper_cost_per_iunit * conv_usage_mult -
          self.ac.soln_fixed_oper_cost_per_iunit) * TERAWATT_TO_KILOWATT

      # Difference in variable operating cost of conventional versus that of solution
      conv_var_cost = self.ac.conv_var_oper_cost_per_funit + self.ac.conv_fuel_cost_per_funit
      soln_var_cost = self.ac.soln_var_oper_cost_per_funit + self.ac.soln_fuel_cost_per_funit
      cost += (self.ac.soln_avg_annual_use * conv_var_cost -
          self.ac.soln_avg_annual_use * soln_var_cost) * TERAWATT_TO_KILOWATT

      # account for a partial year at the end of the lifetime.
      cost *= min(1, soln_lifetime)
      result[year] = cost

      soln_lifetime -= 1
      conv_lifetime -= 1
    return result

  def soln_vs_conv_single_iunit_npv(self, single_iunit_purchase_year, soln_vs_conv_single_iunit_cashflow):
    """Net Present Value of single iunit cashflow.
       'Operating Cost'!J126:J250
    """
    npv = []
    offset = single_iunit_purchase_year - soln_vs_conv_single_iunit_cashflow.first_valid_index() + 1
    for n in range(len(soln_vs_conv_single_iunit_cashflow.index)):
      l = [0] * (n + offset) + [soln_vs_conv_single_iunit_cashflow.iloc[n]]
      npv.append(np.npv(rate=self.ac.npv_discount_rate, values=l))
    result = pd.Series(npv, index=soln_vs_conv_single_iunit_cashflow.index.copy())
    result.name = 'soln_vs_conv_single_iunit_npv'
    return result

  def soln_vs_conv_single_iunit_payback(self, soln_vs_conv_single_iunit_cashflow):
    """Whether the solution has paid off versus the conventional, for each year.
       'Operating Cost'!K126:K250
    """
    result = soln_vs_conv_single_iunit_cashflow.cumsum().apply(lambda x: 1 if x >= 0 else 0)
    result.name = 'soln_vs_conv_single_iunit_payback'
    return result

  def soln_vs_conv_single_iunit_payback_discounted(self, soln_vs_conv_single_iunit_npv):
    """Whether the solution NPV has paid off versus the conventional, for each year.
       'Operating Cost'!L126:L250
    """
    result = soln_vs_conv_single_iunit_npv.cumsum().apply(lambda x: 1 if x >= 0 else 0)
    result.name = 'soln_vs_conv_single_iunit_payback_discounted'
    return result

  def soln_only_single_iunit_cashflow(self, single_iunit_purchase_year, soln_pds_install_cost_per_iunit):
    """
       'Operating Cost'!M126:M250
    """
    first_year = 2015
    last_year = self.ac.report_end_year
    last_row = 2139
    result = pd.Series(0, index=np.arange(first_year, last_row + 1), dtype='float')
    result.index.name = 'Year'
    result.index = result.index.astype(int)
    result.name = 'soln_only_single_iunit_cashflow'

    soln_lifetime = self.ac.soln_lifetime_replacement
    conv_usage_mult = self.ac.soln_avg_annual_use / self.ac.conv_avg_annual_use
    for year in range(first_year, last_year + 1):
      cost = 0;
      if soln_lifetime <= 0:
        break

      if year == first_year:
        # account for the cost of the solution iunit in the first year.
        cost -= soln_pds_install_cost_per_iunit.loc[single_iunit_purchase_year]

      # Difference in fixed operating cost of conventional versus that of solution
      cost += (self.ac.conv_fixed_oper_cost_per_iunit * conv_usage_mult -
          self.ac.soln_fixed_oper_cost_per_iunit) * TERAWATT_TO_KILOWATT

      # Difference in variable operating cost of conventional versus that of solution
      conv_var_cost = self.ac.conv_var_oper_cost_per_funit + self.ac.conv_fuel_cost_per_funit
      soln_var_cost = self.ac.soln_var_oper_cost_per_funit + self.ac.soln_fuel_cost_per_funit
      cost += (self.ac.soln_avg_annual_use * conv_var_cost -
          self.ac.soln_avg_annual_use * soln_var_cost) * TERAWATT_TO_KILOWATT

      # account for a partial year at the end of the lifetime.
      cost *= min(1, soln_lifetime)
      result[year] = cost

      soln_lifetime -= 1
    return result

  def soln_only_single_iunit_npv(self, single_iunit_purchase_year, soln_only_single_iunit_cashflow):
    """Net Present Value of single iunit cashflow, looking only at costs of the Solution.
       'Operating Cost'!N126:N250
    """
    npv = []
    offset = single_iunit_purchase_year - soln_only_single_iunit_cashflow.first_valid_index() + 1
    for n in range(len(soln_only_single_iunit_cashflow.index)):
      l = [0] * (n + offset) + [soln_only_single_iunit_cashflow.iloc[n]]
      npv.append(np.npv(rate=self.ac.npv_discount_rate, values=l))
    result = pd.Series(npv, index=soln_only_single_iunit_cashflow.index.copy())
    result.name = 'soln_only_single_iunit_npv'
    return result

  def soln_only_single_iunit_payback(self, soln_only_single_iunit_cashflow):
    """Whether the solution has paid off, for each year.
       'Operating Cost'!O126:O250
    """
    result = soln_only_single_iunit_cashflow.cumsum().apply(lambda x: 1 if x >= 0 else 0)
    result.name = 'soln_only_single_iunit_payback'
    return result

  def soln_only_single_iunit_payback_discounted(self, soln_only_single_iunit_npv):
    """Whether the solution NPV has paid off, for each year.
       'Operating Cost'!P126:P250
    """
    result = soln_only_single_iunit_npv.cumsum().apply(lambda x: 1 if x >= 0 else 0)
    result.name = 'soln_only_single_iunit_payback_discounted'
    return result
