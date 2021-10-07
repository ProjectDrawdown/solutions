"""N2O Calcs module.
"""
from functools import lru_cache
from meta_model.json_mixin import JsonMixin
from model import emissionsfactors


class N2OCalcs(JsonMixin):
    """N2O Calcs module.
         Arguments:
           ac: advanced_cost.py object, storing settings to control model operation.
           soln_net_annual_funits_adopted: annual functional/land units
           soln_pds_direct_n2o_co2_emissions_saved: direct n2o emissions avoided per land unit
             (not used for RRS).
      """

    def __init__(self, ac, soln_net_annual_funits_adopted,
                 soln_pds_direct_n2o_co2_emissions_saved=None):
        self.ac = ac
        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted
        self.soln_pds_direct_n2o_co2_emissions_saved = soln_pds_direct_n2o_co2_emissions_saved

    
    @lru_cache()
    def n2o_tons_reduced(self):
        """n2o reduced from the RRS model, in tons n2o per year.
        """
        if self.ac.n2o_is_co2eq:
            ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)
            result = (self.soln_net_annual_funits_adopted * self.ac.n2o_co2_per_funit)/ef.N2Omultiplier
        else:
            result = self.soln_net_annual_funits_adopted * self.ac.n2o_co2_per_funit
        result.loc[:self.ac.report_start_year - 1] = 0.0
        result.loc[self.ac.report_end_year + 1:] = 0.0
        result.name = "n2o_tons_reduced"
        return result

    
    @lru_cache()
    def avoided_direct_emissions_n2o_land(self):
        """n2o emissions avoided, in tons per year
        """
        ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)
        result = self.soln_pds_direct_n2o_co2_emissions_saved.copy(deep=True) / ef.N2Omultiplier
        result.loc[:self.ac.report_start_year - 1] = 0.0
        result.loc[self.ac.report_end_year + 1:] = 0.0
        result.name = "avoided_direct_emissions_n2o_land"
        return result
    
    
    @lru_cache()
    def n2o_megatons_avoided_or_reduced(self):
        """n2o emissions avoided or reduced, Mega in tons per year (units needed for the FaIR model)
        """
        if self.soln_pds_direct_n2o_co2_emissions_saved is not None:
            n2o_tons = self.avoided_direct_emissions_n2o_land()
        else:
            n2o_tons = self.n2o_tons_reduced()
        
        result = n2o_tons * 0.000001
        result.name = "n2o_megatons_avoided_or_reduced"
        return result
    
