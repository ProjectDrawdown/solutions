"""CH4 Calcs module.

Computes reductions for methane in individual gas units and CO2-equivalent emissions.
"""

from functools import lru_cache
import numpy as np
import pandas as pd

from model.data_handler import DataHandler
from model.decorators import data_func
from model import emissionsfactors



class CH4Calcs(DataHandler):
    """CH4 Calcs module.
         Arguments:
           ac: advanced_cost.py object, storing settings to control model operation.
           soln_net_annual_funits_adopted: annual functional/land units
           soln_pds_direct_ch4_co2_emissions_saved: direct CH4 emissions avoided per land unit
             (not used for RRS).
      """

    def __init__(self, ac, soln_net_annual_funits_adopted,
                 soln_pds_direct_ch4_co2_emissions_saved=None):

        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted
        self.soln_pds_direct_ch4_co2_emissions_saved = soln_pds_direct_ch4_co2_emissions_saved

        ef = emissionsfactors.CO2Equiv(ac.co2eq_conversion_source)
        self.CH4multiplier = ef.CH4multiplier
        
        # The setting of ac.ch4_is_co2eq determines whether ac.ch4_co2_per_funit is expressed
        # in co2eq or mass.   Make our code less confusing by disambiguating and storing both.

        c4val = ac.ch4_co2_per_funit
        if ac.ch4_is_co2eq:
            self.ch4_co2eq_per_unit = c4val
            self.ch4_mass_per_unit = c4val / self.CH4multiplier
        else:
            self.ch4_co2eq_per_unit = c4val * self.CH4multiplier
            self.ch4_mass_per_unit = c4val


    @lru_cache()
    @data_func
    def ch4_co2eq_tons_reduced(self):
        """CH4 reduced, in tons of CO2eq per year.
        """
        result = self.soln_net_annual_funits_adopted * self.ch4_co2eq_per_unit
        result.name = "ch4_co2eq_tons_reduced"
        return result
    
    @lru_cache()
    def ch4_tons_reduced(self):
        """CH4 reduced from the RRS model, in tons CH4 per year.
        """        
        result = self.soln_net_annual_funits_adopted * self.ch4_mass_per_unit
        result.name = "ch4_tons_reduced"
        return result
    

    @lru_cache()
    def avoided_direct_emissions_ch4_co2eq_land(self):
        """CH4 emissions avoided from the land model, in tons of CO2eq per year
        """
        result = self.soln_pds_direct_ch4_co2_emissions_saved.copy(deep=True)
        result.name = "avoided_direct_emissions_ch4_co2eq_land"
        return result
    
    

    @lru_cache()
    def avoided_direct_emissions_ch4_land(self):
        """CH4 direct emissions avoided, in tons per year
        """
        result = self.soln_pds_direct_ch4_co2_emissions_saved.copy(deep=True) / self.CH4multiplier
        result.name = "avoided_direct_emissions_ch4_land"
        return result
    
    

    @lru_cache()
    def ch4_megatons_avoided_or_reduced(self):
        """CH4 emissions avoided or reduced, in megatons per year (units needed for the FaIR model). A key result!
        """
        if self.soln_pds_direct_ch4_co2_emissions_saved is not None:
            ch4_tons = self.avoided_direct_emissions_ch4_land()
        else:
            ch4_tons = self.ch4_tons_reduced()
        result = ch4_tons * 0.000001
        result.name = "ch4_megatons_avoided_or_reduced"
        return result
    

    @lru_cache()
    def ch4_ppb_calculator(self):
        """Parts Per Billion reduction calculator for CH4.
           Each yearly reduction in CH4 (in metric tons) is modeled as a discrete avoided pulse.
           A Simplified atmospheric lifetime function for CH4 is taken from Myhrvald and Caldeira
           (2012). Atmospheric tons of CH4 are converted to parts per billion CH4 based on the
           molar mass of CH4 and the moles of atmosphere.
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
