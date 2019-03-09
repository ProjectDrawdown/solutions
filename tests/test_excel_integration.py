"""
excel_integration_test is an end-to-end test which starts a Python flask
HTTP server, starts up a copy of Microsoft Excel, sets the spreadsheet
to reference the local HTTP server for its calculations, fetches key
results from the spreadsheet, and compares them to expected golden
values.
"""

import os.path
import pathlib
import re
import shutil
import sys
import threading
import time
import tempfile
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
import pytest
import xlrd

xlwings = pytest.importorskip("xlwings")

from solution import biogas
from solution import biomass
from solution import concentratedsolar
from solution import improvedcookstoves
from solution import landfillmethane
from solution import microwind
from solution import offshorewind
from solution import onshorewind
from solution import silvopasture
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


def get_pd_read_excel_args(r):
  """Convert 'A11:G55' notation to (usecols, skiprows, nrows) for pd.read_excel."""
  (start, end) = r.split(':')
  (startcol, startrow) = filter(None, re.split(r'(\d+)', start))
  startrow = int(startrow) - 1
  (endcol, endrow) = filter(None, re.split(r'(\d+)', end))
  endrow = int(endrow) - 1
  usecols = startcol + ':' + endcol
  skiprows = startrow
  nrows = endrow - startrow + 1
  return (usecols, skiprows, nrows)


@pytest.fixture()
def start_excel(request, tmpdir):
  excelfile = request.param
  assert os.path.exists(excelfile)
  if sys.platform == 'darwin':
    dirpath = str(os.path.join(os.path.expanduser("~"), 'Library', 'Containers',
        'com.microsoft.Excel', 'Data'))
  else:
    dirpath = str(tmpdir)
  (_, tmpfile) = tempfile.mkstemp(suffix='.xlsm', dir=dirpath,
      prefix='drawdown_test_excel_integration_')
  shutil.copyfile(excelfile, tmpfile)
  print("Opening " + tmpfile)
  workbook = xlwings.Book(tmpfile)
  workbook.filepath = tmpfile
  workbook.app.visible = False
  yield workbook
  workbook.close()
  workbook.app.quit()
  os.unlink(tmpfile)


def verify_tam_data(obj, verify=None):
  """Verified tables in TAM Data."""
  if verify is None:
    verify = {}
  verify['TAM Data'] = [
      ('W46:Y94', obj.tm.forecast_min_max_sd_global().reset_index(drop=True)),
      ('AA46:AC94', obj.tm.forecast_low_med_high_global().reset_index(drop=True)),
      ('BX50:BZ96', obj.tm.forecast_trend_global(trend='Linear').reset_index(drop=True)),
      ('CE50:CH96', obj.tm.forecast_trend_global(trend='Degree2').reset_index(drop=True)),
      ('CM50:CQ96', obj.tm.forecast_trend_global(trend='Degree3').reset_index(drop=True)),
      ('CV50:CX96', obj.tm.forecast_trend_global(trend='Exponential').reset_index(drop=True)),
      #('DZ45:EA91', obj.tm.forecast_trend_global().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      # TODO Figure out PDS TAM handling
      ('W164:Y212', obj.tm.forecast_min_max_sd_oecd90().reset_index(drop=True)),
      ('AA164:AC212', obj.tm.forecast_low_med_high_oecd90().reset_index(drop=True)),
      ('BX168:BZ214', obj.tm.forecast_trend_oecd90(trend='Linear').reset_index(drop=True)),
      ('CE168:CH214', obj.tm.forecast_trend_oecd90(trend='Degree2').reset_index(drop=True)),
      ('CM168:CQ214', obj.tm.forecast_trend_oecd90(trend='Degree3').reset_index(drop=True)),
      ('CV168:CX214', obj.tm.forecast_trend_oecd90(trend='Exponential').reset_index(drop=True)),
      #('DZ163:EA209', obj.tm.forecast_trend_oecd90().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W228:Y276', obj.tm.forecast_min_max_sd_eastern_europe().reset_index(drop=True)),
      ('AA228:AC276', obj.tm.forecast_low_med_high_eastern_europe().reset_index(drop=True)),
      ('BX232:BZ278', obj.tm.forecast_trend_eastern_europe(trend='Linear').reset_index(drop=True)),
      ('CE232:CH278', obj.tm.forecast_trend_eastern_europe(trend='Degree2').reset_index(drop=True)),
      ('CM232:CQ278', obj.tm.forecast_trend_eastern_europe(trend='Degree3').reset_index(drop=True)),
      ('CV232:CX278', obj.tm.forecast_trend_eastern_europe(trend='Exponential').reset_index(drop=True)),
      #('DZ227:EA273', obj.tm.forecast_trend_eastern_europe().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W291:Y339', obj.tm.forecast_min_max_sd_asia_sans_japan().reset_index(drop=True)),
      ('AA291:AC339', obj.tm.forecast_low_med_high_asia_sans_japan().reset_index(drop=True)),
      ('BX295:BZ341', obj.tm.forecast_trend_asia_sans_japan(trend='Linear').reset_index(drop=True)),
      ('CE295:CH341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree2').reset_index(drop=True)),
      ('CM295:CQ341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree3').reset_index(drop=True)),
      ('CV295:CX341', obj.tm.forecast_trend_asia_sans_japan(trend='Exponential').reset_index(drop=True)),
      #('DZ290:EA336', obj.tm.forecast_trend_asia_sans_japan().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W354:Y402', obj.tm.forecast_min_max_sd_middle_east_and_africa().reset_index(drop=True)),
      ('AA354:AC402', obj.tm.forecast_low_med_high_middle_east_and_africa().reset_index(drop=True)),
      ('BX358:BZ404', obj.tm.forecast_trend_middle_east_and_africa(trend='Linear').reset_index(drop=True)),
      ('CE358:CH404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree2').reset_index(drop=True)),
      ('CM358:CQ404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree3').reset_index(drop=True)),
      ('CV358:CX404', obj.tm.forecast_trend_middle_east_and_africa(trend='Exponential').reset_index(drop=True)),
      #('DZ353:EA399', obj.tm.forecast_trend_middle_east_and_africa().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W417:Y465', obj.tm.forecast_min_max_sd_latin_america().reset_index(drop=True)),
      ('AA417:AC465', obj.tm.forecast_low_med_high_latin_america().reset_index(drop=True)),
      ('BX421:BZ467', obj.tm.forecast_trend_latin_america(trend='Linear').reset_index(drop=True)),
      ('CE421:CH467', obj.tm.forecast_trend_latin_america(trend='Degree2').reset_index(drop=True)),
      ('CM421:CQ467', obj.tm.forecast_trend_latin_america(trend='Degree3').reset_index(drop=True)),
      ('CV421:CX467', obj.tm.forecast_trend_latin_america(trend='Exponential').reset_index(drop=True)),
      #('DZ416:EA465', obj.tm.forecast_trend_latin_america().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W480:Y528', obj.tm.forecast_min_max_sd_china().reset_index(drop=True)),
      ('AA480:AC528', obj.tm.forecast_low_med_high_china().reset_index(drop=True)),
      ('BX484:BZ530', obj.tm.forecast_trend_china(trend='Linear').reset_index(drop=True)),
      ('CE484:CH530', obj.tm.forecast_trend_china(trend='Degree2').reset_index(drop=True)),
      ('CM484:CQ530', obj.tm.forecast_trend_china(trend='Degree3').reset_index(drop=True)),
      ('CV484:CX530', obj.tm.forecast_trend_china(trend='Exponential').reset_index(drop=True)),
      #('DZ479:EA525', obj.tm.forecast_trend_china().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W544:Y592', obj.tm.forecast_min_max_sd_india().reset_index(drop=True)),
      ('AA544:AC592', obj.tm.forecast_low_med_high_india().reset_index(drop=True)),
      ('BX548:BZ594', obj.tm.forecast_trend_india(trend='Linear').reset_index(drop=True)),
      ('CE548:CH594', obj.tm.forecast_trend_india(trend='Degree2').reset_index(drop=True)),
      ('CM548:CQ594', obj.tm.forecast_trend_india(trend='Degree3').reset_index(drop=True)),
      ('CV548:CX594', obj.tm.forecast_trend_india(trend='Exponential').reset_index(drop=True)),
      #('DZ543:EA591', obj.tm.forecast_trend_india().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W608:Y656', obj.tm.forecast_min_max_sd_eu().reset_index(drop=True)),
      ('AA608:AC656', obj.tm.forecast_low_med_high_eu().reset_index(drop=True)),
      ('BX612:BZ658', obj.tm.forecast_trend_eu(trend='Linear').reset_index(drop=True)),
      ('CE612:CH658', obj.tm.forecast_trend_eu(trend='Degree2').reset_index(drop=True)),
      ('CM612:CQ658', obj.tm.forecast_trend_eu(trend='Degree3').reset_index(drop=True)),
      ('CV612:CX658', obj.tm.forecast_trend_eu(trend='Exponential').reset_index(drop=True)),
      #('DZ607:EA653', obj.tm.forecast_trend_eu().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ('W673:Y721', obj.tm.forecast_min_max_sd_usa().reset_index(drop=True)),
      ('AA673:AC721', obj.tm.forecast_low_med_high_usa().reset_index(drop=True)),
      ('BX677:BZ723', obj.tm.forecast_trend_usa(trend='Linear').reset_index(drop=True)),
      ('CE677:CH723', obj.tm.forecast_trend_usa(trend='Degree2').reset_index(drop=True)),
      ('CM677:CQ723', obj.tm.forecast_trend_usa(trend='Degree3').reset_index(drop=True)),
      ('CV677:CX723', obj.tm.forecast_trend_usa(trend='Exponential').reset_index(drop=True)),
      #('DZ672:EA718', obj.tm.forecast_trend_usa().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      ]
  return verify

def verify_tam_data_eleven_sources(obj, verify=None):
  """Verified tables in TAM Data, with smaller source data area.

     Some solutions, first noticed with ImprovedCookStoves, have a smaller set of
     columns to hold data sources and this shifts all of the rest of the columns to
     the left. This test specifies the columns for this narrower layout.
  """
  if verify is None:
    verify = {}
  verify['TAM Data'] = [
      ('S46:U94', obj.tm.forecast_min_max_sd_global().reset_index(drop=True)),
      ('W46:Y94', obj.tm.forecast_low_med_high_global().reset_index(drop=True)),
      ('BT50:BV96', obj.tm.forecast_trend_global(trend='Linear').reset_index(drop=True)),
      ('CA50:CD96', obj.tm.forecast_trend_global(trend='Degree2').reset_index(drop=True)),
      ('CI50:CM96', obj.tm.forecast_trend_global(trend='Degree3').reset_index(drop=True)),
      ('CR50:CT96', obj.tm.forecast_trend_global(trend='Exponential').reset_index(drop=True)),
      #('DV45:DW91', obj.tm.forecast_trend_global().reset_index().loc[:, ['Year', 'adoption']]), first year differs
      # TODO Figure out PDS TAM handling
      ('S164:U212', obj.tm.forecast_min_max_sd_oecd90().reset_index(drop=True)),
      ('W164:Y212', obj.tm.forecast_low_med_high_oecd90().reset_index(drop=True)),
      ('BT168:BV214', obj.tm.forecast_trend_oecd90(trend='Linear').reset_index(drop=True)),
      ('CA168:CD214', obj.tm.forecast_trend_oecd90(trend='Degree2').reset_index(drop=True)),
      ('CI168:CM214', obj.tm.forecast_trend_oecd90(trend='Degree3').reset_index(drop=True)),
      ('CR168:CT214', obj.tm.forecast_trend_oecd90(trend='Exponential').reset_index(drop=True)),
      #('DV163:DW209', obj.tm.forecast_trend_oecd90().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S228:U276', obj.tm.forecast_min_max_sd_eastern_europe().reset_index(drop=True)),
      ('W228:Y276', obj.tm.forecast_low_med_high_eastern_europe().reset_index(drop=True)),
      ('BT232:BV278', obj.tm.forecast_trend_eastern_europe(trend='Linear').reset_index(drop=True)),
      ('CA232:CD278', obj.tm.forecast_trend_eastern_europe(trend='Degree2').reset_index(drop=True)),
      ('CI232:CM278', obj.tm.forecast_trend_eastern_europe(trend='Degree3').reset_index(drop=True)),
      ('CR232:CT278', obj.tm.forecast_trend_eastern_europe(trend='Exponential').reset_index(drop=True)),
      #('DV227:DW273', obj.tm.forecast_trend_eastern_europe().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S291:U339', obj.tm.forecast_min_max_sd_asia_sans_japan().reset_index(drop=True)),
      ('W291:Y339', obj.tm.forecast_low_med_high_asia_sans_japan().reset_index(drop=True)),
      ('BT295:BV341', obj.tm.forecast_trend_asia_sans_japan(trend='Linear').reset_index(drop=True)),
      ('CA295:CD341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree2').reset_index(drop=True)),
      ('CI295:CM341', obj.tm.forecast_trend_asia_sans_japan(trend='Degree3').reset_index(drop=True)),
      ('CR295:CT341', obj.tm.forecast_trend_asia_sans_japan(trend='Exponential').reset_index(drop=True)),
      #('DV290:DW336', obj.tm.forecast_trend_asia_sans_japan().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S354:U402', obj.tm.forecast_min_max_sd_middle_east_and_africa().reset_index(drop=True)),
      ('W354:Y402', obj.tm.forecast_low_med_high_middle_east_and_africa().reset_index(drop=True)),
      ('BT358:BV404', obj.tm.forecast_trend_middle_east_and_africa(trend='Linear').reset_index(drop=True)),
      ('CA358:CD404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree2').reset_index(drop=True)),
      ('CI358:CM404', obj.tm.forecast_trend_middle_east_and_africa(trend='Degree3').reset_index(drop=True)),
      ('CR358:CT404', obj.tm.forecast_trend_middle_east_and_africa(trend='Exponential').reset_index(drop=True)),
      #('DV353:DW399', obj.tm.forecast_trend_middle_east_and_africa().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S417:U465', obj.tm.forecast_min_max_sd_latin_america().reset_index(drop=True)),
      ('W417:Y465', obj.tm.forecast_low_med_high_latin_america().reset_index(drop=True)),
      ('BT421:BV467', obj.tm.forecast_trend_latin_america(trend='Linear').reset_index(drop=True)),
      ('CA421:CD467', obj.tm.forecast_trend_latin_america(trend='Degree2').reset_index(drop=True)),
      ('CI421:CM467', obj.tm.forecast_trend_latin_america(trend='Degree3').reset_index(drop=True)),
      ('CR421:CT467', obj.tm.forecast_trend_latin_america(trend='Exponential').reset_index(drop=True)),
      #('DV416:DW465', obj.tm.forecast_trend_latin_america().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S480:U528', obj.tm.forecast_min_max_sd_china().reset_index(drop=True)),
      ('W480:Y528', obj.tm.forecast_low_med_high_china().reset_index(drop=True)),
      ('BT484:BV530', obj.tm.forecast_trend_china(trend='Linear').reset_index(drop=True)),
      ('CA484:CD530', obj.tm.forecast_trend_china(trend='Degree2').reset_index(drop=True)),
      ('CI484:CM530', obj.tm.forecast_trend_china(trend='Degree3').reset_index(drop=True)),
      ('CR484:CT530', obj.tm.forecast_trend_china(trend='Exponential').reset_index(drop=True)),
      #('DV479:DW525', obj.tm.forecast_trend_china().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S544:U592', obj.tm.forecast_min_max_sd_india().reset_index(drop=True)),
      ('W544:Y592', obj.tm.forecast_low_med_high_india().reset_index(drop=True)),
      ('BT548:BV594', obj.tm.forecast_trend_india(trend='Linear').reset_index(drop=True)),
      ('CA548:CD594', obj.tm.forecast_trend_india(trend='Degree2').reset_index(drop=True)),
      ('CI548:CM594', obj.tm.forecast_trend_india(trend='Degree3').reset_index(drop=True)),
      ('CR548:CT594', obj.tm.forecast_trend_india(trend='Exponential').reset_index(drop=True)),
      #('DV543:DW591', obj.tm.forecast_trend_india().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S608:U656', obj.tm.forecast_min_max_sd_eu().reset_index(drop=True)),
      ('W608:Y656', obj.tm.forecast_low_med_high_eu().reset_index(drop=True)),
      ('BT612:BV658', obj.tm.forecast_trend_eu(trend='Linear').reset_index(drop=True)),
      ('CA612:CD658', obj.tm.forecast_trend_eu(trend='Degree2').reset_index(drop=True)),
      ('CI612:CM658', obj.tm.forecast_trend_eu(trend='Degree3').reset_index(drop=True)),
      ('CR612:CT658', obj.tm.forecast_trend_eu(trend='Exponential').reset_index(drop=True)),
      #('DV607:DW653', obj.tm.forecast_trend_eu().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ('S673:U721', obj.tm.forecast_min_max_sd_usa().reset_index(drop=True)),
      ('W673:Y721', obj.tm.forecast_low_med_high_usa().reset_index(drop=True)),
      ('BT677:BV723', obj.tm.forecast_trend_usa(trend='Linear').reset_index(drop=True)),
      ('CA677:CD723', obj.tm.forecast_trend_usa(trend='Degree2').reset_index(drop=True)),
      ('CI677:CM723', obj.tm.forecast_trend_usa(trend='Degree3').reset_index(drop=True)),
      ('CR677:CT723', obj.tm.forecast_trend_usa(trend='Exponential').reset_index(drop=True)),
      #('DV672:DW718', obj.tm.forecast_trend_usa().reset_index().loc[:, ['Uear', 'adoption']]), first year differs
      ]
  return verify


def verify_adoption_data(obj, verify=None):
  """Verified tables in Adoption Data."""
  if verify is None:
    verify = {}
  verify['Adoption Data'] = [
      ('X46:Z94', obj.ad.adoption_min_max_sd_global().reset_index(drop=True)),
      ('AB46:AD94', obj.ad.adoption_low_med_high_global().reset_index(drop=True)),
      ('BY50:CA96', obj.ad.adoption_trend_global(trend='Linear').reset_index(drop=True)),
      ('CF50:CI96', obj.ad.adoption_trend_global(trend='Degree2').reset_index(drop=True)),
      ('CN50:CR96', obj.ad.adoption_trend_global(trend='Degree3').reset_index(drop=True)),
      ('CW50:CY96', obj.ad.adoption_trend_global(trend='Exponential').reset_index(drop=True)),
      #('EA45:EB91', obj.ad.adoption_trend_global().reset_index().loc[:, ['Year', 'adoption']]),
      ('X106:Z154', obj.ad.adoption_min_max_sd_oecd90().reset_index(drop=True)),
      ('AB106:AD154', obj.ad.adoption_low_med_high_oecd90().reset_index(drop=True)),
      ('BY110:CA156', obj.ad.adoption_trend_oecd90(trend='Linear').reset_index(drop=True)),
      ('CF110:CI156', obj.ad.adoption_trend_oecd90(trend='Degree2').reset_index(drop=True)),
      ('CN110:CR156', obj.ad.adoption_trend_oecd90(trend='Degree3').reset_index(drop=True)),
      ('CW110:CY156', obj.ad.adoption_trend_oecd90(trend='Exponential').reset_index(drop=True)),
      #('EA105:EB151', obj.ad.adoption_trend_oecd90().reset_index().loc[:, ['Year', 'adoption']]),
      ('X170:Z218', obj.ad.adoption_min_max_sd_eastern_europe().reset_index(drop=True)),
      ('AB170:AD218', obj.ad.adoption_low_med_high_eastern_europe().reset_index(drop=True)),
      ('BY174:CA220', obj.ad.adoption_trend_eastern_europe(trend='Linear').reset_index(drop=True)),
      ('CF174:CI220', obj.ad.adoption_trend_eastern_europe(trend='Degree2').reset_index(drop=True)),
      ('CN174:CR220', obj.ad.adoption_trend_eastern_europe(trend='Degree3').reset_index(drop=True)),
      ('CW174:CY220', obj.ad.adoption_trend_eastern_europe(trend='Exponential').reset_index(drop=True)),
      #('EA169:EB217', obj.ad.adoption_trend_eastern_europe().reset_index().loc[:, ['Year', 'adoption']]),
      ('X233:Z281', obj.ad.adoption_min_max_sd_asia_sans_japan().reset_index(drop=True)),
      ('AB233:AD281', obj.ad.adoption_low_med_high_asia_sans_japan().reset_index(drop=True)),
      ('BY237:CA283', obj.ad.adoption_trend_asia_sans_japan(trend='Linear').reset_index(drop=True)),
      ('CF237:CI283', obj.ad.adoption_trend_asia_sans_japan(trend='Degree2').reset_index(drop=True)),
      ('CN237:CR283', obj.ad.adoption_trend_asia_sans_japan(trend='Degree3').reset_index(drop=True)),
      ('CW237:CY283', obj.ad.adoption_trend_asia_sans_japan(trend='Exponential').reset_index(drop=True)),
      #('EA232:EB278', obj.ad.adoption_trend_asia_sans_japan().reset_index().loc[:, ['Year', 'adoption']]),
      ('X296:Z344', obj.ad.adoption_min_max_sd_middle_east_and_africa().reset_index(drop=True)),
      ('AB296:AD344', obj.ad.adoption_low_med_high_middle_east_and_africa().reset_index(drop=True)),
      ('BY300:CA346', obj.ad.adoption_trend_middle_east_and_africa(trend='Linear').reset_index(drop=True)),
      ('CF300:CI346', obj.ad.adoption_trend_middle_east_and_africa(trend='Degree2').reset_index(drop=True)),
      ('CN300:CR346', obj.ad.adoption_trend_middle_east_and_africa(trend='Degree3').reset_index(drop=True)),
      ('CW300:CY346', obj.ad.adoption_trend_middle_east_and_africa(trend='Exponential').reset_index(drop=True)),
      #('EA295:EB341', obj.ad.adoption_trend_middle_east_and_africa().reset_index().loc[:, ['Year', 'adoption']]),
      ('X359:Z407', obj.ad.adoption_min_max_sd_latin_america().reset_index(drop=True)),
      ('AB359:AD407', obj.ad.adoption_low_med_high_latin_america().reset_index(drop=True)),
      ('BY363:CA409', obj.ad.adoption_trend_latin_america(trend='Linear').reset_index(drop=True)),
      ('CF363:CI409', obj.ad.adoption_trend_latin_america(trend='Degree2').reset_index(drop=True)),
      ('CN363:CR409', obj.ad.adoption_trend_latin_america(trend='Degree3').reset_index(drop=True)),
      ('CW363:CY409', obj.ad.adoption_trend_latin_america(trend='Exponential').reset_index(drop=True)),
      #('EA358:EB404', obj.ad.adoption_trend_latin_america().reset_index().loc[:, ['Year', 'adoption']]),
      ('X422:Z470', obj.ad.adoption_min_max_sd_china().reset_index(drop=True)),
      ('AB422:AD470', obj.ad.adoption_low_med_high_china().reset_index(drop=True)),
      ('BY426:CA472', obj.ad.adoption_trend_china(trend='Linear').reset_index(drop=True)),
      ('CF426:CI472', obj.ad.adoption_trend_china(trend='Degree2').reset_index(drop=True)),
      ('CN426:CR472', obj.ad.adoption_trend_china(trend='Degree3').reset_index(drop=True)),
      ('CW426:CY472', obj.ad.adoption_trend_china(trend='Exponential').reset_index(drop=True)),
      #('EA421:EB467', obj.ad.adoption_trend_china().reset_index().loc[:, ['Year', 'adoption']]),
      ('X486:Z534', obj.ad.adoption_min_max_sd_india().reset_index(drop=True)),
      ('AB486:AD534', obj.ad.adoption_low_med_high_india().reset_index(drop=True)),
      ('BY490:CA536', obj.ad.adoption_trend_india(trend='Linear').reset_index(drop=True)),
      ('CF490:CI536', obj.ad.adoption_trend_india(trend='Degree2').reset_index(drop=True)),
      ('CN490:CR536', obj.ad.adoption_trend_india(trend='Degree3').reset_index(drop=True)),
      ('CW490:CY536', obj.ad.adoption_trend_india(trend='Exponential').reset_index(drop=True)),
      #('EA485:EB531', obj.ad.adoption_trend_india().reset_index().loc[:, ['Year', 'adoption']]),
      ('X550:Z598', obj.ad.adoption_min_max_sd_eu().reset_index(drop=True)),
      ('AB550:AD598', obj.ad.adoption_low_med_high_eu().reset_index(drop=True)),
      ('BY554:CA600', obj.ad.adoption_trend_eu(trend='Linear').reset_index(drop=True)),
      ('CF554:CI600', obj.ad.adoption_trend_eu(trend='Degree2').reset_index(drop=True)),
      ('CN554:CR600', obj.ad.adoption_trend_eu(trend='Degree3').reset_index(drop=True)),
      ('CW554:CY600', obj.ad.adoption_trend_eu(trend='Exponential').reset_index(drop=True)),
      #('EA549:EB595', obj.ad.adoption_trend_eu().reset_index().loc[:, ['Year', 'adoption']]),
      ('X615:Z663', obj.ad.adoption_min_max_sd_usa().reset_index(drop=True)),
      ('AB615:AD663', obj.ad.adoption_low_med_high_usa().reset_index(drop=True)),
      ('BY619:CA665', obj.ad.adoption_trend_usa(trend='Linear').reset_index(drop=True)),
      ('CF619:CI665', obj.ad.adoption_trend_usa(trend='Degree2').reset_index(drop=True)),
      ('CN619:CR665', obj.ad.adoption_trend_usa(trend='Degree3').reset_index(drop=True)),
      ('CW619:CY665', obj.ad.adoption_trend_usa(trend='Exponential').reset_index(drop=True)),
      #('EA614:EB660', obj.ad.adoption_trend_usa().reset_index().loc[:, ['Year', 'adoption']]),
      ]
  return verify


def verify_adoption_data_eleven_sources(obj, verify=None):
  """Verified tables in Adoption Data.

     Some solutions, first noticed with ImprovedCookStoves, have a smaller set of
     columns to hold data sources and this shifts all of the rest of the columns to
     the left. This test specifies the columns for this narrower layout.
  """
  if verify is None:
    verify = {}
  verify['Adoption Data'] = [
      ('S46:U94', obj.ad.adoption_min_max_sd_global().reset_index(drop=True)),
      ('W46:Y94', obj.ad.adoption_low_med_high_global().reset_index(drop=True)),
      ('BT50:BV96', obj.ad.adoption_trend_global(trend='Linear').reset_index(drop=True)),
      ('CA50:CD96', obj.ad.adoption_trend_global(trend='Degree2').reset_index(drop=True)),
      ('CI50:CM96', obj.ad.adoption_trend_global(trend='Degree3').reset_index(drop=True)),
      ('CR50:CT96', obj.ad.adoption_trend_global(trend='Exponential').reset_index(drop=True)),
      #('DV45:DW91', obj.ad.adoption_trend_global().reset_index().loc[:, ['Year', 'adoption']]),
      ]
  return verify


def verify_unit_adoption_calculations(obj, verify=None):
  """Verified tables in Unit Adoption Calculations."""
  if verify is None:
    verify = {}
  verify['Unit Adoption Calculations'] = [
      ('A17:K63', obj.tm.ref_tam_per_region().reset_index()),
      ('P17:Z63', obj.ua.ref_population().reset_index()),
      ('AB17:AL63', obj.ua.ref_gdp().reset_index()),
      ('AN17:AX63', obj.ua.ref_gdp_per_capita().reset_index()),
      ('BA17:BK63', obj.ua.ref_tam_per_capita().reset_index()),
      ('BM17:BW63', obj.ua.ref_tam_per_gdp_per_capita().reset_index()),
      ('BY17:CI63', obj.ua.ref_tam_growth().reset_index()),
      ('A69:K115', obj.tm.pds_tam_per_region().reset_index()),
      ('P69:Z115', obj.ua.pds_population().reset_index()),
      ('AB69:AL115', obj.ua.pds_gdp().reset_index()),
      ('AN69:AX115', obj.ua.pds_gdp_per_capita().reset_index()),
      ('BA69:BK115', obj.ua.pds_tam_per_capita().reset_index()),
      ('BM69:BW115', obj.ua.pds_tam_per_gdp_per_capita().reset_index()),
      ('BY69:CI115', obj.ua.pds_tam_growth().reset_index()),
      #('B135:L181' tested in 'Helper Tables'!C91
      ('Q135:AA181', obj.ua.soln_pds_cumulative_funits().reset_index()),
      ('AG137:AQ182', obj.ua.soln_pds_new_iunits_reqd().reset_index()),
      ('AX136:BH182', obj.ua.soln_pds_tot_iunits_reqd().reset_index()),
      #('BN136:BS182', not yet implemented
      #('B198:L244' tested in 'Helper Tables'!C27
      ('Q198:AA244', obj.ua.soln_ref_cumulative_funits().reset_index()),
      ('AG199:AQ244', obj.ua.soln_ref_new_iunits_reqd().reset_index()),
      ('AX198:BH244', obj.ua.soln_ref_tot_iunits_reqd().reset_index()),
      ('B252:L298', obj.ua.soln_net_annual_funits_adopted().reset_index()),
      ('Q252:AA298', obj.ua.conv_ref_tot_iunits().reset_index()),
      ('AG253:AQ298', obj.ua.conv_ref_new_iunits().reset_index()),
      ('AX252:BH298', obj.ua.conv_ref_annual_tot_iunits().reset_index()),
      ('B308:L354', obj.ua.soln_pds_net_grid_electricity_units_saved().reset_index()),
      ('Q308:AA354', obj.ua.soln_pds_net_grid_electricity_units_used().reset_index()),
      ('AD308:AN354', obj.ua.soln_pds_fuel_units_avoided().reset_index()),
      ('AT308:BD354', obj.ua.soln_pds_direct_co2_emissions_saved().reset_index()),
      ('BF308:BP354', obj.ua.soln_pds_direct_ch4_co2_emissions_saved().reset_index()),
      ('BR308:CB354', obj.ua.soln_pds_direct_n2o_co2_emissions_saved().reset_index()),
      ]
  return verify


def verify_helper_tables(obj, verify=None):
  """Verified tables in Helper Tables."""
  if verify is None:
    verify = {}
  verify['Helper Tables'] = [
      ('B27:L73', obj.ht.soln_ref_funits_adopted().reset_index()),
      ('B91:L137', obj.ht.soln_pds_funits_adopted().reset_index()),
      ]
  return verify


def verify_emissions_factors(obj, verify=None):
  """Verified tables in Emissions Factors."""
  if verify is None:
    verify = {}
  verify['Emissions Factors'] = [
      ('A12:K57', obj.ef.conv_ref_grid_CO2eq_per_KWh().reset_index()),
      ('A67:K112', obj.ef.conv_ref_grid_CO2_per_KWh().reset_index()),
      ]
  return verify


def verify_first_cost(obj, verify=None):
  """Verified tables in First Cost."""
  if verify is None:
    verify = {}
  verify['First Cost'] = [
      ('C37:C82', obj.fc.soln_pds_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True)),
      #('D37:D82', checked by 'Unit Adoption Calculations'!AH137
      ('E37:E82', obj.fc.soln_pds_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True)),
      ('F37:F82', obj.fc.soln_pds_cumulative_install().loc[2015:].to_frame().reset_index(drop=True)),
      ('L37:L82', obj.fc.soln_ref_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True)),
      #('M37:M82', checked by 'Unit Adoption Calculations'!AH199
      ('N37:N82', obj.fc.soln_ref_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True)),
      ('O37:O82', obj.fc.conv_ref_install_cost_per_iunit().loc[2015:].to_frame().reset_index(drop=True)),
      #('P37:P82', checked by 'Unit Adoption Calculations'!AH253
      ('Q37:Q82', obj.fc.conv_ref_annual_world_first_cost().loc[2015:].to_frame().reset_index(drop=True)),
      ('R37:R82', obj.fc.ref_cumulative_install().loc[2015:].to_frame().reset_index(drop=True)),
      ]
  return verify


def verify_operating_cost(obj, verify=None):
  """Verified tables in Operating Cost."""
  if verify is None:
    verify = {}
  verify['Operating Cost'] = [
      ('B262:AV386', obj.oc.soln_pds_annual_breakout().reset_index()),
      ('B399:AV523', obj.oc.conv_ref_annual_breakout().reset_index()),
      #('B19:B64', Not implemented
      #('C19:C64', checked by 'Unit Adoption Calculations'!C253
      ('D19:D64', obj.oc.soln_pds_annual_operating_cost().loc[2015:2060].to_frame().reset_index(drop=True)),
      ('E19:E64', obj.oc.soln_pds_cumulative_operating_cost().loc[2015:2060].to_frame().reset_index(drop=True)),
      ('F19:F64', obj.oc.soln_pds_new_funits_per_year().loc[2015:, ['World']].reset_index(drop=True)),
      #('I19:I64', Not implemented
      #('J19:J64', checked by 'Unit Adoption Calculations'!C253
      ('K19:K64', obj.oc.conv_ref_annual_operating_cost().to_frame().reset_index(drop=True)),
      ('L19:L64', obj.oc.conv_ref_cumulative_operating_cost().to_frame().reset_index(drop=True)),
      #('B69:B114', equal to D19:D64,
      #('C69:C114', equal to K19:K64,
      ('D69:D114', obj.oc.marginal_annual_operating_cost().to_frame().reset_index(drop=True)),
      ('A126:E250', obj.oc.lifetime_cost_forecast().reset_index()),
      ('I126:I250', obj.oc.soln_vs_conv_single_iunit_cashflow().to_frame().reset_index(drop=True)),
      ('J126:J250', obj.oc.soln_vs_conv_single_iunit_npv().to_frame().reset_index(drop=True)),
      #('K126:K250', obj.oc.soln_vs_conv_single_iunit_payback().to_frame().reset_index(drop=True)),
      #('L126:L250', obj.oc.soln_vs_conv_single_iunit_payback_discounted().to_frame().reset_index(drop=True)),
      ('M126:M250', obj.oc.soln_only_single_iunit_cashflow().to_frame().reset_index(drop=True)),
      ('N126:N250', obj.oc.soln_only_single_iunit_npv().to_frame().reset_index(drop=True)),
      #('O126:O250', obj.oc.soln_only_single_iunit_payback().to_frame().reset_index(drop=True)),
      #('P126:P250', obj.oc.soln_only_single_iunit_payback_discounted().to_frame().reset_index(drop=True)),
      ]
  return verify


def verify_co2_calcs(obj, verify=None):
  """Verified tables in CO2 Calcs."""
  if verify is None:
    verify = {}
  verify['CO2 Calcs'] = [
      ('A10:K55', obj.c2.co2_mmt_reduced().loc[2015:].reset_index()),
      ('A65:K110', obj.c2.co2eq_mmt_reduced().loc[2015:].reset_index()),
      ('A120:AW165', obj.c2.co2_ppm_calculator().loc[2015:].reset_index()),
      ('A172:F217', obj.c2.co2eq_ppm_calculator().loc[2015:].reset_index()),
      ('A235:K280', obj.c2.co2_reduced_grid_emissions().loc[2015:].reset_index()),
      ('R235:AB280', obj.c2.co2_replaced_grid_emissions().loc[2015:].reset_index()),
      ('AI235:AS280', obj.c2.co2_increased_grid_usage_emissions().loc[2015:].reset_index()),
      ('A289:K334', obj.c2.co2eq_reduced_grid_emissions().loc[2015:].reset_index()),
      ('R289:AB334', obj.c2.co2eq_replaced_grid_emissions().loc[2015:].reset_index()),
      ('AI289:AS334', obj.c2.co2eq_increased_grid_usage_emissions().loc[2015:].reset_index()),
      ('A345:K390', obj.c2.co2eq_direct_reduced_emissions().loc[2015:].reset_index()),
      ('U345:AE390', obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].reset_index()),
      ('AP345:AZ390', obj.c2.co2eq_net_indirect_emissions().loc[2015:].reset_index()),
      ]


def verify_ch4_calcs(obj, verify=None):
  """Verified tables in CH4 Calcs."""
  if verify is None:
    verify = {}
  verify['CH4 Calcs'] = [
      ('A11:K56', obj.c4.ch4_tons_reduced().reset_index()),
      ('A65:AW110', obj.c4.ch4_ppb_calculator().reset_index()),
      ]
  return verify


def energy_solution_verify_list(obj):
  """Assemble verification for the modules used in the energy solutions."""
  verify = {}
  verify_tam_data(obj, verify)
  verify_adoption_data(obj, verify)
  verify_helper_tables(obj, verify)
  verify_emissions_factors(obj, verify)
  verify_unit_adoption_calculations(obj, verify)
  verify_first_cost(obj, verify)
  verify_operating_cost(obj, verify)
  verify_co2_calcs(obj, verify)
  return verify


def compare_dataframes(actual_df, expected_df, description=''):
  """Compare two dataframes and print where they differ."""
  nerrors = 0
  if actual_df.shape != expected_df.shape:
    raise AssertionError(description + '\nDataFrames differ in shape: ' + \
        str(actual_df.shape) + " versus " + str(expected_df.shape))
  (nrows, ncols) = actual_df.shape
  msg = ''
  for r in range(nrows):
    for c in range(ncols):
      matches = True
      act = actual_df.iloc[r,c]
      exp = expected_df.iloc[r,c]
      if isinstance(act, str) and isinstance(exp, str):
        matches = (act == exp)
      elif pd.isna(act) or act == '' or act is None or act == 0 or act == pytest.approx(0.0):
        matches = pd.isna(exp) or exp == '' or exp is None or exp == 0 or exp == pytest.approx(0.0)
      else:
        matches = (act == pytest.approx(exp))
      if not matches:
        msg += "Err [" + str(r) + "][" + str(c) + "] : " + \
            "'" + str(act) + "' != '" + str(exp) + "'\n"
        nerrors += 1
      if nerrors > 10:
        break
  if msg:
    raise AssertionError(description + '\nDataFrames differ:\n' + msg)


def check_excel_against_object(obj, workbook, scenario, verify):
  print("Checking " + scenario)
  sheet = workbook.sheets['ScenarioRecord']
  excel_write_cell_xlwings(sheet, 'B9', scenario)
  macro = workbook.macro("LoadScenario_Click")
  macro()
  _ = excel_read_cell_xlwings(sheet, 'B9')
  workbook.app.calculate()
  workbook.save()

  description = "Solution: " + obj.name + " Scenario: " + scenario + " "
  wb = xlrd.open_workbook(filename=workbook.filepath, on_demand=True)
  for sheetname in verify.keys():
    sheet = workbook.sheets[sheetname]
    for (cellrange, actual_df) in verify[sheetname]:
      (usecols, skiprows, nrows) = get_pd_read_excel_args(cellrange)
      expected_df = pd.read_excel(wb, engine='xlrd', sheet_name=sheetname, header=None,
        index_col=None, usecols=usecols, skiprows=skiprows, nrows=nrows)
      descr = description + sheetname + " " + cellrange
      compare_dataframes(actual_df, expected_df, descr)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('biogas', 'testdata', 'Drawdown-Large Biodigesters (Biogas)_RRS.ES_v1.1_13Jan2019_PUBLIC.xlsm'))],
    indirect=True)
def test_Biogas_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file Biogas*."""
  workbook = start_excel
  for scenario in biogas.scenarios.keys():
    obj = biogas.Biogas(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('biomass', 'testdata',
      'Drawdown-Biomass from Perennial Crops for Electricity Generation_RRS.ES_v1.1_13Jan2019_PUBLIC.xlsm'))],
    indirect=True)
def test_Biomass_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file Biomass*."""
  workbook = start_excel
  for scenario in biomass.scenarios.keys():
    obj = biomass.Biomass(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('concentratedsolar', 'testdata', 'CSP_RRS_ELECGEN_v1.1b_24Oct18.xlsm'))],
    indirect=True)
@pytest.mark.skip(reason="need to resolve Adoption Data X367 and Z367")
def test_ConcentratedSolar_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file CSP_RRS_ELECGEN_*."""
  workbook = start_excel
  for scenario in concentratedsolar.scenarios.keys():
    obj = concentratedsolar.ConcentratedSolar(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('improvedcookstoves', 'testdata', 'Drawdown-Improved Cook Stoves (ICS)_RRS_v1.1_28Nov2018_PUBLIC.xlsm'))],
    indirect=True)
def test_ImprovedCookStoves_RRS(start_excel, tmpdir):
  """Test for Excel model file ImprovedCookStoves."""
  workbook = start_excel
  for scenario in improvedcookstoves.scenarios.keys():
    obj = improvedcookstoves.ImprovedCookStoves(scenario=scenario)
    verify = {}
    verify_tam_data_eleven_sources(obj, verify)
    if obj.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
      verify_adoption_data_eleven_sources(obj, verify)
    verify_unit_adoption_calculations(obj, verify)
    verify_helper_tables(obj, verify)
    verify_emissions_factors(obj, verify)
    verify_first_cost(obj, verify)
    verify_operating_cost(obj, verify)
    verify['CO2 Calcs'] = [
        ('A10:K55', obj.c2.co2_mmt_reduced().loc[2015:].reset_index()),
        ('A65:K110', obj.c2.co2eq_mmt_reduced().loc[2015:].reset_index()),
        ('A120:AW165', obj.c2.co2_ppm_calculator().loc[2015:].reset_index()),
        ('A172:F217', obj.c2.co2eq_ppm_calculator().loc[2015:].reset_index()),
        ('A235:K280', obj.c2.co2_reduced_grid_emissions().loc[2015:].reset_index()),
        ('R235:AB280', obj.c2.co2_replaced_grid_emissions().loc[2015:].reset_index()),
        ('AI235:AS280', obj.c2.co2_increased_grid_usage_emissions().loc[2015:].reset_index()),
        ('A289:K334', obj.c2.co2eq_reduced_grid_emissions().loc[2015:].reset_index()),
        ('R289:AB334', obj.c2.co2eq_replaced_grid_emissions().loc[2015:].reset_index()),
        ('AI289:AS334', obj.c2.co2eq_increased_grid_usage_emissions().loc[2015:].reset_index()),
        ('A345:K390', obj.c2.co2eq_direct_reduced_emissions().loc[2015:].reset_index()),
        # last two blocks are shifted compared with other solutions.
        ('R345:AB390', obj.c2.co2eq_reduced_fuel_emissions().loc[2015:].reset_index()),
        ('AM345:AW390', obj.c2.co2eq_net_indirect_emissions().loc[2015:].reset_index()),
        ]
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('landfillmethane', 'testdata', 'LandfillMethane_RRS_ELECGEN_v1.1c_24Oct18.xlsm'))],
    indirect=True)
@pytest.mark.skip(reason="need to resolve Unit Adoption Calculations W252 and X252")
def test_LandfillMethane_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file LandfillMethane_RRS_ELECGEN_*."""
  workbook = start_excel
  # Regional data where all but the first row are #VALUE, and the regional
  # data is not used. Just zero out the first row, don't try to match it
  # in Python.
  rewrites = [('Unit Adoption Calculations', 'B251:BH298', 1, 21, 0.0),
      ('Unit Adoption Calculations', 'B251:BH298', 1, 22, 0.0),]
  for scenario in landfillmethane.scenarios.keys():
    obj = landfillmethane.LandfillMethane(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('microwind', 'testdata', 'Drawdown-MicroWind Turbines_RRS.ES_v1.1_13Jan2019_PUBLIC.xlsm'))],
    indirect=True)
def test_MicroWind_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file MicroWind_RRS_*."""
  workbook = start_excel
  for scenario in microwind.scenarios.keys():
    obj = microwind.MicroWind(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('offshorewind', 'testdata', 'Drawdown-Wind Offshore_RRS.ES_v1.1_13Jan2019_PUBLIC.xlsm'))],
    indirect=True)
def test_OffshoreWind_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file OffshoreWind_*."""
  workbook = start_excel
  for scenario in offshorewind.scenarios.keys():
    obj = offshorewind.OffshoreWind(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('onshorewind', 'testdata', 'Drawdown-Onshore Wind_RRS.ES_v1.1_13Jan2019_PUBLIC.xlsm'))],
    indirect=True)
def test_OnshoreWind_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file OnshoreWind_*."""
  workbook = start_excel
  for scenario in onshorewind.scenarios.keys():
    obj = onshorewind.OnshoreWind(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('silvopasture', 'testdata', 'Silvopasture_L-Use_v1.1a_3Aug18.xlsm'))],
    indirect=True)
def test_Silvopasture_LAND_USE(start_excel, tmpdir):
  """Test for Excel model file Silvopasture_L-Use*."""
  workbook = start_excel
  for scenario in silvopasture.scenarios.keys():
    obj = silvopasture.Silvopasture(scenario=scenario)
    verify = {}
    verify['Helper Tables'] = [
        ('B27:L73', obj.ht.soln_ref_funits_adopted().reset_index()),
        ]
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('solarpvroof', 'testdata', 'SolarPVRooftop_RRS_ELECGEN_v1.1b_24Oct18.xlsm'))],
    indirect=True)
@pytest.mark.skip(reason="no excel file checked in")
def test_SolarRooftop_RRS_ELECGEN(start_excel, tmpdir):
  """Test for Excel model file SolarPVRooftop_RRS_ELECGEN_*."""
  workbook = start_excel
  for scenario in solarpvroof.scenarios.keys():
    obj = solarpvroof.SolarPVRoof(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)


@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('solarpvutil', 'testdata', 'SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18.xlsm'))],
    indirect=True)
def test_SolarPVUtility_RRS_ELECGEN(start_excel):
  """Test for Excel model file SolarPVUtility_RRS_ELECGEN_*."""
  workbook = start_excel
  for scenario in solarpvutil.scenarios.keys():
    obj = solarpvutil.SolarPVUtil(scenario=scenario)
    verify = energy_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)
