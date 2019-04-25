#!/usr/bin/env python  # by Denton Gentry
"""Extract parameters from a Drawdown excel model to help create  # by Denton Gentry
   the Python implementation of the solution and its scenarios.  # by Denton Gentry
  # by Denton Gentry
   The code in this file is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE  # by Denton Gentry
   version 3.0.  # by Denton Gentry
  # by Denton Gentry
   Outputs of this utility are considered to be data and do not automatically  # by Denton Gentry
   carry the license used for the code in this utility. It is up to the user and  # by Denton Gentry
   copyright holder of the inputs to determine what copyright applies to the  # by Denton Gentry
   output.  # by Denton Gentry
"""  # by Denton Gentry
# by Denton Gentry
import argparse  # by Denton Gentry
import os.path  # by Denton Gentry
import re  # by Denton Gentry
import sys  # by Denton Gentry
import textwrap  # by Denton Gentry
import warnings
# by Denton Gentry
import xlrd  # by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry
from solution import rrs  # by Denton Gentry
# by Denton Gentry
from tools.util import convert_bool, cell_to_offsets  # by Denton Gentry
from tools.vma_xls_extract import VMAReader
from model.advanced_controls import SOLUTION_CATEGORY  # by Denton Gentry

# by Denton Gentry
pd.set_option('display.max_rows', 500)  # by Denton Gentry
pd.set_option('display.max_columns', 500)  # by Denton Gentry
pd.set_option('display.width', 1000)  # by Denton Gentry


# by Denton Gentry
def convert_sr_float(val):  # by Denton Gentry
    """Return floating point value from Excel ScenarioRecord tab.  # by Denton Gentry
    # by Denton Gentry
       There are three main formats:  # by Denton Gentry
       + simple: 0.182810601365724  # by Denton Gentry
       + percentage: 20%  # by Denton Gentry
       + annotated: Val:(0.182810601365724) Formula:='Variable Meta-analysis'!G1411  # by Denton Gentry
    """  # by Denton Gentry
    m = re.match(r'Val:\(([-+]?(\d+(\.\d*)?|\d+(\,\d*)?|\.\d+)([eE][-+]?\d+)?)\) Formula:=',
                 str(val))  # by Denton Gentry
    if m:  # by Denton Gentry
        s = str(m.group(1)).replace(',', '.')  # by Denton Gentry
        return float(s)  # by Denton Gentry
    if str(val).endswith('%'):  # by Denton Gentry
        (num, _) = str(val).split('%', maxsplit=1)  # by Denton Gentry
        return float(num) / 100.0  # by Denton Gentry
    if val == '':  # by Denton Gentry
        return 0.0  # by Denton Gentry
    return float(val)  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def get_rrs_scenarios(wb):  # by Denton Gentry
    """Extract scenarios from an RRS Excel file.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         wb: Excel workbook as returned by xlrd.  # by Denton Gentry
    """  # by Denton Gentry
    sr_tab = wb.sheet_by_name('ScenarioRecord')  # by Denton Gentry
    ac_tab = wb.sheet_by_name('Advanced Controls')  # by Denton Gentry
    scenarios = {}  # by Denton Gentry
    for row in range(1, sr_tab.nrows):  # by Denton Gentry
        col_d = sr_tab.cell_value(row, 3)  # by Denton Gentry
        col_e = sr_tab.cell_value(row, 4)  # by Denton Gentry
        if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:  # by Denton Gentry
            # start of scenario block  # by Denton Gentry
            scenario_name = col_e  # by Denton Gentry
            s = {}  # by Denton Gentry
            # by Denton Gentry
            s['description'] = sr_tab.cell_value(row + 1, 4)  # by Denton Gentry
            report_years = sr_tab.cell_value(row + 2, 4)  # E:2 from top of scenario  # by Denton Gentry
            (start, end) = report_years.split('-')  # by Denton Gentry
            s['report_start_year'] = int(start)  # by Denton Gentry
            s['report_end_year'] = int(end)  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 46, 1) == 'Conventional'  # by Denton Gentry
            assert sr_tab.cell_value(row + 47, 3) == 'First Cost:'  # by Denton Gentry
            s['conv_2014_cost'] = convert_sr_float(sr_tab.cell_value(row + 47, 4))  # by Denton Gentry
            s['conv_first_cost_efficiency_rate'] = convert_sr_float(sr_tab.cell_value(row + 48, 4))  # by Denton Gentry
            s['conv_lifetime_capacity'] = convert_sr_float(sr_tab.cell_value(row + 49, 4))  # by Denton Gentry
            s['conv_avg_annual_use'] = convert_sr_float(sr_tab.cell_value(row + 50, 4))  # by Denton Gentry
            s['conv_var_oper_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 51, 4))  # by Denton Gentry
            s['conv_fixed_oper_cost_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 52, 4))  # by Denton Gentry
            s['conv_fuel_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 54, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 64, 1) == 'Solution'  # by Denton Gentry
            assert sr_tab.cell_value(row + 65, 3) == 'First Cost:'  # by Denton Gentry
            s['pds_2014_cost'] = s['ref_2014_cost'] = convert_sr_float(
                sr_tab.cell_value(row + 65, 4))  # by Denton Gentry
            s['soln_first_cost_efficiency_rate'] = convert_sr_float(sr_tab.cell_value(row + 66, 4))  # by Denton Gentry
            s['soln_first_cost_below_conv'] = convert_bool(sr_tab.cell_value(row + 66, 6))  # by Denton Gentry
            s['soln_lifetime_capacity'] = convert_sr_float(sr_tab.cell_value(row + 67, 4))  # by Denton Gentry
            s['soln_avg_annual_use'] = convert_sr_float(sr_tab.cell_value(row + 68, 4))  # by Denton Gentry
            s['soln_var_oper_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 69, 4))  # by Denton Gentry
            s['soln_fixed_oper_cost_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 70, 4))  # by Denton Gentry
            s['soln_fuel_cost_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 72, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 76, 1) == 'General'  # by Denton Gentry
            s['npv_discount_rate'] = convert_sr_float(sr_tab.cell_value(row + 77, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 86, 1) == 'EMISSIONS INPUTS'  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 88, 1) == 'Grid Emissions'  # by Denton Gentry
            s['conv_annual_energy_used'] = convert_sr_float(sr_tab.cell_value(row + 89, 4))  # by Denton Gentry
            s['soln_energy_efficiency_factor'] = convert_sr_float(sr_tab.cell_value(row + 90, 4))  # by Denton Gentry
            s['soln_annual_energy_used'] = convert_sr_float(sr_tab.cell_value(row + 91, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 94, 1) == 'Fuel Emissions'  # by Denton Gentry
            s['conv_fuel_consumed_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 95, 4))  # by Denton Gentry
            s['soln_fuel_efficiency_factor'] = convert_sr_float(sr_tab.cell_value(row + 96, 4))  # by Denton Gentry
            s['conv_fuel_emissions_factor'] = convert_sr_float(sr_tab.cell_value(row + 97, 4))  # by Denton Gentry
            s['soln_fuel_emissions_factor'] = convert_sr_float(sr_tab.cell_value(row + 98, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 103, 1) == 'Direct Emissions'  # by Denton Gentry
            s['conv_emissions_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 105, 4))  # by Denton Gentry
            s['soln_emissions_per_funit'] = convert_sr_float(sr_tab.cell_value(row + 106, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 111, 1) == 'Indirect Emissions'  # by Denton Gentry
            s['conv_indirect_co2_per_unit'] = convert_sr_float(sr_tab.cell_value(row + 112, 4))  # by Denton Gentry
            s['soln_indirect_co2_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 113, 4))  # by Denton Gentry
            i_vs_f = str(sr_tab.cell_value(row + 114, 4)).lower().strip()  # by Denton Gentry
            s['conv_indirect_co2_is_iunits'] = False if i_vs_f == 'functional' else True  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 118, 1) == 'Optional Inputs'  # by Denton Gentry
            s['ch4_co2_per_twh'] = convert_sr_float(sr_tab.cell_value(row + 119, 4))  # by Denton Gentry
            s['ch4_is_co2eq'] = (sr_tab.cell_value(row + 119, 5) == 't CH4-CO2eq per TWh')  # by Denton Gentry
            s['n2o_co2_per_twh'] = convert_sr_float(sr_tab.cell_value(row + 120, 4))  # by Denton Gentry
            s['n2o_is_co2eq'] = (sr_tab.cell_value(row + 120, 5) == 't N2O-CO2eq per TWh')  # by Denton Gentry
            s['co2eq_conversion_source'] = str(sr_tab.cell_value(row + 121, 4)).strip()  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 124, 1) == 'General Climate Inputs'  # by Denton Gentry
            s['emissions_use_co2eq'] = convert_bool(sr_tab.cell_value(row + 125, 4))  # by Denton Gentry
            s['emissions_grid_source'] = str(sr_tab.cell_value(row + 126, 4)).strip()  # by Denton Gentry
            s['emissions_grid_range'] = str(sr_tab.cell_value(row + 127, 4)).strip()  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 135, 1) == 'TAM'  # by Denton Gentry
            s['source_until_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 4)))  # by Denton Gentry
            s['ref_source_post_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 7)))  # by Denton Gentry
            s['pds_source_post_2014'] = normalize_source_name(str(sr_tab.cell_value(row + 136, 10)))  # by Denton Gentry
            # by Denton Gentry
            s['pds_base_adoption'] = [  # by Denton Gentry
                ('World', convert_sr_float(sr_tab.cell_value(row + 151, 4))),  # by Denton Gentry
                ('OECD90', convert_sr_float(sr_tab.cell_value(row + 152, 4))),  # by Denton Gentry
                ('Eastern Europe', convert_sr_float(sr_tab.cell_value(row + 153, 4))),  # by Denton Gentry
                ('Asia (Sans Japan)', convert_sr_float(sr_tab.cell_value(row + 154, 4))),  # by Denton Gentry
                ('Middle East and Africa', convert_sr_float(sr_tab.cell_value(row + 155, 4))),  # by Denton Gentry
                ('Latin America', convert_sr_float(sr_tab.cell_value(row + 156, 4))),  # by Denton Gentry
                ('China', convert_sr_float(sr_tab.cell_value(row + 157, 4))),  # by Denton Gentry
                ('India', convert_sr_float(sr_tab.cell_value(row + 158, 4))),  # by Denton Gentry
                ('EU', convert_sr_float(sr_tab.cell_value(row + 159, 4))),  # by Denton Gentry
                ('USA', convert_sr_float(sr_tab.cell_value(row + 160, 4)))]  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 163, 1) == 'PDS ADOPTION SCENARIO INPUTS'  # by Denton Gentry
            s['soln_pds_adoption_basis'] = str(sr_tab.cell_value(row + 164, 4)).strip()  # by Denton Gentry
            s['soln_pds_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 165, 4))  # by Denton Gentry

            def percnt(r):
                return 0.0 if sr_tab.cell_value(r, 4) == '' else sr_tab.cell_value(r, 4)  # by Denton Gentry

            percentages = [('World', percnt(row + 170)), ('OECD90', percnt(row + 171)),  # by Denton Gentry
                           ('Eastern Europe', percnt(row + 172)), ('Asia (Sans Japan)', percnt(row + 173)),
                           # by Denton Gentry
                           ('Middle East and Africa', percnt(row + 174)), ('Latin America', percnt(row + 175)),
                           # by Denton Gentry
                           ('China', percnt(row + 176)), ('India', percnt(row + 177)),  # by Denton Gentry
                           ('EU', percnt(row + 178)), ('USA', percnt(row + 179))]  # by Denton Gentry
            s['pds_adoption_final_percentage'] = percentages  # by Denton Gentry
            # by Denton Gentry
            if s['soln_pds_adoption_basis'] == 'DEFAULT S-Curve':  # by Denton Gentry
                s_curve_type = str(sr_tab.cell_value(row + 181, 4))  # by Denton Gentry
                if s_curve_type == 'Alternate S-Curve (Bass Model)':  # by Denton Gentry
                    s['soln_pds_adoption_basis'] = 'Bass Diffusion S-Curve'  # by Denton Gentry
                    s['pds_adoption_s_curve_innovation'] = [  # by Denton Gentry
                        ('World', convert_sr_float(sr_tab.cell_value(row + 170, 6))),  # by Denton Gentry
                        ('OECD90', convert_sr_float(sr_tab.cell_value(row + 171, 6))),  # by Denton Gentry
                        ('Eastern Europe', convert_sr_float(sr_tab.cell_value(row + 172, 6))),  # by Denton Gentry
                        ('Asia (Sans Japan)', convert_sr_float(sr_tab.cell_value(row + 173, 6))),  # by Denton Gentry
                        ('Middle East and Africa', convert_sr_float(sr_tab.cell_value(row + 174, 6))),
                        # by Denton Gentry
                        ('Latin America', convert_sr_float(sr_tab.cell_value(row + 175, 6))),  # by Denton Gentry
                        ('China', convert_sr_float(sr_tab.cell_value(row + 176, 6))),  # by Denton Gentry
                        ('India', convert_sr_float(sr_tab.cell_value(row + 177, 6))),  # by Denton Gentry
                        ('EU', convert_sr_float(sr_tab.cell_value(row + 178, 6))),  # by Denton Gentry
                        ('USA', convert_sr_float(sr_tab.cell_value(row + 179, 6)))]  # by Denton Gentry
                    s['pds_adoption_s_curve_imitation'] = [  # by Denton Gentry
                        ('World', convert_sr_float(sr_tab.cell_value(row + 170, 7))),  # by Denton Gentry
                        ('OECD90', convert_sr_float(sr_tab.cell_value(row + 171, 7))),  # by Denton Gentry
                        ('Eastern Europe', convert_sr_float(sr_tab.cell_value(row + 172, 7))),  # by Denton Gentry
                        ('Asia (Sans Japan)', convert_sr_float(sr_tab.cell_value(row + 173, 7))),  # by Denton Gentry
                        ('Middle East and Africa', convert_sr_float(sr_tab.cell_value(row + 174, 7))),
                        # by Denton Gentry
                        ('Latin America', convert_sr_float(sr_tab.cell_value(row + 175, 7))),  # by Denton Gentry
                        ('China', convert_sr_float(sr_tab.cell_value(row + 176, 7))),  # by Denton Gentry
                        ('India', convert_sr_float(sr_tab.cell_value(row + 177, 7))),  # by Denton Gentry
                        ('EU', convert_sr_float(sr_tab.cell_value(row + 178, 7))),  # by Denton Gentry
                        ('USA', convert_sr_float(sr_tab.cell_value(row + 179, 7)))]  # by Denton Gentry
                elif s_curve_type == 'Default S-Curve (Logistic Model)':  # by Denton Gentry
                    s['soln_pds_adoption_basis'] = 'Logistic S-Curve'  # by Denton Gentry
                else:  # by Denton Gentry
                    raise ValueError('Unknown S-Curve:' + s_curve_type)  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 183, 1) == 'Existing PDS Prognostication Assumptions'  # by Denton Gentry
            adopt = normalize_source_name(str(sr_tab.cell_value(row + 184, 4)).strip())  # by Denton Gentry
            if adopt: s['soln_pds_adoption_prognostication_source'] = adopt  # by Denton Gentry
            adopt = str(sr_tab.cell_value(row + 185, 4)).strip()  # by Denton Gentry
            if adopt: s['soln_pds_adoption_prognostication_trend'] = adopt  # by Denton Gentry
            adopt = str(sr_tab.cell_value(row + 186, 4)).strip()  # by Denton Gentry
            if adopt: s['soln_pds_adoption_prognostication_growth'] = adopt  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 194, 1) == 'Fully Customized PDS'  # by Denton Gentry
            custom = str(sr_tab.cell_value(row + 195, 4)).strip()  # by Denton Gentry
            if custom:  # by Denton Gentry
                s['soln_pds_adoption_custom_name'] = custom  # by Denton Gentry
                if 'soln_pds_adoption_basis' not in s:  # sometimes row 164 is blank  # by Denton Gentry
                    s['soln_pds_adoption_basis'] = 'Fully Customized PDS'  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 198, 1) == 'REF ADOPTION SCENARIO INPUTS'  # by Denton Gentry
            adopt = str(sr_tab.cell_value(row + 199, 4)).strip()  # by Denton Gentry
            if adopt: s['soln_ref_adoption_basis'] = adopt  # by Denton Gentry
            custom = str(sr_tab.cell_value(row + 200, 4)).strip()  # by Denton Gentry
            if custom: s['soln_ref_adoption_custom_name'] = custom  # by Denton Gentry
            s['soln_ref_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 201, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 217, 1) == 'Adoption Adjustment'  # by Denton Gentry
            adjust = sr_tab.cell_value(row + 218, 4)  # by Denton Gentry
            if adjust and adjust != "(none)":  # by Denton Gentry
                s['pds_adoption_use_ref_years'] = [int(x) for x in adjust.split(',') if x is not '']  # by Denton Gentry
            adjust = sr_tab.cell_value(row + 219, 4)  # by Denton Gentry
            if adjust and adjust != "(none)":  # by Denton Gentry
                s['ref_adoption_use_pds_years'] = [int(x) for x in adjust.split(',') if x is not '']  # by Denton Gentry
            # by Denton Gentry
            # From Advanced Controls  # by Denton Gentry
            category = ac_tab.cell_value(*cell_to_offsets('A159'))  # by Denton Gentry
            if category: s['solution_category'] = category  # by Denton Gentry
            # by Denton Gentry
            row += 202  # by Denton Gentry
            scenarios[scenario_name] = s  # by Denton Gentry
    return scenarios  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def get_land_scenarios(wb):  # by Denton Gentry
    """Extract scenarios from a LAND Excel file.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         wb: Excel workbook returned by xlrd.  # by Denton Gentry
    """  # by Denton Gentry
    sr_tab = wb.sheet_by_name('ScenarioRecord')  # by Denton Gentry
    scenarios = {}  # by Denton Gentry
    for row in range(1, sr_tab.nrows):  # by Denton Gentry
        col_d = sr_tab.cell_value(row, 3)  # by Denton Gentry
        col_e = sr_tab.cell_value(row, 4)  # by Denton Gentry
        if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:  # by Denton Gentry
            # start of scenario block  # by Denton Gentry
            scenario_name = col_e  # by Denton Gentry
            s = {}  # by Denton Gentry
            # by Denton Gentry
            # Note: these cases are handled in oneline()
            s['solution_category'] = SOLUTION_CATEGORY.LAND  # by Denton Gentry
            s['vmas'] = 'VMAs'

            s['description'] = sr_tab.cell_value(row + 1, 4)
            report_years = sr_tab.cell_value(row + 2, 4)  # E:2 from top of scenario  # by Denton Gentry
            (start, end) = report_years.split('-')  # by Denton Gentry
            s['report_start_year'] = int(start)  # by Denton Gentry
            s['report_end_year'] = int(end)  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 201, 3) == 'Custom TLA Used?:'
            s['use_custom_tla'] = convert_bool(sr_tab.cell_value(row + 201, 4))

            assert sr_tab.cell_value(row + 230, 1) == 'PDS ADOPTION SCENARIO INPUTS'
            adopt = str(sr_tab.cell_value(row + 231, 4)).strip()
            if adopt: s['soln_pds_adoption_basis'] = adopt
            s['soln_pds_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 232, 4))

            def percnt(r):
                return 0.0 if sr_tab.cell_value(r, 4) == '' else sr_tab.cell_value(r, 4)

            percentages = [('World', percnt(row + 236)), ('OECD90', percnt(row + 237)),
                           ('Eastern Europe', percnt(row + 238)), ('Asia (Sans Japan)', percnt(row + 239)),

                           ('Middle East and Africa', percnt(row + 240)), ('Latin America', percnt(row + 241)),

                           ('China', percnt(row + 242)), ('India', percnt(row + 243)),
                           ('EU', percnt(row + 244)), ('USA', percnt(row + 245))]
            s['pds_adoption_final_percentage'] = percentages

            assert sr_tab.cell_value(row + 258, 1) == 'Fully Customized PDS'
            custom = str(sr_tab.cell_value(row + 259, 4)).strip()
            if custom:
                s['soln_pds_adoption_custom_name'] = custom
                if 'soln_pds_adoption_basis' not in s:  # sometimes row 164 is blank
                    s['soln_pds_adoption_basis'] = 'Fully Customized PDS'

            assert sr_tab.cell_value(row + 262, 1) == 'REF ADOPTION SCENARIO INPUTS'
            s['soln_ref_adoption_regional_data'] = convert_bool(sr_tab.cell_value(row + 265, 4))
            assert sr_tab.cell_value(row + 286, 1) == 'Adoption Adjustment'
            adjust = sr_tab.cell_value(row + 287, 4)
            if adjust and adjust != "(none)":
                s['pds_adoption_use_ref_years'] = [int(x) for x in adjust.split(',') if x is not '']
            adjust = sr_tab.cell_value(row + 288, 4)
            if adjust and adjust != "(none)":
                s['ref_adoption_use_pds_years'] = [int(x) for x in adjust.split(',') if x is not '']
            # TODO: handle soln_pds_adoption_prognostication_source

            assert sr_tab.cell_value(row + 54, 1) == 'Conventional'
            assert sr_tab.cell_value(row + 55, 3) == 'First Cost:'
            s['conv_2014_cost'] = link_vma(sr_tab.cell_value(row + 55, 4))
            s['conv_first_cost_efficiency_rate'] = 0.0  # always 0 for LAND models
            s['conv_fixed_oper_cost_per_iunit'] = link_vma(sr_tab.cell_value(row + 56, 4))
            s['conv_expected_lifetime'] = convert_sr_float(sr_tab.cell_value(row + 59, 4))
            s['yield_from_conv_practice'] = link_vma(sr_tab.cell_value(row + 60, 4))

            assert sr_tab.cell_value(row + 72, 1) == 'Solution'
            assert sr_tab.cell_value(row + 73, 3) == 'First Cost:'
            s['pds_2014_cost'] = s['ref_2014_cost'] = link_vma(sr_tab.cell_value(row + 73, 4))
            s['soln_first_cost_efficiency_rate'] = 0.0  # always 0 for LAND models
            s['soln_fixed_oper_cost_per_iunit'] = link_vma(sr_tab.cell_value(row + 74, 4))
            s['soln_expected_lifetime'] = convert_sr_float(sr_tab.cell_value(row + 77, 4))
            s['yield_gain_from_conv_to_soln'] = link_vma(sr_tab.cell_value(row + 78, 4))

            assert sr_tab.cell_value(row + 90, 1) == 'General'  # by Denton Gentry
            s['npv_discount_rate'] = convert_sr_float(sr_tab.cell_value(row + 91, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 156, 1) == 'General Emissions Inputs'  # by Denton Gentry
            s['emissions_use_co2eq'] = convert_bool(sr_tab.cell_value(row + 157, 4))  # by Denton Gentry
            s['emissions_use_agg_co2eq'] = convert_bool(sr_tab.cell_value(row + 158, 4))
            s['emissions_grid_source'] = str(sr_tab.cell_value(row + 159, 4))  # by Denton Gentry
            s['emissions_grid_range'] = str(sr_tab.cell_value(row + 160, 4))  # by Denton Gentry
            # by Denton Gentry
            assert sr_tab.cell_value(row + 144, 1) == 'Indirect Emissions'
            s['conv_indirect_co2_per_unit'] = convert_sr_float(sr_tab.cell_value(row + 145, 4))
            s['soln_indirect_co2_per_iunit'] = convert_sr_float(sr_tab.cell_value(row + 146, 4))
            # by Denton Gentry
            assert sr_tab.cell_value(row + 132, 1) == 'Direct Emissions'
            s['tco2eq_reduced_per_land_unit'] = link_vma(sr_tab.cell_value(row + 133, 4))
            s['tco2eq_rplu_rate'] = str(sr_tab.cell_value(row + 133, 7))
            s['tco2_reduced_per_land_unit'] = link_vma(sr_tab.cell_value(row + 134, 4))
            s['tco2_rplu_rate'] = str(sr_tab.cell_value(row + 134, 7))
            s['tn2o_co2_reduced_per_land_unit'] = link_vma(sr_tab.cell_value(row + 135, 4))
            s['tn2o_co2_rplu_rate'] = str(sr_tab.cell_value(row + 135, 7))
            s['tch4_co2_reduced_per_land_unit'] = link_vma(sr_tab.cell_value(row + 136, 4))
            s['tch4_co2_rplu_rate'] = str(sr_tab.cell_value(row + 136, 7))
            s['land_annual_emissons_lifetime'] = convert_sr_float(sr_tab.cell_value(row + 137, 4))  # by Denton Gentry

            assert sr_tab.cell_value(row + 109, 1) == 'Grid Emissions'  # by Denton Gentry
            s['conv_annual_energy_used'] = convert_sr_float(sr_tab.cell_value(row + 110, 4))  # by Denton Gentry
            s['soln_annual_energy_used'] = convert_sr_float(sr_tab.cell_value(row + 112, 4))  # by Denton Gentry

            assert sr_tab.cell_value(row + 168, 1) == 'Carbon Sequestration and Land Inputs'
            if sr_tab.cell(row + 169, 4).ctype == xlrd.XL_CELL_EMPTY:  # by Denton Gentry
                # Excel checks whether this cell == "" to trigger different handling. The best equivalent  # by Denton Gentry
                # in Python is to set it to NaN. We can distinguish None (not set) from NaN, and if  # by Denton Gentry
                # the value is ever inadvertantly used it will result in NaN.  # by Denton Gentry
                s['seq_rate_global'] = np.nan  # by Denton Gentry
                # by Denton Gentry
                if 'Variable Meta-analysis-DD' not in wb.sheet_names():  # by Denton Gentry
                    assert NotImplementedError(
                        'VMA Thermal-Moisture Regime sequestration not implemented')  # by Denton Gentry
                    # (4/2019) vma.py does have support for regimes in avg_high_low, it needs to be  # by Denton Gentry
                    # implemented in advanced_controls to pass a regime name through to vma.py  # by Denton Gentry
                # by Denton Gentry
                # For the public models using 'Variable Meta-analysis-DD', the DD tab does not contain  # by Denton Gentry
                # avg/high/low for the Thermal Moisture Regimes so we extract value from ScenarioRecord.  # by Denton Gentry
                s['seq_rate_per_regime'] = {  # by Denton Gentry
                    'Tropical-Humid': convert_sr_float(sr_tab.cell_value(row + 170, 4)),  # by Denton Gentry
                    'Temperate/Boreal-Humid': convert_sr_float(sr_tab.cell_value(row + 171, 4)),  # by Denton Gentry
                    'Tropical-Semi-Arid': convert_sr_float(sr_tab.cell_value(row + 172, 4)),  # by Denton Gentry
                    'Temperate/Boreal-Semi-Arid': convert_sr_float(sr_tab.cell_value(row + 173, 4)),  # by Denton Gentry
                    'Global Arid': convert_sr_float(sr_tab.cell_value(row + 174, 7)),  # by Denton Gentry
                    'Global Arctic': 0.0}  # by Denton Gentry
            else:  # by Denton Gentry
                s['seq_rate_global'] = link_vma(sr_tab.cell_value(row + 169, 4))  # by Denton Gentry
            if sr_tab.cell_value(row + 175, 3) == 'Growth Rate of Land Degradation':
                s['global_multi_for_regrowth'] = convert_sr_float(sr_tab.cell_value(row + 178, 4))
                s['degradation_rate'] = link_vma(sr_tab.cell_value(row + 175, 4))
            elif sr_tab.cell_value(row + 175,
                                   3) == 'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing':
                s['carbon_not_emitted_after_harvesting'] = link_vma(sr_tab.cell_value(row + 175, 4))

            s['disturbance_rate'] = link_vma(sr_tab.cell_value(row + 176, 4))
            # by Denton Gentry
            assert sr_tab.cell_value(row + 188, 1) == 'General Land Inputs'
            if sr_tab.cell_value(row + 189, 3) == 'Delay Impact of Protection by 1 Year? (Leakage)':
                s['delay_protection_1yr'] = convert_bool(sr_tab.cell_value(row + 189, 4))
                s['delay_regrowth_1yr'] = convert_bool(sr_tab.cell_value(row + 190, 4))
                s['include_unprotected_land_in_regrowth_calcs'] = convert_bool(
                    sr_tab.cell_value(row + 191, 4))
            elif sr_tab.cell_value(row + 189, 3) == 'New Growth is Harvested/Cleared Every':
                s['harvest_frequency'] = convert_sr_float(sr_tab.cell_value(row + 189, 4))
            scenarios[scenario_name] = s  # by Denton Gentry
    return scenarios  # by Denton Gentry
    # by Denton Gentry


def oneline(f, s, names, prefix='', suffix=None):  # by Denton Gentry
    """Format a set of outputs onto a single line.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         f: file-like object to write output to  # by Denton Gentry
         s: a dictionary loaded with values for the scenario we are processing.  # by Denton Gentry
         prefix: string to prepend to each line (typically, some number of spaces)  # by Denton Gentry
         suffix: string to append to the end of the line (typically, a newline)  # by Denton Gentry
    # by Denton Gentry
       This routine *removes* the dict elements in names from s before returning.  # by Denton Gentry
       The intent is that each call to oneline() both outputs a line of text and  # by Denton Gentry
       consumes the entries from s, so that at the end we can check if any  # by Denton Gentry
       unconsumed entries remain.  # by Denton Gentry
    """  # by Denton Gentry
    if not all(n in s for n in names):  # by Denton Gentry
        return  # by Denton Gentry
    f.write(prefix)  # by Denton Gentry
    for n in names:  # by Denton Gentry
        if n == 'vmas':  # by Denton Gentry
            f.write(n + "=" + s[n] + ", ")
        elif isinstance(s[n], SOLUTION_CATEGORY):  # by Denton Gentry
            f.write(n + "=" + str(s[n]) + ", ")  # by Denton Gentry
        elif isinstance(s[n], str):
            f.write(str(n) + "='" + str(s[n]) + "', ")
        elif isinstance(s[n], np.float) and np.isnan(s[n]):  # by Denton Gentry
            f.write(str(n) + "=np.nan, ")  # by Denton Gentry
        else:  # by Denton Gentry
            f.write(str(n) + "=" + str(s[n]) + ", ")
        del s[n]  # by Denton Gentry
    f.write('\n')  # by Denton Gentry
    if suffix:  # by Denton Gentry
        f.write(str(suffix))  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_scenario(f, s):  # by Denton Gentry
    """Write out the advanced_controls entries for a given scenario."""  # by Denton Gentry
    prefix = '      '  # by Denton Gentry
    # by Denton Gentry
    if 'description' in s:  # by Denton Gentry
        description = re.sub(r'\s+', ' ', s['description'])  # by Denton Gentry
        for line in textwrap.wrap(description, width=80):  # by Denton Gentry
            f.write(prefix + '# ' + line + '\n')  # by Denton Gentry
        del s['description']  # by Denton Gentry
        f.write('\n')
    # by Denton Gentry
    f.write(prefix + '# general' + '\n')
    oneline(f=f, s=s, names=['solution_category'], prefix=prefix)
    oneline(f=f, s=s, names=['vmas'], prefix=prefix)
    oneline(f=f, s=s, names=['report_start_year', 'report_end_year'], prefix=prefix)
    # by Denton Gentry
    if 'use_custom_tla' in s:
        f.write('\n' + prefix + '# TLA' + '\n')
        oneline(f=f, s=s, names=['use_custom_tla'], prefix=prefix)

    f.write('\n' + prefix + '# adoption' + '\n')
    oneline(f=f, s=s, names=['soln_ref_adoption_basis'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_ref_adoption_custom_name'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_ref_adoption_regional_data', 'soln_pds_adoption_regional_data'],
            prefix=prefix)
    oneline(f=f, s=s, names=['soln_pds_adoption_basis'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_pds_adoption_custom_name'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_source'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_trend'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_pds_adoption_prognostication_growth'], prefix=prefix)
    oneline(f=f, s=s, names=['ref_adoption_use_pds_years'], prefix=prefix)
    oneline(f=f, s=s, names=['pds_adoption_use_ref_years'], prefix=prefix)
    oneline(f=f, s=s, names=['source_until_2014'], prefix=prefix)
    oneline(f=f, s=s, names=['ref_source_post_2014'], prefix=prefix)
    oneline(f=f, s=s, names=['pds_source_post_2014'], prefix=prefix)
    oneline(f=f, s=s, names=['pds_base_adoption'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['pds_adoption_final_percentage'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['pds_adoption_s_curve_innovation'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['pds_adoption_s_curve_imitation'], prefix=prefix)  # by Denton Gentry

    f.write('\n' + prefix + '# financial' + '\n')
    oneline(f=f, s=s, names=['pds_2014_cost', 'ref_2014_cost'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['conv_2014_cost'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['soln_first_cost_efficiency_rate'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['conv_first_cost_efficiency_rate'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_first_cost_below_conv'], prefix=prefix)
    oneline(f=f, s=s, names=['npv_discount_rate'], prefix=prefix)
    # by Denton Gentry
    oneline(f=f, s=s, names=['soln_lifetime_capacity', 'soln_avg_annual_use'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['conv_lifetime_capacity', 'conv_avg_annual_use'], prefix=prefix,
            suffix='\n')
    oneline(f=f, s=s, names=['soln_expected_lifetime'], prefix=prefix)
    oneline(f=f, s=s, names=['conv_expected_lifetime'], prefix=prefix)
    oneline(f=f, s=s, names=['yield_from_conv_practice'], prefix=prefix)
    oneline(f=f, s=s, names=['yield_gain_from_conv_to_soln'], prefix=prefix, suffix='\n')
    # by Denton Gentry
    oneline(f=f, s=s, names=['soln_var_oper_cost_per_funit', 'soln_fuel_cost_per_funit'],
            prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['soln_fixed_oper_cost_per_iunit'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['conv_var_oper_cost_per_funit', 'conv_fuel_cost_per_funit'],
            prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['conv_fixed_oper_cost_per_iunit'], prefix=prefix)  # by Denton Gentry

    f.write('\n' + prefix + '# emissions' + '\n')
    oneline(f=f, s=s, names=['ch4_is_co2eq', 'n2o_is_co2eq'], prefix=prefix)
    oneline(f=f, s=s, names=['co2eq_conversion_source'], prefix=prefix)
    oneline(f=f, s=s, names=['soln_indirect_co2_per_iunit'], prefix=prefix)
    oneline(f=f, s=s, names=['conv_indirect_co2_per_unit'], prefix=prefix)
    oneline(f=f, s=s, names=['conv_indirect_co2_is_iunits'], prefix=prefix)
    oneline(f=f, s=s, names=['ch4_co2_per_twh', 'n2o_co2_per_twh'], prefix=prefix, suffix='\n')
    oneline(f=f, s=s, names=['soln_energy_efficiency_factor'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['soln_annual_energy_used', 'conv_annual_energy_used'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['conv_fuel_consumed_per_funit', 'soln_fuel_efficiency_factor'],
            prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['conv_fuel_emissions_factor', 'soln_fuel_emissions_factor'],  # by Denton Gentry
            prefix=prefix, suffix='\n')  # by Denton Gentry
    # by Denton Gentry
    oneline(f=f, s=s, names=['tco2eq_reduced_per_land_unit'], prefix='\n' + prefix)
    oneline(f=f, s=s, names=['tco2eq_rplu_rate'], prefix=prefix)
    oneline(f=f, s=s, names=['tco2_reduced_per_land_unit'], prefix=prefix)
    oneline(f=f, s=s, names=['tco2_rplu_rate'], prefix=prefix)
    oneline(f=f, s=s, names=['tn2o_co2_reduced_per_land_unit'], prefix=prefix)
    oneline(f=f, s=s, names=['tn2o_co2_rplu_rate'], prefix=prefix)
    oneline(f=f, s=s, names=['tch4_co2_reduced_per_land_unit'], prefix=prefix)
    oneline(f=f, s=s, names=['tch4_co2_rplu_rate'], prefix=prefix)
    oneline(f=f, s=s, names=['land_annual_emissons_lifetime'], prefix=prefix, suffix='\n')  # by Denton Gentry

    oneline(f=f, s=s, names=['emissions_grid_source', 'emissions_grid_range'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['emissions_use_co2eq'], prefix=prefix)  # by Denton Gentry
    oneline(f=f, s=s, names=['emissions_use_agg_co2eq'], prefix=prefix)
    oneline(f=f, s=s, names=['conv_emissions_per_funit', 'soln_emissions_per_funit'],  # by Denton Gentry
            prefix=prefix, suffix='\n')  # by Denton Gentry
    # by Denton Gentry
    if 'seq_rate_global' in s:
        f.write('\n' + prefix + '# sequestration' + '\n')
        oneline(f=f, s=s, names=['seq_rate_global'], prefix=prefix)
        oneline(f=f, s=s, names=['seq_rate_per_regime'], prefix=prefix)  # by Denton Gentry
        oneline(f=f, s=s, names=['global_multi_for_regrowth'], prefix=prefix)
        oneline(f=f, s=s, names=['degradation_rate'], prefix=prefix)
        oneline(f=f, s=s, names=['disturbance_rate'], prefix=prefix, suffix='\n')
        oneline(f=f, s=s, names=['delay_protection_1yr'], prefix=prefix)
        oneline(f=f, s=s, names=['delay_regrowth_1yr'], prefix=prefix)
        oneline(f=f, s=s, names=['include_unprotected_land_in_regrowth_calcs'], prefix=prefix)
        oneline(f=f, s=s, names=['harvest_frequency'], prefix=prefix)
        oneline(f=f, s=s, names=['carbon_not_emitted_after_harvesting'], prefix=prefix)
        f.write('\n')

    # by Denton Gentry


def xls(tab, row, col):  # by Denton Gentry
    """Return a quoted string read from tab(row, col)."""  # by Denton Gentry
    cell = tab.cell(row, col)  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_ERROR or cell.ctype == xlrd.XL_CELL_EMPTY:  # by Denton Gentry
        return ''  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_TEXT or cell.ctype == xlrd.XL_CELL_NUMBER:  # by Denton Gentry
        return "'" + str(cell.value).strip() + "'"  # by Denton Gentry
    raise ValueError(
        "Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))  # by Denton Gentry
    # by Denton Gentry


def xln(tab, row, col):  # by Denton Gentry
    """Return the string of a floating point number read from tab(row, col)."""  # by Denton Gentry
    cell = tab.cell(row, col)  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_ERROR:  # by Denton Gentry
        return 'np.nan'  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_NUMBER:  # by Denton Gentry
        return str(cell.value)  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_EMPTY:  # by Denton Gentry
        return '0.0'  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_TEXT and cell.value == '':  # by Denton Gentry
        return '0.0'  # by Denton Gentry
    raise ValueError(
        "Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))  # by Denton Gentry
    # by Denton Gentry


def xli(tab, row, col):  # by Denton Gentry
    """Return the string of an integer value read from tab(row, col)."""  # by Denton Gentry
    cell = tab.cell(row, col)  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_ERROR:  # by Denton Gentry
        return 'np.nan'  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_TEXT or cell.ctype == xlrd.XL_CELL_NUMBER:  # by Denton Gentry
        return str(int(cell.value))  # by Denton Gentry
    if cell.ctype == xlrd.XL_CELL_EMPTY:  # by Denton Gentry
        return '0'  # by Denton Gentry
    raise ValueError(
        "Unhandled cell ctype: " + str(cell.ctype) + " at r=" + str(row) + " c=" + str(col))  # by Denton Gentry
    # by Denton Gentry


def recursive_keys(sources):  # by Denton Gentry
    result = {}  # by Denton Gentry
    for k in sources.keys():  # by Denton Gentry
        try:  # by Denton Gentry
            value = recursive_keys(sources[k])  # by Denton Gentry
        except AttributeError:  # by Denton Gentry
            value = None  # by Denton Gentry
        result[k] = value  # by Denton Gentry
    return result  # by Denton Gentry
    # by Denton Gentry


def abandon_files(sources, outputdir):  # by Denton Gentry
    """We're not going to use the extracted files after all, remove them."""  # by Denton Gentry
    for (key, filename) in sources.items():  # by Denton Gentry
        try:  # by Denton Gentry
            abandon_files(sources=sources[key], outputdir=outputdir)  # by Denton Gentry
        except AttributeError:  # by Denton Gentry
            try:  # by Denton Gentry
                fullpath = os.path.join(outputdir, filename)  # by Denton Gentry
                os.unlink(fullpath)  # by Denton Gentry
            except FileNotFoundError:  # by Denton Gentry
                pass  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_tam(f, wb, outputdir):  # by Denton Gentry
    """Generate the TAM section of a solution.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         f - file-like object for output  # by Denton Gentry
         wb - an Excel workbook as returned by xlrd  # by Denton Gentry
         outputdir: name of directory to write CSV files to.  # by Denton Gentry
    """  # by Denton Gentry
    tm_tab = wb.sheet_by_name('TAM Data')  # by Denton Gentry
    f.write("    tamconfig_list = [\n")  # by Denton Gentry
    f.write(
        "      ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")  # by Denton Gentry
    f.write("       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")  # by Denton Gentry
    f.write("      ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,\n")  # by Denton Gentry
    f.write("       " + xls(tm_tab, 15, 21) + ", " + xls(tm_tab, 18, 21) + ", " + xls(tm_tab, 21,
                                                                                      21) + ", ")  # by Denton Gentry
    f.write(xls(tm_tab, 24, 21) + ", " + xls(tm_tab, 27, 21) + ", " + xls(tm_tab, 30, 21) + ",\n")  # by Denton Gentry
    f.write("       " + xls(tm_tab, 33, 21) + ", " + xls(tm_tab, 36, 21) + ", " + xls(tm_tab, 39,
                                                                                      21) + "],\n")  # by Denton Gentry
    f.write(
        "      ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,\n")  # by Denton Gentry
    f.write("       " + xls(tm_tab, 15, 21) + ", " + xls(tm_tab, 18, 21) + ", " + xls(tm_tab, 21,
                                                                                      21) + ", ")  # by Denton Gentry
    f.write(xls(tm_tab, 24, 21) + ", " + xls(tm_tab, 27, 21) + ", " + xls(tm_tab, 30, 21) + ",\n")  # by Denton Gentry
    f.write("       " + xls(tm_tab, 33, 21) + ", " + xls(tm_tab, 36, 21) + ", " + xls(tm_tab, 39,
                                                                                      21) + "],\n")  # by Denton Gentry
    # One might assume PDS_World for trend and growth would use self.ac.soln_pds_adoption_prognostication_*,  # by Denton Gentry
    # but that is not what the TAM Data in Excel does. EA104 references B19 and C19, the World trend and growth.  # by Denton Gentry
    f.write("      ['trend', " + xls(tm_tab, 18, 1) + ", " + xls(tm_tab, 18, 1) + ",\n")  # by Denton Gentry
    f.write("       " + xls(tm_tab, 16, 11) + ", " + xls(tm_tab, 19, 11) + ", " + xls(tm_tab, 22,
                                                                                      11) + ", ")  # by Denton Gentry
    f.write(xls(tm_tab, 25, 11) + ", " + xls(tm_tab, 28, 11) + ", " + xls(tm_tab, 31, 11) + ",\n")  # by Denton Gentry
    f.write("       " + xls(tm_tab, 34, 11) + ", " + xls(tm_tab, 37, 11) + ", " + xls(tm_tab, 40,
                                                                                      11) + "],\n")  # by Denton Gentry
    f.write("      ['growth', " + xls(tm_tab, 18, 2) + ", " + xls(tm_tab, 18, 2) + ", " + xls(tm_tab, 16,
                                                                                              12) + ", ")  # by Denton Gentry
    f.write(xls(tm_tab, 19, 12) + ",\n")  # by Denton Gentry
    f.write("       " + xls(tm_tab, 22, 12) + ", " + xls(tm_tab, 25, 12) + ", " + xls(tm_tab, 28,
                                                                                      12) + ", ")  # by Denton Gentry
    f.write(xls(tm_tab, 31, 12) + ", " + xls(tm_tab, 34, 12) + ", " + xls(tm_tab, 37, 12) + ", ")  # by Denton Gentry
    f.write(xls(tm_tab, 40, 12) + "],\n")  # by Denton Gentry
    f.write("      ['low_sd_mult', " + xln(tm_tab, 24, 1) + ", " + xln(tm_tab, 24, 1) + ", ")  # by Denton Gentry
    f.write(xln(tm_tab, 16, 16) + ", " + xln(tm_tab, 19, 16) + ", " + xln(tm_tab, 22, 16) + ", ")  # by Denton Gentry
    f.write(xln(tm_tab, 25, 16) + ", " + xln(tm_tab, 28, 16) + ", " + xln(tm_tab, 31, 16) + ", ")  # by Denton Gentry
    f.write(xln(tm_tab, 34, 16) + ", " + xln(tm_tab, 37, 16) + ", " + xln(tm_tab, 40, 16) + "],\n")  # by Denton Gentry
    f.write("      ['high_sd_mult', " + xln(tm_tab, 23, 1) + ", " + xln(tm_tab, 23, 1) + ", ")  # by Denton Gentry
    f.write(xln(tm_tab, 15, 16) + ", " + xln(tm_tab, 18, 16) + ", " + xln(tm_tab, 21, 16) + ", ")  # by Denton Gentry
    f.write(xln(tm_tab, 24, 16) + ", " + xln(tm_tab, 27, 16) + ", " + xln(tm_tab, 30, 16) + ", ")  # by Denton Gentry
    f.write(xln(tm_tab, 33, 16) + ", " + xln(tm_tab, 36, 16) + ", " + xln(tm_tab, 39, 16) + "]]\n")  # by Denton Gentry
    f.write(
        "    tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0], dtype=np.object).set_index('param')\n")  # by Denton Gentry
    # by Denton Gentry
    tam_regions = {'World': 44, 'OECD90': 162, 'Eastern Europe': 226,  # by Denton Gentry
                   'Asia (Sans Japan)': 289, 'Middle East and Africa': 352, 'Latin America': 415,  # by Denton Gentry
                   'China': 478, 'India': 542, 'EU': 606, 'USA': 671}  # by Denton Gentry
    ref_sources = extract_source_data(wb=wb, sheet_name='TAM Data', regions=tam_regions,  # by Denton Gentry
                                      outputdir=outputdir, prefix='tam_')  # by Denton Gentry
    if recursive_keys(ref_sources) == recursive_keys(rrs.tam_ref_data_sources):  # by Denton Gentry
        arg_ref = 'rrs.tam_ref_data_sources'  # by Denton Gentry
        abandon_files(ref_sources, outputdir=outputdir)  # by Denton Gentry
    else:  # by Denton Gentry
        f.write("    tam_ref_data_sources = {\n")  # by Denton Gentry
        for region, cases in ref_sources.items():  # by Denton Gentry
            f.write("      '" + region + "': {\n")  # by Denton Gentry
            for (case, sources) in cases.items():  # by Denton Gentry
                if isinstance(sources, str):  # by Denton Gentry
                    f.write("          '" + case + "': THISDIR.joinpath('" + sources + "'),\n")
                else:  # by Denton Gentry
                    f.write("        '" + case + "': {\n")  # by Denton Gentry
                    for (source, filename) in sources.items():  # by Denton Gentry
                        f.write("          '" + source + "': THISDIR.joinpath('" + filename + "'),\n")
                    f.write("        },\n")  # by Denton Gentry
            f.write("      },\n")  # by Denton Gentry
        f.write("    }\n")  # by Denton Gentry
        arg_ref = 'tam_ref_data_sources'  # by Denton Gentry
    # by Denton Gentry
    tam_regions = {'World': 102}  # by Denton Gentry
    pds_sources = extract_source_data(wb=wb, sheet_name='TAM Data', regions=tam_regions,  # by Denton Gentry
                                      outputdir=outputdir, prefix='tam_pds_')  # by Denton Gentry
    if recursive_keys(pds_sources) == recursive_keys(rrs.tam_pds_data_sources):  # by Denton Gentry
        arg_pds = 'rrs.tam_pds_data_sources'  # by Denton Gentry
        abandon_files(pds_sources, outputdir=outputdir)  # by Denton Gentry
    elif recursive_keys(pds_sources) == recursive_keys(rrs.tam_ref_data_sources):  # by Denton Gentry
        arg_pds = 'rrs.tam_ref_data_sources'  # by Denton Gentry
        abandon_files(pds_sources, outputdir=outputdir)  # by Denton Gentry
    elif not pds_sources:  # by Denton Gentry
        arg_pds = 'tam_ref_data_sources'  # by Denton Gentry
    else:  # by Denton Gentry
        f.write("    tam_pds_data_sources = {\n")  # by Denton Gentry
        for region, cases in pds_sources.items():  # by Denton Gentry
            f.write("      '" + region + "': {\n")  # by Denton Gentry
            for (case, sources) in cases.items():  # by Denton Gentry
                if isinstance(sources, str):  # by Denton Gentry
                    f.write("          '" + case + "': THISDIR.joinpath('" + sources + "'),\n")
                else:  # by Denton Gentry
                    f.write("        '" + case + "': {\n")  # by Denton Gentry
                    for (source, filename) in sources.items():  # by Denton Gentry
                        f.write("          '" + source + "': THISDIR.joinpath('" + filename + "'),\n")
                    f.write("        },\n")  # by Denton Gentry
            f.write("      },\n")  # by Denton Gentry
        f.write("    }\n")  # by Denton Gentry
        arg_pds = 'tam_pds_data_sources'  # by Denton Gentry
    # by Denton Gentry
    regional = convert_bool(tm_tab.cell(28, 1).value) and convert_bool(tm_tab.cell(29, 1).value)  # by Denton Gentry
    f.write("    self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=" + arg_ref + ",\n")  # by Denton Gentry
    if regional:  # by Denton Gentry
        f.write("      world_includes_regional=True,\n")  # by Denton Gentry
    f.write("      tam_pds_data_sources=" + arg_pds + ")\n")  # by Denton Gentry
    f.write("    ref_tam_per_region=self.tm.ref_tam_per_region()\n")  # by Denton Gentry
    f.write("    pds_tam_per_region=self.tm.pds_tam_per_region()\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def normalize_source_name(sourcename):  # by Denton Gentry
    """Return a common name for widely used studies.  # by Denton Gentry
       Correct mis-spelings and inconsistencies in the column names.  # by Denton Gentry
       A few solution files, notably OnshoreWind, are inconsistent about the ordering  # by Denton Gentry
       of columns between different regions, and additionally use inconsistent names  # by Denton Gentry
       and some spelling errors. We need the column names to be consistent to properly  # by Denton Gentry
       combine them.  # by Denton Gentry
    # by Denton Gentry
       World  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       |   Baseline Cases  |  Ambitious Cases  |     Conservative Cases      |100% REN |  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       | source1 | source2 | source3 | source4 | source5 | source6 | source7 | source8 |  # by Denton Gentry
    # by Denton Gentry
       OECD90  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       |   Baseline Cases  |  Ambitious Cases  |     Conservative Cases      |100% REN |  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       | source2 | source1 | source3 | Source 4| surce5  | source6 | source7 | source8 |  # by Denton Gentry
    """  # by Denton Gentry
    special_cases = {  # by Denton Gentry
        'Based on: Greenpeace (2015) Reference': 'Based on: Greenpeace 2015 Reference',  # by Denton Gentry
        'Greenpeace 2015 Reference Scenario': 'Based on: Greenpeace 2015 Reference',  # by Denton Gentry
        'Based on Greenpeace 2015 Reference Scenario': 'Based on: Greenpeace 2015 Reference',  # by Denton Gentry
        'Based on Greenpeace 2015 Reference': 'Based on: Greenpeace 2015 Reference',  # by Denton Gentry
        'Conservative: Based on- Greenpeace 2015 Reference': 'Based on: Greenpeace 2015 Reference',  # by Denton Gentry
        '100% REN: Based on- Greenpeace Advanced [R]evolution': 'Based on: Greenpeace 2015 Advanced Revolution',
        # by Denton Gentry
        'Drawdown TAM: Baseline Cases': 'Baseline Cases',  # by Denton Gentry
        'Drawdown TAM: Conservative Cases': 'Conservative Cases',  # by Denton Gentry
        'Drawdown TAM: Ambitious Cases': 'Ambitious Cases',  # by Denton Gentry
        'Drawdown TAM: Maximum Cases': 'Maximum Cases',  # by Denton Gentry
        'Drawdown Projections based on adjusted IEA data (ETP 2012) on projected growth in each year, and recent sales Data (IEA - ETP 2016)':  # by Denton Gentry
    'Drawdown Projections based on adjusted IEA data (ETP 2012) on projected growth in each year, and recent sales Data (IEA - ETP 2016)',  # by Denton Gentry
    'ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - Baseline Scenario':  # by Denton Gentry
    'ITDP/UC Davis 2014 Global High Shift Baseline',  # by Denton Gentry
    'ITDP/UC Davis (2014)  A Global High Shift Scenario Updated Report Data - HighShift Scenario':  # by Denton Gentry
    'ITDP/UC Davis 2014 Global High Shift HighShift',  # by Denton Gentry
    'What a Waste: A Global Review of Solid Waste Management (Hoornweg, 2012) - Static % of Organic Waste':  # by Denton Gentry
    'What a Waste Solid Waste Management Static',  # by Denton Gentry
    'What a Waste: A Global Review of Solid Waste Management (Hoornweg, 2012) - Dynamic % of Organic Waste':  # by Denton Gentry
    'What a Waste Solid Waste Management Dynamic',  # by Denton Gentry
    'What a Waste: A Global Review of Solid Waste Management (Hoornweg, 2012) - Dynamic Organic Fraction by Un Mediam Variant':  # by Denton Gentry
    'What a Waste Solid Waste Management Dynamic Organic Fraction',  # by Denton Gentry
    'IPCC, 2006 - Calculated': 'IPCC, 2006 Calculated',  # by Denton Gentry
    "Combined from IEA (2016) ETP 2016, ICAO (2014) Annual Report 2014, Appendix 1, Boeing (2013) World Air cargo Forecast 2014-2015, Airbus (2014) Global market Forecast: Flying by the Numbers 2015-2034 - Highest Ranges": 'Combined from IEA ETP 2016, ICAO 2014, Boeing 2013, Airbus 2014, Highest Ranges',  # by Denton Gentry
    "Combined from IEA (2016) ETP 2016, ICAO (2014) Annual Report 2014, Appendix 1, Boeing (2013) World Air cargo Forecast 2014-2015, Airbus (2014) Global market Forecast: Flying by the Numbers 2015-2034 - Middle Ranges": 'Combined from IEA ETP 2016, ICAO 2014, Boeing 2013, Airbus 2014, Middle Ranges',  # by Denton Gentry
    "Combined from IEA (2016) ETP 2016, ICAO (2014) Annual Report 2014, Appendix 1, Boeing (2013) World Air cargo Forecast 2014-2015, Airbus (2014) Global market Forecast: Flying by the Numbers 2015-2034 - Lowest Ranges": 'Combined from IEA ETP 2016, ICAO 2014, Boeing 2013, Airbus 2014, Lowest Ranges',  # by Denton Gentry
    }  # by Denton Gentry
    normalized = sourcename.replace("'", "").replace('\n', ' ').strip()  # by Denton Gentry
    if normalized in special_cases:  # by Denton Gentry
        return special_cases[normalized]  # by Denton Gentry
    if re.search('\[Source \d+', sourcename):  # by Denton Gentry
        return None  # by Denton Gentry
    # by Denton Gentry
    name = re.sub(r"[\[\]]", "", sourcename.upper())  # [R]evolution to REVOLUTION  # by Denton Gentry
    if 'UN CES' in name and 'ITU' in name and 'AMPERE' in name:  # by Denton Gentry
        if 'BASELINE' in name: return 'Based on: CES ITU AMPERE Baseline'  # by Denton Gentry
        if '550' in name: return 'Based on: CES ITU AMPERE 550'  # by Denton Gentry
        if '450' in name: return 'Based on: CES ITU AMPERE 450'  # by Denton Gentry
        raise ValueError('Unknown UN CES ITU AMPERE source: ' + sourcename)  # by Denton Gentry
    if 'IEA' in name and 'ETP' in name:  # by Denton Gentry
        if '2016' in name and '6DS' in name: return 'Based on: IEA ETP 2016 6DS'  # by Denton Gentry
        if '2016' in name and '4DS' in name: return 'Based on: IEA ETP 2016 4DS'  # by Denton Gentry
        if '2016' in name and '2DS' in name and 'OPT2-PERENNIALS' in name:  # by Denton Gentry
            return 'Based on: IEA ETP 2016 2DS with OPT2 perennials'  # by Denton Gentry
        if '2016' in name and '2DS' in name: return 'Based on: IEA ETP 2016 2DS'  # by Denton Gentry
        if '2017' in name and 'REF' in name: return 'Based on: IEA ETP 2017 Ref Tech'  # by Denton Gentry
        if '2017' in name and 'B2DS' in name: return 'Based on: IEA ETP 2017 B2DS'  # by Denton Gentry
        if '2017' in name and '2DS' in name: return 'Based on: IEA ETP 2017 2DS'  # by Denton Gentry
        if '2017' in name and '4DS' in name: return 'Based on: IEA ETP 2017 4DS'  # by Denton Gentry
        if '2017' in name and '6DS' in name: return 'Based on: IEA ETP 2017 6DS'  # by Denton Gentry
        raise ValueError('Unknown IEA ETP source: ' + sourcename)  # by Denton Gentry
    if 'AMPERE' in name and 'MESSAGE' in name:  # by Denton Gentry
        if '450' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO 450'  # by Denton Gentry
        if '550' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO 550'  # by Denton Gentry
        if 'REF' in name: return 'Based on: AMPERE 2014 MESSAGE MACRO Reference'  # by Denton Gentry
        raise ValueError('Unknown AMPERE MESSAGE-MACRO source: ' + sourcename)  # by Denton Gentry
    if 'AMPERE' in name and 'IMAGE' in name:  # by Denton Gentry
        if '450' in name: return 'Based on: AMPERE 2014 IMAGE TIMER 450'  # by Denton Gentry
        if '550' in name: return 'Based on: AMPERE 2014 IMAGE TIMER 550'  # by Denton Gentry
        if 'REF' in name: return 'Based on: AMPERE 2014 IMAGE TIMER Reference'  # by Denton Gentry
        raise ValueError('Unknown AMPERE IMAGE-TIMER source: ' + sourcename)  # by Denton Gentry
    if 'AMPERE' in name and 'GEM' in name and 'E3' in name:  # by Denton Gentry
        if '450' in name: return 'Based on: AMPERE 2014 GEM E3 450'  # by Denton Gentry
        if '550' in name: return 'Based on: AMPERE 2014 GEM E3 550'  # by Denton Gentry
        if 'REF' in name: return 'Based on: AMPERE 2014 GEM E3 Reference'  # by Denton Gentry
        raise ValueError('Unknown AMPERE GEM E3 source: ' + sourcename)  # by Denton Gentry
    if 'GREENPEACE' in name and 'ENERGY' in name:  # by Denton Gentry
        if 'ADVANCED' in name and 'DRAWDOWN-PERENNIALS' in name:  # by Denton Gentry
            return 'Based on: Greenpeace 2015 Advanced Revolution with Drawdown perennials'  # by Denton Gentry
        if 'ADVANCED' in name: return 'Based on: Greenpeace 2015 Advanced Revolution'  # by Denton Gentry
        if 'REVOLUTION' in name and 'DRAWDOWN-PERENNIALS' in name:  # by Denton Gentry
            return 'Based on: Greenpeace 2015 Energy Revolution with Drawdown perennials'  # by Denton Gentry
        if 'REVOLUTION' in name: return 'Based on: Greenpeace 2015 Energy Revolution'  # by Denton Gentry
        if 'REFERENCE' in name: return 'Based on: Greenpeace 2015 Reference'  # by Denton Gentry
        raise ValueError('Unknown Greenpeace Energy source: ' + sourcename)  # by Denton Gentry
    if 'GREENPEACE' in name and 'THERMAL' in name:  # by Denton Gentry
        if 'MODERATE' in name: return 'Based on: Greenpeace 2016 Solar Thermal Moderate'  # by Denton Gentry
        if 'ADVANCED' in name: return 'Based on: Greenpeace 2016 Solar Thermal Advanced'  # by Denton Gentry
        raise ValueError('Unknown Greenpeace Solar Thermal source: ' + sourcename)  # by Denton Gentry
    return normalized  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def normalize_case_name(name):  # by Denton Gentry
    rewrites = {  # by Denton Gentry
        'Drawdown TAM: Baseline Cases': 'Baseline Cases',  # by Denton Gentry
        'Drawdown TAM: Conservative Cases': 'Conservative Cases',  # by Denton Gentry
        'Drawdown TAM: Ambitious Cases': 'Ambitious Cases',  # by Denton Gentry
        'Drawdown TAM: Maximum Cases': 'Maximum Cases',  # by Denton Gentry
    }  # by Denton Gentry
    return rewrites.get(name, name)  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def get_filename_for_source(sourcename, prefix=''):  # by Denton Gentry
    """Return string to use for the filename for known sources."""  # by Denton Gentry
    if re.search(r'\[Source \d+', sourcename):  # by Denton Gentry
        return None  # by Denton Gentry
    if re.search(r'Drawdown TAM: \[Source \d+', sourcename):  # by Denton Gentry
        return None  # by Denton Gentry
    # by Denton Gentry
    filename = re.sub(r"[^\w\s\.]", '', sourcename)  # by Denton Gentry
    filename = re.sub(r"\s+", '_', filename)  # by Denton Gentry
    filename = re.sub(r"\.+", '_', filename)  # by Denton Gentry
    filename = filename.replace('Based_on_', 'based_on_')  # by Denton Gentry
    if len(filename) > 63:  # by Denton Gentry
        s = filename[63:]  # by Denton Gentry
        h = hex(abs(hash(s)))[-8:]  # by Denton Gentry
        filename = filename[:63] + h  # by Denton Gentry
    return prefix + filename + '.csv'  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_ad(f, wb, outputdir):  # by Denton Gentry
    """Generate the Adoption Data section of a solution.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         f - file-like object for output  # by Denton Gentry
         wb - an Excel workbook as returned by xlrd  # by Denton Gentry
         outputdir: name of directory to write CSV files to.  # by Denton Gentry
    """  # by Denton Gentry
    a = wb.sheet_by_name('Adoption Data')  # by Denton Gentry
    f.write("    adconfig_list = [\n")  # by Denton Gentry
    f.write("      ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',\n")  # by Denton Gentry
    f.write("       'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],\n")  # by Denton Gentry
    f.write("      ['trend', self.ac.soln_pds_adoption_prognostication_trend, ")  # by Denton Gentry
    f.write(xls(a, 16, 11) + ",\n")  # by Denton Gentry
    f.write("       " + xls(a, 19, 11) + ", " + xls(a, 22, 11) + ", ")  # by Denton Gentry
    f.write(xls(a, 25, 11) + ", " + xls(a, 28, 11) + ", ")  # by Denton Gentry
    f.write(xls(a, 31, 11) + ",\n")  # by Denton Gentry
    f.write("       " + xls(a, 34, 11) + ", " + xls(a, 37, 11) + ", ")  # by Denton Gentry
    f.write(xls(a, 40, 11) + "],\n")  # by Denton Gentry
    f.write("      ['growth', self.ac.soln_pds_adoption_prognostication_growth, ")  # by Denton Gentry
    f.write(xls(a, 16, 12) + ",\n")  # by Denton Gentry
    f.write("       " + xls(a, 19, 12) + ", " + xls(a, 22, 12) + ", " + xls(a, 25, 12) + ", ")  # by Denton Gentry
    f.write(xls(a, 28, 12) + ", " + xls(a, 31, 12) + ",\n")  # by Denton Gentry
    f.write("       " + xls(a, 34, 12) + ", " + xls(a, 37, 12) + ", " + xls(a, 40, 12) + "],\n")  # by Denton Gentry
    f.write("      ['low_sd_mult', " + xln(a, 24, 1) + ", " + xln(a, 16, 16) + ", ")  # by Denton Gentry
    f.write(xln(a, 19, 16) + ", " + xln(a, 22, 16) + ", " + xln(a, 25, 16) + ", ")  # by Denton Gentry
    f.write(xln(a, 28, 16) + ", " + xln(a, 31, 16) + ", " + xln(a, 34, 16) + ", ")  # by Denton Gentry
    f.write(xln(a, 37, 16) + ", " + xln(a, 40, 16) + "],\n")  # by Denton Gentry
    f.write("      ['high_sd_mult', " + xln(a, 23, 1) + ", " + xln(a, 15, 16) + ", ")  # by Denton Gentry
    f.write(xln(a, 18, 16) + ", " + xln(a, 21, 16) + ", " + xln(a, 24, 16) + ", ")  # by Denton Gentry
    f.write(xln(a, 27, 16) + ", " + xln(a, 30, 16) + ", " + xln(a, 33, 16) + ", ")  # by Denton Gentry
    f.write(xln(a, 36, 16) + ", " + xln(a, 39, 16) + "]]\n")  # by Denton Gentry
    f.write(
        "    adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0], dtype=np.object).set_index('param')\n")  # by Denton Gentry
    ad_regions = {'World': 44, 'OECD90': 104, 'Eastern Europe': 168, 'Asia (Sans Japan)': 231,  # by Denton Gentry
                  'Middle East and Africa': 294, 'Latin America': 357, 'China': 420, 'India': 484, 'EU': 548,
                  # by Denton Gentry
                  'USA': 613}  # by Denton Gentry
    sources = extract_source_data(wb=wb, sheet_name='Adoption Data', regions=ad_regions,  # by Denton Gentry
                                  outputdir=outputdir, prefix='ad_')  # by Denton Gentry
    f.write("    ad_data_sources = {\n")  # by Denton Gentry
    for region, cases in sources.items():  # by Denton Gentry
        f.write("      '" + region + "': {\n")  # by Denton Gentry
        for (case, sources) in cases.items():  # by Denton Gentry
            if isinstance(sources, str):  # by Denton Gentry
                f.write("          '" + case + "': THISDIR.joinpath('" + sources + "'),\n")
            else:  # by Denton Gentry
                f.write("        '" + case + "': {\n")  # by Denton Gentry
                for (source, filename) in sources.items():  # by Denton Gentry
                    f.write("          '" + source + "': THISDIR.joinpath('" + filename + "'),\n")
                f.write("        },\n")  # by Denton Gentry
        f.write("      },\n")  # by Denton Gentry
    f.write("    }\n")  # by Denton Gentry
    f.write("    self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,\n")  # by Denton Gentry
    regional = convert_bool(a.cell(29, 1).value) and convert_bool(a.cell(30, 1).value)  # by Denton Gentry
    if regional:  # by Denton Gentry
        f.write("        world_includes_regional=True,\n")  # by Denton Gentry
    f.write("        adconfig=adconfig)\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_custom_ad(case, f, wb, outputdir, is_land):  # by Denton Gentry
    """Generate the Custom Adoption Data section of a solution.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         case: 'PDS' or 'REF'  # by Denton Gentry
         f: file-like object for output  # by Denton Gentry
         wb: an Excel workbook as returned by xlrd  # by Denton Gentry
         outputdir: name of directory to write CSV files to.  # by Denton Gentry
         is_land: boolean of whether this is a Land solution  # by Denton Gentry
    """  # by Denton Gentry
    f.write("    # Custom {} Data\n".format(case))
    if outputdir is None:
        f.write("    # no output dir specified for custom {} adoption\n\n".format(case))
        return
    assert case == 'REF' or case == 'PDS', 'write_custom_ad case must be PDS or REF: ' + str(case)

    ca_dir_path = os.path.join(outputdir, 'ca_{}_data'.format(case.lower()))  # by Denton Gentry
    if not os.path.exists(ca_dir_path):
        os.mkdir(ca_dir_path)
    scenarios, multipliers = extract_custom_adoption(wb=wb, outputdir=ca_dir_path,
                                                     sheet_name='Custom {} Adoption'.format(case),
                                                     prefix='custom_{}_ad_'.format(case.lower()))
    f.write("    ca_{}_data_sources = [\n".format(case.lower()))
    # by Denton Gentry
    for s in scenarios:  # by Denton Gentry
        f.write(
            "      {'name': '" + s['name'].strip() + "', 'include': " + str(s['include']) + ",\n")  # by Denton Gentry
        f.write("          'filename': THISDIR.joinpath({})}},\n".format(
            "'ca_{}_data', '{}'".format(case.lower(), s['filename'])))
    f.write("    ]\n")  # by Denton Gentry
    # by Denton Gentry
    if case == 'REF':  # by Denton Gentry
        f.write(
            "    self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,\n")  # by Denton Gentry
        f.write("        soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,\n")
        f.write("        high_sd_mult={}, low_sd_mult={},\n".format(multipliers['high'],
                                                                    multipliers['low']))  # by Denton Gentry
        if is_land:  # by Denton Gentry
            f.write("        total_adoption_limit=self.tla_per_region)\n")  # by Denton Gentry
        else:  # by Denton Gentry
            f.write("        total_adoption_limit=ref_tam_per_region)\n")  # by Denton Gentry
    if case == 'PDS':  # by Denton Gentry
        f.write(
            "    self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,\n")  # by Denton Gentry
        f.write("        soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,\n")
        f.write("        high_sd_mult={}, low_sd_mult={},\n".format(multipliers['high'],
                                                                    multipliers['low']))  # by Denton Gentry
        if is_land:  # by Denton Gentry
            f.write("        total_adoption_limit=self.tla_per_region)\n")  # by Denton Gentry
        else:  # by Denton Gentry
            f.write("        total_adoption_limit=pds_tam_per_region)\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_s_curve_ad(f, wb):  # by Denton Gentry
    """Generate the S-Curve section of a solution.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         f: file-like object for output  # by Denton Gentry
         wb: an Excel workbook as returned by xlrd  # by Denton Gentry
    """  # by Denton Gentry
    s = wb.sheet_by_name('S-Curve Adoption')  # by Denton Gentry
    u = wb.sheet_by_name('Unit Adoption Calculations')  # by Denton Gentry
    f.write("    sconfig_list = [['region', 'base_year', 'last_year'],\n")  # by Denton Gentry
    f.write("      ['World', " + xli(s, 16, 1) + ", " + xli(s, 19, 1) + "],\n")  # by Denton Gentry
    f.write("      ['OECD90', " + xli(s, 16, 2) + ", " + xli(s, 19, 2) + "],\n")  # by Denton Gentry
    f.write("      ['Eastern Europe', " + xli(s, 16, 3) + ", " + xli(s, 19, 3) + "],\n")  # by Denton Gentry
    f.write("      ['Asia (Sans Japan)', " + xli(s, 16, 4) + ", " + xli(s, 19, 4) + "],\n")  # by Denton Gentry
    f.write("      ['Middle East and Africa', " + xli(s, 16, 5) + ", " + xli(s, 19, 5) + "],\n")  # by Denton Gentry
    f.write("      ['Latin America', " + xli(s, 16, 6) + ", " + xli(s, 19, 6) + "],\n")  # by Denton Gentry
    f.write("      ['China', " + xli(s, 16, 7) + ", " + xli(s, 19, 7) + "],\n")  # by Denton Gentry
    f.write("      ['India', " + xli(s, 16, 8) + ", " + xli(s, 19, 8) + "],\n")  # by Denton Gentry
    f.write("      ['EU', " + xli(s, 16, 9) + ", " + xli(s, 19, 9) + "],\n")  # by Denton Gentry
    f.write("      ['USA', " + xli(s, 16, 10) + ", " + xli(s, 19, 10) + "]]\n")  # by Denton Gentry
    f.write(
        "    sconfig = pd.DataFrame(sconfig_list[1:], columns=sconfig_list[0], dtype=np.object).set_index('region')\n")  # by Denton Gentry
    f.write("    sconfig['pds_tam_2050'] = pds_tam_per_region.loc[[2050]].T\n")  # by Denton Gentry
    f.write("    sc_regions, sc_percentages = zip(*self.ac.pds_base_adoption)\n")  # by Denton Gentry
    f.write(
        "    sconfig['base_adoption'] = pd.Series(list(sc_percentages), index=list(sc_regions))\n")  # by Denton Gentry
    f.write(
        "    sconfig['base_percent'] = sconfig['base_adoption'] / pds_tam_per_region.loc[2014]\n")  # by Denton Gentry
    f.write("    sc_regions, sc_percentages = zip(*self.ac.pds_adoption_final_percentage)\n")  # by Denton Gentry
    f.write(
        "    sconfig['last_percent'] = pd.Series(list(sc_percentages), index=list(sc_regions))\n")  # by Denton Gentry
    f.write("    if self.ac.pds_adoption_s_curve_innovation is not None:\n")  # by Denton Gentry
    f.write("      sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_innovation)\n")  # by Denton Gentry
    f.write(
        "      sconfig['innovation'] = pd.Series(list(sc_percentages), index=list(sc_regions))\n")  # by Denton Gentry
    f.write("    if self.ac.pds_adoption_s_curve_imitation is not None:\n")  # by Denton Gentry
    f.write("      sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_imitation)\n")  # by Denton Gentry
    f.write(
        "      sconfig['imitation'] = pd.Series(list(sc_percentages), index=list(sc_regions))\n")  # by Denton Gentry
    f.write(
        "    self.sc = s_curve.SCurve(transition_period=" + xli(s, 14, 0) + ", sconfig=sconfig)\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_ht(f, wb, has_custom_ref_ad, is_land):  # by Denton Gentry
    """Generate the Helper Tables section of a solution.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         f: file-like object for output  # by Denton Gentry
         wb: an Excel workbook as returned by xlrd  # by Denton Gentry
         has_custom_ref_ad: whether a REF customadoption is in use.  # by Denton Gentry
         has_single_source: whether to emit a pds_adoption_is_single_source arg  # by Denton Gentry
         is_land: True if LAND model
    """  # by Denton Gentry
    h = wb.sheet_by_name('Helper Tables')  # by Denton Gentry
    initial_datapoint_year = int(h.cell_value(*cell_to_offsets('B21')))  # by Denton Gentry
    final_datapoint_year = int(h.cell_value(*cell_to_offsets('B22')))  # by Denton Gentry
    # by Denton Gentry
    tam_or_tla = 'ref_tam_per_region' if not is_land else 'self.tla_per_region'
    f.write("    ht_ref_adoption_initial = pd.Series(\n")  # by Denton Gentry
    r = [xln(h, 20, n) for n in range(2, 7)]  # by Denton Gentry
    f.write("      [" + ", ".join(r) + ",\n")  # by Denton Gentry
    r = [xln(h, 20, n) for n in range(7, 12)]  # by Denton Gentry
    f.write("       " + ", ".join(r) + "],\n")  # by Denton Gentry
    f.write("       index=REGIONS)\n")  # by Denton Gentry
    f.write(
        "    ht_ref_adoption_final = {0}.loc[{1}] * (ht_ref_adoption_initial / {0}.loc[{2}])\n".format(
            tam_or_tla, final_datapoint_year, initial_datapoint_year))
    f.write("    ht_ref_datapoints = pd.DataFrame(columns=REGIONS)\n")  # by Denton Gentry
    f.write("    ht_ref_datapoints.loc[" + str(
        initial_datapoint_year) + "] = ht_ref_adoption_initial\n")  # by Denton Gentry
    f.write("    ht_ref_datapoints.loc[" + str(
        final_datapoint_year) + "] = ht_ref_adoption_final.fillna(0.0)\n")  # by Denton Gentry
    # by Denton Gentry
    tam_or_tla = 'pds_tam_per_region' if not is_land else 'self.tla_per_region'
    f.write("    ht_pds_adoption_initial = ht_ref_adoption_initial\n")  # by Denton Gentry
    f.write("    ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)\n")  # by Denton Gentry
    f.write(
        "    ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))\n")  # by Denton Gentry
    f.write("    ht_pds_adoption_final = ht_pds_adoption_final_percentage * {}.loc[{}]\n".format(
        tam_or_tla, final_datapoint_year))
    f.write("    ht_pds_datapoints = pd.DataFrame(columns=REGIONS)\n")  # by Denton Gentry
    f.write("    ht_pds_datapoints.loc[" + str(
        initial_datapoint_year) + "] = ht_pds_adoption_initial\n")  # by Denton Gentry
    f.write("    ht_pds_datapoints.loc[" + str(
        final_datapoint_year) + "] = ht_pds_adoption_final.fillna(0.0)\n")  # by Denton Gentry
    # by Denton Gentry
    f.write("    self.ht = helpertables.HelperTables(ac=self.ac,\n")  # by Denton Gentry
    f.write("        ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,\n")  # by Denton Gentry
    f.write("        pds_adoption_data_per_region=pds_adoption_data_per_region,\n")  # by Denton Gentry
    if not is_land:
        f.write(
            "        ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,\n")
    else:
        f.write(
            "        ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,\n")
    if has_custom_ref_ad:  # by Denton Gentry
        f.write("        ref_adoption_data_per_region=ref_adoption_data_per_region,\n")  # by Denton Gentry
    f.write("        pds_adoption_trend_per_region=pds_adoption_trend_per_region,\n")  # by Denton Gentry
    f.write("        pds_adoption_is_single_source=pds_adoption_is_single_source)\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_ua(f, wb, is_rrs=True):
    """Write out the Unit Adoption module for this solution class."""  # by Denton Gentry
    ua_tab = wb.sheet_by_name('Unit Adoption Calculations')  # by Denton Gentry
    ac_tab = wb.sheet_by_name('Advanced Controls')  # by Denton Gentry
    f.write("    self.ua = unitadoption.UnitAdoption(ac=self.ac,\n")
    if is_rrs:
        f.write(
            "        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,\n")
    else:
        f.write("        tla_per_region=self.tla_per_region,\n")
        f.write("        electricity_unit_factor=1000000.0,\n")  # by Denton Gentry
    f.write("        soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),\n")  # by Denton Gentry
    f.write("        soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),\n")  # by Denton Gentry
    if 'Repeated First Cost to Maintaining Implementation Units' in ac_tab.cell(42, 0).value:  # by Denton Gentry
        repeated_cost_for_iunits = convert_bool(ac_tab.cell(42, 2).value)  # by Denton Gentry
        f.write("        repeated_cost_for_iunits=" + str(repeated_cost_for_iunits) + ",\n")  # by Denton Gentry
    # If S135 == D135 (for all regions), then it must not be adding in 'Advanced Controls'!C62  # by Denton Gentry
    bug_cfunits_double_count = False  # by Denton Gentry
    for i in range(0, 9):  # by Denton Gentry
        if ua_tab.cell(134, 18 + i).value != ua_tab.cell(134, 3 + i).value:  # by Denton Gentry
            bug_cfunits_double_count = True  # by Denton Gentry
    f.write("        bug_cfunits_double_count=" + str(bug_cfunits_double_count) + ")\n")  # by Denton Gentry
    f.write("    soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()\n")  # by Denton Gentry
    f.write("    soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()\n")  # by Denton Gentry
    f.write("    conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()\n")
    f.write("    soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_fc(f, wb):  # by Denton Gentry
    """Code generate the First Code module for this solution class."""  # by Denton Gentry
    fc_tab = wb.sheet_by_name('First Cost')  # by Denton Gentry
    f.write("    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=" + xli(fc_tab, 24,
                                                                                              2) + ",\n")  # by Denton Gentry
    f.write("        ref_learning_increase_mult=" + xli(fc_tab, 24, 3)  # by Denton Gentry
            + ", conv_learning_increase_mult=" + xli(fc_tab, 24, 4) + ",\n")  # by Denton Gentry
    f.write("        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,\n")  # by Denton Gentry
    f.write("        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,\n")  # by Denton Gentry
    f.write("        conv_ref_tot_iunits=conv_ref_tot_iunits,\n")
    f.write("        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),\n")  # by Denton Gentry
    f.write("        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),\n")  # by Denton Gentry
    f.write("        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),\n")
    if fc_tab.cell(35, 15).value == 'Implementation Units Installed Each Yr (CONVENTIONAL-REF)':  # by Denton Gentry
        f.write("        conv_ref_first_cost_uses_tot_units=True,\n")  # by Denton Gentry
    if fc_tab.cell(14, 5).value == 1000000000 and fc_tab.cell(14, 6).value == '$/kW TO $/TW':  # by Denton Gentry
        f.write("        fc_convert_iunit_factor=rrs.TERAWATT_TO_KILOWATT)\n")  # by Denton Gentry
    elif fc_tab.cell(15, 5).value == 1000000 and fc_tab.cell(17, 5).value == 'million hectare':

        f.write("        fc_convert_iunit_factor=land.MHA_TO_HA)\n")
    else:  # by Denton Gentry
        f.write("        fc_convert_iunit_factor=" + xln(fc_tab, 14, 5) + ")\n")  # by Denton Gentry
    f.write('\n')  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_oc(f, wb, is_land=False):
    """Code generate the Operating Code module for this solution class."""  # by Denton Gentry
    oc_tab = wb.sheet_by_name('Operating Cost')  # by Denton Gentry
    f.write("    self.oc = operatingcost.OperatingCost(ac=self.ac,\n")  # by Denton Gentry
    f.write("        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,\n")  # by Denton Gentry
    f.write("        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,\n")  # by Denton Gentry
    f.write("        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,\n")  # by Denton Gentry
    f.write("        conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),\n")  # by Denton Gentry
    f.write(
        "        soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),\n")  # by Denton Gentry
    f.write(
        "        soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),\n")  # by Denton Gentry
    f.write(
        "        conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),\n")  # by Denton Gentry
    f.write("        single_iunit_purchase_year=" + xli(oc_tab, 120, 8) + ",\n")  # by Denton Gentry
    f.write("        soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),\n")  # by Denton Gentry
    f.write("        conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit(),\n")  # by Denton Gentry
    # by Denton Gentry
    units = oc_tab.cell(12, 5).value  # by Denton Gentry
    is_energy_units = (units == '$/kW TO $/TW' or units == 'From US$2014 per kW to US$2014 per TW')  # by Denton Gentry
    conversion_factor_fom = oc_tab.cell(12, 4).value  # by Denton Gentry
    conversion_factor_vom = oc_tab.cell(13, 4).value  # by Denton Gentry
    # by Denton Gentry
    if conversion_factor_fom == 1000000000 and is_energy_units:  # by Denton Gentry
        conversion_factor_fom = 'rrs.TERAWATT_TO_KILOWATT'  # by Denton Gentry
    if conversion_factor_vom == 1000000000 and is_energy_units:  # by Denton Gentry
        conversion_factor_vom = 'rrs.TERAWATT_TO_KILOWATT'  # by Denton Gentry
    if is_land:  # by Denton Gentry
        conversion_factor_fom = conversion_factor_vom = 'land.MHA_TO_HA'  # by Denton Gentry
    # by Denton Gentry
    # In almost all cases the two conversion factors are equal. We only know of one solution where  # by Denton Gentry
    # they differ (Heatpumps). operatingcost.py accomodates this, if passed a single number it will  # by Denton Gentry
    # use it for both factors.  # by Denton Gentry
    if conversion_factor_fom == conversion_factor_vom:  # by Denton Gentry
        f.write("        conversion_factor=" + str(conversion_factor_fom) + ")\n")  # by Denton Gentry
    else:  # by Denton Gentry
        f.write("        conversion_factor=(" + str(conversion_factor_fom) + ", " +  # by Denton Gentry
                str(conversion_factor_vom) + "))\n")  # by Denton Gentry
    f.write('\n')  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_c2_c4(f, is_rrs=True, is_protect=False, has_harvest=False):
    """Write out the CO2 Calcs and CH4 Calcs modules for this solution class."""  # by Denton Gentry
    f.write("    self.c4 = ch4calcs.CH4Calcs(ac=self.ac,\n")  # by Denton Gentry
    if not is_rrs:  # by Denton Gentry
        f.write(
            "        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),\n")  # by Denton Gentry
    f.write("        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)\n\n")
    f.write("    self.c2 = co2calcs.CO2Calcs(ac=self.ac,\n")  # by Denton Gentry
    f.write("        ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),\n")  # by Denton Gentry
    f.write(
        "        soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),\n")  # by Denton Gentry
    f.write(
        "        soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),\n")  # by Denton Gentry
    if is_rrs:
        f.write(
            "        soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),\n")
        f.write(
            "        soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),\n")
        f.write(
            "        soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),\n")
    else:
        f.write(
            "        soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),\n")
        f.write(
            "        soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),\n")
        f.write(
            "        soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),\n")
        f.write(
            "        soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),\n")
    f.write("        soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),\n")  # by Denton Gentry
    f.write("        soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),\n")  # by Denton Gentry
    f.write("        conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),\n")
    f.write("        conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),\n")  # by Denton Gentry
    f.write("        conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),\n")  # by Denton Gentry
    f.write("        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,\n")  # by Denton Gentry
    if is_rrs:
        f.write("        fuel_in_liters=False)\n")
    else:
        if is_protect:
            f.write(
                "        tot_red_in_deg_land=self.ua.cumulative_reduction_in_total_degraded_land(),\n")
            f.write(
                "        pds_protected_deg_land=self.ua.pds_cumulative_degraded_land_protected(),\n")
            f.write(
                "        ref_protected_deg_land=self.ua.ref_cumulative_degraded_land_protected(),\n")
        if has_harvest:
            f.write(
                "        annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),\n")
        f.write("        land_distribution=self.ae.get_land_distribution())\n")
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def extract_sources(wb_tab, lines):  # by Denton Gentry
    """Pull the names of sources, by case, from the Excel file.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         wb_tab: an Excel workbook tab as returned by wb.sheet_by_name  # by Denton Gentry
         lines: list of row numbers to process  # by Denton Gentry
    # by Denton Gentry
       Returns: a dict of category keys, containing lists of source names.  # by Denton Gentry
    # by Denton Gentry
       Parsing the data sources can be messy: the number of sources within each category  # by Denton Gentry
       varies between solutions, and even the names of the cases can vary. Most solutions have  # by Denton Gentry
       Baseline/Ambitious/Conservative, but we're not sure that all do, and the final most  # by Denton Gentry
       aggressive case varies in names like "100% REN" (renewables) or "Maximum Cases".  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       |   Baseline Cases  |  Ambitious Cases  |     Conservative Cases      |100% REN |  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       | source1 | source2 | source3 | source4 | source5 | source6 | source7 | source8 | Functional Unit  # by Denton Gentry
    # by Denton Gentry
       The category label like "Baseline Cases" is a merged cell one, two, three, or more cells  # by Denton Gentry
       across. In xlrd, the first cell contains the string and the subsequent cells are ctype  # by Denton Gentry
       XL_CELL_EMPTY. They have a border, but at the time of this writing xlrd does not extract  # by Denton Gentry
       styling information like borders from xlsx/xlsm files (only the classic Excel file format).  # by Denton Gentry
    """  # by Denton Gentry
    sources = {}  # by Denton Gentry
    for line in lines:  # by Denton Gentry
        case = ''  # by Denton Gentry
        for col in range(2, wb_tab.ncols):  # by Denton Gentry
            if wb_tab.cell(line + 1, col).value == 'Functional Unit':  # by Denton Gentry
                break  # by Denton Gentry
            if wb_tab.cell(line, col).ctype != xlrd.XL_CELL_EMPTY:  # by Denton Gentry
                case = wb_tab.cell(line, col).value  # by Denton Gentry
                l = sources.get(case, list())  # by Denton Gentry
            new_source = normalize_source_name(wb_tab.cell(line + 1, col).value)  # by Denton Gentry
            if new_source is not None and new_source not in l:  # by Denton Gentry
                l.append(new_source)  # by Denton Gentry
                sources[case] = l  # by Denton Gentry
    return sources  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def find_source_data_columns(wb, sheet_name, row):  # by Denton Gentry
    """Figure out which columns in Adoption Data (and similar tabs) should be extracted.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         wb: Excel workbook  # by Denton Gentry
         sheet_name: name of the spreadsheet tab like "Adoption Data" or "Fresh Adoption Data"  # by Denton Gentry
         row: row number to check  # by Denton Gentry
       Returns:  # by Denton Gentry
         The string of Excel columns to use, like 'B:R'  # by Denton Gentry
    """  # by Denton Gentry
    ad_tab = wb.sheet_by_name(sheet_name)  # by Denton Gentry
    for col in range(2, ad_tab.ncols):  # by Denton Gentry
        if ad_tab.cell(row, col).value == 'Functional Unit':  # by Denton Gentry
            break  # by Denton Gentry
    return 'B:' + chr(ord('A') + col - 1)  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def extract_source_data(wb, sheet_name, regions, outputdir, prefix):  # by Denton Gentry
    """Pull the names of sources, by case, from the Excel file and write data to CSV.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         wb: Excel workbook  # by Denton Gentry
         sheet_name: name of the Excel tab to go to, like 'Adoption Data' or 'TAM Data'  # by Denton Gentry
         regions: a dict of regions to extract and the line numbers they start at:  # by Denton Gentry
           { 'World': 44, 'OECD90': 104, 'Eastern Europe': 168 ...}  # by Denton Gentry
         outputdir: name of directory to write CSV files to.  # by Denton Gentry
         prefix: prefix for filenames like 'ad_' or 'tam_'  # by Denton Gentry
    # by Denton Gentry
       Returns: a dict of category keys, containing lists of source names.  # by Denton Gentry
    # by Denton Gentry
       Parsing the data sources can be messy: the number of sources within each category  # by Denton Gentry
       varies between solutions, and even the names of the cases can vary. Most solutions have  # by Denton Gentry
       Baseline/Ambitious/Conservative, but we're not sure that all do, and the final most  # by Denton Gentry
       aggressive case varies in names like "100% REN" (renewables) or "Maximum Cases".  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       |   Baseline Cases  |  Ambitious Cases  |     Conservative Cases      |100% REN |  # by Denton Gentry
       +-------------------+-------------------+-----------------------------+---------+  # by Denton Gentry
       | source1 | source2 | source3 | source4 | source5 | source6 | source7 | source8 | Functional Unit  # by Denton Gentry
    # by Denton Gentry
       The category label like "Baseline Cases" is a merged cell one, two, three, or more cells  # by Denton Gentry
       across. In xlrd, the first cell contains the string and the subsequent cells are ctype  # by Denton Gentry
       XL_CELL_EMPTY. They have a border, but at the time of this writing xlrd does not extract  # by Denton Gentry
       styling information like borders from xlsx/xlsm files (only the classic Excel file format).  # by Denton Gentry
    """  # by Denton Gentry
    region_data = {}  # by Denton Gentry
    for (region, skiprows) in regions.items():  # by Denton Gentry
        usecols = find_source_data_columns(wb=wb, sheet_name=sheet_name, row=skiprows)  # by Denton Gentry
        df = pd.read_excel(wb, engine='xlrd', sheet_name=sheet_name, header=0,  # by Denton Gentry
                           index_col=0, usecols=usecols, skiprows=skiprows, nrows=49)  # by Denton Gentry
        df.name = region  # by Denton Gentry
        df.rename(columns=normalize_source_name, inplace=True)  # by Denton Gentry
        region_data[region] = df  # by Denton Gentry
    # by Denton Gentry
    sources = {}  # by Denton Gentry
    for df in region_data.values():  # by Denton Gentry
        for source_name in df.columns:  # by Denton Gentry
            if source_name is not None:  # by Denton Gentry
                sources[source_name] = ''  # by Denton Gentry
    # by Denton Gentry
    for source_name in list(sources.keys()):  # by Denton Gentry
        if not source_name:  # by Denton Gentry
            continue  # by Denton Gentry
        df = pd.DataFrame()  # by Denton Gentry
        for region in region_data.keys():  # by Denton Gentry
            if source_name in region_data[region].columns:  # by Denton Gentry
                df[region] = region_data[region].loc[:, source_name]  # by Denton Gentry
            else:  # by Denton Gentry
                df[region] = np.nan  # by Denton Gentry
        filename = get_filename_for_source(source_name, prefix=prefix)  # by Denton Gentry
        if df.empty or df.isna().all(axis=None, skipna=False) or not filename:  # by Denton Gentry
            del sources[source_name]  # by Denton Gentry
            continue  # by Denton Gentry
        df.index = df.index.astype(int)  # by Denton Gentry
        df.index.name = 'Year'  # by Denton Gentry
        # by Denton Gentry
        zero_adoption_ok = False  # by Denton Gentry
        zero_adoption_solutions = ['nuclear', 'cars']  # by Denton Gentry
        for sname in zero_adoption_solutions:  # by Denton Gentry
            if sname in outputdir:  # by Denton Gentry
                zero_adoption_ok = True  # by Denton Gentry
        if not zero_adoption_ok:  # by Denton Gentry
            # In the Excel implementation, adoption data of 0.0 is treated the same as N/A,  # by Denton Gentry
            # no data available. We don't want to implement adoptiondata.py the same way, we  # by Denton Gentry
            # want to be able to express the difference between a solution which did not  # by Denton Gentry
            # exist prior to year N, and therefore had 0.0 adoption, from a solution which  # by Denton Gentry
            # did exist but for which we have no data prior to year N.  # by Denton Gentry
            # We're handling this in the code generator: when extracting adoption data from  # by Denton Gentry
            # an Excel file, treat values of 0.0 as N/A and write out a CSV file with no  # by Denton Gentry
            # data at that location.  # by Denton Gentry
            df.replace(to_replace=0.0, value=np.nan, inplace=True)  # by Denton Gentry
        # by Denton Gentry
        outputfile = os.path.join(outputdir, filename)  # by Denton Gentry
        df.to_csv(outputfile, header=True)  # by Denton Gentry
        sources[source_name] = filename  # by Denton Gentry
    # by Denton Gentry
    tmp_cases = {}  # by Denton Gentry
    tab = wb.sheet_by_name(sheet_name)  # by Denton Gentry
    for (region, line) in regions.items():  # by Denton Gentry
        case = ''  # by Denton Gentry
        for col in range(2, tab.ncols):  # by Denton Gentry
            if tab.cell(line, col).value == 'Functional Unit':  # by Denton Gentry
                break  # by Denton Gentry
            if tab.cell(line - 1, col).ctype != xlrd.XL_CELL_EMPTY:  # by Denton Gentry
                case = normalize_case_name(tab.cell(line - 1, col).value)  # by Denton Gentry
            # it is important to get the source name from the regional_data.columns here, not re-read  # by Denton Gentry
            # the source_name from Excel, because some solutions like Composting have duplicate  # by Denton Gentry
            # column names and pd.read_excel automatically appends ".1" and ".2" to make them unique.  # by Denton Gentry
            source_name = region_data[region].columns[col - 2]  # by Denton Gentry
            filename = sources.get(source_name, None)  # by Denton Gentry
            if source_name is not None and filename is not None:  # by Denton Gentry
                key = 'Region: ' + region  # by Denton Gentry
                region_cases = tmp_cases.get(key, dict())  # by Denton Gentry
                tmp_cases[key] = region_cases  # by Denton Gentry
                s = region_cases.get(case, dict())  # by Denton Gentry
                if source_name not in s:  # by Denton Gentry
                    s[source_name] = filename  # by Denton Gentry
                    region_cases[case] = s  # by Denton Gentry
    # by Denton Gentry
    # suppress regions which are identical to World.  # by Denton Gentry
    if 'Region: World' in tmp_cases:  # by Denton Gentry
        world = tmp_cases['Region: World']  # by Denton Gentry
        del tmp_cases['Region: World']  # by Denton Gentry
        cases = world.copy()  # by Denton Gentry
        for (region, values) in tmp_cases.items():  # by Denton Gentry
            if values != world:  # by Denton Gentry
                cases[region] = values  # by Denton Gentry
    else:  # by Denton Gentry
        cases = tmp_cases  # by Denton Gentry
    return cases  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def extract_custom_adoption(wb, outputdir, sheet_name, prefix):  # by Denton Gentry
    """Extract custom adoption scenarios from an Excel file.  # by Denton Gentry
       Arguments:  # by Denton Gentry
         wb: Excel workbook as returned by xlrd.  # by Denton Gentry
         outputdir: directory where output files are written  # by Denton Gentry
         sheet_name: Excel sheet name to extract from  # by Denton Gentry
         prefix: string to prepend to filenames  # by Denton Gentry
    """  # by Denton Gentry
    custom_ad_tab = wb.sheet_by_name(sheet_name)  # by Denton Gentry

    assert custom_ad_tab.cell_value(*cell_to_offsets('AN25')) == 'High'
    multipliers = {'high': custom_ad_tab.cell_value(*cell_to_offsets('AO25')),
                   'low': custom_ad_tab.cell_value(*cell_to_offsets('AO26'))}
    scenarios = []  # by Denton Gentry
    for row in range(20, 36):  # by Denton Gentry
        if not re.search(r"Scenario \d+", str(custom_ad_tab.cell(row, 13).value)):  # by Denton Gentry
            continue  # by Denton Gentry
        name = str(custom_ad_tab.cell(row, 14).value)  # by Denton Gentry
        includestr = str(custom_ad_tab.cell_value(row, 18))  # by Denton Gentry
        include = convert_bool(includestr) if includestr else False  # by Denton Gentry
        filename = get_filename_for_source(name, prefix=prefix)  # by Denton Gentry
        if not filename:  # by Denton Gentry
            continue  # by Denton Gentry
        skip = True  # by Denton Gentry
        for row in range(0, custom_ad_tab.nrows):  # by Denton Gentry
            if str(custom_ad_tab.cell(row, 1).value) == name:  # by Denton Gentry
                df = pd.read_excel(wb, engine='xlrd', sheet_name=sheet_name,  # by Denton Gentry
                                   header=0, index_col=0, usecols="A:K", skiprows=row + 1, nrows=49)  # by Denton Gentry
                df.rename(mapper={'Middle East & Africa': 'Middle East and Africa'},  # by Denton Gentry
                          axis='columns', inplace=True)  # by Denton Gentry
                if not df.dropna(how='all', axis=1).dropna(how='all', axis=0).empty:  # by Denton Gentry
                    df.to_csv(os.path.join(outputdir, filename), index=True, header=True)  # by Denton Gentry
                    skip = False  # by Denton Gentry
                break  # by Denton Gentry
        if not skip:  # by Denton Gentry
            scenarios.append({'name': name, 'filename': filename, 'include': include})  # by Denton Gentry
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
    # by Denton Gentry
    # by Denton Gentry


def extract_vmas(wb, outputdir):
    """Extract VMAs from an Excel file.
       Arguments:
         wb: Excel workbook as returned by xlrd.
         outputdir: directory where output files are written
    """
    vma_dir_path = os.path.join(outputdir, 'vma_data')
    if not os.path.exists(vma_dir_path):
        os.mkdir(vma_dir_path)
    vma_r = VMAReader(wb)
    vma_r.read_xls(csv_path=vma_dir_path)
    if 'Variable Meta-analysis-DD' in wb.sheet_names():  # by Denton Gentry
        vma_r.read_xls(csv_path=vma_dir_path, alt_vma=True)  # by Denton Gentry


def lookup_unit(tab, row, col):  # by Denton Gentry
    unit_mapping = {  # by Denton Gentry
        'Million hectare': u'Mha',  # by Denton Gentry
        'MMt FlyAsh Cement (Sol) or MMt OPC (Conv) (Transient)': u'MMt',  # by Denton Gentry
        'Billion USD': u'US$B',  # by Denton Gentry
        'million m2 commercial floor space': u'Mm\u00B2',  # by Denton Gentry
        'Million Households': u'MHholds',  # by Denton Gentry
        'Million m2 of Comm.+Resid. Floor Area Equiv. for Cold Climates': u'Mm\u00B2',  # by Denton Gentry
        'Giga-Liter Water': u'GL H\u2082O',  # by Denton Gentry
        'Million Metric tonnes per year': 'MMt',  # by Denton Gentry
        'million tonne-km': 'Mt-km',  # by Denton Gentry
        'million tonne-kms': 'Mt-km',  # by Denton Gentry
        'Residential and Commercial roof area, m2': u'm\u00B2',  # by Denton Gentry
        'Residential and Commercial roof area,  m2': u'm\u00B2',  # by Denton Gentry
    }  # by Denton Gentry
    name = str(tab.cell_value(row, col))  # by Denton Gentry
    return unit_mapping.get(name, name)  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_units_rrs(f, wb):  # by Denton Gentry
    """Write out units for this solution."""  # by Denton Gentry
    sr_tab = wb.sheet_by_name('ScenarioRecord')  # by Denton Gentry
    f.write('  units = {\n')  # by Denton Gentry
    for row in range(1, sr_tab.nrows):  # by Denton Gentry
        col_d = sr_tab.cell_value(row, 3)  # by Denton Gentry
        col_e = sr_tab.cell_value(row, 4)  # by Denton Gentry
        if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:  # by Denton Gentry
            f.write('    "implementation unit": "' + lookup_unit(sr_tab, row + 5, 5) + '",\n')  # by Denton Gentry
            f.write('    "functional unit": "' + lookup_unit(sr_tab, row + 7, 5) + '",\n')  # by Denton Gentry
            f.write('    "first cost": "' + lookup_unit(sr_tab, row + 16, 5) + '",\n')  # by Denton Gentry
            f.write('    "operating cost": "' + lookup_unit(sr_tab, row + 17, 5) + '",\n')  # by Denton Gentry
            break  # by Denton Gentry
    f.write('  }\n\n')  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def write_units_land(f, wb):  # by Denton Gentry
    """Write out units for this solution."""  # by Denton Gentry
    sr_tab = wb.sheet_by_name('ScenarioRecord')  # by Denton Gentry
    f.write('  units = {\n')  # by Denton Gentry
    for row in range(1, sr_tab.nrows):  # by Denton Gentry
        col_d = sr_tab.cell_value(row, 3)  # by Denton Gentry
        col_e = sr_tab.cell_value(row, 4)  # by Denton Gentry
        if col_d == 'Name of Scenario:' and 'TEMPLATE' not in col_e:  # by Denton Gentry
            f.write('    "implementation unit": None,\n')  # by Denton Gentry
            f.write('    "functional unit": "' + lookup_unit(sr_tab, row + 5, 5) + '",\n')  # by Denton Gentry
            f.write('    "first cost": "' + lookup_unit(sr_tab, row + 12, 5) + '",\n')  # by Denton Gentry
            f.write('    "operating cost": "' + lookup_unit(sr_tab, row + 13, 5) + '",\n')  # by Denton Gentry
            break  # by Denton Gentry
    f.write('  }\n\n')  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def output_solution_python_file(outputdir, xl_filename, classname):  # by Denton Gentry
    """Extract relevant fields from Excel file and output a Python class.  # by Denton Gentry
    # by Denton Gentry
       Arguments:  # by Denton Gentry
         outputdir: filename to write to. None means stdout.  # by Denton Gentry
         xl_filename: an Excel file to open, can be xls/xlsm/etc.  # by Denton Gentry
           Note that we cannot run Macros from xlsm files, only read values.  # by Denton Gentry
         classname: what name to give to the generated Python class.  # by Denton Gentry
    """  # by Denton Gentry
    py_filename = '-' if outputdir is None else os.path.join(outputdir, '__init__.py')  # by Denton Gentry
    wb = xlrd.open_workbook(filename=xl_filename)  # by Denton Gentry
    ac_tab = wb.sheet_by_name('Advanced Controls')  # by Denton Gentry
    # by Denton Gentry
    is_rrs = 'RRS' in xl_filename or 'TAM' in wb.sheet_names()  # by Denton Gentry
    is_land = 'PDLAND' in xl_filename or 'L-Use' in xl_filename or 'AEZ Data' in wb.sheet_names()  # by Denton Gentry
    has_tam = is_rrs  # by Denton Gentry
    # by Denton Gentry
    f = open(py_filename, 'w') if py_filename != '-' else sys.stdout  # by Denton Gentry
    # by Denton Gentry
    solution_name = ac_tab.cell_value(39, 2)  # 'Advanced Controls'!C40  # by Denton Gentry
    f.write('"""' + str(solution_name) + ' solution model.\n')  # by Denton Gentry
    f.write('   Excel filename: ' + os.path.basename(xl_filename) + '\n')  # by Denton Gentry
    f.write('"""\n')  # by Denton Gentry
    f.write('\n')  # by Denton Gentry
    f.write('import pathlib\n')  # by Denton Gentry
    f.write('\n')  # by Denton Gentry
    f.write('import numpy as np\n')  # by Denton Gentry
    f.write('import pandas as pd\n')  # by Denton Gentry
    f.write('\n')  # by Denton Gentry
    f.write('from model import adoptiondata\n')  # by Denton Gentry
    f.write('from model import advanced_controls\n')  # by Denton Gentry
    if is_land:
        f.write('from model import aez\n')
    f.write('from model import ch4calcs\n')  # by Denton Gentry
    f.write('from model import co2calcs\n')  # by Denton Gentry
    f.write('from model import customadoption\n')  # by Denton Gentry
    f.write('from model import emissionsfactors\n')  # by Denton Gentry
    f.write('from model import firstcost\n')  # by Denton Gentry
    f.write('from model import helpertables\n')  # by Denton Gentry
    f.write('from model import operatingcost\n')  # by Denton Gentry
    f.write('from model import s_curve\n')  # by Denton Gentry
    f.write('from model import unitadoption\n')  # by Denton Gentry
    f.write('from model import vma\n')  # by Denton Gentry
    f.write('from model.advanced_controls import SOLUTION_CATEGORY\n\n')
    # by Denton Gentry
    if has_tam:  # by Denton Gentry
        f.write('from model import tam\n')  # by Denton Gentry
    elif is_land:
        f.write('from model import tla\n')
    # by Denton Gentry
    if is_rrs:  # by Denton Gentry
        f.write('from solution import rrs\n\n')  # by Denton Gentry
        scenarios = get_rrs_scenarios(wb=wb)  # by Denton Gentry
    elif is_land:  # by Denton Gentry
        f.write('from solution import land\n\n')
        scenarios = get_land_scenarios(wb=wb)  # by Denton Gentry
    else:  # by Denton Gentry
        scenarios = {}  # by Denton Gentry
    # by Denton Gentry
    f.write("DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))\n")
    f.write("THISDIR = pathlib.Path(__file__).parents[0]\n")
    if is_land:
        extract_vmas(wb=wb, outputdir=outputdir)
        f.write("VMAs = vma.generate_vma_dict(THISDIR.joinpath('vma_data'))\n\n")
    else:
        f.write("\n")
    f.write(
        "REGIONS = ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa',\n")  # by Denton Gentry
    f.write("           'Latin America', 'China', 'India', 'EU', 'USA']\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    has_default_pds_ad = has_custom_pds_ad = has_default_ref_ad = has_custom_ref_ad = False  # by Denton Gentry
    has_s_curve_pds_ad = has_linear_pds_ad = use_custom_tla = is_protect = has_harvest = False
    for s in scenarios.values():  # by Denton Gentry
        if s.get('soln_pds_adoption_basis', '') == 'Existing Adoption Prognostications':  # by Denton Gentry
            has_default_pds_ad = True  # by Denton Gentry
        if s.get('soln_pds_adoption_basis', '') == 'Fully Customized PDS':  # by Denton Gentry
            has_custom_pds_ad = True  # by Denton Gentry
        if 'S-Curve' in s.get('soln_pds_adoption_basis', ''):  # by Denton Gentry
            has_s_curve_pds_ad = True  # by Denton Gentry
        if 'Linear' in s.get('soln_pds_adoption_basis', ''):  # by Denton Gentry
            has_linear_pds_ad = True  # by Denton Gentry
        if s.get('soln_ref_adoption_basis', '') == 'Default':  # by Denton Gentry
            has_default_ref_ad = True  # by Denton Gentry
        if s.get('soln_ref_adoption_basis', '') == 'Custom':  # by Denton Gentry
            has_custom_ref_ad = True  # by Denton Gentry
        if s.get('use_custom_tla', ''):
            extract_custom_tla(wb, outputdir=outputdir)
            use_custom_tla = True
        if 'delay_protection_1yr' in s.keys():
            is_protect = True
        if 'carbon_not_emitted_after_harvesting' in s.keys():
            has_harvest = True
    # by Denton Gentry
    f.write('scenarios = {\n')  # by Denton Gentry
    for name, s in scenarios.items():  # by Denton Gentry
        prefix = '  '  # by Denton Gentry
        f.write(prefix + "'" + name + "': advanced_controls.AdvancedControls(\n")  # by Denton Gentry
        write_scenario(f=f, s=s)  # by Denton Gentry
        f.write(2 * prefix + '),\n')  # by Denton Gentry
    f.write('}\n\n')  # by Denton Gentry
    # by Denton Gentry
    f.write("class " + str(classname) + ":\n")  # by Denton Gentry
    f.write("  name = '" + str(solution_name) + "'\n")  # by Denton Gentry
    if is_rrs:  # by Denton Gentry
        write_units_rrs(f=f, wb=wb)  # by Denton Gentry
    if is_land:  # by Denton Gentry
        write_units_land(f=f, wb=wb)  # by Denton Gentry
    f.write("  def __init__(self, scenario=None):\n")  # by Denton Gentry
    f.write("    if scenario is None:\n")  # by Denton Gentry
    f.write("      scenario = '" + list(scenarios.keys())[0] + "'\n")  # by Denton Gentry
    f.write("    self.scenario = scenario\n")  # by Denton Gentry
    f.write("    self.ac = scenarios[scenario]\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    if has_tam:  # by Denton Gentry
        f.write("    # TAM\n")
        write_tam(f=f, wb=wb, outputdir=outputdir)  # by Denton Gentry
    elif is_land:
        f.write("    # TLA\n")
        f.write("    self.ae = aez.AEZ(solution_name=self.name)\n")
        if use_custom_tla:
            f.write("    if self.ac.use_custom_tla:\n")
            f.write(
                "      self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))\n")
            f.write("      custom_world_vals = self.c_tla.get_world_values()\n")
            f.write("    else:\n")
            f.write("      custom_world_vals = None\n")
            f.write("    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(), ")
            f.write("custom_world_values=custom_world_vals)\n\n")
        else:
            f.write(
                "    self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())\n\n")
    # by Denton Gentry
    if has_default_pds_ad or has_default_ref_ad:  # by Denton Gentry
        write_ad(f=f, wb=wb, outputdir=outputdir)  # by Denton Gentry
    if has_custom_pds_ad:  # by Denton Gentry
        write_custom_ad(case='PDS', f=f, wb=wb, outputdir=outputdir, is_land=is_land)  # by Denton Gentry
    if has_custom_ref_ad:  # by Denton Gentry
        write_custom_ad(case='REF', f=f, wb=wb, outputdir=outputdir, is_land=is_land)  # by Denton Gentry
    if has_s_curve_pds_ad:  # by Denton Gentry
        write_s_curve_ad(f=f, wb=wb)  # by Denton Gentry
    # by Denton Gentry
    if has_custom_ref_ad and has_default_ref_ad:  # by Denton Gentry
        f.write("    if self.ac.soln_ref_adoption_basis == 'Custom':\n")  # by Denton Gentry
        f.write("      ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()\n")  # by Denton Gentry
        f.write("    else:\n")  # by Denton Gentry
        f.write("      ref_adoption_data_per_region = None\n")  # by Denton Gentry
    elif has_custom_ref_ad:  # by Denton Gentry
        f.write("    ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()\n")  # by Denton Gentry
    elif has_default_ref_ad:  # by Denton Gentry
        f.write("    ref_adoption_data_per_region = None\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    f.write("    if False:\n")  # by Denton Gentry
    f.write("      # One may wonder why this is here. This file was code generated.\n")  # by Denton Gentry
    f.write("      # This 'if False' allows subsequent conditions to all be elif.\n")  # by Denton Gentry
    f.write("      pass\n")  # by Denton Gentry
    if has_custom_pds_ad:  # by Denton Gentry
        f.write("    elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':\n")  # by Denton Gentry
        f.write("      pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()\n")  # by Denton Gentry
        f.write("      pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()\n")  # by Denton Gentry
        f.write("      pds_adoption_is_single_source = None\n")  # by Denton Gentry
    if has_s_curve_pds_ad:  # by Denton Gentry
        f.write("    elif self.ac.soln_pds_adoption_basis == 'Logistic S-Curve':\n")  # by Denton Gentry
        f.write("      pds_adoption_data_per_region = None\n")  # by Denton Gentry
        f.write("      pds_adoption_trend_per_region = self.sc.logistic_adoption()\n")  # by Denton Gentry
        f.write("      pds_adoption_is_single_source = None\n")  # by Denton Gentry
        f.write("    elif self.ac.soln_pds_adoption_basis == 'Bass Diffusion S-Curve':\n")  # by Denton Gentry
        f.write("      pds_adoption_data_per_region = None\n")  # by Denton Gentry
        f.write("      pds_adoption_trend_per_region = self.sc.bass_diffusion_adoption()\n")  # by Denton Gentry
        f.write("      pds_adoption_is_single_source = None\n")  # by Denton Gentry
    if has_default_pds_ad or has_default_ref_ad:  # by Denton Gentry
        f.write(
            "    elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':\n")  # by Denton Gentry
        f.write("      pds_adoption_data_per_region = self.ad.adoption_data_per_region()\n")  # by Denton Gentry
        f.write("      pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()\n")  # by Denton Gentry
        f.write("      pds_adoption_is_single_source = self.ad.adoption_is_single_source()\n")  # by Denton Gentry
    if has_linear_pds_ad:  # by Denton Gentry
        f.write("    elif self.ac.soln_pds_adoption_basis == 'Linear':\n")  # by Denton Gentry
        f.write("      pds_adoption_data_per_region = None\n")  # by Denton Gentry
        f.write("      pds_adoption_trend_per_region = None\n")  # by Denton Gentry
        f.write("      pds_adoption_is_single_source = None\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    write_ht(f=f, wb=wb, has_custom_ref_ad=has_custom_ref_ad, is_land=is_land)  # by Denton Gentry

    f.write("    self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)\n")  # by Denton Gentry
    f.write("\n")  # by Denton Gentry
    write_ua(f=f, wb=wb, is_rrs=is_rrs)
    write_fc(f=f, wb=wb)  # by Denton Gentry
    write_oc(f=f, wb=wb, is_land=is_land)

    write_c2_c4(f=f, is_rrs=is_rrs, is_protect=is_protect, has_harvest=has_harvest)
    # by Denton Gentry
    if is_rrs:  # by Denton Gentry
        f.write(
            "    self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],\n")  # by Denton Gentry
        f.write("        soln_avg_annual_use=self.ac.soln_avg_annual_use,\n")  # by Denton Gentry
        f.write("        conv_avg_annual_use=self.ac.conv_avg_annual_use)\n")  # by Denton Gentry
        f.write("\n")  # by Denton Gentry
    # by Denton Gentry
    for key, values in scenarios.items():  # by Denton Gentry
        if values:  # by Denton Gentry
            raise KeyError('Scenario ' + key + ' has unconsumed fields: ' + str(values.keys()))  # by Denton Gentry
    # by Denton Gentry
    f.close()  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


def infer_classname(filename):  # by Denton Gentry
    """Pick a reasonable classname if none is specified."""  # by Denton Gentry
    special_cases = [  # by Denton Gentry
        ('Aircraft Fuel Efficiency', 'Airplanes'),  # by Denton Gentry
        ('BiomassELC', 'Biomass'),  # by Denton Gentry
        ('Biomass from Perennial Crops for Electricity Generation', 'Biomass'),  # by Denton Gentry
        ('Bioplastics', 'Bioplastic'),  # by Denton Gentry
        ('Car Fuel Efficiency', 'Cars'),  # by Denton Gentry
        ('Cement', 'AlternativeCement'),  # by Denton Gentry
        ('CHP_A_', 'CoGenElectricity'),  # by Denton Gentry
        ('CHP_B_', 'CoGenHeat'),  # by Denton Gentry
        ('CSP_', 'ConcentratedSolar'),  # by Denton Gentry
        ('High Efficient Heat Pumps', 'HeatPumps'),  # by Denton Gentry
        ('Household & Commercial Recycling', 'Recycling'),  # by Denton Gentry
        ('Increasing Distribution Efficiency in WDSs', 'WaterDistribution'),  # by Denton Gentry
        ('Instream Hydro', 'InstreamHydro'),  # by Denton Gentry
        ('Large Biodigesters', 'Biogas'),  # by Denton Gentry
        ('MicroWind Turbines', 'MicroWind'),  # by Denton Gentry
        ('Oceanic Freight Improvements', 'Ships'),  # by Denton Gentry
        ('Regenerative_Agriculture', 'RegenerativeAgriculture'),  # by Denton Gentry
        ('Renewable District Heating', 'DistrictHeating'),  # by Denton Gentry
        ('Rooftop Solar PV', 'SolarPVRoof'),  # by Denton Gentry
        ('Small Biogas Digesters', 'BiogasSmall'),  # by Denton Gentry
        ('SolarPVUtility', 'SolarPVUtil'),  # by Denton Gentry
        ('SolarPVRooftop', 'SolarPVRoof'),  # by Denton Gentry
        ('solution_xls_extract_RRS_test_A', 'TestClassA'),  # by Denton Gentry
        ('Tropical_Forest_Restoration', 'TropicalForests'),  # by Denton Gentry
        ('Truck Fuel Efficiency', 'Trucks'),  # by Denton Gentry
        ('Utility Scale Solar PV', 'SolarPVUtil'),  # by Denton Gentry
        ('Videoconferencing and Telepresence', 'Telepresence'),  # by Denton Gentry
        ('WastetoEnergy', 'WasteToEnergy'),  # by Denton Gentry
        ('Wave&Tidal', 'WaveAndTidal'),  # by Denton Gentry
        ('Wave and Tidal', 'WaveAndTidal'),  # by Denton Gentry
        ('Wind Offshore', 'OffshoreWind'),  # by Denton Gentry
    ]  # by Denton Gentry
    for (pattern, classname) in special_cases:  # by Denton Gentry
        if pattern.replace(' ', '').lower() in filename.replace(' ', '').lower():  # by Denton Gentry
            return classname  # by Denton Gentry
    namelist = re.split('[(_-]', os.path.basename(filename))  # by Denton Gentry
    if namelist[0] == 'Drawdown':  # by Denton Gentry
        namelist.pop(0)  # by Denton Gentry
    return namelist[0].replace(' ', '')  # by Denton Gentry
    # by Denton Gentry


def link_vma(cell_value):
    """
    Certain AdvancedControls inputs are linked to the mean, high or low value of their
    corresponding VMA tables. In the Excel ScenarioRecord, the cell value will look like:
    'Val:(328.415857769938) Formula:=C80'
    We can infer the chosen statistic from the cell reference. If there is no forumla we
    return the cell value as a float.
    Args:
      cell_value: raw string from the Excel cell
  
    Returns:
      'mean', 'high' or 'low' or raw value if no formula in cell
    """
    if not isinstance(cell_value, str) or 'Formula:=' not in cell_value:
        return convert_sr_float(cell_value)
    if 'Error' in cell_value:
        return 0.
    if True in [cell_value.endswith(x) for x in ['80', '95', '175', '189', '140']]:
        return {'value': convert_sr_float(cell_value), 'statistic': 'mean'}
    elif True in [cell_value.endswith(x) for x in ['81', '96', '176', '190', '141']]:
        return {'value': convert_sr_float(cell_value), 'statistic': 'high'}
    elif True in [cell_value.endswith(x) for x in ['82', '97', '177', '191', '142']]:
        return {'value': convert_sr_float(cell_value), 'statistic': 'low'}
    else:
        formula = cell_value.split(':=')[1]
        warnings.warn('cell formula: {} not recognised - using value instead'.format(formula))
        return {'value': convert_sr_float(cell_value), 'xls cell formula': formula}

    # by Denton Gentry


if __name__ == "__main__":  # by Denton Gentry
    parser = argparse.ArgumentParser(  # by Denton Gentry
        description='Create python Drawdown solution from Excel version.')  # by Denton Gentry
    parser.add_argument('--excelfile', required=True, help='Excel filename to process')  # by Denton Gentry
    parser.add_argument('--outputdir', default=None,
                        help='Directory to write generated Python code to')  # by Denton Gentry
    parser.add_argument('--classname', help='Name for Python class')  # by Denton Gentry
    args = parser.parse_args(sys.argv[1:])  # by Denton Gentry
    # by Denton Gentry
    if args.classname is None:  # by Denton Gentry
        args.classname = infer_classname(filename=args.excelfile)  # by Denton Gentry
    # by Denton Gentry
    output_solution_python_file(outputdir=args.outputdir, xl_filename=args.excelfile,  # by Denton Gentry
                                classname=args.classname)  # by Denton Gentry
