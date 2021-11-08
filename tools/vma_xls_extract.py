from pathlib import Path
import json
import pandas as pd
from tools.util import *

# These are "standard" columns that we pay attention to in a VMA table.
# In some cases there may be additional columns; they will be ignored.
# (Note that model/vma.py renames these columns, and ignores even more of them,
# but for theoretical forward compatibility, we keep the original standard set.)
STANDARD_COLUMNS = [
    "SOURCE ID: Author/Org, Date, Info",
    "Link",
    "World / Drawdown Region",
    "Specific Geographic Location",
    "Source Validation Code",
    "Year / Date",
    "License Code",
    "Raw Data Input",
    "Original Units",
    "Conversion calculation",
    "Common Units",
    "Weight",
    "Assumptions",
    "Exclude Data?"
]

def get_vma_sheet(wb):
    """Return the preferred VMA worksheet in this workbook"""
    if "Variable Meta-analysis-DD" in wb.sheetnames:
        return "Variable Meta-analysis-DD"
    if "Variable Meta-analysis" in wb.sheetnames:
        return "Variable Meta-analysis"
    return None


def extract_vmas(ws, start_column=co("C"), start_row=40):
    """Extract all the non-empty VMAs on the worksheet. Parameters start_column and/or 
    start_row may be set to alternate values if the sheet is not formatted
    in the usual way.  Returns an array of the vmas read, including their data table."""
    tableinfo = find_vma_tables(ws, start_row=start_row, start_column=start_column)
    results = []
    for loc in tableinfo:
        d = get_vma_table_info(ws,*loc)
        if d is not None:
            df = get_vma_table_data(ws,*loc)
            if df is not None:
                d['data'] = df
                results.append(d)
    return results


def write_vmas(vmas_data, outputdir):
    """Write vmas (as returned by extract_vmas) into the specified output directory,
    including writing the directory json file.  Note this will overwrite existing
    files, but will not take into account any other VMA files already in the directory."""
    outputdir = Path(outputdir)
    dirinfo = {}
    filenames = []
    for vma_d in vmas_data:
        vma_name = vma_d['name']
        filename = to_unique_filename(vma_name, filenames, maxlen=60)
        filenames.append(filename)
        vma_d['data'].to_csv(outputdir/filename, encoding='utf-8', index=False)
        dcopy = vma_d.copy()
        del(dcopy['name'])
        del(dcopy['data'])
        dcopy['filename'] = filename
        dirinfo[vma_name] = dcopy
    (outputdir/"vma_sources.json").write_text(json.dumps(dirinfo,indent=2))   


def find_vma_tables(ws, start_row, start_column):
    """Locate the VMAs on a worksheet, starting from the given row and column.
    The column must be the leftmost column of the VMA table proper (the one which
    contains the first column heading).  Returns a list of 
    (firstrow, firstcol, lastrow, lastcol) tuples.  The firstrow indicates the header
    row and lastrow indicates the last (possibly empty) row of the table proper (not
    including the Average, etc., summary at the bottom).  firstcol is just a repeat
    of start_column, and lastcol is the column number of the "Exclude Data?" column.
    Columns after that are ignored."""
    
    # We use the presence of the "SOURCE ID: Author/Org, Date, Info" information to identify
    # the start of the table, and the presence of "**add calc above" in the "Conversion
    # calculation**" column to identify the bottom.  We also assume that all the VMAs on this
    # sheet will have Exclude Data? in the same column, so we don't need to keep searching for
    # it.  Note this returns all VMAs, even if they are empty.

    firstrow = find_in_column(ws, start_column, STANDARD_COLUMNS[0], start_row)
    if firstrow is None:
        raise ValueError("Unable to find any VMA tables on Excel page")

    lastcol = find_in_row(ws, firstrow, "Exclude Data?", start_column)
    if lastcol is None:
        # sometimes the column gets renamed.  Scan for it where it should be instead.
        for i in range(start_column+10, start_column+16):
            if "Exclude" in str(ws.cell[firstrow, i].value):
                lastcol = i
        else:
            raise ValueError("Unable to find last column of VMA table at " + str(firstrow))
    
    checkcol = find_in_row(ws, firstrow, "Conversion calculation**", start_column)
    if checkcol is None:
        raise ValueError("Unable to find 'Conversion calculation column' in VMA at " + str(firstrow))

    result = []
    while firstrow is not None:
        # To minimize the possibility of mistakenly finding a range that spans multiple tables,
        # we actually look for the next table first, then look for the end of this table before that.
        next_firstrow = find_in_column(ws, start_column, STANDARD_COLUMNS[0], start_row=firstrow+1)
        lastrow = find_in_column(ws, checkcol, "**Add calc above", start_row=firstrow+1, end_row=next_firstrow)
        if lastrow is None:
            raise ValueError("Unable to find end of VMA table at " + str(firstrow))
        result.append((firstrow, start_column, lastrow-1, lastcol))
        firstrow = next_firstrow
    
    return result


def get_vma_table_info(ws, firstrow, firstcol, lastrow, lastcol):
    """Return the ancillary information that surrounds the VMA table.  Returns a dictionary
    containing:
        name: the name of the VMA
        use_weight:  the value of the "Use weight?" field
        bound_correction:  the value of the "Low Correction?" field
        description: the value of the table "Explanation" field
        units: the units of the VMA.
    Returns None if the name is a "template" name (indicating an empty table)."""
    # VMA table structure tends to be pretty reliable, but we use some flexibility in finding
    # these bits anyway.
    
    # name: first non-empty string upwards from table start
    for i in range(1,5):
        name = xls(ws,firstrow-i,firstcol)
        if name:
            break
    else:
        raise ValueError("Unable to find name of VMA at " + str(firstrow))
    
    if name.startswith("VARIABLE"):
        return None
    result = { 'name': normalize_vma_name(name) }
    
    # use weight
    row = find_in_column(ws, lastcol+1, "Use weight?", start_row=lastrow)
    if row is None or row-lastrow > 12:
        raise ValueError("Unable to locate 'Use Weight?' of VMA at " + str(firstrow))
    result['use_weight'] = convert_bool(xls(ws, row+1, lastcol+1))

    # bound correction
    col = find_in_row(ws, lastrow+2, "Low Correction?", start_col=lastcol)
    if col is None or col-lastcol > 10:
        raise ValueError("Unable to locate 'Low Correction?' of VMA at " + str(firstrow))
    result['bound_correction'] = convert_bool(xls(ws,lastrow+3,col))

    # description
    row = find_in_column(ws, firstcol, "Explanation:", start_row=lastrow)
    if row is None or row-lastrow > 5:     # if not found, no error, just skip
        pass
    else:
        result['description'] = xls(ws, row, firstcol+1)
        
    # units
    col = find_in_row(ws, firstrow, "Common Units", start_col=firstcol)
    if col is None or col > lastcol:
        raise ValueError("Unable to locate units column of VMA at " + str(firstrow))
    result['units'] = xls(ws, firstrow+1, col)

    return result


def get_vma_table_data(ws, firstrow, firstcol, lastrow, lastcol, drop_extra_cols=True):
    """Return the vma data from the table as a pandas DataFrame.  Removes empty rows and
    cleans some column names and data values.  By default drops any columns not in the
    standard list.  Returns None if the dataframe is empty."""
    
    headers = [normalize_col_name(h) for h in read_row(ws, firstrow, firstcol, lastcol)]
    data = read_range(ws, firstrow+1, firstcol, lastrow, lastcol)
    df = pd.DataFrame(data, columns=headers)

    # drop columns we don't want
    if drop_extra_cols:
        keepheaders = [ h for h in headers if h in STANDARD_COLUMNS ]
        df = df.reindex(columns=keepheaders)
    
    # if we don't have all the columns, something is wrong.  complain.
    # note: we don't really need all the columns, so we could be more lenient, but
    # complaining is a good idea because we really do expect to get them all.
    if len(df.columns) < len(STANDARD_COLUMNS):
        missing = set(STANDARD_COLUMNS) - set(df.columns)
        raise ValueError(f"VMA table at {firstrow} missing column(s) {str(missing)}")

    # drop rows we don't want.
    # keep a row only if it has a value in at least one of the 'Raw Data Input' or 'Conversion calculation' columns
    hasraw_data = df["Raw Data Input"].notnull()
    hasconv_data = df["Conversion calculation"].notnull()
    df = df.loc[ hasraw_data.add(hasconv_data) ]  # pandas doesn't have element-wise 'or', but 'add' works
    if len(df) == 0:
        return None
    
    # data cleaning/conversion for a few columns
    def tryint(x):
        try: return int(x)
        except: return x

    df["World / Drawdown Region"] = [ normalize_region_name(x) for x in df["World / Drawdown Region"] ]
    df["Year / Date"] = [ tryint(x) for x in df["Year / Date"] ]    # openpyxl reads numbers as floats...
    df["Exclude Data?"] = [ convert_bool(x,accept_empty=True) for x in df["Exclude Data?"] ]

    return df


def normalize_col_name(name):
    if name is None:
        return None
    substitutions = {
        # someone did a global replace of 'version' with 'edition' in Conservation Ag.
        'Conedition calculation': 'Conversion calculation',
        # Airplanes removed Geographic Location from one of the VMAs.
        'Specific': 'Specific Geographic Location',
        # This one isn't an error, its just how we normalize it
        'Conversion calculation**': 'Conversion calculation'
    }
    name = name.strip()
    if name in substitutions:
        return substitutions[name]
    if "Exclude" in name:
        return "Exclude Data?"
    if "Weight" in name:
        return "Weight"
    return name

def normalize_vma_name(name):
    """Substitute standardized VMA names for common variations"""
    substitutions = {
        'SOLUTION First Cost per Implementation Unit of the solution':
            'SOLUTION First Cost per Implementation Unit',
        'CONVENTIONAL First Cost per Implementation Unit for replaced practices/technologies':
            'CONVENTIONAL First Cost per Implementation Unit',
        'Yield  from CONVENTIONAL Practice': 'Yield from CONVENTIONAL Practice',
        'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE on Advanced Controls':
            'CONVENTIONAL Indirect CO2 Emissions per Unit',
        'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE':
            'CONVENTIONAL Indirect CO2 Emissions per Unit',
        'Indirect CO2 Emissions per SOLUTION Implementation Unit (Select on Advanced Controls)':
            'SOLUTION Indirect CO2 Emissions per Unit',
        'ALTERNATIVE APPROACH      Annual Energy Used UNDEGRADED LAND':
            'ALTERNATIVE APPROACH Annual Energy Used UNDEGRADED LAND',
        'SOLUTION VARIABLE Operating Cost per Functional Unit':
            'SOLUTION Variable Operating Cost (VOM) per Functional Unit',
        'SOLUTION FIXED Operating Cost per Implementation Unit':
            'SOLUTION Fixed Operating Cost (FOM)',
        'CONVENTIONAL VARIABLE Operating Cost per Functional Unit':
            'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit',
        'CONVENTIONAL FIXED Operating Cost per Implementation Unit':
            'CONVENTIONAL Fixed Operating Cost (FOM)',
        'Fuel Consumed per Functional Unit - CONVENTIONAL':
            'CONVENTIONAL Fuel Consumed per Functional Unit',
        'Total Energy Used per functional unit - SOLUTION':
            'SOLUTION Total Energy Used per Functional Unit',
        'Electricity Consumed per Functional Unit - CONVENTIONAL':
            'CONVENTIONAL Total Energy Used per Functional Unit',
        'Electricty Consumed per Functional Unit - CONVENTIONAL':
            'CONVENTIONAL Total Energy Used per Functional Unit',
        'Fuel Efficiency Factor - SOLUTION': 
            'SOLUTION Fuel Efficiency Factor',
        'Energy Efficiency Factor - SOLUTION':
            'SOLUTION Energy Efficiency Factor',
        'Direct Emissions per CONVENTIONAL Functional Unit':
            'CONVENTIONAL Direct Emissions per Functional Unit',
        'Direct Emissions per SOLUTION Functional Unit':
            'SOLUTION Direct Emissions per Functional Unit',
        'Lifetime Capacity - SOLUTION':
            'SOLUTION Lifetime Capacity',
        'Lifetime Capacity - CONVENTIONAL':
            'CONVENTIONAL Lifetime Capacity',
        'Average Annual Use - SOLUTION':
            'SOLUTION Average Annual Use',
        'Average Annual Use - CONVENTIONAL':
            'CONVENTIONAL Average Annual Use',
    }
    return substitutions.get(name,name)
