"""Test solution classes."""

import pytest
import solarpvroof
import solarpvutil

def check_to_dict(obj):
  expected = ['tam_data', 'adoption_data', 'helper_tables', 'emissions_factors',
      'unit_adoption', 'first_cost', 'operating_cost', 'ch4_calcs', 'co2_calcs']
  result = obj.to_dict()
  for ex in expected:
    assert ex in result

def test_solarpvutil():
  obj = solarpvutil.SolarPVUtil()
  check_to_dict(obj)
  assert obj.soln_2014_cost == pytest.approx(1444.93954421485)
  assert obj.soln_lifetime_years == pytest.approx(26.249979638045904)
  expected = (1918.42560000000, 2428.47499956894, 1408.37620043106)
  result = obj.soln_avg_annual_use_vma.avg_high_low()
  assert result == pytest.approx(expected)
  assert obj.soln_avg_annual_use == pytest.approx(1918.42560000000)

def test_solarpvroof():
  obj = solarpvroof.SolarPVRoof()
  check_to_dict(obj)
  assert obj.soln_2014_cost == pytest.approx(1883.5303928735746)
  assert obj.soln_lifetime_years == pytest.approx(24.000000178367633)
  expected = (1725.04615384615, 2132.15185664880, 1317.94045104351)
  result = obj.soln_avg_annual_use_vma.avg_high_low()
  assert result == pytest.approx(expected)
  assert obj.soln_avg_annual_use == pytest.approx(1725.04615384615)
