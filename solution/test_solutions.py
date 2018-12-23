"""Test solution classes."""

import solarpvutil

def test_solarpvutil():
  pv = solarpvutil.SolarPVUtil()
  assert pv is not None
  result = pv.to_dict()
  expected = ['tam_data', 'adoption_data', 'helper_tables', 'emissions_factors',
      'unit_adoption', 'first_cost', 'operating_cost', 'ch4_calcs', 'co2_calcs']
  for ex in expected:
    assert ex in result
