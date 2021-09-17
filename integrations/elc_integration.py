import pandas as pd
from pathlib import Path
from model import vma

conventional_plus_hydro = ["coal", "natural gas", "hydro", "oil products"]
energy_solutions=["onshorewind","offshorewind","solarpvutil","solarpvroof","concentratedsolar","geothermal","waveandtidal",
                  "biomass","microwind","instreamhydro","nuclear","wastetoenergy","landfillmethane","biogas"]


# Tab 2A: Emissions_Factors_VMA
# From the Excel: "The Solutions  tables below should be similar to the ones availablle  on the VMA 
# tables on emissions of each model. 1) update on each solution model and then copy the final versions 
# here before integration.
# We have also saved the emissions factors for conventional sources in this folder.

THISDIR=Path(__file__).parent
DATADIR=THISDIR / "data" / "elc"


def gather_emissions_factors_vmas():
    """
    Gather VMA data from the individual sources.
    Also load emissions factors for the conventional sources
    """

    emissions_factors = {
        # conventional
        'coal':         vma.VMA( filename=DATADIR/"COAL_Emissions_Factor.csv",fixed_summary=(1028.25, 1250.948609519274, 805.551390480726)),
        'natural gas':  vma.VMA( filename=DATADIR/"NATURAL_GAS_Emissions_Factor.csv", fixed_summary=(574.0743333333334, 746.9153177801815, 401.23334888648526)),
        'hydro':        vma.VMA( filename=DATADIR/"HYDRO_Indirect_CO2_Emissions.csv", fixed_summary=(202.26478260869567, 703.9449847283984, 0.0)),
        'oil products': vma.VMA( filename=DATADIR/"OIL_Emissions_Factor.csv", fixed_summary=(828.22, 1047.5515152913504, 608.8884847086497)),
    }
    for soln in energy_solutions:
        emissions_factors[soln] = standard_solution_emissions_vma(soln)
    
    return emissions_factors



def SOLN_VMA_PATH(soln):
    return THISDIR.parents[2] / "solution" / soln / "vma_data"

def standard_solution_emissions_vma(solution):
    return vma.VMA( filename=SOLN_VMA_PATH(solution)/"SOLUTION_Indirect_CO2_Emissions_per_Unit.csv")
