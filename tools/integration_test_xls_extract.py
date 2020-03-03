"""Extract values and results from Excel for use in tests/test_excel_integration.py"""

import argparse
import glob
import os.path
import pathlib
import shutil
import sys
import time
import tempfile
import pandas as pd
import xlrd
import zipfile


class ExcelAccessFailed(TimeoutError):
    """Raised if we timeout communicating with Microsoft Excel."""
    pass

# pylint: disable=import-error
if sys.platform == 'darwin':  # MacOS
    import appscript.reference
    ExcelTimeoutException = appscript.reference.CommandError
else:
    ExcelTimeoutException = None


def excel_read_cell_xlwings(sheet, cell_name):
    """Retry reading from Excel a few times, work around flakiness."""
    for _ in range(0, 5):
        try:
            return sheet.range(cell_name).value
        except ExcelTimeoutException:
            time.sleep(1)
    raise ExcelAccessFailed


def excel_write_cell_xlwings(sheet, cell_name, value):
    """Retry writing to Excel a few times, work around flakiness."""
    for _ in range(0, 20):
        try:
            sheet.range(cell_name).value = value
            return
        except ExcelTimeoutException:
            time.sleep(1)
    raise ExcelAccessFailed


def get_scenario_names(excelfile):
    wb = xlrd.open_workbook(filename=excelfile, on_demand=True)
    sr_tab = wb.sheet_by_name('ScenarioRecord')
    scenarios = []
    for row in range(1, sr_tab.nrows):
        col_d = sr_tab.cell_value(row, 3)
        col_e = sr_tab.cell_value(row, 4)
        if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:
            # start of scenario block
            scenarios.append(col_e)
    return scenarios


def extract_xls_scenario(workbook, zip_f, scenario, tmpdir):
    sheet = workbook.sheets['ScenarioRecord']
    excel_write_cell_xlwings(sheet, 'B9', scenario)
    macro = workbook.macro("LoadScenario_Click")
    macro()
    _ = excel_read_cell_xlwings(sheet, 'B9')
    workbook.app.calculate()
    workbook.save()

    # there are a few tabs which we're never going to compare against Python results, and
    # therefore don't need to extract.
    skiplist = ['Welcome', 'Data Interpolator', 'Regions-Countries sorting', 'XLLang',
            'WORLD Land Data', 'Land Allocation - Max TLA', 'TLA Data', 'Adoption Factoring']

    wb = xlrd.open_workbook(filename=workbook.filepath, on_demand=True)
    for sheet_name in wb.sheet_names():
        if sheet_name in skiplist:
            continue
        sheet = wb.sheet_by_name(sheet_name)
        df = pd.read_excel(wb, engine='xlrd', sheet_name=sheet_name, header=None, index_col=None,
                usecols=range(sheet.ncols + 1), skiprows=0, nrows=sheet.nrows)
        (_, csvfile) = tempfile.mkstemp(dir=tmpdir)
        df.to_csv(path_or_buf=csvfile, header=False, index=False, compression=None)
        arcname = scenario + '/' + sheet_name
        zip_f.write(filename=csvfile, arcname=arcname)
        os.unlink(csvfile)


def extract_xls(excelfile, zipfilename, tmpdir):
    if sys.platform == 'linux':
        raise EnvironmentError('extract_xls requires xlwings which is only supported on Windows and macOS')

    import xlwings

    (_, tmpfile) = tempfile.mkstemp(suffix='.xlsm', dir=tmpdir, prefix='intg_test_xls_extract_')
    shutil.copyfile(excelfile, tmpfile)
    scenarios = get_scenario_names(tmpfile)
    print(f'Processing {tmpfile}')
    workbook = xlwings.Book(tmpfile)
    workbook.filepath = tmpfile
    workbook.app.visible = False
    # ZIP_LZMA and ZIP_BZIP2 give better compression but are not supported by the MacOS zip client
    # so we use ZIP_DEFLATED for maximum compatibility
    zip_f = zipfile.ZipFile(file=zipfilename, mode='w', compression=zipfile.ZIP_DEFLATED)

    for scenario in scenarios:
        print(f'Processing {scenario}')
        extract_xls_scenario(workbook=workbook, zip_f=zip_f, scenario=scenario, tmpdir=tmpdir)

    workbook.close()
    workbook.app.quit()
    os.unlink(tmpfile)
    zip_f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract expected values for test_excel_integration.py from Excel version.')
    parser.add_argument('--excelfile', help='Excel filename to process')
    parser.add_argument('--solutiondir', default=None, required=True, help='Solution directory')
    args = parser.parse_args(sys.argv[1:])
    outputdirpath = pathlib.Path(args.solutiondir).joinpath('testdata')
    outputdirpath.mkdir(parents=True, exist_ok=True)

    if args.excelfile is None:
        files = list(glob.glob(str(outputdirpath.joinpath('[!~]*.xlsm'))))
        if len(files) == 1:
            args.excelfile = files[0]
            print(f'Using excelfile: {str(args.excelfile)}')
    if not os.path.exists(args.excelfile):
        raise ValueError(f'No such Excel file: {args.excelfile}')

    zipfilename = outputdirpath.joinpath('expected.zip')

    tmpdirobj = None
    if sys.platform == 'darwin':
        tmpdir = str(os.path.join(os.path.expanduser("~"), 'Library', 'Containers',
            'com.microsoft.Excel', 'Data'))
    else:
        tmpdirobj = tempfile.TemporaryDirectory(prefix='intg_test_xls_extract_')
        tmpdir = tmpdirobj.name

    extract_xls(excelfile=args.excelfile, zipfilename=zipfilename, tmpdir=tmpdir)

    if tmpdirobj:
        tmpdirobj.cleanup()
