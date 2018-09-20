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
import unittest
import urllib.request

import app


excel_present = False
xlwings_present = True


try:
  import xlwings
except ImportError:
  xlwings_present = False

if xlwings_present:
  excel_app_empty = xlwings.App()
  if excel_app_empty:
    excel_app_empty.quit()
    excel_present = True
  else:
    print("Microsoft Excel not present, skipping tests.")
else:
  print("xlwings not present, skipping tests.")


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



def run_flask(flask_app):
  """Start a flask server, for use as the main routine in a thread.

  auto-reloader on code change only works in main thread, so disable it.

  TODO: should choose a random port, to allow multiple instances of the
  test to run (for example for continuous integration). Flask does not
  make it easy to choose a random port.
  """
  flask_app.add_url_rule('/quitquitquit', 'quit', view_func=app.shutdown)
  flask_app.run(debug=True, use_reloader=False)


class TestExcelScenarios(unittest.TestCase):
  """Integration tests for Excel <-> HTTP server."""

  excel_files_dir = os.path.dirname(__file__) + os.path.sep + 'excel'
  flask_app_thread = None
  workbook = None

  def setUp(self):
    if not excel_present:
      raise unittest.SkipTest('Microsoft Excel not present on this system.')
    flask_app = app.get_app_for_tests()
    self.flask_app_thread = threading.Thread(target=run_flask, args=(flask_app,))
    self.flask_app_thread.start()

  def tearDown(self):
    if self.workbook:
      excel_app = self.workbook.app
      self.workbook.close()
      self.workbook = None
      excel_app.quit()
    if self.flask_app_thread:
      with urllib.request.urlopen('http://localhost:5000/quitquitquit') as response:
        _ = response.read()
      self.flask_app_thread.join()

  def open_excel_file(self, filename, sheet_name='Sheet1'):
    """Open an Excel workbook, and prepare to close it automatically later."""
    self.workbook = xlwings.Book(filename)
    return self.workbook.sheets[sheet_name]

  def test_SolarPVUtility_RRS_ELECGEN(self):
    """Test for Excel model file SolarPVUtility_RRS_ELECGEN_*."""
    scenario_filename = 'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18.xlsm'
    filename = os.path.join(self.excel_files_dir, scenario_filename)
    self.assertTrue(os.path.exists(filename))
    sheet = self.open_excel_file(filename=filename, sheet_name='Basic Controls')
    total_emissions_reduction = excel_read_cell(sheet, 'F4')
    total_emissions_reduction_expected = 66.5737
    self.assertAlmostEqual(total_emissions_reduction, total_emissions_reduction_expected, places=3)


if __name__ == '__main__':
  unittest.main()
