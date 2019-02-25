#!/usr/bin/env python
"""Extract parameters from a Drawdown excel model to help create
   the Python implementation of the solution and its scenarios.
"""

import argparse
import os.path
import re
import sys
import textwrap

import xlrd
import numpy as np
import pandas as pd
from solution import rrs

from tools.util import convert_bool, cell_to_offsets

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def convert_sr_float(val):
  """Return floating point value from Excel ScenarioRecord tab.

     There are two main formats:
     + simple: 0.182810601365724
     + annotated: Val:(0.182810601365724) Formula:='Variable Meta-analysis'!G1411
  """
  m = re.match(r'Val:\((\d+\.\d+)\) Formula:=', str(val))
  if m:
    return float(m.group(1))
  if val == '':
    return 0.0
  return float(val)


def get_rrs_scenarios(wb):
  """Extract scenarios from an RRS Excel file.
     Arguments:
       wb: Excel workbook as returned by xlrd.
  """
  sr_tab = wb.sheet_by_name('ScenarioRecord')
  ac_tab = wb.sheet_by_name('Advanced Controls')
  scenarios = {}
  for row in range(1, sr_tab.nrows):
    col_d = sr_tab.cell_value(row, 3)
    col_e = sr_tab.cell_value(row, 4)
    if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:
      # start of scenario block
      scenario_name = col_e
      s = {}

      s['description'] = sr_tab.cell_value(row + 1, 4)
      report_years = sr_tab.cell_value(row + 2, 4)  # E:2 from top of scenario
      (start, end) = report_years.split('-')
      s['report_start_year'] = int(start)
      s['report_end_year'] = int(end)

      assert sr_tab.cell_value(row + 46, 1) == 'Conventional'
      assert sr_tab.cell_value(row + 47, 3) == 'First Cost:'
      s['conv_2014_cost'] = convert_sr_float(sr_tab.cell_value(row + 47, 4))
      s['conv_first_cost_efficiency_rate'] = convert_sr_float(sr_tab.cell_value(row + 48, 4))
      s['conv_lifetime_capacity'] = convert_sr_float(sr_tab.cell_value(row + 49, 4))
      s['conv_avg_annual_use'] = convert_sr_float(sr_tab.cell_value(row + 50, 4))
      s['conv_var_oper_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 51, 4))
      s['conv_fixed_oper_cost_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 52, 4))
      s['conv_fuel_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 54, 4))

      assert sr_tab.cell_value(row + 64, 1) == 'Solution'
      assert sr_tab.cell_value(row + 65, 3) == 'First Cost:'
      s['pds_2014_cost'] = s['ref_2014_cost'] = convert_sr_float(sr_tab.cell_value(row + 65, 4))
      s['soln_first_cost_efficiency_rate'] = convert_sr_float(sr_tab.cell_value(row + 66, 4))
      s['soln_first_cost_below_conv'] = convert_bool(sr_tab.cell_value(row + 66, 6))
      s['soln_lifetime_capacity'] = convert_sr_float(sr_tab.cell_value(row + 67, 4))
      s['soln_avg_annual_use'] = convert_sr_float(sr_tab.cell_value(row + 68, 4))
      s['soln_var_oper_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 69, 4))
      s['soln_fixed_oper_cost_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 70, 4))
      s['soln_fuel_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 72, 4))

      assert sr_tab.cell_value(row + 76, 1) == 'General'
      s['npv_discount_rate'] = convert_sr_float(sr_tab.cell_value(row + 77, 4))

      assert sr_tab.cell_value(row + 103, 1) == 'Direct Emissions'
      s['conv_emissions_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 105, 4))
      s['soln_emissions_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 106, 4))

      assert sr_tab.cell_value(row + 111, 1) == 'Indirect Emissions'
      s['conv_indirect_co2_per_unit'] = convert_sr_float(sr_tab.cell_value(row + 112, 4))
      s['soln_indirect_co2_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 113, 4))
      i_vs_f = str(sr_tab.cell_value(row + 114, 4)).lower()
      s['conv_indirect_co2_is_iunits'] = False if i_vs_f == 'functional' else True

      assert sr_tab.cell_value(row + 118, 1) == 'Optional Inputs'
      s['ch4_co2_per_twh'] = convert_sr_float(sr_tab.cell_value(row + 119, 4))
      s['ch4_is_co2eq'] = (sr_tab.cell_value(row + 119, 5) == 't CH4-CO2eq per TWh')
      s['n2o_co2_per_twh'] = convert_sr_float(sr_tab.cell_value(row + 120, 4))
      s['n2o_is_co2eq'] = (sr_tab.cell_value(row + 120, 5) == 't N2O-CO2eq per TWh')
      s['co2eq_conversion_source'] = str(sr_tab.cell_value(row + 121, 4))

      assert sr_tab.cell_value(row + 124, 1) == 'General Climate Inputs'
      s['emissions_use_co2eq'] = convert_bool(sr_tab.cell_value(row + 125, 4))
      s['emissions_grid_source'] = str(sr_tab.cell_value(row + 126, 4))
      s['emissions_grid_range'] = str(sr_tab.cell_value(row + 127, 4))

      assert sr_tab.cell_value(row + 135, 1) == 'TAM'
      s['source_until_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 4)))
      s['ref_source_post_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 7)))
      s['pds_source_post_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 10)))

      assert sr_tab.cell_value(row + 163, 1) == 'PDS ADOPTION SCENARIO INPUTS'
      s['soln_pds_adoption_basis'] = str(sr_tab.cell_value(row + 164, 4))
      s['soln_pds_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 165, 4))

      assert sr_tab.cell_value(row + 183, 1) == 'Existing PDS Prognostication Assumptions'
      adopt = str(sr_tab.cell_value(row + 184, 4))
      if adopt: s['soln_pds_adoption_prognostication_source'] = adopt
      adopt = str(sr_tab.cell_value(row + 185, 4))
      if adopt: s['soln_pds_adoption_prognostication_trend'] = adopt
      adopt = str(sr_tab.cell_value(row + 186, 4))
      if adopt: s['soln_pds_adoption_prognostication_growth'] = adopt

      assert sr_tab.cell_value(row + 194, 1) == 'Fully Customized PDS'
      custom = str(sr_tab.cell_value(row + 195, 4))
      if custom:
        s['soln_pds_adoption_custom_name'] = custom
        if 'soln_pds_adoption_basis' not in s:  # sometimes row 164 is blank
          s['soln_pds_adoption_basis'] = 'Fully Customized PDS'

      assert sr_tab.cell_value(row + 198, 1) == 'REF ADOPTION SCENARIO INPUTS'
      s['soln_ref_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 201, 4))

      assert sr_tab.cell_value(row + 217, 1) == 'Adoption Adjustment'
      adjust = sr_tab.cell_value(row + 218, 4)
      if adjust and adjust != "(none)":
        s['pds_adoption_use_ref_years'] = [int(x) for x in adjust.split(',') if x is not '']
      adjust = sr_tab.cell_value(row + 219, 4)
      if adjust and adjust != "(none)":
        s['ref_adoption_use_pds_years'] = [int(x) for x in adjust.split(',') if x is not '']

      # From Advanced Controls
      category = ac_tab.cell_value(*cell_to_offsets('A159'))
      if category: s['solution_category'] = category

      row += 202
      scenarios[scenario_name] = s
  return scenarios


def get_land_scenarios(wb):
  """Extract scenarios from a LAND Excel file.
     Arguments:
       wb: Excel workbook returned by xlrd.
  """
  sr_tab = wb.sheet_by_name('ScenarioRecord')
  scenarios = {}
  for row in range(1, sr_tab.nrows):
    col_d = sr_tab.cell_value(row, 3)
    col_e = sr_tab.cell_value(row, 4)
    if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:
      # start of scenario block
      scenario_name = col_e
      s = {}

      report_years = sr_tab.cell_value(row + 2, 4)  # E:2 from top of scenario
      (start, end) = report_years.split('-')
      s['report_start_year'] = int(start)
      s['report_end_year'] = int(end)

      assert sr_tab.cell_value(row + 90, 1) == 'General'
      s['npv_discount_rate'] = convert_sr_float(sr_tab.cell_value(row + 91, 4))

      assert sr_tab.cell_value(row + 156, 1) == 'General Emissions Inputs'
      s['emissions_use_co2eq'] = convert_bool(sr_tab.cell_value(row + 157, 4))
      s['emissions_grid_source'] = str(sr_tab.cell_value(row + 159, 4))
      s['emissions_grid_range'] = str(sr_tab.cell_value(row + 160, 4))

      assert sr_tab.cell_value(row + 230, 1) == 'PDS ADOPTION SCENARIO INPUTS'
      s['soln_pds_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 232, 4))

      assert sr_tab.cell_value(row + 262, 1) == 'REF ADOPTION SCENARIO INPUTS'
      s['soln_ref_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 265, 4))

      # TODO: handle soln_pds_adoption_prognostication_source

      scenarios[scenario_name] = s
  return scenarios

def oneline(f, s, names, prefix='', suffix=None):
  """Format a set of outputs onto a single line.
     Arguments:
       f: file-like object to write output to
       s: a dictionary loaded with values for the scenario we are processing.
       prefix: string to prepend to each line (typically, some number of spaces)
       suffix: string to append to the end of the line (typically, a newline)

     This routine *removes* the dict elements in names from s before returning.
     The intent is that each call to oneline() both outputs a line of text and
     consumes the entries from s, so that at the end we can check if any
     unconsumed entries remain.
  """
  if not all(n in s for n in names):
    return
  f.write(prefix)
  for n in names:
    if isinstance(s[n], str):
      f.write(str(n) + " = '" + str(s[n]) + "', ")
    else:
      f.write(str(n) + " = " + str(s[n]) + ", ")
    del s[n]
  f.write('\n')
  if suffix:
    f.write(str(suffix))


def write_scenario(f, s):
  """Write out the advanced_controls entries for a given scenario."""
  prefix = '      '

  if 'description' in s:
    description = re.sub(r'\s+', ' ', s['description'])
    for line in textwrap.wrap(description, width=80):
      f.write(prefix + '# ' + line + '\n')
    del s['description']

  oneline(f=f, s=s, names=['report_start_year', 'report_end_year'], prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['pds_2014_cost', 'ref_2014_cost'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_2014_cost'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_first_cost_efficiency_rate'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_first_cost_efficiency_rate',
    'soln_first_cost_below_conv'], prefix=prefix)
  oneline(f=f, s=s, names=['npv_discount_rate'], prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['ch4_is_co2eq', 'n2o_is_co2eq'], prefix=prefix)
  oneline(f=f, s=s, names=['co2eq_conversion_source'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_indirect_co2_per_iunit'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_indirect_co2_per_unit', 'conv_indirect_co2_is_iunits'],
      prefix=prefix)
  oneline(f=f, s=s, names=['ch4_co2_per_twh', 'n2o_co2_per_twh'], prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['soln_lifetime_capacity', 'soln_avg_annual_use'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_lifetime_capacity', 'conv_avg_annual_use'],
      prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['soln_var_oper_cost_per_funit', 'soln_fuel_cost_per_funit'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_fixed_oper_cost_per_iunit'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_var_oper_cost_per_funit', 'conv_fuel_cost_per_funit'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_fixed_oper_cost_per_iunit'], prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['emissions_grid_source', 'emissions_grid_range'], prefix=prefix)
  oneline(f=f, s=s, names=['emissions_use_co2eq'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_emissions_per_funit', 'soln_emissions_per_funit'],
      prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['soln_ref_adoption_regional_data',
    'soln_pds_adoption_regional_data'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_basis'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_source'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_trend'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_growth'], prefix=prefix)
  oneline(f=f, s=s, names=['ref_adoption_use_pds_years'], prefix=prefix)
  oneline(f=f, s=s, names=['pds_adoption_use_ref_years'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_custom_name'], prefix=prefix)
  oneline(f=f, s=s, names=['source_until_2014'], prefix=prefix)
  oneline(f=f, s=s, names=['ref_source_post_2014'], prefix=prefix)
  oneline(f=f, s=s, names=['pds_source_post_2014'], prefix=prefix, suffix='\n')
  oneline(f=f, s=s, names=['solution_category'], prefix=prefix)

def xls(tab, row, col):
  """Return a quoted string read from tab(row, col)."""
  cell = tab.cell(row, col)
  if cell.ctype == xlrd.XL_CELL_ERROR or cell.ctype == xlrd.XL_CELL_EMPTY:
    return ''
  if cell.ctype == xlrd.XL_CELL_TEXT or cell.ctype == xlrd.XL_CELL_NUMBER:
    return "'" + str(cell.value).strip() + "'"
  raise ValueError("Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))

def xln(tab, row, col):
  """Return the string of a floating point number read from tab(row, col)."""
  cell = tab.cell(row, col)
  if cell.ctype == xlrd.XL_CELL_ERROR:
    return 'np.nan'
  if cell.ctype == xlrd.XL_CELL_NUMBER:
    return str(cell.value)
  if cell.ctype == xlrd.XL_CELL_EMPTY:
    return '0.0'
  raise ValueError("Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))

def xli(tab, row, col):
  """Return the string of an integer value read from tab(row, col)."""
  cell = tab.cell(row, col)
  if cell.ctype == xlrd.XL_CELL_ERROR:
    return 'np.nan'
  if cell.ctype == xlrd.XL_CELL_NUMBER:
    return str(int(cell.value))
  if cell.ctype == xlrd.XL_CELL_EMPTY:
    return '0'
  raise ValueError("Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))

def write_tam(f, wb):
  """Generate the TAM section of a solution.
     Arguments:
       f - file-like object for output
       wb - an Excel workbook as returned by xlrd
  """
  tm_tab = wb.sheet_by_name('TAM Data')
  f.write("    tamconfig_list = [\n")
  f.write("      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
  f.write("       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")
  f.write("      ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,\n")
  f.write("       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014,\n")
  f.write("       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014,\n")
  f.write("       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014],\n")
  f.write("      ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,\n")
  f.write("       " + xls(tm_tab, 15, 21) + ", " + xls(tm_tab, 18, 21) + ", " + xls(tm_tab, 21, 21) + ", ")
  f.write(            xls(tm_tab, 24, 21) + ", " + xls(tm_tab, 27, 21) + ", " + xls(tm_tab, 30, 21) + ",\n")
  f.write("       " + xls(tm_tab, 33, 21) + ", " + xls(tm_tab, 36, 21) + ", " + xls(tm_tab, 39, 21) + "],\n")
  # One might assume PDS_World for trend and growth would use self.ac.soln_pds_adoption_prognostication_*,
  # but that is not what the TAM Data in Excel does. EA104 references B19 and C19, the World trend and growth.
  f.write("      ['trend', " + xls(tm_tab, 18, 1) + ", " + xls(tm_tab, 18, 1) + ",\n")
  f.write("       " + xls(tm_tab, 16, 11) + ", " + xls(tm_tab, 19, 11) + ", " + xls(tm_tab, 22, 11) + ", ")
  f.write(            xls(tm_tab, 25, 11) + ", " + xls(tm_tab, 28, 11) + ", " + xls(tm_tab, 31, 11) + ",\n")
  f.write("       " + xls(tm_tab, 34, 11) + ", " + xls(tm_tab, 37, 11) + ", " + xls(tm_tab, 40, 11) + "],\n")
  f.write("      ['growth', " + xls(tm_tab, 18, 2) + ", " + xls(tm_tab, 18, 2) + ", " + xls(tm_tab, 16, 12) + ", ")
  f.write(            xls(tm_tab, 19, 12) + ",\n")
  f.write("       " + xls(tm_tab, 22, 12) + ", " + xls(tm_tab, 25, 12) + ", " + xls(tm_tab, 28, 12) + ", ")
  f.write(            xls(tm_tab, 31, 12) + ", " + xls(tm_tab, 34, 12) + ", " + xls(tm_tab, 37, 12) + ", ")
  f.write(            xls(tm_tab, 40, 12) + "],\n")
  f.write("      ['low_sd_mult', " + xln(tm_tab, 24, 1) + ", " + xln(tm_tab, 24, 1) + ", ")
  f.write(            xln(tm_tab, 16, 16) + ", " + xln(tm_tab, 19, 16) + ", " + xln(tm_tab, 22, 16) + ", ")
  f.write(            xln(tm_tab, 25, 16) + ", " + xln(tm_tab, 28, 16) + ", " + xln(tm_tab, 31, 16) + ", ")
  f.write(            xln(tm_tab, 34, 16) + ", " + xln(tm_tab, 37, 16) + ", " + xln(tm_tab, 40, 16) + "],\n")
  f.write("      ['high_sd_mult', " + xln(tm_tab, 23, 1) + ", " + xln(tm_tab, 23, 1) + ", ")
  f.write(            xln(tm_tab, 15, 16) + ", " + xln(tm_tab, 18, 16) + ", " + xln(tm_tab, 21, 16) + ", ")
  f.write(            xln(tm_tab, 24, 16) + ", " + xln(tm_tab, 27, 16) + ", " + xln(tm_tab, 30, 16) + ", ")
  f.write(            xln(tm_tab, 33, 16) + ", " + xln(tm_tab, 36, 16) + ", " + xln(tm_tab, 39, 16) + "]]\n")
  f.write("    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')\n")
  f.write("    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.tam_ref_data_sources,\n")
  f.write("      tam_pds_data_sources=rrs.tam_pds_data_sources)\n")
  f.write("    ref_tam_per_region=self.tm.ref_tam_per_region()\n")
  f.write("    pds_tam_per_region=self.tm.pds_tam_per_region()\n")
  f.write("\n")


def normalize_source_name(sourcename):
  """Return a common name for widely used studies.
     Correct mis-spelings and inconsistencies in the column names.
     A few solution files, notably OnshoreWind, are inconsistent about the ordering
     of columns between different regions, and additionally use inconsistent names
     and some spelling errors. We need the column names to be consistent to properly
     combine them.

     World
     +-------------------+-------------------+-----------------------------+---------+
     |   Baseline Cases  |  Ambitious Cases  |     Conservative Cases      |100% REN |
     +-------------------+-------------------+-----------------------------+---------+
     | source1 | source2 | source3 | source4 | source5 | source6 | source7 | source8 |

     OECD90 
     +-------------------+-------------------+-----------------------------+---------+
     |   Baseline Cases  |  Ambitious Cases  |     Conservative Cases      |100% REN |
     +-------------------+-------------------+-----------------------------+---------+
     | source2 | source1 | source3 | Source 4| surce5  | source6 | source7 | source8 |
  """
  special_cases = {
    'Based on: Greenpeace (2015) Reference': 'Based on: Greenpeace 2015 Reference',
    'Greenpeace 2015 Reference Scenario': 'Based on: Greenpeace 2015 Reference',
    'Based on Greenpeace 2015 Reference Scenario': 'Based on: Greenpeace 2015 Reference',
    'Based on Greenpeace 2015 Reference': 'Based on: Greenpeace 2015 Reference',
    }
  normalized = sourcename.replace("'", "").strip()
  if normalized in special_cases:
    return special_cases[normalized]
  if re.search(normalized, '\[Source \d+'):
    return None
  if re.search(normalized, 'Drawdown TAM: \[Source \d+'):
    return None

  name = re.sub(r"[\[\]]", "", sourcename.upper())  # [R]evolution to REVOLUTION
  if 'UN CES' in name and 'ITU' in name and 'AMPERE' in name:
    if 'BASELINE' in name: return 'Based on: CES ITU AMPERE Baseline'
    if '550' in name: return 'Based on: CES ITU AMPERE 550'
    if '450' in name: return 'Based on: CES ITU AMPERE 450'
    raise ValueError('Unknown UN CES ITU AMPERE source: ' + sourcename)
  if 'IEA' in name and 'ETP' in name:
    if '2016' in name and '6DS' in name: return 'Based on: IEA ETP 2016 6DS'
    if '2016' in name and '4DS' in name: return 'Based on: IEA ETP 2016 4DS'
    if '2016' in name and '2DS' in name and 'OPT2-PERENNIALS' in name:
      return 'Based on: IEA ETP 2016 2DS with OPT2 perennials'
    if '2016' in name and '2DS' in name: return 'Based on: IEA ETP 2016 2DS'
    if '2017' in name and 'REF' in name: return 'Based on: IEA ETP 2017 Ref Tech'
    if '2017' in name and 'B2DS' in name: return 'Based on: IEA ETP 2017 B2DS'
    if '2017' in name and '2DS' in name: return 'Based on: IEA ETP 2017 2DS'
    if '2017' in name and '4DS' in name: return 'Based on: IEA ETP 2017 4DS'
    if '2017' in name and '6DS' in name: return 'Based on: IEA ETP 2017 6DS'
    raise ValueError('Unknown IEA ETP source: ' + sourcename)
  if 'AMPERE' in name and 'MESSAGE' in name:
    if '450' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO 450'
    if '550' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO 550'
    if 'REF' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO Reference'
    raise ValueError('Unknown AMPERE MESSAGE-MACRO source: ' + sourcename)
  if 'AMPERE' in name and 'IMAGE' in name:
    if '450' in name: return 'Based on: AMPERE 2014 IMAGE TIMER 450'
    if '550' in name: return 'Based on: AMPERE 2014 IMAGE TIMER 550'
    if 'REF' in name: return 'Based on: AMPERE 2014 IMAGE TIMER Reference'
    raise ValueError('Unknown AMPERE IMAGE-TIMER source: ' + sourcename)
  if 'AMPERE' in name and 'GEM' in name and 'E3' in name:
    if '450' in name: return 'Based on: AMPERE 2014 GEM E3 450'
    if '550' in name: return 'Based on: AMPERE 2014 GEM E3 550'
    if 'REF' in name: return 'Based on: AMPERE 2014 GEM E3 Reference'
    raise ValueError('Unknown AMPERE GEM E3 source: ' + sourcename)
  if 'GREENPEACE' in name and 'ENERGY' in name:
    if 'ADVANCED' in name and 'DRAWDOWN-PERENNIALS' in name:
      return 'Based on: Greenpeace 2015 Advanced Revolution with Drawdown perennials'
    if 'ADVANCED' in name: return 'Based on: Greenpeace 2015 Advanced Revolution'
    if 'REVOLUTION' in name and 'DRAWDOWN-PERENNIALS' in name:
      return 'Based on: Greenpeace 2015 Energy Revolution with Drawdown perennials'
    if 'REVOLUTION' in name: return 'Based on: Greenpeace 2015 Energy Revolution'
    if 'REFERENCE' in name: return 'Based on: Greenpeace 2015 Reference'
    raise ValueError('Unknown Greenpeace Energy source: ' + sourcename)
  if 'GREENPEACE' in name and 'THERMAL' in name:
    if 'MODERATE' in name: return 'Based on: Greenpeace 2016 Solar Thermal Moderate'
    if 'ADVANCED' in name: return 'Based on: Greenpeace 2016 Solar Thermal Advanced'
    raise ValueError('Unknown Greenpeace Solar Thermal source: ' + sourcename)
  return normalized


def lookup_source_filename(sourcename, prefix=''):
  """Return string to use for the filename for known sources."""
  if re.search(r'\[Source \d+', sourcename):
    return None
  if re.search(r'Drawdown TAM: \[Source \d+', sourcename):
    return None

  filename = re.sub(r"[^\w\s\.]", '', sourcename)
  filename = re.sub(r"\s+", '_', filename)
  filename = re.sub(r"\.+", '_', filename)
  filename = filename.replace('Based_on_', 'based_on_')
  return prefix + filename + '.csv'


def write_ad(f, wb):
  """Generate the Adoption Data section of a solution.
     Arguments:
       f - file-like object for output
       wb - an Excel workbook as returned by xlrd
  """
  a = wb.sheet_by_name('Adoption Data')
  f.write("    adconfig_list = [\n")
  f.write("      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
  f.write("       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")
  f.write("      ['trend', self.ac.soln_pds_adoption_prognostication_trend, ")
  f.write(            xls(a, 16, 11) + ",\n")
  f.write("       " + xls(a, 19, 11) + ", " + xls(a, 22, 11) + ", ")
  f.write(            xls(a, 25, 11) + ", " + xls(a, 28, 11) + ", ")
  f.write(            xls(a, 31, 11) + ",\n")
  f.write("       " + xls(a, 34, 11) + ", " + xls(a, 37, 11) + ", ")
  f.write(            xls(a, 40, 11) + "],\n")
  f.write("      ['growth', self.ac.soln_pds_adoption_prognostication_growth, ")
  f.write(            xls(a, 16, 12) + ",\n")
  f.write("       " + xls(a, 19, 12) + ", " + xls(a, 22, 12) + ", " + xls(a, 25, 12) + ", ")
  f.write(            xls(a, 28, 12) + ", " + xls(a, 31, 12) + ",\n")
  f.write("       " + xls(a, 34, 12) + ", " + xls(a, 37, 12) + ", " + xls(a, 40, 12) + "],\n")
  f.write("      ['low_sd_mult', " + xln(a, 24, 1) + ", " + xln(a, 16, 16) + ", ")
  f.write(            xln(a, 19, 16) + ", " + xln(a, 22, 16) + ", " + xln(a, 25, 16) + ", ")
  f.write(            xln(a, 28, 16) + ", " + xln(a, 31, 16) + ", " + xln(a, 34, 16) + ", ")
  f.write(            xln(a, 37, 16) + ", " + xln(a, 40, 16) + "],\n")
  f.write("      ['high_sd_mult', " + xln(a, 23, 1) + ", " + xln(a, 15, 16) + ", ")
  f.write(            xln(a, 18, 16) + ", " + xln(a, 21, 16) + ", " + xln(a, 24, 16) + ", ")
  f.write(            xln(a, 27, 16) + ", " + xln(a, 30, 16) + ", " + xln(a, 33, 16) + ", ")
  f.write(            xln(a, 36, 16) + ", " + xln(a, 39, 16) + "]]\n")
  f.write("    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')\n")
  sources = extract_sources(wb_tab=wb.sheet_by_name('Adoption Data'),
      lines=[43, 103, 167, 230, 293, 356, 419, 483, 547, 612])
  f.write("    ad_data_sources = {\n")
  for case in sources.keys():
    f.write("      '" + case + "': {\n")
    for source in sources[case]:
      if not source:
        continue
      source = re.sub('\s+', ' ', source).strip()  # remove extra/double spaces
      filename = lookup_source_filename(source, prefix="ad_")
      if filename:
        f.write("        '" + source + "': str(thisdir.joinpath('" + filename + "')),\n")
    f.write("      },\n")
  f.write("    }\n")
  f.write("    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources, adconfig=adconfig)\n")
  f.write("    adoption_data_per_region = self.ad.adoption_data_per_region()\n")
  f.write("    adoption_trend_per_region = self.ad.adoption_trend_per_region()\n")
  f.write("    adoption_is_single_source = self.ad.adoption_is_single_source()\n")
  f.write("\n")


def write_custom_ad(f, wb, outputdir):
  """Generate the Custom Adoption Data section of a solution.
     Arguments:
       f - file-like object for output
       wb - an Excel workbook as returned by xlrd
       outputdir: name of directory to write CSV files to.
  """
  scenarios = extract_custom_adoption(wb=wb, outputdir=outputdir)
  f.write("    custom_ad_data_sources = {\n")
  for s in scenarios:
    f.write("      '" + s['name'] + "': {'include': " + str(s['include']) + ",\n")
    f.write("          'filename': str(thisdir.joinpath('" + s['filename'] + "'))},\n")
  f.write("    }\n")
  f.write("    self.custom_ad = customadoption.CustomAdoption(scenario_type='PDS',\n")
  f.write("        data_sources=custom_ad_data_sources,\n")
  f.write("        soln_pds_adoption_custom_name=self.ac.soln_pds_adoption_custom_name)\n")
  f.write("    adoption_data_per_region = self.custom_ad.adoption_data_per_region()\n")
  f.write("    adoption_trend_per_region = self.custom_ad.adoption_trend_per_region()\n")
  f.write("    adoption_is_single_source = True\n")
  f.write("\n")


def write_ht(f, wb):
  """Generate the Helper Tables section of a solution.
     Arguments:
       f - file-like object for output
       wb - an Excel workbook as returned by xlrd
  """
  h = wb.sheet_by_name('Helper Tables')
  initial_datapoint_year = int(h.cell_value(*cell_to_offsets('B21')))
  final_datapoint_year = int(h.cell_value(*cell_to_offsets('B22')))

  f.write("    ht_ref_adoption_initial = pd.Series(\n")
  r = [xln(h, 20, n) for n in range(2, 7)]
  f.write("      [" + ", ".join(r) + ",\n")
  r = [xln(h, 20, n) for n in range(7, 12)]
  f.write("       " + ", ".join(r) + "],\n")
  f.write("       index=REGIONS)\n")
  f.write("    ht_ref_adoption_final = ref_tam_per_region.loc[" + str(final_datapoint_year) + "] * ")
  f.write("(ht_ref_adoption_initial / ref_tam_per_region.loc[" + str(initial_datapoint_year) + "])\n")
  f.write("    ht_ref_datapoints = pd.DataFrame(columns=REGIONS)\n")
  f.write("    ht_ref_datapoints.loc[" + str(initial_datapoint_year) + "] = ht_ref_adoption_initial\n")
  f.write("    ht_ref_datapoints.loc[" + str(final_datapoint_year) + "] = ht_ref_adoption_final\n")

  f.write("    ht_pds_adoption_initial = ht_ref_adoption_initial\n")
  f.write("    ht_pds_adoption_final_percentage = pd.Series(\n")
  r = [xln(h, 83, n) for n in range(2, 7)]
  f.write("      [" + ", ".join(r) + ",\n")
  r = [xln(h, 83, n) for n in range(7, 12)]
  f.write("       " + ", ".join(r) + "],\n")
  f.write("       index=REGIONS)\n")
  f.write("    ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[" + str(final_datapoint_year) + "]\n")
  f.write("    ht_pds_datapoints = pd.DataFrame(columns=REGIONS)\n")
  f.write("    ht_pds_datapoints.loc[" + str(initial_datapoint_year) + "] = ht_pds_adoption_initial\n")
  f.write("    ht_pds_datapoints.loc[" + str(final_datapoint_year) + "] = ht_pds_adoption_final\n")

  f.write("    self.ht = helpertables.HelperTables(ac=self.ac,\n")
  f.write("        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,\n")
  f.write("        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,\n")
  f.write("        adoption_data_per_region=adoption_data_per_region,\n")
  f.write("        adoption_trend_per_region=adoption_trend_per_region,\n")
  f.write("        adoption_is_single_source=adoption_is_single_source)\n")
  f.write("\n")


def write_ua(f):
  """Write out the Unit Adoption module for this solution class."""
  f.write("    self.ua = unitadoption.UnitAdoption(ac=self.ac, datadir=datadir,\n")
  f.write("        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,\n")
  f.write("        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),\n")
  f.write("        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted())\n")
  f.write("    soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()\n")
  f.write("    soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()\n")
  f.write("    conv_ref_tot_iunits_reqd = self.ua.conv_ref_tot_iunits_reqd()\n")
  f.write("    soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()\n")
  f.write("\n")


def write_fc(f, wb):
  """Code generate the First Code module for this solution class."""
  fc_tab = wb.sheet_by_name('First Cost')
  f.write("    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=" + xli(fc_tab, 24, 2) + ",\n")
  f.write("        ref_learning_increase_mult=" + xli(fc_tab, 24, 3)
      + ", conv_learning_increase_mult=" + xli(fc_tab, 24, 4) + ",\n")
  f.write("        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,\n")
  f.write("        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,\n")
  f.write("        conv_ref_tot_iunits_reqd=conv_ref_tot_iunits_reqd,\n")
  f.write("        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),\n")
  f.write("        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),\n")
  f.write("        conv_ref_new_iunits_reqd=self.ua.conv_ref_new_iunits_reqd())\n")
  f.write('\n')


def write_oc(f, wb):
  """Code generate the Operating Code module for this solution class."""
  oc_tab = wb.sheet_by_name('Operating Cost')
  f.write("    self.oc = operatingcost.OperatingCost(ac=self.ac,\n")
  f.write("        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,\n")
  f.write("        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,\n")
  f.write("        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,\n")
  f.write("        conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),\n")
  f.write("        soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),\n")
  f.write("        soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),\n")
  f.write("        conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),\n")
  f.write("        single_iunit_purchase_year=" + xli(oc_tab, 120, 8) + ",\n")
  f.write("        soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),\n")
  f.write("        conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit())\n")
  f.write('\n')


def write_c2_c4(f):
  """Write out the CO2 Calcs and CH4 Calcs modules for this solution class."""
  f.write("    self.c4 = ch4calcs.CH4Calcs(ac=self.ac,\n")
  f.write("        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)\n")
  f.write("    self.c2 = co2calcs.CO2Calcs(ac=self.ac,\n")
  f.write("        ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),\n")
  f.write("        soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),\n")
  f.write("        soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),\n")
  f.write("        soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),\n")
  f.write("        soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),\n")
  f.write("        soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),\n")
  f.write("        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),\n")
  f.write("        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),\n")
  f.write("        conv_ref_new_iunits_reqd=self.ua.conv_ref_new_iunits_reqd(),\n")
  f.write("        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),\n")
  f.write("        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),\n")
  f.write("        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,\n")
  f.write("        fuel_in_liters=False)\n")
  f.write("\n")


def write_to_dict(f, has_tam):
  """Write out the to_dict() routine for this solution class."""
  f.write("  def to_dict(self):\n")
  f.write('    """Return all data as a dict, to be serialized to JSON."""\n')
  f.write("    rs = dict()\n")
  if has_tam:
    f.write("    rs['tam_data'] = self.tm.to_dict()\n")
  f.write("    rs['adoption_data'] = self.ad.to_dict()\n")
  f.write("    rs['helper_tables'] = self.ht.to_dict()\n")
  f.write("    rs['emissions_factors'] = self.ef.to_dict()\n")
  f.write("    rs['unit_adoption'] = self.ua.to_dict()\n")
  f.write("    rs['first_cost'] = self.fc.to_dict()\n")
  f.write("    rs['operating_cost'] = self.oc.to_dict()\n")
  f.write("    rs['ch4_calcs'] = self.c4.to_dict()\n")
  f.write("    rs['co2_calcs'] = self.c2.to_dict()\n")
  f.write("    return rs\n")
  f.write("\n")


def extract_sources(wb_tab, lines):
  """Pull the names of sources, by case, from the Excel file.
     Arguments:
       wb_tab: an Excel workbook tab as returned by wb.sheet_by_name
       lines: list of row numbers to process

     Returns: a dict of category keys, containing lists of source names.

     Parsing the data sources can be messy: the number of sources within each category
     varies between solutions, and even the names of the cases can vary. Most solutions have
     Baseline/Ambitious/Conservative, but we're not sure that all do, and the final most
     aggressive case varies in names like "100% REN" (renewables) or "Maximum Cases".
     +-------------------+-------------------+-----------------------------+---------+
     |   Baseline Cases  |  Ambitious Cases  |     Conservative Cases      |100% REN |
     +-------------------+-------------------+-----------------------------+---------+
     | source1 | source2 | source3 | source4 | source5 | source6 | source7 | source8 | Functional Unit

     The category label like "Baseline Cases" is a merged cell one, two, three, or more cells
     across. In xlrd, the first cell contains the string and the subsequent cells are ctype
     XL_CELL_EMPTY. They have a border, but at the time of this writing xlrd does not extract
     styling information like borders from xlsx/xlsm files (only the classic Excel file format).
  """
  sources = {}
  for line in lines:
    case = ''
    for col in range(2, wb_tab.ncols):
      if wb_tab.cell(line+1, col).value == 'Functional Unit':
        break
      if wb_tab.cell(line, col).ctype != xlrd.XL_CELL_EMPTY:
        case = wb_tab.cell(line, col).value
        l = sources.get(case, list())
      new_source = normalize_source_name(wb_tab.cell(line+1, col).value)
      if new_source not in l:
        l.append(new_source)
        sources[case] = l
  return sources


def extract_adoption_data(wb, outputdir):
  """Create CSV files for Adoption Data.
     Arguments:
       wb: Excel workbook
       outputdir: name of directory to write CSV files to.
     Returns: dict of {'source name': 'filename'} mappings
  """
  world = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=44, nrows=49)
  world.name = 'World'
  world.rename(columns=normalize_source_name, inplace=True)
  oecd90 = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=104, nrows=49)
  oecd90.name = 'OECD90'
  oecd90.rename(columns=normalize_source_name, inplace=True)
  eastern_europe = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=168, nrows=49)
  eastern_europe.name ='Eastern Europe'
  eastern_europe.rename(columns=normalize_source_name, inplace=True)
  asia_sans_japan = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=231, nrows=49)
  asia_sans_japan.name = 'Asia (Sans Japan)'
  asia_sans_japan.rename(columns=normalize_source_name, inplace=True)
  middle_east_and_africa = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=294, nrows=49)
  middle_east_and_africa.name = 'Middle East and Africa'
  middle_east_and_africa.rename(columns=normalize_source_name, inplace=True)
  latin_america = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=357, nrows=49)
  latin_america.name = 'Latin America'
  latin_america.rename(columns=normalize_source_name, inplace=True)
  china = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=420, nrows=49)
  china.name = 'China'
  china.rename(columns=normalize_source_name, inplace=True)
  india = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=484, nrows=49)
  india.name = 'India'
  india.rename(columns=normalize_source_name, inplace=True)
  eu = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=548, nrows=49)
  eu.name = 'EU'
  eu.rename(columns=normalize_source_name, inplace=True)
  usa = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=613, nrows=49)
  usa.name = 'USA'
  usa.rename(columns=normalize_source_name, inplace=True)

  sources = {}
  for region in [world, oecd90, eastern_europe, asia_sans_japan, middle_east_and_africa,
      latin_america, china, india, eu, usa]:
    for source_name in region.columns:
      sources[source_name] = ''

  for source_name in sources:
    if not source_name:
      continue
    filename = lookup_source_filename(source_name, prefix='ad_')
    df_nan = pd.Series(np.nan, index=world.index)
    df = pd.concat({
      'World': world.get(source_name, df_nan), 'OECD90': oecd90.get(source_name, df_nan),
      'Eastern Europe': eastern_europe.get(source_name, df_nan),
      'Asia (Sans Japan)': asia_sans_japan.get(source_name, df_nan),
      'Middle East and Africa': middle_east_and_africa.get(source_name, df_nan),
      'Latin America': latin_america.get(source_name, df_nan),
      'China': china.get(source_name, df_nan), 'India': india.get(source_name, df_nan),
      'EU': eu.get(source_name, df_nan), 'USA': usa.get(source_name, df_nan)},
      axis=1)
    if df.empty or not filename:
      continue
    df.index = df.index.astype(int)
    df.index.name = 'Year'
    # In the Excel implementation, adoption data of 0.0 is treated the same as N/A,
    # no data available. We don't want to implement adoptiondata.py the same way, we
    # want to be able to express the difference between a solution which did not
    # exist prior to year N, and therefore had 0.0 adoption, from a solution which
    # did exist but for which we have no data prior to year N.
    # We're handling this in the code generator: when extracting adoption data from
    # an Excel file, treat values of 0.0 as N/A and write out a CSV file with no
    # data at that location.
    df.replace(to_replace=0.0, value=np.nan, inplace=True)
    outputfile = os.path.join(outputdir, filename)
    df[['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
      'Latin America', 'China', 'India', 'EU', 'USA']].to_csv(outputfile, header=True)
    sources[source_name] = filename
  return sources


def extract_fresh_adoption_data(wb, outputdir):
  """Create CSV files for Fresh Adoption Data, if present.
     Arguments:
       wb: Excel workbook
       outputdir: name of directory to write CSV files to.
     Returns: dict of {'source name': 'filename'} mappings
  """
  if 'Fresh Adoption Data' not in wb.sheets():
    return

  world = pd.read_excel(wb, engine='xlrd', sheet_name='Fresh Adoption Data', header=0, index_col=0, usecols="B:R", skiprows=5, nrows=49)
  world.name = 'World'

  sources = {}
  ad_tab = wb.sheet_by_name('Fresh Adoption Data')
  for col in range(2, ad_tab.ncols):
    if ad_tab.cell(5, col).value == 'Functional Unit':
      break
    source_name = ad_tab.cell(5, col).value
    filename = lookup_source_filename(source_name, prefix='ad_')
    df_nan = pd.Series(np.nan, index=world.index)
    df = pd.concat({'World': world[source_name], 'OECD90': df_nan,
      'Eastern Europe': df_nan, 'Asia (Sans Japan)': df_nan,
      'Middle East and Africa': df_nan, 'Latin America': df_nan,
      'China': df_nan, 'India': df_nan, 'EU': df_nan, 'USA': df_nan,
      }, axis=1)
    if df.empty or not filename:
      continue
    df.index = df.index.astype(int)
    df.index.name = 'Year'
    # In the Excel implementation, adoption data of 0.0 is treated the same as N/A,
    # no data available. We don't want to implement adoptiondata.py the same way, we
    # want to be able to express the difference between a solution which did not
    # exist prior to year N, and therefore had 0.0 adoption, from a solution which
    # did exist but for which we have no data prior to year N.
    # We're handling this in the code generator: when extracting adoption data from
    # an Excel file, treat values of 0.0 as N/A and write out a CSV file with no
    # data at that location.
    df.replace(to_replace=0.0, value=np.nan, inplace=True)
    outputfile = os.path.join(outputdir, filename)
    df[['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
      'Latin America', 'China', 'India', 'EU', 'USA']].to_csv(outputfile, header=True)
    sources[source_name] = filename
  return sources


def extract_custom_adoption(wb, outputdir):
  """Extract custom adoption scenarios from an Excel file.
     Arguments:
       wb: Excel workbook as returned by xlrd.
       outputdir: directory where output files are written
  """
  custom_ad_tab = wb.sheet_by_name('Custom PDS Adoption')
  scenarios = []
  for row in range(20, 36):
    if not re.search(r"Scenario \d+", str(custom_ad_tab.cell(row, 13).value)):
      continue
    name = str(custom_ad_tab.cell(row, 14).value)
    includestr = str(custom_ad_tab.cell_value(row, 18))
    include = convert_bool(includestr) if includestr else False
    filename = lookup_source_filename(name, prefix='custom_ad_')
    if not filename:
      continue
    skip = True 
    for row in range(0, custom_ad_tab.nrows):
      if str(custom_ad_tab.cell(row, 1).value) == name:
        df = pd.read_excel(wb, engine='xlrd', sheet_name='Custom PDS Adoption',
            header=0, index_col=0, usecols="A:K", skiprows=row+1, nrows=49)
        if not df.dropna(how='all', axis=1).dropna(how='all', axis=0).empty:
          df.to_csv(os.path.join(outputdir, filename), index=True, header=True)
          skip = False
        break
    if not skip:
      scenarios.append({'name': name, 'filename': filename, 'include': include})
  return scenarios


def output_solution_python_file(outputdir, xl_filename, classname):
  """Extract relevant fields from Excel file and output a Python class.

     Arguments:
       outputdir: filename to write to. None means stdout.
       xl_filename: an Excel file to open, can be xls/xlsm/etc.
         Note that we cannot run Macros from xlsm files, only read values.
       classname: what name to give to the generated Python class.
  """
  py_filename = '-' if outputdir is None else os.path.join(outputdir, '__init__.py')
  wb = xlrd.open_workbook(filename=xl_filename)
  ac_tab = wb.sheet_by_name('Advanced Controls')

  is_rrs = 'RRS' in xl_filename
  is_land = 'PDLAND' in xl_filename or 'L-UseAgr' in xl_filename
  has_tam = is_rrs

  f = open(py_filename, 'w') if py_filename != '-' else sys.stdout

  solution_name = ac_tab.cell_value(39, 2)  # 'Advanced Controls'!C40
  f.write('"""' + str(solution_name) + ' solution model.\n')
  f.write('   Excel filename: ' + os.path.basename(xl_filename) + '\n')
  f.write('"""\n')
  f.write('\n')
  f.write('import pathlib\n')
  f.write('\n')
  f.write('import numpy as np\n')
  f.write('import pandas as pd\n')
  f.write('\n')
  f.write('from model import adoptiondata\n')
  f.write('from model import advanced_controls\n')
  f.write('from model import ch4calcs\n')
  f.write('from model import co2calcs\n')
  f.write('from model import emissionsfactors\n')
  f.write('from model import firstcost\n')
  f.write('from model import helpertables\n')
  f.write('from model import operatingcost\n')
  f.write('from model import unitadoption\n')
  f.write('from model import vma\n')
  f.write('\n')

  if is_rrs:
    f.write('from solution import rrs\n\n')
    scenarios = get_rrs_scenarios(wb=wb)
  elif is_land:
    scenarios = get_land_scenarios(wb=wb)
  else:
    scenarios = {}

  f.write("REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',\n")
  f.write("           'Latin America', 'China', 'India', 'EU', 'USA']\n")
  f.write("\n")

  is_custom_adoption = False
  is_default_adoption = False
  for s in scenarios.values():
    basis = s.get('soln_pds_adoption_basis', '')
    if basis == 'Fully Customized PDS':
      is_custom_adoption = True
    if basis == 'Existing Adoption Prognostications':
      is_default_adoption = True
  assert is_custom_adoption or is_default_adoption
  assert not (is_custom_adoption and is_default_adoption)

  if has_tam:
    f.write('from model import tam\n')
  
  f.write('scenarios = {\n')
  for name, s in scenarios.items():
    prefix = '  '
    f.write(prefix + "'" + name + "': advanced_controls.AdvancedControls(\n")
    write_scenario(f=f, s=s)
    f.write(2*prefix + '),\n')
  f.write('}\n\n')

  f.write("class " + str(classname) + ":\n")
  f.write("  name = '" + str(solution_name) + "'\n")
  f.write("  def __init__(self, scenario=None):\n")
  f.write("    datadir = str(pathlib.Path(__file__).parents[2].joinpath('data'))\n")
  f.write("    parentdir = pathlib.Path(__file__).parents[1]\n")
  f.write("    thisdir = pathlib.Path(__file__).parents[0]\n")
  f.write("    if scenario is None:\n")
  f.write("      scenario = '" + list(scenarios.keys())[0] + "'\n")
  f.write("    self.scenario = scenario\n")
  f.write("    self.ac = scenarios[scenario]\n")
  f.write("\n")
  if has_tam:
    write_tam(f=f, wb=wb)
  if is_default_adoption:
    extract_adoption_data(wb=wb, outputdir=outputdir)
    extract_fresh_adoption_data(wb=wb, outputdir=outputdir)
    write_ad(f=f, wb=wb)
  if is_custom_adoption:
    write_custom_ad(f=f, wb=wb, outputdir=outputdir)
  write_ht(f=f, wb=wb)
  f.write("    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)\n")
  f.write("\n")
  write_ua(f=f)
  write_fc(f=f, wb=wb)
  write_oc(f=f, wb=wb)
  write_c2_c4(f=f)

  if is_rrs:
    f.write("    self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],\n")
    f.write("        soln_avg_annual_use=self.ac.soln_avg_annual_use,\n")
    f.write("        conv_avg_annual_use=self.ac.conv_avg_annual_use)\n")
    f.write("\n")

  f.write("    self.VMAs = []\n")
  f.write("\n")
  write_to_dict(f=f, has_tam=has_tam)

  for key, values in scenarios.items():
    if values:
      raise KeyError('Scenario ' + key + ' has unconsumed fields: ' + str(values.keys()))

  f.close()


def infer_classname(filename):
  """Pick a reasonable classname if none is specified."""
  special_cases = [
      ('BiomassELC', 'Biomass'),
      ('Biomass from Perennial Crops for Electricity Generation', 'Biomass'),
      ('CHP_A_', 'CoGenElectricity'),
      ('CHP_B_', 'CoGenHeat'),
      ('CSP_', 'ConcentratedSolar'),
      ('Instream Hydro', 'InstreamHydro'),
      ('Large Biodigesters', 'Biogas'),
      ('MicroWind Turbines', 'MicroWind'),
      ('Regenerative_Agriculture', 'RegenerativeAgriculture'),
      ('Rooftop Solar PV', 'SolarPVRoof'),
      ('SolarPVUtility', 'SolarPVUtil'),
      ('SolarPVRooftop', 'SolarPVRoof'),
      ('solution_xls_extract_RRS_test_A', 'TestClassA'),
      ('Tropical_Forest_Restoration', 'TropicalForests'),
      ('Utility Scale Solar PV', 'SolarPVUtil'),
      ('WastetoEnergy', 'WasteToEnergy'),
      ('Wave&Tidal', 'WaveAndTidal'),
      ('Wave and Tidal', 'WaveAndTidal'),
      ('Wind Offshore', 'OffshoreWind'),
      ]
  for (pattern, classname) in special_cases:
    if pattern.replace(' ', '').lower() in filename.replace(' ', '').lower():
      return classname
  namelist = re.split('[_-]', os.path.basename(filename))
  if namelist[0] == 'Drawdown':
    namelist.pop(0)
  return namelist[0].replace(' ', '')


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description='Create python Drawdown solution from Excel version.')
  parser.add_argument('--excelfile', required=True, help='Excel filename to process')
  parser.add_argument('--outputdir', default=None, help='Directory to write generated Python code to')
  parser.add_argument('--classname', help='Name for Python class')
  args = parser.parse_args(sys.argv[1:])

  if args.classname is None:
    args.classname = infer_classname(filename=args.excelfile)

  output_solution_python_file(outputdir=args.outputdir, xl_filename=args.excelfile,
      classname=args.classname)
