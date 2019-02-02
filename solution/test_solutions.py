"""Test solution classes."""

import pytest
import concentratedsolar
import solarpvroof
import solarpvutil

def check_to_dict(obj):
  expected = ['tam_data', 'adoption_data', 'helper_tables', 'emissions_factors',
      'unit_adoption', 'first_cost', 'operating_cost', 'ch4_calcs', 'co2_calcs']
  result = obj.to_dict()
  for ex in expected:
    assert ex in result

def test_solarpvutil():
  scenario = list(solarpvutil.scenarios.keys())[0]
  obj = solarpvutil.SolarPVUtil(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)
  expected = (2044.15474808447, 2643.36995195410, 1444.93954421485)
  result = obj.soln_2014_cost_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (1918.42560000000, 2428.47499956894, 1408.37620043106)
  result = obj.soln_avg_annual_use_vma.avg_high_low()
  assert result == pytest.approx(expected)
  result = obj.soln_fixed_oper_cost_per_iunit_vma.avg_high_low()
  # soln_fixed_oper_cost_per_iunit_vma depends on soln_avg_annual_use, which varies
  # by assumptions in the scenario. Just check that it is rational, not an exact value.
  assert result[0] > 0 and result[0] < 100
  expected = (91558.52222222220, 189681.34083303900, -6564.29638859436)
  result = obj.soln_indirect_co2_per_iunit_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (0.59888888889, 0.67039819071, 0.52737958707)
  result = obj.soln_solar_util_vs_roof_vma.avg_high_low()
  assert result == pytest.approx(expected)

def test_solarpvroof():
  scenario = list(solarpvroof.scenarios.keys())[0]
  obj = solarpvroof.SolarPVRoof(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)
  expected = (2910.31295690078, 3937.09552092798, 1883.53039287357)
  result = obj.soln_2014_cost_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (1725.04615384615, 2132.15185664880, 1317.94045104351)
  result = obj.soln_avg_annual_use_vma.avg_high_low()
  assert result == pytest.approx(expected)
  result = obj.soln_fixed_oper_cost_per_iunit_vma.avg_high_low()
  # soln_fixed_oper_cost_per_iunit_vma depends on soln_avg_annual_use, which varies
  # by assumptions in the scenario. Just check that it is rational, not an exact value.
  assert result[0] > 0 and result[0] < 100
  expected = (47096.81818181820, 65382.64314055300, 28810.99322308340)
  result = obj.soln_indirect_co2_per_iunit_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (0.40111111111, 0.47262041293, 0.32960180929)
  result = obj.soln_solar_util_vs_roof_vma.avg_high_low()
  assert result == pytest.approx(expected)

def test_concentratedsolar():
  scenario = list(concentratedsolar.scenarios.keys())[0]
  obj = concentratedsolar.ConcentratedSolar(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name
  check_to_dict(obj)
