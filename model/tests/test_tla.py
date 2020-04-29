"""Tests for tla.py."""

import pandas as pd
import pathlib
import pytest
from model import tla

datadir = pathlib.Path(__file__).parents[0].joinpath('data')


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


def test_tla_per_region_sub_world_vals():
    sp_land_dist_all = [331.702828, 181.9634517, 88.98630743, 130.15193962, 201.18287123, 933.98739798, 37.60589239,
                        7.02032552, 43.64118779, 88.61837725]
    index = pd.Index(
        ['OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'Global', 'China',
         'India', 'EU', 'USA'])
    land_dist = pd.DataFrame(sp_land_dist_all, columns=['All'], index=index)
    custom_world_vals = list(range(100, 149))
    index = pd.Index(data=list(range(2012, 2061)), name='Year')
    custom_world_vals_df = pd.DataFrame(custom_world_vals, columns=['Source 1'], index=index)
    tla_per_region = tla.tla_per_region(land_dist=land_dist, custom_world_values=custom_world_vals_df)
    pd.testing.assert_series_equal(tla_per_region.loc[:, 'World'], custom_world_vals_df.loc[2014:, 'Source 1'],
                                   check_names=False)


def test_custom_tla():
    tl = tla.CustomTLA(filename=datadir.joinpath('trr_custom_tla_data.csv'))
    world_vals = list(tl.get_world_values().iloc[:, 0])
    assert all(val == 304 for val in world_vals)


def test_custom_tla_handles_bad_filename():
    with pytest.raises(FileNotFoundError):
        _ = tla.CustomTLA(filename='adfadf')


def test_custom_tla_fixed_value():
    tl = tla.CustomTLA(fixed_value=7.0)
    df = tl.get_world_values()
    assert (df['World'] == 7.0).all()
