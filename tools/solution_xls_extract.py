#!/usr/bin/env python
"""Extract parameters from a Drawdown excel model to help create
   the Python implementation of the solution and its scenarios.
"""

import argparse
import os.path
import re
import sys

import xlrd
import pandas as pd

from tools.util import convert_bool, cell_to_offsets


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

      assert sr_tab.cell_value(row + 111, 1) == 'Indirect Emissions'
      s['conv_indirect_co2_per_unit'] = convert_sr_float(sr_tab.cell_value(row + 112, 4))
      s['soln_indirect_co2_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 113, 4))
      i_vs_f = str(sr_tab.cell_value(row + 114, 4)).lower()
      s['conv_indirect_co2_is_iunits'] = False if i_vs_f == 'functional' else True

      assert sr_tab.cell_value(row + 118, 1) == 'Optional Inputs'
      s['co2eq_conversion_source'] = str(sr_tab.cell_value(row + 121, 4))

      assert sr_tab.cell_value(row + 124, 1) == 'General Climate Inputs'
      s['emissions_use_co2eq'] = convert_bool(sr_tab.cell_value(row + 125, 4))
      s['emissions_grid_source'] = str(sr_tab.cell_value(row + 126, 4))
      s['emissions_grid_range'] = str(sr_tab.cell_value(row + 127, 4))

      assert sr_tab.cell_value(row + 135, 1) == 'TAM'
      s['source_until_2014'] = str(sr_tab.cell_value(row + 136, 4))
      s['ref_source_post_2014'] = str(sr_tab.cell_value(row + 136, 7))
      s['pds_source_post_2014'] = str(sr_tab.cell_value(row + 136, 10))

      assert sr_tab.cell_value(row + 163, 1) == 'PDS ADOPTION SCENARIO INPUTS'
      s['soln_pds_adoption_basis'] = str(sr_tab.cell_value(row + 164, 4))
      s['soln_pds_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 165, 4))

      assert sr_tab.cell_value(row + 183, 1) == 'Existing PDS Prognostication Assumptions'
      s['soln_pds_adoption_prognostication_source']= str(sr_tab.cell_value(row + 184, 4))
      s['soln_pds_adoption_prognostication_trend'] = str(sr_tab.cell_value(row + 185, 4))
      s['soln_pds_adoption_prognostication_growth'] = str(sr_tab.cell_value(row + 186, 4))

      assert sr_tab.cell_value(row + 198, 1) == 'REF ADOPTION SCENARIO INPUTS'
      s['soln_ref_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 201, 4))

      # From Advanced Controls
      (r, c) = cell_to_offsets('A159')
      s['solution_category'] = ac_tab.cell_value(r, c)

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
      prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['soln_lifetime_capacity', 'soln_avg_annual_use'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_lifetime_capacity', 'conv_avg_annual_use'],
      prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['soln_var_oper_cost_per_funit', 'soln_fuel_cost_per_funit'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_fixed_oper_cost_per_iunit'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_var_oper_cost_per_funit', 'conv_fuel_cost_per_funit'], prefix=prefix)
  oneline(f=f, s=s, names=['conv_fixed_oper_cost_per_iunit'], prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['emissions_grid_source', 'emissions_grid_range'], prefix=prefix)
  oneline(f=f, s=s, names=['emissions_use_co2eq'], prefix=prefix, suffix='\n')

  oneline(f=f, s=s, names=['soln_ref_adoption_regional_data',
    'soln_pds_adoption_regional_data'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_basis'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_source'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_trend'], prefix=prefix)
  oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_growth'], prefix=prefix)
  oneline(f=f, s=s, names=['source_until_2014'], prefix=prefix)
  oneline(f=f, s=s, names=['ref_source_post_2014'], prefix=prefix)
  oneline(f=f, s=s, names=['pds_source_post_2014'], prefix=prefix, suffix='\n')
  oneline(f=f, s=s, names=['solution_category'], prefix=prefix)


def write_tam(f, wb):
  """Generate the TAM section of a solution.
     Arguments:
       f - file-like object for output
       wb - an Excel workbook as returned by xlrd
  """
  tm_tab = wb.sheet_by_name('TAM Data')
  # concise routines to return strings and numbers extracted from Excel.
  def xls(row, col): return "'" + str(tm_tab.cell_value(row, col)) + "'"
  def xln(row, col): return str(tm_tab.cell_value(row, col))
  f.write("    tamconfig_list = [\n")
  f.write("      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
  f.write("       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")
  f.write("      ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,\n")
  f.write("       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014,\n")
  f.write("       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014,\n")
  f.write("       self.ac.source_until_2014, self.ac.source_until_2014, self.ac.source_until_2014],\n")
  f.write("      ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,\n")
  f.write("       " + xls(15, 21) + ", " + xls(18, 21) + ", " + xls(21, 21) + ", " + xls(24, 21) + ", ")
  f.write(            xls(27, 21) + ", " + xls(30, 21) + ",\n")
  f.write("       " + xls(33, 21) + ", " + xls(36, 21) + ", " + xls(39, 21) + "],\n")
  # One might assume PDS_World for trend and growth would use self.ac.soln_pds_adoption_prognostication_*,
  # but that is not what the TAM Data in Excel does. EA104 references B19 and C19, the World trend and growth.
  f.write("      ['trend', " + xls(18, 1) + ", " + xls(18, 1) + ",\n")
  f.write("       " + xls(16, 11) + ", " + xls(19, 11) + ", " + xls(22, 11) + ", " + xls(25, 11) + ", ")
  f.write(            xls(28, 11) + ", " + xls(31, 11) + ",\n")
  f.write("       " + xls(34, 11) + ", " + xls(37, 11) + ", " + xls(40, 11) + "],\n")
  f.write("      ['growth', " + xls(18, 2) + ", " + xls(18, 2) + ", " + xls(16, 12) + ", " + xls(19, 12) + ",\n")
  f.write("       " + xls(22, 12) + ", " + xls(25, 12) + ", " + xls(28, 12) + ", " + xls(31, 12) + ", ")
  f.write(            xls(34, 12) + ", " + xls(37, 12) + ", " + xls(40, 12) + "],\n")
  f.write("      ['low_sd_mult', " + xln(24, 1) + ", " + xln(24, 1) + ", " + xln(16, 16) + ", ")
  f.write(            xln(19, 16) + ", " + xln(22, 16) + ", " + xln(25, 16) + ", " + xln(28, 16) + ", ")
  f.write(            xln(31, 16) + ", " + xln(34, 16) + ", " + xln(37, 16) + ", " + xln(40, 16) + "],\n")
  f.write("      ['high_sd_mult', " + xln(23, 1) + ", " + xln(23, 1) + ", " + xln(15, 16) + ", ")
  f.write(            xln(18, 16) + ", " + xln(21, 16) + ", " + xln(24, 16) + ", " + xln(27, 16) + ", ")
  f.write(            xln(30, 16) + ", " + xln(33, 16) + ", " + xln(36, 16) + ", " + xln(39, 16) + "]]\n")
  f.write("    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')\n")
  f.write("    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.tam_ref_data_sources,\n")
  f.write("      tam_pds_data_sources=rrs.tam_pds_data_sources)\n")
  f.write("    ref_tam_per_region=self.tm.ref_tam_per_region()\n")
  f.write("    pds_tam_per_region=self.tm.pds_tam_per_region()\n")
  f.write("\n")


def lookup_ad_source_filename(source_name):
  """Return string to use for the filename for known sources."""
  map_sources = {
    "Based on: IEA ETP 2016 6DS": 'IEA_ETP_2016_6DS',
    "Based on: IEA ETP 2016 - 6DS": 'IEA_ETP_2016_6DS',
    "Based on: AMPERE (2014) IMAGE Refpol": 'AMPERE_2014_IMAGE_REF',
    "Based on: AMPERE IMAGE REFpol": 'AMPERE_2014_IMAGE_REF',
    "Based on: AMPERE (2014) MESSAGE REFPol": 'AMPERE_2014_MESSAGE_REF',
    "Based on: AMPERE MESSAGE REFpol": 'AMPERE_2014_MESSAGE_REF',
    "Based on: AMPERE (2014) GEM E3 REFpol": 'AMPERE_2014_GEM_E3_REF',
    "Based on: AMPERE GEM E3 REFpol": 'AMPERE_2014_GEM_E3_REF',
    "Based on: IEA ETP 2016 4DS": 'IEA_ETP_2016_4DS',
    "Based on: IEA ETP 2016 - 4DS": 'IEA_ETP_2016_4DS',
    "Based on: AMPERE (2014) IMAGE 550": 'AMPERE_2014_IMAGE_550',
    "Based on: AMPERE IMAGE 550": 'AMPERE_2014_IMAGE_550',
    "Based on: AMPERE (2014) MESSAGE 550": 'AMPERE_2014_MESSAGE_550',
    "Based on: AMPERE MESSAGE 550": 'AMPERE_2014_MESSAGE_550',
    "Based on: AMPERE (2014) GEM E3 550": 'AMPERE_2014_GEM_E3_550',
    "Based on: AMPERE GEM E3 550": 'AMPERE_2014_GEM_E3_550',
    "Based on: Greenpeace (2015) Reference": 'Greenpeace_2015_Reference',
    "Based on: IEA ETP 2016 2DS": 'IEA_ETP_2016_2DS',
    "Based on: IEA ETP 2016 - 2DS": 'IEA_ETP_2016_2DS',
    "Based on: AMPERE (2014) IMAGE 450": 'AMPERE_2014_IMAGE_450',
    "Based on: AMPERE IMAGE 450": 'AMPERE_2014_IMAGE_450',
    "Based on: AMPERE (2014) MESSAGE 450": 'AMPERE_2014_MESSAGE_450',
    "Based on: AMPERE MESSAGE 450": 'AMPERE_2014_MESSAGE_450',
    "Based on: AMPERE (2014) GEM E3 450": 'AMPERE_2014_GEM_E3_450',
    "Based on: AMPERE GEM E3 450": 'AMPERE_2014_GEM_E3_450',
    "Based on: Greenpeace (2015) Energy Revolution": 'Greenpeace_2015_Energy_Revolution',
    "Based on: Greenpeace 2015 Energy Revolution Scenario": 'Greenpeace_2015_Energy_Revolution',
    "Based on: Greenpeace (2015) Advanced Energy Revolution": 'Greenpeace_2015_Advanced_Energy_Revolution',
    "Based on: Greenpeace 2015 Advanced Energy Revolution Scenario": 'Greenpeace_2015_Advanced_Energy_Revolution',
    "Based on: Greenpeace Solar Thermal Elc Global Outlook 2016 (Moderate Scenario)": 'Greenpeace_2016_Solar_Thermal_Moderate',
    "Based on: Greenpeace Solar Thermal Elc Global Outlook 2016 (Advanced Scenario)": 'Greenpeace_2016_Solar_Thermal_Advanced',
    }
  known_sources = {
    'IEA_ETP_2016_6DS': 'ad_based_on_IEA_ETP_2016_6DS.csv',
    'AMPERE_2014_IMAGE_REF': 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv',
    'AMPERE_2014_MESSAGE_REF': 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv',
    'AMPERE_2014_GEM_E3_REF': 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv',
    'IEA_ETP_2016_4DS': 'ad_based_on_IEA_ETP_2016_4DS.csv',
    'AMPERE_2014_IMAGE_550': 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv',
    'AMPERE_2014_MESSAGE_550': 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv',
    'AMPERE_2014_GEM_E3_550': 'ad_based_on_AMPERE_2014_GEM_E3_550.csv',
    'Greenpeace_2015_Reference': 'ad_based_on_Greenpeace_2015_Reference.csv',
    'IEA_ETP_2016_2DS': 'ad_based_on_IEA_ETP_2016_2DS.csv',
    'AMPERE_2014_IMAGE_450': 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv',
    'AMPERE_2014_MESSAGE_450': 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv',
    'AMPERE_2014_GEM_E3_450': 'ad_based_on_AMPERE_2014_GEM_E3_450.csv',
    'Greenpeace_2015_Energy_Revolution': 'ad_based_on_Greenpeace_2015_Energy_Revolution.csv',
    '[Source 6 - Ambitious]': 'ad_source_6_ambitious.csv',
    'Greenpeace_2015_Advanced_Energy_Revolution': 'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv',
    'Greenpeace_2016_Solar_Thermal_Moderate': 'ad_based_on_Greenpeace_2016_Solar_Thermal_Moderate.csv',
    'Greenpeace_2016_Solar_Thermal_Advanced': 'ad_based_on_Greenpeace_2016_Solar_Thermal_Advanced.csv',
    }
  source_id = map_sources.get(source_name, source_name)
  return known_sources.get(source_id, '')


def write_ad(f, wb):
  """Generate the Adoption Data section of a solution.
     Arguments:
       f - file-like object for output
       wb - an Excel workbook as returned by xlrd
  """
  ad_tab = wb.sheet_by_name('Adoption Data')
  # concise routines to return strings and numbers extracted from Excel.
  def xls(row, col): return str(ad_tab.cell_value(row, col)).strip()
  def xln(row, col): return str(ad_tab.cell_value(row, col))
  f.write("    adconfig_list = [\n")
  f.write("      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
  f.write("       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")
  f.write("      ['trend', self.ac.soln_pds_adoption_prognostication_trend, '" + xls(16, 11) + "',\n")
  f.write("       '" + xls(19, 11) + "', '" + xls(22, 11) + "', '" + xls(25, 11) + "', '")
  f.write(            xls(28, 11) + "', '" + xls(31, 11) + "',\n")
  f.write("       '" + xls(34, 11) + "', '" + xls(37, 11) + "', '" + xls(40, 11) + "'],\n")
  f.write("      ['growth', self.ac.soln_pds_adoption_prognostication_growth, '" + xls(16, 12) + "',\n")
  f.write("       '" + xls(19, 12) + "', '" + xls(22, 12) + "', '" + xls(25, 12) + "', '" + xls(28, 12) + "', '" + xls(31, 12) + "',\n")
  f.write("       '" + xls(34, 12) + "', '" + xls(37, 12) + "', '" + xls(40, 12) + "'],\n")
  f.write("      ['low_sd_mult', " + xln(24, 1) + ", " + xln(16, 16) + ", ")
  f.write(            xln(19, 16) + ", " + xln(22, 16) + ", " + xln(25, 16) + ", ")
  f.write(            xln(28, 16) + ", " + xln(31, 16) + ", " + xln(34, 16) + ", ")
  f.write(            xln(37, 16) + ", " + xln(40, 16) + "],\n")
  f.write("      ['high_sd_mult', " + xln(23, 1) + ", " + xln(15, 16) + ", ")
  f.write(            xln(18, 16) + ", " + xln(21, 16) + ", " + xln(24, 16) + ", ")
  f.write(            xln(27, 16) + ", " + xln(30, 16) + ", " + xln(33, 16) + ", ")
  f.write(            xln(36, 16) + ", " + xln(39, 16) + "]]\n")
  f.write("    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')\n")
  f.write("    ad_data_sources = {\n")
  sources = {}
  sources['Baseline Cases'] = [xls(44, 2), xls(44, 3), xls(44, 4), xls(44, 5)]
  sources['Conservative Cases'] = [xls(44, 6), xls(44, 7), xls(44, 8), xls(44, 9), xls(44, 10)]
  sources['Ambitious Cases'] = [xls(44, 11), xls(44, 12), xls(44, 13), xls(44, 14), xls(44, 15), xls(44, 16)]
  sources['100% Case'] = [xls(44, 17)]
  for case in ['Baseline Cases', 'Conservative Cases', 'Ambitious Cases', '100% Case']:
    f.write("      '" + case + "': {\n")
    for source in sources[case]:
      source = re.sub('\s+', ' ', source).strip()  # remove extra/double spaces
      f.write("        '" + source + "': str(thisdir.joinpath('" + lookup_ad_source_filename(source) + "')),\n")
    f.write("      },\n")
  f.write("    }\n")
  f.write("    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources, adconfig=adconfig)\n")
  f.write("\n")


def write_ht(f, wb):
  """Generate the Helper Tables section of a solution.
     Arguments:
       f - file-like object for output
       wb - an Excel workbook as returned by xlrd
  """
  ht_tab = wb.sheet_by_name('Helper Tables')
  # concise routines to return strings, floats, and integers extracted from Excel.
  def xls(row, col): return "'" + str(ht_tab.cell_value(row, col)) + "'"
  def xln(row, col): return str(ht_tab.cell_value(row, col))
  def xli(row, col): return str(int(ht_tab.cell_value(row, col)))
  f.write("    ht_ref_datapoints = pd.DataFrame([\n")
  r = [xln(20, n) for n in range(2, 6)]
  f.write("      [" + xli(20, 1) + ", " + ", ".join(r) + ",\n")
  r = [xln(20, n) for n in range(6, 10)]
  f.write("       " + ", ".join(r) + ",\n")
  r = [xln(20, n) for n in range(10, 12)]
  f.write("       " + ", ".join(r) + "],\n")
  r = [xln(21, n) for n in range(2, 6)]
  f.write("      [" + xli(21, 1) + ", " + ", ".join(r) + ",\n")
  r = [xln(21, n) for n in range(6, 10)]
  f.write("       " + ", ".join(r) + ",\n")
  r = [xln(21, n) for n in range(10, 12)]
  f.write("       " + ", ".join(r) + "]],\n")
  f.write("      columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
  f.write("          'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA']).set_index('Year')\n")
  f.write("    ht_pds_datapoints = pd.DataFrame([\n")
  r = [xln(84, n) for n in range(2, 6)]
  f.write("      [" + xli(84, 1) + ", " + ", ".join(r) + ",\n")
  r = [xln(84, n) for n in range(6, 10)]
  f.write("       " + ", ".join(r) + ",\n")
  r = [xln(84, n) for n in range(10, 12)]
  f.write("       " + ", ".join(r) + "],\n")
  r = [xln(85, n) for n in range(2, 6)]
  f.write("      [" + xli(85, 1) + ", " + ", ".join(r) + ",\n")
  r = [xln(85, n) for n in range(6, 10)]
  f.write("       " + ", ".join(r) + ",\n")
  r = [xln(85, n) for n in range(10, 12)]
  f.write("       " + ", ".join(r) + "]],\n")
  f.write("      columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
  f.write("          'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA']).set_index('Year')\n")
  f.write("    self.ht = helpertables.HelperTables(ac=self.ac,\n")
  f.write("        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,\n")
  f.write("        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,\n")
  f.write("        adoption_data_per_region=self.ad.adoption_data_per_region(),\n")
  f.write("        adoption_is_single_source=self.ad.adoption_is_single_source())\n")
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
  # concise routine to return integers extracted from Excel.
  def xli(row, col): return str(int(fc_tab.cell_value(row, col)))
  f.write("    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=" + xli(24, 2) + ",\n")
  f.write("        ref_learning_increase_mult=" + xli(24, 3) + ", conv_learning_increase_mult=" + xli(24, 4) + ",\n")
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
  # concise routine to return integers extracted from Excel.
  def xli(row, col): return str(int(oc_tab.cell_value(row, col)))
  f.write("    self.oc = operatingcost.OperatingCost(ac=self.ac,\n")
  f.write("        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,\n")
  f.write("        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,\n")
  f.write("        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,\n")
  f.write("        conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),\n")
  f.write("        soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),\n")
  f.write("        soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),\n")
  f.write("        conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),\n")
  f.write("        single_iunit_purchase_year=" + xli(120, 8) + ",\n")
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


def extract_adoption_data(wb, outputdir):
  """Create CSV files for Adoption Data.
     Arguments:
       wb: Excel workbook
       outputdir: name of directory to write CSV files to.
  """
  world = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=45, nrows=49)
  world.name = 'World'
  oecd90 = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=105, nrows=49)
  oecd90.name = 'OECD90'
  eastern_europe = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=169, nrows=49)
  eastern_europe.name ='Eastern Europe'
  asia_sans_japan = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=232, nrows=49)
  asia_sans_japan.name = 'Asia (Sans Japan)'
  middle_east_and_africa = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=295, nrows=49)
  middle_east_and_africa.name = 'Middle East and Africa'
  latin_america = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=358, nrows=49)
  latin_america.name = 'Latin America'
  china = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=421, nrows=49)
  china.name = 'China'
  india = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=485, nrows=49)
  india.name = 'India'
  eu = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=549, nrows=49)
  eu.name = 'EU'
  usa = pd.read_excel(wb, engine='xlrd', sheet_name='Adoption Data', header=None, index_col=0, usecols="B:R", skiprows=614, nrows=49)
  usa.name = 'USA'

  ad_tab = wb.sheet_by_name('Adoption Data')
  for col in range(0, 16):
    source_name = str(ad_tab.cell_value(44, col + 2)).strip()
    filename = lookup_ad_source_filename(source_name)
    outputfile = os.path.join(outputdir, filename)
    df = pd.concat({'World': world.iloc[:, col], 'OECD90': oecd90.iloc[:, col],
      'Eastern Europe': eastern_europe.iloc[:, col],
      'Asia (Sans Japan)': asia_sans_japan.iloc[:, col],
      'Middle East and Africa': middle_east_and_africa.iloc[:, col],
      'Latin America': latin_america.iloc[:, col],
      'China': china.iloc[:, col], 'India': india.iloc[:, col],
      'EU': eu.iloc[:, col], 'USA':  usa.iloc[:, col]}, axis=1)
    df.index = df.index.astype(int)
    df.index.name = 'Year'
    df[['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',
      'Latin America', 'China', 'India', 'EU', 'USA']].to_csv(outputfile, header=True)


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
  if is_rrs:
    write_ad(f=f, wb=wb)
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

  extract_adoption_data(wb=wb, outputdir=outputdir)
  f.close()


def infer_classname(filename):
  """Pick a reasonable classname if none is specified."""
  special_cases = [
      ('BiomassELC', 'Biomass'),
      ('CHP_A_', 'CoGenElectricity'),
      ('CHP_B_', 'CoGenHeat'),
      ('CSP_', 'ConcentratedSolar'),
      ('Regenerative_Agriculture', 'RegenerativeAgriculture'),
      ('solution_xls_extract_RRS_test_A', 'TestClassA'),
      ('Utility Scale Solar PV', 'SolarPVUtil'),
      ('SolarPVUtility', 'SolarPVUtil'),
      ('SolarPVRooftop', 'SolarPVRoof'),
      ('Rooftop Solar PV', 'SolarPVRoof'),
      ('Tropical_Forest_Restoration', 'TropicalForests'),
      ('WastetoEnergy', 'WasteToEnergy'),
      ('Wave&Tidal', 'WaveAndTidal'),
      ('Wave and Tidal', 'WaveAndTidal'),
      ]
  for (pattern, classname) in special_cases:
    if pattern.replace(' ', '').lower() in filename.replace(' ', '').lower():
      return classname
  namelist = re.split('[_-]', filename)
  if namelist[0] == 'Drawdown':
    namelist.pop()
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
