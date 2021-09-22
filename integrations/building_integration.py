from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from model import integration
from integration_base import *

THISDIR = Path(__file__).parent
DATADIR = THISDIR/"data"/"building"

@dataclass
class building_integration_state:
    # This data class holds global variables that are shared between steps.  Embedding it in a class
    # enables us to avoid having to declare 'global' anytime we want to change something.

    cooking_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"cooking_global_tam.csv", index_col="year", squeeze=False)
    floor_area_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"floor_area_global_tam.csv", index_col="year", squeeze=False)
    households_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"households_global_tam.csv", index_col="year", squeeze=False)
    lighting_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"lighting_global_tam.csv", index_col="year", squeeze=False)
    roof_area_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"roof_area_global_tam.csv", index_col="year", squeeze=False)
    space_cooling_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"space_cooling_global_tam.csv", index_col="year", squeeze=False)
    space_heating_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"space_heating_global_tam.csv", index_col="year", squeeze=False)
    water_heating_global_tam : pd.DataFrame = pd.read_csv(DATADIR/"water_heating_global_tam.csv", index_col="year", squeeze=False)

data_state = building_integration_state()

def integrate():
    """Perform all steps of the integration together."""
    pass

def insulation_integration():
    """Step 1 in integration chain. Calculate the total energy saved and split
    saved energy into cooling and heating usage. Result does not affect other
    integration steps."""
    pass

def roofs_integration():
    """Step 2. Combines calculations for cool and green roofs."""
    pass

def high_performance_glass_integration():
    """Step 3. Combines calculation for residential and commercial high performance
    glass. """
    pass

def led_integration():
    """Step 4. LED integration."""
    pass

def dynamic_glass_integration():
    """Step 5. Dynamic glass integration. Depends on both high performance glass
    and LED. Commercial only."""
    pass

def building_automation_integration():
    """Step 6. Building automation. Depends on dynamic glass."""
    pass

def smart_thermostat_integration():
    """Step 7. Smart thermostat. Depends on building automation"""
    pass

def heat_pumps_integration():
    """Step 8. Heat pumpts. Depends on smart thermostat."""
    pass

def district_heating_integration():
    """Step 9. District heating. Depends on heat pumps."""
    pass

def cooking_biogas_integration():
    """Step 10. Cooking biogas. No upstream dependency."""
    pass

def clean_stoves_integration():
    """Step 11. Clean stoves. Depends on cooking biogas."""
    pass

def low_flow_fixtures_integration():
    """Step 12. Lo-flow fixtures. No upstream dependency."""
    pass

def solar_hw_integration():
    """Step 13. Solar HW. Depends on low flow fixtures."""
