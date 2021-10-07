from io import StringIO
import json
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from meta_model import integration
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


trim_year = 2014    # Remove years before this from results.


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
    
    ref_tam_sources : dict = None                   # TAM data structrue (SMA)
    reference_tam : pd.DataFrame = None             # year series, Units TWh.    Excel Tab 3D column X
    integrated_tam : pd.DataFrame = None            # year x PDS123, Units TWh.  Excel Tab 5B, columns AW:AY
    old_integrated_tam : pd.DataFrame = None

    # Adoption of energy sources
    # Raw adoption units are TWh, the final adoption table units are % TAM

    coal_raw_adoption : pd.DataFrame = None         # year x BCA100%   Excel Tab 5A, columns BC:BF
    ng_raw_adoption : pd.DataFrame = None           # year x BCA100%   Excel Tab 5A, columns BC:BF
    hydro_raw_adoption : pd.DataFrame = None        # year x BCA100%   Excel Tab 5A, columns BC:BF
    oil_raw_adoption : pd.DataFrame = None          # year x BCA100%   Excel Tab 5A, columns BC:BF
    es_raw_adoption : pd.DataFrame = None           # year x (all solution sources x PDS123)  
                                                    #          Excel Tabs 5B, 5C, 5D, columns BF:CF
    
    conventional_adoption_profile : pd.DataFrame = None   # year x (PDS123 x source x (total,%))
                                                    # Excel tabs 5B, 5C, 5D, colums CO:DB
    
    ref_adoption : pd.DataFrame = None              # year x source, Units % ref TAM   Excel 
    pds_adoption: pd.DataFrame = None               # year x (source x PDS123), Units % integrated TAM 

    # Emissions

    ref_grid_emissions : pd.DataFrame = None        # year x (medium,high,low), Units ??, Excel tab 2E, columns A#:AH
    #pds_grid_emissions:  pd.DataFrame = None        # year x PDS123, Units g CO2-eq/kWh, Excel tab 2E, columns AK:Az

es = elc_integration_state()


# ########################################################################################################################
#                                       Data Collection and Supporting Functions
#
#  Grid Mix

def check_grid_mix():
    # Make sure grid mix has been specified, and complain otherwise
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
    return es.historical_grid_mix


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
        es.ref_tam_sources = scenario.load_sources(public_datadir/"ref_tam_sources_current.json", '*')
    print("Reference TAM sources loaded")
 
    # While we're at it, also load the old integrated TAM, so we have it to compare to, and before 
    # we potentially overwrite it.  Note we're skipping the TAM module and just loading the csvs
    es.old_integrated_tam = pd.concat({
        'PDS1' : pd.read_csv(public_datadir/"PDS_plausible_scenario_current.csv", index_col="Year")['World'],
        'PDS2' : pd.read_csv(public_datadir/"PDS_drawdown_scenario_current.csv", index_col="Year")['World'],
        'PDS3' : pd.read_csv(public_datadir/"PDS_optimum_scenario_current.csv", index_col="Year")['World']
    }, axis=1).loc[trim_year:]


def calc_energy_tam(case):
    # The spreadsheet actually does a simple average, so if we could figure out how to get the @#$#EF
    # raw data out of the TAM, we would too.
    tamconfig = tam.make_tam_config(overrides=[
        ('trend','World','Linear'),
        ('source_after_2014','World',case)])
    tam_object = tam.TAM(tamconfig, es.ref_tam_sources, es.ref_tam_sources)
    return tam_object.ref_tam_per_region()['World']


def integrated_tam_comparision():
    if es.integrated_tam is None:
        print("Cannot compare TAM until it has been calculated")
        return
    makedelta = lambda x, y, col: pd.concat({'old': x[col], 'new': y[col], 'delta': y[col].sub(x[col],axis=0)}, axis=1)
    old = es.old_integrated_tam
    new = es.integrated_tam
    return pd.concat({
        'PDS1': makedelta(old, new, 'PDS1'),
        'PDS2': makedelta(old, new, 'PDS2'),
        'PDS3': makedelta(old, new, 'PDS3')
    }, axis=1)


def load_conventional_adoption_profile():
    testdata = load_testmode_snapshot("conventional_pds_adoption.csv")
    source = StringIO(testdata) if testdata else datadir/"conventional_pds_adoption.csv"
    es.conventional_adoption_profile = pd.read_csv(source,index_col=0,header=[0,1,2])
    audit("conventional adoption profile loaded", es.conventional_adoption_profile)
    print("Current conventional adoption profile loaded")
    return es.conventional_adoption_profile

def use_conventional_adoption_profile(new_profile):
    es.conventional_adoption_profile = new_profile
    audit("conventional adoption profile set", new_profile)
    print("New conventional adoption profile set")
    

def compare_adoption_to_tam(segment):
    segments = ['reference', 'PDS1', 'PDS2', 'PDS3']
    if segment not in segments:
        print("Error: segment argument must be one of " + str(segments))
        return

    if segment == "reference":
        adoption_sum = es.ref_adoption.sum(axis=1)
        tam = es.reference_tam
    else:
        adoption_sum = es.pds_adoption[segment].sum(axis=1)
        tam = es.integrated_tam[segment]
    return pd.concat({"Adoption Total": adoption_sum, "TAM": tam, "Delta": tam.sub(adoption_sum, axis=0)}, axis=1)
\

def load_net_grid_use() -> pd.DataFrame:
    """Gather net electricity grid use from all solutions for all PDS1/2/3 scenarios.
    Returns a DataFrame with years index and (solutions) x (pds1/2/3) columns"""

    print("Loading net energy deltas for all solutions; this takes some time")
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
        
        df = pd.concat(collect, axis=1).loc[trim_year:]
    es.net_grid_use = df
    audit("net grid use", es.net_grid_use)
    print("*** done.")

# Emissions

def load_emissions_factors():
    """Load (average, high, low) emissions factors for each energy type, including conventional sources"""

    testdata = load_testmode_snapshot("emissions_factors.csv")
    if testdata:
        basedata = { x[0] : [float(z) for z in x[1:]] for x in [y.split(',') for y in testdata.splitlines()] }

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


def integrate():
    step1_calculate_tams()
    step2_calculate_adoptions()
    step3_calculate_emissions()
    step4_update()


def step1_calculate_tams():
    """Calculate the energy TAMs"""

    check_grid_mix()
 
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
    es.integrated_tam = pd.concat({'PDS1': pds_tam['PDS1'], 'PDS2': opttam, 'PDS3': opttam}, axis=1).loc[trim_year:]
    audit("integrated tam", es.integrated_tam)  # Excel TAb 5B, columns AW:AY
    print("integrated TAM calculated")


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

    # for solution sources, we take the current grid mix and assume that it will be unchanged over time,
    # so we multiply the percentage times the reference tam.
    solutional = pd.concat({
        soln: es.reference_tam * es.current_grid_mix.loc[soln,'percent'] for soln in energy_solutions
    }, axis=1)
    # Finally, add a column for "other biomass", which is the remainder after taking into
    # account the solutions in the biomass sector
    # We need this because we know that the biomass sector consists of more than just
    # the solutions we model, by a significant degree.
    pcnt = lambda s : es.current_grid_mix.loc[s,'percent']
    remainder_pcnt = pcnt('biomass and waste') - (pcnt('biogas') + pcnt('biomass') + pcnt('landfillmethane') + pcnt('wastetoenergy'))
    solutional['other biomass'] = es.reference_tam * remainder_pcnt
    
    es.ref_adoption = pd.concat([conventional, solutional],axis=1).loc[trim_year:]
    audit("ref adoption (of energy sources)", es.ref_adoption)

    # PDS adoption: use PDS solution values and integrated TAM.
    # Conventional PDS values are complicated; they involve adjusting "buffer" sources 
    # and such, so we make the user do this work, and save it in the conventional profile
    if es.conventional_adoption_profile is not None:
        print("using loaded conventional adoption profile")
    else:
        print("loading previously-saved conventional adoption profile")
        load_conventional_adoption_profile()
    
    # remove the percentages, which we will recalculate later.
    conventional = es.conventional_adoption_profile.xs('total',level=2,axis=1)

    # Get the solution adoption from the solutions themselves.
    maybedata = load_testmode_snapshot("solution_adoptions.csv")
    if maybedata:
        solutional = pd.read_csv(StringIO(maybedata), header=[0,1], index_col=0)
        solutional = solutional.rename(columns=factory.find_solution_by_name, level=1)
    else:
        solutional = pd.concat({
            soln : load_solution_adoptions(soln) for soln in energy_solutions
        }, axis=1).swaplevel(axis=1)

    es.pds_adoption = pd.concat([conventional, solutional], axis=1).sort_index(axis=1, level=0).loc[trim_year:]
    
    # TODO: recalculate the percents and put them back?

    audit("pds adoption", es.pds_adoption)
    print("Adoptions calculated")


def step3_calculate_emissions():
    # Calculate the results of TAB 2C
    
    # The fundamental emission equation is sum over energy sources s of
    #    emissions factor(s) * adoption share(s)
    #
    # Currently emissions factors are considered constant over time, so the only evolving
    # aspect is the shifting adoption shares.
    
    load_emissions_factors()

    es.ref_grid_emissions = pd.concat( {
        'medium': es.ref_adoption.mul(es.emissions_factors['avg']).sum(axis=1),
        'high': es.ref_adoption.mul(es.emissions_factors['high']).sum(axis=1),
        'low': es.ref_adoption.mul(es.emissions_factors['low']).sum(axis=1) }, axis=1)
    audit("ref grid emissions", es.ref_grid_emissions)

    # The Excel integration computes mean/high/low values for all three PDS, but if it uses
    # them for anything, I haven't figure out what yet, so I'm skipping that for now.
    # 
    # es.pds_grid_emissions = es.pds_adoption.mul(es.emissions_factors['avg']).sum(axis=1)
    # audit("pds grid emissions", es.pds_grid_emissions)
    print("Grid Emissions factors calculated")


def step4_update():
    version = str(es.integration_year)

    # Update emissions data
    emissions_file = thisdir.parent/"data"/"emissions"/"meta.csv"
    update_to_version(emissions_file, version, df_to_csv_string(es.ref_grid_emissions))
    print("Grid Emissions Data saved")

    # PDS TAM data
    # Create updated versions of each of the data files, and then also the updated json file
    munge = lambda x: df_to_csv_string(x.set_axis(['World'],axis=1))
    update_to_version(public_datadir/"PDS_plausible_scenario.csv", version, munge(es.integrated_tam[['PDS1']]))
    update_to_version(public_datadir/"PDS_drawdown_scenario.csv", version, munge(es.integrated_tam[['PDS2']]))
    update_to_version(public_datadir/"PDS_optimum_scenario.csv", version, munge(es.integrated_tam[['PDS3']]))

    # We don't have to update the "current" version of the json file, because it already points to the 
    # current versions of the csvs.  So we update only the versioned version of the json file,
    content = {
        "Ambitious Cases": {
        "Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario": "PDS_plausible_scenario_VERSION.csv",
        "Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario": "PDS_drawdown_scenario_VERSION.csv",
        "Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario": "PDS_optimum_scenario_VERSION.csv"
    }}
    contentstring = json.dumps(content,indent=2).replace("VERSION",version)
    filename = integration.integration_alt_file(public_datadir/f"pds_tam_sources_{version}.csv")
    filename.write_text(contentstring, encoding='utf-8')
    print("PDS (Integrated) TAM saved")