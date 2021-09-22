"""Base classes of all scenario objects"""
import os
import json
import pandas as pd
import warnings
import numbers
from pathlib import Path
from model import integration
from model import adoptiondata
from model import advanced_controls
from model import customadoption
from model import helpertables
from model import s_curve
from model import tam
from solution import factory


# A note on how the Scenario inheritance structure works:
# Solutions have a great deal of code in common, but also may differ in details to almost
# an arbitrary degree: they may have unique settings of common parameters, or a completely custom
# implementation of a whole segment of the model.
# In order to support this variety of implementations while minimizing the amount of repeated
# boilerplate code, the base Scenario class (and RSSSenario and LandScenario classes) support a kind
# of inverted initialization.  The base classes in this file don't implement __init__ themselves; 
# subclasses must do that themselves.  However the base classes implement functions (like 
# initialize_adoption_bases) that do large chunks of common initialization.  The subclass
# passes parameters that control the initialization functions in various private `_` fields, and the
# initialization puts the results into the public (no `_`) fields.
# Also, the subclass can itself set the results (pds_ca, etc.) in which case the code here
# will leave it be (usually).
#
# This is all unpleasantly spaghetti, but will hopefully get cleaner as we continue to migrate code
# "upwards" to the base classes and in to the functional classes (like TAM) themselves, and as
# we simplify and generalize the kinds of parameterization these classes support.


class Scenario:

    # Public Fields common across all scenarios.
    name: str
    """The name of the solution (in English, e.g. 'Household & Commercial Recycling')"""
    module_name: str
    """The name of the solution module (e.g. 'hcrecycling')"""
    scenario: str
    """The name of the scenario """

    ac: advanced_controls.AdvancedControls = None
    """The parameters that define this scenario"""

    # Adoption state
    ht: helpertables.HelperTables = None
    """The ref and pds adoptions of this scenario"""
    ad: adoptiondata.AdoptionData = None
    """The base pds adoption, if this scenario uses an Existing Prognostication pds adoption (otherwise None)"""
    pds_ca: customadoption.CustomAdoption = None
    """The base pds adoption, if this scenario uses a Fully Customized PDS Adoption (otherwise None)"""
    ref_ca: customadoption.CustomAdoption = None
    """The base ref adoption, if this scenario uses a Fully Customized reference adoption (otherwise None)"""
    sc: s_curve.SCurve = None
    """The base s-curve adoption, if this scenario uses an s-curve adoption (otherwise None)."""

    
    ##############################################################################################################
    # Initialization

    def initialize_ac(self, scenario_name_or_ac, scenario_list, default_scenario_name):
        """Initialize the advanced controls object for this scenario based on the various cases.
        The first argument may be an instantiated advanced controls argument, or a string naming
        the requested scenario, or None.  The second argument is a list of all the available named scenarios,
        and the last is the default scenario to use if None is given."""
        
        if isinstance(scenario_name_or_ac, advanced_controls.AdvancedControls):
            self.scenario = scenario_name_or_ac.name
            self.ac = scenario_name_or_ac
        else:
            self.scenario = scenario_name_or_ac or default_scenario_name
            alt_scenario = integration.integration_alt_name(self.scenario)
            if alt_scenario in scenario_list:
                self.scenario = alt_scenario

            self.ac = scenario_list[self.scenario]

    # Initialize Adoption
    # Control of adoption initialization is a combination of the contents of the ac parameters
    # and the settings of these fields by the subclass
    _ref_ca_sources = None  
    _pds_ca_sources = None 
    _pds_ca_settings = { 'high_sd_mult' : 1.0, 'low_sd_mult' : 1.0 }
    _pds_ad_sources = None
    _pds_ad_settings = { 'main_includes_regional' : True, 'groups_include_hundred_percent': True,
        'config_overrides' : None }
    

    def initialize_adoption_bases(self):
        """Initialize the pds and ref adoption bases for this scenario to one of 
        several different types, depending on the parameters of the scenario.
        Note this function only initializes the base ref and pds adoptions: the HelperTables
        object ht still needs to be initialized after."""

        # ###  Reference Adoption

        # handle the inline-override case
        if self.ac.ref_adoption_custom_source:
            self.ref_ca = customadoption.CustomAdoption(
                data_sources = [ {'name': 'Inline Ref Adoption', 'include': True, 'filename': self.ac.ref_adoption_custom_source}],
                soln_adoption_custom_name ='Inline Ref Adoption',
                total_adoption_limit= self.adoption_limit()
            )
            self.ac.soln_ref_adoption_basis = "Custom"
        
        elif self.ac.soln_ref_adoption_basis == "Custom" and not self.ref_ca:
            if not self._ref_ca_sources:
                raise ValueError("Custom Ref Adoption requires reference data sources")
            self.ref_ca = customadoption.CustomAdoption(
                data_sources = self._ref_ca_sources,
                soln_adoption_custom_name = self.ac.soln_ref_adoption_custom_name,
                total_adoption_limit = self.adoption_limit()
            )
        # For default reference adoption, we do nothing; HelperTables will
        # do all the work.

        # ###  PDS Adoption        

        # handle the inline-override case 
        if self.ac.pds_adoption_custom_source:
            sources = [ {'name': 'Inline PDS Adoption', 'include': True, 'filename': self.ac.ref_adoption_custom_source}],
            self.pds_ca = customadoption.CustomAdoption(
               data_sources = sources,
               soln_adoption_custom_name = 'Inline PDS Adoption',
               total_adoption_limit = self.adoption_limit()
            )
            # override the AC setting, so the rest of the code will use this adoption.
            self.ac.soln_pds_adoption_basis='Fully Customized PDS'      
        
        elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS' and not self.pds_ca:
            # scenarios can paramaterize which solutions should be included in the customized PDS
            sources = self._pds_ca_sources
            if self.ac.soln_pds_adoption_scenarios_included:
                sources = sources.copy()
                for (i,s) in enumerate(sources):
                    s['include'] = (i in self.ac.soln_pds_adoption_scenarios_included)
            
            self.pds_ca = customadoption.CustomAdoption(
                data_sources = sources,
                soln_adoption_custom_name = self.ac.soln_pds_adoption_custom_name,
                high_sd_mult = self._pds_ca_settings['high_sd_mult'],
                low_sd_mult = self._pds_ca_settings['low_sd_mult'],
                total_adoption_limit = self.adoption_limit()
            )
        
        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications' and not self.ad:
            overrides = [('trend','World',self.ac.soln_pds_adoption_prognostication_trend),
                         ('growth','World',self.ac.soln_pds_adoption_prognostication_growth)]
            overrides.extend(self._pds_ad_settings['config_overrides'] or [])
            adconfig = adoptiondata.make_adoption_config(overrides=overrides)
            self.ad = adoptiondata.AdoptionData(
                ac = self.ac,
                data_sources = self._pds_ad_sources,
                adconfig = adconfig,
                main_includes_regional = self._pds_ad_settings['main_includes_regional'],
                groups_include_hundred_percent = self._pds_ad_settings['groups_include_hundred_percent']
            )
        # else PASS
        # for now, classes are responsible for initializing s-curves themselves.


    def adoption_limit(self):
        """Returns the tam or aez limitations on adoption."""
        raise NotImplementedError("Subclass must implement")

    ##############################################################################################################
    #   
    # Functionality
    #
    # Commentary: Currently here's no clear line between which functionality we adopt at the top scenario level, 
    # vs. which is deferred to the subordinate objects like ua, ht, etc.  Things tend to get added at this top level
    # either because (a) we want to unify the functionality across multiple scenario types, or (b) we want a 
    # nice shorthand for something that is commonly used, or (c) its new stuff.  But at some point we should 
    # revisit and decide if there's a more clear-cut dividing line we can use.
    # 
    # "Key Results"   These reproduce the summary results that appeared in the top left corder of the
    # Advanced Controls tab in Excel.  They are a general way of characterizing the overall impact of a
    # scenario, and used to compare across multiple scenarios and/or solutions.
    #
    def adoption_unit_increase(self, year=None, region='World'):
        if year is None:
            year = self.ac.report_end_year
        return (self.ht.soln_pds_funits_adopted().loc[year][region]  - 
                self.ht.soln_ref_funits_adopted().loc[year][region])

    def marginal_first_cost(self, year=None):
        if year is None:
            year = self.ac.report_end_year
        if self.ac.soln_lifetime_replacement == 0.0 or self.ac.conv_lifetime_replacement == 0.0:
            return 0.0
        return (self.fc.soln_pds_annual_world_first_cost().loc[:year].sum()-
            self.fc.soln_ref_annual_world_first_cost().loc[:year].sum()-
            self.fc.conv_ref_annual_world_first_cost().loc[:year].sum()
            ) / 1e9

    def net_operating_savings(self, start_year=None, end_year=None):
        if start_year is None:
            start_year = self.ac.report_start_year
        if end_year is None:
            end_year = self.ac.report_end_year
        if self.ac.soln_lifetime_replacement == 0.0 or self.ac.conv_lifetime_replacement == 0.0:
            return 0.0
        return (
            (self.oc.conv_ref_cumulative_operating_cost().loc[end_year] -
            self.oc.conv_ref_cumulative_operating_cost().loc[start_year]) -
            (self.oc.soln_pds_cumulative_operating_cost().loc[end_year]  -
            self.oc.soln_pds_cumulative_operating_cost().loc[start_year])
            ) / 1e9

    def lifetime_operating_savings(self):
        if self.ac.soln_lifetime_replacement == 0.0 or self.ac.conv_lifetime_replacement == 0.0:
            return 0.0
        return self.oc.soln_marginal_operating_cost_savings().sum() / 1e9

    def cumulative_emissions_reduced(self, start_year=None, end_year=None, region='World'):
        if start_year is None:
            start_year = self.ac.report_start_year
        if end_year is None:
            end_year = self.ac.report_end_year
        return self.c2.co2eq_mmt_reduced().loc[start_year:end_year, region].sum() / 1e3

    # Additional Added Calculations

    def soln_net_energy_grid_impact(self) -> pd.DataFrame :
        """The net impact of this solution on the energy grid over time relative to the reference case.  
        This result may be positive (if the solution requires additional electricity to operate), negative (if the 
        adoption of this technology lowers energy use) or zero (if this solution doesn't impact the grid at all).
        Units: TWh"""
        # Chose between Excel tables Unit Adoption Calculations!B305 and Unit Adoption Calculations!Q305,
        # depending on the circumstance.
        result = (self.ua.soln_pds_net_grid_electricity_units_saved() *-1.0 
                    if self.ac.soln_energy_efficiency_factor else 
                  self.ua.soln_pds_net_grid_electricity_units_used())
        result.name = "soln_net_grid_energy_impact"
        return result
    
    
    # Integration support.  This is limited and hacky at this time.

    @classmethod
    def scenario_path(cls):
        return Path(__file__).parents[1]/"solution"/cls.module_name
        
    @classmethod
    def _pds_ca_lookup(cls, name):
        """Return the filename associated with a specific custom adoption, if we know it"""
        if cls._pds_ca_sources:
            for x in cls._pds_ca_sources:
                if x['name'] == name:
                    return x['filename'] if 'filename' in x else None
        return None

    @classmethod
    def update_adoptions(cls, scenario_names, newadoptions : pd.DataFrame):
        for (i, scenario_name) in enumerate(scenario_names):

            ca_pds_dir = cls.scenario_path()/"ca_pds_data"
            if not ca_pds_dir.is_dir():
                warnings.warn(f"Updating adoption has no affect on {cls.module_name} solution, since it does not implement file-based custom adoptions")
                return

            # get the existing scenario ac
            oldac : advanced_controls.AdvancedControls = factory.load_scenario(cls.module_name, scenario_name).ac 

            # define new adoption name and data file
            new_adoption_name = None
            new_file_name = None
            if oldac.soln_pds_adoption_basis == 'Fully Customized PDS':
                old_adoption_name = oldac.soln_pds_adoption_custom_name
                # Look up the adoption in _pds_ca.  If it is there, we'll use a modified version
                # of the adoption and filenames.  This fails for adoptions that don't have files, or
                # for adoptions of the form "Average of all..."
                old_file_name = cls._pds_ca_lookup(old_adoption_name)
                if old_file_name:
                    new_adoption_name = integration.integration_alt_name(old_adoption_name)
                    new_file_name = integration.integration_alt_file(old_file_name)
            if not new_adoption_name:
                # just generate one
                new_adoption_name = integration.integration_alt_name(f"new updated adoption {i}")
                new_file_name = integration.integration_alt_file(f"new_updated_adoption_{i}")
            
            # Write or overwrite the data file
            colname = newadoptions.columns[i]
            new_data = newadoptions[[colname]].rename(columns={colname: "World"})
            new_data.to_csv(ca_pds_dir/new_file_name, encoding="utf-8")

            # update or add this source to the custom adoption directory 
            sources = cls._pds_ca_sources or []
            for x in sources:
                if x['name'] == new_adoption_name: # update it
                    x['filename'] = new_file_name
                    break;
            else: # add it
                sources.append({
                    'name' : new_adoption_name,
                    'filename': new_file_name,
                    'include': True,
                    'description': f"updated integration adoption {i}"
                })
            # overwrite the directory file
            write_sources(sources, cls.scenario_path(), "pds_ca")

            # if necessary, update the scenario object as well.
            new_scenario_name = integration.integration_alt_name(oldac.name)
            if new_scenario_name == oldac.name and new_adoption_name == oldac.soln_pds_adoption_custom_name:
                # we've already updated this scenario before; don't need to do it again
                return

            new_scenario_file = Path(oldac.jsfile).name if oldac.jsfile else f"updated_integration_{i}.json"
            new_scenario_file = integration.integration_alt_file(new_scenario_file)
            ac_data = oldac.as_dict()
            ac_data['name'] = new_scenario_name
            ac_data['soln_pds_adoption_basis'] = 'Fully Customized PDS'
            ac_data['soln_pds_adoption_custom_name'] = new_adoption_name
            (cls.scenario_path()/"ac"/new_scenario_file).write_text(json.dumps(ac_data,indent=2), encoding="utf-8") 


class RRSScenario(Scenario):

    # State
    tm: tam.TAM = None
    """The total addressable market for this solution."""

    # Initialization
    # These must be set by each class
    _ref_tam_sources = None
    _pds_tam_sources = None

    def set_tam(self, config_values=None, **args):
        """Create the self.tm object based on the information in self._ref_tam_sources
        and self._pds_tam_sources.  
        
        Overrides to individual values in the tamconfig can also be specified
        in the config_values argument, which should be a list of tuples (param_name, region, value)

        Other configuration values may be passed directly to tam.TAM via **args.
        """
        tamconfig = tam.make_tam_config(overrides=config_values)
        tamconfig.loc['source_until_2014','World']     = self.ac.source_until_2014
        tamconfig.loc['source_until_2014','PDS World'] = self.ac.source_until_2014
        tamconfig.loc['source_after_2014','World']     = self.ac.ref_source_post_2014
        tamconfig.loc['source_after_2014','PDS World'] = self.ac.pds_source_post_2014

        ref_data_sources = self._ref_tam_sources
        pds_data_sources = self._pds_tam_sources
        
        # Handle the inline override case by completely overriding the relevant fields
        if self.ac.ref_tam_custom_source:
            #  Create a custom source structure for an inline source
            # HACK        
            # TAM doesn't auto-interpolate single sources.  But it does auto-interpolate groups.
            # So we use the sneaky hack of duplicating the source get TAM to do this work for us,
            # and as a result we can accept a TAM that doesn't have data at every point.
            # It keeps the code changes less invasive for now, but should be refactored later.
            name = 'Inline Tam'
            ref_data_sources = { 'Custom Cases' : { 
                    name : self.ac.ref_tam_custom_source,
                    name + 'dup' : self.ac.ref_tam_custom_source,
                    'include': True
                }}
            # set 'source_after_2014' for 'World' and all regions (everything except 'PDS World')
            pdsworld = tamconfig.loc['source_after_2014', 'PDS World']
            tamconfig.loc['source_after_2014',:] = 'Custom Cases'
            tamconfig.loc['source_after_2014','PDS World'] = pdsworld
        if self.ac.pds_tam_custom_source:
            name = 'Inline Tam'
            pds_data_sources = { 'Custom Cases' : { 
                    name : self.ac.pds_tam_custom_source,
                    name + 'dup' : self.ac.pds_tam_custom_source,
                    'include': True
                }}
            tamconfig.loc['source_after_2014','PDS World'] = 'Custom Cases'

        self.tm = tam.TAM(
            tamconfig=tamconfig, 
            tam_ref_data_sources = ref_data_sources,
            tam_pds_data_sources = pds_data_sources,
            **args)
        
    def adoption_limit(self):
        return self.tm.pds_tam_per_region()

    def get_key_results(self):
        return {'implementation_unit_adoption_increase': self.implementation_unit_adoption_increase(),
                'functional_unit_adoption_increase': self.adoption_unit_increase(),
                'marginal_first_cost': self.marginal_first_cost(),
                'net_operating_savings': self.net_operating_savings(),
                'lifetime_operating_savings': self.lifetime_operating_savings(),
                'cumulative_emissions_reduced': self.cumulative_emissions_reduced()}

    def implementation_unit_adoption_increase(self, year=2050, region='World'):
        if self.ac.soln_avg_annual_use == 0.0:
            return 0.0
        return (self.ht.soln_pds_funits_adopted().loc[year][region] / self.ac.soln_avg_annual_use - 
            self.ht.soln_ref_funits_adopted().loc[year][region] / self.ac.soln_avg_annual_use)

    def functional_unit_adoption_increase(self, year=2050, region='World'):
        return (self.ht.soln_pds_funits_adopted().loc[year] - 
                self.ht.soln_ref_funits_adopted().loc[year]
                )[region]

class LandScenario(Scenario):

    tla_per_region: pd.DataFrame = None
    """Total land area per region, by year.
    (Land area remains constant over time; this format is used because it is consistent with TAM)"""

    def adoption_limit(self):
        return self.tla_per_region

    def get_key_results(self):
        return {'adoption_unit_increase': self.adoption_unit_increase(),
                'marginal_first_cost': self.marginal_first_cost(),
                'net_operating_savings': self.net_operating_savings(),
                'lifetime_operating_savings': self.lifetime_operating_savings(),
                'cumulative_emissions_reduced': self.cumulative_emissions_reduced(),
                'total_additional_co2eq_sequestered': self.total_additional_co2eq_sequestered()}

    def total_additional_co2eq_sequestered(self, end_year=None):
        # farmlandrestoration starts in year 2021 in Advanced Control excel
        # Not sure if this is a bug or intended. Excel also says it should start at 2020
        if end_year is None:
            end_year = self.ac.report_end_year

        return (self.c2.co2_sequestered_global().loc[2021:end_year,'All'] / 1000).sum()


    
def load_sources(jsonfile, fieldname='filename'):
    """Load the named jsonfile, and replace relative filenames within it with absolute ones based on the same directory.
    Works for tam, ad, configs.  By default, replaces fields named 'filename'.  If the special
    field name '*' is given, then _any_ string-valued dictionary value is replaced.

    Now with added super-powers: detects if we are doing an integration, and if so, checks for the integration
    version of the same json file."""

    def rootstruct(struct, rootdir, fieldname):
        if isinstance(struct, list):
            for i in range(len(struct)):
                rootstruct(struct[i], rootdir, fieldname)
        elif isinstance(struct, dict):
            for k in struct.keys():
                if k == fieldname or (fieldname == '*' and isinstance(struct[k],str)):
                    f = Path(struct[k])
                    if not f.is_absolute():
                        struct[k] = str(rootdir / f)
                elif isinstance(struct[k],dict) or isinstance(struct[k], list):
                    rootstruct(struct[k], rootdir, fieldname)

    # if we are supposed to use an alternate version, and that version exists, use it.
    jsonfile = Path(jsonfile).resolve()
    alternatejsonfile = integration.integration_alt_file(jsonfile)
    if alternatejsonfile.is_file():
        jsonfile = alternatejsonfile

    struct = json.loads( jsonfile.read_text(encoding='utf-8') )
    rootstruct(struct, jsonfile.parent, fieldname)
    return struct

def write_sources(struct, solution_path, source_type):
    """Write a data sources structure out to its standard location for solution_name.  Processes filename
    fields to write only the relative file name.  Also remove any fields that have values that are not simple.
    This is rather hacky, and we should implement more careful control later.
    """
    def clean(struct, fieldname):
        result = struct.copy()
        if isinstance(result, list):
            for i in range(len(result)):
                result[i] = clean(result[i], fieldname)
        elif isinstance(result, dict):
            for k in list(result.keys()):
                if k == fieldname or (fieldname == '*' and isinstance(result[k], str) or isinstance(result[k], Path)):
                    result[k] = str(Path(result[k]).name)
                elif isinstance(struct[k], dict) or isinstance(struct[k], list):
                    result[k] = clean(result[k], fieldname)
                elif not (isinstance(result[k], str) or isinstance(result[k],numbers.Number)):
                    del result[k]
        return result

    # map source_type onto the standard directory and name.
    dirs = {'pds_tam': 'tam', 'ref_tam': 'tam', 
            'pds_ca': 'ca_pds_data', 'ref_ca': 'ca_ref_data', 'ad': 'ad'}
    filenames = {'pds_tam': 'tam_pds_sources.json', 'ref_tam': 'tam_ref_sources.json',
                 'pds_ca': 'ca_pds_sources.json', 'ref_ca': 'ref_pds_sources.json', 'ad': 'ad_sources.json'}
    
    fieldname = 'filename' if source_type in ['ca_pds','ca_ref'] else '*'
    cleaned = clean(struct, fieldname)
    thedir = solution_path/dirs[source_type]
    thedir.mkdir(exist_ok=True)
    filename = integration.integration_alt_file(filenames[source_type])
    (thedir/filename).write_text( json.dumps(cleaned, indent=2), encoding='utf-8')


