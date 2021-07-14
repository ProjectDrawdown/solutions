import re
import openpyxl
from numpy import nan

def cell_to_offsets(cellref):
    """Convert an Excel reference like "C33" to (row, col) in 1-based notation"""
    return openpyxl.utils.cell.coordinate_to_tuple(cellref)

def co(colref):
    """Convert a column reference like "D" or "AA" to an indexed in 1-based notation"""
    return openpyxl.utils.cell.column_index_from_string(colref)

# The functions xls, xln and xli all take two forms of parameters
#   xls(tab, ref)        # ref in "A3" format
#   xls(tab, row, col)   # row and column in 1-based notation

def xls(tab, row, col=None):
    """Return a string value from tab(ref) or tab(row, col), where tab is a openpyxl sheet"""
    if col is None:
        (row, col) = cell_to_offsets(row)
    val = tab.cell(row, col).value
    if val is None or tab.cell(row, col).data_type == 'e':
        return ''
    return str(val).strip()

def xln(tab, row, col=None, empty_is_nan=False):
    """Return the floating point number read from tab(ref) or tab(row, col), where tab is a openpyxl sheet.
    Returns NaN in case of error. """
    if col is None:
        (row, col) = cell_to_offsets(row)
    if tab.cell(row, col).data_type == 'e': # error
        return nan
    val = tab.cell(row, col).value
    if val is None or val == '':
        return nan if empty_is_nan else 0.0
    return float(val)


def xli(tab, row, col=None):
    """Return the integer read from tab(ref) or tab(row, col), where tab is a openpyxl sheet."""
    if col is None:
        (row, col) = cell_to_offsets(row)
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
