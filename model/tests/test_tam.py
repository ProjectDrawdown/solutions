"""Tests for tam.py."""

import pathlib

import pandas as pd
import pytest
from model import tam

solution_dir = pathlib.Path(__file__).parents[2].joinpath('solution')
ref_tam_per_region_filename = solution_dir.joinpath('solarpvutil_ref_tam_per_region.csv')
pds_tam_per_region_filename = solution_dir.joinpath('solarpvutil_pds_tam_per_region.csv')

def test_ref_tam_per_region():
  tm = tam.TAM(ref_tam_per_region_filename=ref_tam_per_region_filename,
      pds_tam_per_region_filename=None)
  tpr = tm.ref_tam_per_region()
  assert tpr['World'][2015] == pytest.approx(24255.85984701330)
  assert tpr['Middle East and Africa'][2030] == pytest.approx(3327.58692761822)
  assert tpr['USA'][2060] == pytest.approx(5667.10030035318)

def test_pds_tam_per_region():
  tm = tam.TAM(ref_tam_per_region_filename=None,
      pds_tam_per_region_filename=pds_tam_per_region_filename)
  tpr = tm.pds_tam_per_region()
  assert tpr['World'][2015] == pytest.approx(24618.92406917750)
  assert tpr['Middle East and Africa'][2032] == pytest.approx(3605.37700804011)
  assert tpr['EU'][2060] == pytest.approx(5065.47629965147)
