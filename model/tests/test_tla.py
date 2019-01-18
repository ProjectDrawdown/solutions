"""Tests for tla.py."""

import pathlib

import numpy as np
import pandas as pd
import pytest

from model import tla

# arguments used in Tropical Forest Restoration v1.1d 27Aug18
tlaconfig_list = [
  ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
   'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
  ['source_until_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
   'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],

  # Not sure about this
  # ['source_after_2014', 'Baseline Cases',
  #   'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario', 'ALL SOURCES',
  #   'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
  #   'ALL SOURCES', 'ALL SOURCES'],

  # (placeholder)
  ['source_after_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
   'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],

  ['trend', '3rd Poly', '3rd Poly', 'Linear', 'Linear', 'Linear', 'Linear', 'Linear',
   'Linear', 'Linear', 'Linear', 'Linear'],
  ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
   'Medium', 'Medium', 'Medium'],
  ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
  ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
g_tlaconfig = pd.DataFrame(tlaconfig_list[1:], columns=tlaconfig_list[0]).set_index('param')

datadir = pathlib.Path(__file__).parents[2]

# This is a custom data source specific to solution
g_tla_ref_data_sources = {
  'Based on- WRI 2016': str(
      datadir.joinpath('solution', 'tropicalforests', 'tla_based_on_WRI_2016_widescale_reforestation.csv')),
}

def test_forecast_data():
  tl = tla.TLA(tlaconfig=g_tlaconfig, tla_ref_data_sources=g_tla_ref_data_sources)
  forecast = tl.forecast_data_global()
  wri = 'Based on- WRI 2016'
  assert forecast.loc[2060, wri] == pytest.approx(304.0)

