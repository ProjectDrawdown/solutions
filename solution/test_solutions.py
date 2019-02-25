"""Test solution classes."""

import pytest
import biogas
import biomass
import concentratedsolar
import landfillmethane
import microwind
import offshorewind
import onshorewind
import solarpvroof
import solarpvutil

def check_to_dict(obj):
  expected = ['tam_data', 'adoption_data', 'helper_tables', 'emissions_factors',
      'unit_adoption', 'first_cost', 'operating_cost', 'ch4_calcs', 'co2_calcs']
  result = obj.to_dict()
  for ex in expected:
    assert ex in result

def test_biogas():
  scenario = list(biogas.scenarios.keys())[0]
  obj = biogas.Biogas(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_biomass():
  scenario = list(biomass.scenarios.keys())[0]
  obj = biomass.Biomass(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_concentratedsolar():
  scenario = list(concentratedsolar.scenarios.keys())[0]
  obj = concentratedsolar.ConcentratedSolar(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_landfillmethane():
  scenario = list(landfillmethane.scenarios.keys())[0]
  obj = landfillmethane.LandfillMethane(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_microwind():
  scenario = list(microwind.scenarios.keys())[0]
  obj = microwind.MicroWind(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_offshorewind():
  scenario = list(offshorewind.scenarios.keys())[0]
  obj = offshorewind.OffshoreWind(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_onshorewind():
  scenario = list(onshorewind.scenarios.keys())[0]
  obj = onshorewind.OnshoreWind(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_solarpvroof():
  scenario = list(solarpvroof.scenarios.keys())[0]
  obj = solarpvroof.SolarPVRoof(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)

def test_solarpvutil():
  scenario = list(solarpvutil.scenarios.keys())[0]
  obj = solarpvutil.SolarPVUtil(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)
