"""Test solution classes."""

import solarpvroof
import solarpvutil

def test_solarpv():
  expected = ['tam_data', 'adoption_data', 'helper_tables', 'emissions_factors',
      'unit_adoption', 'first_cost', 'operating_cost', 'ch4_calcs', 'co2_calcs']
  objs = [solarpvutil.SolarPVUtil(), solarpvroof.SolarPVRoof()]
  for pv in objs:
    assert pv is not None
    result = pv.to_dict()
    for ex in expected:
      assert ex in result
