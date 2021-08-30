from pathlib import Path
import pandas as pd
import numpy as np
from model import sma
from model import tam
from model import dd

THISDIR = Path(__file__).parent
DATADIR = THISDIR / "data" / "msw"

# ########################################################################################################################
# Default values for parameters of the integration
# These values are writable, so experimentation may be done by setting them to other values before calling the
# integration functions.  Values initialized to None here are set to default values by the function load_default_values().

# Notes: Some of these are originally defined in the Excel models for the corresponding solution (e.g. composting), but
# we have not implemented that part of the solution yet.  When/if we do, it will be important to make sure that we 
# reference a single source, and not create duplicates.

waste_tam : pd.DataFrame = None
"""Total addressable market for waste products.
Units: Million tonnes generated."""

compostable_proportion : pd.Series = None
"""Estimate of proportion of waste worldwide that is compostable; time series.
Units: % (i.e fraction * 100)"""

recyclable_proportion: pd.Series = None
"""Estimate of proportion of waste worldwide that is recyclable; time series.
Units: % (i.e fraction * 100)"""

# Note the regional waste values are not actually used.  They are provided for informational value only.
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
"""Regional proportion of organic waste.
Derived the Intergovernmental Panel on Climate Change (IPCC), 2006 and Hoornweg & Bhada-Tata (2012).
Units: fraction"""

# Note the regional waste values are not actually used.  They are provided for informational value only.
regional_recyclable_fraction = pd.Series({
    'OECD90': 0.295212,
    'Eastern Europe': 0.047083,
    'Asia (Sans Japan)': 0.144916,
    'Middle East and Africa': 0.395601,
    'Latin America': 0.117187,
})
"""Regional portion of recyclable waste.
Units: fraction"""

# Note: comments in excel indicate that there is a complete TAM for plastics somewhere, but 
# I'm not sure where.  For now, just using what is available from the integration itself.
plastics_worldwide : pd.Series = None
"""Total plastics market worldwide; time series.
Units: Million tonnes."""


# Note: the excel had a mistake here: while the text clearly indicates an intent to divide by the Waste TAM[2016],
# the Excel divides by the Waste TAM[2014].  I have corrected that mistake.  This drops the estimate from 78% to 69%
# If you want to match the Excel behavior, substitute 0.78 for this value.
proportion_plastics_in_waste = 0.69
"""Proportion of yearly plastic production that ends up in waste.
Estimated from waste TAM, plastics TAM and What a Waste 2.0 estimate that 12% of waste in 2016 is plastic.
(1932.45927 * 0.12) / 335 = 0.6922
Units: fraction"""


# #########################################################################################################################
#  
#  Pre-integration calculations: accumulate inputs into useful values.
# 
def get_organic_waste_portion() -> pd.DataFrame:
    """Composite Mt MSW Organic Fraction.
    Using waste fraction data from the Intergovernmental
    Panel on Climate Change (IPCC), 2006 and Hoornweg & Bhada-Tata (2012) a forecast for the
    organic fraction of MSW is devloped for Drawdown regions and the World. Food waste and
    "green material" is considered organic fraction. Soiled paper may be considered "green
    material" in some regions, but paper waste is allocated elsewhere. Green material includes
    landscape waste and certain debris. This forecast becomes the TAM for Composting and is
    directly affected by reductions in food waste and an increase in Bioplastics production and
    a simulataneous, but distinct forecast in compostability of bioplastic. When bioplastic is
    considered compostable it moves to the organic fraction."""
    # Note the regional waste values are not actually used.  They are provided for informational value only.

    # Table 2: Multiply the Waste TAM by compostable proportion and regional organic fraction
    # table 2, column A
    compost_organic_fraction_world = waste_tam['World'] * compostable_proportion / 100
    
    # the regional columns are an outer product with regional_organic_fraction
    op = series_outer_product(compost_organic_fraction_world, regional_organic_fraction)
    return pd.concat([compost_organic_fraction_world,op], axis=1).loc[2014:]


def get_recyclable_waste_portion() -> pd.DataFrame:
    """Composite Mt MSW Recycleable Fraction (This is TAM for Recycling).
    Does NOT Include Paper. This is developed from multiple sources including  the Intergovernmental
    Panel on Climate Change (IPCC), 2006; Hoornweg & Bhada-Tata (2012);Bahor, et al(2009);
    Hoornweg et al (2015)."""
    # Note the regional waste values are not actually used.  They are provided for informational value only.

    # Table 3: Multiply the Waste TAM by recycling proportion and regional recycling fraction
    # table 3, column A
    recyclable_portion_world = waste_tam['World'] * recyclable_proportion / 100

    # the regional columns are an outer product with regional_recyclable_fraction
    op = series_outer_product(recyclable_portion_world, regional_recyclable_fraction)
    return pd.concat([recyclable_portion_world,op], axis=1).loc[2014:]

def get_waste_remainder() -> pd.DataFrame:
    """Waste TAM less compost and recyclables.
    This includes paper."""
    # Note the regional waste values are not actually used.  They are provided for informational value only.
    # Table 4
    remainder = waste_tam - get_organic_waste_portion() - get_recyclable_waste_portion()
    return remainder.reindex(columns=dd.REGIONS)

def get_plastics_waste_portion() -> pd.Series:
    """Amount of plastic waste per year.
    Not all plastic produced each year enters MSW.  This estimates
    plastic in MSW based on benchmark from World Bank 2018. 12% of MSW is plastics.
    Units: million tonnes."""
    # Table 5
    return plastics_worldwide * proportion_plastics_in_waste

# #######################################################################################################
#
# Utilities

def series_outer_product(series1, series2) -> pd.DataFrame :
    """Compute the outer product of series1 and series2, where series1 becomes the rows and series2 the columns."""
    return pd.DataFrame(np.outer(series1, series2), columns=series2.index, index=series1.index)

# Load default values if they haven't been set already
def load_default_values():

    global waste_tam
    if waste_tam is None:
        # Table 1: read Waste TAM from file
        tamconfig = tam.make_tam_config()
        tamsources = sma.SMA.read( DATADIR, "waste_tam", read_data=False ).as_tamsources( DATADIR )
        waste_tam = tam.TAM(tamconfig, tamsources, tamsources).ref_tam_per_region()

    global compostable_proportion
    if compostable_proportion is None:
        compostable_proportion = sma.SMA.read( DATADIR, "organic_compost_sma" ).summary(case='S1')['World']
    
    global recyclable_proportion
    if recyclable_proportion is None:
        recyclable_proportion = sma.SMA.read( DATADIR, "hc_percent_recyclable_sma" ).summary(case='S1')['World']

    global plastics_worldwide
    if plastics_worldwide is None:
        plastics_worldwide = sma.SMA.read( DATADIR, "plastics_worldwide_sma" ).summary(case='S1')['World']

