"""Tests for world_data_xls_extract.py"""

import os
import pathlib
import subprocess
import tempfile

import pytest
#import tools.world_data_xls_extract

this_dir = pathlib.Path(__file__).parents[0]

pytestmark = pytest.mark.skip("Pending upgrade to openpyxl")

# @pytest.mark.slow
# def test_land():
#     tmpdir = tempfile.TemporaryDirectory()
#     r = tools.world_data_xls_extract.WorldDataReader(key='land', outputdir=tmpdir.name)
#     r.read_world_data_xls()
#     r.make_csvs()
#     dirs = os.listdir(tmpdir.name)
#     assert 'Global_Arctic.csv' in dirs
#     assert 'Temperate_Humid.csv' in dirs
#     assert 'Boreal_Humid.csv' in dirs
#     assert 'Tropical_Humid.csv' in dirs
#     assert 'Global_Arid.csv' in dirs
#     assert 'Temperate_Semi_Arid.csv' in dirs
#     assert 'Boreal_Semi_Arid.csv' in dirs
#     assert 'Tropical_Semi_Arid.csv' in dirs


# @pytest.mark.slow
# def test_ocean():
#     tmpdir = tempfile.TemporaryDirectory()
#     r = tools.world_data_xls_extract.WorldDataReader(key='ocean', outputdir=tmpdir.name)
#     r.read_world_data_xls()
#     r.make_csvs()
#     dirs = os.listdir(tmpdir.name)
#     assert 'Blooms.csv' in dirs
#     assert 'Deserts.csv' in dirs
#     assert 'Equator.csv' in dirs
#     assert 'Ice.csv' in dirs
#     assert 'Shallow.csv' in dirs
#     assert 'Slopes.csv' in dirs
#     assert 'Transition.csv' in dirs


# @pytest.mark.slow
# def test_invoke_world_data_xls_extract():
#     script = str(this_dir.joinpath('test_world_data_xls_extract.sh'))
#     toolsdir = str(this_dir.parents[0])
#     rc = subprocess.run([script, toolsdir], capture_output=True, timeout=120)
#     assert rc.returncode == 0, rc.stdout
