"""First Cost module calculations."""  # by Denton Gentry
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import math  # by Denton Gentry
# by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry


# by Denton Gentry
# by Denton Gentry
class FirstCost:  # by Denton Gentry
    """Implementation for the First Cost module.  # by Denton Gentry
    # by Denton Gentry
    Arguments:  # by Denton Gentry
      ac = advanced_controls.py object, storing settings to control module operation.
      pds_learning_increase_mult = multiplicative factor for the PDS learning  # by Denton Gentry
        rate. This is typically 2 or 4.  # by Denton Gentry
      ref_learning_increase_mult = multiplicative factor for the reference  # by Denton Gentry
        solution learning rate. This is typically 2 or 4.  # by Denton Gentry
      conv_learning_increase_mult = multiplicative factor for the Conventional  # by Denton Gentry
        learning rate. This is typically 2 or 4.  # by Denton Gentry
      soln_pds_tot_iunits_reqd: total implementation units required each year in  # by Denton Gentry
        the Project Drawdown scenario, as a DataFrame with columns per region.  # by Denton Gentry
      soln_ref_tot_iunits_reqd: total implementation units required each year in  # by Denton Gentry
        the Reference scenario, as a DataFrame with columns per region.  # by Denton Gentry
      conv_ref_tot_iunits: total implementation units required each year in
        the Conventional Reference scenario, as a DataFrame with columns per region.  # by Denton Gentry
      soln_pds_new_iunits_reqd: new implementation units required each year in  # by Denton Gentry
        the Project Drawdown scenario, as a DataFrame with columns per region.  # by Denton Gentry
      soln_ref_new_iunits_reqd: new implementation units required each year in  # by Denton Gentry
        the Reference scenario, as a DataFrame with columns per region.  # by Denton Gentry
      conv_ref_new_iunits: new implementation units required each year in
        the Conventional Reference scenario, as a DataFrame with columns per region.  # by Denton Gentry
      fc_convert_iunit_factor: conversion factor from iunits to a more natural monetary  # by Denton Gentry
        unit.  # by Denton Gentry
      conv_ref_first_cost_uses_tot_units: Many RRS solutions use conv_ref_new_iunits to  # by Denton Gentry
        calculate conv_ref_annual_world_first_cost. Many Land solutions use the new  # by Denton Gentry
        conv_ref_tot_iunits year over year (which are land units, not iunits, in this case).  # by Denton Gentry
    """  # by Denton Gentry

    def __init__(self, ac, pds_learning_increase_mult,  # by Denton Gentry
                 ref_learning_increase_mult, conv_learning_increase_mult,  # by Denton Gentry
                 soln_pds_tot_iunits_reqd, soln_ref_tot_iunits_reqd, conv_ref_tot_iunits,
                 soln_pds_new_iunits_reqd, soln_ref_new_iunits_reqd, conv_ref_new_iunits,
                 fc_convert_iunit_factor=1.0, conv_ref_first_cost_uses_tot_units=False):  # by Denton Gentry
        self.ac = ac  # by Denton Gentry
        self.pds_learning_increase_mult = pds_learning_increase_mult  # by Denton Gentry
        self.ref_learning_increase_mult = ref_learning_increase_mult  # by Denton Gentry
        self.conv_learning_increase_mult = conv_learning_increase_mult  # by Denton Gentry
        self.soln_pds_tot_iunits_reqd = soln_pds_tot_iunits_reqd  # by Denton Gentry
        self.soln_ref_tot_iunits_reqd = soln_ref_tot_iunits_reqd  # by Denton Gentry
        self.conv_ref_tot_iunits = conv_ref_tot_iunits
        self.soln_pds_new_iunits_reqd = soln_pds_new_iunits_reqd  # by Denton Gentry
        self.soln_ref_new_iunits_reqd = soln_ref_new_iunits_reqd  # by Denton Gentry
        self.conv_ref_new_iunits = conv_ref_new_iunits
        self.fc_convert_iunit_factor = fc_convert_iunit_factor  # by Denton Gentry
        self.conv_ref_first_cost_uses_tot_units = conv_ref_first_cost_uses_tot_units  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_install_cost_per_iunit(self):  # by Denton Gentry
        """Install cost per implementation unit in Solution-PDS  # by Denton Gentry
           'First Cost'!C37:C82  # by Denton Gentry
        """  # by Denton Gentry
        log_learning_rate = math.log10(self.ac.soln_first_cost_learning_rate)  # by Denton Gentry
        log_learning_mult = math.log10(self.pds_learning_increase_mult)  # by Denton Gentry
        parameter_b = log_learning_rate / log_learning_mult  # by Denton Gentry
        # by Denton Gentry
        p = (1 / self.soln_pds_tot_iunits_reqd['World'][2015]) ** parameter_b  # by Denton Gentry
        first_unit_cost = self.ac.pds_2014_cost * p  # by Denton Gentry
        # by Denton Gentry
        world = self.soln_pds_tot_iunits_reqd.loc[:, 'World']  # by Denton Gentry
        result_per_iunit = (first_unit_cost * world ** parameter_b)  # by Denton Gentry
        # In Excel, NaN^0 == NaN. In Python, NaN^0 == 1.  # by Denton Gentry
        # We want to match the Excel behavior.  # by Denton Gentry
        result_per_iunit.mask(world.isna(), other=np.nan, inplace=True)  # by Denton Gentry
        result_display = result_per_iunit * self.fc_convert_iunit_factor  # by Denton Gentry
        # by Denton Gentry
        if self.ac.soln_first_cost_below_conv:  # by Denton Gentry
            result = result_display  # by Denton Gentry
        else:  # by Denton Gentry
            conv = self.conv_ref_install_cost_per_iunit()  # by Denton Gentry
            result = result_display.combine(conv, lambda x1, x2: max(x1, x2))  # by Denton Gentry
        result.name = "soln_pds_install_cost_per_iunit"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_install_cost_per_iunit(self):  # by Denton Gentry
        """Install cost per implementation unit in Conventional-REF  # by Denton Gentry
           'First Cost'!O37:O82  # by Denton Gentry
        """  # by Denton Gentry
        log_learning_rate = math.log10(self.ac.conv_first_cost_learning_rate)  # by Denton Gentry
        log_learning_mult = math.log10(self.conv_learning_increase_mult)  # by Denton Gentry
        parameter_b = log_learning_rate / log_learning_mult  # by Denton Gentry
        # by Denton Gentry
        # Excel implementation referenced the cell for 2014, not 2015, so we  # by Denton Gentry
        # do the same here. Normally, we base calculations from 2015.  # by Denton Gentry
        p = (1 / self.conv_ref_tot_iunits['World'][2014]) ** parameter_b
        first_unit_cost = self.ac.conv_2014_cost * p  # by Denton Gentry

        # by Denton Gentry
        def calc(x):  # by Denton Gentry
            if x == 0 or parameter_b == 0:  # by Denton Gentry
                new_val = first_unit_cost  # by Denton Gentry
            elif pd.isna(x):  # by Denton Gentry
                new_val = np.nan  # by Denton Gentry
            else:  # by Denton Gentry
                new_val = first_unit_cost * x ** parameter_b  # by Denton Gentry
            return new_val * self.fc_convert_iunit_factor  # by Denton Gentry

        step1 = self.conv_ref_tot_iunits['World'].apply(calc)
        # The model postulates that conventional technologies decrease  # by Denton Gentry
        # in cost only slowly, and never increase in cost. We walk back  # by Denton Gentry
        # through the array comparing each year to the previous year.  # by Denton Gentry
        step2 = step1.rolling(2).apply(lambda x: min(x[0], x[1]), raw=True)  # by Denton Gentry
        first = step1.first_valid_index()  # by Denton Gentry
        step2[first] = step1[first]  # no min() for first item  # by Denton Gentry
        step2.name = "conv_ref_install_cost_per_iunit"  # by Denton Gentry
        return step2  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_ref_install_cost_per_iunit(self):  # by Denton Gentry
        """Install cost per implementation unit in Solution-REF  # by Denton Gentry
           'First Cost'!L37:L82  # by Denton Gentry
        """  # by Denton Gentry
        log_learning_rate = math.log10(self.ac.soln_first_cost_learning_rate)  # by Denton Gentry
        log_learning_mult = math.log10(self.ref_learning_increase_mult)  # by Denton Gentry
        parameter_b = log_learning_rate / log_learning_mult  # by Denton Gentry
        # by Denton Gentry
        if self.soln_ref_tot_iunits_reqd['World'][2015] == 0:  # by Denton Gentry
            first_unit_cost = self.ac.ref_2014_cost  # by Denton Gentry
        else:  # by Denton Gentry
            p = (1 / self.soln_ref_tot_iunits_reqd['World'][2015]) ** parameter_b  # by Denton Gentry
            first_unit_cost = self.ac.ref_2014_cost * p  # by Denton Gentry

        # by Denton Gentry
        def calc(x):  # by Denton Gentry
            if x == 0 or parameter_b == 0:  # by Denton Gentry
                new_val = first_unit_cost  # by Denton Gentry
            elif pd.isna(x):  # by Denton Gentry
                new_val = np.nan  # by Denton Gentry
            else:  # by Denton Gentry
                new_val = first_unit_cost * x ** parameter_b  # by Denton Gentry
            return new_val * self.fc_convert_iunit_factor  # by Denton Gentry

        step1 = self.soln_ref_tot_iunits_reqd.loc[:, 'World'].apply(calc)  # by Denton Gentry
        if self.ac.soln_first_cost_below_conv:  # by Denton Gentry
            result = step1  # by Denton Gentry
        else:  # by Denton Gentry
            conv = self.conv_ref_install_cost_per_iunit()  # by Denton Gentry
            result = step1.combine(conv, lambda x1, x2: max(x1, x2))  # by Denton Gentry
        result.name = "soln_ref_install_cost_per_iunit"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_annual_world_first_cost(self):  # by Denton Gentry
        """Annual World First Cost (SOLUTION-PDS)  # by Denton Gentry
           'First Cost'!E37:E82  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_new_iunits_reqd["World"] * self.soln_pds_install_cost_per_iunit()  # by Denton Gentry
        result.name = "soln_pds_annual_world_first_cost"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_ref_annual_world_first_cost(self):  # by Denton Gentry
        """Annual World First Cost (SOLUTION-REF)  # by Denton Gentry
           'First Cost'!N37:N82  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_ref_new_iunits_reqd["World"] * self.soln_ref_install_cost_per_iunit()  # by Denton Gentry
        result.name = "soln_ref_annual_world_first_cost"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_annual_world_first_cost(self):  # by Denton Gentry
        """Annual World First Cost (CONVENTIONAL-REF)  # by Denton Gentry
           'First Cost'!Q37:Q82  # by Denton Gentry
        """  # by Denton Gentry
        if self.conv_ref_first_cost_uses_tot_units:  # by Denton Gentry
            result = self.conv_ref_tot_iunits[
                         "World"].diff() * self.conv_ref_install_cost_per_iunit()  # by Denton Gentry
        else:  # by Denton Gentry
            result = self.conv_ref_new_iunits["World"] * self.conv_ref_install_cost_per_iunit()  # by Denton Gentry
        result.name = "conv_ref_annual_world_first_cost"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_cumulative_install(self):  # by Denton Gentry
        """Cumulative Install/Implementation (SOLUTION-PDS)  # by Denton Gentry
           'First Cost'!F37:F82  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_annual_world_first_cost().cumsum()  # by Denton Gentry
        result.name = "soln_pds_cumulative_install"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_cumulative_install(self):  # by Denton Gentry
        """Cumulative Install / Implementation (CONVENTIONAL-REF + SOLUTION-REF)  # by Denton Gentry
           'First Cost'!R37:R82  # by Denton Gentry
        """  # by Denton Gentry
        csum1 = self.conv_ref_annual_world_first_cost().fillna(0.0).clip(lower=0.0).cumsum()  # by Denton Gentry
        csum2 = self.soln_ref_annual_world_first_cost().fillna(0.0).clip(lower=0.0).cumsum()  # by Denton Gentry
        result = csum1.add(csum2)  # by Denton Gentry
        result.name = "ref_cumulative_install"  # by Denton Gentry
        return result  # by Denton Gentry
