"""Implements the Advanced Controls, settings which have a default  # by Denton Gentry
   but can be overridden to fit particular needs.  # by Denton Gentry
"""  # by Denton Gentry
# by Denton Gentry
import enum  # by Denton Gentry
from pytest import approx
from warnings import warn
from model import emissionsfactors as ef  # by Denton Gentry
from model import excel_math  # by Denton Gentry

# by Denton Gentry
# by Denton Gentry
SOLUTION_CATEGORY = enum.Enum('SOLUTION_CATEGORY', 'REPLACEMENT REDUCTION NOT_APPLICABLE LAND')
translate_adoption_bases = {"DEFAULT Linear": "Linear", "DEFAULT S-Curve": "Logistic S-Curve"}  # by Denton Gentry
valid_pds_adoption_bases = {'Linear', 'Logistic S-Curve', 'Existing Adoption Prognostications',  # by Denton Gentry
                            'Customized S-Curve Adoption', 'Fully Customized PDS', 'Bass Diffusion S-Curve',
                            None}  # by Denton Gentry
valid_ref_adoption_bases = {'Default', 'Custom', None}  # by Denton Gentry
valid_adoption_growth = {'High', 'Medium', 'Low', None}


# by Denton Gentry
class AdvancedControls:  # by Denton Gentry
    """Advanced Controls module, with settings impacting other modules.  # by Denton Gentry
  
    vmas: dict of VMA objects required for calculation of certain values.
        dict keys should be the VMA title (found in VMA_info.csv in solution dir).
        Example:
        {'Sequestration Rates': vma.VMA('path_to_soln_vmas' + 'Sequestration_Rates.csv')}
  
    pds_2014_cost: US$2014 cost to acquire + install, per implementation  # by Denton Gentry
       unit (ex: kW for energy scenarios), for the Project Drawdown  # by Denton Gentry
       Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
       Solution (PDS).  SolarPVUtil "Advanced Controls"!B128  # by Denton Gentry
    ref_2014_cost: US$2014 cost to acquire + install, per implementation  # by Denton Gentry
       unit, for the reference technology.  # by Denton Gentry
       Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
       SolarPVUtil "Advanced Controls"!B128 (same as PDS)  # by Denton Gentry
    conv_2014_cost: US$2014 cost to acquire + install, per implementation  # by Denton Gentry
       unit, for the conventional technology.  # by Denton Gentry
       Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
       SolarPVUtil "Advanced Controls"!B95  # by Denton Gentry
    soln_first_cost_efficiency_rate: rate that the modelled solution improves /  # by Denton Gentry
       lowers in cost per year. In calculations this is usually converted  # by Denton Gentry
       to the learning rate, which is 1/efficiency_rate.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!C128  # by Denton Gentry
    conv_first_cost_efficiency_rate: rate that the conventional technology  # by Denton Gentry
       improves / lowers in cost each year. Efficiency rates for the  # by Denton Gentry
       conventional technology are typically close to zero, these technologies  # by Denton Gentry
       have already had many years of development and maturation.  # by Denton Gentry
       In calculations this is usually converted to the learning rate,  # by Denton Gentry
       which is 1/efficiency_rate.  SolarPVUtil "Advanced Controls"!C95  # by Denton Gentry
    soln_first_cost_below_conv (boolean): The solution first cost may decline  # by Denton Gentry
       below that of the Conventional due to the learning rate chosen. This may  # by Denton Gentry
       be acceptable in some cases for instance when the projections in the  # by Denton Gentry
       literature indicate so. In other cases, it may not be likely for the  # by Denton Gentry
       Solution to become cheaper than the Conventional.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!C132  # by Denton Gentry
    soln_energy_efficiency_factor (float): Units of energy reduced per year per  # by Denton Gentry
       functional unit installed.  # by Denton Gentry
    # by Denton Gentry
       FOR CLEAN RENEWABLE ENERGY SOLUTIONS: enter 0 (e.g. implementing solar PV  # by Denton Gentry
       fully replaces existing fossil fuel-based generation, but does not reduce  # by Denton Gentry
       the amount of energy generated)  # by Denton Gentry
    # by Denton Gentry
       FOR ENERGY EFFICIENCY SOLUTIONS: enter positive number representing total  # by Denton Gentry
       energy reduced, 0 < X < 1 (e.g. HVAC efficiencies reduce the average annual  # by Denton Gentry
       energy consumption of buildings, by square meters of floor space; they still  # by Denton Gentry
       use the electric grid, but significantly less)  # by Denton Gentry
    # by Denton Gentry
       FOR SOLUTIONS THAT CONSUME MORE ENERGY THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:  # by Denton Gentry
       Use the next input, Total Annual Energy Used SOLUTION (e.g. electric vehicles  # by Denton Gentry
       use energy from the electric grid, whereas conventional vehicles use only fuel)  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!C159  # by Denton Gentry
    conv_annual_energy_used (float): for solutions that reduce electricity  # by Denton Gentry
       consumption per functional unit, enter the average electricity used per  # by Denton Gentry
       functional unit of the conventional technologies/practices.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!B159  # by Denton Gentry
    soln_annual_energy_used (float): This refers to the units of average energy  # by Denton Gentry
       used per year per functional unit installed.  # by Denton Gentry
    # by Denton Gentry
       This is an optional variable to be used in cases where a) the literature  # by Denton Gentry
       reports the energy use of the solution rather than energy efficiency; or  # by Denton Gentry
       b) the solution uses more electricity than the conventional  # by Denton Gentry
       technologies/practices.  # by Denton Gentry
    # by Denton Gentry
       E.g. electric vehicles use energy from the electric grid, whereas  # by Denton Gentry
       conventional vehicles use only fuel)  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!D159  # by Denton Gentry
    # by Denton Gentry
    conv_fuel_consumed_per_funit (float): This refers to the unit (default is Liters)  # by Denton Gentry
       of FUEL used per year per cumulative unit installed. The equation may need to  # by Denton Gentry
       be edited if your energy savings depend on the marginal unit installed rather  # by Denton Gentry
       than the cumulative units. SolarPVUtil "Advanced Controls"!F159  # by Denton Gentry
    soln_fuel_efficiency_factor (float): This refers to the % fuel reduced by the  # by Denton Gentry
       SOLUTION relative to the CONVENTIONAL mix of technologies/practices. The  # by Denton Gentry
       Percent reduction is assumed to apply to the Conventional Fuel Unit, if  # by Denton Gentry
       different to the Solution Fuel Unit.  # by Denton Gentry
    # by Denton Gentry
       FOR REPLACEMENT SOLUTIONS: enter 1 (e.g. electric vehicles fully replace fuel  # by Denton Gentry
       consumption with electricity use -- but be sure to add a negative value for  # by Denton Gentry
       Annual Energy Reduced from Electric Grid Mix!)  # by Denton Gentry
    # by Denton Gentry
       FOR FUEL EFFICIENCY SOLUTIONS: enter positive number representing total fuel  # by Denton Gentry
       reduced, 0 < X < 1  (e.g. hybrid-electric vehicles partially replace fuel  # by Denton Gentry
       consumption with electricity use, it thus uses less fuel compared to conventional  # by Denton Gentry
       vehicles)  # by Denton Gentry
    # by Denton Gentry
       FOR SOLUTIONS THAT CONSUME MORE FUEL THAN THE CONVENTIONAL TECHNOLOGY/PRACTICE:  # by Denton Gentry
       enter negative number representing total additional fuel used, X < 0 (e.g. we  # by Denton Gentry
       hope solutions do not actually consume more fuel than the conventional practice,  # by Denton Gentry
       check with the senior research team if you run into this)  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!G159  # by Denton Gentry
    # by Denton Gentry
    conv_fuel_emissions_factor (float): direct fuel emissions per funit, conventional  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!I159  # by Denton Gentry
    soln_fuel_emissions_factor (float): direct fuel emissions per funit, solution  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!I163  # by Denton Gentry
    # by Denton Gentry
    conv_emissions_per_funit (float): This represents the direct CO2-eq emissions  # by Denton Gentry
       that result per functional unit that are not accounted for by use of the  # by Denton Gentry
       electric grid or fuel consumption.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!C174  # by Denton Gentry
    soln_emissions_per_funit (float): This represents the direct CO2-eq emissions  # by Denton Gentry
       that result per functional unit that are not accounted for by use of the  # by Denton Gentry
       electric grid or fuel consumption.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!D174  # by Denton Gentry
    # by Denton Gentry
    ch4_is_co2eq (boolean): True if CH4 emissions measurement is in terms of CO2  # by Denton Gentry
       equivalent, False if measurement is in units of CH4 mass.  # by Denton Gentry
       derived from SolarPVUtil "Advanced Controls"!I184  # by Denton Gentry
    n2o_is_co2eq (boolean): True if N2O emissions measurement is in terms of CO2  # by Denton Gentry
       equivalent, False if measurement is in units of N2O mass.  # by Denton Gentry
       derived from SolarPVUtil "Advanced Controls"!J184  # by Denton Gentry
    co2eq_conversion_source (string): One of the conversion_source names  # by Denton Gentry
       defined in model/emissions_factors.py like "AR5 with feedback" or "AR4"  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!I185  # by Denton Gentry
    ch4_co2_per_twh (float): CO2-equivalent CH4 emitted per TWh, in tons.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!I174  # by Denton Gentry
    n2o_co2_per_twh (float): CO2-equivalent N2O emitted per TWh, in tons.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!J174  # by Denton Gentry
    soln_indirect_co2_per_iunit (float): CO2-equivalent indirect emissions per  # by Denton Gentry
       iunit, in tons.  SolarPVUtil "Advanced Controls"!G174  # by Denton Gentry
    conv_indirect_co2_per_unit (float): CO2-equivalent indirect emissions per  # by Denton Gentry
       unit (func or impl depending on conv_indirect_co2_in_iunits).  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!F174  # by Denton Gentry
    conv_indirect_co2_is_iunits (boolean): whether conv_indirect_co2_per_unit is  # by Denton Gentry
       iunits (True) or funits (False).  SolarPVUtil "Advanced Controls"!F184  # by Denton Gentry
    # by Denton Gentry
    soln_lifetime_capacity (float): This is the average expected number of  # by Denton Gentry
       functional units generated by the SOLUTION throughout their lifetime  # by Denton Gentry
       before replacement is required.  If no replacement time is discovered or  # by Denton Gentry
       applicable the fellow will default to 100 years.  # by Denton Gentry
    # by Denton Gentry
       E.g. an electric vehicle will have an average number of passenger kilometers  # by Denton Gentry
       it can travel until it can no longer be used and a new vehicle is required.  # by Denton Gentry
       Another example would be an efficient HVAC system, which can only service a  # by Denton Gentry
       certain amount of floor space over a period of time before it will require  # by Denton Gentry
       replacement.  SolarPVUtil "Advanced Controls"!E128  # by Denton Gentry
    soln_avg_annual_use (float): Average Annual Use is the average annual use of  # by Denton Gentry
       the technology/practice, in functional units per implementation unit. This  # by Denton Gentry
       will likely differ significantly based on location, be sure to note which  # by Denton Gentry
       region the data is coming from. If data varies substantially by region, a  # by Denton Gentry
       weighted average may need to be used.  # by Denton Gentry
    # by Denton Gentry
       E.g. the average annual number of passenger kilometers (pkm) traveled per  # by Denton Gentry
       electric vehicle.  SolarPVUtil "Advanced Controls"!F128  # by Denton Gentry
    conv_lifetime_capacity (float): as soln_lifetime_capacity but for the conventional  # by Denton Gentry
       technology.  SolarPVUtil "Advanced Controls"!E95  # by Denton Gentry
    conv_avg_annual_use (float): as soln_avg_annual_use but for the conventional  # by Denton Gentry
       technology.  SolarPVUtil "Advanced Controls"!F95  # by Denton Gentry
    # by Denton Gentry
    report_start_year (int): first year of results to report (typically 2020).  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!H4  # by Denton Gentry
    report_end_year (int): last year of results to report (typically 2050).  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!I4  # by Denton Gentry
    # by Denton Gentry
    soln_var_oper_cost_per_funit (float): This is the annual operating cost per functional  # by Denton Gentry
       unit, derived from the SOLUTION.  In most cases this will be expressed as a  # by Denton Gentry
       cost per 'some unit of energy'.  # by Denton Gentry
    # by Denton Gentry
       E.g., $1 per Kwh or $1,000,000,000 per TWh. In terms of transportation, this  # by Denton Gentry
       can be considered the weighted average price of fuel per passenger kilometer.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!H128  # by Denton Gentry
    soln_fixed_oper_cost_per_iunit (float): This is the annual operating cost per  # by Denton Gentry
       implementation unit, derived from the SOLUTION.  In most cases this will be  # by Denton Gentry
       expressed as a cost per 'some unit of installation size'  # by Denton Gentry
    # by Denton Gentry
       E.g., $10,000 per kw. In terms of transportation, this can be considered the  # by Denton Gentry
       total insurance, and maintenance cost per car.  # by Denton Gentry
    # by Denton Gentry
       Purchase costs can be amortized here or included as a first cost, but not both.  # by Denton Gentry
  
       Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
  
       SolarPVUtil "Advanced Controls"!I128  # by Denton Gentry
  
       For LAND solutions this is simply the operating cost per funit
       (funits == iunits == land units). The LAND model has no variable operating costs.
       Silvopasture "Advanced Controls"!C92
  
    soln_fuel_cost_per_funit (float): Fuel/consumable cost per functional unit.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!K128  # by Denton Gentry
    conv_var_oper_cost_per_funit (float): as soln_var_oper_cost_per_funit.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!H95  # by Denton Gentry
    conv_fixed_oper_cost_per_iunit (float): as soln_fixed_oper_cost_per_funit.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!I95 / Silvopasture "Advanced Controls"!C77
    conv_fuel_cost_per_funit (float): as soln_fuel_cost_per_funit.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!K95  # by Denton Gentry
    # by Denton Gentry
    npv_discount_rate (float): discount rate for Net Present Value calculations.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!B141  # by Denton Gentry
  
    emissions_use_co2eq (boolean): whether to use CO2-equivalent for ppm calculations.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!B189  # by Denton Gentry
    emissions_grid_source (string): "IPCC Only" or "Meta Analysis" of multiple studies.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!C189  # by Denton Gentry
    emissions_grid_range (string): "mean", "low" or "high" for which estimate to use.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!D189  # by Denton Gentry
    # by Denton Gentry
    soln_ref_adoption_regional_data (boolean): whether funit adoption should add the regional data  # by Denton Gentry
       to estimate the World, or perform a separate estimate for the world.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!B284  # by Denton Gentry
    soln_pds_adoption_regional_data (boolean): as soln_ref_adoption_regional_data.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!B246  # by Denton Gentry
    soln_ref_adoption_basis (string): whether to use adoption_data.py or custom_adoption.py.  # by Denton Gentry
       Must be one of valid_ref_adoption_bases.  SolarPVUtil "Advanced Controls"!B279  # by Denton Gentry
    soln_ref_adoption_custom_name (string): Name of the Custom REF Adoption source to use, if  # by Denton Gentry
       soln_ref_adoption_basis is "Custom".  Insulation "Advanced Controls"!B267  # by Denton Gentry
    soln_pds_adoption_basis (string): the type of interpolation to fill in adoption data for  # by Denton Gentry
       each year. Must be one of valid_pds_adoption_bases. SolarPVUtil "Advanced Controls"!B243  # by Denton Gentry
    soln_pds_adoption_prognostication_source (string): the name of one specific data source, or the  # by Denton Gentry
       name of a class of sources (like "Conservative Cases" or "Ambitious Cases"), or "ALL SOURCES"  # by Denton Gentry
       to take the average of all sources. SolarPVUtil "Advanced Controls"!B265  # by Denton Gentry
    soln_pds_adoption_prognostication_trend (string): the type of curve fit  # by Denton Gentry
       to use like 2nd order polynomial or exponential. SolarPVUtil "Advanced Controls"!B270  # by Denton Gentry
    soln_pds_adoption_prognostication_growth (string): High, Medium, or Low projected growth.  # by Denton Gentry
       SolarPVUtil "Advanced Controls"!C270  # by Denton Gentry
    soln_pds_adoption_custom_name (string): Name of the Custom PDS Adoption source to use, if  # by Denton Gentry
       soln_pds_adoption_basis is "Fully Customized PDS".  # by Denton Gentry
       SmartThermostats "Advanced Controls"!H250  # by Denton Gentry
    pds_source_post_2014 (string): The name of the data source to use for the PDS case for  # by Denton Gentry
       years after 2014. SolarPVUtil "Advanced Controls"!B55  # by Denton Gentry
    ref_source_post_2014 (string): The name of the data source to use for the REF case for  # by Denton Gentry
       years after 2014. SolarPVUtil "Advanced Controls"!B54  # by Denton Gentry
    source_until_2014 (string): The name of the data source to use for all cases for years  # by Denton Gentry
       2014 and before. SolarPVUtil "Advanced Controls"!B53  # by Denton Gentry
    ref_adoption_use_pds_years (list of int): years for which the Helpertables REF adoption  # by Denton Gentry
       for 'World' should use the PDS adoption values. SolarPVUtil "ScenarioRecord"! offset 218  # by Denton Gentry
    pds_adoption_use_ref_years (list of int): years for which the Helpertables PDS adoption  # by Denton Gentry
       for 'World' should use the REF adoption values. SolarPVUtil "ScenarioRecord"! offset 219  # by Denton Gentry
    pds_base_adoption (dict): a list of (region, float) tuples of the base adoption for the PDS  # by Denton Gentry
       calculations. For example: [('World', 150000000.0), ('OECD90', 90000000.0), ...]  # by Denton Gentry
       SolarPVUtil "ScenarioRecord" rows 151 - 160.  # by Denton Gentry
    pds_adoption_final_percentage (dict): a list of (region, %) tuples of the final adoption  # by Denton Gentry
       percentage for the PDS calculations. For example: [('World', 0.54), ('OECD90', 0.60), ...]  # by Denton Gentry
       SolarPVUtil "ScenarioRecord" rows 170 - 179.  # by Denton Gentry
    pds_adoption_s_curve_innovation (dict): a list of (region, float) tuples of the innovation  # by Denton Gentry
       factor used in the Bass Diffusion S-Curve model.  SolarPVUtil "ScenarioRecord" rows 170 - 179.  # by Denton Gentry
    pds_adoption_s_curve_imitation (dict): a list of (region, float) tuples of the innovation  # by Denton Gentry
       factor used in the Bass Diffusion S-Curve model.  SolarPVUtil "ScenarioRecord" rows 170 - 179.  # by Denton Gentry
    # by Denton Gentry
    solution_category (SOLUTION_CATEGORY): Whether the solution is primarily REDUCTION of  # by Denton Gentry
       emissions from an existing technology, REPLACEMENT of a technology to one with lower  # by Denton Gentry
       emissions, or NOT_APPLICABLE for something else entirely.  'Advanced Controls'!A159  # by Denton Gentry
    # by Denton Gentry
    tco2eq_reduced_per_land_unit: Aggregate emissions reduced per land unit
      ForestProtection "Advanced Controls"!B138 (Land models)
    tco2eq_rplu_rate: whether tco2eq_reduced_per_land_unit is 'One-time' or 'Annual'
      ForestProtection "Advanced Controls"!B148 (Land models)
    [similar vars for co2, n2o_co2 and ch4_co2 ForestProtection "Advanced Controls"!C148:E148 (Land models)]
    emissions_use_agg_co2eq: Use Aggregate CO2-eq instead of Individual GHG? (for direct emissions)
      ForestProtection "Advanced Controls"!C155 (Land models)
  
    seq_rate_global (float): carbon sequestration rate for All Land or All of Special Land.  # by Denton Gentry
      Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
      "Advanced Controls"!B173 (Land models)
    seq_rate_per_regime (dict of float): carbon sequestration rate for each thermal-moisture  # by Denton Gentry
      regime. "Advanced Controls"!C173:G173 (Land models)  # by Denton Gentry
    growth_rate_of_land_degradation: % annually ForestProtection "Advanced Controls"!B187 (Land models)
    disturbance_rate (float): disturbance rate TropicalForests. "Advanced Controls"!I173 (Land models)
    global_multi_for_regrowth: Global multiplier for regrowth  ForestProtection "Advanced Controls"!E187 (Land models)
    soln_expected_lifetime: solution expected lifetime in year.s "Advanced Controls"!F92 (Land models)
    conv_expected_lifetime: conventional expected lifetime in years. Default value is 30.
     "Advanced Controls"!F77 (Land models)
    yield_from_conv_practice: conventional yield in DM tons fodder/ha/year.
      Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
      "Advanced Controls"!G77 (Land models)
    yield_gain_from_conv_to_soln: yield % increase from conventional to solution.
      Can alternatively be set to 'mean', 'high' or 'low' of its corresponding VMA object
      "Advanced Controls"!G92 (Land models)
    use_custom_tla: bool indicating whether to use custom TLA data instead of Drawdown land allocation
      "Advanced Controls"!E54 (Land models)
    harvest_frequency (float): new growth is harvested/cleared every ... (years) Afforestation "Advanced Controls"!B187
    carbon_not_emitted_after_harvesting (float): Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing
      Afforestation "Advanced Controls"!H187
  
    delay_protection_1yr (bool): Delay Impact of Protection by 1 Year? (Leakage)  # by Denton Gentry
      ForestProtection "Advanced Controls"!B200 (land models)  # by Denton Gentry
    delay_regrowth_1yr (bool): Delay Regrowth of Degraded Land by 1 Year?  # by Denton Gentry
      ForestProtection "Advanced Controls"!C200 (land models)  # by Denton Gentry
    include_unprotected_land_in_regrowth_calcs (bool): Include Unprotected Land in Regrowth Calculations?  # by Denton Gentry
      ForestProtection "Advanced Controls"!D200 (land models)  # by Denton Gentry
    land_annual_emissons_lifetime (bool): Lifetime of tracked emissions.  # by Denton Gentry
      Conservation Agriculture "Advanced Controls"!D150 (land models)  # by Denton Gentry
    """  # by Denton Gentry

    def __init__(self,  # by Denton Gentry
                 vmas=None,

                 pds_2014_cost=None,  # by Denton Gentry
                 ref_2014_cost=None,  # by Denton Gentry
                 conv_2014_cost=None,  # by Denton Gentry
                 # by Denton Gentry
                 soln_first_cost_efficiency_rate=None,  # by Denton Gentry
                 conv_first_cost_efficiency_rate=None,  # by Denton Gentry
                 soln_first_cost_below_conv=None,  # by Denton Gentry
                 # by Denton Gentry
                 soln_energy_efficiency_factor=None,  # by Denton Gentry
                 conv_annual_energy_used=None,  # by Denton Gentry
                 soln_annual_energy_used=None,  # by Denton Gentry
                 # by Denton Gentry
                 conv_fuel_consumed_per_funit=None,  # by Denton Gentry
                 soln_fuel_efficiency_factor=None,  # by Denton Gentry
                 conv_fuel_emissions_factor=None,  # by Denton Gentry
                 soln_fuel_emissions_factor=None,  # by Denton Gentry
                 # by Denton Gentry
                 conv_emissions_per_funit=None,  # by Denton Gentry
                 soln_emissions_per_funit=None,  # by Denton Gentry
                 # by Denton Gentry
                 ch4_is_co2eq=None,  # by Denton Gentry
                 n2o_is_co2eq=None,  # by Denton Gentry
                 co2eq_conversion_source=None,  # by Denton Gentry
                 ch4_co2_per_twh=None,  # by Denton Gentry
                 n2o_co2_per_twh=None,  # by Denton Gentry
                 soln_indirect_co2_per_iunit=None,  # by Denton Gentry
                 conv_indirect_co2_per_unit=None,  # by Denton Gentry
                 conv_indirect_co2_is_iunits=None,  # by Denton Gentry
                 # by Denton Gentry
                 soln_lifetime_capacity=None,  # by Denton Gentry
                 soln_avg_annual_use=None,  # by Denton Gentry
                 conv_lifetime_capacity=None,  # by Denton Gentry
                 conv_avg_annual_use=None,  # by Denton Gentry
                 # by Denton Gentry
                 report_start_year=2020,
                 report_end_year=2050,
                 # by Denton Gentry
                 soln_var_oper_cost_per_funit=None,  # by Denton Gentry
                 soln_fixed_oper_cost_per_iunit=None,  # by Denton Gentry
                 soln_fuel_cost_per_funit=None,  # by Denton Gentry
                 conv_var_oper_cost_per_funit=None,  # by Denton Gentry
                 conv_fixed_oper_cost_per_iunit=None,  # by Denton Gentry
                 conv_fuel_cost_per_funit=None,  # by Denton Gentry
                 # by Denton Gentry
                 npv_discount_rate=None,  # by Denton Gentry
                 # by Denton Gentry
                 emissions_use_co2eq=None,  # by Denton Gentry
                 emissions_grid_source=None,  # by Denton Gentry
                 emissions_grid_range=None,  # by Denton Gentry
                 # by Denton Gentry
                 soln_ref_adoption_regional_data=None,  # by Denton Gentry
                 soln_pds_adoption_regional_data=None,  # by Denton Gentry
                 soln_ref_adoption_basis=None,  # by Denton Gentry
                 soln_ref_adoption_custom_name=None,  # by Denton Gentry
                 soln_pds_adoption_basis=None,  # by Denton Gentry
                 soln_pds_adoption_prognostication_source=None,  # by Denton Gentry
                 soln_pds_adoption_prognostication_trend=None,  # by Denton Gentry
                 soln_pds_adoption_prognostication_growth=None,  # by Denton Gentry
                 soln_pds_adoption_custom_name=None,  # by Denton Gentry
                 pds_source_post_2014=None,  # by Denton Gentry
                 ref_source_post_2014=None,  # by Denton Gentry
                 source_until_2014=None,  # by Denton Gentry
                 ref_adoption_use_pds_years=None,
                 pds_adoption_use_ref_years=None,
                 pds_base_adoption=None,  # by Denton Gentry
                 pds_adoption_final_percentage=None,  # by Denton Gentry
                 pds_adoption_s_curve_innovation=None,  # by Denton Gentry
                 pds_adoption_s_curve_imitation=None,  # by Denton Gentry
                 # by Denton Gentry
                 solution_category=None,

                 # LAND only
                 tco2eq_reduced_per_land_unit=None,
                 tco2eq_rplu_rate=None,
                 tco2_reduced_per_land_unit=None,
                 tco2_rplu_rate=None,
                 tn2o_co2_reduced_per_land_unit=None,
                 tn2o_co2_rplu_rate=None,
                 tch4_co2_reduced_per_land_unit=None,
                 tch4_co2_rplu_rate=None,
                 emissions_use_agg_co2eq=None,

                 seq_rate_global=None,
                 seq_rate_per_regime=None,  # by Denton Gentry
                 degradation_rate=None,
                 disturbance_rate=None,
                 global_multi_for_regrowth=None,
                 soln_expected_lifetime=None,
                 conv_expected_lifetime=None,
                 yield_from_conv_practice=None,
                 yield_gain_from_conv_to_soln=None,
                 use_custom_tla=None,
                 harvest_frequency=None,
                 carbon_not_emitted_after_harvesting=None,

                 delay_protection_1yr=None,
                 delay_regrowth_1yr=None,
                 include_unprotected_land_in_regrowth_calcs=None,  # by Denton Gentry
                 land_annual_emissons_lifetime=None  # by Denton Gentry
                 ):  # by Denton Gentry

        self.vmas = vmas

        self.pds_2014_cost = self._substitute_vma(
            pds_2014_cost, vma_title='SOLUTION First Cost per Implementation Unit')
        self.ref_2014_cost = self._substitute_vma(
            ref_2014_cost, vma_title='SOLUTION First Cost per Implementation Unit')
        self.conv_2014_cost = self._substitute_vma(
            conv_2014_cost,
            vma_title='CONVENTIONAL First Cost per Implementation Unit for replaced practices')  # by Denton Gentry
        self.soln_first_cost_efficiency_rate = soln_first_cost_efficiency_rate  # by Denton Gentry
        self.conv_first_cost_efficiency_rate = conv_first_cost_efficiency_rate  # by Denton Gentry
        self.soln_first_cost_below_conv = soln_first_cost_below_conv  # by Denton Gentry
        self.soln_energy_efficiency_factor = self.value_or_zero(soln_energy_efficiency_factor)  # by Denton Gentry
        self.conv_annual_energy_used = self.value_or_zero(conv_annual_energy_used)  # by Denton Gentry
        self.soln_annual_energy_used = self.value_or_zero(soln_annual_energy_used)  # by Denton Gentry
        self.conv_fuel_consumed_per_funit = self.value_or_zero(conv_fuel_consumed_per_funit)  # by Denton Gentry
        self.soln_fuel_efficiency_factor = self.value_or_zero(soln_fuel_efficiency_factor)  # by Denton Gentry
        self.conv_fuel_emissions_factor = self.value_or_zero(conv_fuel_emissions_factor)  # by Denton Gentry
        self.soln_fuel_emissions_factor = self.value_or_zero(soln_fuel_emissions_factor)  # by Denton Gentry
        self.conv_emissions_per_funit = self.value_or_zero(conv_emissions_per_funit)  # by Denton Gentry
        self.soln_emissions_per_funit = self.value_or_zero(soln_emissions_per_funit)  # by Denton Gentry
        # by Denton Gentry
        self.ch4_is_co2eq = ch4_is_co2eq  # by Denton Gentry
        self.n2o_is_co2eq = n2o_is_co2eq  # by Denton Gentry
        self.co2eq_conversion_source = co2eq_conversion_source  # by Denton Gentry
        if isinstance(co2eq_conversion_source, str):  # by Denton Gentry
            self.co2eq_conversion_source = ef.string_to_conversion_source(co2eq_conversion_source)  # by Denton Gentry
        self.ch4_co2_per_twh = self.value_or_zero(ch4_co2_per_twh)  # by Denton Gentry
        self.n2o_co2_per_twh = self.value_or_zero(n2o_co2_per_twh)  # by Denton Gentry
        self.soln_indirect_co2_per_iunit = soln_indirect_co2_per_iunit  # by Denton Gentry
        self.conv_indirect_co2_per_unit = conv_indirect_co2_per_unit  # by Denton Gentry
        self.conv_indirect_co2_is_iunits = conv_indirect_co2_is_iunits  # by Denton Gentry
        # by Denton Gentry
        self.soln_lifetime_capacity = soln_lifetime_capacity  # by Denton Gentry
        self.soln_avg_annual_use = soln_avg_annual_use  # by Denton Gentry
        self.conv_lifetime_capacity = conv_lifetime_capacity  # by Denton Gentry
        self.conv_avg_annual_use = conv_avg_annual_use  # by Denton Gentry
        self.report_start_year = report_start_year  # by Denton Gentry
        self.report_end_year = report_end_year  # by Denton Gentry
        self.soln_var_oper_cost_per_funit = soln_var_oper_cost_per_funit  # by Denton Gentry
        self.soln_fixed_oper_cost_per_iunit = self._substitute_vma(
            soln_fixed_oper_cost_per_iunit,
            vma_title='SOLUTION Operating Cost per Functional Unit per Annum')
        self.soln_fuel_cost_per_funit = soln_fuel_cost_per_funit  # by Denton Gentry
        self.conv_var_oper_cost_per_funit = conv_var_oper_cost_per_funit  # by Denton Gentry
        self.conv_fixed_oper_cost_per_iunit = self._substitute_vma(
            conv_fixed_oper_cost_per_iunit,
            vma_title='CONVENTIONAL Operating Cost per Functional Unit per Annum')
        self.conv_fuel_cost_per_funit = conv_fuel_cost_per_funit  # by Denton Gentry
        self.npv_discount_rate = npv_discount_rate  # by Denton Gentry
        # by Denton Gentry
        self.emissions_use_co2eq = emissions_use_co2eq  # by Denton Gentry
        self.emissions_grid_source = emissions_grid_source  # by Denton Gentry
        if isinstance(emissions_grid_source, str):  # by Denton Gentry
            self.emissions_grid_source = ef.string_to_emissions_grid_source(emissions_grid_source)  # by Denton Gentry
        self.emissions_grid_range = emissions_grid_range  # by Denton Gentry
        if isinstance(emissions_grid_range, str):  # by Denton Gentry
            self.emissions_grid_range = ef.string_to_emissions_grid_range(emissions_grid_range)  # by Denton Gentry
        # by Denton Gentry
        self.soln_ref_adoption_regional_data = soln_ref_adoption_regional_data  # by Denton Gentry
        self.soln_pds_adoption_regional_data = soln_pds_adoption_regional_data  # by Denton Gentry
        soln_ref_adoption_basis = translate_adoption_bases.get(soln_ref_adoption_basis,  # by Denton Gentry
                                                               soln_ref_adoption_basis)  # by Denton Gentry
        if soln_ref_adoption_basis not in valid_ref_adoption_bases:  # by Denton Gentry
            raise ValueError("invalid adoption basis name=" + str(soln_ref_adoption_basis))  # by Denton Gentry
        self.soln_ref_adoption_basis = soln_ref_adoption_basis  # by Denton Gentry
        self.soln_ref_adoption_custom_name = soln_ref_adoption_custom_name  # by Denton Gentry
        soln_pds_adoption_basis = translate_adoption_bases.get(soln_pds_adoption_basis,  # by Denton Gentry
                                                               soln_pds_adoption_basis)  # by Denton Gentry
        if soln_pds_adoption_basis not in valid_pds_adoption_bases:  # by Denton Gentry
            raise ValueError("invalid adoption basis name=" + str(soln_pds_adoption_basis))  # by Denton Gentry
        self.soln_pds_adoption_basis = soln_pds_adoption_basis  # by Denton Gentry
        self.soln_pds_adoption_prognostication_source = soln_pds_adoption_prognostication_source  # by Denton Gentry
        self.soln_pds_adoption_prognostication_trend = soln_pds_adoption_prognostication_trend  # by Denton Gentry
        if soln_pds_adoption_prognostication_growth not in valid_adoption_growth:  # by Denton Gentry
            g = soln_pds_adoption_prognostication_growth  # by Denton Gentry
            raise ValueError("invalid adoption prognostication growth name=" + str(g))  # by Denton Gentry
        self.soln_pds_adoption_prognostication_growth = soln_pds_adoption_prognostication_growth  # by Denton Gentry
        self.soln_pds_adoption_custom_name = soln_pds_adoption_custom_name  # by Denton Gentry
        self.pds_source_post_2014 = pds_source_post_2014  # by Denton Gentry
        self.ref_source_post_2014 = ref_source_post_2014  # by Denton Gentry
        self.source_until_2014 = source_until_2014  # by Denton Gentry
        # by Denton Gentry
        self.ref_adoption_use_pds_years = set() if ref_adoption_use_pds_years is None else ref_adoption_use_pds_years
        self.pds_adoption_use_ref_years = set() if pds_adoption_use_ref_years is None else pds_adoption_use_ref_years
        intersect = set(self.ref_adoption_use_pds_years) & set(self.pds_adoption_use_ref_years)
        if intersect:  # by Denton Gentry
            err = "cannot be in both ref_adoption_use_pds_years and pds_adoption_use_ref_years:" + str(
                intersect)  # by Denton Gentry
            raise ValueError(err)  # by Denton Gentry
        self.pds_base_adoption = pds_base_adoption  # by Denton Gentry
        self.pds_adoption_final_percentage = pds_adoption_final_percentage  # by Denton Gentry
        self.pds_adoption_s_curve_innovation = pds_adoption_s_curve_innovation  # by Denton Gentry
        self.pds_adoption_s_curve_imitation = pds_adoption_s_curve_imitation  # by Denton Gentry
        # by Denton Gentry
        self.solution_category = solution_category  # by Denton Gentry
        if isinstance(solution_category, str):  # by Denton Gentry
            self.solution_category = self.string_to_solution_category(solution_category)  # by Denton Gentry
        # by Denton Gentry
        # LAND only
        self.tco2eq_reduced_per_land_unit = self._substitute_vma(tco2eq_reduced_per_land_unit,
                                                                 vma_title='t CO2-eq (Aggregate emissions) Reduced per Land Unit')
        self.tco2eq_rplu_rate = tco2eq_rplu_rate
        self.tco2_reduced_per_land_unit = self._substitute_vma(tco2_reduced_per_land_unit,
                                                               vma_title='t CO2 Reduced per Land Unit')
        self.tco2_rplu_rate = tco2_rplu_rate
        self.tn2o_co2_reduced_per_land_unit = self._substitute_vma(tn2o_co2_reduced_per_land_unit,
                                                                   vma_title='t N2O-CO2-eq Reduced per Land Unit')
        self.tn2o_co2_rplu_rate = tn2o_co2_rplu_rate
        self.tch4_co2_reduced_per_land_unit = self._substitute_vma(tch4_co2_reduced_per_land_unit,
                                                                   vma_title='t CH4-CO2-eq Reduced per Land Unit')
        self.tch4_co2_rplu_rate = tch4_co2_rplu_rate
        self.emissions_use_agg_co2eq = emissions_use_agg_co2eq

        self.seq_rate_global = self._substitute_vma(seq_rate_global, vma_title='Sequestration Rates')
        self.seq_rate_per_regime = seq_rate_per_regime  # by Denton Gentry
        self.degradation_rate = self._substitute_vma(degradation_rate,
                                                     vma_title='Growth Rate of Land Degradation')
        self.disturbance_rate = self._substitute_vma(disturbance_rate, vma_title='Disturbance Rate')
        self.global_multi_for_regrowth = global_multi_for_regrowth
        self.soln_expected_lifetime = soln_expected_lifetime
        self.conv_expected_lifetime = conv_expected_lifetime
        self.yield_from_conv_practice = self._substitute_vma(yield_from_conv_practice,
                                                             vma_title='Yield  from CONVENTIONAL Practice')
        self.yield_gain_from_conv_to_soln = self._substitute_vma(yield_gain_from_conv_to_soln,
                                                                 vma_title='Yield Gain (% Increase from CONVENTIONAL to SOLUTION)')
        self.use_custom_tla = use_custom_tla
        self.harvest_frequency = harvest_frequency
        self.carbon_not_emitted_after_harvesting = self._substitute_vma(carbon_not_emitted_after_harvesting,

                                                                        vma_title='Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing')

        self.delay_protection_1yr = delay_protection_1yr
        self.delay_regrowth_1yr = delay_regrowth_1yr
        self.include_unprotected_land_in_regrowth_calcs = include_unprotected_land_in_regrowth_calcs
        self.land_annual_emissons_lifetime = land_annual_emissons_lifetime  # by Denton Gentry

    def value_or_zero(self, val):  # by Denton Gentry
        """Allow a blank space or empty string to mean zero.  # by Denton Gentry
           Useful for advanced controls like conv_average_electricity_used."""  # by Denton Gentry
        try:  # by Denton Gentry
            return float(val)  # by Denton Gentry
        except (ValueError, TypeError):  # by Denton Gentry
            return 0.0  # by Denton Gentry

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

    @property  # by Denton Gentry
    def soln_first_cost_learning_rate(self):  # by Denton Gentry
        return 1.0 - self.soln_first_cost_efficiency_rate  # by Denton Gentry

    # by Denton Gentry
    @property  # by Denton Gentry
    def conv_first_cost_learning_rate(self):  # by Denton Gentry
        return 1.0 - self.conv_first_cost_efficiency_rate  # by Denton Gentry

    # by Denton Gentry
    @property  # by Denton Gentry
    def soln_fuel_learning_rate(self):  # by Denton Gentry
        return 1.0 - self.soln_fuel_efficiency_factor  # by Denton Gentry

    # by Denton Gentry
    @property  # by Denton Gentry
    def soln_lifetime_replacement(self):  # by Denton Gentry
        if self.soln_lifetime_capacity is not None:  # RRS
            return self.soln_lifetime_capacity / self.soln_avg_annual_use
        elif self.soln_expected_lifetime is not None:  # LAND
            return self.soln_expected_lifetime
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for solution')

    # by Denton Gentry
    @property  # by Denton Gentry
    def soln_lifetime_replacement_rounded(self):  # by Denton Gentry
        if self.soln_lifetime_capacity is not None:  # RRS
            # ROUND and decimal.quantize do not match Excel ROUND(), so we implemented one.  # by Denton Gentry
            return excel_math.round(self.soln_lifetime_capacity / self.soln_avg_annual_use)  # by Denton Gentry
        elif self.soln_expected_lifetime is not None:  # LAND
            # LAND models input lifetime directly so I doubt we will come across rounding errors
            # i.e. expected_lifetime will probably be a whole number of years.
            # Integration test will catch the case where this assumption is wrong
            return int(self.soln_expected_lifetime)
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for solution')

    # by Denton Gentry
    @property  # by Denton Gentry
    def conv_lifetime_replacement(self):  # by Denton Gentry
        if self.conv_lifetime_capacity is not None:  # RRS
            return self.conv_lifetime_capacity / self.conv_avg_annual_use
        elif self.conv_expected_lifetime is not None:  # LAND
            return self.conv_expected_lifetime
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for conventional')

    # by Denton Gentry
    @property  # by Denton Gentry
    def conv_lifetime_replacement_rounded(self):  # by Denton Gentry
        if self.conv_lifetime_capacity is not None:  # RRS
            # ROUND and decimal.quantize do not match Excel ROUND(), so we implemented one.  # by Denton Gentry
            return excel_math.round(self.conv_lifetime_capacity / self.conv_avg_annual_use)  # by Denton Gentry
        elif self.conv_expected_lifetime is not None:  # LAND
            # LAND models input lifetime directly so I doubt we will come across rounding errors
            # i.e. expected_lifetime will probably be a whole number of years
            # Integration test will catch the case where this assumption is wrong
            return int(self.conv_expected_lifetime)
        else:
            raise ValueError(
                'Must input either lifetime capacity (RRS) or expected lifetime (LAND) for conventional')

    # by Denton Gentry
    def string_to_solution_category(self, text):  # by Denton Gentry
        ltext = str(text).lower()  # by Denton Gentry
        if ltext == "replacement":  # by Denton Gentry
            return SOLUTION_CATEGORY.REPLACEMENT  # by Denton Gentry
        elif ltext == "reduction":
            return SOLUTION_CATEGORY.REDUCTION  # by Denton Gentry
        elif ltext == 'land':
            return SOLUTION_CATEGORY.LAND
        elif ltext == "not_applicable" or ltext == "not applicable" or ltext == "na":
            return SOLUTION_CATEGORY.NOT_APPLICABLE  # by Denton Gentry
        raise ValueError("invalid solution category: " + str(text))  # by Denton Gentry

    def _substitute_vma(self, val, vma_title):
        """
        If val is 'mean', 'high' or 'low', returns the corresponding statistic from the VMA object in
        self.vmas with the corresponding title.
        Args:
          val: input can be a number, a string ('mean', 'high' or 'low') or a dict containing a 'value' key
          vma_title: title of VMA table (can be found in vma_info.csv in the soln dir)
        Returns:
            mean, high or low value from VMA table or passes through value if it's a number or dict
        """
        raw_val_from_excel = None  # the raw value from the scenario record tab
        if isinstance(val, str):
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
            if vma_key.startswith(
                vma_title):  # This handles the case of 'first cost' title discrepancies
                vma_title = vma_key
                break
        else:
            raise KeyError(
                '{} must be included in vmas to calculate mean/high/low. vmas included: {}'.format(vma_title,
                                                                                                   self.vmas.keys()))
        result = self.vmas[vma_title].avg_high_low(key=stat.lower())
        if raw_val_from_excel is not None and result != approx(raw_val_from_excel):
            warn(
                "raw value from scenario record tab in excel does not match the {0} of VMA table '{1}'. \nThis is probably "
                "because the scenario was linked to the {0} of an older version of the table.".format(stat,
                                                                                                      vma_title))
            result = raw_val_from_excel
        return result
