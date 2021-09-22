import pandas as pd
from pathlib import Path
from model import vma
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


def gather_emissions_factors():
    """Return a dictionary of emissions factors (average, high, low) for each energy type, including conventional sources"""

    testdata = load_testmode_snapshot("emissions_factors")
    if testdata:
        return { x[0] : x[1:] for x in [y.split(',') for y in testdata.splitlines()] }

    # else, collect the data from the VMAs
    emissions_factors = {
        # conventional
        'coal':         vma.VMA( DATADIR/"COAL_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
        'natural gas':  vma.VMA( DATADIR/"NATURAL_GAS_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
        'large hydro':  vma.VMA( DATADIR/"HYDRO_Indirect_CO2_Emissions.csv", stat_correction=True, bound_correction=True).avg_high_low(),
        'oil products': vma.VMA( DATADIR/"OIL_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
    }
    for soln in energy_solutions:
        v = factory.solution_vma(soln, 'SOLUTION Indirect CO2 Emissions per Unit')
        if v:
            # See if we have to correct the units; our standardized units are g CO2-eq/kWh
            if v.units == 't CO2-eq/TWh':
                unit_factor = 1e-3
            else:
                unit_factor = 1
        
            emissions_factors[soln] = [ x*unit_factor for x in v.avg_high_low(bound_correction=True) ]
        else:
            print(f"Solution {soln} missing 'Indirect CO2 Emissions' VMA; skipping for emissions factor analysis")
    
    return emissions_factors


def gather_net_grid_use() -> pd.DataFrame:
    """Gather net electricity grid use from all solutions for all PDS1/2/3 scenarios.
    Returns a DataFrame with years index and (solutions) x (pds1/2/3) columns"""

    collect = {}
    for x in ["electricvehicles","residentialglass"]:
        s1 = factory.load_scenario(x, scenario_names[x][0])
        s2 = factory.load_scenario(x, scenario_names[x][1])
        s3 = factory.load_scenario(x, scenario_names[x][2])
        collect[x] = pd.DataFrame({
            "PDS1": s1.soln_net_energy_grid_impact()['World'],
            "PDS2": s2.soln_net_energy_grid_impact()['World'],
            "PDS3": s3.soln_net_energy_grid_impact()['World']})
    
    return collect


