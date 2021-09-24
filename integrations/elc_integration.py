from io import StringIO
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from model import integration
from model import scenario
from model import tam
from model import vma
from solution import factory
from integrations.integration_base import *

thisdir=Path(__file__).parent.resolve()
datadir=(thisdir/"data"/"elc").resolve()
public_datadir = (thisdir.parent/"data"/"energy").resolve()


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
    reference_tam : pd.DataFrame = None
    pds_tam : pd.DataFrame = None
    historical_grid_mix : pd.DataFrame = None
    current_grid_mix : pd.DataFrame = None
    emissions_factors : pd.DataFrame = None
    net_grid_use : pd.DataFrame = None
elc = elc_integration_state()

# ########################################################################################################################
#                                              Data Collection

def load_reference_tam():
    testdata = load_testmode_snapshot("reference_tam.csv")
    if testdata:
        elc.reference_tam = pd.read_csv(StringIO(testdata),index_col=0)
    else:
        tamconfig = tam.make_tam_config(overrides=[
            ('source_until_2014','World',"Baseline Cases"),
            ('source_after_2014','World',"Baseline Cases")
            ])
        tam_sources = scenario.load_sources(public_datadir/"ref_tam_2_sources.json", '*')
        tam_object = tam.TAM(tamconfig, tam_sources, tam_sources)
        elc.reference_tam = tam_object.ref_tam_per_region()['World']
    audit("reference tam", elc.reference_tam)
    

def load_emissions_factors():
    """Return a dictionary of emissions factors (average, high, low) for each energy type, including conventional sources"""

    testdata = load_testmode_snapshot("emissions_factors")
    if testdata:
        basedata = { x[0] : x[1:] for x in [y.split(',') for y in testdata.splitlines()] }

    else:
        basedata = {
            # conventional
            'coal':         vma.VMA( datadir/"COAL_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
            'natural gas':  vma.VMA( datadir/"NATURAL_GAS_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
            'large hydro':  vma.VMA( datadir/"HYDRO_Indirect_CO2_Emissions.csv", stat_correction=True, bound_correction=True).avg_high_low(),
            'oil products': vma.VMA( datadir/"OIL_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
        }
        for soln in energy_solutions:
            v = factory.solution_vma(soln, 'SOLUTION Indirect CO2 Emissions per Unit')
            if v:
                # See if we have to correct the units; our standardized units are g CO2-eq/kWh
                if v.units == 't CO2-eq/TWh':
                    unit_factor = 1e-3
                else:
                    unit_factor = 1
            
                basedata[soln] = [ x*unit_factor for x in v.avg_high_low(bound_correction=True) ]
            else:
                print(f"Solution {soln} missing 'Indirect CO2 Emissions' VMA; skipping for emissions factor analysis")
    
    elc.emissions_factors = pd.DataFrame(basedata)
    audit("emissions factors", elc.emissions_factors)


def load_net_grid_use() -> pd.DataFrame:
    """Gather net electricity grid use from all solutions for all PDS1/2/3 scenarios.
    Returns a DataFrame with years index and (solutions) x (pds1/2/3) columns"""

    testdata = load_testmode_snapshot("grid_impact_pds1.csv")
    if testdata:
        # stored in three files for easier cut-pasting from Excel
        df1 = pd.read_csv(StringIO(testdata), index_col=0).rename(columns=factory.find_solution_by_name)
        testdata = load_testmode_snapshot("grid_impact_pds2.csv")
        df2 = pd.read_csv(StringIO(testdata), index_col=0).rename(columns=factory.find_solution_by_name)
        testdata = load_testmode_snapshot("grid_impact_pds3.csv")
        df3 = pd.read_csv(StringIO(testdata), index_col=0).rename(columns=factory.find_solution_by_name)
        df = pd.concat({'PDS1': df1, 'PDS2': df2, 'PDS3': df3}, axis=1).swaplevel(axis=1)
        df.columns = df.columns.sort_values()
    else:
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
        
        df = pd.concat(collect, axis=1)
    elc.net_grid_use = df
    audit("net grid use", elc.net_grid_use)


def load_historical_grid_mix():
    testdata = load_testmode_snapshot("GridMix.csv")
    if testdata:
        filename = StringIO(testdata)
    else:
        filename = datadir/"GridMix.csv"
        altfilename = integration.integration_alt_file(filename)
        if altfilename.is_file():
            filename = altfilename

    df = pd.read_csv(filename, index_col=0)
    # replace string column headers with integers to avoid confusion later
    df.columns = [ int(c) for c in df.columns ]
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
    return df[year]


# ########################################################################################################################
#                                              Action
#
#  We're going to have an interesting dynamic here.  For waste integration we could delay updating files until the 
#  very end.  But in this case I think we are going to end up writing out things like the updated TAM early, so that
#  solutions will use it.  But then we want to avoid recaclculating it, if we've udpated it already.
#  Have to think about this.
#  

def setup(year):
    elc.integration_year = year
    print(f"Integration year set to {year}")


def step1_calculate_TAM():
    """Calculate the updated energy TAM"""
    load_reference_tam()
    load_net_grid_use()
    # The PDS tam is the REF tam with adjustments based on PDS1/2/3 scenarios of the technologies
    df = elc.net_grid_use.swaplevel(axis=1)
    pds1 = df['PDS1'].sum(axis=1)
    pds2 = df['PDS2'].sum(axis=1)
    pds3 = df['PDS3'].sum(axis=1)
    demand_delta = pd.concat({"PSD1": pds1, "PDS2": pds2, "PDS3": pds3}, axis=1)
    audit("grid demand delta",demand_delta)
    elc.pds_tam = demand_delta.add(df, axis=0)
    audit("pds tam", elc.pds_tam)


def step2_calculate_emissions():
    # check before loading because this function might get called multiple times as user experiments with
    # current_grid_mix
    if elc.emissions_factors is None:
        load_emissions_factors()
    if elc.historical_grid_mix is None:
        load_historical_grid_mix()
    
    try:
        cymix = grid_mix_for_year(elc.integration_year)
        elc.current_grid_mix = cymix
        print(f"Previously defined grid mix loaded for year {elc.integration_year}")
    except:
        message = """The grid mix for YEAR1 must be set before continuing.  The most recent grid mix is available as 
        grid_mix_for_year(YEAR2), and a projection from that mix as TODO.
        When you are have a satisfactory mix, set it as the current grid mix with set_as_current_grid_mix(newmix)"""
        message = message.replace("YEAR2", max(elc.historical_grid_mix['total']).columns).replace("YEAR1",elc.integration_year)
        print(message)


def set_as_current_grid_mix(newmix: pd.DataFrame):
    """Save the new grid mix as the accepted grid mix for this year.  Percentages will be updated automatically."""
    
    # save it to internal state
    newmix = calc_grid_mix_percentages(newmix)
    elc.current_grid_mix = newmix
    audit("updated grid mix", newmix)

    # recreate the historical grid mix structure we want to save to the file
    histmix = elc.historical_grid_mix['total'].copy()
    histmix[elc.integration_year] = newmix['total']
    histfile = integration.integration_alt_file(datadir/"GridMix.csv")
    histmix.to_csv(histfile)
    print(f"Updated grid mix saved to {histfile.resolve()}")

    # and finally, make our in-memory version consistent
    elc.historical_grid_mix = calc_grid_mix_percentages(histmix)




