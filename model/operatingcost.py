"""Operating Cost module calculations."""

from functools import lru_cache
import math

import model.dd as dd
import numpy as np
import numpy_financial
import pandas as pd


class OperatingCost:
    """Implementation for the Operating Cost module.

      Arguments:
      ac: advanced_cost.py object, storing settings to control model operation.
      soln_net_annual_funits_adopted: funits adopted each year, per region
      soln_pds_tot_iunits_reqd: total implementation units
      soln_ref_tot_iunits_reqd: total implementation units
      conv_ref_annual_tot_iunits: total implementation units required, per year
      soln_pds_annual_world_first_cost: first cost, per year
      soln_ref_annual_world_first_cost: first cost, per year
      conv_ref_annual_world_first_cost: first cost, per year
      single_iunit_purchase_year: year to calculate single iunit first cost
      soln_pds_install_cost_per_iunit: cost per implementation unit
      conv_ref_install_cost_per_iunit: cost per implementation unit
      conversion_factor: conversion factor from iunits to a more natural
        monetary unit. In almost all cases a single conversion factor is used for
        both fixed and variable operating costs. Passing a single integer or float
        to conversion_factor will suffice. For those cases where a different factor
        is needed for fixed versus variable costs, passing a tuple of
        (<fixed_conv>, <var_conv>) can be used. At the time of this writing in 4/2019
        there is only one solution which does this (heatpumps).
    """

    def __init__(self, ac, soln_net_annual_funits_adopted,
                 soln_pds_tot_iunits_reqd,
                 soln_ref_tot_iunits_reqd,
                 conv_ref_annual_tot_iunits,
                 soln_pds_annual_world_first_cost,
                 soln_ref_annual_world_first_cost,
                 conv_ref_annual_world_first_cost,
                 single_iunit_purchase_year,
                 soln_pds_install_cost_per_iunit,
                 conv_ref_install_cost_per_iunit,
                 conversion_factor):
        self.ac = ac
        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted
        self.soln_pds_tot_iunits_reqd = soln_pds_tot_iunits_reqd
        self.soln_ref_tot_iunits_reqd = soln_ref_tot_iunits_reqd
        self.conv_ref_annual_tot_iunits = conv_ref_annual_tot_iunits
        self.soln_pds_annual_world_first_cost = soln_pds_annual_world_first_cost
        self.soln_ref_annual_world_first_cost = soln_ref_annual_world_first_cost
        self.conv_ref_annual_world_first_cost = conv_ref_annual_world_first_cost
        self.single_iunit_purchase_year = single_iunit_purchase_year
        self.soln_pds_install_cost_per_iunit = soln_pds_install_cost_per_iunit
        self.conv_ref_install_cost_per_iunit = conv_ref_install_cost_per_iunit
        try:
            self.conversion_factor_fom = conversion_factor[0]
            self.conversion_factor_vom = conversion_factor[1]
        except TypeError:
            self.conversion_factor_fom = conversion_factor
            self.conversion_factor_vom = conversion_factor


    @lru_cache()
    def soln_pds_annual_operating_cost(self):
        """Total operating cost per year.
           SolarPVUtil 'Operating Cost'!D19:D64
        """
        result = self.soln_pds_annual_breakout().sum(axis=1)
        result.name = 'soln_pds_annual_operating_cost'
        return result


    @lru_cache()
    def soln_pds_cumulative_operating_cost(self):
        """Cumulative operating cost.
           SolarPVUtil 'Operating Cost'!E19:E64
        """
        result = self.soln_pds_annual_operating_cost().cumsum()
        result.name = 'soln_pds_cumulative_operating_cost'
        return result


    @lru_cache()
    def conv_ref_annual_operating_cost(self):
        """Total operating cost per year.
           SolarPVUtil 'Operating Cost'!K19:K64
        """
        result = self.conv_ref_annual_breakout_core().sum(axis=1)
        result.name = 'conv_ref_annual_operating_cost'
        return result


    @lru_cache()
    def conv_ref_cumulative_operating_cost(self):
        """Cumulative operating cost.
           SolarPVUtil 'Operating Cost'!L19:L64
        """
        result = self.conv_ref_annual_operating_cost().cumsum()
        result.name = 'conv_ref_cumulative_operating_cost'
        return result


    @lru_cache()
    def marginal_annual_operating_cost(self):
        """Marginal operating cost, difference between soln_pds and conv_ref.
           SolarPVUtil 'Operating Cost'!D69:D114
        """
        result = self.conv_ref_annual_operating_cost() - self.soln_pds_annual_operating_cost()
        result.name = 'marginal_annual_operating_cost'
        return result.dropna()


    @lru_cache()
    def soln_pds_new_funits_per_year(self):
        """New functional units required each year.
           SolarPVUtil 'Operating Cost'!F19:F64
        """
        growth = self.soln_net_annual_funits_adopted.fillna(0.0).diff()
        growth.iloc[0] = self.soln_net_annual_funits_adopted.iloc[0]  # iloc[0] is NA after diff()
        growth.name = 'soln_pds_new_funits_per_year'
        return growth.sort_index()


    @lru_cache()
    def soln_pds_net_annual_iunits_reqd(self):
        """Total implementation units required each year.
           SolarPVUtil 'Operating Cost'!I531:I576
        """
        result = self.soln_pds_tot_iunits_reqd - self.soln_ref_tot_iunits_reqd
        result.name = 'soln_pds_net_annual_iunits_reqd'
        return result


    @lru_cache()
    def soln_pds_new_annual_iunits_reqd(self):
        """New implementation units required each year.
           SolarPVUtil 'Operating Cost'!K531:K576
        """
        delta = self.soln_pds_net_annual_iunits_reqd().diff()
        delta.iloc[0] = self.soln_pds_net_annual_iunits_reqd().iloc[0]  # iloc[0] is NA after diff()
        delta.name = 'soln_pds_new_annual_iunits_reqd'
        return delta


    @lru_cache()
    def soln_pds_annual_breakout(self):
        """Operating costs broken out per year for Solution-PDS
           This table calculates the contribution of each new set of SOLUTION
           implementation units installed over the lifetime of the units, but only
           for new or replacement units installed during our analysis period.
           Fixed and Variable costs that are constant or changing over time are included.
           SolarPVUtil 'Operating Cost'!B262:AV386
        """
        result = self._annual_breakout(
            new_funits_per_year=self.soln_pds_new_funits_per_year().loc[:, 'World'],
            new_annual_iunits_reqd=self.soln_pds_new_annual_iunits_reqd().loc[:, 'World'],
            lifetime_replacement=self.ac.soln_lifetime_replacement,
            var_oper_cost_per_funit=self.ac.soln_var_oper_cost_per_funit,
            fuel_cost_per_funit=self.ac.soln_fuel_cost_per_funit,
            fixed_oper_cost_per_iunit=self.ac.soln_fixed_oper_cost_per_iunit)
        result.name = 'soln_pds_annual_breakout'
        return result


    @lru_cache()
    def soln_pds_annual_breakout_core(self):
        """Returns soln_pds_annual_breakout for CORE_START_YEAR:CORE_END_YEAR"""
        return self.soln_pds_annual_breakout().loc[dd.CORE_START_YEAR:dd.CORE_END_YEAR]


    @lru_cache()
    def conv_ref_new_annual_iunits_reqd(self):
        """New implementation units required each year.
           SolarPVUtil 'Operating Cost'!L531:L576
        """
        delta = self.conv_ref_annual_tot_iunits.diff()
        delta.iloc[0] = self.conv_ref_annual_tot_iunits.iloc[0]  # iloc[0] is NA after diff()
        delta.name = 'conv_ref_new_annual_iunits_reqd'
        return delta


    @lru_cache()
    def conv_ref_annual_breakout(self):
        """Operating costs broken out per year for Conventional-REF
           This table calculates the contribution of each new set of CONVENTIONAL
           implementation units installed over the lifetime of the units, but only
           for new or replacement units installed during our analysis period.
           Fixed and Variable costs that are constant or changing over time are included.
           SolarPVUtil 'Operating Cost'!B399:AV523
        """
        result = self._annual_breakout(
            new_funits_per_year=self.soln_pds_new_funits_per_year().loc[:, 'World'],
            new_annual_iunits_reqd=self.conv_ref_new_annual_iunits_reqd().loc[:, 'World'],
            lifetime_replacement=self.ac.soln_lifetime_replacement,
            var_oper_cost_per_funit=self.ac.conv_var_oper_cost_per_funit,
            fuel_cost_per_funit=self.ac.conv_fuel_cost_per_funit,
            fixed_oper_cost_per_iunit=self.ac.conv_fixed_oper_cost_per_iunit)
        result.name = 'conv_ref_annual_breakout'
        return result


    @lru_cache()
    def conv_ref_annual_breakout_core(self):
        """Returns conv_ref_annual_breakout for CORE_START_YEAR:CORE_END_YEAR"""
        return self.conv_ref_annual_breakout().loc[dd.CORE_START_YEAR:dd.CORE_END_YEAR]


    def _annual_breakout(self, new_funits_per_year, new_annual_iunits_reqd,
                         lifetime_replacement, var_oper_cost_per_funit, fuel_cost_per_funit,
                         fixed_oper_cost_per_iunit):
        """Breakout of operating cost per year, including replacements.
           Supplies calculations for:
           SolarPVUtil 'Operating Cost'!B262:AV386 for soln_pds
           SolarPVUtil 'Operating Cost'!B399:AV523 for conv_ref
        """
        first_year = dd.CORE_START_YEAR
        last_year = self.ac.report_end_year
        last_column = dd.CORE_END_YEAR
        last_row = 2139
        breakout = pd.DataFrame(0, index=np.arange(first_year, last_row + 1),
                                columns=np.arange(first_year, last_column + 1), dtype='float')
        breakout.index.name = 'Year'
        breakout.index = breakout.index.astype(int)

        # if there are no operating costs we return a table of 0s
        if not self.ac.has_var_costs and not fixed_oper_cost_per_iunit:
            return breakout

        for year in range(first_year, last_year + 1):
            # within the years of interest, assume replacement of worn out equipment.
            lifetime = lifetime_replacement
            assert lifetime_replacement != 0, 'Cannot have a lifetime replacement of 0 and non-zero operating costs'
            while math.ceil(lifetime) < (last_year + 1 - year):
                lifetime += lifetime_replacement

            cost = var_oper_cost_per_funit + fuel_cost_per_funit if self.ac.has_var_costs else 0
            total = new_funits_per_year.loc[year] * cost * self.conversion_factor_vom
            cost = fixed_oper_cost_per_iunit
            total += new_annual_iunits_reqd.loc[year] * cost * self.conversion_factor_fom

            # for each year, add in operating costs for equipment purchased in that
            # starting year through the year where it wears out.
            for row in range(year, last_row + 1):
                remaining_lifetime = np.clip(lifetime, 0, 1)
                val = total * remaining_lifetime
                breakout.loc[row, year] = val if math.fabs(val) > 0.01 else 0.0
                lifetime -= 1
                if lifetime <= 0:
                    break
        return breakout


    @lru_cache()
    def soln_marginal_first_cost(self):
        """Marginal First Cost.
           SolarPVUtil 'Operating Cost'!B126:B250
        """
        result = self.soln_ref_annual_world_first_cost + self.conv_ref_annual_world_first_cost
        result = result - self.soln_pds_annual_world_first_cost
        index = pd.RangeIndex(result.first_valid_index(), 2140)
        result = result.reindex(index=index)
        # Excel returns 0.0 for years after self.ac.report_end_year
        result.loc[self.ac.report_end_year + 1:] = 0.0
        result.name = 'soln_marginal_first_cost'
        return result


    @lru_cache()
    def soln_marginal_operating_cost_savings(self):
        """Marginal First Cost.
           SolarPVUtil 'Operating Cost'!C126:C250
        """
        conv_ref_lifetime_cost = self.conv_ref_annual_breakout().sum(axis=1)
        soln_pds_lifetime_cost = self.soln_pds_annual_breakout().sum(axis=1)
        result = conv_ref_lifetime_cost - soln_pds_lifetime_cost
        index = pd.RangeIndex(result.first_valid_index(), 2140)
        result = result.reindex(index)
        result.name = 'soln_marginal_operating_cost_savings'
        return result


    @lru_cache()
    def soln_net_cash_flow(self):
        """Marginal First Cost.
           SolarPVUtil 'Operating Cost'!D126:D250
        """
        result = self.soln_marginal_first_cost() + self.soln_marginal_operating_cost_savings()
        index = pd.RangeIndex(result.first_valid_index(), 2140)
        result = result.reindex(index)
        result.name = 'soln_net_cash_flow'
        return result


    @lru_cache()
    def soln_net_present_value(self):
        """Marginal First Cost.
           SolarPVUtil 'Operating Cost'!E126:E250
        """
        npv = []
        net_cash_flow = self.soln_net_cash_flow()
        for n in range(len(net_cash_flow.index)):
            l = [0] * (n + 1) + [net_cash_flow.iloc[n]]
            npv.append(numpy_financial.npv(rate=self.ac.npv_discount_rate, values=l))
        result = pd.Series(npv, index=net_cash_flow.index)
        result.name = 'soln_net_present_value'
        return result


    @lru_cache()
    def soln_vs_conv_single_iunit_cashflow(self):
        """Estimate the cash flows for a single solution implementation unit while matching
           the output of that unit (in functional units) with the equivalent output of a
           conventional implementation unit. This takes into account:
             + changes in first cost due to learning
             + differences in functional unit output of the solution and conventional unit
             + differences in lifetime of the solution and implementation unit (scaling
               appropriately in each case).
           SolarPVUtil 'Operating Cost'!I126:I250
        """
        first_year = dd.CORE_START_YEAR
        last_year = max(dd.CORE_END_YEAR,
                dd.CORE_START_YEAR + self.ac.soln_lifetime_replacement_rounded)
        last_row = 2139
        result = pd.Series(0, index=np.arange(first_year, last_row + 1), dtype='float')
        result.index.name = 'Year'
        result.index = result.index.astype(int)
        result.name = 'soln_vs_conv_single_iunit_cashflow'

        soln_lifetime = self.ac.soln_lifetime_replacement
        if self.ac.soln_avg_annual_use is not None and self.ac.conv_avg_annual_use is not None:
            conv_usage_mult = self.ac.soln_avg_annual_use / self.ac.conv_avg_annual_use  # RRS
        else:
            conv_usage_mult = 1  # LAND

        for year in range(first_year, last_year + 1):
            cost = 0
            if soln_lifetime <= 0:
                break
            remainder = (year - (first_year - 1)) % self.ac.conv_lifetime_replacement
            if remainder <= 1 and remainder > 0:
                # A new conventional iunit is costed as many times as needed to cover the
                # lifetime and output of a solution iunit.
                soln_first_cost = (self.ac.soln_lifetime_replacement - (year - first_year) + 0)
                soln_first_cost /= self.ac.conv_lifetime_replacement
                cost_year = min(dd.CORE_END_YEAR,
                                year + (self.single_iunit_purchase_year - dd.CORE_START_YEAR))
                cost += (self.conv_ref_install_cost_per_iunit[cost_year] * conv_usage_mult *
                         min(1, soln_first_cost))

            if year == first_year:
                # account for the cost of the solution iunit in the first year.
                cost -= self.soln_pds_install_cost_per_iunit.loc[self.single_iunit_purchase_year]

            # Difference in fixed operating cost of conventional versus that of solution
            cost += (self.ac.conv_fixed_oper_cost_per_iunit * conv_usage_mult -
                     self.ac.soln_fixed_oper_cost_per_iunit) * self.conversion_factor_fom

            # Difference in variable operating cost of conventional versus that of solution
            if self.ac.has_var_costs:
                conv_var_cost = self.ac.conv_var_oper_cost_per_funit + self.ac.conv_fuel_cost_per_funit
                soln_var_cost = self.ac.soln_var_oper_cost_per_funit + self.ac.soln_fuel_cost_per_funit
                cost += (
                            self.ac.soln_avg_annual_use * conv_var_cost - self.ac.soln_avg_annual_use * soln_var_cost) \
                        * self.conversion_factor_vom

            # account for a partial year at the end of the lifetime.
            cost *= min(1, soln_lifetime)
            result[year] = cost if math.fabs(cost) > 0.01 else 0.0

            soln_lifetime -= 1

        return result



    @lru_cache()
    def soln_vs_conv_single_iunit_npv(self):
        """Net Present Value of single iunit cashflow.
           SolarPVUtil 'Operating Cost'!J126:J250
        """
        npv = []
        svcsic = self.soln_vs_conv_single_iunit_cashflow()
        offset = self.single_iunit_purchase_year - svcsic.first_valid_index() + 1
        for n in range(len(svcsic.index)):
            l = [0] * (n + offset) + [svcsic.iloc[n]]
            npv.append(numpy_financial.npv(rate=self.ac.npv_discount_rate, values=l))
        result = pd.Series(npv, index=svcsic.index.copy())
        result.name = 'soln_vs_conv_single_iunit_npv'
        return result



    @lru_cache()
    def soln_vs_conv_single_iunit_payback(self):
        """Whether the solution has paid off versus the conventional, for each year.
           SolarPVUtil 'Operating Cost'!K126:K250
        """
        result = self.soln_vs_conv_single_iunit_cashflow().cumsum().apply(lambda x: 1 if x >= 0 else 0)
        result.name = 'soln_vs_conv_single_iunit_payback'
        return result



    @lru_cache()
    def soln_vs_conv_single_iunit_payback_discounted(self):
        """Whether the solution NPV has paid off versus the conventional, for each year.
           SolarPVUtil 'Operating Cost'!L126:L250
        """
        result = self.soln_vs_conv_single_iunit_npv().cumsum().apply(lambda x: 1 if x >= 0 else 0)
        result.name = 'soln_vs_conv_single_iunit_payback_discounted'
        return result



    @lru_cache()
    def soln_only_single_iunit_cashflow(self):
        """
           SolarPVUtil 'Operating Cost'!M126:M250
        """
        first_year = dd.CORE_START_YEAR
        last_year = max(dd.CORE_END_YEAR,
                dd.CORE_START_YEAR + self.ac.soln_lifetime_replacement_rounded)
        last_row = 2139
        result = pd.Series(0, index=np.arange(first_year, last_row + 1), dtype='float')
        result.index.name = 'Year'
        result.index = result.index.astype(int)
        result.name = 'soln_only_single_iunit_cashflow'

        soln_lifetime = self.ac.soln_lifetime_replacement
        if self.ac.soln_avg_annual_use is not None and self.ac.conv_avg_annual_use is not None:
            conv_usage_mult = self.ac.soln_avg_annual_use / self.ac.conv_avg_annual_use  # RRS
        else:
            conv_usage_mult = 1  # LAND

        for year in range(first_year, last_year + 1):
            cost = 0
            if soln_lifetime <= 0:
                break

            if year == first_year:
                # account for the cost of the solution iunit in the first year.
                cost -= self.soln_pds_install_cost_per_iunit.loc[self.single_iunit_purchase_year]

            # Difference in fixed operating cost of conventional versus that of solution
            cost += (self.ac.conv_fixed_oper_cost_per_iunit * conv_usage_mult -
                     self.ac.soln_fixed_oper_cost_per_iunit) * self.conversion_factor_fom

            # Difference in variable operating cost of conventional versus that of solution
            if self.ac.has_var_costs:
                conv_var_cost = self.ac.conv_var_oper_cost_per_funit + self.ac.conv_fuel_cost_per_funit
                soln_var_cost = self.ac.soln_var_oper_cost_per_funit + self.ac.soln_fuel_cost_per_funit
                cost += (self.ac.soln_avg_annual_use * conv_var_cost -
                         self.ac.soln_avg_annual_use * soln_var_cost) * self.conversion_factor_vom

            # account for a partial year at the end of the lifetime.
            cost *= min(1, soln_lifetime)
            result[year] = cost if math.fabs(cost) > 0.01 else 0.0

            soln_lifetime -= 1
        return result



    @lru_cache()
    def soln_only_single_iunit_npv(self):
        """Net Present Value of single iunit cashflow, looking only at costs of the Solution.
           SolarPVUtil 'Operating Cost'!N126:N250
        """
        npv = []
        sosic = self.soln_only_single_iunit_cashflow()
        offset = self.single_iunit_purchase_year - sosic.first_valid_index() + 1
        for n in range(len(sosic.index)):
            l = [0] * (n + offset) + [sosic.iloc[n]]
            npv.append(numpy_financial.npv(rate=self.ac.npv_discount_rate, values=l))
        result = pd.Series(npv, index=sosic.index.copy())
        result.name = 'soln_only_single_iunit_npv'
        return result



    @lru_cache()
    def soln_only_single_iunit_payback(self):
        """Whether the solution has paid off, for each year.
           SolarPVUtil 'Operating Cost'!O126:O250
        """
        result = self.soln_only_single_iunit_cashflow().cumsum().apply(lambda x: 1 if x >= 0 else 0)
        result.name = 'soln_only_single_iunit_payback'
        return result



    @lru_cache()
    def soln_only_single_iunit_payback_discounted(self):
        """Whether the solution NPV has paid off, for each year.
           SolarPVUtil 'Operating Cost'!P126:P250
        """
        result = self.soln_only_single_iunit_npv().cumsum().apply(lambda x: 1 if x >= 0 else 0)
        result.name = 'soln_only_single_iunit_payback_discounted'
        return result
