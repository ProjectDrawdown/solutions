"""Integrate building solutions.

In total 14 solutions are part of building integration. They belong to five
different categories: space heating, space cooling, lighting, cooking and
water heating. Their effects are at three different levels: Building envelope,
systems or appliances. The 14 solutions are:
Insulation - insulation - Space heating/cooling - Building envelope
    Insulation is the first solution to be integrated in the heating/cooling
    chain. It is only adopted for residential floor area. Its adoption affects
    all other heating/cooling integrations but no adjustments are made to its
    own impact.
Cool Roofs - coolroofs - Space heating/cooling - Building envelope
    Cool Roofs is the second solution in the heating/cooling chain. It is
    integrated with respect to insulation. The extent to which insulation
    is adopted lowers the electricity saved by cool roofs and lowers its
    heating/cooling efficiency factor.
Green Roofs - greenroofs - Space heating/cooling - Building envelope
    Same idea as for cool roofs.
High Perf. Glass - residentialglass/commercialglass - Space heating/cooling - Building envelope
    Only residential high performance glass needs to be integrated with
    respect to insulation because insulation is only modeled for residential
    floor area. The extent to which insulation is adopted lowers the electricity
    saved by high performance glass and lower the fuel inputs efficiency.
Dynamic Glass - smartglass - Space cooling/lighting - Building envelope
    Dynamic glass also appears as smart glass in the original excel sheet.
    Dynamic glass is only modeled for commercial buildings and is therefore
    not integrated with insulation. It is also not integrated with high
    performance glass. However, it needs to be integrated with commercial
    LED adoption in the lighting chain.
Building Automation - buildingautomation - Space heating/cooling/lighting - Systems
    Building automatin is only for commercial buildings.
    Building automation is among the more complicated integrations, because it
    is integrated both inthe heating/cooling chain as well as the lighting chain.
    In the heating/cooling chain the overlap is calculated for cool roof,
    green roof, high perf. glass and dynamic glass. For each year, the maximum
    overlap of these solutions is chosen. In the lighting chain, the maximum from
    commercial LED and dynamic glass. 
Smart thermostats - smartthermostats - space heating/cooling - Systems
    Smart thermostats is residential only. It is integrated with respect to the
    maximum in each year from insulation, cool roof, green roof or high performance
    residential glass.
District heating - districtheating - Space heating - Systems
    District heating is not integrated.
Heat pumps - heatpumps - Space heating - Appliances
    Heat pumps are not integrated.
LED - leds_commercial/leds_residential - Lighting - Appliances
    LED lighting for commercial and residential space. This is the first step in the
    lighting chain and is therefore not itself integrated.
Cooking biogas - biogas - Cooking - Appliances
    Not integrated here but TAM-limited by the amount of available waste elsewhere.
Clean cookstoves - improvedcookstoves - Cooking - Appliances
    Integrated elsewhere.
Water saving home (WaSH) - waterefficiency - Water heating - Appliances
    Not integrated here
Solar hot water - solarhotwater - Water heating - Appliances
    Not integrated here.
"""

from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from model import integration
from integration_base import *
from solution import factory
import pdb

THISDIR = Path(__file__).parent
DATADIR = THISDIR/"data"/"building"

audit = start_audit("building")

building_solutions = {
    "Insulation (Residential Only)": "insulation",
    "Cool Roofs": "coolroofs",
    "Green Roofs": "greenroofs",
    "High Performance Glass-Residential Model": "residentialglass",
    "High Performance Glass- Commercial Model": "commercialglass",
    "Dynamic Glass (Commercial Only)": "smartglass",
    "Building Automation (Commercial Only)": "buildingautomation",
    "Smart Thermostats (Residential Only)": "smartthermostats",
    "Heat Pumps": "heatpumps",
    "District Heat": "districtheating",
    "Residential LED (Excludes Commercial LED)": "leds_residential",
    "Commercial LED (Excludes Household LED)": "leds_commercial",
    "Water Saving - Home (WaSH)": "waterefficiency",
    "Solar Hot Water (SHW)": "solarhotwater",
    "Biogas for Cooking": "biogas",
    "Clean Cookstoves":  "improvedcookstoves"
    }

building_solutions_needed = {
    "Insulation (Residential Only)": "insulation",
    "Cool Roofs": "coolroofs",
    "Green Roofs": "greenroofs",
    "High Performance Glass-Residential Model": "residentialglass",
    "High Performance Glass- Commercial Model": "commercialglass",
    "Dynamic Glass (Commercial Only)": "smartglass",
    "Building Automation (Commercial Only)": "buildingautomation",
    "Smart Thermostats (Residential Only)": "smartthermostats",
    "Residential LED (Excludes Commercial LED)": "leds_residential",
    "Commercial LED (Excludes Household LED)": "leds_commercial",
    }

# Load adoption data from solutions
@dataclass
class building_integration_state:
    # This data class holds global variables that are shared between steps.  Embedding it in a class
    # enables us to avoid having to declare 'global' anytime we want to change something.

    # In testmode, test data is loaded to check against calculations.
    # Turning testmode off reduces load time


    # All solutions that take part in the building integration
    # Key is the full name from excel sheet, value is the name in Python repo

    pds : str = 'pds1'
    cooking_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"cooking_global_tam.csv", index_col="year", squeeze=False)
    floor_area_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"floor_area_global_tam.csv", index_col="year", squeeze=False)
    households_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"households_global_tam.csv", index_col="year", squeeze=False)
    lighting_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"lighting_global_tam.csv", index_col="year", squeeze=False)
    roof_area_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"roof_area_global_tam.csv", index_col="year", squeeze=False)
    space_cooling_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"space_cooling_global_tam.csv", index_col="year", squeeze=False)
    space_heating_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"space_heating_global_tam.csv", index_col="year", squeeze=False)
    water_heating_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"water_heating_global_tam.csv", index_col="year", squeeze=False)

    testmode = False
    adoption_dict = {}
    for key, value in building_solutions_needed.items():
        adoption_dict[key] = load_solution_adoptions(value)[pds.upper()]
    adoption : pd.DataFrame = pd.DataFrame(data=adoption_dict)

    # Load test data
    if testmode:
        adoption_test : pd.DataFrame = pd.read_csv(DATADIR/f"adoption_{pds}.csv", index_col="year", squeeze=False)
        fuel_avoided_test : pd.DataFrame = pd.read_csv(DATADIR/f"fuel_avoided_{pds}.csv", index_col="year", squeeze=False)
        net_grid_electricity_test : pd.DataFrame = pd.read_csv(DATADIR/f"net_grid_electricity_{pds}.csv", index_col="year", squeeze=False)

    TWh_to_EJ : float = 3.6e-3
    EJ_to_TWh : float = 1/TWh_to_EJ
    TJ_to_EJ : float = 1e-6
    TJ_to_TWh : float = 1/3600

# ds = building_integration_state()

test_adoption = False
if test_adoption:
    # ds.adoption = ds.adoption_test
    pass

def integrate():
    """Perform all steps of the integration together."""
    for pds in ['pds1', 'pds2', 'pds3']:
        print(pds)
        ds = building_integration_state(pds=pds)
        cool_roofs_integration(ds)
        green_roofs_integration(ds)
        high_performance_glass_residential_integration(ds)
        dynamic_glass_integration(ds)
        building_automation_integration_lighting(ds)  # Each of the building integrations accoutns for both heating and lighting
        smart_thermostat_integration(ds)

def insulation_integration(ds):
    """Step 1 in integration chain. Calculate the total energy saved and split
    saved energy into cooling and heating usage. Result does not affect other
    integration steps.
    
    Columns in Excel
    ----------------
    Adoption - Million m2 of Res Floor Area
        Copy pasted from the solution.
    Net Grid Electricity - TWh
        Copy pasted from the solution.
    Fuel Avoided - TJ
        Copy pasted from the solution.
    Total FINAL Energy Saved - EJ
        Calculated from the avoided fuel and the grid electricity used.
    Space Heating FINAL energy Saved - EJ
        Calculated from Total FINAL Energy Saved and several conversion factors.
    Space Cooling FINAL energy Saved - EJ
        Calculated from Total FINAL Energy Saved and several conversion factors.
    """
    insulation = factory.load_scenario('insulation')

    return insulation.total_energy_saving()

def cool_roofs_integration(ds):
    """Step 2. Cool roofs calculation.
    
    Columns in Excel
    ----------------
    Adoption - Residential and Commercial roof area, m2
        Copy pasted from solution.
    Estimated Adoption Overlap with Insulation - Residential and Commercial roof area, m2
        Calculated based on Insulation adoption, Cool Roofs adoption, TAM Roof Area & TAM Floor Area.
    Electricity Consumption - TWh/m2 INTEGRATION PARAMETER
        This is a scalar paramter that is integrated. Integration is based on the pre-integration value,
        the adoption and the adoption overlap with insulation. 
    Thermal/Cooling Efficiency Factor - Percentage INTEGRATION PARAMETER
        This is a scalar parameter that is integrated.  Integration is based on the pre-integration value,
        the adoption and the adoption overlap with insulation
    INTEGRATION STEP
        Post-integration values from Electricity Consumption and Thermal/Cooling Efficiency Factor are inserted
        into the solution excel sheet. The resulting calculations of Net Grid Electricity Used and Fuel Avoided
        are copy pasted from the solution sheet to the integration sheet.
    Net Grid Electricity Used - TWh POST INTEGRATION
        Net grid electricity used after integration of Electricity consumption and Thermal/Cooling Efficiency
    Fuel Avoided - TJ POST INTEGRATION
        Fueld avoided after integration of Electricity consumption and Themrla/Cooling Efficiency
    Net EJ Reduction from Cool Roofs - EJ
        Calculated from Net Grid Electricity Used and Fuel Avoided.

    - Load scenario through the factory.
    - Get it's .ac as a dictionary
    - Change values to post-integration values
    - load scenario again through factory passing the changed dictionary as second argument

    Audit saves things in an audit log. 
    """
    coolroofs = factory.load_scenario('coolroofs', ds.pds.upper())
    insulation_overlap = (ds.adoption['Cool Roofs'] * ds.roof_area_global_tam['Roof Area - Residential - Case 1 - Average'] /
                                     ds.roof_area_global_tam['Roof Area - Total - Case 1 - Average'] * ds.adoption['Insulation (Residential Only)']  /
                                     ds.floor_area_global_tam['Residential - Average'])

    # Hardcoded into the integration excel sheet
    insulation_reduces_cool_roofs_heating_penalty = 0.75
    insulation_reduces_cool_roofs_electricity_impact = 0.5

    avg_reduction_fuel_impact = ((insulation_overlap.loc[2020:2050] / ds.adoption['Cool Roofs'].loc[2020:2050]).mean() * 
                                            insulation_reduces_cool_roofs_heating_penalty)
    avg_reduction_electricity_impact = ((insulation_overlap.loc[2020:2050] / ds.adoption['Cool Roofs'].loc[2020:2050]).mean() * 
                                        insulation_reduces_cool_roofs_electricity_impact)

    thermal_efficiency_factor = coolroofs.ac.soln_energy_efficiency_factor
    electricity_consumption_conventional = coolroofs.ac.conv_annual_energy_used
    electricity_consumption_pre_integration = coolroofs.ac.soln_annual_energy_used

    electricity_consumption_integrated = coolroofs.ac.conv_annual_energy_used

    thermal_efficiency_factor_integrated = thermal_efficiency_factor * (1-avg_reduction_fuel_impact)

    electricity_consumption_post_integration = (electricity_consumption_conventional -
        (electricity_consumption_conventional - electricity_consumption_pre_integration)*
        (1-avg_reduction_electricity_impact))

    """
    ac_integrated = coolroofs.ac.with_modifications(soln_annual_energy_used=electricity_consumption_post_integration,
                                                    soln_fuel_efficiency_factor=thermal_efficiency_factor_integrated)
    """

    # Integrate coolroofs
    # This also writes the new ac disk in solution directory
    coolroofs.update_ac(coolroofs.ac,
                        soln_annual_energy_used=electricity_consumption_post_integration,
                        soln_fuel_efficiency_factor=thermal_efficiency_factor_integrated)

    return coolroofs.total_energy_saving()

def green_roofs_integration(ds):
    """Step 3. Green roofs calculation
    
    Columns in Excel
    ----------------
    Adoption - Residential and Commercial roof area, m2
        Copy pasted from solution.
    Estimated Adoption Overlap with Insulation - Residential and Commercial roof area, m2
        Calculated based on Insulation adoption, Cool Roofs adoption, TAM Roof Area & TAM Floor Area.
    Electricity Consumption - TWh/m2 INTEGRATION PARAMETER
        This is a scalar paramter that is integrated. Integration is based on the pre-integration value,
        the adoption and the adoption overlap with insulation. 
    Thermal/Cooling Efficiency Factor - Percentage INTEGRATION PARAMETER
        This is a scalar parameter that is integrated.  Integration is based on the pre-integration value,
        the adoption and the adoption overlap with insulation
    INTEGRATION STEP
        Post-integration values from Electricity Consumption and Thermal/Cooling Efficiency Factor are inserted
        into the solution excel sheet. The resulting calculations of Net Grid Electricity Used and Fuel Avoided
        are copy pasted from the solution sheet to the integration sheet.
    Net Grid Electricity Used - TWh POST INTEGRATION
        Net grid electricity used after integration of Electricity consumption and Thermal/Cooling Efficiency
    Fuel Avoided - TJ POST INTEGRATION
        Fueld avoided after integration of Electricity consumption and Themrla/Cooling Efficiency
    Net EJ Reduction from Cool Roofs - EJ
        Calculated from Net Grid Electricity Used and Fuel Avoided.

    - Load scenario through the factory.
    - Get it's .ac as a dictionary
    - Change values to post-integration values
    - load scenario again through factory passing the changed dictionary as second argument

    Audit saves things in an audit log. 
    """

    greenroofs = factory.load_scenario('greenroofs', ds.pds.upper())
    insulation_overlap = (ds.adoption['Green Roofs'] * ds.roof_area_global_tam['Roof Area - Residential - Case 1 - Average'] /
                                     ds.roof_area_global_tam['Roof Area - Total - Case 1 - Average'] * ds.adoption['Insulation (Residential Only)']  /
                                     ds.floor_area_global_tam['Residential - Average'])

    # Hardcoded into the integration excel sheet
    insulation_reduces_green_roofs_heating_penalty = 0.5
    insulation_reduces_green_roofs_electricity_impact = 0.5

    avg_reduction_fuel_impact = ((insulation_overlap.loc[2020:2050] / ds.adoption['Green Roofs'].loc[2020:2050]).mean() * 
                                            insulation_reduces_green_roofs_heating_penalty)
    avg_reduction_electricity_impact = ((insulation_overlap.loc[2020:2050] / ds.adoption['Green Roofs'].loc[2020:2050]).mean() * 
                                        insulation_reduces_green_roofs_electricity_impact)

    # TODO These are hardcoded for now but should be taken from solution.ac at some point
    # Currently the numbers we have in Python are clearly outdated though
    thermal_efficiency_factor = greenroofs.ac.soln_energy_efficiency_factor
    electricity_consumption_conventional = greenroofs.ac.conv_annual_energy_used
    electricity_consumption_pre_integration = greenroofs.ac.soln_annual_energy_used

    electricity_consumption_integrated = greenroofs.ac.conv_annual_energy_used

    thermal_efficiency_factor_integrated = thermal_efficiency_factor * (1-avg_reduction_fuel_impact)

    electricity_consumption_post_integration = (electricity_consumption_conventional -
        (electricity_consumption_conventional - electricity_consumption_pre_integration)*
        (1-avg_reduction_electricity_impact))

    # Integrate greenroofs
    greenroofs.update_ac(greenroofs.ac,
                        soln_annual_energy_used=electricity_consumption_post_integration,
                        soln_fuel_efficiency_factor=thermal_efficiency_factor_integrated)


    return greenroofs.total_energy_saving()

def high_performance_glass_residential_integration(ds):
    """Step 4. Combines calculation for residential and commercial high performance
    glass. """
    residentialglass = factory.load_scenario('residentialglass', ds.pds.upper())
    
    insulation_overlap = ds.adoption['Insulation (Residential Only)'] / ds.floor_area_global_tam['Residential - Average'] * ds.adoption["High Performance Glass-Residential Model"] 

    insulation_reduces_glass_electricity_impact = 0.5
    insulation_reduces_glass_fuel_impact = 0.5

    average_reduction_electricity_efficiency = ((insulation_overlap.loc[2020:2050] / ds.adoption["High Performance Glass-Residential Model"].loc[2020:2050]).mean() * 
                                        insulation_reduces_glass_electricity_impact)

    average_reduction_fuel_efficiency = ((insulation_overlap.loc[2020:2050] / ds.adoption["High Performance Glass-Residential Model"].loc[2020:2050]).mean() * 
                                        insulation_reduces_glass_fuel_impact)

    fuel_inputs_conv = residentialglass.ac.conv_fuel_consumed_per_funit
    fuel_inputs_soln_efficiency = residentialglass.ac.soln_fuel_efficiency_factor
    thermal_efficiency_factor = residentialglass.ac.soln_energy_efficiency_factor
    electricity_consumption_conventional = residentialglass.ac.conv_annual_energy_used
    electricity_consumption_pre_integration = residentialglass.ac.soln_annual_energy_used

    # goes to total_energy_used_per_functional_unit solution
    electricity_inputs_integrated = (electricity_consumption_conventional -
        (electricity_consumption_conventional - electricity_consumption_pre_integration)*
        (1-average_reduction_electricity_efficiency))

    # goes to fuel_inputs_soln_efficiency
    fuel_inputs_integrated = fuel_inputs_soln_efficiency * (1 - average_reduction_fuel_efficiency)

    # pdb.set_trace()

    residentialglass.update_ac(residentialglass.ac,
                    soln_annual_energy_used=electricity_inputs_integrated,
                    soln_fuel_efficiency_factor=fuel_inputs_integrated)

    return residentialglass.total_energy_saving()

def high_performance_glass_commercial_integration(ds):
    """No integration needed because insulation is defined only for residential buildings."""
    smartglass = factory.load_scenario('smartglass', ds.pds.upper())
    return smartglass.total_energy_saving()

def led_residential_integration(ds):
    """Step 5. LED integration."""
    leds_residential = factory.load_scenario('leds_residential', ds.pds.upper())

    return leds_residential.soln_net_energy_grid_impact() * ds.TWh_to_EJ

def led_commercial_integration(ds):
    """Step 5. LED integration."""
    leds_commercial = factory.load_scenario('leds_commercial', ds.pds.upper())

    return leds_commercial.soln_net_energy_grid_impact() * ds.TWh_to_EJ

def dynamic_glass_integration(ds):
    """Step 6. Dynamic glass integration. Depends on both high performance glass
    and LED. Commercial only."""

    smartglass = factory.load_scenario('smartglass', ds.pds.upper())

    adoption_overlap = (
        ds.adoption['Commercial LED (Excludes Household LED)'] / 
        ds.lighting_global_tam['Lighting Demand - Commercial - Case 1 - Average'] * 
        ds.adoption['Dynamic Glass (Commercial Only)'])

    electricity_consumption_conventional = smartglass.ac.conv_annual_energy_used
    electricity_consumption_solution = smartglass.ac.soln_annual_energy_used

    electricity_end_use_shares_heating_cooling = 0.293
    electricity_end_use_shares_lighting = 0.236

    # This one should depend on smart glass integration with respect to insulation
    # Is 0 because insulation is residential and smartglass is commercial.
    average_reduction_electricity_efficiency_insulation = 0.0

    led_reduces_smart_glass_electricity_impact = 0.5

    average_reduction_electricity_efficiency_led_commercial = (
        (adoption_overlap.loc[2020:2050] / ds.adoption["Dynamic Glass (Commercial Only)"].loc[2020:2050]).mean() * 
        led_reduces_smart_glass_electricity_impact
        )

    electricity_consumption_integrated = (
        electricity_consumption_conventional -
        (electricity_consumption_conventional - electricity_consumption_solution) *
        (
            (1 - electricity_end_use_shares_heating_cooling - electricity_end_use_shares_lighting) +
            electricity_end_use_shares_heating_cooling * 
            (1 - average_reduction_electricity_efficiency_insulation) +
            electricity_end_use_shares_lighting * (1 - average_reduction_electricity_efficiency_led_commercial)
        )
    )

    return smartglass.total_energy_saving()

def building_automation_integration(ds):
    """Step 7. Building automation. Depends on dynamic glass."""

    buildingautomation = factory.load_scenario('buildingautomation', ds.pds.upper())

    numstories_comm = 1.58

    possible_overlap = ((ds.adoption['Cool Roofs'] + ds.adoption['Green Roofs']) / 1e6 * 
        ds.roof_area_global_tam['Roof Area - Residential - Case 1 - Average'] / ds.roof_area_global_tam['Roof Area - Residential - Case 1 - Average'] * numstories_comm
        )
    columns_max = pd.DataFrame({'col1':possible_overlap, 
                                'col2': ds.adoption['High Performance Glass- Commercial Model'],
                                'col3': ds.adoption['Insulation (Residential Only)']}).max(axis=1)
    adoption_overlap = columns_max / ds.floor_area_global_tam['Residential - Average'] * ds.adoption['Building Automation (Commercial Only)']

    roof_glass_electricity_impact = 0.5
    roof_glass_fuel_impact = 0.5

    average_change_heating_electricity_efficiency = (
        (adoption_overlap.loc[2020:2050] / ds.adoption['Building Automation (Commercial Only)'].loc[2020:2050]).mean() * 
        roof_glass_electricity_impact
        )

    average_change_fuel_efficiency = (
        (adoption_overlap.loc[2020:2050] / ds.adoption['Building Automation (Commercial Only)'].loc[2020:2050]).mean() * 
        roof_glass_fuel_impact)

    fuel_efficiency_factor = buildingautomation.ac.soln_fuel_efficiency_factor
    electrical_efficiency_factor = buildingautomation.ac.soln_energy_efficiency_factor

    # TODO Locate these in the sollutions!
    electricity_end_use_shares_heating_cooling = 0.296
    electricity_end_use_shares_lighting = 0.236
    lighting_energy_impact = 0.326

    electrical_efficiency_factor_integrated = (
        electrical_efficiency_factor * ((1 - electricity_end_use_shares_heating_cooling - electricity_end_use_shares_lighting)) + 
        electricity_end_use_shares_heating_cooling * (1 - average_change_heating_electricity_efficiency) + 
        electricity_end_use_shares_lighting * (1 - lighting_energy_impact)
    )

    fuel_efficiency_factor_integrated = fuel_efficiency_factor * (1 - average_change_fuel_efficiency)

    buildingautomation.update_ac(buildingautomation.ac,
                soln_fuel_efficiency_factor=fuel_efficiency_factor_integrated,
                soln_energy_efficiency_factor=electrical_efficiency_factor_integrated)

    # TODO take care of the sign change in net_impact!
    return buildingautomation.total_energy_saving()

def smart_thermostat_integration(ds):
    """Step 8. Smart thermostat. Depends on building automation"""
    # =MAX($L6,($U6+$AE6)/10^6*TAM_RoofArea!$C21/TAM_RoofArea!$O21*NumStories_RES,$AR6)/TAM_Area!$J33*AI62
    # =MAX(($U6+$AE6)/10^6*TAM_RoofArea!$I21/TAM_RoofArea!$O21*NumStories_Comm,$BB6,$L62)/TAM_Area!$R33*Y62

    smartthermostats = factory.load_scenario('smartthermostats', ds.pds.upper())

    numstories_res = 1.58

    possible_overlap = ((ds.adoption['Cool Roofs'] + ds.adoption['Green Roofs']) / 1e6 * 
        ds.roof_area_global_tam['Roof Area - Residential - Case 1 - Average'] / ds.roof_area_global_tam['Roof Area - Residential - Case 1 - Average'] * numstories_res
        )

    columns_max = pd.DataFrame({'col1':possible_overlap, 
                                'col2': ds.adoption['High Performance Glass- Commercial Model'],
                                'col3': ds.adoption['Insulation (Residential Only)']}).max(axis=1)

    adoption_overlap = columns_max / ds.floor_area_global_tam['Residential - Average'] * ds.adoption['Smart Thermostats (Residential Only)']

    roof_glass_electricity_impact = 0.5
    roof_glass_fuel_impact = 0.5

    average_change_electricity_efficiency = (
        (adoption_overlap.loc[2020:2050] / ds.adoption['Smart Thermostats (Residential Only)'].loc[2020:2050]).mean() * 
        roof_glass_electricity_impact
        )

    average_change_fuel_efficiency = (
        (adoption_overlap.loc[2020:2050] / ds.adoption['Smart Thermostats (Residential Only)'].loc[2020:2050]).mean() * 
        roof_glass_fuel_impact)

    fuel_efficiency_factor = smartthermostats.ac.soln_fuel_efficiency_factor
    electrical_efficiency_factor = smartthermostats.ac.soln_energy_efficiency_factor

    electrical_efficiency_factor_integrated = (
        electrical_efficiency_factor * (1 - average_change_electricity_efficiency)
        )

    fuel_efficiency_factor_integrated = fuel_efficiency_factor * (1 - average_change_fuel_efficiency)

    smartthermostats.update_ac(smartthermostats.ac,
                soln_fuel_efficiency_factor=fuel_efficiency_factor_integrated,
                soln_energy_efficiency_factor=electrical_efficiency_factor_integrated)
    
    return smartthermostats.total_energy_saving()

def heat_pumps_integration(ds):
    """Step 9. Heat pumpts. Depends on smart thermostat."""
    heatpumps = factory.load_scenario('heatpumps', ds.pds.upper())

    return heatpumps.total_energy_saving()

def district_heating_integration(ds):
    """Step 10. District heating. Depends on heat pumps."""
    districtheating = factory.load_scenario('districtheating', ds.pds.upper())

    return districtheating.total_energy_saving()

def building_automation_integration_lighting(ds):
    buildingautomation = factory.load_scenario('buildingautomation', ds.pds.upper())

    lighting = ds.adoption['Commercial LED (Excludes Household LED)'] / ds.lighting_global_tam['Lighting Demand - Commercial - Case 1 - Average']

    glass = ds.adoption['Dynamic Glass (Commercial Only)'] / ds.floor_area_global_tam['Commercial - Average']

    columns_max = pd.DataFrame({'col1':lighting, 
                            'col2': glass}).max(axis=1)

    overlap = columns_max * ds.adoption['Building Automation (Commercial Only)']

    commercial_led_and_glass_reduce_bas_electricity_impact = 0.5

    average_reduction_lighting_electrical_efficiency = (
        (overlap.loc[2020:2050] / ds.adoption["Building Automation (Commercial Only)"].loc[2020:2050]).mean() * 
        commercial_led_and_glass_reduce_bas_electricity_impact
        )

    electricity_end_use_shares_heating_cooling = 0.296
    electricity_end_use_shares_lighting = 0.236

    roof_glass_electricity_impact = 0.5

    average_change_heating_electricity_efficiency = (
        (overlap.loc[2020:2050] / ds.adoption['Building Automation (Commercial Only)'].loc[2020:2050]).mean() * 
        roof_glass_electricity_impact
        )

    electrical_efficiency_factor = buildingautomation.ac.soln_energy_efficiency_factor

    electrical_efficiency_factor_integrated = (
        electrical_efficiency_factor * (
            (1 - electricity_end_use_shares_heating_cooling - electricity_end_use_shares_lighting) +
            electricity_end_use_shares_heating_cooling * (
                1 - average_change_heating_electricity_efficiency
            ) +
            electricity_end_use_shares_lighting * (
                1 - average_reduction_lighting_electrical_efficiency
            )
        )
    )

    buildingautomation.update_ac(buildingautomation.ac,
            soln_energy_efficiency_factor=electrical_efficiency_factor_integrated)
    
    return buildingautomation.total_energy_saving()

def water_saving_home(ds):
    waterefficiency = factory.load_scenario('waterefficiency', ds.pds.upper())
    return waterefficiency.total_energy_saving()

def solar_hw_integration(ds):
    """Step 14. Solar HW. Depends on low flow fixtures."""
    solarhotwater = factory.load_scenario('solarhotwater', ds.pds.upper())
    return solarhotwater.total_energy_saving()

def cooking_biogas_integration(ds):
    """Step 11. Cooking biogas. No upstream dependency."""
    biogas = factory.load_scenario('biogas', ds.pds.upper())
    return biogas.total_energy_saving()

def clean_stoves_integration(ds):
    """Step 12. Clean stoves. Depends on cooking biogas."""
    
    improvedcookstoves = factory.load_scenario('improvedcookstoves', ds.pds.upper())
    return improvedcookstoves.total_energy_saving()
