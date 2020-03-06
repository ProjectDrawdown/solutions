"""Implements the Advanced Controls, settings which have a default
   but can be overridden to fit particular needs.
"""

import dataclasses
import enum
import glob
import json
import os
import typing

import pandas as pd
import pytest
from model import emissionsfactors as ef
from model import excel_math
from model.dd import REGIONS, MAIN_REGIONS

SOLUTION_CATEGORY = enum.Enum('SOLUTION_CATEGORY', 'REPLACEMENT REDUCTION NOT_APPLICABLE LAND OCEAN')
translate_adoption_bases = {"DEFAULT Linear": "Linear", "DEFAULT S-Curve": "Logistic S-Curve"}
valid_pds_adoption_bases = {'Linear', 'Logistic S-Curve', 'Existing Adoption Prognostications',
                            'Customized S-Curve Adoption', 'Fully Customized PDS',
                            'Bass Diffusion S-Curve', None}
valid_ref_adoption_bases = {'Default', 'Custom', None}
valid_adoption_growth = {'High', 'Medium', 'Low', None}


@dataclasses.dataclass(eq=True, frozen=True)
class AdvancedControls:
    """Advanced Controls module, with settings impacting other modules."""

    # solution_category (SOLUTION_CATEGORY): Whether the solution is primarily REDUCTION of
    #   emissions from an existing technology, REPLACEMENT of a technology to one with lower
    #   emissions, or NOT_APPLICABLE for something else entirely.  'Advanced Controls'!A159
    solution_category: typing.Any = None

    # vmas: dict of VMA objects required for calculation of certain values.
    #    dict keys should be the VMA title (found in VMA_info.csv in solution dir).
    #    Example:
    #    {'Sequestration Rates': vma.VMA('path_to_soln_vmas' + 'Sequestration_Rates.csv')}
    vmas: typing.Dict = None

    # name: string name of this scenario.
    name: str = None

    # description: freeform text describing the construction or intention for this scenario.
    description: str = None

    # js: JSON this AdvancedControls object was created from (if any)
    # jsfile: the filename containing the JSON (if any)
    js: str = None
    jsfile: str = None

    # pds_2014_cost: US$2014 cost to acquire + install, per implementation
    #   unit (ex: kW for energy scenarios), for the Project Drawdown Solution (PDS)
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    pds_2014_cost: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['SOLUTION First Cost per Implementation Unit'],
        'subtitle': '(implementation/land units)',
        'tooltip': ("SOLUTION First Cost per Implementation Unit\n\n"
            "NOTE: This is the cost of acquisition and the cost of installation "
            "(sometimes one and the same) or the cost of initiating a program/practice "
            "(for solutions where there is no direct artifact to acquire and install) "
            "per Implementation unit of the SOLUTION.\n\n"
            "E.g. What is the cost to acquire and install rooftop solar PV?"),
        'excelref': 'SolarPVUtil "Advanced Controls"!B128',
        })

    # ref_2014_cost: US$2014 cost to acquire + install, per implementation
    #   unit, for the reference technology.
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    ref_2014_cost: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['SOLUTION First Cost per Implementation Unit'],
        'subtitle': '(implementation/land units)',
        'tooltip': ("SOLUTION First Cost per Implementation Unit\n\n"
            "NOTE: This is the cost of acquisition and the cost of installation "
            "(sometimes one and the same) or the cost of initiating a program/practice "
            "(for solutions where there is no direct artifact to acquire and install) "
            "per Implementation unit of the SOLUTION.\n\n"
            "E.g. What is the cost to acquire and install rooftop solar PV?"),
        'excelref': 'SolarPVUtil "Advanced Controls"!B128',
        })

    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    conv_2014_cost: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['CONVENTIONAL First Cost per Implementation Unit'],
        'subtitle': '(implementation units)',
        'tooltip': ("CONVENTIONAL First Cost per Implementation Unit for replaced "
            "practices/technologies\n\n"
            "NOTE: This is the cost of acquisition and the cost of installation "
            "(sometimes one and the same) or the cost of initiating a program/practice "
            "(for solutions where there is no direct artifact to acquire and install) "
            "per Unit of Implementation of the CONVENTIONAL mix of practices (those "
            "practices that do not include the technology in question.\n\n"
            "E.g. What is the cost to purchase an internal combustion engine (ICE) "
            "vehicle?"),
        'excelref': 'SolarPVUtil "Advanced Controls"!B95',
        })

    soln_first_cost_efficiency_rate: float = dataclasses.field(default=None, metadata={
        'vma_titles': [],
        'subtitle': '(Rates are usually Close to 0%)',
        'tooltip': ("First Cost Learning Rate\n"
            "NOTE: Learning curves (sometimes called experience curves) are used to analyze "
            "a well-known and easily observed phenomena: humans become increasingly efficient "
            "with experience. The first time a product is manufactured or a service provided, "
            "costs are high, work is inefficient, quality is marginal, and time is wasted. "
            "As experience is acquired, costs decline, efficiency and quality improve, "
            "and waste is reduced.\n\n"

            "In many situations, this pattern of improvement follows a predictable pattern: "
            'for every doubling of (or some multiple of) production of units, the "cost" of '
            "production (measured in dollars, hours, or in terms of other inputs) declines "
            "to some fraction of previous costs.\n\n"

            "This learning rate will be applied to the technology in question for both the "
            "Optimal and BusinessAsUsual scenario."),
        'excelref': 'SolarPVUtil "Advanced Controls"!C128',
        })

    conv_first_cost_efficiency_rate: float = dataclasses.field(default=None, metadata={
        'vma_titles': [],
        'subtitle': '(Rates are usually Close to 0%)',
        'tooltip': ("First Cost Learning Rate\n"
            "NOTE: Learning curves (sometimes called experience curves) are used to analyze "
            "a well-known and easily observed phenomena: humans become increasingly efficient "
            "with experience. The first time a product is manufactured or a service provided, "
            "costs are high, work is inefficient, quality is marginal, and time is wasted. "
            "As experience is acquired, costs decline, efficiency and quality improve, and "
            "waste is reduced.\n\n"

            "In many situations, this pattern of improvement follows a predictable pattern: "
            'for every doubling of (or some multiple of) production of units, the "cost" of '
            "production (measured in dollars, hours, or in terms of other inputs) declines "
            "to some fraction of previous costs. \n\n"

            "This would be the learning rate or efficiency rate for the CONVENTIONAL mix of "
            "practices. In many/most cases this will be 0% if the market is mature."),
        'excelref': 'SolarPVUtil "Advanced Controls"!C95',
        })

    soln_first_cost_below_conv: bool = dataclasses.field(default=None, metadata={
        'vma_titles': [],
        'subtitle': '',
        'tooltip': ("Allow solution First Cost to go Below Conventional?\n",
            "NOTE: The Solution First Cost may decline below that of the Conventional due to "
            "the learning rate chosen. This may be acceptable in some cases for instance when "
            "the projections in the literature indicate so. In other cases, it may not be "
            "likely for the Solution to become cheaper than the Conventional."),
        'excelref': 'SolarPVUtil "Advanced Controls"!C132',

        })

    soln_energy_efficiency_factor: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['SOLUTION Energy Efficiency Factor'],
        'subtitle': '',
        'tooltip': ("Energy Efficiency Factor SOLUTION\n"
            "soln_energy_efficiency_factor: Units of energy reduced per year per "
            "functional unit installed.\n\n"

            "FOR CLEAN RENEWABLE ENERGY SOLUTIONS: enter 0 (e.g. implementing solar PV "
            "fully replaces existing fossil fuel-based generation, but does not reduce "
            "the amount of energy generated)\n\n"

            "FOR ENERGY EFFICIENCY SOLUTIONS: enter positive number representing total "
            "energy reduced, 0 < X < 1 (e.g. HVAC efficiencies reduce the average annual "
            "energy consumption of buildings, by square meters of floor space; they still "
            "use the electric grid, but significantly less)\n\n"

            "FOR SOLUTIONS THAT CONSUME MORE ENERGY THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE: "
            "Use the next input, Total Annual Energy Used SOLUTION (e.g. electric vehicles "
            "use energy from the electric grid, whereas conventional vehicles use only fuel)"
            ),
        'excelref': 'SolarPVUtil "Advanced Controls"!C159; Silvopasture "Advanced Controls"!C123',
        })

    conv_annual_energy_used: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['CONVENTIONAL Total Energy Used per Functional Unit'],
        'subtitle': '',
        'tooltip': ("Average Electricty Used CONVENTIONAL\n"
            "NOTE: for solutions that reduce electricity consumption per functional unit, "
            "enter the average electricity used per functional unit of the conventional "
            "technologies/practices."),
        'excelref': 'SolarPVUtil "Advanced Controls"!B159; Silvopasture "Advanced Controls"!B123',
        })

    soln_annual_energy_used: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['SOLUTION Total Energy Used per Functional Unit'],
        'subtitle': '',
        'tooltip': ("ALTERNATIVE APPROACH Annual Energy Used SOLUTION\n"
            "This refers to the units of average energy used per year per functional unit "
            "installed.\n\n"
            "This is an optional variable to be used in cases where a) the literature "
            "reports the energy use of the solution rather than energy efficiency; or "
            "b) the solution uses more electricity than the conventional "
            "technologies/practices.\n\n"
            "E.g. electric vehicles use energy from the electric grid, whereas "
            "conventional vehicles use only fuel"),
        'excelref': 'SolarPVUtil "Advanced Controls"!D159',
        })

    conv_fuel_consumed_per_funit: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['CONVENTIONAL Fuel Consumed per Functional Unit'],
        'subtitle': '',
        'tooltip': ("Fuel Consumed per CONVENTIONAL Functional Unit\n"
            "This refers to the unit (default is Liters) of FUEL used per year per "
            "cumulative unit installed. The equation may need to be edited if your "
            "energy savings depend on the marginal unit installed rather than the "
            "cumulative units."),
        'excelref': 'SolarPVUtil "Advanced Controls"!F159; Silvopasture "Advanced Controls"!F123',
        })

    soln_fuel_efficiency_factor: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['SOLUTION Fuel Efficiency Factor'],
        'subtitle': '',
        'tooltip': ("Fuel Efficiency Factor - SOLUTION\n"
            "This refers to the % fuel reduced by the SOLUTION relative to the "
            "CONVENTIONAL mix of technologies/practices. The Percent reduction is "
            "assumed to apply to the Conventional Fuel Unit, if different to the "
            "Solution Fuel Unit.\n\n"

            "FOR REPLACEMENT SOLUTIONS: enter 1 (e.g. electric vehicles fully replace fuel "
            "consumption with electricity use -- but be sure to add a negative value for "
            "Annual Energy Reduced from Electric Grid Mix!)\n\n"

            "FOR FUEL EFFICIENCY SOLUTIONS: enter positive number representing total fuel "
            "reduced, 0 < X < 1  (e.g. hybrid-electric vehicles partially replace fuel "
            "consumption with electricity use, it thus uses less fuel compared to conventional "
            "vehicles)\n\n"

            "FOR SOLUTIONS THAT CONSUME MORE FUEL THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE: "
            "enter negative number representing total additional fuel used, X < 0 (e.g. we "
            "hope solutions do not actually consume more fuel than the conventional practice, "
            "check with the senior research team if you run into this)"),
        'excelref': 'SolarPVUtil "Advanced Controls"!G159; Silvopasture "Advanced Controls"!G123',
        })

    conv_fuel_emissions_factor: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': [],
        'subtitle': '',
        'tooltip': 'direct fuel emissions per funit, conventional',
        'excelref': 'SolarPVUtil "Advanced Controls"!I159',
        })

    soln_fuel_emissions_factor: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': [],
        'subtitle': '',
        'tooltip': 'direct fuel emissions per funit, solution',
        'excelref': 'SolarPVUtil "Advanced Controls"!I163; DistrictHeating "Advanced Controls"!I144',
        })

    conv_emissions_per_funit: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['CONVENTIONAL Direct Emissions per Functional Unit'],
        'subtitle': '',
        'tooltip': ("Direct Emissions per CONVENTIONAL Functional Unit\n"
            "This represents the direct CO2-eq emissions that result per functional unit "
            "that are not accounted for by use of the electric grid or fuel consumption."),
        'excelref': 'SolarPVUtil "Advanced Controls"!C174',
        })

    soln_emissions_per_funit: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['SOLUTION Direct Emissions per Functional Unit'],
        'subtitle': '',
        'tooltip': ("Direct Emissions per SOLUTION Functional Unit\n"
            "This represents the direct CO2-eq emissions that result per functional unit "
            "that are not accounted for by use of the electric grid or fuel consumption."),
        'excelref': 'SolarPVUtil "Advanced Controls"!D174',
        })

    # ch4_is_co2eq: True if CH4 emissions measurement is in terms of CO2
    #   equivalent, False if measurement is in units of CH4 mass.
    #   derived from SolarPVUtil "Advanced Controls"!I184
    ch4_is_co2eq: bool = None

    # n2o_is_co2eq: True if N2O emissions measurement is in terms of CO2
    #   equivalent, False if measurement is in units of N2O mass.
    #   derived from SolarPVUtil "Advanced Controls"!J184
    n2o_is_co2eq: bool = None

    # co2eq_conversion_source: One of the conversion_source names
    #   defined in model/emissions_factors.py like "AR5 with feedback" or "AR4"
    #   SolarPVUtil "Advanced Controls"!I185
    co2eq_conversion_source: str = None

    ch4_co2_per_funit: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['CH4-CO2eq Tons Reduced'],
        'subtitle': '',
        'tooltip': ("CH4-CO2eq Tons Reduced\n"
            "CO2-equivalent CH4 emitted per functional unit, in tons."),
        'excelref': 'SolarPVUtil "Advanced Controls"!I174',
        })

    n2o_co2_per_funit: float = dataclasses.field(default=0.0, metadata={
        'vma_titles': ['N2O-CO2eq Tons Reduced'],
        'subtitle': '',
        'tooltip': ("N2O-CO2eq Tons Reduced\n"
            "CO2-equivalent N2O emitted per functional unit, in tons."),
        'excelref': 'SolarPVUtil "Advanced Controls"!J174',
        })

    soln_indirect_co2_per_iunit: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['SOLUTION Indirect CO2 Emissions per Unit'],
        'subtitle': '',
        'tooltip': ("Indirect CO2 Emissions per SOLUTION Implementation Unit\n"
            "CO2-equivalent indirect emissions per iunit, in tons."),
        'excelref': 'SolarPVUtil "Advanced Controls"!G174',
        })

    conv_indirect_co2_per_unit: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['CONVENTIONAL Indirect CO2 Emissions per Unit'],
        'subtitle': '',
        'tooltip': ("Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit\n"
            "NOTE: this represents the indirect CO2 emissions that result per implementation "
            "unit installed. The production, distribution, and installation of "
            "technologies/practices often generate their own emissions that are not associated "
            "with their function.\n\n"

            "E.g. the production of ICE vehicles is an energy- and resource-intensive endeavor "
            "that generates indirect emissions that must be accounted for.\n"),
        'excelref': 'SolarPVUtil "Advanced Controls"!F174',
        })

    # conv_indirect_co2_is_iunits: whether conv_indirect_co2_per_unit is
    #   iunits (True) or funits (False).  SolarPVUtil "Advanced Controls"!F184
    conv_indirect_co2_is_iunits: bool = None

    soln_lifetime_capacity: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['SOLUTION Lifetime Capacity'],
        'subtitle': '(use until replacement is required)',
        'tooltip': ("Lifetime Capacity - SOLUTION\n\n"
            "NOTE: This is the average expected number of functional units generated by the "
            "SOLUTION throughout their lifetime before replacement is required. If no replacement "
            "time is discovered or applicable the fellow will default to 100 years.\n\n"

            "E.g. an electric vehicle will have an average number of passenger kilometers it "
            "can travel until it can no longer be used and a new vehicle is required. Another "
            "example would be an efficient HVAC system, which can only service a certain amount "
            "of floor space over a period of time before it will require replacement."),
        'excelref': 'SolarPVUtil "Advanced Controls"!E128',
        })

    soln_avg_annual_use: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['SOLUTION Average Annual Use'],
        'subtitle': '(annual use)',
        'tooltip': ("Average Annual Use - SOLUTION\n\n"
            "NOTE:  Average Annual Use is the average annual use of the technology/practice, "
            "in functional units per implementation unit. This will likely differ significantly "
            "based on location, be sure to note which region the data is coming from. If data "
            "varies substantially by region, a weighted average may need to be used.\n\n"

            "E.g. the average annual number of passenger kilometers (pkm) traveled per "
            "electric vehicle."),
        'excelref': 'SolarPVUtil "Advanced Controls"!F128',
        })

    conv_lifetime_capacity: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['CONVENTIONAL Lifetime Capacity'],
        'subtitle': '(use until replacement is required)',
        'tooltip': ("Lifetime Capacity - CONVENTIONAL\n\n"
            "NOTE: This is the average expected number of functional units "
            "generated by the CONVENTIONAL mix of technologies/practices "
            "throughout their lifetime before replacement is required.  "
            "If no replacement time is discovered or applicable, please "
            "use 100 years.\n\n"
            "E.g. a vehicle will have an average number of passenger kilometers "
            "it can travel until it can no longer be used and a new vehicle is "
            "required. Another example would be an HVAC system, which can only "
            "service a certain amount of floor space over a period of time before "
            "it will require replacement."),
        'excelref': 'SolarPVUtil "Advanced Controls"!E95',
        })

    conv_avg_annual_use: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['CONVENTIONAL Average Annual Use'],
        'subtitle': '(annual use)',
        'tooltip': ("Average Annual Use - CONVENTIONAL\n\n"
            "NOTE:  Average Annual Use is the average annual use of the technology/practice, "
            "in functional units per implementation unit. This will likely differ significantly "
            "based on location, be sure to note which region the data is coming from. If data "
            "varies substantially by region, a weighted average may need to be used.\n\n"

            "E.g. the average annual number of passenger kilometers (pkm) traveled per "
            "conventional vehicle.\n"),
        'excelref': 'SolarPVUtil "Advanced Controls"!F95',
        })

    # report_start_year: first year of results to report (typically 2020).
    #   SolarPVUtil "Advanced Controls"!H4
    report_start_year: int = 2020

    # report_end_year: last year of results to report (typically 2050).
    #   SolarPVUtil "Advanced Controls"!I4
    report_end_year: int = 2050

    soln_var_oper_cost_per_funit: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['SOLUTION Variable Operating Cost (VOM) per Functional Unit'],
        'subtitle': '(functional units)',
        'tooltip': ("SOLUTION Variable Operating Cost (VOM)\n"
            "NOTE: This is the annual operating cost per functional unit, derived from the "
            "SOLUTION. In most cases this will be expressed as a cost per 'some unit of "
            "energy'.\n\n"

            "E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this "
            "can be considered the weighted average price of fuel per passenger kilometer."),
        'excelref': 'SolarPVUtil "Advanced Controls"!H128',
        })

    soln_fixed_oper_cost_per_iunit: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['SOLUTION Operating Cost per Functional Unit per Annum',
            'SOLUTION Fixed Operating Cost (FOM)'],
        'subtitle': '(per ha per annum)',
        'tooltip': ("SOLUTION Operating Cost per Functional Unit per Annum\n\n"
            "NOTE: This is the Operating Cost per functional unit, derived from the "
            "SOLUTION. In most cases this will be expressed as a cost per 'hectare of "
            "land'.\n\n"
            "This annualized value should capture both the variable costs for maintaining "
            "the SOLUTION practice as well as the fixed costs. The value should reflect "
            "the average over the reasonable lifetime of the practice."),
        # That tooltip is phrased for land solutions, one for RRS would be:
        'tooltipFIXME': ("SOLUTION Operating Cost per Functional Unit per Annum\n\n"
            "NOTE: This is the annual operating cost per implementation unit, derived from "
            "the SOLUTION.  In most cases this will be expressed as a cost per 'some unit of "
            "installation size' E.g., $10,000 per kw. In terms of transportation, this can be "
            "considered the total insurance, and maintenance cost per car.\n\n"

            "Purchase costs can be amortized here or included as a first cost, but not both."),
        'excelref': 'SolarPVUtil "Advanced Controls"!I128; Silvopasture "Advanced Controls"!C92',
        })

    # soln_fuel_cost_per_funit: Fuel/consumable cost per functional unit.
    #   SolarPVUtil "Advanced Controls"!K128
    soln_fuel_cost_per_funit: float = None

    conv_var_oper_cost_per_funit: float = dataclasses.field(default=None, metadata={
        'vma_titles': ['CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit'],
        'subtitle': '(functional units)',
        'tooltip': ("CONVENTIONAL Variable Operating Cost (VOM)\n\n"
            "NOTE: This is the annual operating cost per functional unit, derived from the "
            "CONVENTIONAL mix of technologies. In most cases this will be expressed as a "
            "cost per 'some unit of energy'.\n\n"

            "E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this "
            "can be considered the weighted average price of fuel per passenger kilometer."),
        'excelref': 'SolarPVUtil "Advanced Controls"!H95',
        })

    # conv_fixed_oper_cost_per_iunit: as soln_fixed_oper_cost_per_funit.
    #   SolarPVUtil "Advanced Controls"!I95 / Silvopasture "Advanced Controls"!C77
    conv_fixed_oper_cost_per_iunit: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['CONVENTIONAL Operating Cost per Functional Unit per Annum',
            'CONVENTIONAL Fixed Operating Cost (FOM)'],
        'subtitle': '(per ha per annum)',
        'tooltip': ("CONVENTIONAL Operating Cost per Functional Unit per Annum\n\n"
            "NOTE: This is the Operating Cost per functional unit, derived "
            "from the CONVENTIONAL mix of technologies/practices.  In most "
            "cases this will be expressed as a cost per 'hectare of land'.\n\n"
            "This annualized value should capture the variable costs for "
            "maintaining the CONVENTIONAL practice, as well as  fixed costs. "
            "The value should reflect the average over the reasonable lifetime "
            "of the practice.\n\n"),
        'excelref': 'SolarPVUtil "Advanced Controls"!I95; Silvopasture "Advanced Controls"!C77',
        })

    # conv_fuel_cost_per_funit: as soln_fuel_cost_per_funit.
    #   SolarPVUtil "Advanced Controls"!K95
    conv_fuel_cost_per_funit: float = None

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

    # soln_ref_adoption_regional_data: whether funit adoption should add the regional data
    #   to estimate the World, or perform a separate estimate for the world.
    #   SolarPVUtil "Advanced Controls"!B284
    # soln_pds_adoption_regional_data: as soln_ref_adoption_regional_data.
    #   SolarPVUtil "Advanced Controls"!B246
    soln_ref_adoption_regional_data: bool = None
    soln_pds_adoption_regional_data: bool = None

    # soln_ref_adoption_basis: whether to use adoption_data.py or custom_adoption.py.
    #   Must be one of valid_ref_adoption_bases.  SolarPVUtil "Advanced Controls"!B279
    # soln_ref_adoption_custom_name: Name of the Custom REF Adoption source to use, if
    #   soln_ref_adoption_basis is "Custom".  Insulation "Advanced Controls"!B267
    soln_ref_adoption_basis: str = None
    soln_ref_adoption_custom_name: str = None

    # soln_pds_adoption_basis: the type of interpolation to fill in adoption data for
    #   each year. Must be one of valid_pds_adoption_bases. SolarPVUtil "Advanced Controls"!B243
    # soln_pds_adoption_custom_name: Name of the Custom PDS Adoption source to use, if
    #   soln_pds_adoption_basis is "Fully Customized PDS".
    #   SmartThermostats "Advanced Controls"!H250
    soln_pds_adoption_basis: str = None
    soln_pds_adoption_custom_name: str = None

    # soln_pds_adoption_prognostication_source: the name of one specific data source, or the
    #   name of a class of sources (like "Conservative Cases" or "Ambitious Cases"),
    #   or "ALL SOURCES" to take the average of all sources. SolarPVUtil "Advanced Controls"!B265
    # soln_pds_adoption_prognostication_trend: the type of curve fit to use like 2nd order
    #   polynomial or exponential. SolarPVUtil "Advanced Controls"!B270
    # soln_pds_adoption_prognostication_growth: High, Medium, or Low projected growth.
    #   SolarPVUtil "Advanced Controls"!C270
    soln_pds_adoption_prognostication_source: str = None
    soln_pds_adoption_prognostication_trend: str = None
    soln_pds_adoption_prognostication_growth: str = None

    # pds_source_post_2014: The name of the data source to use for the PDS case for
    #   years after 2014. SolarPVUtil "Advanced Controls"!B55
    # ref_source_post_2014: The name of the data source to use for the REF case for
    #   years after 2014. SolarPVUtil "Advanced Controls"!B54
    # source_until_2014: The name of the data source to use for all cases for years
    #   2014 and before. SolarPVUtil "Advanced Controls"!B53
    pds_source_post_2014: str = None
    ref_source_post_2014: str = None
    source_until_2014: str = None

    # ref_adoption_use_pds_years: years for which the Helpertables REF adoption
    #   for 'World' should use the PDS adoption values. SolarPVUtil "ScenarioRecord"! offset 218
    # pds_adoption_use_ref_years: years for which the Helpertables PDS adoption
    #   for 'World' should use the REF adoption values. SolarPVUtil "ScenarioRecord"! offset 219
    ref_adoption_use_pds_years: typing.List[int] = dataclasses.field(default_factory=list)
    pds_adoption_use_ref_years: typing.List[int] = dataclasses.field(default_factory=list)

    # pds_base_adoption: OBSOLETE a list of (region, float) tuples of the base adoption for the
    #   PDS calculations. For example: [('World', 150000000.0), ('OECD90', 90000000.0), ...]
    #   SolarPVUtil "ScenarioRecord" rows 151 - 160.
    #   This is being replaced by ref_base_adoption, once we regenerate all solutions.
    # ref_base_adoption: a dict of region: float values of the base adoption for the REF
    #   calculations. For example: {'World': 150000000.0, 'OECD90': 90000000.0, ...}
    #   SolarPVUtil "ScenarioRecord" rows 151 - 160.
    # pds_adoption_final_percentage: a list of (region, %) tuples of the final adoption
    #   percentage for the PDS calculations. For example: [('World', 0.54), ('OECD90', 0.60), ...]
    #   SolarPVUtil "ScenarioRecord" rows 170 - 179.
    pds_base_adoption: typing.List[tuple] = None
    ref_base_adoption: typing.Dict = None
    pds_adoption_final_percentage: typing.List[tuple] = None

    # pds_adoption_s_curve_innovation: a list of (region, float) tuples of the innovation
    #   factor used in the Bass Diffusion S-Curve model.
    #   SolarPVUtil "ScenarioRecord" rows 170 - 179.
    # pds_adoption_s_curve_imitation: a list of (region, float) tuples of the innovation
    #   factor used in the Bass Diffusion S-Curve model.
    #   SolarPVUtil "ScenarioRecord" rows 170 - 179.
    pds_adoption_s_curve_innovation: typing.List[tuple] = None
    pds_adoption_s_curve_imitation: typing.List[tuple] = None

    # LAND only
    tco2eq_reduced_per_land_unit: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['t CO2-eq (Aggregate emissions) Reduced per Land Unit'],
        'subtitle': '(t CO2-eq / ha)',
        'tooltip': ("t CO2-eq (Aggregate emissions) Reduced per Land Unit\n"
            "NOTE: This is the CO2-equivalent reduced per land unit (million Hectare)."),
        'excelref': 'ForestProtection "Advanced Controls"!B138',
        })

    # tco2eq_rplu_rate: whether tco2eq_reduced_per_land_unit is 'One-time' or 'Annual'
    #    ForestProtection "Advanced Controls"!B148 (Land models)
    tco2eq_rplu_rate: str = None
    tco2_rplu_rate: str = None
    tn2o_co2_rplu_rate: str = None
    tch4_co2_rplu_rate: str = None

    tco2_reduced_per_land_unit: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['t CO2 Reduced per Land Unit'],
        'subtitle': '(t CO2 / ha)',
        'tooltip': ("t CO2 Reduced per Land Unit\n"
            "NOTE: This is the CO2 reduced per land unit (million Hectare)."),
        'excelref': 'ForestProtection "Advanced Controls"!C148',
        })

    tn2o_co2_reduced_per_land_unit: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['t N2O-CO2-eq Reduced per Land Unit'],
        'subtitle': '(t N2O-CO2-eq / ha)',
        'tooltip': ("t N2O-CO2-eq Reduced per Land Unit\n"
            "NOTE: This is the N2O reduced per land unit (million Hectare) but converted "
            "to CO2-eq."),
        'excelref': 'ForestProtection "Advanced Controls"!D148',
        })

    tch4_co2_reduced_per_land_unit: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['t CH4-CO2-eq Reduced per Land Unit'],
        'subtitle': '',
        'tooltip': ("t CH4-CO2-eq Reduced per Land Unit\n"
            "NOTE: This is the CH4 reduced per land unit (million Hectare) but "
            "converted to CO2-eq."),
        'excelref': 'ForestProtection "Advanced Controls"!E148',
        })

    # emissions_use_agg_co2eq: Use Aggregate CO2-eq instead of Individual GHG for direct emissions
    #  ForestProtection "Advanced Controls"!C155 (Land models)
    emissions_use_agg_co2eq: bool = None

    # seq_rate_global: carbon sequestration rate for All Land or All of Special Land.
    #  Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #  "Advanced Controls"!B173 (Land models)
    seq_rate_global: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['Sequestration Rates'],
        'subtitle': '(t C / ha /year)',
        'tooltip': ("Sequestration Rate for All Land or All of Special Land\n"
            "NOTE: Once a  Rate is entered here, it would be used. If rates are available for "
            "each Thermal-Humidity Regime, leave this blank."),
        'ecelref': '"Advanced Controls"!B173 (Land models)',
        })

    #seq_rate_per_regime (dict of float): carbon sequestration rate for each thermal-moisture
    #  regime. "Advanced Controls"!C173:G173 (Land models)
    seq_rate_per_regime: typing.Dict = None

    degradation_rate: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['Growth Rate of Land Degradation'],
        'subtitle': '',
        'tooltip': ("Growth Rate of Land Degradation\n"
            'NOTE: This is the rate of degradation of unprotected land (or "At Risk" land '
            "that is neither protected nor already degraded. This number should exclude the "
            "Disturbance Rate if that is also entered."),
        'excelref': 'ForestProtection "Advanced Controls"!B187',
        })

    disturbance_rate: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['Disturbance Rate'],
        'subtitle': '',
        'tooltip': ("Disturbance Rate\n"
            "NOTE: This is the annual percent of some output that fails for some reason "
            "(possibly due to weather, human activities, etc). It applies ONLY to land "
            "adopted/protected with the SOLUTION, and affects degraded land, direct emissions, "
            "sequestration and  yield. The SOLUTION adoption remains unaffected.\n\n"

            "Ensure that the Growth Rate of Land degradation does not already account for "
            "the Disturbance Rate if it is entered here."),
        'excelref': 'TropicalForests. "Advanced Controls"!I173',
        })

    # global_multi_for_regrowth: Global multiplier for regrowth
    #   ForestProtection "Advanced Controls"!E187 (Land models)
    global_multi_for_regrowth: float = None

    # soln_expected_lifetime: solution expected lifetime in years
    #   "Advanced Controls"!F92 (Land models)
    # conv_expected_lifetime: conventional expected lifetime in years. Default value is 30.
    #   "Advanced Controls"!F77 (Land models)
    soln_expected_lifetime: float = None
    conv_expected_lifetime: float = None

    # yield_from_conv_practice: conventional yield in DM tons fodder/ha/year.
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   "Advanced Controls"!G77 (Land models)
    yield_from_conv_practice: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['Yield from CONVENTIONAL Practice'],
        'subtitle': '(kg / ha /yr)',
        'tooltip': ("Yield  from CONVENTIONAL Practice"),
        'excelref': '"Advanced Controls"!G77 (Land models)',
        })

    # yield_gain_from_conv_to_soln: yield % increase from conventional to solution.
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   "Advanced Controls"!G92 (Land models)
    yield_gain_from_conv_to_soln: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['Yield Gain (% Increase from CONVENTIONAL to SOLUTION)'],
        'subtitle': '%',
        'tooltip': ("Yield Gain (% Increase from CONVENTIONAL to SOLUTION)"),
        'excelref': '"Advanced Controls"!G92 (Land models)',
        })

    # use_custom_tla: whether to use custom TLA data instead of Drawdown land allocation
    #   "Advanced Controls"!E54 (Land models)
    use_custom_tla: bool = None

    # harvest_frequency: new growth is harvested/cleared every ... (years)
    #   Afforestation "Advanced Controls"!B187
    harvest_frequency: float = None

    carbon_not_emitted_after_harvesting: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing'],
        'subtitle': '(t C/ha)',
        'tooltip': ("Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing\n"),
        'excelref': 'Afforestation "Advanced Controls"!H173',
        })

    # avoided_deforest_with_intensification: Factor for avoiding deforestation by more
    #   intensively using the land. Women Smallholders "Advanced Controls"!E205
    avoided_deforest_with_intensification: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['Avoided Deforested Area With Increase in Agricultural Intensification'],
        'subtitle': '',
        'tooltip': ("Avoided Deforested Area With Increase in Agricultural Intensification"),
        'excelref': 'Women Smallholders "Advanced Controls"!E205',
        })

    # delay_protection_1yr: Delay Impact of Protection by 1 Year? (Leakage)
    #   ForestProtection "Advanced Controls"!B200 (land models)
    # delay_regrowth_1yr: Delay Regrowth of Degraded Land by 1 Year?
    #   ForestProtection "Advanced Controls"!C200 (land models)
    delay_protection_1yr: bool = None
    delay_regrowth_1yr: bool = None

    # include_unprotected_land_in_regrowth_calcs: Include Unprotected Land in Regrowth Calculations?
    #   ForestProtection "Advanced Controls"!D200 (land models)
    include_unprotected_land_in_regrowth_calcs: bool = None

    # land_annual_emissons_lifetime (bool): Lifetime of tracked emissions.
    #   Conservation Agriculture "Advanced Controls"!D150 (land models)
    land_annual_emissons_lifetime: bool = None

    # MISSING DESCRIPTION
    tC_storage_in_protected_land_type: typing.Any = dataclasses.field(default=None, metadata={
        'vma_titles': ['t C storage in Protected Landtype'],
        'subtitle': '',
        'tooltip': ("t C storage in Protected Landtype"),
        'excelref': '',
        })

    def __post_init__(self):
        object.__setattr__(self, 'incorrect_cached_values', {})
        for field in dataclasses.fields(self):
            vma_titles = field.metadata.get('vma_titles', None)
            if vma_titles is not None and self.vmas is not None:
                val = getattr(self, field.name)
                newval = self._substitute_vma(val=val, vma_titles=vma_titles)
                if newval is not None:
                    object.__setattr__(self, field.name, newval)

        if isinstance(self.solution_category, str):
            object.__setattr__(self, 'solution_category',
                    string_to_solution_category(self.solution_category))
        if isinstance(self.co2eq_conversion_source, str):
            object.__setattr__(self, 'co2eq_conversion_source', ef.string_to_conversion_source(
                    self.co2eq_conversion_source))
        if isinstance(self.emissions_grid_source, str):
            object.__setattr__(self, 'emissions_grid_source', ef.string_to_emissions_grid_source(
                    self.emissions_grid_source))
        if isinstance(self.emissions_grid_range, str):
            object.__setattr__(self, 'emissions_grid_range', ef.string_to_emissions_grid_range(
                    self.emissions_grid_range))

        object.__setattr__(self, 'soln_ref_adoption_basis', translate_adoption_bases.get(
                self.soln_ref_adoption_basis, self.soln_ref_adoption_basis))
        if self.soln_ref_adoption_basis not in valid_ref_adoption_bases:
            raise ValueError("invalid adoption basis name=" + str(self.soln_ref_adoption_basis))

        object.__setattr__(self, 'soln_pds_adoption_basis', translate_adoption_bases.get(
                self.soln_pds_adoption_basis, self.soln_pds_adoption_basis))
        if self.soln_pds_adoption_basis not in valid_pds_adoption_bases:
            raise ValueError("invalid adoption basis name=" + str(self.soln_pds_adoption_basis))

        if self.soln_pds_adoption_prognostication_growth not in valid_adoption_growth:
            g = self.soln_pds_adoption_prognostication_growth
            raise ValueError("invalid adoption prognostication growth name=" + str(g))

        intersect = set(self.ref_adoption_use_pds_years) & set(self.pds_adoption_use_ref_years)
        if intersect:
            err = ("cannot be in both ref_adoption_use_pds_years and pds_adoption_use_ref_years:"
                    + str(intersect))
            raise ValueError(err)

    @property
    def yield_coeff(self):
        """ Returns coeffecient that converts funits to yield for LAND solutions """
        return self.yield_from_conv_practice * self.yield_gain_from_conv_to_soln * (
            1 - self.disturbance_rate)

    @property
    def has_var_costs(self):
        """
        Returns Boolean to check if variable costs exist (LAND models don't have any).
        All variable costs must be not None for this to return True.
        """
        return None not in (self.conv_var_oper_cost_per_funit,
                            self.conv_fuel_cost_per_funit,
                            self.soln_var_oper_cost_per_funit,
                            self.soln_fuel_cost_per_funit)

    @property
    def soln_first_cost_learning_rate(self):
        return 1.0 - self.soln_first_cost_efficiency_rate

    @property
    def conv_first_cost_learning_rate(self):
        return 1.0 - self.conv_first_cost_efficiency_rate

    @property
    def soln_fuel_learning_rate(self):
        return 1.0 - self.soln_fuel_efficiency_factor

    @property
    def soln_lifetime_replacement(self):
        if self.soln_lifetime_capacity is not None:  # RRS
            return self.soln_lifetime_capacity / self.soln_avg_annual_use
        elif self.soln_expected_lifetime is not None:  # LAND
            return self.soln_expected_lifetime
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for solution')

    @property
    def soln_lifetime_replacement_rounded(self):
        if self.soln_lifetime_capacity is not None:  # RRS
            # ROUND and decimal.quantize do not match Excel ROUND(), so we implemented one.
            return excel_math.round_away(self.soln_lifetime_capacity / self.soln_avg_annual_use)
        elif self.soln_expected_lifetime is not None:  # LAND
            # LAND models input lifetime directly so I doubt we will come across rounding errors
            # i.e. expected_lifetime will probably be a whole number of years.
            # Integration test will catch the case where this assumption is wrong
            return int(self.soln_expected_lifetime)
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for solution')

    @property
    def conv_lifetime_replacement(self):
        if self.conv_lifetime_capacity is not None:  # RRS
            return self.conv_lifetime_capacity / self.conv_avg_annual_use
        elif self.conv_expected_lifetime is not None:  # LAND
            return self.conv_expected_lifetime
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for conventional')

    @property
    def conv_lifetime_replacement_rounded(self):
        if self.conv_lifetime_capacity is not None:  # RRS
            # ROUND and decimal.quantize do not match Excel ROUND(), so we implemented one.
            return excel_math.round_away(self.conv_lifetime_capacity / self.conv_avg_annual_use)
        elif self.conv_expected_lifetime is not None:  # LAND
            # LAND models input lifetime directly so I doubt we will come across rounding errors
            # i.e. expected_lifetime will probably be a whole number of years
            # Integration test will catch the case where this assumption is wrong
            return int(self.conv_expected_lifetime)
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for conventional')


    def _substitute_vma(self, val, vma_titles):
        """
        If val is 'mean', 'high' or 'low', returns the corresponding statistic from the VMA object in
        self.vmas with the corresponding title.
        If val is 'mean per region', 'high per region' or 'low per region', returns a Series of regions and
        corresponding stats. Note that 'World' region will be NaN, as these will be calculated by summing the main
        regions throughout the model.
        Args:
          val: input can be:
                - a number
                - a string ('mean', 'high' or 'low') or ('mean per region', 'high per region' or 'low per region')
                - a dict containing a 'value' key
          vma_titles: list of titles of VMA tables to check. The first one which exists
            will be used.
        """
        raw_val_from_excel = None  # the raw value from the scenario record tab
        return_regional_series = False
        if isinstance(val, str):
            if val.endswith('per region'):
                stat = val.split()[0]
                return_regional_series = True
            else:
                stat = val
        elif isinstance(val, dict):
            if 'statistic' not in val:  # if there is no statistic to link we return the value
                return val['value']
            raw_val_from_excel = val['value']
            stat = val['statistic']
            if not stat:
                return val['value']
        else:
            return val

        for vma_title in vma_titles:
            v = self.vmas.get(vma_title, None)
            if v and not pd.isna(v.avg_high_low(key='mean')):
                break
        else:
            raise KeyError(f'"{vma_titles}" must be included in vmas to calculate mean/high/low.'
                    f'vmas included: {self.vmas.keys()}')

        if return_regional_series:
            result = pd.Series(name='regional values')
            for reg in REGIONS:
                result[reg] = self.vmas[vma_title].avg_high_low(key=stat.lower(), region=reg)
        else:
            result = self.vmas[vma_title].avg_high_low(key=stat.lower())
        if raw_val_from_excel is not None and result != pytest.approx(raw_val_from_excel):
            # pylint: disable=no-member
            self.incorrect_cached_values[vma_title] = (raw_val_from_excel, result)
            result = raw_val_from_excel
        return result

    def _hash_item(self, item):
        if isinstance(item, pd.DataFrame) or isinstance(item, pd.Series):
            item = tuple(pd.util.hash_pandas_object(item))
        try:
            return hash(item)
        except TypeError:
            pass
        try:
            return hash(tuple(item))
        except TypeError as e:
            raise e

    def __hash__(self):
        key = 0x811c9dc5
        key = key ^ id(self)
        for field in dataclasses.fields(self):
            key = key ^ self._hash_item(field)
        return key

    def write_to_json_file(self):
        jsfilenew = self.jsfile + '.new'
        d = dataclasses.asdict(self)
        for rem in ['vmas', 'js', 'jsfile']:
            del d[rem]
        with open(jsfilenew, 'w') as f:
            json.dump(d, f)
            os.replace(jsfilenew, self.jsfile)


def fill_missing_regions_from_world(data):
    """
    AdvancedControls attributes linked to VMAs can optionally be Series of regional values rather than
    single floats. Some calculations in the model require all main regions (not special countries) to have
    values (i.e. not NaN); this function can be used to substitute any missing main regional values
    with the 'World' value, which is calculated as a weighted average of the available regional data by the
    VMA class.
    Note that in most cases it is better practice to input values for all main regions into the VMA table
    if regional data is to be considered for the solution.
    Args:
        data: A Series object with REGIONS as index or float

    Returns: the processed Series object or passes through float
    """
    if isinstance(data, pd.Series):
        filled_data = data.copy(deep=True)
        filled_data.loc[MAIN_REGIONS] = filled_data[MAIN_REGIONS].fillna(data['World'])
        return filled_data
    else:
        return data


def load_scenarios_from_json(directory, vmas):
    """Load scenarios from JSON files in directory."""
    result = {}
    for filename in glob.glob(str(directory.joinpath('*.json'))):
        with open(filename, 'r') as fid:
            j = json.loads(fid.read())
            js = j.copy()
            js['vmas'] = vmas
            js['js'] = j
            js['jsfile'] = str(filename)
            a = AdvancedControls(**js)
            result[a.name] = a
    return result

def get_vma_for_param(param):
    for field in dataclasses.fields(AdvancedControls):
        if field.name == param:
            return field.metadata.get('vma_titles', [])
    return []

def get_param_for_vma_name(name):
    for field in dataclasses.fields(AdvancedControls):
        for vma_name in field.metadata.get('vma_titles', []):
            if name == vma_name:
                return field.name
    return None

def solution_category_to_string(cat):
    if cat == SOLUTION_CATEGORY.REPLACEMENT:
        return 'replacement'
    elif cat == SOLUTION_CATEGORY.REDUCTION:
        return 'reduction'
    elif cat == SOLUTION_CATEGORY.LAND:
        return 'land'
    elif SOLUTION_CATEGORY.NOT_APPLICABLE:
        return 'not_applicable'

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
