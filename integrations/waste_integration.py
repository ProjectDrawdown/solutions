from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from model import integration
from .integration_base import *

THISDIR = Path(__file__).parent
DATADIR = THISDIR/"data"/"msw"

# Excel notes: Excel references refer to the Sheet MSW Integration Calcs (PDS1, 2 or 3) unless
# otherwise noted.  Also, not all Integration Calcs tables are implemented, if their results
# are used in only one location, or if their results are not used by the integration results or
# other featured calculations.

# TEMPORARY SNAPSHOT identifies inputs that are obtained from local data files that
# should be fetched from other models, but we either don't have the model at all (the food model),
# or we haven't implemented that part of the model.  When we do get those implemented, we should
# replace the snapshot a live data fetch.

# ########################################################################################################################
#                                              INPUTS

# By default, the standard PDS scenrios are used, but they can be replaced here with whichever 
# scenarios you want to use for the PDS1, 2, and 3 cases.
bioplastics_scenario_names = ["PDS1","PDS2","PDS3"]
composting_scenario_names = ["PDS1","PDS2","PDS3"]
insulation_scenario_names = ["PDS1","PDS2","PDS3"]
landfill_methane_scenario_names = ["PDS1","PDS2","PDS3"]
recycling_scenario_names = ["PDS1","PDS2","PDS3"]
paper_scenario_names = ["PDS1","PDS2","PDS3"]
waste_to_energy_scenario_names = ["PDS1","PDS2","PDS3"]


# ########################################################################################################################
#                                              State tracking

audit = start_audit("waste")
# The audit log stores results that are computed throughout the process.  It is *append only*.  
# It is never read or modified by this code.  Enables debugging and analysis by users.

@dataclass
class waste_integration_state:
    # This data class holds global variables that are shared between steps.  Embedding it in a class
    # enables us to avoid having to declare 'global' anytime we want to change something.

    # The main state: available waste material for variety of uses
    waste_tam : pd.DataFrame = None      # original, not adjusted
    organic_msw: pd.DataFrame = None     # "used up" as we go along
    recyclable_msw: pd.DataFrame = None  # "used up" as we do along
    remainder_msw: pd.DataFrame = None   # "used up" as we go along
    total_waste_msw: pd.DataFrame = None  # in step5, we revert to considering all waste streams together

    # adoptions may be adjusted
    compost_adoption: pd.DataFrame = None
    paper_adoption: pd.DataFrame = None
    paper_consumption: pd.DataFrame = None
    recycling_adoption: pd.DataFrame = None
    waste_to_energy_adoption: pd.DataFrame = None
    landfill_methane_adoption: pd.DataFrame = None

    effective_lhv: pd.DataFrame = None
    effective_doc: pd.DataFrame = None

    # these are set in step5 and used in step6 and valid only during that period
    organic_proportion: pd.DataFrame = None   # organic proportion of total_waste_msw
    recyclable_proportion: pd.DataFrame = None   # recyclable proportion of total_waste_msw
    remainder_proportion:pd.DataFrame = None   # remainder proportion of total_waste_msw
    
ws = waste_integration_state()

# ########################################################################################################################
#                                              CALCULATION
 
def integrate():
    """Perform all steps of the integration together."""
    ws_step1()
    ws_step2()
    ws_step3()
    ws_step4()
    ws_step5()
    ws_step6()
    ws_step7()


def ws_step1():
    """Step one of the integration divides the waste stream into organic, recyclable and remainder categories"""
    # Start with the global amount of waste
    # TEMPORARY SNAPSHOT, Excel Table1, "Waste Model"
    ws.waste_tam = pd.read_csv(DATADIR/"garbage_tam.csv", index_col="Year", squeeze=False)
    ws.waste_tam = pdsify(ws.waste_tam['World']).loc[2014:]
    audit("waste tam", ws.waste_tam)

    # TEMPORARY SNAPSHOTs Excel Compost!J, composting
    organic_proportion = read_as_series( DATADIR, "organic_compost_sma_S1.csv" ).loc[2014:]
    # TEMPORARY SNAPSHOTs Excel 'H&C Recycling'!K, hcrecycling
    recyclable_proportion = read_as_series( DATADIR, "hc_percent_recyclable_sma_S1.csv" ).loc[2014:]

    # Break into three streams: ORGANIC, RECYCLABLE, REMAINDER
    # PAPER is included in the REMAINDER stream, not the recyclable stream

    ws.organic_msw = df_mult_series(ws.waste_tam, organic_proportion / 100)
    ws.recyclable_msw = df_mult_series(ws.waste_tam, recyclable_proportion /100)
    ws.remainder_msw = ws.waste_tam - ws.organic_msw - ws.recyclable_msw
    audit("base organic", ws.organic_msw)           # Excel Table 2, column 1
    audit("base recyclable", ws.recyclable_msw)     # Excel Table 3, column 1
    audit("base remainder", ws.remainder_msw)       # Excel Table 4

def ws_step2():
    """Step two adjusts the waste stream to account for reductions in food waste and the increase of 
    compostible plastics."""

    # TEMPORARY SNAPSHOT 'Food System Summary'!G, E, H, food model
    food_waste_reduction = pd.read_csv( DATADIR / "food_waste_reduction.csv", index_col="Year" )
    ws.organic_msw -= food_waste_reduction
    audit("organic less reduced food", ws.organic_msw) # Excel table 9

    # TEMPORARY SNAPSHOT Excel Table 11, bioplastic model
    compostable_proportion = read_as_series( DATADIR, "percent_plastic_compostable_sma_S1.csv" )
    
    # Adjust organic waste upwards for the portion of bioplastics that is compostible.
    # Remove same amount from recyclable (where we assume plastic would have been otherwise)
    bioplastics_adoption = load_solution_adoptions("bioplastic", bioplastics_scenario_names)
    compostable_bioplastics = df_mult_series(bioplastics_adoption, compostable_proportion)
    ws.organic_msw += compostable_bioplastics
    ws.recyclable_msw -= compostable_bioplastics
    audit("organic plus compostable bp", ws.organic_msw)  # Excel table 13
    audit("recylable less compostable bp", ws.recyclable_msw) # Excel table 14

    # There is considerable additional stuff going on in the bioplastics part of the workbork that
    # could in theory limit bioplastic adoption (?), but doesn't for now.  I have punted on this.

    
def ws_step3():
    """Step three adjusts the adoptions of composting and recycling to reflect availability of feedstock, 
    and subtracts those uses from their respective waste streams."""

    ws.compost_adoption = load_solution_adoptions("composting", composting_scenario_names)
    audit("base compost adoption", ws.compost_adoption)
    ws.compost_adoption = demand_adjustment("compost adoption", ws.compost_adoption, ws.organic_msw)
    audit("adjusted compost adoption", ws.compost_adoption) # Excel Compost!E
    ws.organic_msw -= ws.compost_adoption
    audit("organics msw less compost", ws.organic_msw) # Excel Table 22 column 2

    ws.recycling_adoption = load_solution_adoptions("hcrecycling", recycling_scenario_names)
    audit("base recycling adoption", ws.recycling_adoption)
    ws.recycling_adoption = demand_adjustment("recycling adjustment", ws.recycling_adoption, ws.recyclable_msw)
    audit("adjusted recycling adoption", ws.recycling_adoption) # Excel H&C Recycling!E
    ws.recyclable_msw -= ws.recycling_adoption
    audit("recyclable msw less recycling", ws.recyclable_msw) # Excel Table 20 column 3

def ws_step4():
    """Step four subtracts the use of recycled paper and insulation from the remainder waste stream."""
    # Calculate the maximum amount of paper available to recycle as the minimum between
    # the recycledpaper TAM and the remainder_MSW
    #       comment: this is slightly wrong: we're adjusting a new paper amount by a soiled paper amount.
    #       but it is what the spreadsheet does.  There could be a corner case in which the adoption was 
    #       less than tam but greater than msw due to the recycling ratio.
    paper_collected = pdsify(load_solution_tam("recycledpaper", paper_scenario_names[1]))
    feedstock = demand_adjustment("paper available feedstock", paper_collected, ws.remainder_msw)
    audit("paper feedstock", feedstock) # Excel Paper!E 
   
    # TEMPORARY SNAPSHOT, Excel Paper!G3, G58, G113,  recycledpaper
    paper_recycling_ratio = pd.Series({'PDS1': 1.29666666666667, 'PDS2': 1.29666666666667, 'PDS3': 1.1154056516757})

    # The adoption is the amount of recycled paper produced
    # The consumption is the amount of waste paper required to produce that adoption amount
    ws.paper_adoption = load_solution_adoptions("recycledpaper", recycling_scenario_names)
    ws.paper_consumption = ws.paper_adoption * paper_recycling_ratio
    audit("paper consumption", ws.paper_consumption) # Excel Paper!G
    ws.paper_consumption = demand_adjustment("paper consumption", ws.paper_consumption, feedstock)
    audit("adjusted paper consumption", ws.paper_consumption) # Excel Paper!E

    # Update the paper adoption to match the available consumption
    ws.paper_adoption = ws.paper_consumption / paper_recycling_ratio
    audit("adjusted paper adoption", ws.paper_adoption)  # Excel doesn't compute this??

    # remainder msw after accounting for paper recycling
    ws.remainder_msw -= ws.paper_consumption
    audit("remainder msw after paper", ws.remainder_msw) # Excel Paper!H

    # for insulation we can get the consumption from the model
    # pds1 = factory.load_scenario("insulation",insulation_scenario_names[0])
    # pds2 = factory.load_scenario("insulation",insulation_scenario_names[1])
    # pds3 = factory.load_scenario("insulation",insulation_scenario_names[2])
    # # This also seems really weird.
    # # Why do we assume that the total amount of insulation would be derived from recycled materials?
    # # I'm not sure I implemented the right thing....
    # insulation_consumption = pd.DataFrame({'PDS1': pds1.adoption_as_material_mass(),
    #                                        'PDS2': pds2.adoption_as_material_mass(),
    #                                        'PDS3': pds3.adoption_as_material_mass()})
    # TEMPORARY SNAPSHOT Paper!I, insulation
    insulation_consumption = pd.read_csv( DATADIR / "insulation_mass_demand.csv", index_col="Year" )
    audit("insulation consumption", insulation_consumption) 

    # don't consume any more than there is.
    insulation_consumption = demand_adjustment("insulation consumption", insulation_consumption, ws.remainder_msw)
    audit("adjusted insulation consumption", insulation_consumption) # Excel not stored

    # Final cellulose-based adjustment of remainder msw
    ws.remainder_msw -= insulation_consumption
    audit("remainder msw after insulation", ws.remainder_msw) # Excel Paper!J or Table 22 col 3

def ws_step5():
    """Step five subtracts the waste material used by Waste to Energy"""
    # To determine the amount of energy that will be generated by burning waste, we need to know its LHV
    # The LHV varies depending on the type of waste.  The Excel workbook did calcs to estimate an LHV for
    # the types of waste tracked here: organic, recyclable and remainder.  So the first step is to 
    # calculate an overall LHV based on the proportions of waste in our waste stream.

    weighted_average_LHV = {'organic': 1.499261376, 'recyclable': 3.549477827, 'remainder': 2.120720855} 
    waste_to_energy_efficiency_factor = 0.2367
    # TEMPORARY SNAPSHOT Excel WTE Tonnes & Composition D62, WTE model

    ws.total_waste_msw = ws.organic_msw + ws.recyclable_msw + ws.remainder_msw
    ws.organic_proportion = ws.organic_msw / ws.total_waste_msw
    ws.recyclable_proportion = ws.recyclable_msw / ws.total_waste_msw
    ws.remainder_proportion = ws.remainder_msw / ws.total_waste_msw
    audit("total waste msw for burning", ws.total_waste_msw) # Table 22 column 1
    
    ws.effective_lhv = ((ws.organic_proportion * weighted_average_LHV['organic']) +
                     (ws.recyclable_proportion * weighted_average_LHV['recyclable']) +
                     (ws.remainder_proportion * weighted_average_LHV['remainder']))
    audit("effective lhv", ws.effective_lhv) # Excel Table 23 Column 5

    false_lhv = pdsify(ws.effective_lhv['PDS1'])  # use PDS2 for all scenarios

    # adoption is the amount of TwH produced.  consumption is the amount of MSW required to produce the adoption
    ws.waste_to_energy_adoption = load_solution_adoptions('wastetoenergy', waste_to_energy_scenario_names)
    #waste_to_energy_consumption = ws.waste_to_energy_adoption / (ws.effective_lhv * waste_to_energy_efficiency_factor)
    waste_to_energy_consumption = ws.waste_to_energy_adoption / (false_lhv * waste_to_energy_efficiency_factor)
    audit("wte base consumption", waste_to_energy_consumption) # Excel WTE Tonnes and Composition!G 
                                                               # Only *one* of the PDS is calculated at a time.
    
    adjusted_consumption = demand_adjustment("wte consumption", ws.total_waste_msw, waste_to_energy_consumption)
    audit("wte adjusted consumption", adjusted_consumption)    # Excel Table 24 column 1 (only one PDS...)

    adjusted_adoption = adjusted_consumption * ws.effective_lhv * waste_to_energy_efficiency_factor
    audit("wte adjusted adoption", adjusted_adoption) # Excel WTE Tonnes and Composition!L, R, Y

    ws.total_waste_msw -= adjusted_consumption
    audit("landfilled waste", ws.total_waste_msw)

def ws_step6():
    """Step six determines adjusts landfill methane adoption based on achievability"""
    tonnage_conversion_factor = 199042.708333333   # Excel Landfill Methane ! D4
    possible_tw = ws.total_waste_msw * tonnage_conversion_factor
    audit("possible twh from lm", possible_tw)
    ws.landfill_methane_adoption = load_solution_adoptions('landfillmethane', landfill_methane_scenario_names)
    ws.landfill_methane_adoption = demand_adjustment('lm adoption', ws.landfill_methane_adoption, possible_tw)
    audit('adjusted lm adoption', ws.landfill_methane_adoption)

    # We also compute a DOC (Degradable Carbon) factor that (does something...), which we will save late
    # similar to the LHV computation above, it is calculated as the weighted average over time
    weighted_average_DOC_fraction = {'organic': 0.198253844, 'recyclable': 0.280060046, 'remainder': 0.342912545}
    ws.effective_doc = ((ws.total_waste_msw * ws.organic_proportion * weighted_average_DOC_fraction['organic']) +
                        (ws.total_waste_msw * ws.recyclable_proportion * weighted_average_DOC_fraction['recyclable']) +
                        (ws.total_waste_msw * ws.remainder_proportion * weighted_average_DOC_fraction['remainder']))
    audit('effective doc', ws.effective_doc)


def ws_step7():
    """Step seven updates the affected scenarios with new adoptions reflecting available waste feedstock and/or efficiency."""
    # Currently we always write out new values, even if they have not changed.  We might want to change this to
    # do a comparison against the original and only update if needed.

    print("updating composting adoption")
    from solution import composting
    composting.Scenario.update_adoptions(composting_scenario_names, ws.compost_adoption)

    print("updating recycling adoption")
    from solution import hcrecycling
    hcrecycling.Scenario.update_adoptions(recycling_scenario_names, ws.recycling_adoption)

    # The instructions do not say that we should update recycledpaper or insulation, but we could.

    print("updating waste to energy LHV values")
    # The instructions do say to update the effective LVH and the DOC to the "Emissions Factoring" sheet
    # of the WTE model, but that sheet does not exist.  I haven't yet found where in the system it is used
    # but for now, I am saving them to a data file in the data directory as if we used them somewhere.
    lhvfile = integration.integration_alt_file(DATADIR/"waste_to_energy_lhv.csv")
    ws.effective_lhv.to_csv(lhvfile)

    print("updating landfill methane DOC values")
    docfile = integration.integration_alt_file(DATADIR/"waste_to_energy_doc.csv")
    ws.effective_doc.to_csv(docfile)