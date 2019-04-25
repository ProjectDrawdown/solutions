"""CH4 Calcs module.  # by Denton Gentry
  # by Denton Gentry
Computes reductions in CO2-equivalent emissions.  # by Denton Gentry
"""  # by Denton Gentry
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import math  # by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry


# by Denton Gentry
class CH4Calcs:  # by Denton Gentry
    """CH4 Calcs module.  # by Denton Gentry
         Arguments:  # by Denton Gentry
           ac: advanced_cost.py object, storing settings to control model operation.  # by Denton Gentry
           soln_net_annual_funits_adopted: annual functional/land units  # by Denton Gentry
           soln_pds_direct_ch4_co2_emissions_saved: direct CH4 emissions avoided per land unit  # by Denton Gentry
             (not used for RRS).  # by Denton Gentry
      """  # by Denton Gentry

    def __init__(self, ac, soln_net_annual_funits_adopted,  # by Denton Gentry
                 soln_pds_direct_ch4_co2_emissions_saved=None):  # by Denton Gentry
        self.ac = ac  # by Denton Gentry
        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted  # by Denton Gentry
        self.soln_pds_direct_ch4_co2_emissions_saved = soln_pds_direct_ch4_co2_emissions_saved  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ch4_tons_reduced(self):  # by Denton Gentry
        """CH4 reduced, in tons.  # by Denton Gentry
           replace gas_ch4_step = `gas_tons_ch4' * `e'^(-(time_from_present - `n')/12)  # by Denton Gentry
           SolarPVUtil 'CH4 Calcs'!A10:K56  # by Denton Gentry
        """  # by Denton Gentry
        if self.ac.ch4_is_co2eq:  # by Denton Gentry
            result = self.soln_net_annual_funits_adopted * 0  # by Denton Gentry
        else:  # by Denton Gentry
            result = self.soln_net_annual_funits_adopted * self.ac.ch4_co2_per_twh  # by Denton Gentry
        result.loc[:self.ac.report_start_year - 1] = 0.0  # by Denton Gentry
        result.loc[self.ac.report_end_year + 1:] = 0.0  # by Denton Gentry
        result.name = "ch4_tons_reduced"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def avoided_direct_emissions_ch4_land(self):  # by Denton Gentry
        """CH4 emissions avoided, in tons  # by Denton Gentry
           replace gas_ch4_step = `gas_tons_ch4' * `e'^(-(time_from_present - `n')/12)  # by Denton Gentry
           Improved Rice 'CH4 Calcs'!A12:K58  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_direct_ch4_co2_emissions_saved.copy(deep=True)  # by Denton Gentry
        result.loc[:self.ac.report_start_year - 1] = 0.0  # by Denton Gentry
        result.loc[self.ac.report_end_year + 1:] = 0.0  # by Denton Gentry
        result.name = "avoided_direct_emissions_ch4_land"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ch4_ppb_calculator(self):  # by Denton Gentry
        """Parts Per Billion reduction calculator for CH4.  # by Denton Gentry
      # by Denton Gentry
           Each yearly reduction in CH4 (in metric tons) is modeled as a discrete avoided pulse.  # by Denton Gentry
           A Simplified atmospheric lifetime function for CH4 is taken from Myhrvald and Caldeira  # by Denton Gentry
           (2012). Atmospheric tons of CH4 are converted to parts per billion CH4 based on the  # by Denton Gentry
           molar mass of CH4 and the moles of atmosphere.   # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'CH4 Calcs'!A64:AW110  # by Denton Gentry
        """  # by Denton Gentry
        if self.soln_pds_direct_ch4_co2_emissions_saved is not None:  # by Denton Gentry
            ch4_tons = self.avoided_direct_emissions_ch4_land()  # by Denton Gentry
        else:  # by Denton Gentry
            ch4_tons = self.ch4_tons_reduced()  # by Denton Gentry
        columns = ["PPB", "Total"] + list(range(2015, 2061))  # by Denton Gentry
        ppb_calculator = pd.DataFrame(0, columns=columns,  # by Denton Gentry
                                      index=ch4_tons.index.copy(), dtype=np.float64)  # by Denton Gentry
        ppb_calculator.index = ppb_calculator.index.astype(int)  # by Denton Gentry
        first_year = ppb_calculator.first_valid_index()  # by Denton Gentry
        last_year = ppb_calculator.last_valid_index()  # by Denton Gentry
        for year in ppb_calculator.index:  # by Denton Gentry
            if year not in columns:  # by Denton Gentry
                continue  # by Denton Gentry
            b = ch4_tons.loc[year, "World"]  # by Denton Gentry
            for delta in range(1, last_year - first_year + 1):  # by Denton Gentry
                if (year + delta - 1) > last_year:  # by Denton Gentry
                    break  # by Denton Gentry
                ppb_calculator.loc[year + delta - 1, year] = b * math.exp(-delta / 12)  # by Denton Gentry
        ppb_calculator.loc[:, "Total"] = ppb_calculator.sum(axis=1)  # by Denton Gentry
        for year in ppb_calculator.index:  # by Denton Gentry
            ppb_calculator.loc[year, "PPB"] = ppb_calculator.loc[year, "Total"] / (
                16.04 * 1.8 * 10 ** 5)  # by Denton Gentry
        ppb_calculator.name = "ch4_ppb_calculator"  # by Denton Gentry
        return ppb_calculator  # by Denton Gentry
