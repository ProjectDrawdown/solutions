"""Tests for solution_xls_extract.py"""

import pathlib
import os.path
import subprocess

import pytest
import xlrd
from tools import solution_xls_extract as sx

this_dir = pathlib.Path(__file__).parents[0]


def test_convert_sr_float():
    s = "Val:(0.182810601365724) Formula:='Variable Meta-analysis'!G1411"
    assert sx.convert_sr_float(s) == pytest.approx(0.182810601365724)
    assert sx.convert_sr_float('0.1987') == pytest.approx(0.1987)
    assert sx.convert_sr_float('') == pytest.approx(0.0)
    assert sx.convert_sr_float('12') == pytest.approx(12.0)
    assert sx.convert_sr_float('20%') == pytest.approx(0.2)
    s = 'Val:(4.16280354784867E-02) Formula:=0.1263*D144'
    assert sx.convert_sr_float(s) == pytest.approx(0.0416280354784867)
    s = 'Val:(0,04) Formula:=F207'
    assert sx.convert_sr_float(s) == pytest.approx(0.04)


def test_get_filename_for_source():
    expected = {
        "Based on: IEA ETP 2016 6DS": 'ad_based_on_IEA_ETP_2016_6DS.csv',
        "Based on: IEA ETP 2016 - 6DS": 'ad_based_on_IEA_ETP_2016_6DS.csv',
        "Based on: IEA ETP 2016 4DS": 'ad_based_on_IEA_ETP_2016_4DS.csv',
        "Based on: IEA ETP 2016 - 4DS": 'ad_based_on_IEA_ETP_2016_4DS.csv',
        "Based on: IEA ETP 2016 2DS": 'ad_based_on_IEA_ETP_2016_2DS.csv',
        "Based on: IEA ETP 2016 - 2DS": 'ad_based_on_IEA_ETP_2016_2DS.csv',
        "Based on: AMPERE (2014) IMAGE Refpol": 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv',
        "Based on: AMPERE IMAGE REFpol": 'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv',
        "Based on: AMPERE (2014) MESSAGE REFPol":
            'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv',
        "Based on: AMPERE MESSAGE REFpol": 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv',
        "Based on: AMPERE (2014) GEM E3 REFpol": 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv',
        "Based on: AMPERE GEM E3 REFpol": 'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv',
        "Based on: AMPERE (2014) IMAGE 550": 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv',
        "Based on: AMPERE IMAGE 550": 'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv',
        "Based on: AMPERE (2014) MESSAGE 550": 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv',
        "Based on: AMPERE MESSAGE 550": 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv',
        "Based on: AMPERE (2014) GEM E3 550": 'ad_based_on_AMPERE_2014_GEM_E3_550.csv',
        "Based on: AMPERE GEM E3 550": 'ad_based_on_AMPERE_2014_GEM_E3_550.csv',
        "Based on: Greenpeace (2015) Reference": 'ad_based_on_Greenpeace_2015_Reference.csv',
        "Based on: AMPERE (2014) IMAGE 450": 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv',
        "Based on: AMPERE IMAGE 450": 'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv',
        "Based on: AMPERE (2014) MESSAGE 450": 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv',
        "Based on: AMPERE MESSAGE 450": 'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv',
        "Based on: AMPERE (2014) GEM E3 450": 'ad_based_on_AMPERE_2014_GEM_E3_450.csv',
        "Based on: AMPERE GEM E3 450": 'ad_based_on_AMPERE_2014_GEM_E3_450.csv',
        'Based on: Greenpeace (2015) Reference': 'ad_based_on_Greenpeace_2015_Reference.csv',
        'Greenpeace 2015 Reference Scenario': 'ad_based_on_Greenpeace_2015_Reference.csv',
        "Based on: Greenpeace (2015) Energy Revolution":
            'ad_based_on_Greenpeace_2015_Energy_Revolution.csv',
        "Based on: Greenpeace 2015 Energy Revolution Scenario":
            'ad_based_on_Greenpeace_2015_Energy_Revolution.csv',
        "Based on: Greenpeace (2015) Advanced Energy Revolution":
            'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv',
        "Based on: Greenpeace 2015 Advanced Energy Revolution Scenario":
            'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv',
        "Based on: Greenpeace Solar Thermal Elc Global Outlook 2016 (Moderate Scenario)":
            'ad_based_on_Greenpeace_2016_Solar_Thermal_Moderate.csv',
        "Based on: Greenpeace Solar Thermal Elc Global Outlook 2016 (Advanced Scenario)":
            'ad_based_on_Greenpeace_2016_Solar_Thermal_Advanced.csv',
    }
    for key, value in expected.items():
        inferred = sx.get_filename_for_source(sx.normalize_source_name(key), prefix="ad_")
        assert inferred == value


def test_find_source_data_columns():
    wb = xlrd.open_workbook(filename=os.path.join(this_dir, 'solution_xls_extract_RRS_test_A.xlsm'))
    assert sx.find_source_data_columns(wb=wb, sheet_name='Adoption Data', row=44) == 'B:R'

def test_invoke_shell_test():
    script = str(this_dir.joinpath('test_solution_xls_extract.sh'))
    toolsdir = str(this_dir.parents[0])
    rc = subprocess.run([script, toolsdir], capture_output=True, timeout=90)
    assert rc.returncode == 0, rc.stdout
