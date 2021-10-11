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
    report_start_year: int = parameterField(default=2014,
        title="Report Start Year", isglobal=True,
        docstring="First year of results to report")
 
    report_end_year: int = parameterField(default=2050,
        title="Report End Year", isglobal=True,
        docstring="Last year of results to report")

    population_model: str = parameterField(default="current",
        title="Population Model", isglobal=True,
        docstring="Name of population model to use; 'current' means use the latest model", )

    npv_discount_rate: float = parameterField(
        title="Net Present Value Discount Rate", isglobal=True
    )

    emissions_use_co2eq: bool = parameterField(default=True,
        title="Use CO2-equivalence for Emissions Calculations", isglobal=True,
        units="True/False"
    )

    emissions_grid_source: str = parameterField(default="current",
        title="Grid Emissions Model", isglobal=True,
        docstring="""Name of the data source to use for grid emissions data.  Options are 'IPCC Only' for IPCC data, or 'Meta-n', to
        use the nth PD Meta-analysis.  The value 'current' means use the latest PD Meta-analysis."""
    )

    emissions_grid_range: str = parameterField(default="mean",
        title="Select Low/Mean/High Grid Emissions Estimate", isglobal=True,
        docstring="Value low, mean or high to select the corresponding estimate from the grid emissions range."       
    )

    
    # co2eq_conversion_source: One of the conversion_source names
    #   defined in model/emissions_factors.py like "AR5 with feedback" or "AR4"
    #   SolarPVUtil "Advanced Controls"!I185
    co2eq_conversion_source: str = None

    # ##########################################################################################
    # 
    # "Constant" Fields
    # These fields aren't used in practice and shoult probably be removed.
    # Putting our thumb on the scale by making them Globals with Defaults for now.  

    # ch4_is_co2eq: True if CH4 emissions measurement is in terms of CO2
    #   equivalent, False if measurement is in units of CH4 mass.
    #   derived from SolarPVUtil "Advanced Controls"!I184
    ch4_is_co2eq: bool = parameterField(isglobal=True, default=False)

    # n2o_is_co2eq: True if N2O emissions measurement is in terms of CO2
    #   equivalent, False if measurement is in units of N2O mass.
    #   derived from SolarPVUtil "Advanced Controls"!J184
    n2o_is_co2eq: bool = parameterField(isglobal=True, default=False)

    # conv_indirect_co2_is_iunits: whether conv_indirect_co2_per_unit is
    #   iunits (True) or funits (False).  SolarPVUtil "Advanced Controls"!F184
    conv_indirect_co2_is_iunits: bool = parameterField(isglobal=True, default=True)


    # ##########################################################################################
    # 
    # Solution- and scenario-specific fields
    

    # ##########################################################################################
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
        title='CONVENTIONAL First Cost Learning Rate',
        units= '%',
        docstring= """Percentage by which the First Cost declines per CONVENTIONAL implementation unit, as technology matures.
        With already mature echnologies, this number should be zero.""",
        excelref= 'SolarPVUtil "Advanced Controls"!C95')


    soln_first_cost_below_conv: bool = parameterField(default=False,
        title='Allow SOLUTION First Cost to go below CONVENTIONAL',
        units= 'True/False',
        docstring= """The Solution First Cost may decline below that of the Conventional due to the learning rate chosen. 
        This may be acceptable in some cases for instance when the projections in the literature indicate so. In other cases, 
        it may not be likely for the Solution to become cheaper than the Conventional.""",
        excelref= 'SolarPVUtil "Advanced Controls"!C132',
        )

    # ##########################################################################################    
    # Solution Emissions Information (typically varies per-solution, not per-scenario)

    soln_energy_efficiency_factor: float = parameterField(default=0.0, 
        title='SOLUTION Energy Efficiency Factor',
        units= '%',
        docstring= (
            "soln_energy_efficiency_factor: Units of energy reduced per year per "
            "functional unit installed."

            "FOR CLEAN RENEWABLE ENERGY SOLUTIONS: enter 0 (e.g. implementing solar PV "
            "fully replaces existing fossil fuel-based generation, but does not reduce "
            "the amount of energy generated)"

            "FOR ENERGY EFFICIENCY SOLUTIONS: enter positive number representing total "
            "energy reduced, 0 < X < 1 (e.g. HVAC efficiencies reduce the average annual "
            "energy consumption of buildings, by square meters of floor space; they still "
            "use the electric grid, but significantly less)"
            ),
        excelref= 'SolarPVUtil "Advanced Controls"!C159; Silvopasture "Advanced Controls"!C123',
        )

    conv_annual_energy_used: float = parameterField(default=0.0, 
        title='CONVENTIONAL Total Energy Used per Functional Unit',
        units= 'TWh per Functional Unit per Year',
        docstring= (
            "for solutions that reduce electricity consumption per functional unit, "
            "enter the average electricity used per functional unit of the conventional "
            "technologies/practices."),
        excelref= 'SolarPVUtil "Advanced Controls"!B159; Silvopasture "Advanced Controls"!B123',
        )

    soln_annual_energy_used: float = parameterField(default=0.0, 
        title='SOLUTION Total Energy Used per Functional Unit',
        units= 'TWh per Functional Unit per Year',
        docstring= (
            "This refers to the units of average energy used per year per functional unit "
            "installed."
            "This is an optional variable to be used in cases where a) the literature "
            "reports the energy use of the solution rather than energy efficiency; or "
            "b) the solution uses more electricity than the conventional "
            "technologies/practices."
            "E.g. electric vehicles use energy from the electric grid, whereas "
            "conventional vehicles use only fuel"),
        excelref= 'SolarPVUtil "Advanced Controls"!D159',
        )

    conv_fuel_consumed_per_funit: float = parameterField(default=0.0, 
        title='CONVENTIONAL Fuel Consumed per Functional Unit',
        units= 'Liters per Functional Unit per Year',
        excelref= 'SolarPVUtil "Advanced Controls"!F159; Silvopasture "Advanced Controls"!F123',
        )

    soln_fuel_efficiency_factor: float = parameterField(default=0.0, 
        title='SOLUTION Fuel Efficiency Factor',
        units= '%',
        docstring= (
            "This refers to the % fuel reduced by the SOLUTION relative to the "
            "CONVENTIONAL mix of technologies/practices. The Percent reduction is "
            "assumed to apply to the Conventional Fuel Unit, if different to the "
            "Solution Fuel Unit."

            "FOR REPLACEMENT SOLUTIONS: enter 1 (e.g. electric vehicles fully replace fuel "
            "consumption with electricity use -- but be sure to add a negative value for "
            "Annual Energy Reduced from Electric Grid Mix!)"

            "FOR FUEL EFFICIENCY SOLUTIONS: enter positive number representing total fuel "
            "reduced, 0 < X < 1  (e.g. hybrid-electric vehicles partially replace fuel "
            "consumption with electricity use, it thus uses less fuel compared to conventional "
            "vehicles)"

            "FOR SOLUTIONS THAT CONSUME MORE FUEL THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE: "
            "enter negative number representing total additional fuel used, X < 0 (e.g. we "
            "hope solutions do not actually consume more fuel than the conventional practice, "
            "check with the senior research team if you run into this)"),
        excelref= 'SolarPVUtil "Advanced Controls"!G159; Silvopasture "Advanced Controls"!G123',
        )

    conv_fuel_emissions_factor: float = parameterField(default=0.0, 
        title='CONVENTIONAL Direct Fuel Emissions per Functional Unit',
        units= 'Tons CO2-eq per Functional Unit per Year',
        excelref= 'SolarPVUtil "Advanced Controls"!I159',
        )

    soln_fuel_emissions_factor: float = parameterField(default=0.0, 
        title='SOLUTION Direct Fuel Emissions per Functional Unit',
        units= 'Tons CO2-eq per Functional Unit per Year',
        excelref= 'SolarPVUtil "Advanced Controls"!I163; DistrictHeating "Advanced Controls"!I144',
        )

    conv_emissions_per_funit: float = parameterField(default=0.0, 
        title='CONVENTIONAL Direct Emissions per Functional Unit',
        units= 'Tons CO2-eq per Functional Unit per Year',
        docstring= (
            "The direct CO2-eq emissions that result per functional unit "
            "that are not accounted for by use of the electric grid or fuel consumption."),
        excelref= 'SolarPVUtil "Advanced Controls"!C174',
        )

    soln_emissions_per_funit: float = parameterField(default=0.0, 
        title='SOLUTION Direct Emissions per Functional Unit',
        units= 'Tons CO2-eq per Functional Unit per Year',
        docstring= (
            "The direct CO2-eq emissions that result per functional unit "
            "that are not accounted for by use of the electric grid or fuel consumption."),
        excelref= 'SolarPVUtil "Advanced Controls"!D174',
        )

    ch4_co2_per_funit: float = parameterField(default=0.0, 
        title='CH4-CO2eq Tons Reduced',
        units= 'Tons CO2-eq per Functional Unit per Year',
        docstring= (
            "CO2-equivalent of the CH4 emitted per functional unit, in tons/year."),
        excelref= 'SolarPVUtil "Advanced Controls"!I174',
        )

    n2o_co2_per_funit: float = parameterField(default=0.0, 
        title='N2O-CO2eq Tons Reduced',
        units= 'Tons CO2-eq per Functional Unit per Year',
        docstring= (
            "CO2-equivalent of the N2O emitted per functional unit, in tons/year."),
        excelref= 'SolarPVUtil "Advanced Controls"!J174',
        )

    soln_indirect_co2_per_iunit: float = parameterField(
        title='SOLUTION Indirect CO2 Emissions per Implementation Unit',
        units= 'Tons CO2-eq per Unit',
        docstring= (            
            "The indirect CO2 emissions that result per implementation "
            "unit installed. The production, distribution, and installation of "
            "technologies/practices often generate their own emissions that are not associated "
            "with their function."

            "E.g. the production of vehicles is an energy- and resource-intensive endeavor "
            "that generates indirect emissions that must be accounted for."),
        excelref= 'SolarPVUtil "Advanced Controls"!G174',
        )

    conv_indirect_co2_per_unit: float = parameterField( 
        title='CONVENTIONAL Indirect CO2 Emissions per Implementation Unit',
        units= 'Tons CO2-eq per Implementation Unit',
        docstring= (
            "The indirect CO2 emissions that result per implementation "
            "unit installed. The production, distribution, and installation of "
            "technologies/practices often generate their own emissions that are not associated "
            "with their function."

            "E.g. the production of vehicles is an energy- and resource-intensive endeavor "
            "that generates indirect emissions that must be accounted for."),
        excelref= 'SolarPVUtil "Advanced Controls"!F174',
        )

# ====> HERE

    soln_lifetime_capacity: float = parameterField( 
        title='SOLUTION Lifetime Capacity',
        units= '(use until replacement is required)',
        docstring= ("Lifetime Capacity - SOLUTION"
            "This is the average expected number of functional units generated by the "
            "SOLUTION throughout their lifetime before replacement is required. If no replacement "
            "time is discovered or applicable the fellow will default to 100 years."
            "E.g. an electric vehicle will have an average number of passenger kilometers it "
            "can travel until it can no longer be used and a new vehicle is required. Another "
            "example would be an efficient HVAC system, which can only service a certain amount "
            "of floor space over a period of time before it will require replacement."),
        excelref= 'SolarPVUtil "Advanced Controls"!E128',
        )

    soln_avg_annual_use: float = parameterField( 
        title='SOLUTION Average Annual Use',
        units= '(annual use)',
        docstring= ("Average Annual Use - SOLUTION"
            " Average Annual Use is the average annual use of the technology/practice, "
            "in functional units per implementation unit. This will likely differ significantly "
            "based on location, be sure to note which region the data is coming from. If data "
            "varies substantially by region, a weighted average may need to be used."
            "E.g. the average annual number of passenger kilometers (pkm) traveled per "
            "electric vehicle."),
        excelref= 'SolarPVUtil "Advanced Controls"!F128',
        )

    conv_lifetime_capacity: float = parameterField( 
        title='CONVENTIONAL Lifetime Capacity',
        units= '(use until replacement is required)',
        docstring= ("Lifetime Capacity - CONVENTIONAL"
            "This is the average expected number of functional units "
            "generated by the CONVENTIONAL mix of technologies/practices "
            "throughout their lifetime before replacement is required.  "
            "If no replacement time is discovered or applicable, please "
            "use 100 years."
            "E.g. a vehicle will have an average number of passenger kilometers "
            "it can travel until it can no longer be used and a new vehicle is "
            "required. Another example would be an HVAC system, which can only "
            "service a certain amount of floor space over a period of time before "
            "it will require replacement."),
        excelref= 'SolarPVUtil "Advanced Controls"!E95',
        )

    conv_avg_annual_use: float = parameterField( 
        title='CONVENTIONAL Average Annual Use',
        units= '(annual use)',
        docstring= ("Average Annual Use - CONVENTIONAL"
            " Average Annual Use is the average annual use of the technology/practice, "
            "in functional units per implementation unit. This will likely differ significantly "
            "based on location, be sure to note which region the data is coming from. If data "
            "varies substantially by region, a weighted average may need to be used."
            "E.g. the average annual number of passenger kilometers (pkm) traveled per "
            "conventional vehicle."),
        excelref= 'SolarPVUtil "Advanced Controls"!F95',
        )


    soln_var_oper_cost_per_funit: float = parameterField( 
        title='SOLUTION Variable Operating Cost (VOM) per Functional Unit',
        units= '(functional units)',
        docstring= ("SOLUTION Variable Operating Cost (VOM)"
            "This is the annual operating cost per functional unit, derived from the "
            "SOLUTION. In most cases this will be expressed as a cost per 'some unit of "
            "energy'."
            "E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this "
            "can be considered the weighted average price of fuel per passenger kilometer."),
        excelref= 'SolarPVUtil "Advanced Controls"!H128',
        )

    soln_fixed_oper_cost_per_iunit: typing.Any = parameterField( 
        title='SOLUTION Fixed Operating Cost (FOM)',
        units= '(per ha per annum)',
        docstring= ("SOLUTION Operating Cost per Functional Unit per Annum"
            "This is the Operating Cost per functional unit, derived from the "
            "SOLUTION. In most cases this will be expressed as a cost per 'hectare of "
            "land'."
            "This annualized value should capture both the variable costs for maintaining "
            "the SOLUTION practice as well as the fixed costs. The value should reflect "
            "the average over the reasonable lifetime of the practice."),
        # That tooltip is phrased for land solutions, one for RRS would be:
        # 'tooltipFIXME': ("SOLUTION Operating Cost per Functional Unit per Annum"
        #     "This is the annual operating cost per implementation unit, derived from "
        #     "the SOLUTION.  In most cases this will be expressed as a cost per 'some unit of "
        #     "installation size' E.g., $10,000 per kw. In terms of transportation, this can be "
        #     "considered the total insurance, and maintenance cost per car."
        # "Purchase costs can be amortized here or included as a first cost, but not both."),
        excelref= 'SolarPVUtil "Advanced Controls"!I128; Silvopasture "Advanced Controls"!C92',
        )



    # conv_fuel_cost_per_funit: as soln_fuel_cost_per_funit.
    #   SolarPVUtil "Advanced Controls"!K95
    conv_fuel_cost_per_funit: float = None

    # soln_fuel_cost_per_funit: Fuel/consumable cost per functional unit.
    #   SolarPVUtil "Advanced Controls"!K128
    soln_fuel_cost_per_funit: float = None

    conv_var_oper_cost_per_funit: float = parameterField( 
        title='CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit',
        units= '(functional units)',
        docstring= ("CONVENTIONAL Variable Operating Cost (VOM)"
            "This is the annual operating cost per functional unit, derived from the "
            "CONVENTIONAL mix of technologies. In most cases this will be expressed as a "
            "cost per 'some unit of energy'."
            "E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this "
            "can be considered the weighted average price of fuel per passenger kilometer."),
        excelref= 'SolarPVUtil "Advanced Controls"!H95',
        )

    # conv_fixed_oper_cost_per_iunit: as soln_fixed_oper_cost_per_funit.
    #   SolarPVUtil "Advanced Controls"!I95 / Silvopasture "Advanced Controls"!C77
    conv_fixed_oper_cost_per_iunit: typing.Any = parameterField( 
        title='CONVENTIONAL Fixed Operating Cost (FOM)',
        units= '(per ha per annum)',
        docstring= ("CONVENTIONAL Operating Cost per Functional Unit per Annum"
            "This is the Operating Cost per functional unit, derived "
            "from the CONVENTIONAL mix of technologies/practices.  In most "
            "cases this will be expressed as a cost per 'hectare of land'."
            "This annualized value should capture the variable costs for "
            "maintaining the CONVENTIONAL practice, as well as  fixed costs. "
            "The value should reflect the average over the reasonable lifetime "
            "of the practice."),
        excelref= 'SolarPVUtil "Advanced Controls"!I95; Silvopasture "Advanced Controls"!C77',
        )



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

    # soln_pds_adoption_scenarios_included: the list of adoption scenarios to include in
    # the fully customized adoption for this scenario.
    # "Custom PDS Adoption"!S25:S34, as captured in ScenarioRecord row+260 E
    soln_pds_adoption_scenarios_included: list[int] = None

    # soln_pds_adoption_custom_high_sd_mult & soln_pds_adoption_custom_low_sd_mult: multiples of
    #   one standard deviation to use when soln_pds_adoption_custom_name is "High of All Custom
    #   Scenarios" or "Low of All Custom Scenarios"
    soln_pds_adoption_custom_high_sd_mult: float = 1.0
    soln_pds_adoption_custom_low_sd_mult: float = 1.0

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
    ref_adoption_use_pds_years: typing.List[int] = parameterField(default_factory=list)
    pds_adoption_use_ref_years: typing.List[int] = parameterField(default_factory=list)

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
    tco2eq_reduced_per_land_unit: typing.Any = parameterField( 
        title='t CO2-eq (Aggregate emissions) Reduced per Land Unit',
        units= '(t CO2-eq / ha)',
        docstring= ("t CO2-eq (Aggregate emissions) Reduced per Land Unit"
            "This is the CO2-equivalent reduced per land unit (million Hectare)."),
        excelref= 'ForestProtection "Advanced Controls"!B138',
        )

    # tco2eq_rplu_rate: whether tco2eq_reduced_per_land_unit is 'One-time' or 'Annual'
    #    ForestProtection "Advanced Controls"!B148 (Land models)
    tco2eq_rplu_rate: str = None
    tco2_rplu_rate: str = None
    tn2o_co2_rplu_rate: str = None
    tch4_co2_rplu_rate: str = None

    tco2_reduced_per_land_unit: typing.Any = parameterField( 
        title='t CO2 Reduced per Land Unit',
        units= '(t CO2 / ha)',
        docstring= ("t CO2 Reduced per Land Unit"
            "This is the CO2 reduced per land unit (million Hectare)."),
        excelref= 'ForestProtection "Advanced Controls"!C148',
        )

    tn2o_co2_reduced_per_land_unit: typing.Any = parameterField( 
        title='t N2O-CO2-eq Reduced per Land Unit',
        units= '(t N2O-CO2-eq / ha)',
        docstring= ("t N2O-CO2-eq Reduced per Land Unit"
            "This is the N2O reduced per land unit (million Hectare) but converted "
            "to CO2-eq."),
        excelref= 'ForestProtection "Advanced Controls"!D148',
        )

    tch4_co2_reduced_per_land_unit: typing.Any = parameterField( 
        title='t CH4-CO2-eq Reduced per Land Unit',
        units= '',
        docstring= ("t CH4-CO2-eq Reduced per Land Unit"
            "This is the CH4 reduced per land unit (million Hectare) but "
            "converted to CO2-eq."),
        excelref= 'ForestProtection "Advanced Controls"!E148',
        )

    # emissions_use_agg_co2eq: Use Aggregate CO2-eq instead of Individual GHG for direct emissions
    #  ForestProtection "Advanced Controls"!C155 (Land models)
    emissions_use_agg_co2eq: bool = None

    # seq_rate_global: carbon sequestration rate for All Land or All of Special Land.
    #  Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #  "Advanced Controls"!B173 (Land models)
    seq_rate_global: typing.Any = parameterField( 
        title='Sequestration Rates',
        units= '(t C / ha /year)',
        docstring= ("Sequestration Rate for All Land or All of Special Land"
            "Once a  Rate is entered here, it would be used. If rates are available for "
            "each Thermal-Humidity Regime, leave this blank."),
        excelref='"Advanced Controls"!B173 (Land models)',
        )

    #seq_rate_per_regime (dict of float): carbon sequestration rate for each thermal-moisture
    #  regime. "Advanced Controls"!C173:G173 (Land models)
    seq_rate_per_regime: typing.Dict = None

    degradation_rate: typing.Any = parameterField( 
        title='Growth Rate of Land Degradation',
        units= '',
        docstring= ("Growth Rate of Land Degradation"
            'This is the rate of degradation of unprotected land (or "At Risk" land '
            "that is neither protected nor already degraded. This number should exclude the "
            "Disturbance Rate if that is also entered."),
        excelref= 'ForestProtection "Advanced Controls"!B187',
        )

    disturbance_rate: typing.Any = parameterField( 
        title='Disturbance Rate',
        units= '',
        docstring= ("Disturbance Rate"
            "This is the annual percent of some output that fails for some reason "
            "(possibly due to weather, human activities, etc). It applies ONLY to land "
            "adopted/protected with the SOLUTION, and affects degraded land, direct emissions, "
            "sequestration and  yield. The SOLUTION adoption remains unaffected."
            "Ensure that the Growth Rate of Land degradation does not already account for "
            "the Disturbance Rate if it is entered here."),
        excelref= 'TropicalForests. "Advanced Controls"!I173',
        )

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
    yield_from_conv_practice: typing.Any = parameterField( 
        title='Yield from CONVENTIONAL Practice',
        units= '(kg / ha /yr)',
        docstring= ("Yield from CONVENTIONAL Practice"),
        excelref= '"Advanced Controls"!G77 (Land models)',
        )

    # yield_gain_from_conv_to_soln: yield % increase from conventional to solution.
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   "Advanced Controls"!G92 (Land models)
    yield_gain_from_conv_to_soln: typing.Any = parameterField( 
        title='Yield Gain (% Increase from CONVENTIONAL to SOLUTION)',
        units= '%',
        docstring= ("Yield Gain (% Increase from CONVENTIONAL to SOLUTION)"),
        excelref= '"Advanced Controls"!G92 (Land models)',
        )

    # use_custom_tla: whether to use custom TLA data instead of Drawdown land allocation
    #   "Advanced Controls"!E54 (Land models)
    use_custom_tla: bool = None

    # a fixed value to set in all elements of a custom TLA, instead of loading from CSV.
    custom_tla_fixed_value: float = None

    # harvest_frequency: new growth is harvested/cleared every ... (years)
    #   Afforestation "Advanced Controls"!B187
    harvest_frequency: float = None

    carbon_not_emitted_after_harvesting: typing.Any = parameterField( 
        title='Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing',
        units= '(t C/ha)',
        docstring= ("Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing"),
        excelref= 'Afforestation "Advanced Controls"!H173',
        )

    # avoided_deforest_with_intensification: Factor for avoiding deforestation by more
    #   intensively using the land. Women Smallholders "Advanced Controls"!E205
    avoided_deforest_with_intensification: typing.Any = parameterField( 
        title='Avoided Deforested Area With Increase in Agricultural Intensification',
        units= '',
        docstring= ("Avoided Deforested Area With Increase in Agricultural Intensification"),
        excelref= 'Women Smallholders "Advanced Controls"!E205',
        )

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
    tC_storage_in_protected_land_type: typing.Any = parameterField( 
        title='t C storage in Protected Landtype',
        units= '',
        docstring= ("t C storage in Protected Landtype"),
        excelref= '',
        )
    
    # NEW ADDITIONS
    # These do not represent quantities that were part of the original spreadsheets, but are used in 
    # for communication from external sources

    # Value is a URI that will return a csv for a custom source to use in place of the REF TAM,
    # overriding whatever else is defined for this solution/scenario
    ref_tam_custom_source: str = None

    # Value is a URI that will return a csv for a custom source to use in place of the PDS TAM,
    # overriding whatever else is defined for this solution/scenario
    pds_tam_custom_source: str = None

    # Value is a URI that will return a csv for a custom source to use in place of the REF Adoption (as a Fully Custom Adoption),
    # overriding whatever else is defined for this solution/scenario
    ref_adoption_custom_source: str = None

    # Value is a URI that will return a csv for a custom source to use in place of the PDS Adoption (as a Fully Custom Adoption),
    # overriding whatever else is defined for this solution/scenario   
    pds_adoption_custom_source: str = None



    # #########################################################################################
    #
    # Computed Fields
    #

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
            if self.soln_avg_annual_use != 0:
                return self.soln_lifetime_capacity / self.soln_avg_annual_use
            else:
                return self.soln_lifetime_capacity
        elif self.soln_expected_lifetime is not None:  # LAND
            return self.soln_expected_lifetime
        else:
            raise ValueError('Must input either lifetime capacity (RRS) or ' +
                             'expected lifetime (LAND) for solution')

    @property
    def soln_lifetime_replacement_rounded(self):
        if self.soln_lifetime_capacity is not None:  # RRS
            if self.soln_avg_annual_use != 0:
                # ROUND and decimal.quantize do not match Excel ROUND(), so we implemented one.
                return excel_math.round_away(self.soln_lifetime_capacity / self.soln_avg_annual_use)
            else:
                return excel_math.round_away(self.soln_lifetime_capacity)
        elif self.soln_expected_lifetime is not None:  # LAND
            # LAND models input lifetime directly so I doubt we will come across rounding errors
            # i.e. expected_lifetime will probably be a whole number of years.
            # Integration test will catch the case where this assumption is wrong
            return int(self.soln_expected_lifetime)
        else:
            raise ValueError('Must input either lifetime capacity (RRS) or ' +
                             'expected lifetime (LAND) for solution')

    @property
    def conv_lifetime_replacement(self):
        if self.conv_lifetime_capacity is not None:  # RRS
            if self.conv_avg_annual_use != 0:
                return self.conv_lifetime_capacity / self.conv_avg_annual_use
            else:
                return self.conv_lifetime_capacity
        elif self.conv_expected_lifetime is not None:  # LAND
            return self.conv_expected_lifetime
        else:
            raise ValueError('Must input either lifetime capacity (RRS) or ' +
                             'expected lifetime (LAND) for conventional')

    @property
    def conv_lifetime_replacement_rounded(self):
        if self.conv_lifetime_capacity is not None:  # RRS
            if self.conv_avg_annual_use != 0:
                # ROUND and decimal.quantize do not match Excel ROUND(), so we implemented one.
                return excel_math.round_away(self.conv_lifetime_capacity / self.conv_avg_annual_use)
            else:
                return excel_math.round_away(self.conv_lifetime_capacity)
        elif self.conv_expected_lifetime is not None:  # LAND
            # LAND models input lifetime directly so I doubt we will come across rounding errors
            # i.e. expected_lifetime will probably be a whole number of years
            # Integration test will catch the case where this assumption is wrong
            return int(self.conv_expected_lifetime)
        else:
            raise ValueError('Must input either lifetime capacity (RRS) or ' +
                             'expected lifetime (LAND) for conventional')

