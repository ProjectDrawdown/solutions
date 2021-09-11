"""
Extract the basic part of the TAM/Adoption tabs that lists studies, categorized into cases.
Doing this independently of solution_xls_extract to enable use for other situations, like integrations,
where the SMA may be located in different positions on the page, or use different ways of setting titles.
This code does *not* exctract the parameters (3rd Poly, etc.) that go with the data table
"""
import pandas as pd
from model.sma import SMA
from tools.util import *
from tools.solution_xls_extract import normalize_case_name, normalize_source_name

# I started from solution_xls_extract.extract_source_data, but kept finding that there
# were inappropriate assumptions or requirements built in.... so I've ended up basically rewriting it.

def extract_sma(wb, sheet_name, year_col, start_row=1, end_row=None, has_regions=True, use_functional_unit=False) -> SMA:
    """use_functional_unit:  Use the presence of the cell with the content "Functional Unit" to find
    the right edge of the table, instead of using merged cells in the case header."""
    ws = wb[sheet_name]

    if has_regions:
        regionlist = find_sma_blocks(ws, year_col, start_row=start_row, end_row=end_row, find_titles=has_regions)
    else:
        oneblock = find_sma_block(ws, year_col, start_row=start_row, end_row=end_row)
        if oneblock is None:
            raise ValueError(f"Could not find an SMA block on {sheet_name} starting at {start_row}")
        regionlist = { 'World':  oneblock }

    region_data = {}
    source_data = {}  # map title -> proto Source object

    # read each block into a dataframe, processing it to build up both the case_data and the source_data.
    # We do _not_ assume that all blocks are the same width or the same height, or have the same cases.

    source_counter=1
    for region_name, location in regionlist.items():
        (start,end) = location

        case_map = find_sma_cases(ws, start, year_col, use_functional_unit=use_functional_unit)

        # read the source names from the header
        min_column = co(year_col)
        max_column = max(case_map.keys())
        source_titles = [ normalize_source_name(x) for x in read_row(ws, start+1, min_column+1, max_column) ]

        # read the table of data values, not including the header row
        # min_column, max_column, skiprows : shift from 1-base to 0-base.
        region_table = pd.read_excel(wb, engine='openpyxl', sheet_name=sheet_name, usecols=range(min_column-1, max_column), index_col=0,
                                     header=None, skiprows=start+1, nrows=(end-start)-1)
        region_table.index.name = "Year"

        # assemble case_data and source_data from the pieces
        case_data = {}
        for (i, title) in enumerate(source_titles):

            source_col = region_table.iloc[:,i]  # the column in the dataframe
            source_col_number = i + min_column + 1  # the column number in excel

            # "empty" sources are indicated in the tables when the data are all nan; skip those
            if source_col.isnull().all():
                continue

            if title in source_data:
                shortname = source_data[title].shortname
            else:
                shortname = f"S{source_counter}"
                source_counter += 1
                source_data[title] = SMA.Source(title, shortname, data={})
            # add column to source's data.  Note that the column is associated with the region name           
            source_data[title].data[region_name] = source_col

            # add source to cases
            if case_map[source_col_number] not in case_data:
                case_data[case_map[source_col_number]] = [shortname]
            else:
                case_data[case_map[source_col_number]].append(shortname)
        # end for

        region_data[region_name] = case_data
    # end for

    # Recreate source_data with the merged dataframe, and shortname as key
    real_source_data = {}
    for source in source_data.values():
        source.data = pd.concat( source.data, axis=1, copy=False )
        real_source_data[ source.shortname ] = source

    return SMA(region_data, real_source_data)



def find_sma_blocks(ws, year_col='B', start_row=1, end_row=None, find_titles=True):
    """Find SMA blocks located on a worksheet.
    year_col is the column in which the years are located; blocks are located by contiguous
    sets of years.
    If find_titles is True, the titles are searched for for each block, and the
    result is a dictionary mapping titles to (startrow,endrow) pairs.
    Otherwise a simple list of (startrow, endrow) pairs is returned.
    """
    blocks = {}
    blk = find_sma_block(ws, year_col, start_row, end_row)
    while blk:
        (start, end) = blk
        if find_titles:
            title = find_sma_block_title(ws, start, year_col)
            title = title or f"Not found {start}"
            blocks[title] = (start,end)
        else:
            blocks[start] = (start,end)
        
        blk = find_sma_block(ws, year_col, start_row=end+1, end_row=end_row)
    
    return blocks if find_titles else blocks.values()

 
def find_sma_block(ws, year_col='B', start_row=1, end_row=None):
    """Find the next SMA block located on the sheet starting from start_row.
    return(first_row, last_row), where
    first_row is the top row of the table (the one that says "baseline cases", etc.).
    If no block is found, returns None
    """
    x = start_row
    end_search = end_row or ws.max_row
    first_row = None
    last_row = None
    col = co(year_col)

    # Search for the first cell with a numerical value in a vaguely appropriate range
    while x < end_search:
        cell = ws.cell(x, col)
        if cell.data_type == 'n':
            try:
                val = int(cell.value)
            except:
                val = -1
            if val > 1900 and val < 2500:
                first_row = x
                break
        x = x+1
    if first_row is None:
        return None

    # Scan until we come to a row that has something other than a non-zero numerical value.
    # If we wanted to be more rigorous, we'd check that they were increasing integer sequence.
    x = x+1
    while x <= end_search:
        cell = ws.cell(x, col)
        if cell.data_type != 'n' or not cell.value:
            last_row = x-1
            break
        x = x+1
    last_row = last_row or end_search

    # Now if we got less than 10 rows, then this wasn't a real SMA, but some intervening stuff.
    # In that case, skip the stuff and try again.
    if last_row - start_row < 10:
        return find_sma_block(ws, year_col, last_row+1, end_row)
    else:
        # Note the -2!  This backs up from the first year value to the top of the table
        return (first_row-2, last_row)
   

def find_sma_block_title(ws, row, col):
    """Row should point to the top row of the table (the one that says "baseline cases", etc.)
    col should be the column with the years in it.  Returns the region name, or the block title,
    if they are in the standard location."""

    col = co(col) # make sure we've got an integer index

    # check for region names first.
    for i in [5,4,3,2,1]:
        cell = ws.cell(row-i,col-1)
        if cell.value is None:
            continue
        lval = str(cell.value).lower()
        if lval.startswith('region') or lval.startswith('country'):
            val = str(cell.value)
            val = val[ val.index(':')+1: ].strip()
            return normalize_block_name(val)

    # check for titles by going the other way, avoiding empty cells and standard other fields
    for i in [0,1,2,3]:
        cell = ws.cell(row-i,col-1)
        if cell.value is None:
            continue
        lval = str(cell.value).lower()
        if not lval or 'references' in lval or 'sources' in lval or 'back to top' in lval:
            continue
        return normalize_block_name(str(cell.value).strip())
    
    return None


def find_sma_cases(ws, row, year_col, use_functional_unit=False):
    """return a mapping from column number to case name.  Starts at year_col+1 and proceeds right.
    By default it uses the presence of merged cells to detect the cases, and stops at the first 
    empty, unmerged cell.  If this sma isn't using merged cells, set `use_functional_unit` to True,
    and we will check for the presence of the cell with the contents 'Functional Unit' one row down instead."
    Case names are normalized."""

    if use_functional_unit:
        return _find_sma_cases_functional_unit_version(ws, row, year_col)

    year_col = co(year_col)
    currentCase = None
    casemap = {}
    for cell in ws.iter_cols(min_col=year_col+1, min_row=row, max_row=row):
        # we actually get a range back from iter_cols.  dereference
        cell = cell[0]
        if isinstance(cell, openpyxl.cell.cell.MergedCell):
            casemap[cell.column] = currentCase
            # We could raise Value error here if there isn't a current Case
        elif cell.value:
            currentCase = normalize_case_name(cell.value)
            casemap[cell.column] = currentCase
        else:
            break
    return casemap


def _find_sma_cases_functional_unit_version(ws, row, year_col):
    # I just hate embedding magic like "Functional Unit" this deep in the code, but I have to
    # admit is has been a completely reliable indicator in every example I have seen,
    # and I have encountered situations that didn't use merged cells for cases.
    year_col = co(year_col)
    currentCase = None
    casemap = {}
    for cell in ws.iter_cols(min_col=year_col+1, min_row=row, max_row=row):
        cell = cell[0]
        if ws.cell( row+1, cell.column ).value == "Functional Unit":
            break
        if cell.value:
            currentCase = normalize_case_name(cell.value)
        casemap[cell.column] = currentCase
    return casemap


def normalize_block_name(name):
    mapping = {
        'GLOBAL TAM FORECAST' : 'World',
        'GLOBAL INTEGRATED DRAWDOWN TAMS' : 'PDS World',
        'Middle East & Africa' : 'Middle East and Africa',
        'Asia (sans Japan)' : 'Asia (Sans Japan)',
        'EU (region)': 'EU'
    }
    if name in mapping:
        name = mapping[name]
    return name

    

