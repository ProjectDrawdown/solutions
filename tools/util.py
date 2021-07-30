import re
import openpyxl
import pandas as pd
from numpy import nan

# Excel index manipulation

def cell_to_indices(cellref):
    """Convert an Excel reference like "C33" to (row, col) in 1-based notation (suitable for openpyxl)"""
    return openpyxl.utils.cell.coordinate_to_tuple(cellref)

def cell_to_offsets(cellref):
    """Convert an Excel reference like "C33" to (row, col) in 0-based notation (suitable for pd.read_csv or pd.read_excel"""
    ofs = cell_to_indices(cellref)
    return (ofs[0]-1, ofs[1]-1)

def df_excel_range(df, rangeref, to_numeric=True):
    """Return a subset of a DataFrame expressed in Excel notation.
    Use this method when df holds an entire sheet of a spreadsheet.
    Usually you will _not_ want to include the header (column name) row in the df.
    """
    (firstcol, firstrow, lastcol, lastrow) = openpyxl.utils.cell.range_boundaries(rangeref)
    result = df.iloc[ firstrow-1:lastrow, firstcol-1:lastcol ]
    if to_numeric:
        result = result.apply(pd.to_numeric,errors='ignore')
    return result

def co(colref):
    """Convert a column reference like "D" or "AA" to an index in 1-based notation"""
    return openpyxl.utils.cell.column_index_from_string(colref)

# The functions xls, xln and xli all take two forms of parameters
#   xls(tab, ref)        # ref in "A3" format
#   xls(tab, row, col)   # row and column in 1-based notation

def xls(tab, row, col=None):
    """Return a string value from tab(ref) or tab(row, col), where tab is a openpyxl sheet"""
    if col is None:
        (row, col) = cell_to_indices(row)
    val = tab.cell(row, col).value
    if val is None or tab.cell(row, col).data_type == 'e':
        return ''
    return str(val).strip()

def xln(tab, row, col=None, empty_is_nan=False):
    """Return the floating point number read from tab(ref) or tab(row, col), where tab is a openpyxl sheet.
    Returns NaN in case of error, and NaN or zero in case of empty, depending on `empty_is_nan` """
    if col is None:
        (row, col) = cell_to_indices(row)
    if tab.cell(row, col).data_type == 'e': # error
        return nan
    val = tab.cell(row, col).value
    if val is None or val == '':
        return nan if empty_is_nan else 0.0
    return float(val)


def xli(tab, row, col=None):
    """Return the integer read from tab(ref) or tab(row, col), where tab is a openpyxl sheet.
    Returns zero in case of empty or error."""
    if col is None:
        (row, col) = cell_to_indices(row)
    val = tab.cell(row, col).value
    if val is None or val == '' or tab.cell(row, col).data_type == 'e':
        return 0
    return int(val)


def convert_bool(val):
    """Infer a boolean from common conventions in the spreadsheet."""
    if val is None:
        raise ValueError('Cannot convert empty value to boolean')       
    v = str(val).lower()
    if v == 'y' or v == 'yes':
        return True
    if v == 'n' or v == 'no':
        return False
    raise ValueError('Unknown boolean format: ' + str(val))


def convert_float(val, return_nan=False):
    """
    Convert a float; empty cell == 0.0 floating point.
    Ignores strings if they are not empty (will pass through without throwing an error).
    """
    if val is None or val == '':
        return nan if return_nan else 0
    else:
        return float(val)


def empty_to_nan(val):
    """ Converts empty cell or cell containing only spaces to NaN """
    if val is None or isinstance(val, str) and val.replace(' ', '') == '':
        return nan
    else:
        return val


def to_filename(name):
    """ Removes special characters and separates words with single underscores"""
    return re.sub(' +', '_', re.sub('[^a-zA-Z0-9' '\n]', ' ', name)).strip('_')
