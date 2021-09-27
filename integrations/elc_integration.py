from io import StringIO
import json
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
    "biomass and waste" : ["biogas","biomass","landfillmethane","wastetoenergy","other biomass"]
}


# ########################################################################################################################
#                                              State tracking

audit = start_audit("elc")
# The audit log stores results that are computed throughout the process.  It is *append only*.  
# It is never read or modified by this code.  Enables debugging and analysis by users.


@dataclass
class elc_integration_state:
    
    # supporting info

    integration_year = None                         
    historical_grid_mix : pd.DataFrame = None       # year x (source x (total,percent)), Units TWh, %.    Excel Tab 1
    current_grid_mix : pd.DataFrame = None          # source x (total,percent), Units TWh, %.   Excel Tab 1, column Z
    emissions_factors : pd.DataFrame = None         # source x (avg,high,low), Units g CO2-eq/kWh.  Excel Tab 2B, B22:W24
    net_grid_use : pd.DataFrame = None              # year x (solution x PDS123), Units TWh.  Excel tabs 3E, 3F, 3G

    # Energy TAMs, Units TWh
    
    ref_tam_sources : dict = None                   # TAM data structrue (SMA)in
    reference_tam : pd.DataFrame = None             # year series, Units TWh.    Excel Tab 3D column X
    integrated_tam : pd.DataFrame = None            # year x PDS123, Units TWh.  Excel Tab 5B, columns AW:AY

    # Adoption of energy sources
    # Raw adoption units are TWh, the final adoption table units are % TAM

    coal_raw_adoption : pd.DataFrame = None         # year x BCA100%   Excel Tab 5A, columns BC:BF
    ng_raw_adoption : pd.DataFrame = None           # year x BCA100%   Excel Tab 5A, columns BC:BF
    hydro_raw_adoption : pd.DataFrame = None        # year x BCA100%   Excel Tab 5A, columns BC:BF
    oil_raw_adoption : pd.DataFrame = None          # year x BCA100%   Excel Tab 5A, columns BC:BF
    es_raw_adoption : pd.DataFrame = None           # year x (all solution sources x PDS123)  
                                                    #          Excel Tabs 5B, 5C, 5D, columns BF:CF
    
    ref_adoption : pd.DataFrame = None              # year x source, Units % ref TAM   Excel 
    pds_adoption: pd.DataFrame = None               # year x (source x PDS123), Units % integrated TAM 

    # Emissions

    ref_grid_emissions : pd.DataFrame = None        # year series, Units ??, Excel tab 2E, columns A#:AH
    pds_grid_emissions:  pd.DataFrame = None        # year x PDS123, Units ??, Excel tab 2E, columns AK:Az

es = elc_integration_state()

# ########################################################################################################################
#                                       Data Collection and Supporting Functions
#
#  Grid Mix

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
    es.historical_grid_mix = calc_grid_mix_percentages(df)
    audit("historical grid mix", es.historical_grid_mix)


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
    df = es.historical_grid_mix.swaplevel(axis=1)
    return df[year]


def set_as_current_grid_mix(newmix: pd.DataFrame):
    """Save the new grid mix as the accepted grid mix for this year.  Percentages will be updated automatically."""
    
    # save it to internal state
    newmix = calc_grid_mix_percentages(newmix)
    es.current_grid_mix = newmix
    audit("updated grid mix", newmix)

    # recreate the historical grid mix structure we want to save to the file
    histmix = es.historical_grid_mix['total'].copy()
    histmix[es.integration_year] = newmix['total']
    histfile = integration.integration_alt_file(datadir/"GridMix.csv")
    histmix.to_csv(histfile)
    print(f"Updated grid mix saved to {histfile.resolve()}")

    # and finally, make our in-memory version consistent
    es.historical_grid_mix = calc_grid_mix_percentages(histmix)



def load_reference_tam_sources():
    testdata = load_testmode_snapshot("reference_tam_sources.json")
    if testdata:
        es.ref_tam_sources = json.loads(testdata)
    else:
        es.ref_tam_sources = scenario.load_sources(public_datadir/"ref_tam_2_sources.json", '*')


def calc_energy_tam(case):
    """Reutrn the TAM represented by the case"""
    tamconfig = tam.make_tam_config(overrides=[
        ('source_until_2014','World',"Baseline Cases"),
        ('source_after_2014','World',case)
        ])
    tam_object = tam.TAM(tamconfig, es.ref_tam_sources, es.ref_tam_sources)
    return tam_object.ref_tam_per_region()['World']
    

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
    es.net_grid_use = df
    audit("net grid use", es.net_grid_use)

# Emissions

def load_emissions_factors():
    """Load (average, high, low) emissions factors for each energy type, including conventional sources"""

    testdata = load_testmode_snapshot("emissions_factors")
    if testdata:
        basedata = { x[0] : x[1:] for x in [y.split(',') for y in testdata.splitlines()] }

    else:
        basedata = {
            # conventional, and an "extra"
            'coal':         vma.VMA( datadir/"COAL_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
            'natural gas':  vma.VMA( datadir/"NATURAL_GAS_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
            'large hydro':  vma.VMA( datadir/"HYDRO_Indirect_CO2_Emissions.csv", stat_correction=True, bound_correction=True).avg_high_low(),
            'oil products': vma.VMA( datadir/"OIL_Emissions_Factor.csv", stat_correction=False, bound_correction=True).avg_high_low(),
            'other biomass': (621.545, 901.95, 457.024)  # copied from 5B EH65:EH67
        }
        for soln in energy_solutions:
            v = factory.solution_vma(soln, 'SOLUTION Indirect CO2 Emissions per Unit')

            # See if we have to correct the units; our standardized units are g CO2-eq/kWh
            if v.units == 't CO2-eq/TWh':
                unit_factor = 1e-3
            else:
                unit_factor = 1
        
            basedata[soln] = [ x*unit_factor for x in v.avg_high_low(bound_correction=True) ]
    
    es.emissions_factors = pd.DataFrame(basedata, index=["avg","high","low"]).transpose()
    audit("emissions factors", es.emissions_factors)



# ########################################################################################################################
#                                              Action
#
#  We're going to have an interesting dynamic here.  For waste integration we could delay updating files until the 
#  very end.  But in this case I think we are going to end up writing out things like the updated TAM early, so that
#  solutions will use it.  But then we want to avoid recaclculating it, if we've udpated it already.
#  Have to think about this.
#  

def setup(year):
    es.integration_year = year
    print(f"Integration year set to {year}")

    # Get current grid mix, or let the user know we need it.
    load_historical_grid_mix()
    try:
        cymix = grid_mix_for_year(es.integration_year)
        es.current_grid_mix = cymix
        audit("current grid mix", es.current_grid_mix)
        print(f"Previously defined grid mix loaded for year {es.integration_year}")
    except:
        message = """The grid mix for YEAR1 must be set before continuing.  The most recent grid mix is available as 
        grid_mix_for_year(YEAR2), and a projection from that mix as TODO.
        When you are have a satisfactory mix, set it as the current grid mix with set_as_current_grid_mix(newmix).
        Then re-execute this step."""
        message = message.replace("YEAR2", max(es.historical_grid_mix['total']).columns).replace("YEAR1",es.integration_year)
        print(message)
        return


def step1_calculate_tams():
    """Calculate the energy TAMs"""
 
    load_reference_tam_sources()
    es.reference_tam = calc_energy_tam("Baseline Cases")
    audit("reference tam", es.reference_tam)

    # Anticipated energy impact of _all_ solutions under each sceanrio type.
    load_net_grid_use()
    df = es.net_grid_use.swaplevel(axis=1)
    pds1 = df['PDS1'].sum(axis=1)
    pds2 = df['PDS2'].sum(axis=1)
    pds3 = df['PDS3'].sum(axis=1)
    demand_delta = pd.concat({"PDS1": pds1, "PDS2": pds2, "PDS3": pds3}, axis=1)
    audit("grid demand delta",demand_delta)

    # The PDS TAM is the reference tam adjusted by the demand delta.
    # We currently only use the PDS1 result of this TAM (see below), but 
    # calculate the shole thing anyway because its easy enough to do.
    pds_tam = demand_delta.add(es.reference_tam, axis=0)
    audit("pds tam", pds_tam)  #Excel Tabs 3E, 3F, 3G column CK

    # For the integrated TAM, we take the the PDS1 tam for the PDS1 case, but the 100% RES
    # TAM for the PDS2 and PDS3 cases
    opttam = calc_energy_tam("100% RES2050 Case")
    es.integrated_tam = pd.concat({'PDS1': pds_tam['PDS1'], 'PDS2': opttam, 'PDS3': opttam}, axis=1)
    audit("integrated tam", es.integrated_tam)  # Excel TAb 5B, columns AW:AY


def step2_calculate_adoptions():
    # Reference adoption assumes that solution technologies make no progress beyond
    # where they are today
    # PDS Adoption is the adoption of the solutions *at the level of ambitiousness we
    # have chosen* for that scenario.  That is, the adoption of a solution (like nuclear)
    # might be different for PDS3 than the Ambitious or 100% RES case for nuclear.
    # This is used to discount solutions that we regard as bridge solutions.

    # raw conventional adoptions.
    # TEMPORARY SNAPSHOT.  The outcome of SMA evaluation on the source analysis of 
    # the conentional technologies.  Should be replaced by true SMA evalutation.
    es.coal_raw_adoption = pd.read_csv(datadir/"COAL_Adoption.csv",index_col="Year")
    es.ng_raw_adoption = pd.read_csv(datadir/"NATURAL_GAS_Adoption.csv",index_col="Year")
    es.hydro_raw_adoption = pd.read_csv(datadir/"HYDRO_Adoption.csv",index_col="Year")
    es.oil_raw_adoption = pd.read_csv(datadir/"OIL_Adoption.csv",index_col="Year")

    # Ref adoption has two components:
    # for the conventional sources, we use meta analysis of sources
    conventional = pd.concat({
        'coal' : es.coal_raw_adoption['Baseline Cases'],
        'natural gas' : es.ng_raw_adoption['Baseline Cases'],
        'large hydro' : es.hydro_raw_adoption['Baseline Cases'],
        'oil products' : es.oil_raw_adoption['Baseline Cases']}, axis=1)
    percents = conventional.div(es.reference_tam, axis=0)

    # for solution sources, we take the current grid mix and assume that it will be unchanged over time
    pcnt = lambda s : es.current_grid_mix.loc[s,'percent']
    for soln in energy_solutions:
        percents[soln] = pcnt(soln)
    
    # Finally, add a column for "other biomass", which is the remainder after taking into
    # account the solutions in the biomass sector
    # We need this because we know that the biomass sector consists of more than just
    # the solutions we model, by a significant degree.
    percents['other biomass'] = pcnt('biomass and waste') - (
            pcnt('biogas') + pcnt('biomass') + pcnt('landfillmethane') + 
            pcnt('wastetoenergy'))

    es.ref_adoption = percents
    audit("ref adoption (of energy sources)", es.ref_adoption)

    # PDS adoption: use PDS solution values and integrated TAM.
    # Conventional PDS values are complicated; they involve adjusting "buffer" sources 
    # natural gas and hydro to fit declining TAM, and also some overrides that I don't 
    # understand. So for now:
    # TEMPORARY SNAPSHOT: load the % values from columns CO:DB for the PDS
    # (also includes values for "other biomass")
    conventional = pd.read_csv(datadir/"conventional_pds_adoption.csv",index_col=0,header=[0,1])

    solutional = pd.concat( {
        soln : load_solution_adoptions(soln) for soln in energy_solutions
    }, axis=1).swaplevel(axis=1)
    # I'm sure there's a clever way to do this with only one pandas operation, but this works too.
    solutional = pd.concat( {
        'PDS1' : solutional['PDS1'].div(es.integrated_tam['PDS1'], axis=0),
        'PDS2' : solutional['PDS2'].div(es.integrated_tam['PDS2'], axis=0),
        'PDS3' : solutional['PDS3'].div(es.integrated_tam['PDS3'], axis=0)
    }, axis=1)

    es.pds_adoption = pd.concat([conventional, solutional], axis=1)
    audit("pds adoption", es.pds_adoption)



def step3_calculate_emissions():
    # Calculate the results of TAB 2C
    
    # The fundamental emission equation is sum over energy sources s of
    #    emissions factor(s) * adoption share(s)
    #
    # Currently emissions factors are considered constant over time, so the only evolving
    # aspect is the shifting adoption shares.
    
    load_emissions_factors()

    es.ref_grid_emissions = es.ref_adoption.mul(es.emissions_factors['avg']).sum(axis=1)
    audit("ref grid emissions", es.ref_grid_emissions)

    es.pds_grid_emissions = es.pds_adoption.mul(es.emissions_factors['avg']).sum(axis=1)
    audit("pds grid emissions", es.pds_grid_emissions)

