"""CH4 Calcs module.

Computes reductions in CO2-equivalent emissions.
"""

from functools import lru_cache
import numpy as np
import pandas as pd


class CH4Calcs:
    """CH4 Calcs module.
         Arguments:
           ac: advanced_cost.py object, storing settings to control model operation.
           soln_net_annual_funits_adopted: annual functional/land units
           soln_pds_direct_ch4_co2_emissions_saved: direct CH4 emissions avoided per land unit
             (not used for RRS).
      """

    def __init__(self, ac, soln_net_annual_funits_adopted,
                 soln_pds_direct_ch4_co2_emissions_saved=None):
        self.ac = ac
        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted
        self.soln_pds_direct_ch4_co2_emissions_saved = soln_pds_direct_ch4_co2_emissions_saved


    @lru_cache()
    def ch4_tons_reduced(self):
        """CH4 reduced, in tons.
           replace gas_ch4_step = `gas_tons_ch4' * `e'^(-(time_from_present - `n')/12)
           SolarPVUtil 'CH4 Calcs'!A10:K56
        """
        if self.ac.ch4_is_co2eq:
            result = self.soln_net_annual_funits_adopted * 0
        else:
            result = self.soln_net_annual_funits_adopted * self.ac.ch4_co2_per_funit
        result.loc[:self.ac.report_start_year - 1] = 0.0
        result.loc[self.ac.report_end_year + 1:] = 0.0
        result.name = "ch4_tons_reduced"
        return result


    @lru_cache()
    def avoided_direct_emissions_ch4_land(self):
        """CH4 emissions avoided, in tons
           replace gas_ch4_step = `gas_tons_ch4' * `e'^(-(time_from_present - `n')/12)
           Improved Rice 'CH4 Calcs'!A12:K58
        """
        result = self.soln_pds_direct_ch4_co2_emissions_saved.copy(deep=True)
        result.loc[:self.ac.report_start_year - 1] = 0.0
        result.loc[self.ac.report_end_year + 1:] = 0.0
        result.name = "avoided_direct_emissions_ch4_land"
        return result


    @lru_cache()
    def ch4_ppb_calculator(self):
        """Parts Per Billion reduction calculator for CH4.

           Each yearly reduction in CH4 (in metric tons) is modeled as a discrete avoided pulse.
           A Simplified atmospheric lifetime function for CH4 is taken from Myhrvald and Caldeira
           (2012). Atmospheric tons of CH4 are converted to parts per billion CH4 based on the
           molar mass of CH4 and the moles of atmosphere.

           SolarPVUtil 'CH4 Calcs'!A64:AW110
        """
        if self.soln_pds_direct_ch4_co2_emissions_saved is not None:
            ch4_tons = self.avoided_direct_emissions_ch4_land()
        else:
            ch4_tons = self.ch4_tons_reduced()

        col_years = np.arange(2015, 2061)
        index_years = ch4_tons.index.values

        deltas = index_years.reshape(-1, 1) - col_years.reshape(1, -1) + 1

        vals = np.exp( - deltas / 12) * ch4_tons.loc[col_years, "World"].values.reshape(1, -1)
        vals[deltas < 1] = 0 # Overwrite values for negative deltas

        total = vals.sum(axis=1).reshape(-1, 1)
        ppb = total / (16.04 * 1.8 * 10 ** 5)

        ppb_calculator = pd.DataFrame(np.concatenate([ppb, total, vals], axis=1),
                                    columns=["PPB", "Total"] + list(col_years),
                                    index=ch4_tons.index.copy(),
                                    dtype=np.float64
                                    )
        ppb_calculator.name = "ch4_ppb_calculator"
        return ppb_calculator
