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
  expected = (2044.15474808447, 2643.36995195410, 1444.93954421485)
  result = obj.soln_2014_cost_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (1918.42560000000, 2428.47499956894, 1408.37620043106)
  result = obj.soln_avg_annual_use_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (23.18791293579, 35.56679577254, 10.80903009905)
  result = obj.soln_fixed_oper_cost_per_iunit_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (91558.52222222220, 189681.34083303900, -6564.29638859436)
  result = obj.soln_indirect_co2_per_iunit_vma.avg_high_low()
  assert result == pytest.approx(expected)

def test_solarpvroof():
  obj = solarpvroof.SolarPVRoof()
  check_to_dict(obj)
  expected = (2910.31295690078, 3937.09552092798, 1883.53039287357)
  result = obj.soln_2014_cost_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (1725.04615384615, 2132.15185664880, 1317.94045104351)
  result = obj.soln_avg_annual_use_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (21.48419023207, 32.62176221027, 10.34661825388)
  result = obj.soln_fixed_oper_cost_per_iunit_vma.avg_high_low()
  assert result == pytest.approx(expected)
  expected = (47096.81818181820, 65382.64314055300, 28810.99322308340)
  result = obj.soln_indirect_co2_per_iunit_vma.avg_high_low()
  assert result == pytest.approx(expected)
