"""Test rrs.py."""

import pytest
import rrs

def test_rrs():
  assert 'Baseline Cases' in rrs.tam_ref_data_sources
  assert 'Ambitious Cases' in rrs.tam_pds_data_sources

def test_rrs_vma():
  r = rrs.RRS(total_energy_demand=22548.30, soln_avg_annual_use=1841.66857142857)
  assert r.substitutions['@energy_mix_coal@'] == pytest.approx(0.38699149767)

  result = r.oil_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R1015:R1017
  expected = (0.39, 0.39, 0.39)
  assert result == pytest.approx(expected)

  result = r.natural_gas_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R981:R983
  expected = (0.47335870088, 0.56587283233, 0.38084456943)
  assert result == pytest.approx(expected)

  result = r.coal_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R947:R949
  expected = (0.36697534187, 0.43223578286, 0.30171490088)
  assert result == pytest.approx(expected)

  result = r.conv_ref_plant_efficiency_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R893:R895
  expected = (0.41021474451, 0.47368454143, 0.34674494760)
  assert result == pytest.approx(expected)

  result = r.conv_2014_cost_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R107:R109
  expected = (2010.03170851964, 3373.55686730167, 646.50654973761)
  assert result == pytest.approx(expected)

  result = r.conv_lifetime_years_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Advanced Controls'!E95 / F95
  expected = (35.986947222873592, 45.526538153649603, 26.447368421052632)
  assert result == pytest.approx(expected)

  result = r.conv_avg_annual_use_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R947:R949
  expected = (4967.64844181569, 6603.24681182151, 3332.05007180987)
  assert result == pytest.approx(expected)

  result = r.conv_var_oper_cost_per_funit_vma.avg_high_low()
  # WindOnshore_RRS_ELECGEN_v1.1b_24Oct18 'Variable Meta-analysis'!R340:R343
  expected = (0.00475243217, 0.00799278310, 0.00151208124)
  # The comment in the RRS spreadsheets for the €2011/MWh rows says the exchange
  # rate used is €/$ - 1.392705, which would be correct. However the calculation
  # actually uses 1.39448, leading to the values above. The Python code always
  # uses 1.392705. Correcting the exchange rate in Excel results in these values:
  expected = (0.00475054778, 0.00798834718, 0.00151274837)
  assert result == pytest.approx(expected)

  result = r.conv_fixed_oper_cost_per_iunit_vma.avg_high_low()
  # SolarPVUtility_RRS_ELECGEN 'Variable Meta-analysis'!R409:R411
  expected = (32.89064573434, 63.04748100464, 2.73381046403)
  assert result == pytest.approx(expected)
