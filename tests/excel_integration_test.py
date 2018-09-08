"""
excel_integration_test is an end-to-end test which starts a Python flask
HTTP server, starts up a copy of Microsoft Excel, sets the spreadsheet
to reference the local HTTP server for its calculations, fetches key
results from the spreadsheet, and compares them to expected golden
values.
"""

import os.path
import sys
import unittest


excel_present = False
xlwings_present = True


try:
  import xlwings
except ImportError:
  xlwings_present = False


class TestExcelScenarios(unittest.TestCase):
  """Integration tests for Excel <-> HTTP server."""

  excel_files_dir = 'excel'
  workbook = None

  def setUp(self):
    if not excel_present:
      raise unittest.SkipTest('Microsoft Excel not present on this system.')

  def tearDown(self):
    if self.workbook:
      self.workbook.close()
      self.workbook = None

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
    total_emissions_reduction = sheet.range('F4').raw_value
    total_emissions_reduction_expected = 66.5737
    self.assertAlmostEqual(total_emissions_reduction, total_emissions_reduction_expected, places=3)


if __name__ == '__main__':
  if xlwings_present:
    excel_app = xlwings.App()
    if excel_app:
      excel_app.quit()
      excel_present = True
  unittest.main()
