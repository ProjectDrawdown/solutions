import re

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


def convert_float(val):
    """
    Convert a float; empty cell == 0.0 floating point.
    Optionally ignore strings if they are not empty (will pass through without throwing an error).
    """
    if val == '':
        return 0.0
    else:
        return float(val)

