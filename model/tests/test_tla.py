"""Tests for tla.py."""

import pathlib

import numpy as np
import pandas as pd
import pytest

from model import tla

# arguments used in Tropical Forest Restoration v1.1d 27Aug18

datadir = pathlib.Path(__file__).parents[2]

g_tla_ref_data_source = {
    'Based on- WRI 2016': str(
        datadir.joinpath('solution', 'tropicalforests', 'tla_based_on_WRI_2016_widescale_reforestation.csv')),
}

def test_forecast_data_global():
  tl = tla.CustomTLA(g_tla_ref_data_source)
  global_tla = tl.tla_data_global()
  assert global_tla.loc[2060, 'TLA'] == pytest.approx(304.0)

