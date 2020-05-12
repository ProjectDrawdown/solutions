#!/usr/bin/env python
"""Extract parameters from a Drawdown excel model to help create
   the Python implementation of the solution and its scenarios.

   The code in this file is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE
   version 3.0.

   Outputs of this utility are considered to be data and do not automatically
   carry the license used for the code in this utility. It is up to the user and
   copyright holder of the inputs to determine what copyright applies to the
   output.
"""

import argparse
import glob
import hashlib
import json
import os.path
import pathlib
import re
import sys
import textwrap
import unicodedata
import warnings

import xlrd
import numpy as np
import pandas as pd
import pytest
from solution import rrs

from tools.util import convert_bool, cell_to_offsets
from tools.vma_xls_extract import VMAReader
from model import advanced_controls as ac


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



def convert_sr_float(val):
    """Return floating point value from Excel ScenarioRecord tab.

       There are three main formats:
       + simple: 0.182810601365724
       + percentage: 20%
       + annotated: Val:(0.182810601365724) Formula:='Variable Meta-analysis'!G1411
    """
    m = re.match(r'Val:\(([-+]?(\d+(\.\d*)?|\d+(\,\d*)?|\.\d+)([eE][-+]?\d+)?)\) Formula:=',
                 str(val))
    if m:
        s = str(m.group(1)).replace(',', '.')
        return float(s)
    if str(val).startswith('Val:() Formula:='):
        return float(0.0)
    if str(val).endswith('%'):
        (num, _) = str(val).split('%', maxsplit=1)
        return float(num) / 100.0
    if val == '':
        return 0.0
    return float(val)




def get_rrs_scenarios(wb, solution_category):
    """Extract scenarios from an RRS Excel file.
       Arguments:
         wb: Excel workbook as returned by xlrd.
         solution_category: to populate in the scenario
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

            s['name'] = scenario_name
            s['solution_category'] = solution_category
            s['vmas'] = 'VMAs'

            s['description'] = sr_tab.cell_value(row + 1, 4)
            report_years = sr_tab.cell_value(row + 2, 4)  # E:2 from top of scenario
            (start, end) = report_years.split('-')
            s['report_start_year'] = int(start)
            s['report_end_year'] = int(end)

            assert sr_tab.cell_value(row + 46, 1) == 'Conventional'
            assert sr_tab.cell_value(row + 47, 3) == 'First Cost:'
            s['conv_2014_cost'] = link_vma(sr_tab, row + 47, 4)
            s['conv_first_cost_efficiency_rate'] = convert_sr_float(sr_tab.cell_value(row + 48, 4))
            s['conv_lifetime_capacity'] = link_vma(sr_tab, row + 49, 4)
            s['conv_avg_annual_use'] = link_vma(sr_tab, row + 50, 4)
            s['conv_var_oper_cost_per_funit'] = link_vma(sr_tab, row + 51, 4)
            s['conv_fixed_oper_cost_per_iunit'] = link_vma(sr_tab, row + 52, 4)
            s['conv_fuel_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 54, 4))

            assert sr_tab.cell_value(row + 64, 1) == 'Solution'
            assert sr_tab.cell_value(row + 65, 3) == 'First Cost:'
            s['pds_2014_cost'] = s['ref_2014_cost'] = link_vma(sr_tab, row + 65, 4)
            s['soln_first_cost_efficiency_rate'] = convert_sr_float(sr_tab.cell_value(row + 66, 4))
            s['soln_first_cost_below_conv'] = convert_bool(sr_tab.cell_value(row + 66, 6))
            s['soln_lifetime_capacity'] = link_vma(sr_tab, row + 67, 4)
            s['soln_avg_annual_use'] = link_vma(sr_tab, row + 68, 4)
            s['soln_var_oper_cost_per_funit'] = link_vma(sr_tab, row + 69, 4)
            s['soln_fixed_oper_cost_per_iunit'] = link_vma(sr_tab, row + 70, 4)
            s['soln_fuel_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 72, 4))

            assert sr_tab.cell_value(row + 76, 1) == 'General'
            s['npv_discount_rate'] = convert_sr_float(sr_tab.cell_value(row + 77, 4))

            assert sr_tab.cell_value(row + 86, 1) == 'EMISSIONS INPUTS'

            assert sr_tab.cell_value(row + 88, 1) == 'Grid Emissions'
            s['conv_annual_energy_used'] = link_vma(sr_tab, row + 89, 4)
            s['soln_energy_efficiency_factor'] = link_vma(sr_tab, row + 90, 4)
            s['soln_annual_energy_used'] = link_vma(sr_tab, row + 91, 4)

            assert sr_tab.cell_value(row + 94, 1) == 'Fuel Emissions'
            s['conv_fuel_consumed_per_funit'] = link_vma(sr_tab, row + 95, 4)
            s['soln_fuel_efficiency_factor'] = link_vma(sr_tab, row + 96, 4)
            s['conv_fuel_emissions_factor'] = link_vma(sr_tab, row + 97, 4)
            s['soln_fuel_emissions_factor'] = link_vma(sr_tab, row + 98, 4)

            assert sr_tab.cell_value(row + 103, 1) == 'Direct Emissions'
            s['conv_emissions_per_funit'] = link_vma(sr_tab, row + 105, 4)
            s['soln_emissions_per_funit'] = link_vma(sr_tab, row + 106, 4)

            assert sr_tab.cell_value(row + 111, 1) == 'Indirect Emissions'
            s['conv_indirect_co2_per_unit'] = link_vma(sr_tab, row + 112, 4)
            s['soln_indirect_co2_per_iunit'] = link_vma(sr_tab, row + 113, 4)
            i_vs_f = str(sr_tab.cell_value(row + 114, 4)).lower().strip()
            s['conv_indirect_co2_is_iunits'] = False if i_vs_f == 'functional' else True

            assert sr_tab.cell_value(row + 118, 1) == 'Optional Inputs'
            s['ch4_co2_per_funit'] = link_vma(sr_tab, row + 119, 4)
            s['ch4_is_co2eq'] = (sr_tab.cell_value(row + 119, 5) == 't CH4-CO2eq per TWh')
            s['n2o_co2_per_funit'] = link_vma(sr_tab, row + 120, 4)
            s['n2o_is_co2eq'] = (sr_tab.cell_value(row + 120, 5) == 't N2O-CO2eq per TWh')
            s['co2eq_conversion_source'] = str(sr_tab.cell_value(row + 121, 4)).strip()

            assert sr_tab.cell_value(row + 124, 1) == 'General Climate Inputs'
            s['emissions_use_co2eq'] = convert_bool(sr_tab.cell_value(row + 125, 4))
            s['emissions_grid_source'] = str(sr_tab.cell_value(row + 126, 4)).strip()
            s['emissions_grid_range'] = str(sr_tab.cell_value(row + 127, 4)).strip()

            assert sr_tab.cell_value(row + 135, 1) == 'TAM'
            s['source_until_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 4)))
            s['ref_source_post_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 7)))
            s['pds_source_post_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 10)))

            s['ref_base_adoption'] = {
                'World': convert_sr_float(sr_tab.cell_value(row + 151, 4)),
                'OECD90': convert_sr_float(sr_tab.cell_value(row + 152, 4)),
                'Eastern Europe': convert_sr_float(sr_tab.cell_value(row + 153, 4)),
                'Asia (Sans Japan)': convert_sr_float(sr_tab.cell_value(row + 154, 4)),
                'Middle East and Africa': convert_sr_float(sr_tab.cell_value(row + 155, 4)),
                'Latin America': convert_sr_float(sr_tab.cell_value(row + 156, 4)),
                'China': convert_sr_float(sr_tab.cell_value(row + 157, 4)),
                'India': convert_sr_float(sr_tab.cell_value(row + 158, 4)),
                'EU': convert_sr_float(sr_tab.cell_value(row + 159, 4)),
                'USA': convert_sr_float(sr_tab.cell_value(row + 160, 4)),
            }

            assert sr_tab.cell_value(row + 163, 1) == 'PDS ADOPTION SCENARIO INPUTS'
            s['soln_pds_adoption_basis'] = str(sr_tab.cell_value(row + 164, 4)).strip()
            s['soln_pds_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 165, 4))

            def percnt(r):
                return 0.0 if sr_tab.cell_value(r, 4) == '' else sr_tab.cell_value(r, 4)

            s['pds_adoption_final_percentage'] = {
                'World': percnt(row + 170),
                'OECD90': percnt(row + 171),
                'Eastern Europe': percnt(row + 172),
                'Asia (Sans Japan)': percnt(row + 173),
                'Middle East and Africa': percnt(row + 174),
                'Latin America': percnt(row + 175),
                'China': percnt(row + 176),
                'India': percnt(row + 177),
                'EU': percnt(row + 178),
                'USA': percnt(row + 179),
            }

            if s['soln_pds_adoption_basis'] == 'DEFAULT S-Curve':
                s_curve_type = str(sr_tab.cell_value(row + 181, 4))
                if s_curve_type == 'Alternate S-Curve (Bass Model)':
                    s['soln_pds_adoption_basis'] = 'Bass Diffusion S-Curve'
                    s['pds_adoption_s_curve_innovation'] = [
                        ('World', convert_sr_float(sr_tab.cell_value(row + 170, 6))),
                        ('OECD90', convert_sr_float(sr_tab.cell_value(row + 171, 6))),
                        ('Eastern Europe', convert_sr_float(sr_tab.cell_value(row + 172, 6))),
                        ('Asia (Sans Japan)', convert_sr_float(sr_tab.cell_value(row + 173, 6))),
                        ('Middle East and Africa', convert_sr_float(sr_tab.cell_value(row + 174, 6))),

                        ('Latin America', convert_sr_float(sr_tab.cell_value(row + 175, 6))),
                        ('China', convert_sr_float(sr_tab.cell_value(row + 176, 6))),
                        ('India', convert_sr_float(sr_tab.cell_value(row + 177, 6))),
                        ('EU', convert_sr_float(sr_tab.cell_value(row + 178, 6))),
                        ('USA', convert_sr_float(sr_tab.cell_value(row + 179, 6)))]
                    s['pds_adoption_s_curve_imitation'] = [
                        ('World', convert_sr_float(sr_tab.cell_value(row + 170, 7))),
                        ('OECD90', convert_sr_float(sr_tab.cell_value(row + 171, 7))),
                        ('Eastern Europe', convert_sr_float(sr_tab.cell_value(row + 172, 7))),
                        ('Asia (Sans Japan)', convert_sr_float(sr_tab.cell_value(row + 173, 7))),
                        ('Middle East and Africa', convert_sr_float(sr_tab.cell_value(row + 174, 7))),

                        ('Latin America', convert_sr_float(sr_tab.cell_value(row + 175, 7))),
                        ('China', convert_sr_float(sr_tab.cell_value(row + 176, 7))),
                        ('India', convert_sr_float(sr_tab.cell_value(row + 177, 7))),
                        ('EU', convert_sr_float(sr_tab.cell_value(row + 178, 7))),
                        ('USA', convert_sr_float(sr_tab.cell_value(row + 179, 7)))]
                elif s_curve_type == 'Default S-Curve (Logistic Model)':
                    s['soln_pds_adoption_basis'] = 'Logistic S-Curve'
                else:
                    raise ValueError('Unknown S-Curve:' + s_curve_type)

            assert sr_tab.cell_value(row + 183, 1) == 'Existing PDS Prognostication Assumptions'
            adopt = normalize_source_name(str(sr_tab.cell_value(row + 184, 4)).strip())
            adopt = normalize_case_name(adopt)
            if adopt: s['soln_pds_adoption_prognostication_source'] = adopt
            adopt = str(sr_tab.cell_value(row + 185, 4)).strip()
            if adopt: s['soln_pds_adoption_prognostication_trend'] = adopt
            adopt = str(sr_tab.cell_value(row + 186, 4)).strip()
            if adopt: s['soln_pds_adoption_prognostication_growth'] = adopt

            assert sr_tab.cell_value(row + 194, 1) == 'Fully Customized PDS'
            custom = str(sr_tab.cell_value(row + 195, 4)).strip()
            if custom:
                s['soln_pds_adoption_custom_name'] = custom
                if 'soln_pds_adoption_basis' not in s:  # sometimes row 164 is blank
                    s['soln_pds_adoption_basis'] = 'Fully Customized PDS'

            assert sr_tab.cell_value(row + 198, 1) == 'REF ADOPTION SCENARIO INPUTS'
            adopt = str(sr_tab.cell_value(row + 199, 4)).strip()
            if adopt: s['soln_ref_adoption_basis'] = adopt
            custom = str(sr_tab.cell_value(row + 200, 4)).strip()
            if custom: s['soln_ref_adoption_custom_name'] = custom
            s['soln_ref_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 201, 4))

            assert sr_tab.cell_value(row + 217, 1) == 'Adoption Adjustment'
            adjust = sr_tab.cell_value(row + 218, 4)
            if adjust and adjust != "(none)":
                s['pds_adoption_use_ref_years'] = [int(x) for x in adjust.split(',') if x != '']
            adjust = sr_tab.cell_value(row + 219, 4)
            if adjust and adjust != "(none)":
                s['ref_adoption_use_pds_years'] = [int(x) for x in adjust.split(',') if x != '']

            row += 202
            scenarios[scenario_name] = s
    return scenarios




def get_land_scenarios(wb, solution_category):
    """Extract scenarios from a LAND Excel file.
       Arguments:
         wb: Excel workbook returned by xlrd.
         solution_category: to populate in the scenario
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

            s['name'] = scenario_name
            s['solution_category'] = solution_category
            s['vmas'] = 'VMAs'

            s['description'] = sr_tab.cell_value(row + 1, 4)
            report_years = sr_tab.cell_value(row + 2, 4)  # E:2 from top of scenario
            (start, end) = report_years.split('-')
            s['report_start_year'] = int(start)
            s['report_end_year'] = int(end)

            assert sr_tab.cell_value(row + 201, 3) == 'Custom TLA Used?:'
            s['use_custom_tla'] = convert_bool(sr_tab.cell_value(row + 201, 4))
            values = (sr_tab.cell_value(row + 203, 4) and sr_tab.cell_value(row + 203, 7) and
                    sr_tab.cell_value(row + 203, 10))
            if s['use_custom_tla'] and values:
                world_tla = convert_sr_float(sr_tab.cell_value(row + 203, 4))
                future_ref = convert_sr_float(sr_tab.cell_value(row + 203, 7))
                future_pds = convert_sr_float(sr_tab.cell_value(row + 203, 10))
                # we can only handle if all three are the same
                err = f"mismatched Custom TLA values at row {row + 203}"
                assert world_tla == pytest.approx(future_ref), err
                assert world_tla == pytest.approx(future_pds), err
                s['custom_tla_fixed_value'] = world_tla

            s['ref_base_adoption'] = {
                'World': convert_sr_float(sr_tab.cell_value(row + 218, 4)),
                'OECD90': convert_sr_float(sr_tab.cell_value(row + 219, 4)),
                'Eastern Europe': convert_sr_float(sr_tab.cell_value(row + 220, 4)),
                'Asia (Sans Japan)': convert_sr_float(sr_tab.cell_value(row + 221, 4)),
                'Middle East and Africa': convert_sr_float(sr_tab.cell_value(row + 222, 4)),
                'Latin America': convert_sr_float(sr_tab.cell_value(row + 223, 4)),
                'China': convert_sr_float(sr_tab.cell_value(row + 224, 4)),
                'India': convert_sr_float(sr_tab.cell_value(row + 225, 4)),
                'EU': convert_sr_float(sr_tab.cell_value(row + 226, 4)),
                'USA': convert_sr_float(sr_tab.cell_value(row + 227, 4)),
            }

            assert sr_tab.cell_value(row + 230, 1) == 'PDS ADOPTION SCENARIO INPUTS'
            adopt = str(sr_tab.cell_value(row + 231, 4)).strip()
            if adopt: s['soln_pds_adoption_basis'] = adopt
            s['soln_pds_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 232, 4))

            def percnt(r):
                return 0.0 if sr_tab.cell_value(r, 4) == '' else sr_tab.cell_value(r, 4)

            s['pds_adoption_final_percentage'] = {
                'World': percnt(row + 236),
                'OECD90': percnt(row + 237),
                'Eastern Europe': percnt(row + 238),
                'Asia (Sans Japan)': percnt(row + 239),
                'Middle East and Africa': percnt(row + 240),
                'Latin America': percnt(row + 241),
                'China': percnt(row + 242),
                'India': percnt(row + 243),
                'EU': percnt(row + 244),
                'USA': percnt(row + 245),
            }

            assert sr_tab.cell_value(row + 258, 1) == 'Fully Customized PDS'
            custom = str(sr_tab.cell_value(row + 259, 4)).strip()
            if custom:
                s['soln_pds_adoption_custom_name'] = custom
                if 'soln_pds_adoption_basis' not in s:  # sometimes row 164 is blank
                    s['soln_pds_adoption_basis'] = 'Fully Customized PDS'
                high, low = str(sr_tab.cell_value(row + 260, 7)).split(',')
                if high != "1" and high != "":
                    s['soln_pds_adoption_custom_high_sd_mult'] = float(high)
                if low != "1" and low != "":
                    s['soln_pds_adoption_custom_low_sd_mult'] = float(low)

            assert sr_tab.cell_value(row + 262, 1) == 'REF ADOPTION SCENARIO INPUTS'
            adopt = str(sr_tab.cell_value(row + 263, 4)).strip()
            if adopt: s['soln_ref_adoption_basis'] = adopt
            custom = str(sr_tab.cell_value(row + 264, 4)).strip()
            if custom: s['soln_ref_adoption_custom_name'] = custom
            s['soln_ref_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 265, 4))

            assert sr_tab.cell_value(row + 286, 1) == 'Adoption Adjustment'
            adjust = sr_tab.cell_value(row + 287, 4)
            if adjust and adjust != "(none)":
                s['pds_adoption_use_ref_years'] = [int(x) for x in adjust.split(',') if x != '']
            adjust = sr_tab.cell_value(row + 288, 4)
            if adjust and adjust != "(none)":
                s['ref_adoption_use_pds_years'] = [int(x) for x in adjust.split(',') if x != '']
            # TODO: handle soln_pds_adoption_prognostication_source

            assert sr_tab.cell_value(row + 54, 1) == 'Conventional'
            assert sr_tab.cell_value(row + 55, 3) == 'First Cost:'
            s['conv_2014_cost'] = link_vma(sr_tab, row + 55, 4)
            s['conv_first_cost_efficiency_rate'] = 0.0  # always 0 for LAND models
            s['conv_fixed_oper_cost_per_iunit'] = link_vma(sr_tab, row + 56, 4)
            s['conv_expected_lifetime'] = convert_sr_float(sr_tab.cell_value(row + 59, 4))
            s['yield_from_conv_practice'] = link_vma(sr_tab, row + 60, 4)

            assert sr_tab.cell_value(row + 72, 1) == 'Solution'
            assert sr_tab.cell_value(row + 73, 3) == 'First Cost:'
            s['pds_2014_cost'] = s['ref_2014_cost'] = link_vma(sr_tab, row + 73, 4)
            s['soln_first_cost_efficiency_rate'] = 0.0  # always 0 for LAND models
            s['soln_fixed_oper_cost_per_iunit'] = link_vma(sr_tab, row + 74, 4)
            s['soln_expected_lifetime'] = convert_sr_float(sr_tab.cell_value(row + 77, 4))
            s['yield_gain_from_conv_to_soln'] = link_vma(sr_tab, row + 78, 4)

            assert sr_tab.cell_value(row + 90, 1) == 'General'
            s['npv_discount_rate'] = convert_sr_float(sr_tab.cell_value(row + 91, 4))

            assert sr_tab.cell_value(row + 156, 1) == 'General Emissions Inputs'
            s['emissions_use_co2eq'] = convert_bool(sr_tab.cell_value(row + 157, 4))
            s['emissions_use_agg_co2eq'] = convert_bool(sr_tab.cell_value(row + 158, 4))
            s['emissions_grid_source'] = str(sr_tab.cell_value(row + 159, 4))
            s['emissions_grid_range'] = str(sr_tab.cell_value(row + 160, 4))

            assert sr_tab.cell_value(row + 144, 1) == 'Indirect Emissions'
            s['conv_indirect_co2_per_unit'] = convert_sr_float(sr_tab.cell_value(row + 145, 4))
            s['soln_indirect_co2_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 146, 4))

            assert sr_tab.cell_value(row + 132, 1) == 'Direct Emissions'
            s['tco2eq_reduced_per_land_unit'] = link_vma(sr_tab, row + 133, 4)
            s['tco2eq_rplu_rate'] = str(sr_tab.cell_value(row + 133, 7))
            s['tco2_reduced_per_land_unit'] = link_vma(sr_tab, row + 134, 4)
            s['tco2_rplu_rate'] = str(sr_tab.cell_value(row + 134, 7))
            s['tn2o_co2_reduced_per_land_unit'] = link_vma(sr_tab, row + 135, 4)
            s['tn2o_co2_rplu_rate'] = str(sr_tab.cell_value(row + 135, 7))
            s['tch4_co2_reduced_per_land_unit'] = link_vma(sr_tab, row + 136, 4)
            s['tch4_co2_rplu_rate'] = str(sr_tab.cell_value(row + 136, 7))
            s['land_annual_emissons_lifetime'] = convert_sr_float(sr_tab.cell_value(row + 137, 4))

            assert sr_tab.cell_value(row + 109, 1) == 'Grid Emissions'
            s['conv_annual_energy_used'] = convert_sr_float(sr_tab.cell_value(row + 110, 4))
            s['soln_annual_energy_used'] = convert_sr_float(sr_tab.cell_value(row + 112, 4))

            assert sr_tab.cell_value(row + 168, 1) == 'Carbon Sequestration and Land Inputs'
            if sr_tab.cell(row + 169, 4).ctype == xlrd.XL_CELL_EMPTY:
                # Excel checks whether this cell == "" to trigger different handling. The best equivalent
                # in Python is to set it to NaN. We can distinguish None (not set) from NaN, and if
                # the value is ever inadvertantly used it will result in NaN.
                s['seq_rate_global'] = np.nan

                if 'Variable Meta-analysis-DD' not in wb.sheet_names():
                    assert NotImplementedError(
                        'VMA Thermal-Moisture Regime sequestration not implemented')
                    # (4/2019) vma.py does have support for regimes in avg_high_low, it needs to be
                    # implemented in advanced_controls to pass a regime name through to vma.py

                tmr6 = tmr8 = False
                aez_tab = wb.sheet_by_name('AEZ Data')
                for x in range(0, aez_tab.nrows):
                    if aez_tab.cell_value(x, 0) == 'TOTAL Boreal-Humid land':
                        tmr8 = True
                        break
                    if aez_tab.cell_value(x, 0) == 'TOTAL Temperate/Boreal-Humid land':
                        tmr6 = True
                        break

                # For the public models using 'Variable Meta-analysis-DD', the DD tab does not contain
                # avg/high/low for the Thermal Moisture Regimes so we extract value from ScenarioRecord.
                if tmr6:
                    s['seq_rate_per_regime'] = {
                        'Tropical-Humid': convert_sr_float(sr_tab.cell_value(row + 170, 4)),
                        'Temperate/Boreal-Humid': convert_sr_float(sr_tab.cell_value(row + 171, 4)),
                        'Tropical-Semi-Arid': convert_sr_float(sr_tab.cell_value(row + 172, 4)),
                        'Temperate/Boreal-Semi-Arid': convert_sr_float(sr_tab.cell_value(row + 173, 4)),
                        'Global Arid': convert_sr_float(sr_tab.cell_value(row + 174, 7)),
                        'Global Arctic': 0.0}
                if tmr8:
                    s['seq_rate_per_regime'] = {
                        'Tropical-Humid': convert_sr_float(sr_tab.cell_value(row + 170, 4)),
                        'Temperate-Humid': convert_sr_float(sr_tab.cell_value(row + 171, 4)),
                        'Boreal-Humid': convert_sr_float(sr_tab.cell_value(row + 171, 4)),
                        'Tropical-Semi-Arid': convert_sr_float(sr_tab.cell_value(row + 172, 4)),
                        'Temperate-Semi-Arid': convert_sr_float(sr_tab.cell_value(row + 173, 4)),
                        'Boreal-Semi-Arid': convert_sr_float(sr_tab.cell_value(row + 173, 4)),
                        'Global Arid': convert_sr_float(sr_tab.cell_value(row + 174, 7)),
                        'Global Arctic': 0.0}
            else:
                s['seq_rate_global'] = link_vma(sr_tab, row + 169, 4)
            if sr_tab.cell_value(row + 175, 3) == 'Growth Rate of Land Degradation':
                s['global_multi_for_regrowth'] = convert_sr_float(sr_tab.cell_value(row + 178, 4))
                s['degradation_rate'] = link_vma(sr_tab, row + 175, 4)
                s['tC_storage_in_protected_land_type'] = link_vma(sr_tab, row + 177, 4)
            elif sr_tab.cell_value(row + 175,
                                   3) == 'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing':
                s['carbon_not_emitted_after_harvesting'] = link_vma(sr_tab, row + 175, 4)

            s['disturbance_rate'] = link_vma(sr_tab, row + 176, 4)

            assert sr_tab.cell_value(row + 188, 1) == 'General Land Inputs'
            if sr_tab.cell_value(row + 189, 3) == 'Delay Impact of Protection by 1 Year? (Leakage)':
                s['delay_protection_1yr'] = convert_bool(sr_tab.cell_value(row + 189, 4))
                s['delay_regrowth_1yr'] = convert_bool(sr_tab.cell_value(row + 190, 4))
                s['include_unprotected_land_in_regrowth_calcs'] = convert_bool(
                    sr_tab.cell_value(row + 191, 4))
            elif sr_tab.cell_value(row + 189, 3) == 'New Growth is Harvested/Cleared Every':
                s['harvest_frequency'] = convert_sr_float(sr_tab.cell_value(row + 189, 4))

            for addl in range(271, 285):
                label = 'Avoided Deforested Area With Increase in Agricultural Intensification'
                if sr_tab.cell_value(row + addl, 3) == label:
                    s['avoided_deforest_with_intensification'] = convert_sr_float(
                            sr_tab.cell_value(row + addl, 4))
            scenarios[scenario_name] = s
    return scenarios



def json_dumps_default(obj):
    """Default function for json.dumps."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return [[obj.index.name, *obj.columns.tolist()]] + obj.reset_index().values.tolist()
    elif isinstance(obj, pd.Series):
        return [[obj.index.name, obj.name]] + obj.reset_index().values.tolist()
    elif isinstance(obj, ac.SOLUTION_CATEGORY):
        return ac.solution_category_to_string(obj)
    else:
        raise TypeError('Unable to JSON encode: ' + repr(obj))



def write_scenario(filename, s):
    """Write out the advanced_controls entries for a given scenario."""
    with filename.open(mode='w') as f:
        json.dump(obj=s, fp=f, indent=4, default=json_dumps_default)



def xls(tab, row, col):
    """Return a quoted string read from tab(row, col)."""
    cell = tab.cell(row, col)
    if cell.ctype == xlrd.XL_CELL_ERROR or cell.ctype == xlrd.XL_CELL_EMPTY:
        return ''
    if cell.ctype == xlrd.XL_CELL_TEXT or cell.ctype == xlrd.XL_CELL_NUMBER:
        return "'" + str(cell.value).strip() + "'"
    raise ValueError(
        "Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))



def xln(tab, row, col):
    """Return the string of a floating point number read from tab(row, col)."""
    cell = tab.cell(row, col)
    if cell.ctype == xlrd.XL_CELL_ERROR:
        return 'np.nan'
    if cell.ctype == xlrd.XL_CELL_NUMBER:
        return str(cell.value)
    if cell.ctype == xlrd.XL_CELL_EMPTY:
        return '0.0'
    if cell.ctype == xlrd.XL_CELL_TEXT and cell.value == '':
        return '0.0'
    raise ValueError(
        "Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))



def xli(tab, row, col):
    """Return the string of an integer value read from tab(row, col)."""
    cell = tab.cell(row, col)
    if cell.ctype == xlrd.XL_CELL_ERROR:
        return 'np.nan'
    if cell.ctype == xlrd.XL_CELL_TEXT or cell.ctype == xlrd.XL_CELL_NUMBER:
        return str(int(cell.value))
    if cell.ctype == xlrd.XL_CELL_EMPTY:
        return '0'
    raise ValueError(
        "Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))



def recursive_keys(sources):
    result = {}
    for k in sources.keys():
        try:
            value = recursive_keys(sources[k])
        except AttributeError:
            value = None
        result[k] = value
    return result



def abandon_files(sources, outputdir):
    """We're not going to use the extracted files after all, remove them."""
    for (key, filename) in sources.items():
        try:
            abandon_files(sources=sources[key], outputdir=outputdir)
        except AttributeError:
            try:
                fullpath = os.path.join(outputdir, filename)
                os.unlink(fullpath)
            except FileNotFoundError:
                pass




def write_tam(f, wb, outputdir):
    """Generate the TAM section of a solution.
       Arguments:
         f - file-like object for output
         wb - an Excel workbook as returned by xlrd
         outputdir: name of directory to write CSV files to.
    """
    tm_tab = wb.sheet_by_name('TAM Data')
    f.write("        tamconfig_list = [\n")
    f.write("            ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
    f.write("                'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")
    f.write("            ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,\n")
    f.write("                " + xls(tm_tab, 15, 21) + ", " + xls(tm_tab, 18, 21) + ", " + 
            xls(tm_tab, 21, 21) + ", ")
    f.write(xls(tm_tab, 24, 21) + ", " + xls(tm_tab, 27, 21) + ", " + xls(tm_tab, 30, 21) + ",\n")
    f.write("                " + xls(tm_tab, 33, 21) + ", " + xls(tm_tab, 36, 21) + ", " +
            xls(tm_tab, 39, 21) + "],\n")
    f.write("            ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,\n")
    f.write("                " + xls(tm_tab, 15, 21) + ", " + xls(tm_tab, 18, 21) + ", " +
            xls(tm_tab, 21, 21) + ", ")
    f.write(xls(tm_tab, 24, 21) + ", " + xls(tm_tab, 27, 21) + ", " + xls(tm_tab, 30, 21) + ",\n")
    f.write("                " + xls(tm_tab, 33, 21) + ", " + xls(tm_tab, 36, 21) + ", " +
            xls(tm_tab, 39, 21) + "],\n")
    # One might assume PDS_World for trend and growth would use self.ac.soln_pds_adoption_prognostication_*,
    # but that is not what the TAM Data in Excel does. EA104 references B19 and C19, the World trend and growth.
    f.write("            ['trend', " + xls(tm_tab, 18, 1) + ", " + xls(tm_tab, 18, 1) + ",\n")
    f.write("                " + xls(tm_tab, 16, 11) + ", " + xls(tm_tab, 19, 11) + ", " +
            xls(tm_tab, 22, 11) + ", ")
    f.write(xls(tm_tab, 25, 11) + ", " + xls(tm_tab, 28, 11) + ", " + xls(tm_tab, 31, 11) + ",\n")
    f.write("                " + xls(tm_tab, 34, 11) + ", " + xls(tm_tab, 37, 11) + ", " +
            xls(tm_tab, 40, 11) + "],\n")
    f.write("            ['growth', " + xls(tm_tab, 18, 2) + ", " + xls(tm_tab, 18, 2) + ", " +
            xls(tm_tab, 16, 12) + ", ")
    f.write(xls(tm_tab, 19, 12) + ",\n")
    f.write("                " + xls(tm_tab, 22, 12) + ", " + xls(tm_tab, 25, 12) + ", " +
            xls(tm_tab, 28, 12) + ", ")
    f.write(xls(tm_tab, 31, 12) + ", " + xls(tm_tab, 34, 12) + ", " + xls(tm_tab, 37, 12) + ", ")
    f.write(xls(tm_tab, 40, 12) + "],\n")
    f.write("            ['low_sd_mult', " + xln(tm_tab, 24, 1) + ", " + xln(tm_tab, 24, 1) + ", ")
    f.write(xln(tm_tab, 16, 16) + ", " + xln(tm_tab, 19, 16) + ", " + xln(tm_tab, 22, 16) + ", ")
    f.write(xln(tm_tab, 25, 16) + ", " + xln(tm_tab, 28, 16) + ", " + xln(tm_tab, 31, 16) + ", ")
    f.write(xln(tm_tab, 34, 16) + ", " + xln(tm_tab, 37, 16) + ", " + xln(tm_tab, 40, 16) + "],\n")
    f.write("            ['high_sd_mult', " + xln(tm_tab, 23, 1) + ", " + xln(tm_tab, 23, 1) + ", ")
    f.write(xln(tm_tab, 15, 16) + ", " + xln(tm_tab, 18, 16) + ", " + xln(tm_tab, 21, 16) + ", ")
    f.write(xln(tm_tab, 24, 16) + ", " + xln(tm_tab, 27, 16) + ", " + xln(tm_tab, 30, 16) + ", ")
    f.write(xln(tm_tab, 33, 16) + ", " + xln(tm_tab, 36, 16) + ", " + xln(tm_tab, 39, 16) + "]]\n")
    f.write("        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0],\n")
    f.write("            dtype=np.object).set_index('param')\n")

    tam_regions = {'World': 44, 'OECD90': 162, 'Eastern Europe': 226,
                   'Asia (Sans Japan)': 289, 'Middle East and Africa': 352, 'Latin America': 415,
                   'China': 478, 'India': 542, 'EU': 606, 'USA': 671}
    tamoutputdir = os.path.join(outputdir, 'tam')
    os.makedirs(tamoutputdir, exist_ok=True)
    ref_sources = extract_source_data(wb=wb, sheet_name='TAM Data', regions=tam_regions,
                                      outputdir=tamoutputdir, prefix='tam_')
    if recursive_keys(ref_sources) == recursive_keys(rrs.energy_tam_1_ref_data_sources):
        arg_ref = 'rrs.energy_tam_1_ref_data_sources'
        abandon_files(ref_sources, outputdir=tamoutputdir)
    elif recursive_keys(ref_sources) == recursive_keys(rrs.energy_tam_2_ref_data_sources):
        arg_ref = 'rrs.energy_tam_2_ref_data_sources'
        abandon_files(ref_sources, outputdir=tamoutputdir)
    else:
        f.write("        tam_ref_data_sources = {\n")
        for region, cases in ref_sources.items():
            f.write("              '" + region + "': {\n")
            for (case, sources) in cases.items():
                if isinstance(sources, str):
                    f.write("                  '" + case + "': THISDIR.joinpath('tam', '" +
                            sources + "'),\n")
                else:
                    f.write("                  '" + case + "': {\n")
                    for (source, filename) in sources.items():
                        f.write("                  '" + source + "': THISDIR.joinpath('tam', '" +
                                filename + "'),\n")
                    f.write("              },\n")
            f.write("            },\n")
        f.write("        }\n")
        arg_ref = 'tam_ref_data_sources'

    tam_regions = {'World': 102}
    pds_sources = extract_source_data(wb=wb, sheet_name='TAM Data', regions=tam_regions,
                                      outputdir=tamoutputdir, prefix='tam_pds_')
    if recursive_keys(pds_sources) == recursive_keys(rrs.energy_tam_1_pds_data_sources):
        # the source names are the same for energy_tam_1 & 2, distinguish them here.
        plausible_2060 = float(tm_tab.cell_value(*cell_to_offsets('L152')))
        if plausible_2060 == pytest.approx(54539.190092617995):
            arg_pds = 'rrs.energy_tam_2_pds_data_sources'
        elif plausible_2060 == pytest.approx(60153.728317538):
            arg_pds = 'rrs.energy_tam_1_pds_data_sources'
        else:
            raise ValueError(f"Unknown Energy TAM, Plausible World 2060 = {plausible_2060}")
        abandon_files(pds_sources, outputdir=tamoutputdir)
    elif not pds_sources:
        arg_pds = 'tam_ref_data_sources'
    else:
        f.write("        tam_pds_data_sources = {\n")
        for region, cases in pds_sources.items():
            f.write("            '" + region + "': {\n")
            for (case, sources) in cases.items():
                if isinstance(sources, str):
                    f.write("                    '" + case + "': THISDIR.joinpath('tam', '" + 
                            sources + "'),\n")
                else:
                    f.write("                    '" + case + "': {\n")
                    for (source, filename) in sources.items():
                        f.write("                      '" + source + "': THISDIR.joinpath('tam', '"
                                + filename + "'),\n")
                    f.write("              },\n")
            f.write("            },\n")
        f.write("        }\n")
        arg_pds = 'tam_pds_data_sources'

    regional = convert_bool(tm_tab.cell(28, 1).value) and convert_bool(tm_tab.cell(29, 1).value)
    f.write("        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=" + arg_ref + ",\n")
    if regional:
        f.write("            main_includes_regional=True,\n")
    f.write("            tam_pds_data_sources=" + arg_pds + ")\n")
    f.write("        ref_tam_per_region=self.tm.ref_tam_per_region()\n")
    f.write("        pds_tam_per_region=self.tm.pds_tam_per_region()\n")
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
        'Based on: Greenpeace 2015 Reference Scenario': 'Based on: Greenpeace 2015 Reference',
        'Based on Greenpeace 2015 Reference': 'Based on: Greenpeace 2015 Reference',
        'Based on: Greenpeace Reference Scenario': 'Based on: Greenpeace 2015 Reference',
        'Conservative: Based on- Greenpeace 2015 Reference': 'Based on: Greenpeace 2015 Reference',
        '100% REN: Based on- Greenpeace Advanced [R]evolution': 'Based on: Greenpeace 2015 Advanced Revolution',
        'Drawdown TAM: Baseline Cases': 'Baseline Cases',
        'Drawdown TAM: Conservative Cases': 'Conservative Cases',
        'Drawdown TAM: Ambitious Cases': 'Ambitious Cases',
        'Drawdown TAM: Maximum Cases': 'Maximum Cases',
        'Drawdown Projections based on adjusted IEA data (ETP 2012) on projected growth in each year, and recent sales Data (IEA - ETP 2016)': 'Drawdown Projections based on adjusted IEA data (ETP 2012) on projected growth in each year, and recent sales Data (IEA - ETP 2016)',
        'ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - Baseline Scenario': 'ITDP/UC Davis 2014 Global High Shift Baseline',
        'ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - HighShift Scenario': 'ITDP/UC Davis 2014 Global High Shift HighShift',
        'What a Waste: A Global Review of Solid Waste Management (Hoornweg, 2012) - Static % of Organic Waste': 'What a Waste Solid Waste Management Static',
        'What a Waste: A Global Review of Solid Waste Management (Hoornweg, 2012) - Dynamic % of Organic Waste': 'What a Waste Solid Waste Management Dynamic',
        'What a Waste: A Global Review of Solid Waste Management (Hoornweg, 2012) - Dynamic Organic Fraction by Un Mediam Variant': 'What a Waste Solid Waste Management Dynamic Organic Fraction',
        'IPCC, 2006 - Calculated': 'IPCC, 2006 Calculated',
        "Combined from IEA (2016) ETP 2016, ICAO (2014) Annual Report 2014, Appendix 1, Boeing (2013) World Air cargo Forecast 2014-2015, Airbus (2014) Global market Forecast: Flying by the Numbers 2015-2034 - Highest Ranges": 'Combined from IEA ETP 2016, ICAO 2014, Boeing 2013, Airbus 2014, Highest Ranges',
        "Combined from IEA (2016) ETP 2016, ICAO (2014) Annual Report 2014, Appendix 1, Boeing (2013) World Air cargo Forecast 2014-2015, Airbus (2014) Global market Forecast: Flying by the Numbers 2015-2034 - Middle Ranges": 'Combined from IEA ETP 2016, ICAO 2014, Boeing 2013, Airbus 2014, Middle Ranges',
        "Combined from IEA (2016) ETP 2016, ICAO (2014) Annual Report 2014, Appendix 1, Boeing (2013) World Air cargo Forecast 2014-2015, Airbus (2014) Global market Forecast: Flying by the Numbers 2015-2034 - Lowest Ranges": 'Combined from IEA ETP 2016, ICAO 2014, Boeing 2013, Airbus 2014, Lowest Ranges',
        'Based on average of: LUT/EWG (2019) -100% RES; Ecofys (2018) - 1.5ºC and Greenpeace (2015) Advanced [R]evolution': 'Based on average of: LUT/EWG 2019 100% RES, Ecofys 2018 1.5C and Greenpeace 2015 Advanced Revolution',
        'FAO 2015 (Sum of all regions)': 'FAO 2015',  # Afforestation Drawdown 2020
        'FAO 2010 (Sum of all regions)': 'FAO 2010',  # Bamboo Drawdown 2020
    }
    normalized = sourcename.replace("'", "").replace('\n', ' ').strip()
    if normalized in special_cases:
        return special_cases[normalized]
    if re.search(r'\[Source \d+', sourcename):
        return None

    # handle duplicate column names where xlrd appends an integer.
    suffix = ''
    r = re.search(r'(\\.\d)$', sourcename)
    if r is not None:
        suffix = r.group()

    name = re.sub(r"[\[\]]", "", sourcename.upper())  # [R]evolution to REVOLUTION
    if 'UN CES' in name and 'ITU' in name and 'AMPERE' in name:
        if 'BASELINE' in name: return 'Based on: CES ITU AMPERE Baseline' + suffix
        if '550' in name: return 'Based on: CES ITU AMPERE 550' + suffix
        if '450' in name: return 'Based on: CES ITU AMPERE 450' + suffix
        raise ValueError('Unknown UN CES ITU AMPERE source: ' + sourcename)
    if 'IEA' in name and 'ETP' in name:
        if '2014' in name and '2DS' in name: return 'Based on: IEA ETP 2014 2DS' + suffix
        if '2014' in name and '4DS' in name: return 'Based on: IEA ETP 2014 4DS' + suffix
        if '2014' in name and '6DS' in name: return 'Based on: IEA ETP 2014 6DS' + suffix
        if '2016' in name and '6DS' in name: return 'Based on: IEA ETP 2016 6DS' + suffix
        if '2016' in name and '4DS' in name: return 'Based on: IEA ETP 2016 4DS' + suffix
        if '2016' in name and '2DS' in name and 'OPT2-PERENNIALS' in name:
            return 'Based on: IEA ETP 2016 2DS with OPT2 perennials' + suffix
        if '2016' in name and '2DS' in name: return 'Based on: IEA ETP 2016 2DS' + suffix
        if '2016' in name and 'ANNEX' in name: return 'Based on: IEA ETP 2016 Annex' + suffix
        if '2017' in name and 'REF' in name: return 'Based on: IEA ETP 2017 Ref Tech' + suffix
        if '2017' in name and 'B2DS' in name: return 'Based on: IEA ETP 2017 B2DS' + suffix
        if '2017' in name and 'BEYOND 2DS' in name: return 'Based on: IEA ETP 2017 B2DS' + suffix
        if '2017' in name and '2DS' in name: return 'Based on: IEA ETP 2017 2DS' + suffix
        if '2017' in name and '4DS' in name: return 'Based on: IEA ETP 2017 4DS' + suffix
        if '2017' in name and '6DS' in name: return 'Based on: IEA ETP 2017 6DS' + suffix
        raise ValueError('Unknown IEA ETP source: ' + sourcename)
    if 'AMPERE' in name and 'MESSAGE' in name:
        if '450' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO 450' + suffix
        if '550' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO 550' + suffix
        if 'REF' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO Reference' + suffix
        raise ValueError('Unknown AMPERE MESSAGE-MACRO source: ' + sourcename)
    if 'AMPERE' in name and 'IMAGE' in name:
        if '450' in name: return 'Based on: AMPERE 2014 IMAGE TIMER 450' + suffix
        if '550' in name: return 'Based on: AMPERE 2014 IMAGE TIMER 550' + suffix
        if 'REF' in name: return 'Based on: AMPERE 2014 IMAGE TIMER Reference' + suffix
        raise ValueError('Unknown AMPERE IMAGE-TIMER source: ' + sourcename)
    if 'AMPERE' in name and 'GEM' in name and 'E3' in name:
        if '450' in name: return 'Based on: AMPERE 2014 GEM E3 450' + suffix
        if '550' in name: return 'Based on: AMPERE 2014 GEM E3 550' + suffix
        if 'REF' in name: return 'Based on: AMPERE 2014 GEM E3 Reference' + suffix
        raise ValueError('Unknown AMPERE GEM E3 source: ' + sourcename)
    if 'GREENPEACE' in name and 'ENERGY' in name:
        if 'ADVANCED' in name and 'DRAWDOWN-PERENNIALS' in name:
            return 'Based on: Greenpeace 2015 Advanced Revolution with Drawdown perennials' + suffix
        if 'ADVANCED' in name: return 'Based on: Greenpeace 2015 Advanced Revolution' + suffix
        if 'REVOLUTION' in name and 'DRAWDOWN-PERENNIALS' in name:
            return 'Based on: Greenpeace 2015 Energy Revolution with Drawdown perennials' + suffix
        if 'REVOLUTION' in name: return 'Based on: Greenpeace 2015 Energy Revolution' + suffix
        if 'REFERENCE' in name: return 'Based on: Greenpeace 2015 Reference' + suffix
        raise ValueError('Unknown Greenpeace Energy source: ' + sourcename)
    if 'GREENPEACE' in name and 'THERMAL' in name:
        if 'MODERATE' in name: return 'Based on: Greenpeace 2016 Solar Thermal Moderate' + suffix
        if 'ADVANCED' in name: return 'Based on: Greenpeace 2016 Solar Thermal Advanced' + suffix
        raise ValueError('Unknown Greenpeace Solar Thermal source: ' + sourcename)
    return unicodedata.normalize('NFC', normalized)


def normalize_case_name(name):
    rewrites = {
        'Drawdown TAM: Baseline Cases': 'Baseline Cases',
        'Drawdown TAM: Conservative Cases': 'Conservative Cases',
        'Drawdown TAM: Ambitious Cases': 'Ambitious Cases',
        'Drawdown TAM: Maximum Cases': 'Maximum Cases',
        '100% Case': '100% RES2050 Case',
    }
    return rewrites.get(name, name)


def get_filename_for_source(sourcename, prefix=''):
    """Return string to use for the filename for known sources."""
    if re.search(r'\[Source \d+', sourcename):
        return None
    if re.search(r'Drawdown TAM: \[Source \d+', sourcename):
        return None

    filename = sourcename.strip()
    filename = re.sub(r"[^\w\s\.]", '', filename)
    filename = re.sub(r"\s+", '_', filename)
    filename = re.sub(r"\.+", '_', filename)
    filename = filename.replace('Based_on_', 'based_on_')
    if len(filename) > 96:
        h = hashlib.sha256(filename.encode('utf-8')).hexdigest()[-8:]
        filename = filename[:88] + '_' + h
    return prefix + filename + '.csv'


def write_aez(f, wb):
    a = wb.sheet_by_name('Land Allocation - Max TLA')
    first_solution = str(a.cell_value(*cell_to_offsets('B18')))
    if first_solution == 'Peatland Protection':
        f.write("        self.ae = aez.AEZ(solution_name=self.name, cohort=2020,\n")
        f.write("                regimes=dd.THERMAL_MOISTURE_REGIMES8)\n")
    elif first_solution == 'Forest Protection':
        f.write("        self.ae = aez.AEZ(solution_name=self.name, cohort=2018)\n")
    else:
        raise ValueError('cannot determine AEZ Land Allocation to use')


def write_ad(f, wb, outputdir):
    """Generate the Adoption Data section of a solution.
       Arguments:
         f - file-like object for output
         wb - an Excel workbook as returned by xlrd
         outputdir: name of directory to write CSV files to.
    """
    a = wb.sheet_by_name('Adoption Data')
    f.write("        adconfig_list = [\n")
    f.write("            ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")
    f.write("             'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")
    f.write("            ['trend', self.ac.soln_pds_adoption_prognostication_trend, ")
    f.write(xls(a, 16, 11) + ",\n")
    f.write("             " + xls(a, 19, 11) + ", " + xls(a, 22, 11) + ", ")
    f.write(xls(a, 25, 11) + ", " + xls(a, 28, 11) + ", ")
    f.write(xls(a, 31, 11) + ",\n")
    f.write("             " + xls(a, 34, 11) + ", " + xls(a, 37, 11) + ", ")
    f.write(xls(a, 40, 11) + "],\n")
    f.write("            ['growth', self.ac.soln_pds_adoption_prognostication_growth, ")
    f.write(xls(a, 16, 12) + ",\n")
    f.write("             " + xls(a, 19, 12) + ", " + xls(a, 22, 12) + ", " + xls(a, 25, 12) + ", ")
    f.write(xls(a, 28, 12) + ", " + xls(a, 31, 12) + ",\n")
    f.write("             " + xls(a, 34, 12) + ", " + xls(a, 37, 12) + ", " + xls(a, 40, 12) + "],\n")
    f.write("            ['low_sd_mult', " + xln(a, 24, 1) + ", ")
    if xls(a, 16, 17) == 'S.D.':
        f.write(xln(a, 16, 16) + ", " + xln(a, 19, 16) + ", " + xln(a, 22, 16) + ", ")
        f.write(xln(a, 25, 16) + ", " + xln(a, 28, 16) + ", " + xln(a, 31, 16) + ", ")
        f.write(xln(a, 34, 16) + ", " + xln(a, 37, 16) + ", " + xln(a, 40, 16) + "],\n")
    else:
        sd = xln(a, 24, 1)
        f.write(f"{sd}, {sd}, {sd}, {sd}, {sd}, {sd}, {sd}, {sd}, {sd}],\n")
    f.write("            ['high_sd_mult', " + xln(a, 23, 1) + ", ")
    if xls(a, 15, 17) == 'S.D.':
        f.write(xln(a, 15, 16) + ", " + xln(a, 18, 16) + ", " + xln(a, 21, 16) + ", ")
        f.write(xln(a, 24, 16) + ", " + xln(a, 27, 16) + ", " + xln(a, 30, 16) + ", ")
        f.write(xln(a, 33, 16) + ", " + xln(a, 36, 16) + ", " + xln(a, 39, 16) + "]]\n")
    else:
        sd = xln(a, 23, 1)
        f.write(f"{sd}, {sd}, {sd}, {sd}, {sd}, {sd}, {sd}, {sd}, {sd}]]\n")
    f.write("        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0],\n")
    f.write("            dtype=np.object).set_index('param')\n")
    ad_regions = find_ad_regions(wb=wb)
    ad_outputdir = os.path.join(outputdir, 'ad')
    os.makedirs(ad_outputdir, exist_ok=True)
    sources = extract_source_data(wb=wb, sheet_name='Adoption Data', regions=ad_regions,
            outputdir=ad_outputdir, prefix='ad_')
    f.write("        ad_data_sources = {\n")
    for region, cases in sources.items():
        f.write("            '" + region + "': {\n")
        for (case, sources) in cases.items():
            if isinstance(sources, str):
                f.write("                '" + case + "': THISDIR.joinpath('ad', '" + sources + "'),\n")
            else:
                f.write("                '" + case + "': {\n")
                for (source, filename) in sources.items():
                    f.write("                  '" + source + "': THISDIR.joinpath('ad', '" + filename + "'),\n")
                f.write("              },\n")
        f.write("            },\n")
    f.write("        }\n")
    f.write("        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,\n")
    regional = convert_bool(a.cell(29, 1).value) and convert_bool(a.cell(30, 1).value)
    if regional:
        f.write("            main_includes_regional=True,\n")
    f.write("            adconfig=adconfig)\n")
    f.write("\n")


def write_custom_ad(case, f, wb, outputdir, is_land):
    """Generate the Custom Adoption Data section of a solution.
       Arguments:
         case: 'PDS' or 'REF'
         f: file-like object for output
         wb: an Excel workbook as returned by xlrd
         outputdir: name of directory to write CSV files to.
         is_land: boolean of whether this is a Land solution
    """
    f.write(f"        # Custom {case} Data\n")
    if outputdir is None:
        f.write(f"        # no output dir specified for custom {case} adoption\n\n")
        return
    assert case == 'REF' or case == 'PDS', 'write_custom_ad case must be PDS or REF: ' + str(case)

    ca_dir_path = os.path.join(outputdir, f'ca_{case.lower()}_data')
    if not os.path.exists(ca_dir_path):
        os.mkdir(ca_dir_path)
    scenarios, multipliers = extract_custom_adoption(wb=wb, outputdir=ca_dir_path,
                                                     sheet_name=f'Custom {case} Adoption',
                                                     prefix=f'custom_{case.lower()}_ad_')
    f.write(f"        ca_{case.lower()}_data_sources = [\n")

    for s in scenarios:
        f.write(f"            {{'name': '{s['name'].strip()}', 'include': {str(s['include'])},\n")
        description = s['description'].replace("'", "")
        lines = textwrap.wrap(s['description'], width=75)
        f.write(f"                'description': (\n")
        for line in lines:
            f.write(f"                    '{line} '\n")
        f.write(f"                    ),\n")
        f.write(f"                'filename': THISDIR.joinpath('ca_{case.lower()}_data', '{s['filename']}')}},\n")
    f.write("        ]\n")

    if case == 'REF':
        f.write("        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,\n")
        f.write("            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,\n")
        f.write(f"            high_sd_mult={multipliers['high']}, low_sd_mult={multipliers['low']},\n")
        if is_land:
            f.write("            total_adoption_limit=self.tla_per_region)\n")
        else:
            f.write("            total_adoption_limit=ref_tam_per_region)\n")
    if case == 'PDS':
        f.write("        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,\n")
        f.write("            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,\n")
        f.write(f"            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,\n")
        f.write(f"            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,\n")
        if is_land:
            f.write("            total_adoption_limit=self.tla_per_region)\n")
        else:
            f.write("            total_adoption_limit=pds_tam_per_region)\n")
    f.write("\n")


def write_s_curve_ad(f, wb):
    """Generate the S-Curve section of a solution.
       Arguments:
         f: file-like object for output
         wb: an Excel workbook as returned by xlrd
    """
    s = wb.sheet_by_name('S-Curve Adoption')
    u = wb.sheet_by_name('Unit Adoption Calculations')
    f.write("        sconfig_list = [['region', 'base_year', 'last_year'],\n")
    f.write("            ['World', " + xli(s, 16, 1) + ", " + xli(s, 19, 1) + "],\n")
    f.write("            ['OECD90', " + xli(s, 16, 2) + ", " + xli(s, 19, 2) + "],\n")
    f.write("            ['Eastern Europe', " + xli(s, 16, 3) + ", " + xli(s, 19, 3) + "],\n")
    f.write("            ['Asia (Sans Japan)', " + xli(s, 16, 4) + ", " + xli(s, 19, 4) + "],\n")
    f.write("            ['Middle East and Africa', " + xli(s, 16, 5) + ", " + xli(s, 19, 5) + "],\n")
    f.write("            ['Latin America', " + xli(s, 16, 6) + ", " + xli(s, 19, 6) + "],\n")
    f.write("            ['China', " + xli(s, 16, 7) + ", " + xli(s, 19, 7) + "],\n")
    f.write("            ['India', " + xli(s, 16, 8) + ", " + xli(s, 19, 8) + "],\n")
    f.write("            ['EU', " + xli(s, 16, 9) + ", " + xli(s, 19, 9) + "],\n")
    f.write("            ['USA', " + xli(s, 16, 10) + ", " + xli(s, 19, 10) + "]]\n")
    f.write("        sconfig = pd.DataFrame(sconfig_list[1:], columns=sconfig_list[0], dtype=np.object).set_index('region')\n")
    f.write("        sconfig['pds_tam_2050'] = pds_tam_per_region.loc[[2050]].T\n")
    f.write("        sc_regions = list(self.ac.ref_base_adoption.keys())\n")
    f.write("        sc_percentages = list(self.ac.ref_base_adoption.values())\n")
    f.write("        sconfig['base_adoption'] = pd.Series(list(sc_percentages), index=list(sc_regions))\n")
    f.write("        sconfig['base_percent'] = sconfig['base_adoption'] / pds_tam_per_region.loc[2014]\n")
    f.write("        sconfig['last_percent'] = pd.Series(pd.Series(list(self.ac.pds_adoption_final_percentage.values()),\n")
    f.write("            index=list(self.ac.pds_adoption_final_percentage.values()))\n")
    f.write("        if self.ac.pds_adoption_s_curve_innovation is not None:\n")
    f.write("          sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_innovation)\n")
    f.write("          sconfig['innovation'] = pd.Series(list(sc_percentages), index=list(sc_regions))\n")
    f.write("        if self.ac.pds_adoption_s_curve_imitation is not None:\n")
    f.write("          sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_imitation)\n")
    f.write("          sconfig['imitation'] = pd.Series(list(sc_percentages), index=list(sc_regions))\n")
    f.write("        self.sc = s_curve.SCurve(transition_period=" + xli(s, 14, 0) + ", sconfig=sconfig)\n")
    f.write("\n")


def write_ht(f, wb, has_custom_ref_ad, is_land):
    """Generate the Helper Tables section of a solution.
       Arguments:
         f: file-like object for output
         wb: an Excel workbook as returned by xlrd
         has_custom_ref_ad: whether a REF customadoption is in use.
         has_single_source: whether to emit a pds_adoption_is_single_source arg
         is_land: True if LAND model
    """
    h = wb.sheet_by_name('Helper Tables')
    a = wb.sheet_by_name('Advanced Controls')
    initial_datapoint_year = int(h.cell_value(*cell_to_offsets('B21')))
    final_datapoint_year = int(h.cell_value(*cell_to_offsets('B22')))

    tam_or_tla = 'ref_tam_per_region' if not is_land else 'self.tla_per_region'
    f.write("        ht_ref_adoption_initial = pd.Series(\n")
    f.write("            list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)\n")
    # even when the final_datapoint_year is 2018, the TAM initial year is hard-coded to 2014
    f.write(f"        ht_ref_adoption_final = {tam_or_tla}.loc[{final_datapoint_year}] * (ht_ref_adoption_initial /\n")
    f.write(f"            {tam_or_tla}.loc[2014])\n")
    f.write("        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)\n")
    f.write("        ht_ref_datapoints.loc[" + str(initial_datapoint_year) +
            "] = ht_ref_adoption_initial\n")
    f.write("        ht_ref_datapoints.loc[" + str(final_datapoint_year) +
            "] = ht_ref_adoption_final.fillna(0.0)\n")

    initial_datapoint_year = int(h.cell_value(*cell_to_offsets('B85')))
    final_datapoint_year = int(h.cell_value(*cell_to_offsets('B86')))
    tam_or_tla = 'pds_tam_per_region' if not is_land else 'self.tla_per_region'
    f.write("        ht_pds_adoption_initial = ht_ref_adoption_initial\n")
    f.write("        ht_pds_adoption_final_percentage = pd.Series(\n")
    f.write("            list(self.ac.pds_adoption_final_percentage.values()),\n")
    f.write("            index=list(self.ac.pds_adoption_final_percentage.keys()))\n")
    f.write(f"        ht_pds_adoption_final = ht_pds_adoption_final_percentage * {tam_or_tla}.loc[{final_datapoint_year}]\n")
    f.write("        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)\n")
    f.write("        ht_pds_datapoints.loc[" + str(initial_datapoint_year) + "] = ht_pds_adoption_initial\n")
    f.write("        ht_pds_datapoints.loc[" + str(final_datapoint_year) + "] = ht_pds_adoption_final.fillna(0.0)\n")

    first_world_pds_datapoint = int(h.cell_value(*cell_to_offsets('C85')))
    first_world_pds_yearly_result = int(h.cell_value(*cell_to_offsets('C91')))
    use_first_pds_datapoint_main = (first_world_pds_datapoint == first_world_pds_yearly_result)

    try:
        adoption_base_year = int(a.cell_value(*cell_to_offsets('D59')))
    except ValueError:
        try:
            adoption_base_year = int(a.cell_value(*cell_to_offsets('D57')))
        except ValueError:
            adoption_base_year = None

    copy_pds_to_ref = True
    for pds, ref in [('C91', 'C27'), ('C92', 'C28'), ('C93', 'C29'), ('C94', 'C30')]:
        if int(h.cell_value(*cell_to_offsets(pds))) != int(h.cell_value(*cell_to_offsets(ref))):
            copy_pds_to_ref = False

    f.write("        self.ht = helpertables.HelperTables(ac=self.ac,\n")
    f.write("            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,\n")
    f.write("            pds_adoption_data_per_region=pds_adoption_data_per_region,\n")
    if not is_land:
        f.write("            ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,\n")
    else:
        f.write("            ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,\n")
    if has_custom_ref_ad:
        f.write("            ref_adoption_data_per_region=ref_adoption_data_per_region,\n")
    f.write(f"            use_first_pds_datapoint_main={use_first_pds_datapoint_main},\n")
    if adoption_base_year:
        f.write(f"            adoption_base_year={adoption_base_year},\n")
    f.write(f"            copy_pds_to_ref={copy_pds_to_ref},\n")
    f.write("            pds_adoption_trend_per_region=pds_adoption_trend_per_region,\n")
    f.write("            pds_adoption_is_single_source=pds_adoption_is_single_source)\n")
    f.write("\n")


def write_ef(f, wb):
    """Write out the Emissions Factors module for this solution class."""
    ef_tab = wb.sheet_by_name('Emissions Factors')
    grid_factor_2015 = float(ef_tab.cell_value(*cell_to_offsets('B291')))
    if grid_factor_2015 == pytest.approx(0.619753649484954):
        f.write("        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=2)\n")
    else:
        f.write("        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)\n")
    f.write("\n")


def write_ua(f, wb, is_rrs=True):
    """Write out the Unit Adoption module for this solution class."""
    ua_tab = wb.sheet_by_name('Unit Adoption Calculations')
    ac_tab = wb.sheet_by_name('Advanced Controls')
    f.write("        self.ua = unitadoption.UnitAdoption(ac=self.ac,\n")
    if is_rrs:
        f.write("            ref_total_adoption_units=ref_tam_per_region,\n")
        f.write("            pds_total_adoption_units=pds_tam_per_region,\n")
    else:
        f.write("            ref_total_adoption_units=self.tla_per_region,\n")
        f.write("            pds_total_adoption_units=self.tla_per_region,\n")
        f.write("            electricity_unit_factor=1000000.0,\n")
    f.write("            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),\n")
    f.write("            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),\n")
    if 'Repeated First Cost to Maintaining Implementation Units' in ac_tab.cell(42, 0).value:
        repeated_cost_for_iunits = convert_bool(ac_tab.cell(42, 2).value)
        f.write("            repeated_cost_for_iunits=" + str(repeated_cost_for_iunits) + ",\n")
    # If S135 == D135 (for all regions), then it must not be adding in 'Advanced Controls'!C62
    bug_cfunits_double_count = False
    for i in range(0, 9):
        if ua_tab.cell(134, 18 + i).value != ua_tab.cell(134, 3 + i).value:
            bug_cfunits_double_count = True
    f.write("            bug_cfunits_double_count=" + str(bug_cfunits_double_count) + ")\n")
    f.write("        soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()\n")
    f.write("        soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()\n")
    f.write("        conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()\n")
    f.write("        soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()\n")
    f.write("\n")


def write_fc(f, wb):
    """Code generate the First Code module for this solution class."""
    fc_tab = wb.sheet_by_name('First Cost')
    f.write("        self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=" +
            xli(fc_tab, 24, 2) + ",\n")
    f.write("            ref_learning_increase_mult=" + xli(fc_tab, 24, 3) +
            ", conv_learning_increase_mult=" + xli(fc_tab, 24, 4) + ",\n")
    f.write("            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,\n")
    f.write("            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,\n")
    f.write("            conv_ref_tot_iunits=conv_ref_tot_iunits,\n")
    f.write("            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),\n")
    f.write("            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),\n")
    f.write("            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),\n")
    if fc_tab.cell(35, 15).value == 'Implementation Units Installed Each Yr (CONVENTIONAL-REF)':
        f.write("            conv_ref_first_cost_uses_tot_units=True,\n")
    if fc_tab.cell(14, 5).value == 1000000000 and fc_tab.cell(14, 6).value == '$/kW TO $/TW':
        f.write("            fc_convert_iunit_factor=rrs.TERAWATT_TO_KILOWATT)\n")
    elif fc_tab.cell(15, 5).value == 1000000 and fc_tab.cell(17, 5).value == 'million hectare':
        f.write("            fc_convert_iunit_factor=land.MHA_TO_HA)\n")
    else:
        f.write("            fc_convert_iunit_factor=" + xln(fc_tab, 14, 5) + ")\n")
    f.write('\n')


def write_oc(f, wb, is_land=False):
    """Code generate the Operating Code module for this solution class."""
    oc_tab = wb.sheet_by_name('Operating Cost')
    f.write("        self.oc = operatingcost.OperatingCost(ac=self.ac,\n")
    f.write("            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,\n")
    f.write("            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,\n")
    f.write("            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,\n")
    f.write("            conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),\n")
    f.write("            soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),\n")
    f.write("            soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),\n")
    f.write("            conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),\n")
    f.write("            single_iunit_purchase_year=" + xli(oc_tab, 120, 8) + ",\n")
    f.write("            soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),\n")
    f.write("            conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit(),\n")

    units = oc_tab.cell(12, 5).value
    is_energy_units = (units == '$/kW TO $/TW' or units == 'From US$2014 per kW to US$2014 per TW')
    conversion_factor_fom = oc_tab.cell(12, 4).value
    conversion_factor_vom = oc_tab.cell(13, 4).value

    if conversion_factor_fom == 1000000000 and is_energy_units:
        conversion_factor_fom = 'rrs.TERAWATT_TO_KILOWATT'
    if conversion_factor_vom == 1000000000 and is_energy_units:
        conversion_factor_vom = 'rrs.TERAWATT_TO_KILOWATT'
    if is_land:
        conversion_factor_fom = conversion_factor_vom = 'land.MHA_TO_HA'

    # In almost all cases the two conversion factors are equal. We only know of one solution where
    # they differ (Heatpumps). operatingcost.py accomodates this, if passed a single number it will
    # use it for both factors.
    if conversion_factor_fom == conversion_factor_vom:
        f.write("            conversion_factor=" + str(conversion_factor_fom) + ")\n")
    else:
        f.write("            conversion_factor=(" + str(conversion_factor_fom) + ", " +
                str(conversion_factor_vom) + "))\n")
    f.write('\n')


def write_c2_c4(f, is_rrs=True, is_protect=False, has_harvest=False):
    """Write out the CO2 Calcs and CH4 Calcs modules for this solution class."""
    f.write("        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,\n")
    if not is_rrs:
        f.write("            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),\n")
    f.write("            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)\n\n")
    f.write("        self.c2 = co2calcs.CO2Calcs(ac=self.ac,\n")
    f.write("            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),\n")
    f.write("            soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),\n")
    f.write("            soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),\n")
    if is_rrs:
        f.write("            soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),\n")
        f.write("            soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),\n")
        f.write("            soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),\n")
    else:
        f.write("            soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),\n")
        f.write("            soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),\n")
        f.write("            soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),\n")
        f.write("            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),\n")
    f.write("            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),\n")
    f.write("            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),\n")
    f.write("            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),\n")
    f.write("            conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),\n")
    f.write("            conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),\n")
    f.write("            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,\n")
    if is_rrs:
        f.write("            fuel_in_liters=False)\n")
    else:
        if is_protect:
            f.write("            tot_red_in_deg_land=self.ua.cumulative_reduction_in_total_degraded_land(),\n")
            f.write("            pds_protected_deg_land=self.ua.pds_cumulative_degraded_land_protected(),\n")
            f.write("            ref_protected_deg_land=self.ua.ref_cumulative_degraded_land_protected(),\n")
        if has_harvest:
            f.write("            annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),\n")
        f.write("            regime_distribution=self.ae.get_land_distribution(),\n")
        f.write("            regimes=dd.THERMAL_MOISTURE_REGIMES8)\n")
    f.write("\n")


def find_source_data_columns(wb, sheet_name, row):
    """Figure out which columns in Adoption Data (and similar tabs) should be extracted.
       Arguments:
         wb: Excel workbook
         sheet_name: name of the spreadsheet tab like "Adoption Data" or "Fresh Adoption Data"
         row: row number to check
       Returns:
         The string of Excel columns to use, like 'B:R'
    """
    tab = wb.sheet_by_name(sheet_name)
    for col in range(2, tab.ncols):
        if tab.cell(row, col).value == 'Functional Unit':
            break
    return 'B:' + chr(ord('A') + col - 1)


def data_sources_equivalent_for_region(region, world):
    for case, region_sources in region.items():
        world_sources = world.get(case, {})
        for source, region_filename in region_sources.items():
            world_filename = world_sources.get(source, None)
            if region_filename != world_filename:
                return False
    return True


def find_ad_regions(wb):
    ad_default = {'World': 44, 'OECD90': 104, 'Eastern Europe': 168, 'Asia (Sans Japan)': 231,
                  'Middle East and Africa': 294, 'Latin America': 357, 'China': 420, 'India': 484,
                  'EU': 548, 'USA': 613}
    ad_microwind = {'World': 44, 'OECD90': 296, 'Eastern Europe': 170, 'Asia (Sans Japan)': 233,
                  'Middle East and Africa': 359, 'Latin America': 423, 'China': 487, 'India': 613,
                  'EU': 107, 'USA': 552}
    ad_afforestation = {'World': 44, 'OECD90': 102, 'Eastern Europe': 164, 'Asia (Sans Japan)': 225,
                  'Middle East and Africa': 286, 'Latin America': 347, 'China': 408, 'India': 470,
                  'EU': 530, 'USA': 591}
    tab = wb.sheet_by_name("Adoption Data")
    for candidate in [ad_microwind, ad_afforestation]:
        for region, row in candidate.items():
            if region == 'World':
                continue
            found = False
            for r in range(row - 10, row + 1):
                if region.lower() in str(tab.cell(r, 0).value).lower():
                    found = True
                    break
            if not found:
                break
        else:
            return candidate
    return ad_default


def extract_source_data(wb, sheet_name, regions, outputdir, prefix):
    """Pull the names of sources, by case, from the Excel file and write data to CSV.
       Arguments:
         wb: Excel workbook
         sheet_name: name of the Excel tab to go to, like 'Adoption Data' or 'TAM Data'
         regions: a dict of regions to extract and the line numbers they start at:
           { 'World': 44, 'OECD90': 104, 'Eastern Europe': 168 ...}
         outputdir: name of directory to write CSV files to.
         prefix: prefix for filenames like 'ad_' or 'tam_'

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
    region_data = {}
    for (region, skiprows) in regions.items():
        usecols = find_source_data_columns(wb=wb, sheet_name=sheet_name, row=skiprows)
        df = pd.read_excel(wb, engine='xlrd', sheet_name=sheet_name, header=0,
                           index_col=0, usecols=usecols, skiprows=skiprows, nrows=49)
        df.name = region
        df.rename(columns=normalize_source_name, inplace=True)
        region_data[region] = df

    sources = {}
    for df in region_data.values():
        for source_name in df.columns:
            if source_name is not None:
                sources[source_name] = ''

    for source_name in list(sources.keys()):
        if not source_name:
            continue
        df = pd.DataFrame()
        for region in region_data.keys():
            if source_name in region_data[region].columns:
                df[region] = region_data[region].loc[:, source_name]
            else:
                df[region] = np.nan
        filename = get_filename_for_source(source_name, prefix=prefix)
        if df.empty or df.isna().all(axis=None, skipna=False) or not filename:
            del sources[source_name]
            continue
        df.index = df.index.astype(int)
        df.index.name = 'Year'

        zero_adoption_ok = False
        zero_adoption_solutions = ['nuclear', 'cars', 'geothermal', 'improvedcookstoves',
                'waterefficiency']
        for sname in zero_adoption_solutions:
            if sname in outputdir:
                zero_adoption_ok = True
        if not zero_adoption_ok:
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
        df.to_csv(outputfile, header=True)
        sources[source_name] = filename

    tmp_cases = {}
    tab = wb.sheet_by_name(sheet_name)
    case_line = regions['World'] - 1
    for (region, line) in regions.items():
        case = ''
        for col in range(2, tab.ncols):
            if tab.cell(line, col).value == 'Functional Unit':
                break
            if tab.cell(case_line, col).ctype != xlrd.XL_CELL_EMPTY:
                case = normalize_case_name(tab.cell(case_line, col).value)
            # it is important to get the source name from the regional_data.columns here, not re-read
            # the source_name from Excel, because some solutions like Composting have duplicate
            # column names and pd.read_excel automatically appends ".1" and ".2" to make them unique.
            source_name = region_data[region].columns[col - 2]
            filename = sources.get(source_name, None)
            if source_name is not None and filename is not None:
                key = 'Region: ' + region
                region_cases = tmp_cases.get(key, dict())
                tmp_cases[key] = region_cases
                s = region_cases.get(case, dict())
                if source_name not in s:
                    s[source_name] = filename
                    region_cases[case] = s

    # suppress regions which are a subset of World.
    if 'Region: World' in tmp_cases:
        world = tmp_cases['Region: World']
        del tmp_cases['Region: World']
        cases = world.copy()
        for (region_name, sources) in tmp_cases.items():
            if not data_sources_equivalent_for_region(region=sources, world=world):
                cases[region_name] = sources
    else:
        cases = tmp_cases
    return cases


def extract_custom_adoption(wb, outputdir, sheet_name, prefix):
    """Extract custom adoption scenarios from an Excel file.
       Arguments:
         wb: Excel workbook as returned by xlrd.
         outputdir: directory where output files are written
         sheet_name: Excel sheet name to extract from
         prefix: string to prepend to filenames
    """
    custom_ad_tab = wb.sheet_by_name(sheet_name)
    defaultinclude = False if 'PDS' in sheet_name else True

    assert custom_ad_tab.cell_value(*cell_to_offsets('AN25')) == 'High'
    multipliers = {'high': custom_ad_tab.cell_value(*cell_to_offsets('AO25')),
                   'low': custom_ad_tab.cell_value(*cell_to_offsets('AO26'))}
    scenarios = []
    for row in range(20, 36):
        if not re.search(r"Scenario \d+", str(custom_ad_tab.cell(row, 13).value)):
            continue
        name = normalize_source_name(str(custom_ad_tab.cell(row, 14).value))
        includestr = str(custom_ad_tab.cell_value(row, 18))
        include = convert_bool(includestr) if includestr else defaultinclude
        filename = get_filename_for_source(name, prefix=prefix)
        if not filename:
            continue
        skip = True
        for row in range(0, custom_ad_tab.nrows):
            if normalize_source_name(str(custom_ad_tab.cell(row, 1).value)) == name:
                df = pd.read_excel(wb, engine='xlrd', sheet_name=sheet_name,
                                   header=0, index_col=0, usecols="A:K", skiprows=row + 1, nrows=49)
                df.rename(mapper={'Middle East & Africa': 'Middle East and Africa',
                          'Asia (sans Japan)': 'Asia (Sans Japan)'},
                          axis='columns', inplace=True)
                if not df.dropna(how='all', axis=1).dropna(how='all', axis=0).empty:
                    df.to_csv(os.path.join(outputdir, filename), index=True, header=True)
                    skip = False
                for offset in range(0, 3):
                    description = str(custom_ad_tab.cell_value(row + offset, 13))
                    if description:
                        break
                break
        if not skip:
            scenarios.append({'name': name, 'filename': filename, 'include': include,
                'description': description})
    return scenarios, multipliers


def extract_custom_tla(wb, outputdir):
    """Extract custom TLA from an Excel file.
       Arguments:
         wb: Excel workbook as returned by xlrd.
         outputdir: directory where output files are written
    """
    tla_tab = wb.sheet_by_name('TLA Data')
    title_cell = tla_tab.cell_value(*cell_to_offsets('A642')).strip()
    assert title_cell == 'Customized TLA Data', 'Title Cell: ' + title_cell
    assert tla_tab.cell_value(*cell_to_offsets('B645')) == 2012

    df = pd.read_excel(wb, engine='xlrd', sheet_name='TLA Data',
                       header=0, index_col=0, usecols="B:L", skiprows=643, nrows=49)
    df.index.name = 'Year'
    df.index.astype(int)
    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
    if df.empty:
        raise ValueError('Custom TLA is selected but there is no Custom TLA Data')
    else:
        df.to_csv(os.path.join(outputdir, 'custom_tla_data.csv'), index=True, header=True)


def extract_vmas(f, wb, outputdir):
    """Extract VMAs from an Excel file.
       Arguments:
         f: output __init__.py file
         wb: Excel workbook as returned by xlrd.
         outputdir: directory where output files are written
    """
    vma_dir_path = os.path.join(outputdir, 'vma_data')
    if not os.path.exists(vma_dir_path):
        os.mkdir(vma_dir_path)
    vma_r = VMAReader(wb)
    if 'Variable Meta-analysis-DD' in wb.sheet_names():
        vmas = vma_r.read_xls(csv_path=vma_dir_path, alt_vma=True)
    else:
        vmas = vma_r.read_xls(csv_path=vma_dir_path)
    f.write("VMAs = {\n")
    for _, row in vmas.iterrows():
        f.write(f"    '{row['Title on xls']}': vma.VMA(\n")
        filename = row['Filename']
        if not filename:
            f.write(f"        filename=None, use_weight={row['Use weight?']}),\n")
        else:
            if isinstance(filename, str):
                path = f'THISDIR.joinpath("vma_data", "{filename}")'
            else:
                path = f'DATADIR.joinpath(*{filename})'
            f.write(f"        filename={path},\n")
            f.write(f"        use_weight={row['Use weight?']}),\n")
    f.write("}\n")
    f.write("vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))\n\n")


def lookup_unit(tab, row, col):
    unit_mapping = {
        'Million hectare': u'Mha',
        'MMt FlyAsh Cement (Sol) or MMt OPC (Conv) (Transient)': u'MMt',
        'Billion USD': u'US$B',
        'million m2 commercial floor space': u'Mm\u00B2',
        'Million Households': u'MHholds',
        'Million m2 of Comm.+Resid. Floor Area Equiv. for Cold Climates': u'Mm\u00B2',
        'Giga-Liter Water': u'GL H\u2082O',
        'Million Metric tonnes per year': 'MMt',
        'million tonne-km': 'Mt-km',
        'million tonne-kms': 'Mt-km',
        'Residential and Commercial roof area, m2': u'm\u00B2',
        'Residential and Commercial roof area,  m2': u'm\u00B2',
    }
    name = str(tab.cell_value(row, col))
    return unit_mapping.get(name, name)


def write_units_rrs(f, wb):
    """Write out units for this solution."""
    sr_tab = wb.sheet_by_name('ScenarioRecord')
    f.write('units = {\n')
    for row in range(1, sr_tab.nrows):
        col_d = sr_tab.cell_value(row, 3)
        col_e = sr_tab.cell_value(row, 4)
        if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:
            f.write('    "implementation unit": "' + lookup_unit(sr_tab, row + 5, 5) + '",\n')
            f.write('    "functional unit": "' + lookup_unit(sr_tab, row + 7, 5) + '",\n')
            f.write('    "first cost": "' + lookup_unit(sr_tab, row + 16, 5) + '",\n')
            f.write('    "operating cost": "' + lookup_unit(sr_tab, row + 17, 5) + '",\n')
            break
    f.write('}\n\n')


def write_units_land(f, wb):
    """Write out units for this solution."""
    sr_tab = wb.sheet_by_name('ScenarioRecord')
    f.write('units = {\n')
    for row in range(1, sr_tab.nrows):
        col_d = sr_tab.cell_value(row, 3)
        col_e = sr_tab.cell_value(row, 4)
        if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:
            f.write('    "implementation unit": None,\n')
            f.write('    "functional unit": "' + lookup_unit(sr_tab, row + 5, 5) + '",\n')
            f.write('    "first cost": "' + lookup_unit(sr_tab, row + 12, 5) + '",\n')
            f.write('    "operating cost": "' + lookup_unit(sr_tab, row + 13, 5) + '",\n')
            break
    f.write('}\n\n')


def find_RRS_solution_category(wb):
    """Find the solution category (REPLACEMENT or REDUCTION)."""
    ac_tab = wb.sheet_by_name('Advanced Controls')
    possible = [('A157', 'A159'), ('A142', 'A144')]
    for labelcell, valuecell in possible:
        label = str(ac_tab.cell_value(*cell_to_offsets(labelcell)))
        if 'Is this primarily a' in label:
            return str(ac_tab.cell_value(*cell_to_offsets(valuecell)))
    return None


def output_solution_python_file(outputdir, xl_filename):
    """Extract relevant fields from Excel file and output a Python class.

       Arguments:
         outputdir: filename to write to. None means stdout.
         xl_filename: an Excel file to open, can be xls/xlsm/etc.
           Note that we cannot run Macros from xlsm files, only read values.
    """
    py_filename = '-' if outputdir is None else os.path.join(outputdir, '__init__.py')
    wb = xlrd.open_workbook(filename=xl_filename)
    ac_tab = wb.sheet_by_name('Advanced Controls')

    if ('BIOSEQ' in xl_filename or 'PDLAND' in xl_filename or 'L-Use' in xl_filename or
            'AEZ Data' in wb.sheet_names()):
        is_rrs = False
        is_land = True
    elif 'RRS' in xl_filename or 'TAM' in wb.sheet_names():
        is_rrs = True
        is_land = False
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
    f.write('from model import advanced_controls as ac\n')
    if is_land:
        f.write('from model import aez\n')
    f.write('from model import ch4calcs\n')
    f.write('from model import co2calcs\n')
    f.write('from model import customadoption\n')
    f.write('from model import dd\n')
    f.write('from model import emissionsfactors\n')
    f.write('from model import firstcost\n')
    f.write('from model import helpertables\n')
    f.write('from model import operatingcost\n')
    f.write('from model import s_curve\n')
    f.write('from model import unitadoption\n')
    f.write('from model import vma\n')

    if has_tam:
        f.write('from model import tam\n')
    elif is_land:
        f.write('from model import tla\n')

    if is_rrs:
        f.write('from solution import rrs\n\n')
        sc = ac.string_to_solution_category(find_RRS_solution_category(wb=wb))
        solution_category = f'ac.SOLUTION_CATEGORY.{ac.solution_category_to_string(sc).upper()}'
        scenarios = get_rrs_scenarios(wb=wb, solution_category=sc)
    elif is_land:
        f.write('from solution import land\n\n')
        sc = ac.string_to_solution_category('LAND')
        solution_category = 'ac.SOLUTION_CATEGORY.LAND'
        scenarios = get_land_scenarios(wb=wb, solution_category=sc)
    else:
        scenarios = {}

    f.write("DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')\n")
    f.write("THISDIR = pathlib.Path(__file__).parents[0]\n")
    extract_vmas(f=f, wb=wb, outputdir=outputdir)
    if is_rrs:
        write_units_rrs(f=f, wb=wb)
    if is_land:
        write_units_land(f=f, wb=wb)
    f.write(f"name = '{solution_name}'\n")
    f.write(f"solution_category = {solution_category}\n")
    f.write("\n")

    has_default_pds_ad = has_custom_pds_ad = has_default_ref_ad = has_custom_ref_ad = False
    has_s_curve_pds_ad = has_linear_pds_ad = use_custom_tla = is_protect = has_harvest = False
    for s in scenarios.values():
        if s.get('soln_pds_adoption_basis', '') == 'Existing Adoption Prognostications':
            has_default_pds_ad = True
        if s.get('soln_pds_adoption_basis', '') == 'Fully Customized PDS':
            has_custom_pds_ad = True
        if 'S-Curve' in s.get('soln_pds_adoption_basis', ''):
            has_s_curve_pds_ad = True
        if 'Linear' in s.get('soln_pds_adoption_basis', ''):
            has_linear_pds_ad = True
        if s.get('soln_ref_adoption_basis', '') == 'Default':
            has_default_ref_ad = True
        if s.get('soln_ref_adoption_basis', '') == 'Custom':
            has_custom_ref_ad = True
        if s.get('use_custom_tla', ''):
            if not 'custom_tla_fixed_value' in s:
                extract_custom_tla(wb, outputdir=outputdir)
            use_custom_tla = True
        if 'delay_protection_1yr' in s.keys():
            is_protect = True
        if 'carbon_not_emitted_after_harvesting' in s.keys():
            has_harvest = True

    p = pathlib.Path(f'{outputdir}/ac')
    p.mkdir(parents=False, exist_ok=True)
    for name, s in scenarios.items():
        fname = p.joinpath(re.sub(r"['\"\n()\\/\.]", "", name).replace(' ', '_').strip() + '.json')
        write_scenario(filename=fname, s=s)
    f.write("scenarios = ac.load_scenarios_from_json("
        "directory=THISDIR.joinpath('ac'), vmas=VMAs)\n")
    f.write("\n\n")

    f.write("class Scenario:\n")
    f.write("    name = name\n")
    f.write("    units = units\n")
    f.write("    vmas = VMAs\n")
    f.write("    solution_category = solution_category\n")
    f.write("\n")
    f.write("    def __init__(self, scenario=None):\n")
    f.write("        if scenario is None:\n")
    f.write("            scenario = list(scenarios.keys())[0]\n")
    f.write("        self.scenario = scenario\n")
    f.write("        self.ac = scenarios[scenario]\n")
    f.write("\n")
    if has_tam:
        f.write("        # TAM\n")
        write_tam(f=f, wb=wb, outputdir=outputdir)
    elif is_land:
        f.write("        # TLA\n")
        write_aez(f=f, wb=wb)
        if use_custom_tla:
            f.write("        if self.ac.use_custom_tla and self.ac.custom_tla_fixed_value is not None:\n")
            f.write("            self.c_tla = tla.CustomTLA(fixed_value=self.ac.custom_tla_fixed_value)\n")
            f.write("            custom_world_vals = self.c_tla.get_world_values()\n")
            f.write("        elif self.ac.use_custom_tla:\n")
            f.write("            self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))\n")
            f.write("            custom_world_vals = self.c_tla.get_world_values()\n")
            f.write("        else:\n")
            f.write("            custom_world_vals = None\n")
            f.write("        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(),\n")
            f.write("            custom_world_values=custom_world_vals)\n\n")
        else:
            f.write("        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())\n\n")

    if has_default_pds_ad or has_default_ref_ad:
        write_ad(f=f, wb=wb, outputdir=outputdir)
    if has_custom_pds_ad:
        write_custom_ad(case='PDS', f=f, wb=wb, outputdir=outputdir, is_land=is_land)
    if has_custom_ref_ad:
        write_custom_ad(case='REF', f=f, wb=wb, outputdir=outputdir, is_land=is_land)
    if has_s_curve_pds_ad:
        write_s_curve_ad(f=f, wb=wb)

    if has_custom_ref_ad and has_default_ref_ad:
        f.write("        if self.ac.soln_ref_adoption_basis == 'Custom':\n")
        f.write("            ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()\n")
        f.write("        else:\n")
        f.write("            ref_adoption_data_per_region = None\n")
    elif has_custom_ref_ad:
        f.write("        ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()\n")
    elif has_default_ref_ad:
        f.write("        ref_adoption_data_per_region = None\n")
    f.write("\n")

    f.write("        if False:\n")
    f.write("            # One may wonder why this is here. This file was code generated.\n")
    f.write("            # This 'if False' allows subsequent conditions to all be elif.\n")
    f.write("            pass\n")
    if has_custom_pds_ad:
        f.write("        elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':\n")
        f.write("            pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()\n")
        f.write("            pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()\n")
        f.write("            pds_adoption_is_single_source = None\n")
    if has_s_curve_pds_ad:
        f.write("        elif self.ac.soln_pds_adoption_basis == 'Logistic S-Curve':\n")
        f.write("            pds_adoption_data_per_region = None\n")
        f.write("            pds_adoption_trend_per_region = self.sc.logistic_adoption()\n")
        f.write("            pds_adoption_is_single_source = None\n")
        f.write("        elif self.ac.soln_pds_adoption_basis == 'Bass Diffusion S-Curve':\n")
        f.write("            pds_adoption_data_per_region = None\n")
        f.write("            pds_adoption_trend_per_region = self.sc.bass_diffusion_adoption()\n")
        f.write("            pds_adoption_is_single_source = None\n")
    if has_default_pds_ad or has_default_ref_ad:
        f.write("        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':\n")
        f.write("            pds_adoption_data_per_region = self.ad.adoption_data_per_region()\n")
        f.write("            pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()\n")
        f.write("            pds_adoption_is_single_source = self.ad.adoption_is_single_source()\n")
    if has_linear_pds_ad:
        f.write("        elif self.ac.soln_pds_adoption_basis == 'Linear':\n")
        f.write("            pds_adoption_data_per_region = None\n")
        f.write("            pds_adoption_trend_per_region = None\n")
        f.write("            pds_adoption_is_single_source = None\n")
    f.write("\n")

    write_ht(f=f, wb=wb, has_custom_ref_ad=has_custom_ref_ad, is_land=is_land)

    write_ef(f=f, wb=wb)
    write_ua(f=f, wb=wb, is_rrs=is_rrs)
    write_fc(f=f, wb=wb)
    write_oc(f=f, wb=wb, is_land=is_land)

    write_c2_c4(f=f, is_rrs=is_rrs, is_protect=is_protect, has_harvest=has_harvest)

    if is_rrs:
        f.write("        self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],\n")
        f.write("            soln_avg_annual_use=self.ac.soln_avg_annual_use,\n")
        f.write("            conv_avg_annual_use=self.ac.conv_avg_annual_use)\n")
        f.write("\n")

    f.close()


def link_vma(tab, row, col):
    """
    Certain AdvancedControls inputs are linked to the mean, high or low value of their
    corresponding VMA tables. In the Excel ScenarioRecord, the cell value will look like:
    'Val:(328.415857769938) Formula:=C80'
    We can infer the chosen statistic from the cell reference. If there is no forumla we
    return the cell value as a float with no reference to the VMA result.
    Args:
      tab: the Sheet object to use
      row: numeric row number to look at
      col: numeric column number to look at

    Returns:
      'mean', 'high' or 'low' or raw value if no formula in cell
    """
    cell_value = str(tab.cell_value(row, col))
    if not isinstance(cell_value, str) or 'Formula:=' not in cell_value:
        return {'value': convert_sr_float(cell_value), 'statistic': ''}
    if 'Error' in cell_value:
        return 0.
    if True in [cell_value.endswith(x) for x in ['80', '95', '101', '116', '146', '161', '175', '189', '140']]:
        return {'value': convert_sr_float(cell_value), 'statistic': 'mean'}
    elif True in [cell_value.endswith(x) for x in ['81', '96', '102', '117', '147', '162', '176', '190', '141']]:
        return {'value': convert_sr_float(cell_value), 'statistic': 'high'}
    elif True in [cell_value.endswith(x) for x in ['82', '97', '103', '118', '148', '163', '177', '191', '142']]:
        return {'value': convert_sr_float(cell_value), 'statistic': 'low'}
    else:
        formula = cell_value.split(':=')[1]
        warnings.warn(f'formula "{formula}" in {col}:{str(row)} not recognised - using value')
        return {'value': convert_sr_float(cell_value), 'xls cell formula': formula}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create python Drawdown solution from Excel version.')
    parser.add_argument('--excelfile', help='Excel filename to process')
    parser.add_argument('--outputdir', default=None, required=True,
                        help='Directory to write generated Python code to')
    args = parser.parse_args(sys.argv[1:])
    outputdirpath = pathlib.Path(args.outputdir)

    if args.excelfile is None:
        files = list(glob.glob(str(outputdirpath.joinpath('testdata/[!~]*.xlsm'))))
        if len(files) == 1:
            args.excelfile = files[0]
            print(f'Using excelfile: {str(args.excelfile)}')

    output_solution_python_file(outputdir=outputdirpath, xl_filename=args.excelfile)
