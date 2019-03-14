"""Test solution classes."""

import pytest
import biogas
import biomass
import concentratedsolar
import improvedcookstoves
import instreamhydro
import insulation
import landfillmethane
import microwind
import offshorewind
import onshorewind
import solarpvroof
import solarpvutil

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

def test_concentratedsolar():
  scenario = list(concentratedsolar.scenarios.keys())[0]
  obj = concentratedsolar.ConcentratedSolar(scenario=scenario)
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
