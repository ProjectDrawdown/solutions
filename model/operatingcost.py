"""Operating Cost module calculations."""  # by Denton Gentry
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import math  # by Denton Gentry
# by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry

# by Denton Gentry
CORE_START_YEAR = 2015  # by Denton Gentry
CORE_END_YEAR = 2060  # by Denton Gentry


# by Denton Gentry
class OperatingCost:  # by Denton Gentry
    """Implementation for the Operating Cost module.  # by Denton Gentry
    # by Denton Gentry
      Arguments:  # by Denton Gentry
      ac: advanced_cost.py object, storing settings to control model operation.  # by Denton Gentry
      soln_net_annual_funits_adopted: funits adopted each year, per region  # by Denton Gentry
      soln_pds_tot_iunits_reqd: total implementation units  # by Denton Gentry
      soln_ref_tot_iunits_reqd: total implementation units  # by Denton Gentry
      conv_ref_annual_tot_iunits: total implementation units required, per year  # by Denton Gentry
      soln_pds_annual_world_first_cost: first cost, per year  # by Denton Gentry
      soln_ref_annual_world_first_cost: first cost, per year  # by Denton Gentry
      conv_ref_annual_world_first_cost: first cost, per year  # by Denton Gentry
      single_iunit_purchase_year: year to calculate single iunit first cost  # by Denton Gentry
      soln_pds_install_cost_per_iunit: cost per implementation unit  # by Denton Gentry
      conv_ref_install_cost_per_iunit: cost per implementation unit  # by Denton Gentry
      conversion_factor: conversion factor from iunits to a more natural  # by Denton Gentry
        monetary unit. In almost all cases a single conversion factor is used for  # by Denton Gentry
        both fixed and variable operating costs. Passing a single integer or float  # by Denton Gentry
        to conversion_factor will suffice. For those cases where a different factor  # by Denton Gentry
        is needed for fixed versus variable costs, passing a tuple of  # by Denton Gentry
        (<fixed_conv>, <var_conv>) can be used. At the time of this writing in 4/2019  # by Denton Gentry
        there is only one solution which does this (heatpumps).  # by Denton Gentry
    """  # by Denton Gentry

    def __init__(self, ac, soln_net_annual_funits_adopted,  # by Denton Gentry
                 soln_pds_tot_iunits_reqd,  # by Denton Gentry
                 soln_ref_tot_iunits_reqd,  # by Denton Gentry
                 conv_ref_annual_tot_iunits,  # by Denton Gentry
                 soln_pds_annual_world_first_cost,  # by Denton Gentry
                 soln_ref_annual_world_first_cost,  # by Denton Gentry
                 conv_ref_annual_world_first_cost,  # by Denton Gentry
                 single_iunit_purchase_year,  # by Denton Gentry
                 soln_pds_install_cost_per_iunit,  # by Denton Gentry
                 conv_ref_install_cost_per_iunit,
                 conversion_factor):  # by Denton Gentry
        self.ac = ac  # by Denton Gentry
        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted  # by Denton Gentry
        self.soln_pds_tot_iunits_reqd = soln_pds_tot_iunits_reqd  # by Denton Gentry
        self.soln_ref_tot_iunits_reqd = soln_ref_tot_iunits_reqd  # by Denton Gentry
        self.conv_ref_annual_tot_iunits = conv_ref_annual_tot_iunits  # by Denton Gentry
        self.soln_pds_annual_world_first_cost = soln_pds_annual_world_first_cost  # by Denton Gentry
        self.soln_ref_annual_world_first_cost = soln_ref_annual_world_first_cost  # by Denton Gentry
        self.conv_ref_annual_world_first_cost = conv_ref_annual_world_first_cost  # by Denton Gentry
        self.single_iunit_purchase_year = single_iunit_purchase_year  # by Denton Gentry
        self.soln_pds_install_cost_per_iunit = soln_pds_install_cost_per_iunit  # by Denton Gentry
        self.conv_ref_install_cost_per_iunit = conv_ref_install_cost_per_iunit  # by Denton Gentry
        try:  # by Denton Gentry
            self.conversion_factor_fom = conversion_factor[0]  # by Denton Gentry
            self.conversion_factor_vom = conversion_factor[1]  # by Denton Gentry
        except TypeError:  # by Denton Gentry
            self.conversion_factor_fom = conversion_factor  # by Denton Gentry
            self.conversion_factor_vom = conversion_factor  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_annual_operating_cost(self):  # by Denton Gentry
        """Total operating cost per year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!D19:D64  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_annual_breakout().sum(axis=1)  # by Denton Gentry
        result.name = 'soln_pds_annual_operating_cost'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_cumulative_operating_cost(self):  # by Denton Gentry
        """Cumulative operating cost.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!E19:E64  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_annual_operating_cost().cumsum()  # by Denton Gentry
        result.name = 'soln_pds_cumulative_operating_cost'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_annual_operating_cost(self):  # by Denton Gentry
        """Total operating cost per year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!K19:K64  # by Denton Gentry
        """  # by Denton Gentry
        result = self.conv_ref_annual_breakout_core().sum(axis=1)  # by Denton Gentry
        result.name = 'conv_ref_annual_operating_cost'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_cumulative_operating_cost(self):  # by Denton Gentry
        """Cumulative operating cost.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!L19:L64  # by Denton Gentry
        """  # by Denton Gentry
        result = self.conv_ref_annual_operating_cost().cumsum()  # by Denton Gentry
        result.name = 'conv_ref_cumulative_operating_cost'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def marginal_annual_operating_cost(self):  # by Denton Gentry
        """Marginal operating cost, difference between soln_pds and conv_ref.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!D69:D114  # by Denton Gentry
        """  # by Denton Gentry
        result = self.conv_ref_annual_operating_cost() - self.soln_pds_annual_operating_cost()  # by Denton Gentry
        result.name = 'marginal_annual_operating_cost'  # by Denton Gentry
        return result.dropna()  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_new_funits_per_year(self):  # by Denton Gentry
        """New functional units required each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!F19:F64  # by Denton Gentry
        """  # by Denton Gentry
        growth = self.soln_net_annual_funits_adopted.fillna(0.0).diff()  # by Denton Gentry
        growth.iloc[0] = self.soln_net_annual_funits_adopted.iloc[0]  # iloc[0] is NA after diff()  # by Denton Gentry
        growth.name = 'soln_pds_new_funits_per_year'  # by Denton Gentry
        return growth.sort_index()  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_net_annual_iunits_reqd(self):  # by Denton Gentry
        """Total implementation units required each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!I531:I576  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_tot_iunits_reqd - self.soln_ref_tot_iunits_reqd  # by Denton Gentry
        result.name = 'soln_pds_net_annual_iunits_reqd'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_new_annual_iunits_reqd(self):  # by Denton Gentry
        """New implementation units required each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!K531:K576  # by Denton Gentry
        """  # by Denton Gentry
        delta = self.soln_pds_net_annual_iunits_reqd().diff()  # by Denton Gentry
        delta.iloc[0] = self.soln_pds_net_annual_iunits_reqd().iloc[0]  # iloc[0] is NA after diff()  # by Denton Gentry
        delta.name = 'soln_pds_new_annual_iunits_reqd'  # by Denton Gentry
        return delta  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_annual_breakout(self):  # by Denton Gentry
        """Operating costs broken out per year for Solution-PDS  # by Denton Gentry
           This table calculates the contribution of each new set of SOLUTION  # by Denton Gentry
           implementation units installed over the lifetime of the units, but only  # by Denton Gentry
           for new or replacement units installed during our analysis period.  # by Denton Gentry
           Fixed and Variable costs that are constant or changing over time are included.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!B262:AV386  # by Denton Gentry
        """  # by Denton Gentry
        result = self._annual_breakout(  # by Denton Gentry
            new_funits_per_year=self.soln_pds_new_funits_per_year().loc[:, 'World'],  # by Denton Gentry
            new_annual_iunits_reqd=self.soln_pds_new_annual_iunits_reqd().loc[:, 'World'],  # by Denton Gentry
            lifetime_replacement=self.ac.soln_lifetime_replacement,  # by Denton Gentry
            var_oper_cost_per_funit=self.ac.soln_var_oper_cost_per_funit,  # by Denton Gentry
            fuel_cost_per_funit=self.ac.soln_fuel_cost_per_funit,  # by Denton Gentry
            fixed_oper_cost_per_iunit=self.ac.soln_fixed_oper_cost_per_iunit)  # by Denton Gentry
        result.name = 'soln_pds_annual_breakout'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_annual_breakout_core(self):  # by Denton Gentry
        """Returns soln_pds_annual_breakout for CORE_START_YEAR:CORE_END_YEAR"""  # by Denton Gentry
        return self.soln_pds_annual_breakout().loc[CORE_START_YEAR:CORE_END_YEAR]  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_new_annual_iunits_reqd(self):  # by Denton Gentry
        """New implementation units required each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!L531:L576  # by Denton Gentry
        """  # by Denton Gentry
        delta = self.conv_ref_annual_tot_iunits.diff()  # by Denton Gentry
        delta.iloc[0] = self.conv_ref_annual_tot_iunits.iloc[0]  # iloc[0] is NA after diff()  # by Denton Gentry
        delta.name = 'conv_ref_new_annual_iunits_reqd'  # by Denton Gentry
        return delta  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_annual_breakout(self):  # by Denton Gentry
        """Operating costs broken out per year for Conventional-REF  # by Denton Gentry
           This table calculates the contribution of each new set of CONVENTIONAL  # by Denton Gentry
           implementation units installed over the lifetime of the units, but only  # by Denton Gentry
           for new or replacement units installed during our analysis period.  # by Denton Gentry
           Fixed and Variable costs that are constant or changing over time are included.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!B399:AV523  # by Denton Gentry
        """  # by Denton Gentry
        result = self._annual_breakout(  # by Denton Gentry
            new_funits_per_year=self.soln_pds_new_funits_per_year().loc[:, 'World'],  # by Denton Gentry
            new_annual_iunits_reqd=self.conv_ref_new_annual_iunits_reqd().loc[:, 'World'],  # by Denton Gentry
            lifetime_replacement=self.ac.soln_lifetime_replacement,  # by Denton Gentry
            var_oper_cost_per_funit=self.ac.conv_var_oper_cost_per_funit,  # by Denton Gentry
            fuel_cost_per_funit=self.ac.conv_fuel_cost_per_funit,  # by Denton Gentry
            fixed_oper_cost_per_iunit=self.ac.conv_fixed_oper_cost_per_iunit)  # by Denton Gentry
        result.name = 'conv_ref_annual_breakout'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_annual_breakout_core(self):  # by Denton Gentry
        """Returns conv_ref_annual_breakout for CORE_START_YEAR:CORE_END_YEAR"""  # by Denton Gentry
        return self.conv_ref_annual_breakout().loc[CORE_START_YEAR:CORE_END_YEAR]  # by Denton Gentry

    # by Denton Gentry
    def _annual_breakout(self, new_funits_per_year, new_annual_iunits_reqd,  # by Denton Gentry
                         lifetime_replacement, var_oper_cost_per_funit, fuel_cost_per_funit,  # by Denton Gentry
                         fixed_oper_cost_per_iunit):  # by Denton Gentry
        """Breakout of operating cost per year, including replacements.  # by Denton Gentry
           Supplies calculations for:  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!B262:AV386 for soln_pds  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!B399:AV523 for conv_ref  # by Denton Gentry
        """  # by Denton Gentry
        first_year = CORE_START_YEAR  # by Denton Gentry
        last_year = self.ac.report_end_year  # by Denton Gentry
        last_column = CORE_END_YEAR  # by Denton Gentry
        last_row = 2139  # by Denton Gentry
        breakout = pd.DataFrame(0, index=np.arange(first_year, last_row + 1),  # by Denton Gentry
                                columns=np.arange(first_year, last_column + 1), dtype='float')  # by Denton Gentry
        breakout.index.name = 'Year'  # by Denton Gentry
        breakout.index = breakout.index.astype(int)  # by Denton Gentry
        # by Denton Gentry
        # if there are no operating costs we return a table of 0s
        if not self.ac.has_var_costs and not fixed_oper_cost_per_iunit:
            return breakout

        for year in range(first_year, last_year + 1):  # by Denton Gentry
            # within the years of interest, assume replacement of worn out equipment.  # by Denton Gentry
            lifetime = lifetime_replacement  # by Denton Gentry
            assert lifetime_replacement != 0, 'Cannot have a lifetime replacement of 0 and non-zero operating costs'
            while math.ceil(lifetime) < (last_year + 1 - year):  # by Denton Gentry
                lifetime += lifetime_replacement  # by Denton Gentry
            # by Denton Gentry
            cost = var_oper_cost_per_funit + fuel_cost_per_funit if self.ac.has_var_costs else 0
            total = new_funits_per_year.loc[year] * cost * self.conversion_factor_vom  # by Denton Gentry
            cost = fixed_oper_cost_per_iunit  # by Denton Gentry
            total += new_annual_iunits_reqd.loc[year] * cost * self.conversion_factor_fom  # by Denton Gentry
            # by Denton Gentry
            # for each year, add in operating costs for equipment purchased in that  # by Denton Gentry
            # starting year through the year where it wears out.  # by Denton Gentry
            for row in range(year, last_row + 1):  # by Denton Gentry
                remaining_lifetime = np.clip(lifetime, 0, 1)  # by Denton Gentry
                val = total * remaining_lifetime  # by Denton Gentry
                breakout.loc[row, year] = val if math.fabs(val) > 0.01 else 0.0  # by Denton Gentry
                lifetime -= 1  # by Denton Gentry
                if lifetime <= 0:  # by Denton Gentry
                    break  # by Denton Gentry
        return breakout  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_marginal_first_cost(self):  # by Denton Gentry
        """Marginal First Cost.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!B126:B250  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_ref_annual_world_first_cost + self.conv_ref_annual_world_first_cost  # by Denton Gentry
        result = result - self.soln_pds_annual_world_first_cost  # by Denton Gentry
        index = pd.RangeIndex(result.first_valid_index(), 2140)  # by Denton Gentry
        result = result.reindex(index=index)  # by Denton Gentry
        # Excel returns 0.0 for years after self.ac.report_end_year  # by Denton Gentry
        result.loc[self.ac.report_end_year + 1:] = 0.0  # by Denton Gentry
        result.name = 'soln_marginal_first_cost'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_marginal_operating_cost_savings(self):  # by Denton Gentry
        """Marginal First Cost.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!C126:C250  # by Denton Gentry
        """  # by Denton Gentry
        conv_ref_lifetime_cost = self.conv_ref_annual_breakout().sum(axis=1)  # by Denton Gentry
        soln_pds_lifetime_cost = self.soln_pds_annual_breakout().sum(axis=1)  # by Denton Gentry
        result = conv_ref_lifetime_cost - soln_pds_lifetime_cost  # by Denton Gentry
        index = pd.RangeIndex(result.first_valid_index(), 2140)  # by Denton Gentry
        result = result.reindex(index)  # by Denton Gentry
        result.name = 'soln_marginal_operating_cost_savings'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_net_cash_flow(self):  # by Denton Gentry
        """Marginal First Cost.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!D126:D250  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_marginal_first_cost() + self.soln_marginal_operating_cost_savings()  # by Denton Gentry
        index = pd.RangeIndex(result.first_valid_index(), 2140)  # by Denton Gentry
        result = result.reindex(index)  # by Denton Gentry
        result.name = 'soln_net_cash_flow'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_net_present_value(self):  # by Denton Gentry
        """Marginal First Cost.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!E126:E250  # by Denton Gentry
        """  # by Denton Gentry
        npv = []  # by Denton Gentry
        net_cash_flow = self.soln_net_cash_flow()  # by Denton Gentry
        for n in range(len(net_cash_flow.index)):  # by Denton Gentry
            l = [0] * (n + 1) + [net_cash_flow.iloc[n]]  # by Denton Gentry
            npv.append(np.npv(rate=self.ac.npv_discount_rate, values=l))  # by Denton Gentry
        result = pd.Series(npv, index=net_cash_flow.index)  # by Denton Gentry
        result.name = 'soln_net_present_value'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_vs_conv_single_iunit_cashflow(self):  # by Denton Gentry
        """Estimate the cash flows for a single solution implementation unit while matching  # by Denton Gentry
           the output of that unit (in functional units) with the equivalent output of a  # by Denton Gentry
           conventional implementation unit. This takes into account:  # by Denton Gentry
             + changes in first cost due to learning  # by Denton Gentry
             + differences in functional unit output of the solution and conventional unit  # by Denton Gentry
             + differences in lifetime of the solution and implementation unit (scaling  # by Denton Gentry
               appropriately in each case).  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!I126:I250  # by Denton Gentry
        """  # by Denton Gentry
        first_year = CORE_START_YEAR  # by Denton Gentry
        last_year = max(CORE_END_YEAR, CORE_START_YEAR + self.ac.soln_lifetime_replacement_rounded)  # by Denton Gentry
        last_row = 2139  # by Denton Gentry
        result = pd.Series(0, index=np.arange(first_year, last_row + 1), dtype='float')  # by Denton Gentry
        result.index.name = 'Year'  # by Denton Gentry
        result.index = result.index.astype(int)  # by Denton Gentry
        result.name = 'soln_vs_conv_single_iunit_cashflow'  # by Denton Gentry
        # by Denton Gentry
        soln_lifetime = self.ac.soln_lifetime_replacement  # by Denton Gentry
        if self.ac.soln_avg_annual_use is not None and self.ac.conv_avg_annual_use is not None:
            conv_usage_mult = self.ac.soln_avg_annual_use / self.ac.conv_avg_annual_use  # RRS
        else:
            conv_usage_mult = 1  # LAND

        for year in range(first_year, last_year + 1):  # by Denton Gentry
            cost = 0
            if soln_lifetime <= 0:  # by Denton Gentry
                break  # by Denton Gentry
            remainder = (year - (first_year - 1)) % self.ac.conv_lifetime_replacement  # by Denton Gentry
            if remainder <= 1 and remainder > 0:  # by Denton Gentry
                # A new conventional iunit is costed as many times as needed to cover the  # by Denton Gentry
                # lifetime and output of a solution iunit.  # by Denton Gentry
                soln_first_cost = (self.ac.soln_lifetime_replacement - (year - first_year) + 0)  # by Denton Gentry
                soln_first_cost /= self.ac.conv_lifetime_replacement  # by Denton Gentry
                cost_year = min(CORE_END_YEAR,
                                year + (self.single_iunit_purchase_year - CORE_START_YEAR))  # by Denton Gentry
                cost += (self.conv_ref_install_cost_per_iunit[cost_year] * conv_usage_mult *  # by Denton Gentry
                         min(1, soln_first_cost))  # by Denton Gentry
            # by Denton Gentry
            if year == first_year:  # by Denton Gentry
                # account for the cost of the solution iunit in the first year.  # by Denton Gentry
                cost -= self.soln_pds_install_cost_per_iunit.loc[self.single_iunit_purchase_year]  # by Denton Gentry
            # by Denton Gentry
            # Difference in fixed operating cost of conventional versus that of solution  # by Denton Gentry
            cost += (self.ac.conv_fixed_oper_cost_per_iunit * conv_usage_mult -  # by Denton Gentry
                     self.ac.soln_fixed_oper_cost_per_iunit) * self.conversion_factor_fom  # by Denton Gentry
            # by Denton Gentry
            # Difference in variable operating cost of conventional versus that of solution  # by Denton Gentry
            if self.ac.has_var_costs:
                conv_var_cost = self.ac.conv_var_oper_cost_per_funit + self.ac.conv_fuel_cost_per_funit
                soln_var_cost = self.ac.soln_var_oper_cost_per_funit + self.ac.soln_fuel_cost_per_funit
                cost += (
                            self.ac.soln_avg_annual_use * conv_var_cost - self.ac.soln_avg_annual_use * soln_var_cost) \
                        * self.conversion_factor_vom  # by Denton Gentry
            # by Denton Gentry
            # account for a partial year at the end of the lifetime.  # by Denton Gentry
            cost *= min(1, soln_lifetime)  # by Denton Gentry
            result[year] = cost if math.fabs(cost) > 0.01 else 0.0  # by Denton Gentry
            # by Denton Gentry
            soln_lifetime -= 1  # by Denton Gentry

        return result  # by Denton Gentry


    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_vs_conv_single_iunit_npv(self):  # by Denton Gentry
        """Net Present Value of single iunit cashflow.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!J126:J250  # by Denton Gentry
        """  # by Denton Gentry
        npv = []  # by Denton Gentry
        svcsic = self.soln_vs_conv_single_iunit_cashflow()  # by Denton Gentry
        offset = self.single_iunit_purchase_year - svcsic.first_valid_index() + 1  # by Denton Gentry
        for n in range(len(svcsic.index)):  # by Denton Gentry
            l = [0] * (n + offset) + [svcsic.iloc[n]]  # by Denton Gentry
            npv.append(np.npv(rate=self.ac.npv_discount_rate, values=l))  # by Denton Gentry
        result = pd.Series(npv, index=svcsic.index.copy())  # by Denton Gentry
        result.name = 'soln_vs_conv_single_iunit_npv'  # by Denton Gentry
        return result  # by Denton Gentry


    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_vs_conv_single_iunit_payback(self):  # by Denton Gentry
        """Whether the solution has paid off versus the conventional, for each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!K126:K250  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_vs_conv_single_iunit_cashflow().cumsum().apply(lambda x: 1 if x >= 0 else 0)  # by Denton Gentry
        result.name = 'soln_vs_conv_single_iunit_payback'  # by Denton Gentry
        return result  # by Denton Gentry


    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_vs_conv_single_iunit_payback_discounted(self):  # by Denton Gentry
        """Whether the solution NPV has paid off versus the conventional, for each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!L126:L250  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_vs_conv_single_iunit_npv().cumsum().apply(lambda x: 1 if x >= 0 else 0)  # by Denton Gentry
        result.name = 'soln_vs_conv_single_iunit_payback_discounted'  # by Denton Gentry
        return result  # by Denton Gentry


    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_only_single_iunit_cashflow(self):  # by Denton Gentry
        """  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!M126:M250  # by Denton Gentry
        """  # by Denton Gentry
        first_year = CORE_START_YEAR  # by Denton Gentry
        last_year = max(CORE_END_YEAR, CORE_START_YEAR + self.ac.soln_lifetime_replacement_rounded)  # by Denton Gentry
        last_row = 2139  # by Denton Gentry
        result = pd.Series(0, index=np.arange(first_year, last_row + 1), dtype='float')  # by Denton Gentry
        result.index.name = 'Year'  # by Denton Gentry
        result.index = result.index.astype(int)  # by Denton Gentry
        result.name = 'soln_only_single_iunit_cashflow'  # by Denton Gentry
        # by Denton Gentry
        soln_lifetime = self.ac.soln_lifetime_replacement  # by Denton Gentry
        if self.ac.soln_avg_annual_use is not None and self.ac.conv_avg_annual_use is not None:
            conv_usage_mult = self.ac.soln_avg_annual_use / self.ac.conv_avg_annual_use  # RRS
        else:
            conv_usage_mult = 1  # LAND

        for year in range(first_year, last_year + 1):  # by Denton Gentry
            cost = 0
            if soln_lifetime <= 0:  # by Denton Gentry
                break  # by Denton Gentry
            # by Denton Gentry
            if year == first_year:  # by Denton Gentry
                # account for the cost of the solution iunit in the first year.  # by Denton Gentry
                cost -= self.soln_pds_install_cost_per_iunit.loc[self.single_iunit_purchase_year]  # by Denton Gentry
            # by Denton Gentry
            # Difference in fixed operating cost of conventional versus that of solution  # by Denton Gentry
            cost += (self.ac.conv_fixed_oper_cost_per_iunit * conv_usage_mult -  # by Denton Gentry
                     self.ac.soln_fixed_oper_cost_per_iunit) * self.conversion_factor_fom  # by Denton Gentry
            # by Denton Gentry
            # Difference in variable operating cost of conventional versus that of solution  # by Denton Gentry
            if self.ac.has_var_costs:
                conv_var_cost = self.ac.conv_var_oper_cost_per_funit + self.ac.conv_fuel_cost_per_funit
                soln_var_cost = self.ac.soln_var_oper_cost_per_funit + self.ac.soln_fuel_cost_per_funit
                cost += (self.ac.soln_avg_annual_use * conv_var_cost -
                         self.ac.soln_avg_annual_use * soln_var_cost) * self.conversion_factor_vom  # by Denton Gentry
            # by Denton Gentry
            # account for a partial year at the end of the lifetime.  # by Denton Gentry
            cost *= min(1, soln_lifetime)  # by Denton Gentry
            result[year] = cost if math.fabs(cost) > 0.01 else 0.0  # by Denton Gentry
            # by Denton Gentry
            soln_lifetime -= 1  # by Denton Gentry
        return result  # by Denton Gentry


    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_only_single_iunit_npv(self):  # by Denton Gentry
        """Net Present Value of single iunit cashflow, looking only at costs of the Solution.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!N126:N250  # by Denton Gentry
        """  # by Denton Gentry
        npv = []  # by Denton Gentry
        sosic = self.soln_only_single_iunit_cashflow()  # by Denton Gentry
        offset = self.single_iunit_purchase_year - sosic.first_valid_index() + 1  # by Denton Gentry
        for n in range(len(sosic.index)):  # by Denton Gentry
            l = [0] * (n + offset) + [sosic.iloc[n]]  # by Denton Gentry
            npv.append(np.npv(rate=self.ac.npv_discount_rate, values=l))  # by Denton Gentry
        result = pd.Series(npv, index=sosic.index.copy())  # by Denton Gentry
        result.name = 'soln_only_single_iunit_npv'  # by Denton Gentry
        return result  # by Denton Gentry


    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_only_single_iunit_payback(self):  # by Denton Gentry
        """Whether the solution has paid off, for each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!O126:O250  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_only_single_iunit_cashflow().cumsum().apply(lambda x: 1 if x >= 0 else 0)  # by Denton Gentry
        result.name = 'soln_only_single_iunit_payback'  # by Denton Gentry
        return result  # by Denton Gentry


    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_only_single_iunit_payback_discounted(self):  # by Denton Gentry
        """Whether the solution NPV has paid off, for each year.  # by Denton Gentry
           SolarPVUtil 'Operating Cost'!P126:P250  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_only_single_iunit_npv().cumsum().apply(lambda x: 1 if x >= 0 else 0)  # by Denton Gentry
        result.name = 'soln_only_single_iunit_payback_discounted'  # by Denton Gentry
        return result  # by Denton Gentry
