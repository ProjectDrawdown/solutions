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



class LandScenario(Scenario):
    pass
