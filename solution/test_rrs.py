"""Test rrs.py."""

import pytest
import rrs

def test_rrs():
  assert 'Baseline Cases' in rrs.tam_ref_data_sources
  assert 'Ambitious Cases' in rrs.tam_pds_data_sources

def test_rrs_vma():
  result = rrs.vma_oil_plant_efficiency.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R1015:R1017
  expected = (0.39, 0.39, 0.39)
  assert result == pytest.approx(expected)

  result = rrs.vma_natural_gas_plant_efficiency.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R981:R983
  expected = (0.47335870088, 0.56587283233, 0.38084456943)
  assert result == pytest.approx(expected)

  result = rrs.vma_coal_plant_efficiency.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R947:R949
  expected = (0.36697534187, 0.43223578286, 0.30171490088)
  assert result == pytest.approx(expected)

def test_rrs_object():
  r = rrs.RRS(total_energy_demand=22548.30)
  result = r.vma_conv_ref_plant_efficiency.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R893:R895
  expected = (0.41021474451, 0.47368454143, 0.34674494760)
  assert result == pytest.approx(expected)
