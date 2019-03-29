"""Test solution classes."""

import pytest
import airplanes
import altcement
import biogas
import biomass
import bioplastic
import buildingautomation
import concentratedsolar
import electricvehicles
import highspeedrail
import improvedcookstoves
import instreamhydro
import insulation
import landfillmethane
import microwind
import offshorewind
import onshorewind
import ships
import silvopasture
import smartglass
import smartthermostats
import solarhotwater
import solarpvroof
import solarpvutil
import telepresence
import tropicalforests

def test_airplanes():
  scenario = list(airplanes.scenarios.keys())[0]
  obj = airplanes.Airplanes(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_altcement():
  scenario = list(altcement.scenarios.keys())[0]
  obj = altcement.AlternativeCement(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_biogas():
  scenario = list(biogas.scenarios.keys())[0]
  obj = biogas.Biogas(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_biomass():
  scenario = list(biomass.scenarios.keys())[0]
  obj = biomass.Biomass(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_bioplastic():
  scenario = list(bioplastic.scenarios.keys())[0]
  obj = bioplastic.Bioplastic(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_buildingautomation():
  scenario = list(buildingautomation.scenarios.keys())[0]
  obj = buildingautomation.BuildingAutomationSystems(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_concentratedsolar():
  scenario = list(concentratedsolar.scenarios.keys())[0]
  obj = concentratedsolar.ConcentratedSolar(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_electricvehicles():
  scenario = list(electricvehicles.scenarios.keys())[0]
  obj = electricvehicles.ElectricVehicles(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_highspeedrail():
  scenario = list(highspeedrail.scenarios.keys())[0]
  obj = highspeedrail.HighSpeedRail(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_improvedcookstoves():
  scenario = list(improvedcookstoves.scenarios.keys())[0]
  obj = improvedcookstoves.ImprovedCookStoves(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_instreamhydro():
  scenario = list(instreamhydro.scenarios.keys())[0]
  obj = instreamhydro.InstreamHydro(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_insulation():
  scenario = list(insulation.scenarios.keys())[0]
  obj = insulation.Insulation(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_landfillmethane():
  scenario = list(landfillmethane.scenarios.keys())[0]
  obj = landfillmethane.LandfillMethane(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_microwind():
  scenario = list(microwind.scenarios.keys())[0]
  obj = microwind.MicroWind(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_offshorewind():
  scenario = list(offshorewind.scenarios.keys())[0]
  obj = offshorewind.OffshoreWind(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_onshorewind():
  scenario = list(onshorewind.scenarios.keys())[0]
  obj = onshorewind.OnshoreWind(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_ships():
  scenario = list(ships.scenarios.keys())[0]
  obj = ships.Ships(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_silvopasture():
  scenario = list(silvopasture.scenarios.keys())[0]
  obj = silvopasture.Silvopasture(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_smartglass():
  scenario = list(smartglass.scenarios.keys())[0]
  obj = smartglass.SmartGlass(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_smartthermostats():
  scenario = list(smartthermostats.scenarios.keys())[0]
  obj = smartthermostats.SmartThermostats(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_solarhotwater():
  scenario = list(solarhotwater.scenarios.keys())[0]
  obj = solarhotwater.SolarHotWater(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_solarpvroof():
  scenario = list(solarpvroof.scenarios.keys())[0]
  obj = solarpvroof.SolarPVRoof(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_solarpvutil():
  scenario = list(solarpvutil.scenarios.keys())[0]
  obj = solarpvutil.SolarPVUtil(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_telepresence():
  scenario = list(telepresence.scenarios.keys())[0]
  obj = telepresence.Telepresence(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name

def test_tropicalforests():
  scenario = list(tropicalforests.scenarios.keys())[0]
  obj = tropicalforests.TropicalForests(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
