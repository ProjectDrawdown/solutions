"""Tests for world_data_xls_extract.py"""

import os
import pathlib
import tempfile

import pytest
import tools.world_data_xls_extract

this_dir = pathlib.Path(__file__).parents[0]


@pytest.mark.slow
def test_land():
    tmpdir = tempfile.TemporaryDirectory()
    r = tools.world_data_xls_extract.WorldDataReader(key='land', outputdir=tmpdir.name)
    r.read_world_data_xls()
    r.make_csvs()
    dirs = os.listdir(tmpdir.name)
    assert 'Global_Arctic.csv' in dirs
    assert 'Temperate_Boreal_Humid.csv' in dirs
    assert 'Tropical_Humid.csv' in dirs
    assert 'Global_Arid.csv' in dirs
    assert 'Temperate_Boreal_Semi_Arid.csv' in dirs
    assert 'Tropical_Semi_Arid.csv' in dirs


@pytest.mark.slow
def test_ocean():
    tmpdir = tempfile.TemporaryDirectory()
    r = tools.world_data_xls_extract.WorldDataReader(key='ocean', outputdir=tmpdir.name)
    r.read_world_data_xls()
    r.make_csvs()
    dirs = os.listdir(tmpdir.name)
    assert 'Blooms.csv' in dirs
    assert 'Deserts.csv' in dirs
    assert 'Equator.csv' in dirs
    assert 'Ice.csv' in dirs
    assert 'Shallow.csv' in dirs
    assert 'Slopes.csv' in dirs
    assert 'Transition.csv' in dirs
