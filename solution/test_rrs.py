"""Test rrs.py."""

import pytest
import rrs

def test_rrs():
  assert 'Baseline Cases' in rrs.tam_ref_data_sources
  assert 'Ambitious Cases' in rrs.tam_pds_data_sources

def test_rrs_vma():
  result = rrs.oil_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R1015:R1017
  expected = (0.39, 0.39, 0.39)
  assert result == pytest.approx(expected)
  assert rrs.oil_efficiency == pytest.approx(0.39)

  result = rrs.natural_gas_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R981:R983
  expected = (0.47335870088, 0.56587283233, 0.38084456943)
  assert result == pytest.approx(expected)
  assert rrs.natural_gas_efficiency == pytest.approx(0.47335870088)

  result = rrs.coal_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R947:R949
  expected = (0.36697534187, 0.43223578286, 0.30171490088)
  assert result == pytest.approx(expected)
  assert rrs.coal_efficiency == pytest.approx(0.36697534187)

  result = rrs.conv_ref_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R893:R895
  expected = (0.41021474451, 0.47368454143, 0.34674494760)
  assert result == pytest.approx(expected)
  assert rrs.conv_ref_plant_efficiency == pytest.approx(0.41021474451)

  result = rrs.conv_2014_cost_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R107:R109
  expected = (2010.03170851964, 3373.55686730167, 646.50654973761)
  assert result == pytest.approx(expected)
  assert rrs.conv_2014_cost == pytest.approx(2010.03170851964)

  result = rrs.conv_lifetime_years_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Advanced Controls'!E95 / F95
  expected = (35.986947222873592, 45.526538153649603, 26.447368421052632)
  assert result == pytest.approx(expected)
  assert rrs.conv_lifetime_years == pytest.approx(35.986947222873592)

  result = rrs.conv_avg_annual_use_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R947:R949
  expected = (4967.64844181569, 6603.24681182151, 3332.05007180987)
  assert result == pytest.approx(expected)
  assert rrs.conv_avg_annual_use == pytest.approx(4967.64844181569)

def test_rrs_object():
  r = rrs.RRS(total_energy_demand=22548.30)
  assert r.energy_adoption_mix['Coal'] == pytest.approx(0.38699149767)

