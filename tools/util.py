import pathlib
import pandas as pd
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
    return re.sub(' +', '_', re.sub('[^a-zA-Z0-9' '\n]', ' ', name)).strip('_')


def get_full_soln_name(soln_name):
    """ Returns full name of solution when given the module name.
        e.g. 'tropicalforests'  -->  'Tropical Forests' """
    solns_csv = pathlib.Path(__file__).parents[1].joinpath('data', 'overview', 'solutions.csv')
    # remove leading spaces
    solns_df = pd.read_csv(solns_csv).apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    # there are some exceptions
    exceptions = {'riceintensification': 'SRI', 'indigenouspeoplesland': 'IP Forest Management',
                  'peatlands': 'Peatland Protection', 'improvedrice': 'Improved Rice',
                  'tropicalforests': 'Tropical Forest Restoration', 'perennialbioenergy': 'Perennial Bioenergy Crops',
                  'tropicaltreestaples': 'Tropical Tree Staples'}
    if soln_name in exceptions.keys():
        return exceptions[soln_name]
    else:
        return solns_df[solns_df[' DirName'] == soln_name]['Solution'].values[0]


def pretty_print_table(df):
    """ Prints a nice-looking DataFrame """
    from tabulate import tabulate
    print(tabulate(df, headers='keys', tablefmt='psql', stralign='center', numalign='center', disable_numparse=False,
                   floatfmt='.3f'))
