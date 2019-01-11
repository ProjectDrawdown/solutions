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
  scenarios = ['PDS3-16p2050-Optimum (Updated)', 'PDS2-15p2050-Drawdown (Updated)',
      'PDS1-10p2050-Plausible (Updated)', 'PDS-16p2050- Optimum (Book Ed.1)',
      'PDS-15p2050- Drawdown (Book Ed.1)', 'PDS-10p2050- Plausible (Book Ed.1)']
  for scenario in scenarios:
    print(scenario)
    solution_filename = 'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18.xlsm'
    filename = os.path.join(excel_orig_files_dir, solution_filename)
    assert os.path.exists(filename)
    workbook = xlwings.Book(filename)
    excel_app = workbook.app
    excel_app.display_alerts = False
    excel_app.visible = False
    sheet = workbook.sheets['ScenarioRecord']
    excel_write_cell(sheet, 'B9', scenario)
    macro = workbook.macro("LoadScenario_Click")
    macro()
    excel_app.calculate()
    sheet = workbook.sheets['First Cost']
    fc_expected_values = pd.DataFrame(excel_read_cell(sheet, 'B37:R82'))
    sheet = workbook.sheets['Unit Adoption Calculations']
    excel_write_cell(sheet, 'A16', 'Year')
    excel_write_cell(sheet, 'A68', 'Year')
    excel_write_cell(sheet, 'Q307', 'Year')
    excel_write_cell(sheet, 'AT307', 'Year')
    excel_write_cell(sheet, 'BF307', 'Year')
    excel_write_cell(sheet, 'BR307', 'Year')
    ua_expected_values1 = pd.DataFrame(excel_read_cell(sheet, 'P16:CI115'))
    ua_expected_values2 = pd.DataFrame(excel_read_cell(sheet, 'B134:CB182'))
    ua_expected_values3 = pd.DataFrame(excel_read_cell(sheet, 'B196:CB244'))
    ua_expected_values4 = pd.DataFrame(excel_read_cell(sheet, 'B251:CB298'))
    ua_expected_values5 = pd.DataFrame(excel_read_cell(sheet, 'B307:CB354'))
    sheet = workbook.sheets['Operating Cost']
    excel_write_cell(sheet, 'A125', 'Year')
    oc_expected_values1 = pd.DataFrame(excel_read_cell(sheet, 'A18:F64'))
    oc_expected_values2 = pd.DataFrame(excel_read_cell(sheet, 'A125:F250'))
    oc_expected_values3 = pd.DataFrame(excel_read_cell(sheet, 'B262:AV386'))
    oc_expected_values4 = pd.DataFrame(excel_read_cell(sheet, 'I126:P250'))
    # Original uses 1=True and ""=False, but we want to use 0=False
    oc_expected_values4.replace(to_replace="", value=0, inplace=True)
    sheet = workbook.sheets['Emissions Factors']
    excel_write_cell(sheet, 'A11', 'Year')
    excel_write_cell(sheet, 'A66', 'Year')
    ef_expected_values = pd.DataFrame(excel_read_cell(sheet, 'A11:K112'))
    sheet = workbook.sheets['Adoption Data']
    excel_write_cell(sheet, 'B45', 'Year')
    ad_expected_values1 = pd.DataFrame(excel_read_cell(sheet, 'B45:R94'))
    ad_expected_values2 = pd.DataFrame(excel_read_cell(sheet, 'X45:Z94'))
    ad_expected_values3 = pd.DataFrame(excel_read_cell(sheet, 'AB45:AD94'))
    ad_expected_values4 = pd.DataFrame(excel_read_cell(sheet, 'BY50:CA96'))
    ad_expected_values5 = pd.DataFrame(excel_read_cell(sheet, 'CF50:CI96'))
    ad_expected_values6 = pd.DataFrame(excel_read_cell(sheet, 'CN50:CR96'))
    ad_expected_values7 = pd.DataFrame(excel_read_cell(sheet, 'CW50:CY96'))
    sheet = workbook.sheets['Helper Tables']
    ht_expected_values1 = pd.DataFrame(excel_read_cell(sheet, 'B26:L73'))
    ht_expected_values2 = pd.DataFrame(excel_read_cell(sheet, 'B90:L137'))
    sheet = workbook.sheets['CO2 Calcs']
    excel_write_cell(sheet, 'A9', 'Year')
    excel_write_cell(sheet, 'A64', 'Year')
    excel_write_cell(sheet, 'A234', 'Year')
    excel_write_cell(sheet, 'R234', 'Year')
    excel_write_cell(sheet, 'AI234', 'Year')
    excel_write_cell(sheet, 'A288', 'Year')
    excel_write_cell(sheet, 'R288', 'Year')
    excel_write_cell(sheet, 'AI288', 'Year')
    excel_write_cell(sheet, 'A344', 'Year')
    excel_write_cell(sheet, 'U344', 'Year')
    excel_write_cell(sheet, 'AP344', 'Year')
    cc_expected_values = pd.DataFrame(excel_read_cell(sheet, 'A9:AW390'))
    # Original Excel uses "" for empty cells, we want to use 0.0.
    cc_expected_values.replace(to_replace="", value=0, inplace=True)
    # We can't use SolarPVUtil for CH4 Calcs, as the tab is hidden and contains only #VALUE errors.
    #sheet = workbook.sheets['CH4 Calcs']
    #ch_expected_values = pd.DataFrame(excel_read_cell(sheet, 'A10:AW110'))
    #ch_expected_values.replace(to_replace="", value=0, inplace=True)
    sheet = workbook.sheets['TAM Data']
    excel_write_cell(sheet, 'B45', 'Year')
    excel_write_cell(sheet, 'B163', 'Year')
    excel_write_cell(sheet, 'B227', 'Year')
    excel_write_cell(sheet, 'B290', 'Year')
    excel_write_cell(sheet, 'B353', 'Year')
    excel_write_cell(sheet, 'B416', 'Year')
    excel_write_cell(sheet, 'B479', 'Year')
    excel_write_cell(sheet, 'B543', 'Year')
    excel_write_cell(sheet, 'B607', 'Year')
    excel_write_cell(sheet, 'B672', 'Year')
    excel_write_cell(sheet, 'Y103', 'S.D')
    excel_write_cell(sheet, 'AB103', 'Medium')
    td_compare_cells = [
        'B45:Q94', 'L103:N152', 'B163:Q212', 'B227:Q276', 'B290:Q339', 'B353:Q402',
        'B416:Q465', 'B479:Q528', 'B543:Q592', 'B607:Q656', 'B672:Q721',
        'W44:Y94', 'W103:Y152', 'W163:Y212', 'W227:Y276', 'W290:Y339', 'W353:Y402',
        'W416:Y465', 'W479:Y528', 'W543:Y592', 'W607:Y656', 'W672:Y721',
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
    td_expected_values = [pd.DataFrame(excel_read_cell(sheet, c)) for c in td_compare_cells]
    for df in td_expected_values:
      try:
        df.replace(inplace=True,
            to_replace=['Baseline: Based on-  AMPERE MESSAGE-MACRO Reference',
                        'Conservative: Based on-  IEA ETP 2016 4DS',
                        ' Ambitious: Based on- AMPERE GEM E3 450'],
            value=['Baseline: Based on- AMPERE MESSAGE-MACRO Reference',
                        'Conservative: Based on- IEA ETP 2016 4DS',
                        'Ambitious: Based on- AMPERE GEM E3 450'])
      except TypeError:
        pass
    workbook.close()
    excel_app.quit()

    solution_filename = 'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18_VBAWEB.xlsm'
    filename = os.path.join(excel_mod_files_dir, solution_filename)
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
    macro('solarpvutil?' + resource)
    excel_app.calculate()
    sheet = workbook.sheets['First Cost']
    fc_actual_values = pd.DataFrame(excel_read_cell(sheet, 'B37:R82'))
    sheet = workbook.sheets['Unit Adoption Calculations']
    ua_actual_values1 = pd.DataFrame(excel_read_cell(sheet, 'P16:CI115'))
    ua_actual_values2 = pd.DataFrame(excel_read_cell(sheet, 'B134:CB182'))
    ua_actual_values3 = pd.DataFrame(excel_read_cell(sheet, 'B196:CB244'))
    ua_actual_values4 = pd.DataFrame(excel_read_cell(sheet, 'B251:CB298'))
    ua_actual_values5 = pd.DataFrame(excel_read_cell(sheet, 'B307:CB354'))
    sheet = workbook.sheets['Operating Cost']
    oc_actual_values1 = pd.DataFrame(excel_read_cell(sheet, 'A18:F64'))
    oc_actual_values2 = pd.DataFrame(excel_read_cell(sheet, 'A125:F250'))
    oc_actual_values3 = pd.DataFrame(excel_read_cell(sheet, 'B262:AV386'))
    oc_actual_values4 = pd.DataFrame(excel_read_cell(sheet, 'I126:P250'))
    sheet = workbook.sheets['Emissions Factors']
    ef_actual_values = pd.DataFrame(excel_read_cell(sheet, 'A11:K112'))
    sheet = workbook.sheets['Adoption Data']
    ad_actual_values1 = pd.DataFrame(excel_read_cell(sheet, 'B45:R94'))
    ad_actual_values2 = pd.DataFrame(excel_read_cell(sheet, 'X45:Z94'))
    ad_actual_values3 = pd.DataFrame(excel_read_cell(sheet, 'AB45:AD94'))
    ad_actual_values4 = pd.DataFrame(excel_read_cell(sheet, 'BY50:CA96'))
    ad_actual_values5 = pd.DataFrame(excel_read_cell(sheet, 'CF50:CI96'))
    ad_actual_values6 = pd.DataFrame(excel_read_cell(sheet, 'CN50:CR96'))
    ad_actual_values7 = pd.DataFrame(excel_read_cell(sheet, 'CW50:CY96'))
    sheet = workbook.sheets['Helper Tables']
    ht_actual_values1 = pd.DataFrame(excel_read_cell(sheet, 'B26:L73'))
    ht_actual_values2 = pd.DataFrame(excel_read_cell(sheet, 'B90:L137'))
    sheet = workbook.sheets['CO2 Calcs']
    cc_actual_values = pd.DataFrame(excel_read_cell(sheet, 'A9:AW390'))
    # Original Excel uses "" for empty cells, we want to use 0.0 and have to match in *all* cells.
    cc_actual_values.replace(to_replace="", value=0, inplace=True)
    sheet = workbook.sheets['TAM Data']
    td_actual_values = [pd.DataFrame(excel_read_cell(sheet, c)) for c in td_compare_cells]
    workbook.close()
    excel_app.quit()

    pd.testing.assert_frame_equal(fc_actual_values, fc_expected_values, check_exact=False)
    pd.testing.assert_frame_equal(ua_actual_values1, ua_expected_values1, check_exact=False)
    pd.testing.assert_frame_equal(ua_actual_values2, ua_expected_values2, check_exact=False)
    pd.testing.assert_frame_equal(ua_actual_values3, ua_expected_values3, check_exact=False)
    pd.testing.assert_frame_equal(ua_actual_values4, ua_expected_values4, check_exact=False)
    pd.testing.assert_frame_equal(ua_actual_values5, ua_expected_values5, check_exact=False)
    pd.testing.assert_frame_equal(oc_actual_values1, oc_expected_values1, check_exact=False)
    pd.testing.assert_frame_equal(oc_actual_values2, oc_expected_values2, check_exact=False)
    pd.testing.assert_frame_equal(oc_actual_values3, oc_expected_values3, check_exact=False)
    pd.testing.assert_frame_equal(oc_actual_values4, oc_expected_values4, check_exact=False)
    pd.testing.assert_frame_equal(ef_actual_values, ef_expected_values, check_exact=False)
    pd.testing.assert_frame_equal(ad_actual_values1, ad_expected_values1, check_exact=False)
    pd.testing.assert_frame_equal(ad_actual_values2, ad_expected_values2, check_exact=False)
    pd.testing.assert_frame_equal(ad_actual_values3, ad_expected_values3, check_exact=False)
    pd.testing.assert_frame_equal(ad_actual_values4, ad_expected_values4, check_exact=False)
    pd.testing.assert_frame_equal(ad_actual_values5, ad_expected_values5, check_exact=False)
    pd.testing.assert_frame_equal(ad_actual_values6, ad_expected_values6, check_exact=False)
    pd.testing.assert_frame_equal(ad_actual_values7, ad_expected_values7, check_exact=False)
    pd.testing.assert_frame_equal(ht_actual_values1, ht_expected_values1, check_exact=False)
    pd.testing.assert_frame_equal(ht_actual_values2, ht_expected_values2, check_exact=False)
    pd.testing.assert_frame_equal(cc_actual_values, cc_expected_values, check_exact=False)
    for cells, actual, expected in zip(td_compare_cells, td_actual_values, td_expected_values):
      pd.testing.assert_frame_equal(actual, expected, check_exact=False)
