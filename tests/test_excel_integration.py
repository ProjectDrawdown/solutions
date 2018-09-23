"""
excel_integration_test is an end-to-end test which starts a Python flask
HTTP server, starts up a copy of Microsoft Excel, sets the spreadsheet
to reference the local HTTP server for its calculations, fetches key
results from the spreadsheet, and compares them to expected golden
values.
"""

import os.path
import sys
import threading
import time
import urllib.request

import app
import pytest
xlwings = pytest.importorskip("xlwings")


excel_files_dir = os.path.join(os.path.dirname(__file__), 'excel')


def excel_present():
  excel_app_empty = xlwings.App()
  if excel_app_empty:
    excel_app_empty.quit()
    return True


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


@pytest.fixture
def open_excel_file():
  """Pytest fixture to open an Excel file, and cleanly close it at the end."""
  scenario_filename = 'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18.xlsm'
  filename = os.path.join(excel_files_dir, scenario_filename)
  assert os.path.exists(filename)
  workbook = xlwings.Book(filename)
  yield workbook.sheets['Basic Controls']
  excel_app = workbook.app
  workbook.close()
  excel_app.quit()


@pytest.mark.integration
def test_SolarPVUtility_RRS_ELECGEN(open_excel_file):
  """Test for Excel model file SolarPVUtility_RRS_ELECGEN_*."""
  if not excel_present():
    pytest.skip("Microsoft Excel not present")
  sheet = open_excel_file
  total_emissions_reduction = excel_read_cell(sheet, 'F4')
  total_emissions_reduction_expected = 66.5737
  assert total_emissions_reduction == pytest.approx(
      total_emissions_reduction_expected)
