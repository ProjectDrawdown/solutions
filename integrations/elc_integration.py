from io import StringIO
import pandas as pd
from pathlib import Path
from model import vma
from datetime import datetime
from dataclasses import dataclass
from model import integration
from integrations.integration_base import *

THISDIR=Path(__file__).parent
DATADIR=THISDIR/"data"/"elc"


# The energy solutions.  If any new energy solutions are added, be sure to add them to the list below.

conventional_plus_hydro = ["coal", "natural gas", "large hydro", "oil products"]
energy_solutions=["onshorewind","offshorewind","solarpvutil","solarpvroof","concentratedsolar","geothermal","waveandtidal",
                  "biomass","microwind","instreamhydro","nuclear","wastetoenergy","landfillmethane","biogas"]
 
energy_sectors = {
    "hydro" : ["large hydro", "instreamhydro"],
    "solar pv" : ["solarpvutil", "solarpvroof"],
    "biomass and waste" : ["biogas","biomass","landfillmethane","wastetoenergy"]
}


# ########################################################################################################################
#                                              State tracking

audit = start_audit("elc")
# The audit log stores results that are computed throughout the process.  It is *append only*.  
# It is never read or modified by this code.  Enables debugging and analysis by users.


@dataclass
class elc_integration_state:
    # This data class holds global variables that are shared between steps.  Embedding it in a class
    # enables us to avoid having to declare 'global' anytime we want to change something.

    integration_year = None
    historical_grid_mix : pd.DataFrame = None
    current_grid_mix : pd.DataFrame = None
elc = elc_integration_state()

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

    testdata = load_testmode_snapshot("NetGridUse.csv")
    if testdata:
        # TODO: how do you read a multi-level header?
        return pd.read_csv(testdata)

    collect = {}
    for x in factory.all_solutions():
        s1 = factory.load_scenario(x, scenario_names[x][0])
        s2 = factory.load_scenario(x, scenario_names[x][1])
        s3 = factory.load_scenario(x, scenario_names[x][2])
        collect[x] = pd.DataFrame({
            "PDS1": s1.soln_net_energy_grid_impact()['World'],
            "PDS2": s2.soln_net_energy_grid_impact()['World'],
            "PDS3": s3.soln_net_energy_grid_impact()['World']})
    
        # drop no-op solutions
        if collect[x].sum().sum() == 0:
            del(collect[x])

    return pd.concat(collect, axis=1)


def load_historical_grid_mix():
    testdata = load_testmode_snapshot("GridMix.csv")
    if testdata:
        filename = StringIO(testdata)  # It ain't stupid if it works
    else:
        filename = DATADIR/"GridMix.csv"
        altfilename = integration.integration_alt_file(filename)
        if altfilename.is_file():
            filename = altfilename

    df = pd.read_csv(filename, index_col="technology")
    elc.historical_grid_mix = calc_grid_mix_percentages(df)
    audit("historical grid mix", elc.historical_grid_mix)


def calc_grid_mix_percentages(df):
    """Given a series or dataframe grid mix, calculate or update the percentages based on the major-technology totals"""

    # First lets get the df into a shape we can handle.  This will remove the top level off 
    # a hierarchical index, or select the proper column out of a flat one.  If there are 
    # multiple years present, they stay present.  It passes series through unharmed.
    try:
        df = df['total'] 
    except:
        pass

    # OK, now we are ready to compute percentages.  There's a weird thing: in the spreadsheet
    # the sum is taken only over a subset of the technologies.  There is some double counting
    # in the list (biomass sector as well as individual technologies), but the sum does seem to
    # miss some technologies (e.g.  microwind).  Maybe they are too small to matter.  
    # TODO: when we use the numbers, see if this makes sense (or makes any difference), in context.

    toplevelsolns = ['coal','oil products','natural gas','nuclear','large hydro','waveandtidal',
                     'onshorewind','offshorewind','biomass and waste','concentratedsolar',
                     'geothermal','solarpvutil','solarpvroof']

    totals = df.loc[toplevelsolns].sum()  
    dfpercent = df / totals
    return pd.concat( {'total' : df, 'percent': dfpercent}, axis=1)


def grid_mix_for_year(year) -> pd.DataFrame:
    """Return the grid mix for a particular year"""
    df = elc.historical_grid_mix.swaplevel(axis=1)
    return df[str(year)]


# ########################################################################################################################
#                                              Action
#
#  PHASE ONE: UPDATE THE GRID MIX, COSTS and EMISSIONS FACTORS

def phase1_setup(integration_year=None):
    elc.integration_year = integration_year or datetime.now().year
    load_historical_grid_mix()
    try:
        cymix = grid_mix_for_year(elc.integration_year)
        elc.current_grid_mix = cymix
        print(f"Previously defined grid mix loaded for year {elc.integration_year}")
    except:
        # TODO: calculate this
        print(f"Grid mix initialized to extrapolation from previous years")


def set_as_current_grid_mix(newmix: pd.DataFrame):
    """Save the current grid mix as the accepted grid mix for this year.  Percentages will be updated automatically."""
    
    # save it to internal state
    newmix = calc_grid_mix_percentages(newmix)
    elc.current_grid_mix = newmix
    audit("updated grid mix", newmix)

    # recreate the historical grid mix structure we want to save to the file
    histmix = elc.historical_grid_mix['total'].copy()
    histmix[elc.integration_year] = newmix['total']
    histfile = integration.integration_alt_file(DATADIR/"GridMix.csv")
    histmix.to_csv(histfile)
    print(f"Updated grid mix saved to {histfile}")

    # and finally, make our in-memory version consistent
    elc.historical_grid_mix = calc_grid_mix_percentages(histmix)




