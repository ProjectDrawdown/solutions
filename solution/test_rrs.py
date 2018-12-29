"""Test rrs.py."""

import rrs

def test_rrs():
  assert 'Baseline Cases' in rrs.tam_ref_data_sources
  assert 'Ambitious Cases' in rrs.tam_pds_data_sources
