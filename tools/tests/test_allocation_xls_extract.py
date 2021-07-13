"""Tests for allocation_xls_extract.py"""

import os
import pathlib
import tempfile

import pytest
#import tools.allocation_xls_extract

this_dir = pathlib.Path(__file__).parents[0]

pytestmark = pytest.mark.skip("Pending upgrade to openpyxl")

# @pytest.mark.slow
# def test_land():
#     tmpdir = tempfile.TemporaryDirectory()
#     r = tools.allocation_xls_extract.AllocationReader(key='land', outputdir=tmpdir.name)
#     r.read_allocation_xls()
#     r.make_csvs()
#     dirs = os.listdir(tmpdir.name)
#     assert 'Global_Arctic' in dirs
#     assert 'Temperate_Humid' in dirs
#     assert 'Boreal_Humid' in dirs
#     assert 'Tropical_Humid' in dirs
#     assert 'Global_Arid' in dirs
#     assert 'Temperate_Semi_Arid' in dirs
#     assert 'Boreal_Semi_Arid' in dirs
#     assert 'Tropical_Semi_Arid' in dirs


# @pytest.mark.slow
# def test_ocean():
#     tmpdir = tempfile.TemporaryDirectory()
#     r = tools.allocation_xls_extract.AllocationReader(key='ocean', outputdir=tmpdir.name)
#     r.read_allocation_xls()
#     r.make_csvs()
#     dirs = os.listdir(tmpdir.name)
#     assert 'Blooms' in dirs
#     assert 'Deserts' in dirs
#     assert 'Equator' in dirs
#     assert 'Ice' in dirs
#     assert 'Shallow' in dirs
#     assert 'Slopes' in dirs
#     assert 'Transition' in dirs
