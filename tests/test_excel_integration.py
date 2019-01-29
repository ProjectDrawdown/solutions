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
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
import pytest
import app
xlwings = pytest.importorskip("xlwings")

from solution import solarpvutil
from solution import solarpvroof

solutiondir = pathlib.Path(__file__).parents[1].joinpath('solution')


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
  msg = ''
  for r in range(nrows):
    for c in range(ncols):
      matches = True
      if isinstance(d1.iloc[r,c], str) or isinstance(d2.iloc[r,c], str):
        matches = (d1.iloc[r,c] == d2.iloc[r,c])
      else:
        matches = (d1.iloc[r,c] == pytest.approx(d2.iloc[r,c]))
      if not matches:
        msg += "Err [" + str(r) + "][" + str(c) + "] : " + \
            str(d1.iloc[r,c]) + " != " + str(d2.iloc[r,c]) + '\n'
        nerrors += 1
      if nerrors > 10:
        break
  return msg


def _rrs_test(solution, scenario, filename, ch4_calcs=False):
  assert os.path.exists(filename)
  workbook = xlwings.Book(filename)
  excel_app = workbook.app
  #excel_app.display_alerts = False
  excel_app.visible = False
  sheet = workbook.sheets['ScenarioRecord']
  excel_write_cell(sheet, 'B9', scenario)
  macro = workbook.macro("LoadScenario_Click")
  macro()
  excel_app.calculate()
  verify = {}
  adjustments = {}
  expected = {}
  adjustments['TAM Data'] = [('B45', 'Year'), ('B163', 'Year'), ('B227', 'Year'),
      ('B290', 'Year'), ('B353', 'Year'), ('B416', 'Year'), ('B479', 'Year'),
      ('B543', 'Year'), ('B607', 'Year'), ('B672', 'Year'), ('Y103', 'S.D'),
      ('AB103', 'Medium'),]
  verify['TAM Data'] = ['B45:Q94', 'L103:N152', 'B163:Q212', 'B227:Q276',
      'B290:Q339', 'B353:Q402', 'B416:Q465', 'B479:Q528', 'B543:Q592', 'B607:Q656',
      'B672:Q721', 'W44:Y94', 'W103:Y152', 'W163:Y212', 'W227:Y276', 'W290:Y339',
      'W353:Y402', 'W416:Y465', 'W479:Y528', 'W543:Y592', 'W607:Y656', 'W672:Y721',
      'AA44:AC94', 'AA103:AC152', 'AA163:AC212', 'AA227:AC276', 'AA290:AC339', 'AA353:AC402',
      'AA416:AC465', 'AA479:AC528', 'AA543:AC592', 'AA607:AC656', 'AA672:AC721',
      'BX50:BZ96', 'BX168:BZ214', 'BX232:BZ278', 'BX295:BZ341', 'BX358:BZ404',
      'BX421:BZ467', 'BX484:BZ530', 'BX548:BZ594', 'BX612:BZ658', 'BX677:BZ723',
      'CE50:CH96', 'CE168:CH214', 'CE232:CH278', 'CE295:CH341', 'CE358:CH404',
      'CE421:CH467', 'CE484:CH530', 'CE548:CH594', 'CE612:CH658', 'CE677:CH723',
      'CM50:CQ96', 'CM168:CQ214', 'CM232:CQ278', 'CM295:CQ341', 'CM358:CQ404',
      'CM421:CQ467', 'CM484:CQ530', 'CM548:CQ594', 'CM612:CQ658', 'CM677:CQ723',
      'CV50:CX96', 'CV168:CX214', 'CV232:CX278', 'CV295:CX341', 'CV358:CX404',
      'CV421:CX467', 'CV484:CX530', 'CV548:CX594', 'CV612:CX658', 'CV677:CX723']
  adjustments['Adoption Data'] = [('B45', 'Year'),]
  verify['Adoption Data'] = ['B45:R94', 'X45:Z94', 'AB45:AD94', 'BY50:CA96',
      'CF50:CI96', 'CN50:CR96', 'CW50:CY96',]
  adjustments['Unit Adoption Calculations'] = [
      ('A16', 'Year'), ('A68', 'Year'), ('Q307', 'Year'),
      ('AT307', 'Year'), ('BF307', 'Year'), ('BR307', 'Year'),]
  verify['Unit Adoption Calculations'] = ['P16:CI115', 'Q134:AA181', 'AG135:BS182',
      'Q197:BH244', 'B251:BH298', 'B307:CB354',]
  adjustments['Helper Tables'] = []
  verify['Helper Tables'] = ['B26:L73', 'B90:L137',]
  adjustments['First Cost'] = []
  verify['First Cost'] = ['B37:R82',]
  adjustments['Operating Cost'] = [('A125', 'Year'),]
  verify['Operating Cost'] = ['A18:F64', 'A125:F250', 'B262:AV386', 'I126:P250',]
  verify['Operating Cost'] = ['B262:AV386', 'I126:P250', 'A125:F250', 'A18:F64',]
  adjustments['Emissions Factors'] = [('A11', 'Year'), ('A66', 'Year'),]
  verify['Emissions Factors'] = ['A11:K112',]
  adjustments['CO2 Calcs'] = [('A9', 'Year'), ('A64', 'Year'), ('A234', 'Year'),
      ('R234', 'Year'), ('AI234', 'Year'), ('A288', 'Year'), ('R288', 'Year'),
      ('AI288', 'Year'), ('A344', 'Year'), ('U344', 'Year'), ('AP344', 'Year')]
  verify['CO2 Calcs'] = ['A9:AW390',]
  if ch4_calcs:
    # Some solutions have the CH4 Calcs tab hidden and containing only #VALUE errors.
    sheet = workbook.sheets['CH4 Calcs']
    adjustments['CH4 Calcs'] = []
    verify['CH4 Calcs'] = ['A10:AW110']

  for sheetname, adjustment_list in adjustments.items():
    sheet = workbook.sheets[sheetname]
    for (cell, value) in adjustment_list:
      excel_write_cell(sheet, cell, value)
  for sheetname, cells in verify.items():
    sheet = workbook.sheets[sheetname]
    expected[sheetname] = {}
    for c in cells:
      expected[sheetname][c] = pd.DataFrame(excel_read_cell(sheet, c))
  workbook.close()
  excel_app.quit()

  # Perform some rewrites where the Python convention differs from Excel.
  #
  # Original uses 1=True and ""=False, but we want to use 0=False
  expected['Operating Cost']['I126:P250'].replace(to_replace="", value=0, inplace=True)
  # Original Excel uses "" for empty cells, we want to use 0.0.
  expected['CO2 Calcs']['A9:AW390'].replace(to_replace="", value=0, inplace=True)
  expected['Unit Adoption Calculations']['AG135:BS182'].replace(to_replace="", value=0, inplace=True)
  if ch4_calcs:
    expected['CH4 Calcs']['A10:AW110'].replace(to_replace="", value=0, inplace=True)

  for _, modulevalues in expected.items():
    for _, df in modulevalues.items():
      try:
        df.replace(inplace=True,
            to_replace=['Baseline: Based on-  AMPERE MESSAGE-MACRO Reference',
                        'Conservative: Based on-  IEA ETP 2016 4DS',
                        ' Ambitious: Based on- AMPERE GEM E3 450',
                        'Asia (sans Japan)', 'Middle East & Africa',],
            value=['Baseline: Based on- AMPERE MESSAGE-MACRO Reference',
                        'Conservative: Based on- IEA ETP 2016 4DS',
                        'Ambitious: Based on- AMPERE GEM E3 450',
                        'Asia (Sans Japan)', 'Middle East and Africa',])
      except TypeError:
        pass

  filename = 'RRS_VBAWEB.xlsm'
  assert os.path.exists(filename)
  workbook = xlwings.Book(filename)
  excel_app = workbook.app
  excel_app.display_alerts = False
  excel_app.visible = False
  sheet = workbook.sheets['ExtModelCfg']
  excel_write_cell(sheet, 'B23', 1)  # USE_LOCAL_SERVER
  excel_write_cell(sheet, 'B21', 0)  # DEBUG_LEVEL
  macro = workbook.macro("FetchJsonFromDrawdown")
  resource = urllib.parse.urlencode({'scenario': scenario})
  macro(solution + '?' + resource)
  excel_app.calculate()

  actual = {}
  for sheetname, cells in verify.items():
    sheet = workbook.sheets[sheetname]
    actual[sheetname] = {}
    for c in cells:
      actual[sheetname][c] = pd.DataFrame(excel_read_cell(sheet, c))
  # Original Excel uses "" for empty cells, we want to use 0.0 and have to match in *all* cells.
  actual['CO2 Calcs']['A9:AW390'].replace(to_replace="", value=0, inplace=True)
  actual['Unit Adoption Calculations']['AG135:BS182'].replace(to_replace="", value=0, inplace=True)
  actual['Helper Tables']['B90:L137'].replace(to_replace="", value=0, inplace=True)

  workbook.close()
  excel_app.quit()

  for sheetname, values in expected.items():
    for (cells, expected_df) in values.items():
      actual_df = actual[sheetname][cells]
      try:
        pd.testing.assert_frame_equal(actual_df, expected_df, check_exact=False)
      except AssertionError as e:
        msg = "Solution: " + solution + " Scenario: " + scenario + "\n"
        msg += "DataFrames differ: " + sheetname + " " + cells + ":\n"
        msg += diff_dataframes(actual_df, expected_df)
        raise AssertionError(msg)

@pytest.mark.integration
def test_SolarPVUtility_RRS_ELECGEN(start_flask):
  """Test for Excel model file SolarPVUtility_RRS_ELECGEN_*."""
  if not excel_present():
    pytest.skip("Microsoft Excel not present")
  for scenario in solarpvutil.scenarios.keys():
    _rrs_test(solution='solarpvutil', scenario=scenario,
        filename=str(solutiondir.joinpath('solarpvutil', 'testdata',
          'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18.xlsm')))

@pytest.mark.integration
def disabled_test_SolarRooftop_RRS_ELECGEN(start_flask):
  """Test for Excel model file SolarPVRooftop_RRS_ELECGEN_*."""
  if not excel_present():
    pytest.skip("Microsoft Excel not present")
  for scenario in solarpvroof.scenarios.keys():
    _rrs_test(solution='solarpvroof', scenario=scenario,
        filename=str(solutiondir.joinpath('solarpvroof', 'testdata',
          'SolarPVRooftop_RRS_ELECGEN_v1.1b_24Oct18.xlsm')))
