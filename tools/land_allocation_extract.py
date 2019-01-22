""" Reads 'Land Allocation - Max TLA'  sheet """

import xlrd
import re
import pathlib
import pandas as pd
from tools.xls_extract import cell_to_offsets, convert_float

LAND_ALLOCATION_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'Land Allocation - Max TLA.xlsx')
pd.set_option('display.expand_frame_repr', False)


def convert(val):
    """ Allows passing non-empty strings through the convert_float function """
    try:
        return convert_float(val)
    except ValueError:
        return val


def get_single_adoption_df(title_row, title_col, sheet):
    """
    Reads a single adoption table from the spreadsheet when given the title cell.
    e.g. get_single_adoption_df(*cell_to_offsets('C15'), sheet) would give the
    table associated with cell C15 (AEZ1: Forest prime, minimal)
    Returns a DataFrame of this table.
    """
    print(sheet.cell_value(title_row, title_col))

    assert 'AEZ' in sheet.cell_value(title_row, title_col)
    assert 'AEZ' in sheet.cell_value(title_row + 1, title_col)
    columns = {}
    for i in range(6):
        col = []
        for j in range(25):
            col.append(convert(sheet.cell_value(title_row + j + 3, title_col + i)))
        columns[sheet.cell_value(title_row + 2, title_col + i)] = col
    df = pd.DataFrame(columns)
    print(df)
    return df


def read_land_allocation_xls():
    wb = xlrd.open_workbook(filename=LAND_ALLOCATION_PATH)
    sheet = wb.sheet_by_name('Land Allocation - Max TLA')

    # first_forest_cell = cell_to_offsets('C15')
    first_grassland_cell = cell_to_offsets('AA17')
    print(first_grassland_cell)
    get_single_adoption_df(*first_grassland_cell, sheet)



if __name__ == '__main__':
    read_land_allocation_xls()