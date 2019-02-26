"""Tests for tla.py."""

import pandas as pd
import pathlib
import pytest
from model import tla

datadir = pathlib.Path(__file__).parents[0].joinpath('data')
basedir = pathlib.Path(__file__).parents[2]

# arguments used in Tropical Forest Restoration v1.1d 27Aug18
g_tla_ref_data_source = {
    'Based on- WRI 2016': str(
        basedir.joinpath('solution', 'tropicalforests', 'tla_based_on_WRI_2016_widescale_reforestation.csv')),
}


def test_forecast_data_global():
    tl = tla.CustomTLA(g_tla_ref_data_source)
    global_tla = tl.tla_data_global()
    assert global_tla.loc[2060, 'TLA'] == pytest.approx(304.0)


def test_tla_per_region():
    sp_land_dist_all = [331.702828, 181.9634517, 88.98630743, 130.15193962, 201.18287123, 933.98739798, 37.60589239,
                    7.02032552, 43.64118779, 88.61837725]
    index = pd.Index(
        ['OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'Global', 'China',
         'India', 'EU', 'USA'])
    land_dist = pd.DataFrame(sp_land_dist_all, columns=['All'], index=index)

    expected = pd.read_csv(datadir.joinpath('sp_tla.csv'), index_col=0)
    result = tla.tla_per_region(land_dist=land_dist)
    pd.testing.assert_frame_equal(expected, result)
