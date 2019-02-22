import re
from numpy import nan


def cell_to_offsets(cell):
  """Convert an Excel reference like C33 to (row, col) for xlrd."""
  (col, row) = filter(None, re.split(r'(\d+)', cell))
  colnum = 0
  for i, c in enumerate(col):
    colnum = (colnum + min(i, 1)) * 26 + (ord(c.upper()) - ord('A'))
  return (int(row) - 1, colnum)


def convert_bool(val):
  """Infer a boolean from common conventions in the spreadsheet."""
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
    if val == '':
        return nan if return_nan else 0
    else:
        return float(val)


def empty_to_nan(val):
    """ Converts empty cell or cell containing only spaces to NaN """
    if isinstance(val, str) and val.replace(' ', '') == '':
        return nan
    else:
        return val


def to_filename(name):
    """ Removes special characters and separates words with single underscores"""
    return re.sub(' +', '_', re.sub('[^a-zA-Z0-9' '\n]', ' ', name))
