import pandas as pd
from pathlib import Path
from model import vma
from solution.factory import solution_path
from model.integration import integration_alt_file
from integrations.integration_base import *

THISDIR=Path(__file__).parent
DATADIR=THISDIR/"data"/"elc"


# ########################################################################################################################
#                                              State tracking

audit = start_audit("elc")
# The audit log stores results that are computed throughout the process.  It is *append only*.  
# It is never read or modified by this code.  Enables debugging and analysis by users.


# The energy solutions.  If any new energy solutions are added, be sure to add them to the list below.

conventional_plus_hydro = ["coal", "natural gas", "large hydro", "oil products"]
energy_solutions=["onshorewind","offshorewind","solarpvutil","solarpvroof","concentratedsolar","geothermal","waveandtidal",
                  "biomass","microwind","instreamhydro","nuclear","wastetoenergy","landfillmethane","biogas"]




# ########################################################################################################################
#                                              Data Collection


def get_emissions_factors():
    """Return a dictionary of emissions factors (average, high, low) for each energy type, including conventional sources"""

    testdata = load_testmode_snapshot("emissions_factors")
    if testdata:
        return { x[0] : x[1:] for x in [y.split(',') for y in testdata.splitlines()] }

    # else, collect the data from the VMAs
    emissions_factors = {
        # conventional
        'coal':         vma.VMA( DATADIR/"COAL_Emissions_Factor.csv" ),
        'natural gas':  vma.VMA( DATADIR/"NATURAL_GAS_Emissions_Factor.csv" ),
        'large hydro':  vma.VMA( DATADIR/"HYDRO_Indirect_CO2_Emissions.csv" ),
        'oil products': vma.VMA( DATADIR/"OIL_Emissions_Factor.csv" ),
    }
    for soln in energy_solutions:
        filename = solution_path(soln)/"vma_data/SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"
        emissions_factors[soln] = vma.VMA( filename )
    
    # replace each VMA with it's summary
    return { k : v.avg_high_low() for (k,v) in emissions_factors.items() }



def gather_adoptions():
    """Gather adoptions for all sources, including conventional sources"""

    adoptions = {

    }
