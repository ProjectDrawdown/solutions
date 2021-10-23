"""Emissions Factors module.

Conversions and lookups useful in converting to CO2 equivalents,
and other factors relating to emissions and pollutants.
"""

from functools import lru_cache
import enum
import pandas as pd
from pathlib import Path

from model.data_handler import DataHandler
from model.decorators import data_func
from model.integration import integration_alt_file

CO2EQ_SOURCE = enum.Enum('CO2EQ_SOURCE', 'AR5_WITH_FEEDBACK AR5_WITHOUT_FEEDBACK AR4 SAR')
GRID_SOURCE = enum.Enum('GRID_SOURCE', 'META IPCC')
GRID_RANGE = enum.Enum('GRID_RANGE', 'MEAN HIGH LOW')


class CO2Equiv:
    """Convert CH4/N2O/etc to equivalent CO2.

    conversion_source: which standard conversion model to follow:
       AR5 with feedback: value used in the IPCC 5th Assessment Report,
         as amended with feedback. This is the preferred selection.
       AR4: as used in the IPCC 4th Assessment Report.
       SAR: as used in the IPCC Second Assessment Report.
    """
    def __init__(self, conversion_source=None):
        self.conversion_source = conversion_source if conversion_source else CO2EQ_SOURCE.AR5_WITH_FEEDBACK
        if self.conversion_source == CO2EQ_SOURCE.AR5_WITH_FEEDBACK:
            self.CH4multiplier = 34
            self.N2Omultiplier = 298
        elif self.conversion_source == CO2EQ_SOURCE.AR5_WITHOUT_FEEDBACK:
            self.CH4multiplier = 28
            self.N2Omultiplier = 265
        elif self.conversion_source == CO2EQ_SOURCE.AR4:
            self.CH4multiplier = 25
            self.N2Omultiplier = 298
        elif self.conversion_source == CO2EQ_SOURCE.SAR:
            self.CH4multiplier = 21
            self.N2Omultiplier = 310
        else:
            raise ValueError("invalid conversion_source=" + str(self.conversion_source))


def string_to_conversion_source(text):
    """Convert the text strings passed from the Excel implementation of the models
       to the enumerated type defined in this module.
       "Advanced Controls"!I185
    """
    if str(text).lower() == "ar5 with feedback":
        return CO2EQ_SOURCE.AR5_WITH_FEEDBACK
    elif str(text).lower() == "ar5_with_feedback":
        return CO2EQ_SOURCE.AR5_WITH_FEEDBACK
    elif str(text).lower() == "ar5 without feedback":
        return CO2EQ_SOURCE.AR5_WITHOUT_FEEDBACK
    elif str(text).lower() == "ar5_without_feedback":
        return CO2EQ_SOURCE.AR5_WITHOUT_FEEDBACK
    elif str(text).lower() == "ar4":
        return CO2EQ_SOURCE.AR4
    elif str(text).lower() == "sar":
        return CO2EQ_SOURCE.SAR
    else:
        raise ValueError("invalid conversion name=" + str(text))


def string_to_emissions_grid_source(text):
    """Convert the text strings passed from the Excel implementation of the models
       to the enumerated type defined in this module.
       "Advanced Controls"!C189
    """
    if "meta" in str(text).lower():
        return GRID_SOURCE.META
    elif "ipcc" in str(text).lower():
        return GRID_SOURCE.IPCC
    else:
        raise ValueError("invalid grid source name=" + str(text))


def string_to_emissions_grid_range(text):
    """Convert the text strings passed from the Excel implementation of the models
       to the enumerated type defined in this module.
       "Advanced Controls"!D189
    """
    if str(text).lower() == "mean":
        return GRID_RANGE.MEAN
    elif str(text).lower() == "median":
        return GRID_RANGE.MEAN
    elif str(text).lower() == "high":
        return GRID_RANGE.HIGH
    elif str(text).lower() == "low":
        return GRID_RANGE.LOW
    else:
        raise ValueError("invalid grid range name=" + str(text))


class ElectricityGenOnGrid(DataHandler):
    def __init__(self, ac, grid_emissions_version="current"):
        self.ac = ac
        self.grid_emissions_version = grid_emissions_version

    @lru_cache()
    @data_func
    def conv_ref_grid_CO2eq_per_KWh(self):
        """Grid emission factors (kg CO2-eq per kwh) derived from the AMPERE 3
           MESSAGE Base model. Grid emission factors are fixed at 2015 levels
           to reflect the REF case (e.g. no significant technological change).

           'Emissions Factors'!A11:K57
        """
        result = pd.DataFrame(index=list(range(2015, 2061)),
                              columns=["World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                                       "Middle East and Africa", "Latin America", "China", "India",
                                       "EU", "USA"])
        result.index.name = "Year"
        if self.ac.emissions_grid_source == GRID_SOURCE.IPCC:
            grid = get_grid_emissions_data("ipcc")
        else:
            grid = get_grid_emissions_data("meta", self.grid_emissions_version)


        if self.ac.emissions_grid_range == GRID_RANGE.HIGH:
            result.loc[:, "World"] = grid.loc[:, "high"].values
        elif self.ac.emissions_grid_range == GRID_RANGE.LOW:
            result.loc[:, "World"] = grid.loc[:, "low"].values
        elif self.ac.emissions_grid_range == GRID_RANGE.MEAN:
            result.loc[:, "World"] = grid.loc[:, "medium"].values
        else:
            raise ValueError(f"Invalid ac.emissions_grid_range {self.ac.emissions_grid_range}")

        # Generation mixes from the AMPERE/MESSAGE WG3 BAU scenario, direct and
        # indirect emission factors by fuel from the IPCC WG3 Annex III Table A.III.2
        # https://www.ipcc.ch/pdf/assessment-report/ar5/wg3/ipcc_wg3_ar5_annex-iii.pdf
        result.loc[:, "OECD90"] = 0.454068989
        result.loc[:, "Eastern Europe"] = 0.724747956
        result.loc[:, "Asia (Sans Japan)"] = 0.457658947
        result.loc[:, "Middle East and Africa"] = 0.282243907
        result.loc[:, "Latin America"] = 0.564394712
        result.loc[:, "China"] = 0.535962403
        result.loc[:, "India"] = 0.787832379
        result.loc[:, "EU"] = 0.360629290
        result.loc[:, "USA"] = 0.665071666
        return result


    @lru_cache()
    @data_func
    def conv_ref_grid_CO2_per_KWh(self):
        """Generation mixes from the AMPERE/MESSAGE WG3 BAU scenario, direct emission
           factors by fuel from the IPCC WG3 Annex III Table A.III.2.
           "Emissions Factors"!A66:K112
        """
        result = pd.DataFrame(index=list(range(2015, 2061)),
                              columns=["World", "OECD90", "Eastern Europe", "Asia (Sans Japan)",
                                       "Middle East and Africa", "Latin America", "China", "India",
                                       "EU", "USA"])
        result.index.name = "Year"
        result.loc[:, "World"] = 0.484512031078339
        result.loc[:, "OECD90"] = 0.392126590013504
        result.loc[:, "Eastern Europe"] = 0.659977316856384
        result.loc[:, "Asia (Sans Japan)"] = 0.385555833578110
        result.loc[:, "Middle East and Africa"] = 0.185499981045723
        result.loc[:, "Latin America"] = 0.491537630558014
        result.loc[:, "China"] = 0.474730312824249
        result.loc[:, "India"] = 0.725081980228424
        result.loc[:, "EU"] = 0.297016531229019
        result.loc[:, "USA"] = 0.594563066959381
        return result

@lru_cache
def get_grid_emissions_data(emissions_type, emissions_version=None):
    datadir = Path(__file__).parents[1]/"data"/"emissions"
    if emissions_version is None:
        emissions_version = "current"
    filename = f"{emissions_type}_{emissions_version}.csv"
    altname = integration_alt_file(filename)
    if altname.is_file():
        filename = altname
    return pd.read_csv(datadir/filename)
