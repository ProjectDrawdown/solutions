"""Test rrs.py."""

import pytest
import rrs

def test_rrs():
  assert 'Baseline Cases' in rrs.tam_ref_data_sources
  assert 'Ambitious Cases' in rrs.tam_pds_data_sources

def test_rrs_vma():
  r = rrs.RRS(total_energy_demand=22548.30, soln_avg_annual_use=1841.66857142857,
      conv_avg_annual_use=4946.840187342)
  assert r.substitutions['@energy_mix_coal@'] == pytest.approx(0.38699149767)
