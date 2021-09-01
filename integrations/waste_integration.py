from pathlib import Path
import pandas as pd
from model import sma
from model import tam
from model import dd
from .integrations import *

THISDIR = Path(__file__).parent
DATADIR = THISDIR / "data" / "msw"

# Excel notes: Excel references refer to the Sheet MSW Integration Calcs (PDS1, 2 or 3) unless
# otherwise noted.  Also, not all Integration Calcs tables are implemented, if their results
# are used in only one location, or if their results are not used by the integration results or
# other featured calculations.

# ########################################################################################################################
#                                              INPUTS
# These values are writable, so experimentation may be done by setting them to other values before calling the
# integration functions.  Values initialized to None here are set to default values by the function 
# load_default_values().

waste_tam : pd.DataFrame = None
"""Total addressable market for waste products.  Years x Regions df
Units: Million tonnes generated."""
# Excel Table 1

# COMPOST

compost_adoption : pd.DataFrame = None
"""Worldwide compost adoption for three scenarios.  Years x (PDS1,PDS2,PDS3).
Retrieved from composting model.
Units: Million tonnes waste composted."""
# Excel Compost!B
composting_scenario_names = ["PDS1","PDS2","PDS3"]
"""Scenarios to use for composting solution."""

compostable_proportion : pd.Series = None
"""Estimate of proportion of waste worldwide that is compostable. Years series.
Units: % (i.e fraction * 100)"""
# Excel Compost!J

regional_organic_fraction = pd.Series({
    'OECD90': 0.39236288,
    'Eastern Europe': 0.02820816,
    'Asia (Sans Japan)': 0.16053698,
    'Middle East and Africa': 0.28956111,
    'Latin America': 0.12904009,
    'China': 0.13109840,
    'India': 0.16185183,
    'EU': 0.12005864,
    'USA': 0.07888291
})
"""Regional proportion of organic waste.  Regions series.
Derived the Intergovernmental Panel on Climate Change (IPCC), 2006 and Hoornweg & Bhada-Tata (2012).
Units: fraction"""
# Excel P5:X5
# Note the regional waste values are not actually used.  They are provided for informational value only.

# RECYCLING

recyclable_proportion: pd.Series = None
"""Estimate of proportion of waste worldwide that is recyclable.  Years series.
Units: % (i.e fraction * 100)"""
# Excel 'H&C Recycling'!K

regional_recyclable_fraction = pd.Series({
    'OECD90': 0.295212,
    'Eastern Europe': 0.047083,
    'Asia (Sans Japan)': 0.144916,
    'Middle East and Africa': 0.395601,
    'Latin America': 0.117187,
})
"""Regional portion of recyclable waste.  Regions series.
Units: fraction"""
# Excel AC5:AG5
# Note the regional waste values are not actually used.  They are provided for informational value only.

# PLASTICS

plastics_tam : pd.Series = None
"""Total plastics market worldwide. Years series.
From bioplastics model.
Units: Million tonnes."""
# Excel Table 5

proportion_plastics_in_waste = 0.69
"""Proportion of yearly plastic production that ends up in waste.
Estimated from waste TAM, plastics TAM and What a Waste 2.0 estimate that 12% of waste in 2016 is plastic.
(1932.45927 * 0.12) / 335 = 0.6922
Units: fraction"""
# Excel Bioplastics!AI12
# Note: the excel had a mistake here: while the text clearly indicates an intent to divide by the Waste TAM[2016],
# the Excel divides by the Waste TAM[2014].  I have corrected that mistake.  This drops the estimate from 78% to 69%
# If you want to match the Excel behavior, substitute 0.78 for this value.

bioplastics_adoption : pd.DataFrame = None
"""Worldwide bioplastics adoption for three scenarios.  Years x (PDS1,PDS2,PDS3) df.
Units: Million tonnes"""
# Excel Table 10
bioplastics_scenario_names = ["PDS1","PDS2","PDS3"]
"""Scenarios to use for bioplastic solution"""

proportion_bioplastics_compostable : pd.Series = None
"""Proportion of bioplastics that are compostable worldwide.  Years series.
Units: fraction."""
# Excel Table 11

# FOOD

food_waste : pd.DataFrame = None
"""Food waste worldwide for three scenarios.  Years x (PDS1,PDS2,PDS3) df.
Units: Million tonnes."""
# Excel 'Food System Summary'!G, E, H

food_waste_reduction : pd.DataFrame = None
"""Worldwide food waste reduction for three scenarios.  Years x (PDS1,PDS2,PDS3) df.
Includes only food waste reduction in 'Distribution' and 'Consumption' stages of Food System.
Units: Million tonnes"""
# Excel Table 7.


# WASTE TO ENERGY

waste_to_energy_adoption : pd.DataFrame = None
"""Adoption of waste to energy technologies for three scenarios.  Years x (PDS1,PDS2,PDS3) df.
Units: """
waste_to_energy_scenario_names = ["PDS1","PDS2","PDS3"]
"""Names of the scenarios to use for wastetoenergy solution."""

# END INPUTS ----------------------------

def load_default_values(forceAll=False):
    """Load values for inputs.  
    If the input is already set to a value, it is not overwritten, unless forceAll is True"""

    global waste_tam
    if waste_tam is None or forceAll:
        # NOTE: should be obtained from waste model when we have it.
        tamconfig = tam.make_tam_config()
        tamsources = sma.SMA.read( DATADIR, "waste_tam", read_data=False ).as_tamsources( DATADIR )
        waste_tam = tam.TAM(tamconfig, tamsources, tamsources).ref_tam_per_region()


    global compost_adoption
    if compost_adoption is None or forceAll:
        compost_adoption = load_solution_adoptions("composting", composting_scenario_names)
    
    global compostable_proportion
    if compostable_proportion is None or forceAll:
        compostable_proportion = sma.SMA.read( DATADIR, "organic_compost_sma" ).summary(case='S1')['World']


    global recyclable_proportion
    if recyclable_proportion is None or forceAll:
        recyclable_proportion = sma.SMA.read( DATADIR, "hc_percent_recyclable_sma" ).summary(case='S1')['World']


    global plastics_tam
    if plastics_tam is None or forceAll:
        # Load from bioplastics model
        plastics_tam = load_solution_tam("bioplastic", bioplastics_scenario_names[1])

    global bioplastics_adoption
    if bioplastics_adoption is None or forceAll:
        # Load from bioplastics model
        # NOTE: bioplastic is currently failing adoption tests, so these results are suspect.
        bioplastics_adoption = load_solution_adoptions("bioplastic", bioplastics_scenario_names)
    
    global proportion_bioplastics_compostable
    if proportion_bioplastics_compostable is None or forceAll:
        # The excel claims this comes from the bioplastics model, but I don't see it there.
        # Even if it were there that would be a part of the model we haven't implemented yet.
        # NOTE: should be obtained from bioplastics model, if/when it is implemented there.
        ppc_sma = sma.SMA.read( DATADIR, "percent_plastic_compostable_sma" )
        proportion_bioplastics_compostable = ppc_sma.summary(case='S1')['World']


    global food_waste
    if food_waste is None or forceAll:
        # NOTE: should be obtained from food model when we have it.
        food_waste = pd.read_csv( DATADIR / "food_waste.csv", index_col="Year" )
    
    global food_waste_reduction
    if food_waste_reduction is None or forceAll:
        # NOTE: should be obtained from food model when we have it.
        food_waste_reduction = pd.read_csv( DATADIR / "food_waste_reduction.csv", index_col="Year" )


    global waste_to_energy_adoption
    if waste_to_energy_adoption is None or forceAll:
        waste_to_energy_adoption = load_solution_adoptions("wastetoenergy", waste_to_energy_scenario_names)



# #########################################################################################################################
#  
#                                            Intermediate Calculations
# 

def get_base_organic_waste() -> pd.DataFrame:
    """Total amount of organic waste.  Years x Regions df.
    Using waste fraction data from the Intergovernmental
    Panel on Climate Change (IPCC), 2006 and Hoornweg & Bhada-Tata (2012) a forecast for the
    organic fraction of MSW is devloped for Drawdown regions and the World. Food waste and
    "green material" is considered organic fraction. Soiled paper may be considered "green
    material" in some regions, but paper waste is allocated elsewhere. Green material includes
    landscape waste and certain debris. This forecast becomes the TAM for Composting and is
    directly affected by reductions in food waste and an increase in Bioplastics production and
    a simulataneous, but distinct forecast in compostability of bioplastic. When bioplastic is
    considered compostable it moves to the organic fraction.
    Units: Million tonnes."""
    # Excel Table 2
    # Note the regional waste values are not actually used.  They are provided for informational value only.
    
    # column A:
    compost_organic_fraction_world = waste_tam['World'] * compostable_proportion / 100
    # the regional columns are an outer product with regional_organic_fraction
    op = series_outer_product(compost_organic_fraction_world, regional_organic_fraction)
    return pd.concat([compost_organic_fraction_world,op], axis=1).loc[2014:]


def get_base_recyclable_waste() -> pd.DataFrame:
    """Total amount of recyclable waste, excluding paper.  Years x Regions df.
    This is developed from multiple sources including  the Intergovernmental
    Panel on Climate Change (IPCC), 2006; Hoornweg & Bhada-Tata (2012);Bahor, et al(2009);
    Hoornweg et al (2015).
    Units: Million tonnes."""
    # Excel Table 3
    # Note the regional waste values are not actually used.  They are provided for informational value only.

    # table 3, column A
    recyclable_portion_world = waste_tam['World'] * recyclable_proportion / 100
    # the regional columns are an outer product with regional_recyclable_fraction
    op = series_outer_product(recyclable_portion_world, regional_recyclable_fraction)
    return pd.concat([recyclable_portion_world,op], axis=1).loc[2014:]

def get_waste_remainder_1() -> pd.DataFrame:
    """Waste TAM less organics and recyclables.  Years x Regions df.
    This includes paper.
    Units: Million tonnes."""
    # Excel Table 4
    # Note the regional waste values are not actually used.  They are provided for informational value only.
    remainder = waste_tam - get_base_organic_waste() - get_base_recyclable_waste()
    return remainder.reindex(columns=dd.REGIONS)

def get_base_plastic_waste() -> pd.Series:
    """Amount of worldwide plastic waste per year.  Years series.
    Not all plastic produced each year enters MSW.  This estimates
    plastic in MSW based on benchmark from World Bank 2018. 12% of MSW is plastics.
    Units: million tonnes."""
    # Excel Table 5
    return plastics_tam * proportion_plastics_in_waste

def get_waste_less_food_reduction() -> pd.DataFrame:
    """The worldwide waste tam corrected for food waste reduction for three scenarios.
    Year x (PDS1,PDS2,PDS3) df.
    Units: Million tonnes."""
    # Excel Table 8, 12
    return series_sub_df(waste_tam['World'], food_waste_reduction)

def get_updated_organic_waste() -> pd.DataFrame:
    """Total World Organic MSW after reduction in Food Waste and with addition of a % of
    bioplastics for three scenarios.  Years x (PDS1,PDS2,PDS3) df
    This impacts the TAM for Composting.
    Units: Million tonnes."""
    # Excel Table 13 (including computation for Table 9)
    organic_waste_portion = get_base_organic_waste()['World']
    organic_msw_less_food_reduction = series_sub_df(organic_waste_portion, food_waste_reduction)
    compostable_bioplastics = df_mult_series(bioplastics_adoption, proportion_bioplastics_compostable)
    return  organic_msw_less_food_reduction + compostable_bioplastics

def get_updated_recyclable_waste() -> pd.DataFrame:
    """Total World Recyclable MSW after reduction of compostible share of bioplastics for three
    scenarios.  Years x (PDS1,PDS2,PDS3) df.
    Assumes that all bioplastics would have been categorized as recyclable.
    Units: Million tonnes."""
    # Excel Table 14
    compostable_msw = get_base_recyclable_waste()['World']
    compostable_bioplastics = df_mult_series(bioplastics_adoption, proportion_bioplastics_compostable)
    return series_sub_df(compostable_msw, compostable_bioplastics)

def get_waste_remainder_2() -> pd.DataFrame:
    """Total World Remainder MSW after subtraction of reduced food waste and fraction mix change due
    to bioplastics (not Organics and Not Recyclables) for three scenarios. DOES include Paper.
    Years x (PDS1,PDS2,PDS3) df.
    Units: Million tonnes."""
    # Excel Table 15
    x = get_waste_less_food_reduction()
    y = get_updated_organic_waste()
    z = get_updated_recyclable_waste()
    return x - y - z


# #########################################################################################################################
#  
#                                                Integration Steps
# 

def get_feedstock_limited_solutions() -> dict:
    """Return a dictionary mapping solutions to their overshoot (the degree to which their adoption exceeds
    available feedstock)."""
    pairs = {"composting" : (compost_adoption, get_updated_organic_waste())}
    result = {}
    for solution in pairs:
        (adoption, feedstock) = pairs[solution]
        overshoot = (adoption-feedstock)
        if (overshoot > 0).any(axis=None):
            result[solution] = overshoot.clip(lower=0.0)
    return result


def update_feedstock_limited_adoptions(maxtries=5):
    """Update the _in memory_ adoptions of any feedstock limited solutions to max out at the feedstock
    limitation.  Does not affect actual solution scenarios."""
    for _ in range(maxtries):
        solns = get_feedstock_limited_solutions()
        if len(solns) > 0:
            print("These solutions exceed their feedstock and will be adjusted: " + ", ".join(list(solns.keys())))

            if "composting" in solns:
                global compost_adoption
                feedstock = get_updated_organic_waste()
                # read this as "where compost_adoption < feedstock, use compost_adoption, else feedstock"
                compost_adoption = compost_adoption.where( compost_adoption<feedstock, feedstock )
        else:
            return
    
    if len(get_feedstock_limited_solutions() > 0):
        print(f"Feedstock balancing not successful after {maxtries} rounds.  Terminating.")
        #raise ValueError()  dunno yet if this should be an error or not.


def update_solutions(which_solutions=None):
    """Create updated scenarios for all solutions affected by this integration.
    If `which_solutions` is provided, only the listed solutions will be updated."""
    updates = {
        "composting": "foo"
    }

