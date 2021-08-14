# This file will reconstruct a Excel workbook from expected.zip
# The spreadsheet contains only a single scenario, and none of the formulas, formatting, charts, etc. of the
# original workbook.  This "ghost" of the original workbook may be useful when debugging.
# When loaded as a package, the Workbook can be created and accessed in-memory.
# When run as a script, the workbook will create an Excel file "ghost.xlsx"
import zipfile
import openpyxl
import argparse
import csv
from io import StringIO
from pathlib import Path

def locate_expected_zip(solution):
    # Walk to the solution's directory from this code directory.  
    # This enables this script to be run regardless of cwd.
    #path = Path(__file__).parents[2] / 'solution' / solution
    path = Path(__file__).parents[1] / 'solution' / solution
    if not path.is_dir():
        raise ValueError(f"Cannot find solution {solution} at {path}")
    path = path / 'tests' / 'expected.zip'
    if not path.is_file():
        raise ValueError(f"Solution {solution} does not have an expected.zip file at {path}")
    return path


def typeit(val):
    """Given a string val from csv, try to convert it to a number"""
    try:
        out = int(val)
        return out
    except ValueError:
        try:
            out = float(val)
            return out
        except ValueError:
            return val

def create_ghost(filename, scenario_number):
    # The expected.zip files include extra sheets that we don't need.
    # Keep only sheets in this list.
    wanted = ["Advanced Controls", "ScenarioRecord", "Variable Meta-Analysis", 
                "TAM Data", "TLA Data", "AEZ Data", 
                "Adoption Data", "Custom PDS Adoption", "Custom REF Adoption", "S-Curve Adoption", 
                "Helper Tables", "Unit Adoption Calculations", 
                "First Cost", "Operating Cost", "Net Profit Margin", 
                "Emissions Factors", "CO2 Calcs", "CH4 Calcs"]
    
    # Use zipfile.Path to navigate to the top-level directory of the zip file,
    # which lists all the scenarios.
    zipdir = zipfile.Path(filename)
    scenariopaths = list(zipdir.iterdir())
    ourscenario = scenariopaths[scenario_number]

    wb = openpyxl.Workbook()
    
    # get the sheets from the subdirectory for our scenario
    for sheetpath in ourscenario.iterdir():
        # create a new sheet in the workbook
        sheetname = sheetpath.name
        if sheetname not in wanted:
            continue

        wbsheet = wb.create_sheet(sheetname)

        # read the entire sheet into memory
        pagedata = sheetpath.read_text(encoding='utf-8')
        reader = csv.reader(StringIO(pagedata))
        # copy it to the worksheet, row by row
        for row in reader:
            wbsheet.append([typeit(x) for x in row])

    return wb
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Exhume ghost workbook from expected.zip file.  One of the arguments --solution or --file must be provided')
    parser.add_argument('--solution', required=False, help='Name of the solution whose expected.zip we should exhume.')
    parser.add_argument('--file', required=False, help='Path to an expected.zip file')
    parser.add_argument('--scenario', type=int, default=0, required=False, help='Offset of which scenario to exhume; defaults to 0')
    args = parser.parse_args()

    if args.solution and args.file:
        raise ValueError('Only one of --solution or --file can be specified')
    
    if not (args.solution or args.file):
        raise ValueError('One of --solution or --file must be specified')
    
    path = args.file or locate_expected_zip(args.solution)
    ghost = create_ghost(path, args.scenario)
    ghost.save(filename="ghost.xlsx")