"""Base classes of all scenario objects"""
from pathlib import Path

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import dd
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import scenario
from model import unitadoption
from model import vma
from model import tam
from model import conversions
from solution import rrs

# This class is currently a stub, because the code was not oritinally designed with a common Scenario base class.
# We expect to add new functionality, and probably migrate some shared functionality, to this class.

class Scenario:

    ac : advanced_controls.AdvancedControls = None

    def set_ref_adoption(self):
        pass

    def set_pds_adoption(self):
        pass

    def key_results(self, year=2050, region='World'):
        if self.solution_category == self.solution_category.REDUCTION or self.solution_category == self.solution_category.REPLACEMENT:
            return {'implementation_unit_adoption_increase': self.implementation_unit_adoption_increase(year=year),
                    'functional_unit_adoption_increase': self.functional_unit_adoption_increase(year=year),
                    'marginal_first_cost': self.marginal_first_cost(year=year),
                    'net_operating_savings': self.net_operating_savings(year=year),
                    'lifetime_operating_savings': self.lifetime_operating_savings(),
                    'cumulative_emissions_reduced': self.cumulative_emissions_reduced(year=year, region=region)}
        elif self.solution_category == self.solution_category.LAND:
            return {'adoption_unit_increase': self.adoption_unit_increase_LAND(year=year),
                    'marginal_first_cost': self.marginal_first_cost(year=year),
                    'net_operating_savings': self.net_operating_savings(year=year),
                    'lifetime_operating_savings': self.lifetime_operating_savings(),
                    'cumulative_emissions_reduced': self.cumulative_emissions_reduced(year=year, region=region),
                    'total_additional_co2eq_sequestered': self.total_additional_co2eq_sequestered(year)}
        else:
            raise NotImplementedError("key_results only implemented for REDUCTION, REPLACEMENT and LAND")

    def implementation_unit_adoption_increase(self, year=2050, region='World'):
        if hasattr(self, 'pds_ca'):
            if self.pds_ca.soln_adoption_custom_name:
                pds_adoption = self.pds_ca.adoption_data_per_region()
            else:
                pds_adoption = self.ht.soln_pds_funits_adopted()
        else:
            pds_adoption = self.ht.soln_pds_funits_adopted()

        if hasattr(self, 'ref_ca'):
            if self.ref_ca.soln_adoption_custom_name:
                ref_adoption = self.ref_ca.adoption_data_per_region()
            else:
                ref_adoption = self.ht.soln_ref_funits_adopted()
        else:
            ref_adoption = self.ht.soln_ref_funits_adopted()

        return (pds_adoption.loc[year][region] / self.ac.soln_avg_annual_use - 
            ref_adoption.loc[year][region] / self.ac.soln_avg_annual_use)

    def adoption_unit_increase_LAND(self, year=2050, region='World'):
        if hasattr(self, 'pds_ca'):
            if self.pds_ca.soln_adoption_custom_name:
                pds_adoption = self.pds_ca.adoption_data_per_region()
            else:
                pds_adoption = self.ht.soln_pds_funits_adopted()
        else:
            pds_adoption = self.ht.soln_pds_funits_adopted()

        if hasattr(self, 'ref_ca'):
            if self.ref_ca.soln_adoption_custom_name:
                ref_adoption = self.ref_ca.adoption_data_per_region()
            else:
                ref_adoption = self.ht.soln_ref_funits_adopted()
        else:
            ref_adoption = self.ht.soln_ref_funits_adopted()

        return (pds_adoption.loc[year][region]  - 
            ref_adoption.loc[year][region])
        pass

    def total_additional_co2eq_sequestered(self, year=2050):
        # farmlandrestoration starts in year 2021 in Advanced Control excel
        # Not sure if this is a bug or intended. Excel also says it should start at 2020
        return (self.c2.co2_sequestered_global().loc[2021:year,'All'] / 1000).sum()

    def functional_unit_adoption_increase(self, year=2050, region='World'):
        if hasattr(self, 'pds_ca'):
            if self.pds_ca.soln_adoption_custom_name:
                pds_adoption = self.pds_ca.adoption_data_per_region()
            else:
                pds_adoption = self.ht.soln_pds_funits_adopted()
        else:
            pds_adoption = self.ht.soln_pds_funits_adopted()

        if hasattr(self, 'ref_ca'):
            if self.ref_ca.soln_adoption_custom_name:
                ref_adoption = self.ref_ca.adoption_data_per_region()
            else:
                ref_adoption = self.ht.soln_ref_funits_adopted()
        else:
            ref_adoption = self.ht.soln_ref_funits_adopted()

        return (
            pds_adoption.loc[year] - 
            ref_adoption.loc[year]
            )[region]

    def marginal_first_cost(self, year=2050):
        return (self.fc.soln_pds_annual_world_first_cost().loc[:year].sum()-
            self.fc.soln_ref_annual_world_first_cost().loc[:year].sum()-
            self.fc.conv_ref_annual_world_first_cost().loc[:year].sum()
            ) / 1e9

    def net_operating_savings(self, year=2050):
        return (
            (self.oc.conv_ref_cumulative_operating_cost().loc[year] -
            self.oc.conv_ref_cumulative_operating_cost().loc[2020]) -
            (self.oc.soln_pds_cumulative_operating_cost().loc[year]  -
            self.oc.soln_pds_cumulative_operating_cost().loc[2020])
            ) / 1e9

    def lifetime_operating_savings(self):
        return self.oc.soln_marginal_operating_cost_savings().sum() / 1e9

    def cumulative_emissions_reduced(self, year=2050, region='World'):
        return self.c2.co2eq_mmt_reduced().loc[2020:year, region].sum() / 1e3


    


class RRSScenario(Scenario):

    tm: tam.TAM = None

    # These must be set by each class
    tam_ref_data_sources = None
    tam_pds_data_sources = None


    def set_tam(self, config_values=None, **args):
        """Create the self.tm object based on the information in self._tamconfig_list, self.tam_ref_data_sources
        and self.tam_pds_data_sources.  
        
        Overrides to individual values in the tamconfig can also be specified
        in the config_values argument, which should be a list of tuples (param_name, region, value)

        Other configuration values may be passed directly to tam.TAM via **args.
        """
        tamconfig = tam.make_tam_config()
        tamconfig.loc['source_until_2014','World']     = self.ac.source_until_2014
        tamconfig.loc['source_until_2014','PDS World'] = self.ac.source_until_2014
        tamconfig.loc['source_after_2014','World']     = self.ac.ref_source_post_2014
        tamconfig.loc['source_after_2014','PDS World'] = self.ac.pds_source_post_2014
        if config_values is not None:
            for (row,col,val) in config_values:
                tamconfig.loc[row,col] = val
        
        if self.ac.ref_tam_custom_source:
            # completely override the tam_ref_data_sources field
            # #HACK
            # TAM doesn't auto-interpolate single sources.  But it does auto-interpolate groups.
            # So we use the sneaky hack of duplicating the source get TAM to do this work for us.
            # It keeps the code changes less invasive for now, but should be refactored later.
            self.tam_ref_data_sources = { 'Custom Cases' : { 
                                            'Custom Ref Tam' : self.ac.ref_tam_custom_source,
                                            'Custom Ref Dup' : self.ac.ref_tam_custom_source
                                        }}
            # set 'source_after_2014' for 'World' and all regions (everything except 'PDS World')
            pdsworld = tamconfig.loc['source_after_2014', 'PDS World']
            tamconfig.loc['source_after_2014',:] = 'Custom Cases'
            tamconfig.loc['source_after_2014','PDS World'] = pdsworld
        if self.ac.pds_tam_custom_source:
            # completely override the pds_ref_data_sources field
            self.tam_pds_data_sources = { 'Custom Cases' : { 
                                            'Custom PDS Tam' : self.ac.ref_tam_custom_source,
                                            'Custom PDS Dup' : self.ac.ref_tam_custom_source
                                        }}
            tamconfig.loc['source_after_2014','PDS World'] = 'Custom Cases'

        self.tm = tam.TAM(
            tamconfig=tamconfig, 
            tam_ref_data_sources=self.tam_ref_data_sources,
            tam_pds_data_sources=self.tam_pds_data_sources,
            **args)
    """
    def key_results(self, year=2050, region='World'):
        return {'implementation_unit_adoption_increase': self.implementation_unit_adoption_increase(year=year),
                'functional_unit_adoption_increase': self.functional_unit_adoption_increase(year=year),
                'marginal_first_cost': self.marginal_first_cost(year=year),
                'net_operating_savings': self.net_operating_savings(year=year),
                'lifetime_operating_savings': self.lifetime_operating_savings(),
                'cumulative_emissions_reduced': self.cumulative_emissions_reduced(year=year, region=region)}

    def implementation_unit_adoption_increase(self, year=2050, region='World'):
        if hasattr(self, 'pds_ca'):
            if self.pds_ca.soln_adoption_custom_name:
                pds_adoption = self.pds_ca.adoption_data_per_region()
            else:
                pds_adoption = self.ht.soln_pds_funits_adopted()
        else:
            pds_adoption = self.ht.soln_pds_funits_adopted()

        if hasattr(self, 'ref_ca'):
            if self.ref_ca.soln_adoption_custom_name:
                ref_adoption = self.ref_ca.adoption_data_per_region()
            else:
                ref_adoption = self.ht.soln_ref_funits_adopted()
        else:
            ref_adoption = self.ht.soln_ref_funits_adopted()

        return (pds_adoption.loc[year][region] / self.ac.soln_avg_annual_use - 
            ref_adoption.loc[year][region] / self.ac.soln_avg_annual_use)

    def functional_unit_adoption_increase(self, year=2050, region='World'):
        if hasattr(self, 'pds_ca'):
            if self.pds_ca.soln_adoption_custom_name:
                pds_adoption = self.pds_ca.adoption_data_per_region()
            else:
                pds_adoption = self.ht.soln_pds_funits_adopted()
        else:
            pds_adoption = self.ht.soln_pds_funits_adopted()

        if hasattr(self, 'ref_ca'):
            if self.ref_ca.soln_adoption_custom_name:
                ref_adoption = self.ref_ca.adoption_data_per_region()
            else:
                ref_adoption = self.ht.soln_ref_funits_adopted()
        else:
            ref_adoption = self.ht.soln_ref_funits_adopted()

        return (
            pds_adoption.loc[year] - 
            ref_adoption.loc[year]
            )[region]

    def marginal_first_cost(self, year=2050):
        return (self.fc.soln_pds_annual_world_first_cost().loc[:year].sum()-
            self.fc.soln_ref_annual_world_first_cost().loc[:year].sum()-
            self.fc.conv_ref_annual_world_first_cost().loc[:year].sum()
            ) / 1e9

    def net_operating_savings(self, year=2050):
        return (
            (self.oc.conv_ref_cumulative_operating_cost().loc[year] -
            self.oc.conv_ref_cumulative_operating_cost().loc[2020]) -
            (self.oc.soln_pds_cumulative_operating_cost().loc[year]  -
            self.oc.soln_pds_cumulative_operating_cost().loc[2020])
            ) / 1e9

    def lifetime_operating_savings(self):
        return self.oc.soln_marginal_operating_cost_savings().sum() / 1e9

    def cumulative_emissions_reduced(self, year=2050, region='World'):
        return self.c2.co2eq_mmt_reduced().loc[2020:year, region].sum() / 1e3
    """


class LandScenario(Scenario):
    
    pass
