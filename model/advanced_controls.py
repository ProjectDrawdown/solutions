from __future__ import annotations
import dataclasses
import enum
import typing
from meta_model.parameters_class import ParameterCollection, parameterField
from model import excel_math

SOLUTION_CATEGORY = enum.Enum('SOLUTION_CATEGORY', 'REPLACEMENT REDUCTION NOT_APPLICABLE LAND OCEAN')
translate_adoption_bases = {"DEFAULT Linear": "Linear", "DEFAULT S-Curve": "Logistic S-Curve"}
valid_pds_adoption_bases = {'Linear', 'Logistic S-Curve', 'Existing Adoption Prognostications',
                            'Customized S-Curve Adoption', 'Fully Customized PDS',
                            'Bass Diffusion S-Curve', None}
valid_ref_adoption_bases = {'Default', 'Custom', None}
valid_adoption_growth = {'High', 'Medium', 'Low', None}


def string_to_solution_category(text):
    ltext = str(text).lower()
    if 'replacement' in ltext:
        return SOLUTION_CATEGORY.REPLACEMENT
    elif 'reduction' in ltext:
        return SOLUTION_CATEGORY.REDUCTION
    elif 'land' in ltext:
        return SOLUTION_CATEGORY.LAND
    elif 'not_applicable' in ltext or 'not applicable' in ltext or ltext == 'na':
        return SOLUTION_CATEGORY.NOT_APPLICABLE
    raise ValueError('invalid solution category: ' + str(text))


# ###########################################################################################################
#
#      Advanced Controls Parameter Collection
#

@dataclasses.dataclass(repr=False,eq=False,frozen=True)
class AdvancedControls(ParameterCollection):
    """Advanced Controls is a collection of parameters that determine much of the functionality of Scenarios."""

    # #########################################################################################
    #
    # General Fields
    #
    name: str = parameterField(title="Scenario Name")
    description: str = parameterField(title="Scenario Description")

    solution_category : SOLUTION_CATEGORY = parameterField(
        title="Solution Category", 
        docstring="""Whether the solution is primarily REDUCTION of emissions from an existing technology, REPLACEMENT of a technology to one with lower emissions,
        a LAND-use-based solution, an OCEAN-based solution, or NOT_APPLICABLE otherwise.""",
        excelref="'Advanced Controls'!A159", verifier=string_to_solution_category)

    creation_date : str = parameterField(
        title="Creation Date", 
        docstring="Date this scenario was created.", 
        excelref="ScenarioRecord!B4")

    # ##########################################################################################
    # 
    # Global Fields

        # Note: these first two don't actually do what they say.  There are many, many things hardwired to
        # 2014/2018 etc. start dates, and everything uses 2050 end date.
    report_start_year: int = parameterField(
        title="Report Start Year", default=2014, isglobal=True,
        docstring="First year of results to report")
 
    report_end_year: int = parameterField(
        title="Report End Year", default=2050, isglobal=True,
        docstring="Last year of results to report")

    population_model: str = parameterField(
        title="Population Model", isglobal=True,
        docstring="Which population model to use; 'current' means use the latest model", )


    # I think the followinig should be global:  check.

    # npv_discount_rate: discount rate for Net Present Value calculations.
    #   SolarPVUtil "Advanced Controls"!B141
    npv_discount_rate: float = None

    # emissions_use_co2eq: whether to use CO2-equivalent for ppm calculations.
    #   SolarPVUtil "Advanced Controls"!B189
    # emissions_grid_source: "IPCC Only" or "Meta Analysis" of multiple studies.
    #   SolarPVUtil "Advanced Controls"!C189
    # emissions_grid_range: "mean", "low" or "high" for which estimate to use.
    #   SolarPVUtil "Advanced Controls"!D189
    emissions_use_co2eq: bool = None
    emissions_grid_source: str = None
    emissions_grid_range: str = None

    # ##########################################################################################
    # 
    # Solution- and scenario-specific fields
    #
    # Solution Financial information (typically varies per-solution, not per-scenario)

    pds_2014_cost: float = parameterField( 
        title='SOLUTION First Cost per Implementation Unit',
        units= 'US$2014 per implementation or land unit',
        docstring= """Cost to acquire + install, per implementation unit, for the SOLUTION.
        E.g. What is the cost to acquire and install rooftop solar PV?""",
        excelref= 'SolarPVUtil "Advanced Controls"!B128')

    ref_2014_cost: float = parameterField( 
        title='Reference First Cost per Implementation Unit',
        units= 'US$2014 per implementation or land unit',
        docstring= """Cost to acquire + install, per implementation unit, for the SOLUTION in the reference case.
        E.g. What is the cost to acquire and install rooftop solar PV?""",
        excelref= 'SolarPVUtil "Advanced Controls"!B128')

    conv_2014_cost: float = parameterField( 
        title='CONVENTIONAL First Cost per Implementation Unit',
        units= 'US$2014 per implementation or land unit',
        docstring= """Cost to acquire + install, per implementation unit, conventional alternative to this solution.
            E.g. What is the cost to purchase an internal combustion engine (ICE) vehicle?""",
        excelref= 'SolarPVUtil "Advanced Controls"!B95')

    soln_first_cost_efficiency_rate: float = parameterField( 
        title='SOLUTION First Cost Learning Rate',
        units= '%',
        docstring= """Percentage by which the First Cost declines per SOLUTION implementation unit, as technology matures.
        With already mature echnologies, this number should be zero.""",
        excelref= 'SolarPVUtil "Advanced Controls"!C128')

    conv_first_cost_efficiency_rate: float = parameterField(
        title='CONVENTIONAL First Cost Learning Rage',
        units= '%',
        docstring= """Percentage by which the First Cost declines per CONVENTIONAL implementation unit, as technology matures.
        With already mature echnologies, this number should be zero.""",
        excelref= 'SolarPVUtil "Advanced Controls"!C95')
