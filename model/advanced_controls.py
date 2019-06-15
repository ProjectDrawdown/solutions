"""Implements the Advanced Controls, settings which have a default
   but can be overridden to fit particular needs.
"""

import dataclasses
import enum
import json
import typing

import pandas as pd
from pytest import approx
from warnings import warn
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


def from_json(filename):
    j = json.load(open(filename))
    return AdvancedControls(**j)


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

    # pds_2014_cost: US$2014 cost to acquire + install, per implementation
    #   unit (ex: kW for energy scenarios), for the Project Drawdown
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   Solution (PDS).  SolarPVUtil "Advanced Controls"!B128
    # ref_2014_cost: US$2014 cost to acquire + install, per implementation
    #   unit, for the reference technology.
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   SolarPVUtil "Advanced Controls"!B128 (same as PDS)
    # conv_2014_cost: US$2014 cost to acquire + install, per implementation
    #   unit, for the conventional technology.
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   SolarPVUtil "Advanced Controls"!B95
    pds_2014_cost: typing.Any = None
    ref_2014_cost: typing.Any = None
    conv_2014_cost: typing.Any = None

    # soln_first_cost_efficiency_rate: rate that the modelled solution improves /
    #   lowers in cost per year. In calculations this is usually converted
    #   to the learning rate, which is 1/efficiency_rate.
    #   SolarPVUtil "Advanced Controls"!C128
    # conv_first_cost_efficiency_rate: rate that the conventional technology
    #   improves / lowers in cost each year. Efficiency rates for the
    #   conventional technology are typically close to zero, these technologies
    #   have already had many years of development and maturation.
    #   In calculations this is usually converted to the learning rate,
    #   which is 1/efficiency_rate.  SolarPVUtil "Advanced Controls"!C95
    # soln_first_cost_below_conv: The solution first cost may decline
    #   below that of the Conventional due to the learning rate chosen. This may
    #   be acceptable in some cases for instance when the projections in the
    #   literature indicate so. In other cases, it may not be likely for the
    #   Solution to become cheaper than the Conventional.
    #   SolarPVUtil "Advanced Controls"!C132
    soln_first_cost_efficiency_rate: float = None
    conv_first_cost_efficiency_rate: float = None
    soln_first_cost_below_conv: bool = None

    # soln_energy_efficiency_factor: Units of energy reduced per year per
    #   functional unit installed.
    #
    #   FOR CLEAN RENEWABLE ENERGY SOLUTIONS: enter 0 (e.g. implementing solar PV
    #   fully replaces existing fossil fuel-based generation, but does not reduce
    #   the amount of energy generated)
    #
    #   FOR ENERGY EFFICIENCY SOLUTIONS: enter positive number representing total
    #   energy reduced, 0 < X < 1 (e.g. HVAC efficiencies reduce the average annual
    #   energy consumption of buildings, by square meters of floor space; they still
    #   use the electric grid, but significantly less)
    #
    #   FOR SOLUTIONS THAT CONSUME MORE ENERGY THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:
    #   Use the next input, Total Annual Energy Used SOLUTION (e.g. electric vehicles
    #   use energy from the electric grid, whereas conventional vehicles use only fuel)
    #   SolarPVUtil "Advanced Controls"!C159
    soln_energy_efficiency_factor: float = None

    # conv_annual_energy_used: for solutions that reduce electricity
    #   consumption per functional unit, enter the average electricity used per
    #   functional unit of the conventional technologies/practices.
    #   SolarPVUtil "Advanced Controls"!B159
    # soln_annual_energy_used: This refers to the units of average energy
    #   used per year per functional unit installed.
    #
    #   This is an optional variable to be used in cases where a) the literature
    #   reports the energy use of the solution rather than energy efficiency; or
    #   b) the solution uses more electricity than the conventional
    #   technologies/practices.
    #
    #   E.g. electric vehicles use energy from the electric grid, whereas
    #   conventional vehicles use only fuel)
    #   SolarPVUtil "Advanced Controls"!D159
    conv_annual_energy_used: float = None
    soln_annual_energy_used: float = None

    # conv_fuel_consumed_per_funit: This refers to the unit (default is Liters)
    #   of FUEL used per year per cumulative unit installed. The equation may need to
    #   be edited if your energy savings depend on the marginal unit installed rather
    #   than the cumulative units. SolarPVUtil "Advanced Controls"!F159
    # soln_fuel_efficiency_factor: This refers to the % fuel reduced by the
    #   SOLUTION relative to the CONVENTIONAL mix of technologies/practices. The
    #   Percent reduction is assumed to apply to the Conventional Fuel Unit, if
    #   different to the Solution Fuel Unit.
    #
    #   FOR REPLACEMENT SOLUTIONS: enter 1 (e.g. electric vehicles fully replace fuel
    #   consumption with electricity use -- but be sure to add a negative value for
    #   Annual Energy Reduced from Electric Grid Mix!)
    #
    #   FOR FUEL EFFICIENCY SOLUTIONS: enter positive number representing total fuel
    #   reduced, 0 < X < 1  (e.g. hybrid-electric vehicles partially replace fuel
    #   consumption with electricity use, it thus uses less fuel compared to conventional
    #   vehicles)
    #
    #   FOR SOLUTIONS THAT CONSUME MORE FUEL THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:
    #   enter negative number representing total additional fuel used, X < 0 (e.g. we
    #   hope solutions do not actually consume more fuel than the conventional practice,
    #   check with the senior research team if you run into this)
    #   SolarPVUtil "Advanced Controls"!G159
    conv_fuel_consumed_per_funit: float = None
    soln_fuel_efficiency_factor: float = None

    # conv_fuel_emissions_factor: direct fuel emissions per funit, conventional
    #   SolarPVUtil "Advanced Controls"!I159
    # soln_fuel_emissions_factor: direct fuel emissions per funit, solution
    #   SolarPVUtil "Advanced Controls"!I163
    conv_fuel_emissions_factor: float = None
    soln_fuel_emissions_factor: float = None

    # conv_emissions_per_funit: This represents the direct CO2-eq emissions
    #   that result per functional unit that are not accounted for by use of the
    #   electric grid or fuel consumption.
    #   SolarPVUtil "Advanced Controls"!C174
    # soln_emissions_per_funit: This represents the direct CO2-eq emissions
    #   that result per functional unit that are not accounted for by use of the
    #   electric grid or fuel consumption.
    #   SolarPVUtil "Advanced Controls"!D174
    conv_emissions_per_funit: float = None
    soln_emissions_per_funit: float = None

    # ch4_is_co2eq: True if CH4 emissions measurement is in terms of CO2
    #   equivalent, False if measurement is in units of CH4 mass.
    #   derived from SolarPVUtil "Advanced Controls"!I184
    # n2o_is_co2eq: True if N2O emissions measurement is in terms of CO2
    #   equivalent, False if measurement is in units of N2O mass.
    #   derived from SolarPVUtil "Advanced Controls"!J184
    ch4_is_co2eq: bool = None
    n2o_is_co2eq: bool = None

    # co2eq_conversion_source: One of the conversion_source names
    #   defined in model/emissions_factors.py like "AR5 with feedback" or "AR4"
    #   SolarPVUtil "Advanced Controls"!I185
    co2eq_conversion_source: str = None

    # ch4_co2_per_funit: CO2-equivalent CH4 emitted per TWh, in tons.
    #   SolarPVUtil "Advanced Controls"!I174
    # n2o_co2_per_funit: CO2-equivalent N2O emitted per TWh, in tons.
    #   SolarPVUtil "Advanced Controls"!J174
    ch4_co2_per_funit: float = None
    n2o_co2_per_funit: float = None

    # soln_indirect_co2_per_iunit: CO2-equivalent indirect emissions per
    #   iunit, in tons.  SolarPVUtil "Advanced Controls"!G174
    # conv_indirect_co2_per_unit: CO2-equivalent indirect emissions per
    #   unit (func or impl depending on conv_indirect_co2_in_iunits).
    #   SolarPVUtil "Advanced Controls"!F174
    soln_indirect_co2_per_iunit: float = None
    conv_indirect_co2_per_unit: float = None

    # conv_indirect_co2_is_iunits: whether conv_indirect_co2_per_unit is
    #   iunits (True) or funits (False).  SolarPVUtil "Advanced Controls"!F184
    conv_indirect_co2_is_iunits: bool = None

    # soln_lifetime_capacity: This is the average expected number of
    #   functional units generated by the SOLUTION throughout their lifetime
    #   before replacement is required.  If no replacement time is discovered or
    #   applicable the fellow will default to 100 years.
    #
    #   E.g. an electric vehicle will have an average number of passenger kilometers
    #   it can travel until it can no longer be used and a new vehicle is required.
    #   Another example would be an efficient HVAC system, which can only service a
    #   certain amount of floor space over a period of time before it will require
    #   replacement.  SolarPVUtil "Advanced Controls"!E128
    # soln_avg_annual_use: Average Annual Use is the average annual use of
    #   the technology/practice, in functional units per implementation unit. This
    #   will likely differ significantly based on location, be sure to note which
    #   region the data is coming from. If data varies substantially by region, a
    #   weighted average may need to be used.
    #
    #   E.g. the average annual number of passenger kilometers (pkm) traveled per
    #   electric vehicle.  SolarPVUtil "Advanced Controls"!F128
    soln_lifetime_capacity: float = None
    soln_avg_annual_use: float = None

    # conv_lifetime_capacity: as soln_lifetime_capacity but for the conventional
    #   technology.  SolarPVUtil "Advanced Controls"!E95
    # conv_avg_annual_use: as soln_avg_annual_use but for the conventional
    #   technology.  SolarPVUtil "Advanced Controls"!F95
    conv_lifetime_capacity: float = None
    conv_avg_annual_use: float = None

    # report_start_year: first year of results to report (typically 2020).
    #   SolarPVUtil "Advanced Controls"!H4
    # report_end_year: last year of results to report (typically 2050).
    #   SolarPVUtil "Advanced Controls"!I4
    report_start_year: int = 2020
    report_end_year: int = 2050

    # soln_var_oper_cost_per_funit: This is the annual operating cost per functional
    #   unit, derived from the SOLUTION.  In most cases this will be expressed as a
    #   cost per 'some unit of energy'.
    #
    #   E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this
    #   can be considered the weighted average price of fuel per passenger kilometer.
    #   SolarPVUtil "Advanced Controls"!H128
    # soln_fixed_oper_cost_per_iunit: This is the annual operating cost per
    #   implementation unit, derived from the SOLUTION.  In most cases this will be
    #   expressed as a cost per 'some unit of installation size'
    #
    #   E.g., $10,000 per kw. In terms of transportation, this can be considered the
    #   total insurance, and maintenance cost per car.
    #
    #   Purchase costs can be amortized here or included as a first cost, but not both.
    # 
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   SolarPVUtil "Advanced Controls"!I128
    #
    #   For LAND solutions this is simply the operating cost per funit
    #   (funits == iunits == land units). The LAND model has no variable operating costs.
    #   Silvopasture "Advanced Controls"!C92
    # soln_fuel_cost_per_funit: Fuel/consumable cost per functional unit.
    #   SolarPVUtil "Advanced Controls"!K128
    soln_var_oper_cost_per_funit: float = None
    soln_fixed_oper_cost_per_iunit: typing.Any = None
    soln_fuel_cost_per_funit: float = None

    # conv_var_oper_cost_per_funit: as soln_var_oper_cost_per_funit.
    #   SolarPVUtil "Advanced Controls"!H95
    # conv_fixed_oper_cost_per_iunit: as soln_fixed_oper_cost_per_funit.
    #   SolarPVUtil "Advanced Controls"!I95 / Silvopasture "Advanced Controls"!C77
    # conv_fuel_cost_per_funit: as soln_fuel_cost_per_funit.
    #   SolarPVUtil "Advanced Controls"!K95
    conv_var_oper_cost_per_funit: float = None
    conv_fixed_oper_cost_per_iunit: typing.Any = None
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

    # pds_base_adoption: a list of (region, float) tuples of the base adoption for the PDS
    #   calculations. For example: [('World', 150000000.0), ('OECD90', 90000000.0), ...]
    #   SolarPVUtil "ScenarioRecord" rows 151 - 160.
    # pds_adoption_final_percentage: a list of (region, %) tuples of the final adoption
    #   percentage for the PDS calculations. For example: [('World', 0.54), ('OECD90', 0.60), ...]
    #   SolarPVUtil "ScenarioRecord" rows 170 - 179.
    pds_base_adoption: typing.List[tuple] = None
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
    # tco2eq_reduced_per_land_unit: Aggregate emissions reduced per land unit
    #    ForestProtection "Advanced Controls"!B138 (Land models)
    # tco2eq_rplu_rate: whether tco2eq_reduced_per_land_unit is 'One-time' or 'Annual'
    #    ForestProtection "Advanced Controls"!B148 (Land models)
    # [similar vars for co2, n2o_co2 and ch4_co2
    #    ForestProtection "Advanced Controls"!C148:E148 (Land models)]
    tco2eq_reduced_per_land_unit: typing.Any = None
    tco2eq_rplu_rate: str = None
    tco2_reduced_per_land_unit: typing.Any = None
    tco2_rplu_rate: str = None
    tn2o_co2_reduced_per_land_unit: typing.Any = None
    tn2o_co2_rplu_rate: str = None
    tch4_co2_reduced_per_land_unit: typing.Any = None
    tch4_co2_rplu_rate: str = None

    # emissions_use_agg_co2eq: Use Aggregate CO2-eq instead of Individual GHG for direct emissions
    #  ForestProtection "Advanced Controls"!C155 (Land models)
    emissions_use_agg_co2eq: bool = None

    # seq_rate_global: carbon sequestration rate for All Land or All of Special Land.
    #  Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #  "Advanced Controls"!B173 (Land models)
    seq_rate_global: typing.Any = None

    #seq_rate_per_regime (dict of float): carbon sequestration rate for each thermal-moisture
    #  regime. "Advanced Controls"!C173:G173 (Land models)
    seq_rate_per_regime: typing.Dict = None

    # degradation_rate: % annually
    #    ForestProtection "Advanced Controls"!B187 (Land models)
    # disturbance_rate: disturbance rate
    #    TropicalForests. "Advanced Controls"!I173 (Land models)
    degradation_rate: typing.Any = None
    disturbance_rate: typing.Any = None

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
    # yield_gain_from_conv_to_soln: yield % increase from conventional to solution.
    #   Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
    #   "Advanced Controls"!G92 (Land models)
    yield_from_conv_practice: typing.Any = None
    yield_gain_from_conv_to_soln: typing.Any = None

    # use_custom_tla: whether to use custom TLA data instead of Drawdown land allocation
    #   "Advanced Controls"!E54 (Land models)
    use_custom_tla: bool = None

    # harvest_frequency: new growth is harvested/cleared every ... (years)
    #   Afforestation "Advanced Controls"!B187
    harvest_frequency: float = None

    # carbon_not_emitted_after_harvesting: Sequestered Carbon NOT Emitted after Cyclical
    #   Harvesting/Clearing    Afforestation "Advanced Controls"!H187
    carbon_not_emitted_after_harvesting: typing.Any = None

    # avoided_deforest_with_intensification: Factor for avoiding deforestation by more
    #   intensively using the land. Women Smallholders "Advanced Controls"!E205
    avoided_deforest_with_intensification: typing.Any = None
  
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
    tC_storage_in_protected_land_type: typing.Any = None

    def __post_init__(self):
        object.__setattr__(self, 'pds_2014_cost', self._substitute_vma(
                self.pds_2014_cost, vma_title='SOLUTION First Cost per Implementation Unit'))
        object.__setattr__(self, 'ref_2014_cost', self._substitute_vma(
                self.ref_2014_cost, vma_title='SOLUTION First Cost per Implementation Unit'))
        object.__setattr__(self, 'conv_2014_cost', self._substitute_vma(
                self.conv_2014_cost,
                vma_title='CONVENTIONAL First Cost per Implementation Unit for replaced practices'))
        object.__setattr__(self, 'soln_fixed_oper_cost_per_iunit', self._substitute_vma(
                self.soln_fixed_oper_cost_per_iunit,
                vma_title='SOLUTION Operating Cost per Functional Unit per Annum'))
        object.__setattr__(self, 'conv_fixed_oper_cost_per_iunit', self._substitute_vma(
                self.conv_fixed_oper_cost_per_iunit,
                vma_title='CONVENTIONAL Operating Cost per Functional Unit per Annum'))

        # LAND only
        object.__setattr__(self, 'tco2eq_reduced_per_land_unit', self._substitute_vma(
                self.tco2eq_reduced_per_land_unit,
                vma_title='t CO2-eq (Aggregate emissions) Reduced per Land Unit'))
        object.__setattr__(self, 'tco2_reduced_per_land_unit', self._substitute_vma(
                self.tco2_reduced_per_land_unit,
                vma_title='t CO2 Reduced per Land Unit'))
        object.__setattr__(self, 'tn2o_co2_reduced_per_land_unit', self._substitute_vma(
                self.tn2o_co2_reduced_per_land_unit,
                vma_title='t N2O-CO2-eq Reduced per Land Unit'))
        object.__setattr__(self, 'tch4_co2_reduced_per_land_unit', self._substitute_vma(
                self.tch4_co2_reduced_per_land_unit,
                vma_title='t CH4-CO2-eq Reduced per Land Unit'))
        object.__setattr__(self, 'seq_rate_global', self._substitute_vma(
                self.seq_rate_global,
                vma_title='Sequestration Rates'))
        object.__setattr__(self, 'degradation_rate', self._substitute_vma(
                self.degradation_rate,
                vma_title='Growth Rate of Land Degradation'))
        object.__setattr__(self, 'disturbance_rate', self._substitute_vma(
                self.disturbance_rate,
                vma_title='Disturbance Rate'))
        object.__setattr__(self, 'yield_from_conv_practice', self._substitute_vma(
                self.yield_from_conv_practice,
                vma_title='Yield  from CONVENTIONAL Practice'))
        object.__setattr__(self, 'yield_gain_from_conv_to_soln', self._substitute_vma(
                self.yield_gain_from_conv_to_soln,
                vma_title='Yield Gain (% Increase from CONVENTIONAL to SOLUTION)'))
        object.__setattr__(self, 'carbon_not_emitted_after_harvesting', self._substitute_vma(
                self.carbon_not_emitted_after_harvesting,
                vma_title='Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing'))
        object.__setattr__(self, 'avoided_deforest_with_intensification', self._substitute_vma(
                self.avoided_deforest_with_intensification,
                vma_title='Avoided_Deforested_Area_With_Increase_in_Agricultural_Intensification'))
        object.__setattr__(self, 'tC_storage_in_protected_land_type', self._substitute_vma(
                self.tC_storage_in_protected_land_type,
                vma_title='t C storage in Protected Landtype'))

        if isinstance(self.solution_category, str):
            object.__setattr__(self, 'solution_category',
                    self.string_to_solution_category(self.solution_category))
        if isinstance(self.co2eq_conversion_source, str):
            object.__setattr__(self, 'co2eq_conversion_source', ef.string_to_conversion_source(
                    self.co2eq_conversion_source))
        if isinstance(self.emissions_grid_source, str):
            object.__setattr__(self, 'emissions_grid_source', ef.string_to_emissions_grid_source(
                    self.emissions_grid_source))
        if isinstance(self.emissions_grid_range, str):
            object.__setattr__(self, 'emissions_grid_range', ef.string_to_emissions_grid_range(
                    self.emissions_grid_range))

        object.__setattr__(self, 'soln_energy_efficiency_factor',
                self.value_or_zero(self.soln_energy_efficiency_factor))
        object.__setattr__(self, 'conv_annual_energy_used',
                self.value_or_zero(self.conv_annual_energy_used))
        object.__setattr__(self, 'soln_annual_energy_used',
                self.value_or_zero(self.soln_annual_energy_used))
        object.__setattr__(self, 'conv_fuel_consumed_per_funit',
                self.value_or_zero(self.conv_fuel_consumed_per_funit))
        object.__setattr__(self, 'soln_fuel_efficiency_factor',
                self.value_or_zero(self.soln_fuel_efficiency_factor))
        object.__setattr__(self, 'conv_fuel_emissions_factor',
                self.value_or_zero(self.conv_fuel_emissions_factor))
        object.__setattr__(self, 'soln_fuel_emissions_factor',
                self.value_or_zero(self.soln_fuel_emissions_factor))
        object.__setattr__(self, 'conv_emissions_per_funit',
                self.value_or_zero(self.conv_emissions_per_funit))
        object.__setattr__(self, 'soln_emissions_per_funit',
                self.value_or_zero(self.soln_emissions_per_funit))
        object.__setattr__(self, 'ch4_co2_per_funit',
                self.value_or_zero(self.ch4_co2_per_funit))
        object.__setattr__(self, 'n2o_co2_per_funit',
                self.value_or_zero(self.n2o_co2_per_funit))


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


    def value_or_zero(self, val):
        """Allow a blank space or empty string to mean zero.
           Useful for advanced controls like conv_average_electricity_used."""
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

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
            return excel_math.round(self.soln_lifetime_capacity / self.soln_avg_annual_use)
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
            return excel_math.round(self.conv_lifetime_capacity / self.conv_avg_annual_use)
        elif self.conv_expected_lifetime is not None:  # LAND
            # LAND models input lifetime directly so I doubt we will come across rounding errors
            # i.e. expected_lifetime will probably be a whole number of years
            # Integration test will catch the case where this assumption is wrong
            return int(self.conv_expected_lifetime)
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for conventional')

    def string_to_solution_category(self, text):
        ltext = str(text).lower()
        if ltext == "replacement":
            return SOLUTION_CATEGORY.REPLACEMENT
        elif ltext == "reduction":
            return SOLUTION_CATEGORY.REDUCTION
        elif ltext == 'land':
            return SOLUTION_CATEGORY.LAND
        elif ltext == "not_applicable" or ltext == "not applicable" or ltext == "na":
            return SOLUTION_CATEGORY.NOT_APPLICABLE
        raise ValueError("invalid solution category: " + str(text))

    def _substitute_vma(self, val, vma_title):
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
          vma_title: title of VMA table (can be found in vma_info.csv in the soln dir)
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
            else:
                raw_val_from_excel = val['value']
                stat = val['statistic']
        else:
            return val

        for vma_key in self.vmas.keys():
            if vma_key.startswith(vma_title):  # This handles the case of 'first cost' title discrepancies
                vma_title = vma_key
                break
        else:
            raise KeyError(
                '{} must be included in vmas to calculate mean/high/low. vmas included: {}'.format(vma_title,
                                                                                                   self.vmas.keys()))
        if return_regional_series:
            result = pd.Series(name='regional values')
            for reg in REGIONS:
                result[reg] = self.vmas[vma_title].avg_high_low(key=stat.lower(), region=reg)
        else:
            result = self.vmas[vma_title].avg_high_low(key=stat.lower())
        if raw_val_from_excel is not None and result != approx(raw_val_from_excel):
            warn(
                "raw value from scenario record tab in excel does not match the {0} of VMA table '{1}'."
                "\nThis is probably because the scenario was linked to the {0} of an older version of the table.".format(stat, vma_title))
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
