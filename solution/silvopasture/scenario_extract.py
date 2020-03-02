""" Use tools from solution_xls_extract to create AdvancedControls objects for
all Silvopasture scenarios """

import pathlib
import sys
import xlrd
from tools.solution_xls_extract import get_land_scenarios, write_scenario
from model import advanced_controls as ac


if __name__ == '__main__':
    path_to_xls = pathlib.Path(__file__).parents[0].joinpath('testdata', 'Silvopasture_L-Use_v1.1a_3Aug18.xlsm')
    wb = xlrd.open_workbook(filename=path_to_xls)
    scenarios = get_land_scenarios(wb, ac.string_to_solution_category('LAND'))

    for k, s in scenarios.items():
        f = sys.stdout
        print(k)
        write_scenario(f, s)
