"""Tests for tam.py."""

import pandas as pd
import pytest
from model import tam


def test_ref_tam_per_region():
  tm = tam.TAM()
  tpr = tm.ref_tam_per_region()
  assert tpr['World'][2015] == pytest.approx(24255.85984701330)
  assert tpr['Middle East and Africa'][2030] == pytest.approx(3327.58692761822)
  assert tpr['USA'][2060] == pytest.approx(5667.10030035318)

def test_pds_tam_per_region():
  tm = tam.TAM()
  tpr = tm.pds_tam_per_region()
  assert tpr['World'][2015] == pytest.approx(24618.92406917750)
  assert tpr['Middle East and Africa'][2032] == pytest.approx(3605.37700804011)
  assert tpr['EU'][2060] == pytest.approx(5065.47629965147)
