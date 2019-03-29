"""
This solution is being used to test the LAND modifications to solution_xls_extract.
This is a scratch file for developing and testing.
"""

import pathlib
import xlrd
from tools import solution_xls_extract as xe

THISDIR = pathlib.Path(__file__).parents[0]
XLSPATH = str(
    pathlib.Path(__file__).parents[0].joinpath('testdata', 'Tropical_Forest_Restoration_L-Use_v1.1b_3Aug18.xlsm'))


# wb = xlrd.open_workbook(filename=XLSPATH)
xe.output_solution_python_file(THISDIR, XLSPATH, 'TropicalForests')