import re
import openpyxl
from numpy import nan

def cell_to_offsets(cellref):
    """Convert an Excel reference like "C33" to (row, col) in 1-based notation"""
    return openpyxl.utils.cell.coordinate_to_tuple(cellref)


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
