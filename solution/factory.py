"""Return objects for solutions."""

import importlib
from pathlib import Path
from functools import lru_cache
from model import advanced_controls as ac
from model import scenario
from model import vma

def all_solutions():
    # Find all the directories containing an __init__.py
    # The __init__.py check is needed because git doesn't remove empty directories, so if you switch
    # to a branch that doesn't have the solution, you end up with an empty directory.
    # Checking that there is an __init__.py file fixes that case.
    candidates = [ d.name for d in Path(__file__).parent.glob('*') if d.is_dir() and (d/'__init__.py').is_file() ]
   
    # The above test is sufficient, but to be nice, allow for two more ways to make something not a solution
    return [ name for name in candidates if not name.startswith('_') and not name.startswith('test') ]

def list_scenarios(solution):
    """Return a list of scenarios for this solution"""
    m = _load_module(solution)
    return list(m.scenarios.keys())

def load_scenario(solution, scenario=None) -> scenario.Scenario :
    """Load a scenario for the requested solution.  Scenario may be one of the following:
     * None (the default): return the PDS2 scenario for this solution
     * `PDS`, `PDS2` or `PDS3`:  get the most recent scenario of the requested type
     * a scenario name:  load the scenario with that name
     * an AdvancedControl object: load a scenario with completely custom values
     * a json dictionary representing an AdvancedControl object:  load a completely custom scenario based on the data in the object
     * the format should be the same as the sceanrios stored with the solution."""
    m = _load_module(solution)
    if isinstance(scenario, dict):
        scenario = ac.ac_from_dict(scenario, m.VMAs)
    elif scenario in ['PDS1','PDS2','PDS3']:
        md = {'PDS1': m.PDS1, 'PDS2': m.PDS2, 'PDS3': m.PDS3}
        scenario = md[scenario]
    return m.Scenario(scenario)

@lru_cache()
def _load_module(solution):
    """Return the Scenario class and list of scenarios."""
    importname = 'solution.' + solution
    m = importlib.import_module(importname)
    return m

def all_solutions_scenarios():
    everything = {}
    for solution in all_solutions():
        everything[solution] = list_scenarios(solution)
    return everything


def solution_path(solution):
    """Return the root directory where solution is located"""
    return Path(__file__).parent/solution


def solution_vma(solution, vma_title) -> vma.VMA:
    m = _load_module(solution)
    return m.VMAs.get(vma_title,None)


def find_solution_by_name(name):
    """Attempt to find a solution that matches name"""
    try1 = _soln_name_dict.get(name,None)
    # TODO: we could set this up to be more robust, case norming, space norming, 
    # looking for prefixes or substrings...
    return try1


_soln_name_dict = {
    "Afforestation": "afforestation",
    "Aircraft Fuel Efficiency": "airplanes",
    "Alternative Cement": "altcement",
    "Alternative Cements": "altcement",
    "Bamboo": "bamboo",
    "Bicycle  Infrastructure": "bikeinfrastructure",
    "Biochar": "biochar",
    "Biomass (Perennials)": "biomass",
    "Biomass and Waste": "biomass and waste",
    "Biomass Power (Perennial Crops) ": "biomass",
    "Bioplastic": "bioplastic",
    "Bioplastics": "bioplastic",
    "Building Automation (Commercial Only)": "buildingautomation",
    "Building Automation Systems": "buildingautomation",
    "Car Fuel Efficiency": "hybridcars",
    "Carpooling": "carpooling",
    "CHP": "CHP",  #??
    "Clean and Improved Cookstoves (ICS)": "improvedcookstoves",
    "Coal": "coal",
    "Commercial LEDs": "leds_commercial",
    "Commercial LED (Excludes Household LED)" : "leds_commercial",
    "Composting": "composting",
    "Concentrated Solar Power (CSP)": "concentratedsolar",
    "Concentrated Solar Power": "concentratedsolar",
    "Conservation Agriculture": "conservationagriculture",
    "Cookstoves": "cookstoves",
    "Cool Roofs": "coolroofs",
    "CoolRoofs": "coolroofs",
    "Distributed Solar PV": "solarpvroof",
    "District Heating": "districtheating",
    "Electric Bicycles": "electricbikes",
    "Electric Cars": "electricvehicles",
    "Electric Trains": "trains",
    "Electric Vehicles": "electricvehicles",
    "Farmland Restoration": "farmlandrestoration",
    "FarmWater Use EFF": "irregationefficiency",
    "Forest Protection": "forestprotection",
    "Geothermal": "geothermal",
    "Grassland Protection": "grasslandprotection",
    "Green Roofs": "greenroofs",
    "GreenRoofs": "greenroofs",
    "Health and Education": "",
    "Heat Pumps": "heatpumps",
    "High Performance Glass (Commercial)": "commercialglass",
    "High Performance Glass (Residential)": "residentialglass",
    "High Performance Static Glass- Commercial Model": "commercialglass",
    "High Performance Static Glass-Residential Model": "residentialglass",
    "High Speed Rail": "highspeedrail",
    "Household and Commercial Recycling": "hcrecycling",
    "Hydroelectric": "large hydro",
    "Improve Aquaculture": "",
    "Improve Fishery Biomass": "",
    "Improve Fishery Fuel Emissions": "",
    "Improved Livestock Feed": "improvedcattlefeed",
    "Improved Manure Management": "",
    "Improved Rice": "improvedrice",
    "Increasing Distribution Efficiency in WDSs": "waterdistribution",
    "Insulation (Residential Only)": "insulation",
    "Insulation": "insulation",
    "IP Forest Management": "indigenouspeoplesland",
    "Irrigation Efficiency": "irregationefficiency",
    "Landfill Methane Capture": "landfillmethane",
    "Large Biodigesters (Biogas)": "biogas",
    "Large Digesters": "biogas",
    "LED Commercial Lighting": "leds_commercial",
    "Managed Grazing": "managedgrazing",
    "Mangrove Protection": "mangroveprotection",
    "Mangrove Restoration": "mangroverestoration",
    "Mass Transit": "masstransit",
    "Methane Leak Management": "methaneleak",
    "Micro Wind": "microwind",
    "MicroWind Turbines": "microwind",
    "Multistrata Agroforestry": "multistrataagroforestry",
    "Natural gas": "natural gas",
    "Nuclear": "nuclear",
    "Nutrient Management": "nutrientmanagement",
    "Ocean Freight Improvements": "ships",
    "Ocean Power": "waveandtidal",
    "Oil": "oil products",
    "Onshore Wind": "onshorewind",
    "Peatland Protection": "peatlands",
    "Peatland Restoration": "peatlandrestoration",
    "Perennial Bioenergy Crops": "perennialbioenergy",
    "Plant-Rich Diet": "",
    "Protect Coastal Wetlands (Saltmarshes)": "saltmarshprotection",
    "Protect Coastal Wetlands (Seagrasses)": "seagrassprotection",
    "Protect Macroalgae": "macroalgaeprotection",
    "Protect Seafloor": "seafloorprotection",
    "Public Transit": "masstransit",
    "Recycled Metals": "recycledmetals",
    "Recycled Paper": "recycledpaper",
    "Recycled Plastic": "recycledplastics",
    "Reduced Food Waste": "",
    "Refrigerant Management - HFC Replacement": "hfc_replacement",
    "Refrigerant Management": "refrigerants",
    "Regenerative Agriculture": "regenerativeagriculture",
    "Renewable District Heating": "districtheating",
    "Residential LED (Excludes Commercial LED)" : "leds_residential",
    "Residential LED Lighting": "leds_residential",
    "Restore Macroalgae": "macroalgaerestoration",
    "Restore Saltmarshes": "????",
    "Restore Seagrasses": "????",
    "Ridesharing and Carpooling": "carpooling",
    "Rooftop Solar PV": "solarpvroof",
    "Seaweed Farming": "seaweedfarming",
    "Silvopasture": "silvopasture",
    "Small Biogas Digesters": "biogas_small",
    "Small HydroPower <10MW": "instreamhydro",
    "Small Hydropower": "instreamhydro",
    "Smallholder Intensification": "womensmallholders",
    "Smart Glass (Commercial Only)": "smartglass",
    "Smart Glass": "smartglass",
    "Smart Thermostats (Residential Only)" : "smartthermostats",
    "Smart Thermostats": "smartthermostats",
    "Solar Hot Water (SHW)": "solarhotwater",
    "Solar Hot Water": "solarhotwater",
    "Solar Photovoltaic": "solar pv",
    "SRI": "riceintensification",
    "Sustainable Clothing": "sustainableclothing",
    "System of Rice Intensification": "riceintensification",
    "Telepresence": "telepresence",
    "Temporate Forest Restoration": "temperateforests",
    "Train Fuel Efficiency": "trains",
    "Transportation Infrastructure": "bikeinfrastructure",
    "Tree Intercropping": "treeintercropping",
    "Tropical Forest Restoration": "tropicalforests",
    "Tropical Tree Staples": "tropicaltreestaples",
    "Truck Fuel Efficiency": "trucks",
    "Utility Scale Solar PV": "solarpvutil",
    "Videoconferencing": "telepresence",
    "Videoconferencing and Telepresence": "telepresence",
    "Walkable Cities": "walkablecities",
    "Waste to Energy": "wastetoenergy",
    "Water Distribution Efficiency": "waterdistribution",
    "Water Efficiency Measures (Showers and Faucets)": "waterefficiency",
    "Water Saving - Home (WaSH)": "waterefficiency",
    "Wind Offshore": "offshorewind",
    "Wind Onshore": "onshorewind",
}