"""
excel_integration_test is an end-to-end test which starts a Python flask
HTTP server, starts up a copy of Microsoft Excel, sets the spreadsheet
to reference the local HTTP server for its calculations, fetches key
results from the spreadsheet, and compares them to expected golden
values.
"""

import os.path
import pathlib
import sys
import threading
import time
import urllib.request

import pandas as pd
import pytest
import app
xlwings = pytest.importorskip("xlwings")


excel_orig_files_dir = os.path.join(os.path.dirname(__file__), 'excel')
excel_mod_files_dir = os.path.join(str(pathlib.Path(
    os.path.dirname(__file__)).parents[0]), 'ddexcel_models')


def excel_present():
  """Returns true if Microsoft Excel can successfully start."""
  excel_app_empty = xlwings.App()
  if excel_app_empty:
    excel_app_empty.quit()
    return True
  return False


class ExcelAccessFailed(TimeoutError):
  """Raised if we timeout communicating with Microsoft Excel."""
  pass


if sys.platform == 'darwin':  # MacOS
  import appscript.reference
  ExcelTimeoutException = appscript.reference.CommandError
else:
  ExcelTimeoutException = None


def excel_read_cell(sheet, cell_name):
  """Retry reading from Excel a few times, work around flakiness."""
  for _ in range(0, 5):
    try:
      return sheet.range(cell_name).raw_value
    except ExcelTimeoutException:
      time.sleep(1)
  raise ExcelAccessFailed



def excel_write_cell(sheet, cell_name, value):
  """Retry writing to Excel a few times, work around flakiness."""
  for _ in range(0, 20):
    try:
      sheet.range(cell_name).value = value
      return
    except ExcelTimeoutException:
      time.sleep(1)
  raise ExcelAccessFailed


def _run_flask(flask_app):
  """Start a flask server, for use as the main routine in a thread.

  auto-reloader on code change only works in main thread, so disable it.

  TODO: should choose a random port, to allow multiple instances of the
  test to run (for example for continuous integration). Flask does not
  make it easy to choose a random port.
  """
  flask_app.add_url_rule('/quitquitquit', 'quit', view_func=app.shutdown)
  flask_app.run(debug=True, use_reloader=False)


@pytest.fixture
def start_flask():
  """Pytest fixture to start a local flask server, and stop it at the end."""
  flask_app = app.get_app_for_tests()
  flask_app_thread = threading.Thread(target=_run_flask, args=(flask_app,))
  flask_app_thread.start()
  yield  # test case will run here.
  with urllib.request.urlopen('http://localhost:5000/quitquitquit') as response:
    _ = response.read()
  flask_app_thread.join()


def diff_dataframes(d1, d2):
  """Print where two dataframes differ, useful for debugging pd.testing.assert_frame_equal."""
  nerrors = 0
  (nrows, ncols) = d1.shape
  for r in range(nrows):
    for c in range(ncols):
      matches = True
      if isinstance(d1.iloc[r,c], str) or isinstance(d2.iloc[r,c], str):
        matches = (d1.iloc[r,c] == d2.iloc[r,c])
      else:
        matches = (d1.iloc[r,c] == pytest.approx(d2.iloc[r,c]))
      if not matches:
        print("Err [" + str(r) + "][" + str(c) + "] : " + str(d1.iloc[r,c]) + " != " + str(d2.iloc[r,c]))
        nerrors += 1
      if nerrors > 10:
        break


@pytest.mark.integration
def test_SolarPVUtility_RRS_ELECGEN(start_flask):
  """Test for Excel model file SolarPVUtility_RRS_ELECGEN_*."""
  if not excel_present():
    pytest.skip("Microsoft Excel not present")
  scenario_filename = 'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18.xlsm'
  filename = os.path.join(excel_orig_files_dir, scenario_filename)
  assert os.path.exists(filename)
  workbook = xlwings.Book(filename)
  excel_app = workbook.app
  sheet = workbook.sheets['First Cost']
  fc_expected_values = pd.DataFrame(excel_read_cell(sheet, 'B37:R82'))
  sheet = workbook.sheets['Unit Adoption Calculations']
  excel_write_cell(sheet, 'Q307', 'Year')
  excel_write_cell(sheet, 'AT307', 'Year')
  excel_write_cell(sheet, 'BF307', 'Year')
  excel_write_cell(sheet, 'BR307', 'Year')
  ua_expected_values1 = pd.DataFrame(excel_read_cell(sheet, 'P16:CI115'))
  ua_expected_values2 = pd.DataFrame(excel_read_cell(sheet, 'B134:CB354'))
  workbook.close()
  excel_app.quit()

  scenario_filename = 'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18_VBAWEB.xlsm'
  filename = os.path.join(excel_mod_files_dir, scenario_filename)
  assert os.path.exists(filename)
  workbook = xlwings.Book(filename)
  excel_app = workbook.app
  sheet = workbook.sheets['ExtModelCfg']
  excel_write_cell(sheet, 'B23', 1)  # USE_LOCAL_SERVER
  excel_write_cell(sheet, 'B21', 0)  # DEBUG_LEVEL
  macro = workbook.macro("AssignNetFunctionalUnits")
  macro()
  time.sleep(5)
  sheet = workbook.sheets['First Cost']
  fc_actual_values = pd.DataFrame(excel_read_cell(sheet, 'B37:R82'))
  sheet = workbook.sheets['Unit Adoption Calculations']
  ua_actual_values1 = pd.DataFrame(excel_read_cell(sheet, 'P16:CI115'))
  ua_actual_values2 = pd.DataFrame(excel_read_cell(sheet, 'B134:CB354'))
  workbook.close()
  excel_app.quit()

  pd.testing.assert_frame_equal(fc_actual_values, fc_expected_values, check_exact=False)
  pd.testing.assert_frame_equal(ua_actual_values1, ua_expected_values1, check_exact=False)
  pd.testing.assert_frame_equal(ua_actual_values2, ua_expected_values2, check_exact=False)
