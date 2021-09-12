from pathlib import Path
import pandas as pd
from . import integration
from model import advanced_controls as ac
from model import aez
from model import dd
from model import vma
from model import world_land
from solution import factory


standard_land_allocation_types = list(world_land.AEZ_ALLOCATION_MAP.keys()) + ["Add-On Solutions"]

standard_land_solution_priorities = {
    'Non-Degraded Forest':    
        ['peatland', 'mangroverestoration', 'indigenouspeoplesland', 'forestprotection', 'multistrataagroforestry'],
    'Degraded Forest':        
        ['tropicalforests', 'temporateforests', 'BOREAL FOREST', 'peatland', 'mangroverestoration', 'bamboo', 'afforestation'],
    'Non-Degraded Grassland': 
        ['peatland', 'grasslandprotection', 'multistrataagroforestry', 'tropicaltreestaples', 'silvopasture', 'managedgrazing'],
    'Degraded Grassland':     
        ['afforestation', 'farmlandrestoration', 'perennialbioenergy'],
    'Non-Degraded Cropland':  
        ['tropicalforests', 'peatland', 'riceintensification', 'improvedrice', 'conservationagriculture', 'treeintercropping'],
    'Degraded Cropland':      
        ['treeintercropping'],
    'Add-On Solutions':      
        ['improvedcattlefeed', 'regenerativeagriculture', 'irregationefficiency', 'nutrientmanagement', 'SUSTAINABLE INTENSIFICATION']
}
"""The prioritization amongst Land solutions for access to land in each land allocation type.
Any land solution not on this list will be assumed to be lower priority than these."""
# UPPER CASE are items in the integration workbook that don't correspond to any solution known to me:
# BOREAL FOREST, SUSTAINABLE INTENSIFICATION

# VMAS={
#     'Current Adoption': vma.VMA(
#         filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
#         use_weight=False)
# }


class AEZ_Land_Integration:
    """The AEZ / Land Integration looks at competition between LAND solutions for land of different types, 
    and adjusts land availability accordingly.
    """

    def assemble_current_status(self, scenario_list=None):
        """Perform the first step of the integration, which is to collate the current adoptions of all
        the scenarios across all allocation regions and TMRs.  By default, the drawdown PDS2 scenario is
        used for all Land solutions.  An alternative list (with differing solutions and/or scenario choices)
        may be provided instead.
        """
        if scenario_list:
            self.scenario_list = scenario_list
            self.solution_list = [ _map_scenario_to_module(scenario) for scenario in self.scenario_list ]
        else:
            self.solution_list = factory.all_solutions_category(ac.SOLUTION_CATEGORY.LAND)
            self.scenario_list = [ factory.solution_pds_type(x, "PDS2") for x in self.solution_list ]
        
        
        self.world_land_availability = world_land.World_TMR_AEZ_Map(series_name="2020")
        #).reduce_columns(world_land.AEZ_ALLOCATION_MAP)
        
        per_solution_allocations  = {}
        for scenario in self.scenario_list:
            sc_dict = scenario.ae.world_land_alloc_dict
            per_solution_allocations[scenario.name] = pd.concat( sc_dict.values(), keys=sc_dict.keys() )
        
        self.all_solution_allocations = pd.concat( per_solution_allocations.values(), keys=per_solution_allocations.keys() )
    
        # What we want is triple-index (allocation_zone, solution, tmr) and these columns 
        #    "Total Area", "Area Available for Solution", "Solution Current Adoption", "Solution Current Adoption %",
        #    ... more stuff.  Let's start there.

        # Then we have to sort the data by priority within the different Landtypes

        
        





def _map_scenario_to_module(scenario):
    """Given a scenario, return the common module name (e.g. 'afforestation') of the solution"""
    fullmodule = scenario.__module__
    period = fullmodule.rfind('.')
    return fullmodule[period+1:]
