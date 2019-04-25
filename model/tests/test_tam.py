"""Tests for tam.py."""  # by Denton Gentry
# by Denton Gentry
import pathlib  # by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry
import pytest  # by Denton Gentry
from model import tam  # by Denton Gentry

# by Denton Gentry
basedir = pathlib.Path(__file__).parents[2]
datadir = pathlib.Path(__file__).parents[0].joinpath('data')
# by Denton Gentry
# arguments used in SolarPVUtil 28Aug18, used in many tests  # by Denton Gentry
tamconfig_list = [  # by Denton Gentry
    ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',  # by Denton Gentry
     'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],  # by Denton Gentry
    ['source_until_2014', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',  # by Denton Gentry
     'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],  # by Denton Gentry
    ['source_after_2014', 'Baseline Cases',  # by Denton Gentry
     'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario', 'ALL SOURCES',  # by Denton Gentry
     'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',  # by Denton Gentry
     'ALL SOURCES', 'ALL SOURCES'],  # by Denton Gentry
    ['trend', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',  # by Denton Gentry
     '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly'],  # by Denton Gentry
    ['growth', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium',  # by Denton Gentry
     'Medium', 'Medium', 'Medium'],  # by Denton Gentry
    ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],  # by Denton Gentry
    ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]  # by Denton Gentry
g_tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')  # by Denton Gentry
# by Denton Gentry
g_tam_ref_data_sources = {  # by Denton Gentry
    'Baseline Cases': {  # by Denton Gentry
        'Baseline: Based on- IEA ETP 2016 6DS': basedir.joinpath(  # by Denton Gentry
            'data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv'),  # by Denton Gentry
        'Baseline: Based on- AMPERE MESSAGE-MACRO Reference': basedir.joinpath(  # by Denton Gentry
            'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),  # by Denton Gentry
        'Baseline: Based on- AMPERE GEM E3 Reference': basedir.joinpath(  # by Denton Gentry
            'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv'),  # by Denton Gentry
        'Baseline: Based on- AMPERE IMAGE/TIMER Reference': basedir.joinpath(  # by Denton Gentry
            'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),  # by Denton Gentry
    },  # by Denton Gentry
    'Conservative Cases': {  # by Denton Gentry
        'Conservative: Based on- IEA ETP 2016 4DS': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv')),  # by Denton Gentry
        'Conservative: Based on- AMPERE MESSAGE-MACRO 550': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv')),  # by Denton Gentry
        'Conservative: Based on- AMPERE GEM E3 550': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv')),  # by Denton Gentry
        'Conservative: Based on- AMPERE IMAGE/TIMER 550': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv')),  # by Denton Gentry
        'Conservative: Based on- Greenpeace 2015 Reference': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv')),  # by Denton Gentry
    },  # by Denton Gentry
    'Ambitious Cases': {  # by Denton Gentry
        'Ambitious: Based on- IEA ETP 2016 2DS': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv')),  # by Denton Gentry
        'Ambitious: Based on- AMPERE MESSAGE-MACRO 450': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv')),  # by Denton Gentry
        'Ambitious: Based on- AMPERE GEM E3 450': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv')),  # by Denton Gentry
        'Ambitious: Based on- AMPERE IMAGE/TIMER 450': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv')),  # by Denton Gentry
        'Ambitious: Based on- Greenpeace Energy [R]evolution': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv')),  # by Denton Gentry
    },  # by Denton Gentry
    '100% RES2050 Case': {  # by Denton Gentry
        '100% REN: Based on- Greenpeace Advanced [R]evolution': str(basedir.joinpath(
            'data', 'energy', 'tam_based_on_Greenpeace_2015_Advanced_Revolution.csv')),  # by Denton Gentry
    },  # by Denton Gentry
}  # by Denton Gentry
g_tam_pds_data_sources = {  # by Denton Gentry
    'Ambitious Cases': {  # by Denton Gentry
        'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario': str(basedir.joinpath(
            'data', 'energy', 'PDS_plausible_scenario.csv')),  # by Denton Gentry
        'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario': str(basedir.joinpath(
            'data', 'energy', 'PDS_drawdown_scenario.csv')),  # by Denton Gentry
        'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario': str(basedir.joinpath(
            'data', 'energy', 'PDS_optimum_scenario.csv')),  # by Denton Gentry
    },  # by Denton Gentry
}  # by Denton Gentry


# by Denton Gentry
def test_forecast_data_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_global()  # by Denton Gentry
    b = 'Baseline: Based on- AMPERE GEM E3 Reference'  # by Denton Gentry
    c = 'Conservative: Based on- IEA ETP 2016 4DS'  # by Denton Gentry
    assert forecast.loc[2035, b] == pytest.approx(42376.85610878600)  # by Denton Gentry
    assert forecast.loc[2027, c] == pytest.approx(32564.99176177900)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_min_max_sd_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_min_max_sd_global()  # by Denton Gentry
    expected = pd.DataFrame(forecast_min_max_sd_global_list[1:],  # by Denton Gentry
                            columns=forecast_min_max_sd_global_list[0],  # by Denton Gentry
                            index=list(range(2012, 2061)), dtype=np.float64)  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_low_med_high_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_low_med_high_global()  # by Denton Gentry
    expected = pd.DataFrame(forecast_low_med_high_global_list[1:],  # by Denton Gentry
                            columns=forecast_low_med_high_global_list[0],  # by Denton Gentry
                            index=list(range(2012, 2061)), dtype=np.float64)  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_low_med_high_global_larger_sd():  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['source_until_2014', 'World'] = 'Baseline: Based on- IEA ETP 2016 6DS'  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', 'World'] = 'Ambitious: Based on- IEA ETP 2016 2DS'  # by Denton Gentry
    tamconfig_mod.loc['low_sd_mult', 'World'] = 2.0  # by Denton Gentry
    tamconfig_mod.loc['high_sd_mult', 'World'] = 3.0  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_low_med_high_global()  # by Denton Gentry
    expected = pd.DataFrame(forecast_low_med_high_global_larger_list[1:],  # by Denton Gentry
                            columns=forecast_low_med_high_global_larger_list[0],  # by Denton Gentry
                            index=list(range(2012, 2061)), dtype=np.float64)  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_linear_trend_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_global(trend='Linear')  # by Denton Gentry
    expected = pd.DataFrame(linear_trend_global_list[1:],  # by Denton Gentry
                            columns=linear_trend_global_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_poly_degree2_trend_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_global(trend='Degree2')  # by Denton Gentry
    expected = pd.DataFrame(poly_degree2_trend_global_list[1:],  # by Denton Gentry
                            columns=poly_degree2_trend_global_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_poly_degree3_trend_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_global(trend='Degree3')  # by Denton Gentry
    expected = pd.DataFrame(poly_degree3_trend_global_list[1:],  # by Denton Gentry
                            columns=poly_degree3_trend_global_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_exponential_trend_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_global(trend='Exponential')  # by Denton Gentry
    expected = pd.DataFrame(exponential_trend_global_list[1:],  # by Denton Gentry
                            columns=exponential_trend_global_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_pds_global():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_pds_global()  # by Denton Gentry
    a1 = 'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario'  # by Denton Gentry
    a2 = 'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario'  # by Denton Gentry
    a3 = 'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario'  # by Denton Gentry
    assert forecast.loc[2042, a1] == pytest.approx(45246.48136814450)  # by Denton Gentry
    assert forecast.loc[2051, a2] == pytest.approx(55322.78112482230)  # by Denton Gentry
    assert forecast.loc[2033, a3] == pytest.approx(35773.38262874340)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_pds_global()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(59333.209869)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(64314.774793)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(2124.802624)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_pds_global()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(58393.607060)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(60518.409684)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(62643.212309)  # by Denton Gentry
    g = tm.forecast_trend_pds_global(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(36950.208038)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(21761.687416)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(58711.895454)  # by Denton Gentry
    g = tm.forecast_trend_pds_global(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(11846.635815)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(25366.830796)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(23423.141525)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(60636.608137)  # by Denton Gentry
    g = tm.forecast_trend_pds_global(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(-2167.493576)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(15025.626393)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(24197.775743)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(23488.134222)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(60544.042781)  # by Denton Gentry
    g = tm.forecast_trend_pds_global(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(23885.595768)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(2.598937)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(62077.150109)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_pds_global_sources_for_pds():  # by Denton Gentry
    pds_data_sources = {  # by Denton Gentry
        'Baseline Cases': {  # by Denton Gentry
            'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario': str(  # by Denton Gentry
                datadir.joinpath('tam_hotwater_1.csv')),  # by Denton Gentry
            'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario': str(  # by Denton Gentry
                datadir.joinpath('tam_hotwater_2.csv')),  # by Denton Gentry
            'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario': str(  # by Denton Gentry
                datadir.joinpath('tam_hotwater_3.csv')),  # by Denton Gentry
        },  # by Denton Gentry
    }  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=pds_data_sources)  # by Denton Gentry
    lmh_reg = tm.forecast_low_med_high_global()  # by Denton Gentry
    lmh_pds = tm.forecast_low_med_high_pds_global()  # by Denton Gentry
    assert lmh_reg.loc[:2014].equals(lmh_pds.loc[:2014])  # by Denton Gentry
    assert not lmh_reg.loc[2015:].equals(lmh_pds.loc[2015:])  # by Denton Gentry
    # by Denton Gentry


def test_forecast_data_oecd90():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_oecd90()  # by Denton Gentry
    b = 'Baseline: Based on- AMPERE IMAGE/TIMER Reference'  # by Denton Gentry
    c = 'Conservative: Based on- AMPERE MESSAGE-MACRO 550'  # by Denton Gentry
    assert forecast.loc[2055, b] == pytest.approx(14020.47895815650)  # by Denton Gentry
    assert forecast.loc[2017, c] == pytest.approx(8726.22744026733)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_min_max_sd_oecd90():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_min_max_sd_oecd90()  # by Denton Gentry
    expected = pd.DataFrame(forecast_min_max_sd_oecd90_list[1:],  # by Denton Gentry
                            columns=forecast_min_max_sd_oecd90_list[0],  # by Denton Gentry
                            index=list(range(2012, 2061)), dtype=np.float64)  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_low_med_high_oecd90():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_low_med_high_oecd90()  # by Denton Gentry
    expected = pd.DataFrame(forecast_low_med_high_oecd90_list[1:],  # by Denton Gentry
                            columns=forecast_low_med_high_oecd90_list[0],  # by Denton Gentry
                            index=list(range(2012, 2061)), dtype=np.float64)  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_linear_trend_oecd90():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_oecd90(trend='Linear')  # by Denton Gentry
    expected = pd.DataFrame(linear_trend_oecd90_list[1:],  # by Denton Gentry
                            columns=linear_trend_oecd90_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_poly_degree2_trend_oecd90():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_oecd90(trend='Degree2')  # by Denton Gentry
    expected = pd.DataFrame(poly_degree2_trend_oecd90_list[1:],  # by Denton Gentry
                            columns=poly_degree2_trend_oecd90_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_poly_degree3_trend_oecd90():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_oecd90(trend='Degree3')  # by Denton Gentry
    expected = pd.DataFrame(poly_degree3_trend_oecd90_list[1:],  # by Denton Gentry
                            columns=poly_degree3_trend_oecd90_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_exponential_trend_oecd90():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_oecd90(trend='Exponential')  # by Denton Gentry
    expected = pd.DataFrame(exponential_trend_oecd90_list[1:],  # by Denton Gentry
                            columns=exponential_trend_oecd90_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_eastern_europe():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_eastern_europe()  # by Denton Gentry
    a = 'Ambitious: Based on- IEA ETP 2016 2DS'  # by Denton Gentry
    r = '100% REN: Based on- Greenpeace Advanced [R]evolution'  # by Denton Gentry
    assert forecast.loc[2042, a] == pytest.approx(2927.94072286268)  # by Denton Gentry
    assert forecast.loc[2057, r] == pytest.approx(6343.70260870481)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_eastern_europe()  # by Denton Gentry
    assert mms.loc[2058, 'Min'] == pytest.approx(2279.12247278109)  # by Denton Gentry
    assert mms.loc[2058, 'Max'] == pytest.approx(6474.49116739791)  # by Denton Gentry
    assert mms.loc[2058, 'S.D'] == pytest.approx(1011.24848709329)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_eastern_europe()  # by Denton Gentry
    assert lmh.loc[2058, 'Low'] == pytest.approx(2398.68749518803)  # by Denton Gentry
    assert lmh.loc[2058, 'Medium'] == pytest.approx(3409.93598228133)  # by Denton Gentry
    assert lmh.loc[2058, 'High'] == pytest.approx(4421.18446937462)  # by Denton Gentry
    g = tm.forecast_trend_eastern_europe(trend='Linear')  # by Denton Gentry
    assert g.loc[2058, 'x'] == pytest.approx(1429.283338)  # by Denton Gentry
    assert g.loc[2058, 'constant'] == pytest.approx(1994.414541)  # by Denton Gentry
    assert g.loc[2058, 'adoption'] == pytest.approx(3423.697879)  # by Denton Gentry
    g = tm.forecast_trend_eastern_europe(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(46.93646162)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(1415.873621)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(2000.997235)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(3463.807317)  # by Denton Gentry
    g = tm.forecast_trend_eastern_europe(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(-726.6284846)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(1112.658239)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(1023.960717)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(2022.785324)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(3432.775796)  # by Denton Gentry
    g = tm.forecast_trend_eastern_europe(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(2042.049049)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(1.729822342)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(3532.382068)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_asia_sans_japan():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_asia_sans_japan()  # by Denton Gentry
    a = 'Ambitious: Based on- AMPERE GEM E3 450'  # by Denton Gentry
    c = 'Conservative: Based on- AMPERE IMAGE/TIMER 550'  # by Denton Gentry
    assert forecast.loc[2023, a] == pytest.approx(10323.82192491980)  # by Denton Gentry
    assert forecast.loc[2036, c] == pytest.approx(20066.37665215520)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_asia_sans_japan()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(17542.17373865530)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(50261.65772674950)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(7415.12447040017)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_asia_sans_japan()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(20049.96285147210)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(27465.08732187230)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(34880.21179227250)  # by Denton Gentry
    g = tm.forecast_trend_asia_sans_japan(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(18932.02616)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(8057.07299)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(26989.09915)  # by Denton Gentry
    g = tm.forecast_trend_asia_sans_japan(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(1281.362129)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(17679.13874)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(8236.780074)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(27197.28095)  # by Denton Gentry
    g = tm.forecast_trend_asia_sans_japan(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(6036.211651)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(-7571.748292)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(20934.81794)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(8055.78315)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(27455.06445)  # by Denton Gentry
    g = tm.forecast_trend_asia_sans_japan(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(9099.62857)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(3.255584043)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(29624.60557)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_data_middle_east_and_africa():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_middle_east_and_africa()  # by Denton Gentry
    b = 'Baseline: Based on- AMPERE GEM E3 Reference'  # by Denton Gentry
    c = 'Conservative: Based on- IEA ETP 2016 4DS'  # by Denton Gentry
    assert forecast.loc[2025, b] == pytest.approx(2941.25626326821)  # by Denton Gentry
    assert forecast.loc[2039, c] == pytest.approx(3256.84007251502)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_middle_east_and_africa()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(4515.07017474535)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(16298.73629843550)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(3267.94694771890)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_middle_east_and_africa()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(6496.32796179609)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(9764.27490951500)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(13032.22185723390)  # by Denton Gentry
    g = tm.forecast_trend_middle_east_and_africa(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(7768.523146)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(991.9502853)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(8760.473431)  # by Denton Gentry
    g = tm.forecast_trend_middle_east_and_africa(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(5727.415137)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(2168.3839)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(1795.202581)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(9691.001619)  # by Denton Gentry
    g = tm.forecast_trend_middle_east_and_africa(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(1751.627974)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(3158.360776)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(3113.138504)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(1742.679692)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(9765.806946)  # by Denton Gentry
    g = tm.forecast_trend_middle_east_and_africa(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(1774.581583)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(5.686390659)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(10090.96414)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_data_latin_america():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_latin_america()  # by Denton Gentry
    b = 'Baseline: Based on- AMPERE MESSAGE-MACRO Reference'  # by Denton Gentry
    r = '100% REN: Based on- Greenpeace Advanced [R]evolution'  # by Denton Gentry
    assert forecast.loc[2030, b] == pytest.approx(1998.52284327955)  # by Denton Gentry
    assert forecast.loc[2020, r] == pytest.approx(1868.90034084118)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_latin_america()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(3798.01292479911)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(9161.87887718101)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(1659.34938189940)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_latin_america()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(4290.05987598504)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(5949.40925788444)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(7608.75863978384)  # by Denton Gentry
    g = tm.forecast_trend_latin_america(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(4280.327138)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(1411.989083)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(5692.316221)  # by Denton Gentry
    g = tm.forecast_trend_latin_america(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(1766.932238)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(2552.660061)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(1659.795876)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(5979.388175)  # by Denton Gentry
    g = tm.forecast_trend_latin_america(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(-640.1704011)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(2705.848826)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(2207.379018)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(1678.991504)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(5952.048947)  # by Denton Gentry
    g = tm.forecast_trend_latin_america(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(1726.879709)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(3.61818691)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(6248.173559)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_data_china():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_china()  # by Denton Gentry
    b = 'Baseline: Based on- AMPERE MESSAGE-MACRO Reference'  # by Denton Gentry
    c = 'Conservative: Based on- Greenpeace 2015 Reference'  # by Denton Gentry
    assert forecast.loc[2033, b] == pytest.approx(8186.59833863144)  # by Denton Gentry
    assert forecast.loc[2022, c] == pytest.approx(8050.21112508448)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_china()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(7781.53428961777)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(17725.83054370450)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(2400.82849891615)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_china()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(9383.47970362397)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(11784.30820254010)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(14185.13670145630)  # by Denton Gentry
    g = tm.forecast_trend_china(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(6294.735859)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(6156.342065)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(12451.07792)  # by Denton Gentry
    g = tm.forecast_trend_china(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(-5367.764503)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(11543.21671)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(5403.529661)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(11578.98186)  # by Denton Gentry
    g = tm.forecast_trend_china(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(4271.33179)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(-11632.38446)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(13846.99378)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(5275.452986)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(11761.3941)  # by Denton Gentry
    g = tm.forecast_trend_china(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(6234.955122)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(2.106099615)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(13131.43658)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_data_india():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_india()  # by Denton Gentry
    a = 'Ambitious: Based on- AMPERE IMAGE/TIMER 450'  # by Denton Gentry
    c = 'Conservative: Based on- AMPERE IMAGE/TIMER 550'  # by Denton Gentry
    assert forecast.loc[2052, a] == pytest.approx(8646.89896000091)  # by Denton Gentry
    assert forecast.loc[2021, c] == pytest.approx(1872.35548547804)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_india()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(6273.80577690134)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(11850.25398790180)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(1823.74460934643)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_india()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(7038.27156853212)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(8862.01617787855)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(10685.76078722500)  # by Denton Gentry
    g = tm.forecast_trend_india(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(7530.702406)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(874.8077542)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(8405.51016)  # by Denton Gentry
    g = tm.forecast_trend_india(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(2970.018189)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(4626.684621)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(1291.343639)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(8888.046449)  # by Denton Gentry
    g = tm.forecast_trend_india(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(-648.3590152)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(3920.944745)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(4276.986984)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(1310.784804)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(8860.357517)  # by Denton Gentry
    g = tm.forecast_trend_india(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(1535.612932)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(6.636618577)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(10191.27731)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_data_eu():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_eu()  # by Denton Gentry
    c = 'Conservative: Based on- Greenpeace 2015 Reference'  # by Denton Gentry
    r = '100% REN: Based on- Greenpeace Advanced [R]evolution'  # by Denton Gentry
    assert forecast.loc[2012, c] == pytest.approx(3190.07731699797)  # by Denton Gentry
    assert forecast.loc[2013, r] == pytest.approx(3191.42718894118)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_eu()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(3386.28995933476)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(7192.44913678081)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(1239.46103064195)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_eu()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(3771.28270511443)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(5010.74373575638)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(6250.20476639833)  # by Denton Gentry
    g = tm.forecast_trend_eu(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(1526.531345)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(3254.952937)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(4781.484282)  # by Denton Gentry
    g = tm.forecast_trend_eu(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(1089.717815)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(461.0294813)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(3407.782497)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(4958.529793)  # by Denton Gentry
    g = tm.forecast_trend_eu(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(838.2518554)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(-139.7182397)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(913.1473462)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(3382.64736)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(4994.328322)  # by Denton Gentry
    g = tm.forecast_trend_eu(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(3304.393389)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(1.457225648)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(4815.246799)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_data_usa():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    forecast = tm.forecast_data_usa()  # by Denton Gentry
    a = 'Ambitious: Based on- AMPERE IMAGE/TIMER 450'  # by Denton Gentry
    c = 'Conservative: Based on- Greenpeace 2015 Reference'  # by Denton Gentry
    assert forecast.loc[2034, a] == pytest.approx(4755.17137407516)  # by Denton Gentry
    assert forecast.loc[2053, c] == pytest.approx(6679.10400295062)  # by Denton Gentry
    mms = tm.forecast_min_max_sd_usa()  # by Denton Gentry
    assert mms.loc[2059, 'Min'] == pytest.approx(4312.47901236326)  # by Denton Gentry
    assert mms.loc[2059, 'Max'] == pytest.approx(7097.61078977188)  # by Denton Gentry
    assert mms.loc[2059, 'S.D'] == pytest.approx(882.94331416551)  # by Denton Gentry
    lmh = tm.forecast_low_med_high_usa()  # by Denton Gentry
    assert lmh.loc[2059, 'Low'] == pytest.approx(4754.30883599549)  # by Denton Gentry
    assert lmh.loc[2059, 'Medium'] == pytest.approx(5637.25215016100)  # by Denton Gentry
    assert lmh.loc[2059, 'High'] == pytest.approx(6520.19546432651)  # by Denton Gentry
    g = tm.forecast_trend_usa(trend='Linear')  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(1477.300587)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(4069.202924)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(5546.503511)  # by Denton Gentry
    g = tm.forecast_trend_usa(trend='Degree2')  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(916.3405659)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(581.3231445)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(4197.716861)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(5695.380571)  # by Denton Gentry
    g = tm.forecast_trend_usa(trend='Degree3')  # by Denton Gentry
    assert g.loc[2059, 'x^3'] == pytest.approx(-1446.69936)  # by Denton Gentry
    assert g.loc[2059, 'x^2'] == pytest.approx(3038.166295)  # by Denton Gentry
    assert g.loc[2059, 'x'] == pytest.approx(-198.9657649)  # by Denton Gentry
    assert g.loc[2059, 'constant'] == pytest.approx(4241.096409)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(5633.597578)  # by Denton Gentry
    g = tm.forecast_trend_usa(trend='Exponential')  # by Denton Gentry
    assert g.loc[2059, 'coeff'] == pytest.approx(4106.634669)  # by Denton Gentry
    assert g.loc[2059, 'e^x'] == pytest.approx(1.357549289)  # by Denton Gentry
    assert g.loc[2059, 'adoption'] == pytest.approx(5574.958973)  # by Denton Gentry
    # by Denton Gentry


def test_forecast_empty_data():  # by Denton Gentry
    no_data_sources = {'Ambitious Cases': {}, 'Baseline Cases': {},  # by Denton Gentry
                       'Conservative Cases': {}}  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=no_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=no_data_sources)  # by Denton Gentry
    result = tm.forecast_min_max_sd_global()  # by Denton Gentry
    assert all(result.isna())  # by Denton Gentry
    result = tm.forecast_low_med_high_global()  # by Denton Gentry
    assert all(result.isna())  # by Denton Gentry
    # by Denton Gentry


def test_ref_tam_per_region():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.ref_tam_per_region()  # by Denton Gentry
    filename = datadir.joinpath('ref_tam_per_region.csv')
    expected = pd.read_csv(filename, header=0, index_col=0,  # by Denton Gentry
                           skipinitialspace=True, comment='#')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_pds_tam_per_region():  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.pds_tam_per_region()  # by Denton Gentry
    filename = datadir.joinpath('pds_tam_per_region.csv')
    expected = pd.read_csv(filename, header=0, index_col=0,  # by Denton Gentry
                           skipinitialspace=True, comment='#')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_pds_tam_per_region_no_pds_sources():  # by Denton Gentry
    no_data_sources = {'Ambitious Cases': {}, 'Baseline Cases': {},  # by Denton Gentry
                       'Conservative Cases': {}}  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['source_until_2014', 'PDS World'] = 'ALL SOURCES'  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', 'PDS World'] = 'ALL SOURCES'  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=no_data_sources)  # by Denton Gentry
    result = tm.pds_tam_per_region()  # by Denton Gentry
    filename = datadir.joinpath('ref_tam_per_region.csv')  # by Denton Gentry
    expected = pd.read_csv(filename, header=0, index_col=0,  # by Denton Gentry
                           skipinitialspace=True, comment='#')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_pds_tam_per_region_growth_low_2014():  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['growth', 'PDS World'] = 'Low'  # by Denton Gentry
    tamconfig_mod.loc['source_until_2014', 'PDS World'] = 'ALL SOURCES'  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', 'PDS World'] = 'ALL SOURCES'  # by Denton Gentry
    data_sources = {  # by Denton Gentry
        'Baseline Cases': {  # by Denton Gentry
            'B1': str(datadir.joinpath('tam_all_one.csv')),  # by Denton Gentry
            'B2': str(datadir.joinpath('tam_all_zero.csv')),  # by Denton Gentry
        },  # by Denton Gentry
    }  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=data_sources,  # by Denton Gentry
                 tam_pds_data_sources=data_sources)  # by Denton Gentry
    result = tm.pds_tam_per_region()  # by Denton Gentry
    # If the 'Low' growth is applied, the result will be 0.5.  # by Denton Gentry
    assert result.loc[2014, 'World'] == pytest.approx(1.0)  # by Denton Gentry
    # by Denton Gentry


def test_regional_data_source_lists():  # by Denton Gentry
    data_sources = {  # by Denton Gentry
        'Region: China': {  # by Denton Gentry
            # These are the Ambitious Cases from the World region in SolarPVUtil,  # by Denton Gentry
            # repurposed here to be the Baseline Cases for the China region.  # by Denton Gentry
            'Baseline Cases': {  # by Denton Gentry
                'Ambitious: Based on- IEA ETP 2016 2DS': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_IEA_ETP_2016_2DS.csv')),  # by Denton Gentry
                'Ambitious: Based on- AMPERE MESSAGE-MACRO 450': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv')),  # by Denton Gentry
                'Ambitious: Based on- AMPERE GEM E3 450': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_450.csv')),  # by Denton Gentry
                'Ambitious: Based on- AMPERE IMAGE/TIMER 450': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_450.csv')),  # by Denton Gentry
                'Ambitious: Based on- Greenpeace Energy [R]evolution': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_Greenpeace_2015_Energy_Revolution.csv')),  # by Denton Gentry
            },  # by Denton Gentry
        },  # by Denton Gentry
        'Region: India': {  # by Denton Gentry
            # These are the Conservative Cases from the World region in SolarPVUtil,  # by Denton Gentry
            # repurposed here to be the Baseline Cases for the India region.  # by Denton Gentry
            'Baseline Cases': {  # by Denton Gentry
                'Conservative: Based on- IEA ETP 2016 4DS': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_IEA_ETP_2016_4DS.csv')),  # by Denton Gentry
                'Conservative: Based on- AMPERE MESSAGE-MACRO 550': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv')),  # by Denton Gentry
                'Conservative: Based on- AMPERE GEM E3 550': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_550.csv')),  # by Denton Gentry
                'Conservative: Based on- AMPERE IMAGE/TIMER 550': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_550.csv')),  # by Denton Gentry
                'Conservative: Based on- Greenpeace 2015 Reference': str(basedir.joinpath(  # by Denton Gentry
                    'data', 'energy', 'tam_based_on_Greenpeace_2015_Reference.csv')),  # by Denton Gentry
            },  # by Denton Gentry
        },  # by Denton Gentry
        'Baseline Cases': {  # by Denton Gentry
            'Baseline: Based on- IEA ETP 2016 6DS': str(basedir.joinpath(  # by Denton Gentry
                'data', 'energy', 'tam_based_on_IEA_ETP_2016_6DS.csv')),  # by Denton Gentry
            'Baseline: Based on- AMPERE MESSAGE-MACRO Reference': str(basedir.joinpath(  # by Denton Gentry
                'data', 'energy', 'tam_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv')),  # by Denton Gentry
            'Baseline: Based on- AMPERE GEM E3 Reference': str(basedir.joinpath(  # by Denton Gentry
                'data', 'energy', 'tam_based_on_AMPERE_2014_GEM_E3_Reference.csv')),  # by Denton Gentry
            'Baseline: Based on- AMPERE IMAGE/TIMER Reference': str(basedir.joinpath(  # by Denton Gentry
                'data', 'energy', 'tam_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv')),  # by Denton Gentry
        },  # by Denton Gentry
    }  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.ref_tam_per_region()  # by Denton Gentry
    assert result.loc[2059, 'World'] == pytest.approx(62446.806691)  # by Denton Gentry
    # value comes from SolarPVUtil OECD90 with all non-Baseline sources deleted.  # by Denton Gentry
    assert result.loc[2059, 'OECD90'] == pytest.approx(13230.328039)  # by Denton Gentry
    # value comes from SolarPVUtil Eastern Europe with all non-Baseline sources deleted.  # by Denton Gentry
    assert result.loc[2059, 'Eastern Europe'] == pytest.approx(3225.134047)  # by Denton Gentry
    # value comes from SolarPVUtil China with all non-Ambitious sources deleted.  # by Denton Gentry
    # value for the original Baseline Souces would be 11342.46.  # by Denton Gentry
    assert result.loc[2059, 'China'] == pytest.approx(11030.901249)  # by Denton Gentry
    # value comes from SolarPVUtil India with all non-Conservative sources deleted.  # by Denton Gentry
    # value for the original Baseline Souces would be 8529.66.  # by Denton Gentry
    assert result.loc[2059, 'India'] == pytest.approx(8039.649164)  # by Denton Gentry
    # by Denton Gentry


def test_NaN_TAM_2012_data():  # by Denton Gentry
    # test data taken from Solar Hot Water heaters, which has no TAM data for 2012.  # by Denton Gentry
    data_sources = {  # by Denton Gentry
        'Baseline Cases': {  # by Denton Gentry
            'SolarHotWater1': str(datadir.joinpath('tam_hotwater_1.csv')),  # by Denton Gentry
            'SolarHotWater2': str(datadir.joinpath('tam_hotwater_2.csv')),  # by Denton Gentry
            'SolarHotWater3': str(datadir.joinpath('tam_hotwater_3.csv')),  # by Denton Gentry
        },  # by Denton Gentry
        'Conservative Cases': {  # by Denton Gentry
            'SolarHotWater4': str(datadir.joinpath('tam_hotwater_4.csv')),  # by Denton Gentry
            'SolarHotWater5': str(datadir.joinpath('tam_hotwater_5.csv')),  # by Denton Gentry
        },  # by Denton Gentry
    }  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', 'World'] = 'SolarHotWater4'  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_trend_global(trend='Linear')  # by Denton Gentry
    expected = pd.DataFrame(linear_trend_solarhotwater_list[1:],  # by Denton Gentry
                            columns=linear_trend_solarhotwater_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    result = tm.forecast_min_max_sd_global()  # by Denton Gentry
    assert all(pd.isna(result.loc[2012, :]))  # by Denton Gentry
    # by Denton Gentry


def test_mean_ignores_zeros():  # by Denton Gentry
    # Replication of mean() handling from Excel TAM, 0.0 is not included  # by Denton Gentry
    # in the calculation so the mean of [0.0, 1.0] should be 1.0.  # by Denton Gentry
    # See https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.yvwwsbvutw2j  # by Denton Gentry
    data_sources = {  # by Denton Gentry
        'Baseline Cases': {  # by Denton Gentry
            'zero': str(datadir.joinpath('tam_all_zero.csv')),  # by Denton Gentry
            'one': str(datadir.joinpath('tam_all_one.csv')),  # by Denton Gentry
        },  # by Denton Gentry
    }  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_low_med_high_global()  # by Denton Gentry
    assert all(result.loc[:, 'Medium'] == 1.0)  # by Denton Gentry
    # The Excel code to SUM()/COUNTIF(">0") is only used when processing multiple sources  # by Denton Gentry
    # like 'ALL SOURCES' or 'Ambitious Cases', not when an individual source is chosen.  # by Denton Gentry
    # Verify that if there is just one source and it is zero, that Medium is 0.0 not np.nan.  # by Denton Gentry
    data_sources = {  # by Denton Gentry
        'Baseline Cases': {  # by Denton Gentry
            'zero': str(datadir.joinpath('tam_all_zero.csv')),  # by Denton Gentry
        },  # by Denton Gentry
    }  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['source_until_2014', 'World'] = 'zero'  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', 'World'] = 'zero'  # by Denton Gentry
    tm = tam.TAM(tamconfig=g_tamconfig, tam_ref_data_sources=data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_low_med_high_global()  # by Denton Gentry
    assert all(result.loc[:, 'Medium'] == 0.0)  # by Denton Gentry
    # by Denton Gentry


def test_tam_y2014_with_growth_high():  # by Denton Gentry
    # test data taken from Building Automation  # by Denton Gentry
    data_sources = g_tam_ref_data_sources.copy()  # by Denton Gentry
    data_sources['Region: China'] = {  # by Denton Gentry
        'Baseline Cases': {  # by Denton Gentry
            'B1': str(datadir.joinpath('tam_buildingautomation1.csv')),  # by Denton Gentry
            'B2': str(datadir.joinpath('tam_buildingautomation2.csv')),  # by Denton Gentry
        },  # by Denton Gentry
    }  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['growth', 'China'] = 'High'  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.ref_tam_per_region()  # by Denton Gentry
    expected = pd.DataFrame(global_trend_buildingautomation_list[1:],  # by Denton Gentry
                            columns=global_trend_buildingautomation_list[0]).set_index('Year')  # by Denton Gentry
    pd.testing.assert_series_equal(result['China'], expected['China'], check_exact=False)  # by Denton Gentry
    # by Denton Gentry


def test_nonexistent_source_is_NaN():  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['source_until_2014', :] = 'NoSuchSource'  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', :] = 'NoSuchSource'  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources)  # by Denton Gentry
    result = tm.forecast_min_max_sd_global()  # by Denton Gentry
    assert all(pd.isna(result.loc[:, :]))  # by Denton Gentry
    # by Denton Gentry


def test_global_with_regional_included():  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['source_until_2014', :] = 'ALL SOURCES'  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', :] = 'ALL SOURCES'  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources, world_includes_regional=True)  # by Denton Gentry
    result = tm.forecast_min_max_sd_global()  # by Denton Gentry
    expected = pd.DataFrame(forecast_min_max_sd_global_with_regional_list[1:],  # by Denton Gentry
                            columns=forecast_min_max_sd_global_with_regional_list[0]).set_index(
        'Year')  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    result = tm.forecast_low_med_high_global()  # by Denton Gentry
    expected = pd.DataFrame(forecast_low_med_high_global_with_regional_list[1:],  # by Denton Gentry
                            columns=forecast_low_med_high_global_with_regional_list[0]).set_index(
        'Year')  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry
    # if sources != 'ALL SOURCES', min/max/sd includes regional but low/med/high does not.  # by Denton Gentry
    tamconfig_mod = g_tamconfig.copy()  # by Denton Gentry
    tamconfig_mod.loc['source_until_2014', 'World'] = 'Baseline Cases'  # by Denton Gentry
    tamconfig_mod.loc['source_after_2014', 'World'] = 'Baseline Cases'  # by Denton Gentry
    tm = tam.TAM(tamconfig=tamconfig_mod, tam_ref_data_sources=g_tam_ref_data_sources,  # by Denton Gentry
                 tam_pds_data_sources=g_tam_pds_data_sources, world_includes_regional=True)  # by Denton Gentry
    result = tm.forecast_min_max_sd_global()  # by Denton Gentry
    expected = pd.DataFrame(forecast_min_max_sd_global_with_regional_list[1:],  # by Denton Gentry
                            columns=forecast_min_max_sd_global_with_regional_list[0]).set_index(
        'Year')  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    # SD changes because World doesn't include all sources any more, checking that Min  # by Denton Gentry
    # and Max still match is sufficient.  # by Denton Gentry
    pd.testing.assert_frame_equal(result.loc[:, ['Min', 'Max']], expected.loc[:, ['Min', 'Max']],  # by Denton Gentry
                                  check_exact=False)  # by Denton Gentry
    result = tm.forecast_low_med_high_global()  # by Denton Gentry
    expected = pd.DataFrame(forecast_low_med_high_global_list[1:],  # by Denton Gentry
                            columns=forecast_low_med_high_global_list[0],  # by Denton Gentry
                            index=list(range(2012, 2061)), dtype=np.float64)  # by Denton Gentry
    expected.index.name = 'Year'  # by Denton Gentry
    pd.testing.assert_frame_equal(result, expected, check_exact=False)  # by Denton Gentry
    # by Denton Gentry
    # by Denton Gentry


# SolarPVUtil 'TAM Data'!V45:Y94 with source_until_2014='ALL SOURCES',  # by Denton Gentry
# source_after_2014='Baseline Cases', low_sd=1.0, high_sd=1.0  # by Denton Gentry
forecast_min_max_sd_global_list = [['Min', 'Max', 'S.D'],  # by Denton Gentry
                                   [21534.00000000000, 21534.00000000000, 0.00000000000],  # by Denton Gentry
                                   [22203.00000000000, 22203.00000000000, 0.00000000000],  # by Denton Gentry
                                   [22548.29900000000, 22548.29900000000, 0.00000000000],  # by Denton Gentry
                                   [22429.72186613740, 27024.47028030230, 1573.03754318467],  # by Denton Gentry
                                   [22906.91208707250, 27898.55514765100, 1700.78179208709],  # by Denton Gentry
                                   [23402.11898261810, 28756.90389268220, 1826.59454310818],  # by Denton Gentry
                                   [23915.43469432090, 29600.06186266420, 1949.87405540584],  # by Denton Gentry
                                   [24446.91310132170, 30428.52104401230, 2070.53994374119],  # by Denton Gentry
                                   [24872.22274659600, 31079.07510969770, 2213.56778337713],  # by Denton Gentry
                                   [25564.91010953360, 32043.72218365020, 2305.27806750881],  # by Denton Gentry
                                   [26151.94712418630, 32831.96524261970, 2420.43884392962],  # by Denton Gentry
                                   [26758.21045105940, 33608.54961128930, 2535.04332690682],  # by Denton Gentry
                                   [27384.21569039340, 34374.56061482620, 2649.85223593055],  # by Denton Gentry
                                   [28030.45057981490, 35387.69998385000, 2771.99784753967],  # by Denton Gentry
                                   [28697.27510670920, 36509.44295397910, 2883.12788361305],  # by Denton Gentry
                                   [29385.01658968160, 37640.83709757400, 3003.04013793676],  # by Denton Gentry
                                   [30094.11090441640, 38781.92291909170, 3126.04463318390],  # by Denton Gentry
                                   [30825.01685007410, 39932.77141956750, 3252.76500809460],  # by Denton Gentry
                                   [31766.39454410490, 40974.31848294200, 3296.42078579330],  # by Denton Gentry
                                   [32299.50685963790, 42263.94106300020, 3519.53511707383],  # by Denton Gentry
                                   [32931.80139810800, 43444.26074212080, 3660.50771069851],  # by Denton Gentry
                                   [33426.44119216750, 44634.39657467840, 3807.04748961228],  # by Denton Gentry
                                   [33922.51782307470, 45834.33636128930, 3959.46078187048],  # by Denton Gentry
                                   [34466.79329460910, 47044.06260501100, 4105.37491961874],  # by Denton Gentry
                                   [34920.39843102430, 48263.54611959010, 4282.87441317974],  # by Denton Gentry
                                   [35422.84801725060, 49492.75799401440, 4454.24919502414],  # by Denton Gentry
                                   [35928.09819059130, 50731.67302225790, 4632.25928279225],  # by Denton Gentry
                                   [36436.50786680970, 51980.26204388160, 4817.01370436561],  # by Denton Gentry
                                   [36891.04484226660, 53318.69711714730, 5095.39922360529],  # by Denton Gentry
                                   [37464.13317103220, 54506.24339034780, 5207.10869481556],  # by Denton Gentry
                                   [37983.94051696300, 55783.45944978840, 5412.60569009790],  # by Denton Gentry
                                   [38508.07277194310, 57094.96697594920, 5625.16992062115],  # by Denton Gentry
                                   [39036.73739023780, 58748.10225774740, 5844.88482722876],  # by Denton Gentry
                                   [39594.41319952840, 60413.98026242100, 6083.79453667794],  # by Denton Gentry
                                   [40108.55516020810, 62090.52517784090, 6306.19090200500],  # by Denton Gentry
                                   [40652.21519000360, 63775.67005924550, 6548.05790270816],  # by Denton Gentry
                                   [41201.36348823150, 65467.29860921870, 6797.63089838174],  # by Denton Gentry
                                   [41756.22947133940, 67163.27564207200, 7055.12290391661],  # by Denton Gentry
                                   [42313.59819634810, 68762.69252412430, 7291.25692325301],  # by Denton Gentry
                                   [42884.05351472140, 70559.71511013450, 7594.91089880530],  # by Denton Gentry
                                   [43457.50335665930, 72255.90980411190, 7877.83815979076],  # by Denton Gentry
                                   [44037.50938400400, 73947.67647711130, 8169.92722468758],  # by Denton Gentry
                                   [44624.15179991760, 75632.57382684640, 8471.57709338260],  # by Denton Gentry
                                   [45217.56392241990, 77308.23501969790, 8783.24050303591],  # by Denton Gentry
                                   [45817.97637081680, 78972.44968570840, 9105.43004023064],  # by Denton Gentry
                                   [46425.70365916020, 80623.14872784560, 9438.72268536083],  # by Denton Gentry
                                   [47041.07418352010, 82258.28787101410, 9783.75178937746],  # by Denton Gentry
                                   [47664.45901828620, 83875.89923369700, 10141.20924865940],  # by Denton Gentry
                                   [48296.23338953970, 85474.02526601050, 10511.83117785760]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!AA46:AC94  # by Denton Gentry
forecast_low_med_high_global_list = [['Low', 'Medium', 'High'],  # by Denton Gentry
                                     [21534.00000000000, 21534.00000000000, 21534.00000000000],  # by Denton Gentry
                                     [22203.00000000000, 22203.00000000000, 22203.00000000000],  # by Denton Gentry
                                     [22548.29900000000, 22548.29900000000, 22548.29900000000],  # by Denton Gentry
                                     [23168.99955676870, 24742.03709995330, 26315.07464313800],  # by Denton Gentry
                                     [23822.66159619520, 25523.44338828230, 27224.22518036940],  # by Denton Gentry
                                     [24485.97225563620, 26312.56679874430, 28139.16134185250],  # by Denton Gentry
                                     [25158.98753317980, 27108.86158858570, 29058.73564399150],  # by Denton Gentry
                                     [25841.16397624480, 27911.70391998600, 29982.24386372720],  # by Denton Gentry
                                     [26427.94847084320, 28641.51625422030, 30855.08403759750],  # by Denton Gentry
                                     [27229.66463265720, 29534.94270016610, 31840.22076767490],  # by Denton Gentry
                                     [27934.18703226200, 30354.62587619160, 32775.06472012120],  # by Denton Gentry
                                     [28644.36124196430, 31179.40456887110, 33714.44789577800],  # by Denton Gentry
                                     [29359.33913322380, 32009.19136915440, 34659.04360508490],  # by Denton Gentry
                                     [30040.52324052260, 32812.52108806220, 35584.51893560190],  # by Denton Gentry
                                     [30800.06021909020, 33683.18810270320, 36566.31598631630],  # by Denton Gentry
                                     [31523.81124473580, 34526.85138267250, 37529.89152060930],  # by Denton Gentry
                                     [32248.63540639240, 35374.68003957630, 38500.72467276020],  # by Denton Gentry
                                     [32973.74992063480, 36226.51492872940, 39479.27993682400],  # by Denton Gentry
                                     [33886.40858341310, 37182.82936920640, 40479.25015499970],  # by Denton Gentry
                                     [34421.94378052080, 37941.47889759460, 41461.01401466840],  # by Denton Gentry
                                     [35143.66261074720, 38804.17032144570, 42464.67803214420],  # by Denton Gentry
                                     [35862.99847770260, 39670.04596731490, 43477.09345692710],  # by Denton Gentry
                                     [36579.42761751810, 40538.88839938860, 44498.34918125900],  # by Denton Gentry
                                     [37394.77243563120, 41500.14735524990, 45605.52227486860],  # by Denton Gentry
                                     [38001.67745291160, 42284.55186609130, 46567.42627927110],  # by Denton Gentry
                                     [38706.62997490870, 43160.87916993280, 47615.12836495690],  # by Denton Gentry
                                     [39406.95813868560, 44039.21742147790, 48671.47670427010],  # by Denton Gentry
                                     [40102.31389804570, 44919.32760241130, 49736.34130677690],  # by Denton Gentry
                                     [40599.87264795980, 45695.27187156510, 50790.67109517040],  # by Denton Gentry
                                     [41476.69445541550, 46683.80315023110, 51890.91184504660],  # by Denton Gentry
                                     [42154.96475761450, 47567.57044771240, 52980.17613781020],  # by Denton Gentry
                                     [42826.71430965000, 48451.88423027110, 54077.05415089230],  # by Denton Gentry
                                     [43491.45871093340, 49336.34353816220, 55181.22836539090],  # by Denton Gentry
                                     [44089.17440673100, 50172.96894340890, 56256.76348008680],  # by Denton Gentry
                                     [44797.93560749650, 51104.12650950150, 57410.31741150650],  # by Denton Gentry
                                     [45438.65305341790, 51986.71095612610, 58534.76885883420],  # by Denton Gentry
                                     [46070.27282325870, 52867.90372164040, 59665.53462002220],  # by Denton Gentry
                                     [46692.17253139680, 53747.29543531340, 60802.41833923000],  # by Denton Gentry
                                     [47378.19668385750, 54669.45360711050, 61960.71053036350],  # by Denton Gentry
                                     [47904.13271123300, 55499.04361003830, 63093.95450884350],  # by Denton Gentry
                                     [48492.76412708170, 56370.60228687250, 64248.44044666320],  # by Denton Gentry
                                     [49068.65756787440, 57238.58479256200, 65408.51201724960],  # by Denton Gentry
                                     [49630.79946744820, 58102.37656083080, 66573.95365421340],  # by Denton Gentry
                                     [50178.18264934680, 58961.42315238270, 67744.66365541860],  # by Denton Gentry
                                     [50709.84663979500, 59815.27668002570, 68920.70672025630],  # by Denton Gentry
                                     [51224.87420398780, 60663.59688934860, 70102.31957470950],  # by Denton Gentry
                                     [51722.32277142010, 61506.07456079760, 71289.82635017510],  # by Denton Gentry
                                     [52201.24793411850, 62342.45718277790, 72483.66643143730],  # by Denton Gentry
                                     [52660.65083506330, 63172.48201292090, 73684.31319077850]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!AA46:AC94 with B35='Ambitious: Based on- IEA ETP 2016 2DS', B25=2.0, B24=3.0  # by Denton Gentry
forecast_low_med_high_global_larger_list = [['Low', 'Medium', 'High'],  # by Denton Gentry
                                            [21534.00000000000, 21534.00000000000, 21534.00000000000],
                                            # by Denton Gentry
                                            [22203.00000000000, 22203.00000000000, 22203.00000000000],
                                            # by Denton Gentry
                                            [22548.29900000000, 22548.29900000000, 22548.29900000000],
                                            # by Denton Gentry
                                            [21884.26489425440, 24410.14549772370, 28198.96640292780],
                                            # by Denton Gentry
                                            [22230.43144764160, 24930.63374235090, 28980.93718441470],
                                            # by Denton Gentry
                                            [22570.81950045950, 25447.98262185830, 29763.72730395650],
                                            # by Denton Gentry
                                            [22908.61111574560, 25962.19574733010, 30542.57269470690],
                                            # by Denton Gentry
                                            [23244.77253518950, 26473.13961731790, 31315.69024051070],
                                            # by Denton Gentry
                                            [23527.18865789590, 27015.16947226340, 32247.14069381470],
                                            # by Denton Gentry
                                            [23910.40086744870, 27485.30513675620, 32847.66154071750],
                                            # by Denton Gentry
                                            [24237.65905071480, 27987.06568350100, 33611.17563268040],
                                            # by Denton Gentry
                                            [24559.22296032370, 28486.41630764780, 34377.20632863400],
                                            # by Denton Gentry
                                            [24873.50086531350, 28983.77931212480, 35149.19698234180],
                                            # by Denton Gentry
                                            [25106.77343971480, 29418.01130671760, 35884.86810722180],
                                            # by Denton Gentry
                                            [25474.03925080400, 29974.04172990800, 36724.04544856410],
                                            # by Denton Gentry
                                            [25757.53210334390, 30467.52015487140, 37532.50223216260],
                                            # by Denton Gentry
                                            [26028.43600103900, 30960.32916785810, 38358.16891808690],
                                            # by Denton Gentry
                                            [26286.06118803210, 31452.81963829250, 39202.95731368320],
                                            # by Denton Gentry
                                            [26667.01680436810, 31967.50398214730, 39918.23474881610],
                                            # by Denton Gentry
                                            [26760.07165096690, 32438.22297231480, 40955.44995433650],
                                            # by Denton Gentry
                                            [26976.35653955240, 32931.80139810800, 41864.96868594150],
                                            # by Denton Gentry
                                            [27179.13131235010, 33426.44119216750, 42797.40601189360],
                                            # by Denton Gentry
                                            [27368.83072197670, 33922.51782307470, 43753.04847472170],
                                            # by Denton Gentry
                                            [27593.71832436790, 34466.79329460910, 44776.40574997090],
                                            # by Denton Gentry
                                            [27711.11597367610, 34920.39843102430, 45734.32211704650],
                                            # by Denton Gentry
                                            [27864.80061703530, 35422.84801725060, 46759.91911757340],
                                            # by Denton Gentry
                                            [28007.59409679600, 35928.09819059130, 47808.85433128430],
                                            # by Denton Gentry
                                            [28140.00574417140, 36436.50786680970, 48881.26105076720],
                                            # by Denton Gentry
                                            [28017.97372320970, 36891.04484226660, 50200.65152085190],
                                            # by Denton Gentry
                                            [28375.16417279290, 37464.13317103220, 51097.58666839120],
                                            # by Denton Gentry
                                            [28478.28122079030, 37983.94051696300, 52242.42946122200],
                                            # by Denton Gentry
                                            [28571.70018867370, 38508.07277194310, 53412.63164684720],
                                            # by Denton Gentry
                                            [28655.13141730760, 39036.73739023780, 54609.14634963310],
                                            # by Denton Gentry
                                            [28752.04572015840, 39594.41319952840, 55857.96441858320],
                                            # by Denton Gentry
                                            [28789.94301463300, 40108.55516020810, 57086.47337857060],
                                            # by Denton Gentry
                                            [28839.79966520910, 40652.21519000360, 58370.83847719530],
                                            # by Denton Gentry
                                            [28876.55717765950, 41201.36348823150, 59688.57295408940],
                                            # by Denton Gentry
                                            [28898.87020865570, 41756.22947133940, 61042.26836536490],
                                            # by Denton Gentry
                                            [28960.97437134250, 42313.59819634810, 62342.53393385650],
                                            # by Denton Gentry
                                            [28893.63186870560, 42884.05351472140, 63869.68598374510],
                                            # by Denton Gentry
                                            [28862.25387067750, 43457.50335665930, 65350.37758563210],
                                            # by Denton Gentry
                                            [28808.69168916850, 44037.50938400400, 66880.73592625720],
                                            # by Denton Gentry
                                            [28730.38133221740, 44624.15179991760, 68464.80750146790],
                                            # by Denton Gentry
                                            [28624.60608540430, 45217.56392241990, 70107.00067794340],
                                            # by Denton Gentry
                                            [28488.54531831960, 45817.97637081680, 71812.12294956260],
                                            # by Denton Gentry
                                            [28319.27589876760, 46425.70365916020, 73585.34529974900],
                                            # by Denton Gentry
                                            [28113.74078850430, 47041.07418352010, 75432.07427604380],
                                            # by Denton Gentry
                                            [27868.79263012730, 47664.45901828620, 77357.95860052450],
                                            # by Denton Gentry
                                            [27581.20168953220, 48296.23338953970,
                                             79368.78093955100]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!BV50:BZ96  # by Denton Gentry
linear_trend_global_list = [['Year', 'x', 'constant', 'adoption'],  # by Denton Gentry
                            [2014, 0.00000000000, 23342.35885961820, 23342.35885961820],  # by Denton Gentry
                            [2015, 866.83539006894, 23342.35885961820, 24209.19424968710],  # by Denton Gentry
                            [2016, 1733.67078013789, 23342.35885961820, 25076.02963975610],  # by Denton Gentry
                            [2017, 2600.50617020683, 23342.35885961820, 25942.86502982500],  # by Denton Gentry
                            [2018, 3467.34156027577, 23342.35885961820, 26809.70041989400],  # by Denton Gentry
                            [2019, 4334.17695034472, 23342.35885961820, 27676.53580996290],  # by Denton Gentry
                            [2020, 5201.01234041366, 23342.35885961820, 28543.37120003180],  # by Denton Gentry
                            [2021, 6067.84773048260, 23342.35885961820, 29410.20659010080],  # by Denton Gentry
                            [2022, 6934.68312055155, 23342.35885961820, 30277.04198016970],  # by Denton Gentry
                            [2023, 7801.51851062049, 23342.35885961820, 31143.87737023870],  # by Denton Gentry
                            [2024, 8668.35390068943, 23342.35885961820, 32010.71276030760],  # by Denton Gentry
                            [2025, 9535.18929075838, 23342.35885961820, 32877.54815037660],  # by Denton Gentry
                            [2026, 10402.02468082730, 23342.35885961820, 33744.38354044550],  # by Denton Gentry
                            [2027, 11268.86007089630, 23342.35885961820, 34611.21893051440],  # by Denton Gentry
                            [2028, 12135.69546096520, 23342.35885961820, 35478.05432058340],  # by Denton Gentry
                            [2029, 13002.53085103410, 23342.35885961820, 36344.88971065230],  # by Denton Gentry
                            [2030, 13869.36624110310, 23342.35885961820, 37211.72510072130],  # by Denton Gentry
                            [2031, 14736.20163117200, 23342.35885961820, 38078.56049079020],  # by Denton Gentry
                            [2032, 15603.03702124100, 23342.35885961820, 38945.39588085920],  # by Denton Gentry
                            [2033, 16469.87241130990, 23342.35885961820, 39812.23127092810],  # by Denton Gentry
                            [2034, 17336.70780137890, 23342.35885961820, 40679.06666099700],  # by Denton Gentry
                            [2035, 18203.54319144780, 23342.35885961820, 41545.90205106600],  # by Denton Gentry
                            [2036, 19070.37858151680, 23342.35885961820, 42412.73744113490],  # by Denton Gentry
                            [2037, 19937.21397158570, 23342.35885961820, 43279.57283120390],  # by Denton Gentry
                            [2038, 20804.04936165460, 23342.35885961820, 44146.40822127280],  # by Denton Gentry
                            [2039, 21670.88475172360, 23342.35885961820, 45013.24361134180],  # by Denton Gentry
                            [2040, 22537.72014179250, 23342.35885961820, 45880.07900141070],  # by Denton Gentry
                            [2041, 23404.55553186150, 23342.35885961820, 46746.91439147960],  # by Denton Gentry
                            [2042, 24271.39092193040, 23342.35885961820, 47613.74978154860],  # by Denton Gentry
                            [2043, 25138.22631199940, 23342.35885961820, 48480.58517161750],  # by Denton Gentry
                            [2044, 26005.06170206830, 23342.35885961820, 49347.42056168650],  # by Denton Gentry
                            [2045, 26871.89709213720, 23342.35885961820, 50214.25595175540],  # by Denton Gentry
                            [2046, 27738.73248220620, 23342.35885961820, 51081.09134182440],  # by Denton Gentry
                            [2047, 28605.56787227510, 23342.35885961820, 51947.92673189330],  # by Denton Gentry
                            [2048, 29472.40326234410, 23342.35885961820, 52814.76212196230],  # by Denton Gentry
                            [2049, 30339.23865241300, 23342.35885961820, 53681.59751203120],  # by Denton Gentry
                            [2050, 31206.07404248200, 23342.35885961820, 54548.43290210010],  # by Denton Gentry
                            [2051, 32072.90943255090, 23342.35885961820, 55415.26829216910],  # by Denton Gentry
                            [2052, 32939.74482261980, 23342.35885961820, 56282.10368223800],  # by Denton Gentry
                            [2053, 33806.58021268880, 23342.35885961820, 57148.93907230700],  # by Denton Gentry
                            [2054, 34673.41560275770, 23342.35885961820, 58015.77446237590],  # by Denton Gentry
                            [2055, 35540.25099282670, 23342.35885961820, 58882.60985244490],  # by Denton Gentry
                            [2056, 36407.08638289560, 23342.35885961820, 59749.44524251380],  # by Denton Gentry
                            [2057, 37273.92177296460, 23342.35885961820, 60616.28063258270],  # by Denton Gentry
                            [2058, 38140.75716303350, 23342.35885961820, 61483.11602265170],  # by Denton Gentry
                            [2059, 39007.59255310240, 23342.35885961820, 62349.95141272060],  # by Denton Gentry
                            [2060, 39874.42794317140, 23342.35885961820, 63216.78680278960]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!CE50:CH96  # by Denton Gentry
poly_degree2_trend_global_list = [['Year', 'x^2', 'x', 'constant', 'adoption'],  # by Denton Gentry
                                  [2014, 0.00000000000, 0.00000000000, 23408.06113995680, 23408.06113995680],
                                  # by Denton Gentry
                                  [2015, 0.23134605753, 856.65616353760, 23408.06113995680, 24264.94864955200],
                                  # by Denton Gentry
                                  [2016, 0.92538423012, 1713.31232707521, 23408.06113995680, 25122.29885126210],
                                  # by Denton Gentry
                                  [2017, 2.08211451777, 2569.96849061281, 23408.06113995680, 25980.11174508740],
                                  # by Denton Gentry
                                  [2018, 3.70153692049, 3426.62465415042, 23408.06113995680, 26838.38733102770],
                                  # by Denton Gentry
                                  [2019, 5.78365143826, 4283.28081768802, 23408.06113995680, 27697.12560908310],
                                  # by Denton Gentry
                                  [2020, 8.32845807110, 5139.93698122563, 23408.06113995680, 28556.32657925350],
                                  # by Denton Gentry
                                  [2021, 11.33595681899, 5996.59314476323, 23408.06113995680, 29415.99024153900],
                                  # by Denton Gentry
                                  [2022, 14.80614768195, 6853.24930830083, 23408.06113995680, 30276.11659593960],
                                  # by Denton Gentry
                                  [2023, 18.73903065997, 7709.90547183844, 23408.06113995680, 31136.70564245520],
                                  # by Denton Gentry
                                  [2024, 23.13460575304, 8566.56163537604, 23408.06113995680, 31997.75738108590],
                                  # by Denton Gentry
                                  [2025, 27.99287296118, 9423.21779891365, 23408.06113995680, 32859.27181183160],
                                  # by Denton Gentry
                                  [2026, 33.31383228438, 10279.87396245130, 23408.06113995680, 33721.24893469250],
                                  # by Denton Gentry
                                  [2027, 39.09748372264, 11136.53012598890, 23408.06113995680, 34583.68874966830],
                                  # by Denton Gentry
                                  [2028, 45.34382727597, 11993.18628952650, 23408.06113995680, 35446.59125675920],
                                  # by Denton Gentry
                                  [2029, 52.05286294435, 12849.84245306410, 23408.06113995680, 36309.95645596520],
                                  # by Denton Gentry
                                  [2030, 59.22459072779, 13706.49861660170, 23408.06113995680, 37173.78434728630],
                                  # by Denton Gentry
                                  [2031, 66.85901062630, 14563.15478013930, 23408.06113995680, 38038.07493072240],
                                  # by Denton Gentry
                                  [2032, 74.95612263986, 15419.81094367690, 23408.06113995680, 38902.82820627360],
                                  # by Denton Gentry
                                  [2033, 83.51592676849, 16276.46710721450, 23408.06113995680, 39768.04417393980],
                                  # by Denton Gentry
                                  [2034, 92.53842301217, 17133.12327075210, 23408.06113995680, 40633.72283372110],
                                  # by Denton Gentry
                                  [2035, 102.02361137092, 17989.77943428970, 23408.06113995680, 41499.86418561740],
                                  # by Denton Gentry
                                  [2036, 111.97149184473, 18846.43559782730, 23408.06113995680, 42366.46822962880],
                                  # by Denton Gentry
                                  [2037, 122.38206443360, 19703.09176136490, 23408.06113995680, 43233.53496575530],
                                  # by Denton Gentry
                                  [2038, 133.25532913753, 20559.74792490250, 23408.06113995680, 44101.06439399690],
                                  # by Denton Gentry
                                  [2039, 144.59128595652, 21416.40408844010, 23408.06113995680, 44969.05651435340],
                                  # by Denton Gentry
                                  [2040, 156.38993489058, 22273.06025197770, 23408.06113995680, 45837.51132682510],
                                  # by Denton Gentry
                                  [2041, 168.65127593969, 23129.71641551530, 23408.06113995680, 46706.42883141180],
                                  # by Denton Gentry
                                  [2042, 181.37530910386, 23986.37257905290, 23408.06113995680, 47575.80902811360],
                                  # by Denton Gentry
                                  [2043, 194.56203438310, 24843.02874259050, 23408.06113995680, 48445.65191693040],
                                  # by Denton Gentry
                                  [2044, 208.21145177739, 25699.68490612810, 23408.06113995680, 49315.95749786230],
                                  # by Denton Gentry
                                  [2045, 222.32356128675, 26556.34106966570, 23408.06113995680, 50186.72577090930],
                                  # by Denton Gentry
                                  [2046, 236.89836291117, 27412.99723320330, 23408.06113995680, 51057.95673607130],
                                  # by Denton Gentry
                                  [2047, 251.93585665065, 28269.65339674090, 23408.06113995680, 51929.65039334840],
                                  # by Denton Gentry
                                  [2048, 267.43604250519, 29126.30956027850, 23408.06113995680, 52801.80674274050],
                                  # by Denton Gentry
                                  [2049, 283.39892047479, 29982.96572381610, 23408.06113995680, 53674.42578424780],
                                  # by Denton Gentry
                                  [2050, 299.82449055945, 30839.62188735380, 23408.06113995680, 54547.50751787000],
                                  # by Denton Gentry
                                  [2051, 316.71275275917, 31696.27805089140, 23408.06113995680, 55421.05194360730],
                                  # by Denton Gentry
                                  [2052, 334.06370707395, 32552.93421442900, 23408.06113995680, 56295.05906145970],
                                  # by Denton Gentry
                                  [2053, 351.87735350379, 33409.59037796660, 23408.06113995680, 57169.52887142720],
                                  # by Denton Gentry
                                  [2054, 370.15369204870, 34266.24654150420, 23408.06113995680, 58044.46137350970],
                                  # by Denton Gentry
                                  [2055, 388.89272270866, 35122.90270504180, 23408.06113995680, 58919.85656770720],
                                  # by Denton Gentry
                                  [2056, 408.09444548369, 35979.55886857940, 23408.06113995680, 59795.71445401990],
                                  # by Denton Gentry
                                  [2057, 427.75886037378, 36836.21503211700, 23408.06113995680, 60672.03503244760],
                                  # by Denton Gentry
                                  [2058, 447.88596737893, 37692.87119565460, 23408.06113995680, 61548.81830299030],
                                  # by Denton Gentry
                                  [2059, 468.47576649913, 38549.52735919220, 23408.06113995680, 62426.06426564820],
                                  # by Denton Gentry
                                  [2060, 489.52825773440, 39406.18352272980, 23408.06113995680,
                                   63303.77292042100]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!CM50:CQ96  # by Denton Gentry
poly_degree3_trend_global_list = [['Year', 'x^3', 'x^2', 'x', 'constant', 'adoption'],  # by Denton Gentry
                                  [2014, 0.00000000000, 0.00000000000, 0.00000000000, 23393.49730928790,
                                   23393.49730928790],  # by Denton Gentry
                                  [2015, 0.00533005075, -0.12043729196, 862.47764496660, 23393.49730928790,
                                   24255.85984701330],  # by Denton Gentry
                                  [2016, 0.04264040600, -0.48174916784, 1724.95528993319, 23393.49730928790,
                                   25118.01349045930],  # by Denton Gentry
                                  [2017, 0.14391137025, -1.08393562764, 2587.43293489979, 23393.49730928790,
                                   25979.99021993030],  # by Denton Gentry
                                  [2018, 0.34112324799, -1.92699667136, 3449.91057986638, 23393.49730928790,
                                   26841.82201573090],  # by Denton Gentry
                                  [2019, 0.66625634373, -3.01093229900, 4312.38822483298, 23393.49730928790,
                                   27703.54085816560],  # by Denton Gentry
                                  [2020, 1.15129096197, -4.33574251056, 5174.86586979957, 23393.49730928790,
                                   28565.17872753890],  # by Denton Gentry
                                  [2021, 1.82820740720, -5.90142730604, 6037.34351476617, 23393.49730928790,
                                   29426.76760415520],  # by Denton Gentry
                                  [2022, 2.72898598393, -7.70798668544, 6899.82115973276, 23393.49730928790,
                                   30288.33946831920],  # by Denton Gentry
                                  [2023, 3.88560699664, -9.75542064875, 7762.29880469936, 23393.49730928790,
                                   31149.92630033520],  # by Denton Gentry
                                  [2024, 5.33005074985, -12.04372919599, 8624.77644966595, 23393.49730928790,
                                   32011.56008050770],  # by Denton Gentry
                                  [2025, 7.09429754806, -14.57291232715, 9487.25409463255, 23393.49730928790,
                                   32873.27278914140],  # by Denton Gentry
                                  [2026, 9.21032769575, -17.34297004223, 10349.73173959910, 23393.49730928790,
                                   33735.09640654060],  # by Denton Gentry
                                  [2027, 11.71012149743, -20.35390234123, 11212.20938456570, 23393.49730928790,
                                   34597.06291300990],  # by Denton Gentry
                                  [2028, 14.62565925760, -23.60570922415, 12074.68702953230, 23393.49730928790,
                                   35459.20428885370],  # by Denton Gentry
                                  [2029, 17.98892128076, -27.09839069099, 12937.16467449890, 23393.49730928790,
                                   36321.55251437660],  # by Denton Gentry
                                  [2030, 21.83188787140, -30.83194674174, 13799.64231946550, 23393.49730928790,
                                   37184.13956988310],  # by Denton Gentry
                                  [2031, 26.18653933403, -34.80637737642, 14662.11996443210, 23393.49730928790,
                                   38046.99743567760],  # by Denton Gentry
                                  [2032, 31.08485597315, -39.02168259502, 15524.59760939870, 23393.49730928790,
                                   38910.15809206480],  # by Denton Gentry
                                  [2033, 36.55881809325, -43.47786239754, 16387.07525436530, 23393.49730928790,
                                   39773.65351934890],  # by Denton Gentry
                                  [2034, 42.64040599883, -48.17491678397, 17249.55289933190, 23393.49730928790,
                                   40637.51569783470],  # by Denton Gentry
                                  [2035, 49.36159999440, -53.11284575433, 18112.03054429850, 23393.49730928790,
                                   41501.77660782650],  # by Denton Gentry
                                  [2036, 56.75438038445, -58.29164930861, 18974.50818926510, 23393.49730928790,
                                   42366.46822962880],  # by Denton Gentry
                                  [2037, 64.85072747347, -63.71132744681, 19836.98583423170, 23393.49730928790,
                                   43231.62254354630],  # by Denton Gentry
                                  [2038, 73.68262156598, -69.37188016892, 20699.46347919830, 23393.49730928790,
                                   44097.27152988330],  # by Denton Gentry
                                  [2039, 83.28204296647, -75.27330747496, 21561.94112416490, 23393.49730928790,
                                   44963.44716894430],  # by Denton Gentry
                                  [2040, 93.68097197943, -81.41560936492, 22424.41876913150, 23393.49730928790,
                                   45830.18144103390],  # by Denton Gentry
                                  [2041, 104.91138890938, -87.79878583879, 23286.89641409810, 23393.49730928790,
                                   46697.50632645660],  # by Denton Gentry
                                  [2042, 117.00527406079, -94.42283689659, 24149.37405906470, 23393.49730928790,
                                   47565.45380551680],  # by Denton Gentry
                                  [2043, 129.99460773819, -101.28776253831, 25011.85170403130, 23393.49730928790,
                                   48434.05585851910],  # by Denton Gentry
                                  [2044, 143.91137024606, -108.39356276394, 25874.32934899790, 23393.49730928790,
                                   49303.34446576790],  # by Denton Gentry
                                  [2045, 158.78754188890, -115.74023757350, 26736.80699396450, 23393.49730928790,
                                   50173.35160756780],  # by Denton Gentry
                                  [2046, 174.65510297122, -123.32778696697, 27599.28463893100, 23393.49730928790,
                                   51044.10926422320],  # by Denton Gentry
                                  [2047, 191.54603379750, -131.15621094437, 28461.76228389760, 23393.49730928790,
                                   51915.64941603870],  # by Denton Gentry
                                  [2048, 209.49231467226, -139.22550950569, 29324.23992886420, 23393.49730928790,
                                   52788.00404331870],  # by Denton Gentry
                                  [2049, 228.52592589999, -147.53568265092, 30186.71757383080, 23393.49730928790,
                                   53661.20512636780],  # by Denton Gentry
                                  [2050, 248.67884778519, -156.08673038008, 31049.19521879740, 23393.49730928790,
                                   54535.28464549050],  # by Denton Gentry
                                  [2051, 269.98306063235, -164.87865269315, 31911.67286376400, 23393.49730928790,
                                   55410.27458099110],  # by Denton Gentry
                                  [2052, 292.47054474599, -173.91144959015, 32774.15050873060, 23393.49730928790,
                                   56286.20691317440],  # by Denton Gentry
                                  [2053, 316.17328043059, -183.18512107106, 33636.62815369720, 23393.49730928790,
                                   57163.11362234470],  # by Denton Gentry
                                  [2054, 341.12324799065, -192.69966713590, 34499.10579866380, 23393.49730928790,
                                   58041.02668880650],  # by Denton Gentry
                                  [2055, 367.35242773069, -202.45508778465, 35361.58344363040, 23393.49730928790,
                                   58919.97809286430],  # by Denton Gentry
                                  [2056, 394.89279995518, -212.45138301733, 36224.06108859700, 23393.49730928790,
                                   59799.99981482280],  # by Denton Gentry
                                  [2057, 423.77634496864, -222.68855283392, 37086.53873356360, 23393.49730928790,
                                   60681.12383498620],  # by Denton Gentry
                                  [2058, 454.03504307556, -233.16659723444, 37949.01637853020, 23393.49730928790,
                                   61563.38213365920],  # by Denton Gentry
                                  [2059, 485.70087458044, -243.88551621887, 38811.49402349680, 23393.49730928790,
                                   62446.80669114630],  # by Denton Gentry
                                  [2060, 518.80581978779, -254.84530978722, 39673.97166846340, 23393.49730928790,
                                   63331.42948775190]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!CM50:CQ96  # by Denton Gentry
exponential_trend_global_list = [['Year', 'coeff', 'e^x', 'adoption'],  # by Denton Gentry
                                 [2014, 25215.39478371480, 1.00000000000, 25215.39478371480],  # by Denton Gentry
                                 [2015, 25215.39478371480, 1.02181094263, 25765.36631271950],  # by Denton Gentry
                                 [2016, 25215.39478371480, 1.04409760248, 26327.33323919100],  # by Denton Gentry
                                 [2017, 25215.39478371480, 1.06687035538, 26901.55719405540],  # by Denton Gentry
                                 [2018, 25215.39478371480, 1.09013980350, 27488.30551465580],  # by Denton Gentry
                                 [2019, 25215.39478371480, 1.11391678021, 28087.85136921470],  # by Denton Gentry
                                 [2020, 25215.39478371480, 1.13821235520, 28700.47388401100],  # by Denton Gentry
                                 [2021, 25215.39478371480, 1.16303783958, 29326.45827333110],  # by Denton Gentry
                                 [2022, 25215.39478371480, 1.18840479117, 29966.09597225340],  # by Denton Gentry
                                 [2023, 25215.39478371480, 1.21432501989, 30619.68477233060],  # by Denton Gentry
                                 [2024, 25215.39478371480, 1.24081059323, 31287.52896022940],  # by Denton Gentry
                                 [2025, 25215.39478371480, 1.26787384190, 31969.93945939590],  # by Denton Gentry
                                 [2026, 25215.39478371480, 1.29552736552, 32667.23397480930],  # by Denton Gentry
                                 [2027, 25215.39478371480, 1.32378403857, 33379.73714089420],  # by Denton Gentry
                                 [2028, 25215.39478371480, 1.35265701629, 34107.78067265790],  # by Denton Gentry
                                 [2029, 25215.39478371480, 1.38215974087, 34851.70352012450],  # by Denton Gentry
                                 [2030, 25215.39478371480, 1.41230594768, 35611.85202613790],  # by Denton Gentry
                                 [2031, 25215.39478371480, 1.44310967168, 36388.58008760580],  # by Denton Gentry
                                 [2032, 25215.39478371480, 1.47458525394, 37182.24932026100],  # by Denton Gentry
                                 [2033, 25215.39478371480, 1.50674734831, 37993.22922701630],  # by Denton Gentry
                                 [2034, 25215.39478371480, 1.53961092828, 38821.89736999140],  # by Denton Gentry
                                 [2035, 25215.39478371480, 1.57319129391, 39668.63954629170],  # by Denton Gentry
                                 [2036, 25215.39478371480, 1.60750407897, 40533.84996762130],  # by Denton Gentry
                                 [2037, 25215.39478371480, 1.64256525821, 41417.93144381270],  # by Denton Gentry
                                 [2038, 25215.39478371480, 1.67839115482, 42321.29557036110],  # by Denton Gentry
                                 [2039, 25215.39478371480, 1.71499844801, 43244.36292004700],  # by Denton Gentry
                                 [2040, 25215.39478371480, 1.75240418077, 44187.56323874000],  # by Denton Gentry
                                 [2041, 25215.39478371480, 1.79062576782, 45151.33564547200],  # by Denton Gentry
                                 [2042, 25215.39478371480, 1.82968100371, 46136.12883687510],  # by Denton Gentry
                                 [2043, 25215.39478371480, 1.86958807111, 47142.40129607760],  # by Denton Gentry
                                 [2044, 25215.39478371480, 1.91036554927, 48170.62150615730],  # by Denton Gentry
                                 [2045, 25215.39478371480, 1.95203242267, 49221.26816824940],  # by Denton Gentry
                                 [2046, 25215.39478371480, 1.99460808985, 50294.83042441210],  # by Denton Gentry
                                 [2047, 25215.39478371480, 2.03811237247, 51391.80808535310],  # by Denton Gentry
                                 [2048, 25215.39478371480, 2.08256552450, 52512.71186312260],  # by Denton Gentry
                                 [2049, 25215.39478371480, 2.12798824167, 53658.06360888200],  # by Denton Gentry
                                 [2050, 25215.39478371480, 2.17440167113, 54828.39655585860],  # by Denton Gentry
                                 [2051, 25215.39478371480, 2.22182742123, 56024.25556759910],  # by Denton Gentry
                                 [2052, 25215.39478371480, 2.27028757165, 57246.19739163740],  # by Denton Gentry
                                 [2053, 25215.39478371480, 2.31980468362, 58494.79091869620],  # by Denton Gentry
                                 [2054, 25215.39478371480, 2.37040181049, 59770.61744754120],  # by Denton Gentry
                                 [2055, 25215.39478371480, 2.42210250839, 61074.27095561180],  # by Denton Gentry
                                 [2056, 25215.39478371480, 2.47493084724, 62406.35837555550],  # by Denton Gentry
                                 [2057, 25215.39478371480, 2.52891142196, 63767.49987779290],  # by Denton Gentry
                                 [2058, 25215.39478371480, 2.58406936390, 65158.32915924610],  # by Denton Gentry
                                 [2059, 25215.39478371480, 2.64043035255, 66579.49373836430],  # by Denton Gentry
                                 [2060, 25215.39478371480, 2.69802062748, 68031.65525658460]]  # by Denton Gentry
# by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!W164:Y212  # by Denton Gentry
forecast_min_max_sd_oecd90_list = [['Min', 'Max', 'S.D'],  # by Denton Gentry
                                   [9127.62395762832, 10305.81652442160, 389.38280736543],  # by Denton Gentry
                                   [9016.04583411878, 10347.79666328460, 441.53314924355],  # by Denton Gentry
                                   [8874.32776777484, 10407.89374939750, 494.61900968016],  # by Denton Gentry
                                   [8796.37401713529, 10521.49563140290, 550.44832532096],  # by Denton Gentry
                                   [8734.57241775790, 10634.44654265380, 604.49537600318],  # by Denton Gentry
                                   [8688.56759635354, 10746.75661338890, 655.68993827157],  # by Denton Gentry
                                   [8658.11693700063, 10858.49732919750, 703.58808217616],  # by Denton Gentry
                                   [8643.05060245260, 10969.79321817380, 748.10119131488],  # by Denton Gentry
                                   [8666.26490465072, 11080.75427903240, 801.91871406785],  # by Denton Gentry
                                   [8657.96963110739, 11198.34735226450, 827.15279009955],  # by Denton Gentry
                                   [8678.08940995974, 11315.62562419770, 862.50693304821],  # by Denton Gentry
                                   [8705.51175346151, 11432.72635300350, 895.79603788713],  # by Denton Gentry
                                   [8744.67217338976, 11549.82221168050, 927.41524870068],  # by Denton Gentry
                                   [8795.30319733258, 11667.04556762920, 955.40432806037],  # by Denton Gentry
                                   [8857.11071827981, 11781.35995132360, 986.36090127399],  # by Denton Gentry
                                   [8929.73694931189, 11895.86363700740, 1014.40119420254],  # by Denton Gentry
                                   [9012.76618524292, 12010.53033091740, 1042.18513713588],  # by Denton Gentry
                                   [9105.73922952436, 12125.29745364510, 1069.98311977894],  # by Denton Gentry
                                   [8990.47589335468, 12240.11206333870, 1105.93930193796],  # by Denton Gentry
                                   [9153.11818586900, 12343.06537200080, 1123.86813120645],  # by Denton Gentry
                                   [9158.41783783632, 12580.62444539470, 1150.49997915159],  # by Denton Gentry
                                   [9167.26452172009, 12820.19439016820, 1177.96851464040],  # by Denton Gentry
                                   [9179.94925725267, 13060.58802423910, 1206.28008011380],  # by Denton Gentry
                                   [9196.78407016096, 13300.63186910300, 1235.39326445214],  # by Denton Gentry
                                   [9218.10685549866, 13539.18117187920, 1263.56758262112],  # by Denton Gentry
                                   [9244.29067774833, 13775.11917473040, 1292.26214392160],  # by Denton Gentry
                                   [9275.72920508549, 14007.33543183450, 1321.33424977222],  # by Denton Gentry
                                   [9312.83517378283, 14234.73382644230, 1350.62003229283],  # by Denton Gentry
                                   [9462.84592479344, 14454.03899715580, 1363.95781392433],  # by Denton Gentry
                                   [9405.64447791244, 14670.68521633800, 1409.63931896483],  # by Denton Gentry
                                   [9462.09790937527, 14877.02901530950, 1438.91543232762],  # by Denton Gentry
                                   [9525.73363781504, 15074.10111588930, 1467.63062043672],  # by Denton Gentry
                                   [9527.56931196257, 15260.74275705290, 1495.66344471769],  # by Denton Gentry
                                   [9528.67566069747, 15435.82407646980, 1522.93144578080],  # by Denton Gentry
                                   [9530.97562076883, 15598.23031284050, 1548.64212362661],  # by Denton Gentry
                                   [9534.64943141713, 15746.91594825540, 1573.53809492122],  # by Denton Gentry
                                   [9539.93833586131, 15880.90969785490, 1597.71736100204],  # by Denton Gentry
                                   [9547.11317166921, 15999.28867498900, 1621.35981801658],  # by Denton Gentry
                                   [9556.05597733818, 16101.29131664080, 1651.76897733206],  # by Denton Gentry
                                   [9567.99249469952, 16185.29816921970, 1668.21103718492],  # by Denton Gentry
                                   [9581.98510826246, 16250.80876408030, 1692.26452526217],  # by Denton Gentry
                                   [9598.49005784416, 16296.54505954920, 1717.49696492070],  # by Denton Gentry
                                   [9617.58712735764, 16321.40408847390, 1744.63632716120],  # by Denton Gentry
                                   [9639.36417338464, 16324.28861465850, 1774.54116527504],  # by Denton Gentry
                                   [9663.95183295188, 16304.13465731970, 1808.20260847494],  # by Denton Gentry
                                   [9691.48103551797, 16259.87738904200, 1846.73751431201],  # by Denton Gentry
                                   [9722.03588746750, 16190.41487239170, 1891.36889679212],  # by Denton Gentry
                                   [9755.68786960494, 16094.63482700170, 1943.40172618808],  # by Denton Gentry
                                   [9792.52066297022, 16171.32463596520, 2005.10293863081]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!AA187:AC212  # by Denton Gentry
forecast_low_med_high_oecd90_list = [['Low', 'Medium', 'High'],  # by Denton Gentry
                                     [9218.52769374160, 9607.91050110703, 9997.29330847246],  # by Denton Gentry
                                     [9203.31092504407, 9644.84407428763, 10086.37722353120],  # by Denton Gentry
                                     [9136.32230532125, 9630.94131500141, 10125.56032468160],  # by Denton Gentry
                                     [9120.51761417780, 9670.96593949876, 10221.41426481970],  # by Denton Gentry
                                     [9109.80362435594, 9714.29900035912, 10318.79437636230],  # by Denton Gentry
                                     [9105.16186761303, 9760.85180588460, 10416.54174415620],  # by Denton Gentry
                                     [9107.04958482341, 9810.63766699957, 10514.22574917570],  # by Denton Gentry
                                     [9115.64218637196, 9863.74337768683, 10611.84456900170],  # by Denton Gentry
                                     [9143.36532690941, 9945.28404097726, 10747.20275504510],  # by Denton Gentry
                                     [9151.77892819502, 9978.93171829457, 10806.08450839410],  # by Denton Gentry
                                     [9178.27026019878, 10040.77719324700, 10903.28412629520],  # by Denton Gentry
                                     [9209.94086809270, 10105.73690597980, 11001.53294386700],  # by Denton Gentry
                                     [9246.40253677163, 10173.81778547230, 11101.23303417300],  # by Denton Gentry
                                     [9283.46115506554, 10238.86548312590, 11194.26981118630],  # by Denton Gentry
                                     [9332.16925998383, 10318.53016125780, 11304.89106253180],  # by Denton Gentry
                                     [9380.53788074950, 10394.93907495200, 11409.34026915460],  # by Denton Gentry
                                     [9431.83593315484, 10474.02107029070, 11516.20620742660],  # by Denton Gentry
                                     [9485.55648778953, 10555.53960756850, 11625.52272734740],  # by Denton Gentry
                                     [9493.85053683449, 10599.78983877240, 11705.72914071040],  # by Denton Gentry
                                     [9597.90419309269, 10721.77232429910, 11845.64045550560],  # by Denton Gentry
                                     [9655.71204923602, 10806.21202838760, 11956.71200753920],  # by Denton Gentry
                                     [9714.42460233336, 10892.39311697380, 12070.36163161420],  # by Denton Gentry
                                     [9773.81854713124, 10980.09862724500, 12186.37870735880],  # by Denton Gentry
                                     [9833.73720671392, 11069.13047116610, 12304.52373561820],  # by Denton Gentry
                                     [9896.12115387439, 11159.68873649550, 12423.25631911660],  # by Denton Gentry
                                     [9959.00443991999, 11251.26658384160, 12543.52872776320],  # by Denton Gentry
                                     [10022.40999454600, 11343.74424431830, 12665.07849409050],  # by Denton Gentry
                                     [10086.40045321460, 11437.02048550740, 12787.64051780030],  # by Denton Gentry
                                     [10211.23907656650, 11575.19689049080, 12939.15470441520],  # by Denton Gentry
                                     [10217.81033049630, 11627.44964946120, 13037.08896842600],  # by Denton Gentry
                                     [10285.42642994550, 11724.34186227310, 13163.25729460070],  # by Denton Gentry
                                     [10353.87963921050, 11821.51025964720, 13289.14088008390],  # by Denton Gentry
                                     [10423.12916002270, 11918.79260474040, 13414.45604945810],  # by Denton Gentry
                                     [10493.11453480780, 12016.04598058860, 13538.97742636940],  # by Denton Gentry
                                     [10565.54109366880, 12114.18321729540, 13662.82534092200],  # by Denton Gentry
                                     [10638.51675411640, 12212.05484903760, 13785.59294395880],  # by Denton Gentry
                                     [10711.92251711930, 12309.63987812130, 13907.35723912330],  # by Denton Gentry
                                     [10785.59740694710, 12406.95722496370, 14028.31704298030],  # by Denton Gentry
                                     [10828.89985620100, 12480.66883353300, 14132.43781086510],  # by Denton Gentry
                                     [10932.43800463960, 12600.64904182450, 14268.86007900950],  # by Denton Gentry
                                     [11004.52562828180, 12696.79015354390, 14389.05467880610],  # by Denton Gentry
                                     [11074.76140874530, 12792.25837366600, 14509.75533858670],  # by Denton Gentry
                                     [11142.23586063170, 12886.87218779290, 14631.50851495410],  # by Denton Gentry
                                     [11205.91540207520, 12980.45656735030, 14754.99773262530],  # by Denton Gentry
                                     [11264.67722976460, 13072.87983823960, 14881.08244671450],  # by Denton Gentry
                                     [11317.27256779310, 13164.01008210510, 15010.74759641720],  # by Denton Gentry
                                     [11362.29626119870, 13253.66515799080, 15145.03405478290],  # by Denton Gentry
                                     [11398.24590915540, 13341.64763534350, 15285.04936153150],  # by Denton Gentry
                                     [11427.56040162820, 13432.66334025910, 15437.76627888990]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'BV168:BZ214  # by Denton Gentry
linear_trend_oecd90_list = [['Year', 'x', 'constant', 'adoption'],  # by Denton Gentry
                            [2014, 0.00000000000, 9419.20248635240, 9419.20248635240],  # by Denton Gentry
                            [2015, 84.48939237106, 9419.20248635240, 9503.69187872345],  # by Denton Gentry
                            [2016, 168.97878474211, 9419.20248635240, 9588.18127109451],  # by Denton Gentry
                            [2017, 253.46817711317, 9419.20248635240, 9672.67066346557],  # by Denton Gentry
                            [2018, 337.95756948422, 9419.20248635240, 9757.16005583662],  # by Denton Gentry
                            [2019, 422.44696185528, 9419.20248635240, 9841.64944820768],  # by Denton Gentry
                            [2020, 506.93635422634, 9419.20248635240, 9926.13884057873],  # by Denton Gentry
                            [2021, 591.42574659739, 9419.20248635240, 10010.62823294980],  # by Denton Gentry
                            [2022, 675.91513896845, 9419.20248635240, 10095.11762532080],  # by Denton Gentry
                            [2023, 760.40453133950, 9419.20248635240, 10179.60701769190],  # by Denton Gentry
                            [2024, 844.89392371056, 9419.20248635240, 10264.09641006300],  # by Denton Gentry
                            [2025, 929.38331608162, 9419.20248635240, 10348.58580243400],  # by Denton Gentry
                            [2026, 1013.87270845267, 9419.20248635240, 10433.07519480510],  # by Denton Gentry
                            [2027, 1098.36210082373, 9419.20248635240, 10517.56458717610],  # by Denton Gentry
                            [2028, 1182.85149319478, 9419.20248635240, 10602.05397954720],  # by Denton Gentry
                            [2029, 1267.34088556584, 9419.20248635240, 10686.54337191820],  # by Denton Gentry
                            [2030, 1351.83027793690, 9419.20248635240, 10771.03276428930],  # by Denton Gentry
                            [2031, 1436.31967030795, 9419.20248635240, 10855.52215666040],  # by Denton Gentry
                            [2032, 1520.80906267901, 9419.20248635240, 10940.01154903140],  # by Denton Gentry
                            [2033, 1605.29845505006, 9419.20248635240, 11024.50094140250],  # by Denton Gentry
                            [2034, 1689.78784742112, 9419.20248635240, 11108.99033377350],  # by Denton Gentry
                            [2035, 1774.27723979217, 9419.20248635240, 11193.47972614460],  # by Denton Gentry
                            [2036, 1858.76663216323, 9419.20248635240, 11277.96911851560],  # by Denton Gentry
                            [2037, 1943.25602453429, 9419.20248635240, 11362.45851088670],  # by Denton Gentry
                            [2038, 2027.74541690534, 9419.20248635240, 11446.94790325770],  # by Denton Gentry
                            [2039, 2112.23480927640, 9419.20248635240, 11531.43729562880],  # by Denton Gentry
                            [2040, 2196.72420164745, 9419.20248635240, 11615.92668799990],  # by Denton Gentry
                            [2041, 2281.21359401851, 9419.20248635240, 11700.41608037090],  # by Denton Gentry
                            [2042, 2365.70298638957, 9419.20248635240, 11784.90547274200],  # by Denton Gentry
                            [2043, 2450.19237876062, 9419.20248635240, 11869.39486511300],  # by Denton Gentry
                            [2044, 2534.68177113168, 9419.20248635240, 11953.88425748410],  # by Denton Gentry
                            [2045, 2619.17116350273, 9419.20248635240, 12038.37364985510],  # by Denton Gentry
                            [2046, 2703.66055587379, 9419.20248635240, 12122.86304222620],  # by Denton Gentry
                            [2047, 2788.14994824485, 9419.20248635240, 12207.35243459720],  # by Denton Gentry
                            [2048, 2872.63934061590, 9419.20248635240, 12291.84182696830],  # by Denton Gentry
                            [2049, 2957.12873298696, 9419.20248635240, 12376.33121933940],  # by Denton Gentry
                            [2050, 3041.61812535801, 9419.20248635240, 12460.82061171040],  # by Denton Gentry
                            [2051, 3126.10751772907, 9419.20248635240, 12545.31000408150],  # by Denton Gentry
                            [2052, 3210.59691010013, 9419.20248635240, 12629.79939645250],  # by Denton Gentry
                            [2053, 3295.08630247118, 9419.20248635240, 12714.28878882360],  # by Denton Gentry
                            [2054, 3379.57569484224, 9419.20248635240, 12798.77818119460],  # by Denton Gentry
                            [2055, 3464.06508721329, 9419.20248635240, 12883.26757356570],  # by Denton Gentry
                            [2056, 3548.55447958435, 9419.20248635240, 12967.75696593670],  # by Denton Gentry
                            [2057, 3633.04387195541, 9419.20248635240, 13052.24635830780],  # by Denton Gentry
                            [2058, 3717.53326432646, 9419.20248635240, 13136.73575067890],  # by Denton Gentry
                            [2059, 3802.02265669752, 9419.20248635240, 13221.22514304990],  # by Denton Gentry
                            [2060, 3886.51204906857, 9419.20248635240, 13305.71453542100]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!CE168:CH214  # by Denton Gentry
poly_degree2_trend_oecd90_list = [['Year', 'x^2', 'x', 'constant', 'adoption'],  # by Denton Gentry
                                  [2014, 0.00000000000, 0.00000000000, 9591.59776743747, 9591.59776743747],
                                  # by Denton Gentry
                                  [2015, 0.60702563762, 57.78026431562, 9591.59776743747, 9649.98505739072],
                                  # by Denton Gentry
                                  [2016, 2.42810255049, 115.56052863124, 9591.59776743747, 9709.58639861921],
                                  # by Denton Gentry
                                  [2017, 5.46323073861, 173.34079294687, 9591.59776743747, 9770.40179112295],
                                  # by Denton Gentry
                                  [2018, 9.71241020198, 231.12105726249, 9591.59776743747, 9832.43123490194],
                                  # by Denton Gentry
                                  [2019, 15.17564094059, 288.90132157811, 9591.59776743747, 9895.67472995617],
                                  # by Denton Gentry
                                  [2020, 21.85292295445, 346.68158589373, 9591.59776743747, 9960.13227628565],
                                  # by Denton Gentry
                                  [2021, 29.74425624355, 404.46185020935, 9591.59776743747, 10025.80387389040],
                                  # by Denton Gentry
                                  [2022, 38.84964080790, 462.24211452498, 9591.59776743747, 10092.68952277040],
                                  # by Denton Gentry
                                  [2023, 49.16907664750, 520.02237884060, 9591.59776743747, 10160.78922292560],
                                  # by Denton Gentry
                                  [2024, 60.70256376235, 577.80264315622, 9591.59776743747, 10230.10297435600],
                                  # by Denton Gentry
                                  [2025, 73.45010215244, 635.58290747184, 9591.59776743747, 10300.63077706180],
                                  # by Denton Gentry
                                  [2026, 87.41169181778, 693.36317178746, 9591.59776743747, 10372.37263104270],
                                  # by Denton Gentry
                                  [2027, 102.58733275837, 751.14343610309, 9591.59776743747, 10445.32853629890],
                                  # by Denton Gentry
                                  [2028, 118.97702497421, 808.92370041871, 9591.59776743747, 10519.49849283040],
                                  # by Denton Gentry
                                  [2029, 136.58076846529, 866.70396473433, 9591.59776743747, 10594.88250063710],
                                  # by Denton Gentry
                                  [2030, 155.39856323162, 924.48422904995, 9591.59776743747, 10671.48055971900],
                                  # by Denton Gentry
                                  [2031, 175.43040927319, 982.26449336557, 9591.59776743747, 10749.29267007620],
                                  # by Denton Gentry
                                  [2032, 196.67630659001, 1040.04475768120, 9591.59776743747, 10828.31883170870],
                                  # by Denton Gentry
                                  [2033, 219.13625518208, 1097.82502199682, 9591.59776743747, 10908.55904461640],
                                  # by Denton Gentry
                                  [2034, 242.81025504940, 1155.60528631244, 9591.59776743747, 10990.01330879930],
                                  # by Denton Gentry
                                  [2035, 267.69830619196, 1213.38555062806, 9591.59776743747, 11072.68162425750],
                                  # by Denton Gentry
                                  [2036, 293.80040860977, 1271.16581494368, 9591.59776743747, 11156.56399099090],
                                  # by Denton Gentry
                                  [2037, 321.11656230283, 1328.94607925931, 9591.59776743747, 11241.66040899960],
                                  # by Denton Gentry
                                  [2038, 349.64676727114, 1386.72634357493, 9591.59776743747, 11327.97087828350],
                                  # by Denton Gentry
                                  [2039, 379.39102351469, 1444.50660789055, 9591.59776743747, 11415.49539884270],
                                  # by Denton Gentry
                                  [2040, 410.34933103349, 1502.28687220617, 9591.59776743747, 11504.23397067710],
                                  # by Denton Gentry
                                  [2041, 442.52168982753, 1560.06713652179, 9591.59776743747, 11594.18659378680],
                                  # by Denton Gentry
                                  [2042, 475.90809989682, 1617.84740083742, 9591.59776743747, 11685.35326817170],
                                  # by Denton Gentry
                                  [2043, 510.50856124136, 1675.62766515304, 9591.59776743747, 11777.73399383190],
                                  # by Denton Gentry
                                  [2044, 546.32307386115, 1733.40792946866, 9591.59776743747, 11871.32877076730],
                                  # by Denton Gentry
                                  [2045, 583.35163775618, 1791.18819378428, 9591.59776743747, 11966.13759897790],
                                  # by Denton Gentry
                                  [2046, 621.59425292646, 1848.96845809990, 9591.59776743747, 12062.16047846380],
                                  # by Denton Gentry
                                  [2047, 661.05091937199, 1906.74872241553, 9591.59776743747, 12159.39740922500],
                                  # by Denton Gentry
                                  [2048, 701.72163709277, 1964.52898673115, 9591.59776743747, 12257.84839126140],
                                  # by Denton Gentry
                                  [2049, 743.60640608879, 2022.30925104677, 9591.59776743747, 12357.51342457300],
                                  # by Denton Gentry
                                  [2050, 786.70522636006, 2080.08951536239, 9591.59776743747, 12458.39250915990],
                                  # by Denton Gentry
                                  [2051, 831.01809790657, 2137.86977967801, 9591.59776743747, 12560.48564502210],
                                  # by Denton Gentry
                                  [2052, 876.54502072833, 2195.65004399364, 9591.59776743747, 12663.79283215940],
                                  # by Denton Gentry
                                  [2053, 923.28599482534, 2253.43030830926, 9591.59776743747, 12768.31407057210],
                                  # by Denton Gentry
                                  [2054, 971.24102019760, 2311.21057262488, 9591.59776743747, 12874.04936025990],
                                  # by Denton Gentry
                                  [2055, 1020.41009684510, 2368.99083694050, 9591.59776743747, 12980.99870122310],
                                  # by Denton Gentry
                                  [2056, 1070.79322476785, 2426.77110125612, 9591.59776743747, 13089.16209346140],
                                  # by Denton Gentry
                                  [2057, 1122.39040396585, 2484.55136557175, 9591.59776743747, 13198.53953697510],
                                  # by Denton Gentry
                                  [2058, 1175.20163443909, 2542.33162988737, 9591.59776743747, 13309.13103176390],
                                  # by Denton Gentry
                                  [2059, 1229.22691618759, 2600.11189420299, 9591.59776743747, 13420.93657782800],
                                  # by Denton Gentry
                                  [2060, 1284.46624921132, 2657.89215851861, 9591.59776743747,
                                   13533.95617516740]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!CM168:CQ214  # by Denton Gentry
poly_degree3_trend_oecd90_list = [['Year', 'x^3', 'x^2', 'x', 'constant', 'adoption'],  # by Denton Gentry
                                  [2014, 0.00000000000, 0.00000000000, 0.00000000000, 9649.41539887043,
                                   9649.41539887043],  # by Denton Gentry
                                  [2015, -0.02116001736, 2.00358678335, 34.66929335563, 9649.41539887043,
                                   9686.06711899205],  # by Denton Gentry
                                  [2016, -0.16928013888, 8.01434713339, 69.33858671126, 9649.41539887043,
                                   9726.59905257621],  # by Denton Gentry
                                  [2017, -0.57132046871, 18.03228105012, 104.00788006689, 9649.41539887043,
                                   9770.88423951875],  # by Denton Gentry
                                  [2018, -1.35424111100, 32.05738853355, 138.67717342252, 9649.41539887043,
                                   9818.79571971551],  # by Denton Gentry
                                  [2019, -2.64500216993, 50.08966958368, 173.34646677816, 9649.41539887043,
                                   9870.20653306234],  # by Denton Gentry
                                  [2020, -4.57056374964, 72.12912420050, 208.01576013379, 9649.41539887043,
                                   9924.98971945508],  # by Denton Gentry
                                  [2021, -7.25788595429, 98.17575238401, 242.68505348942, 9649.41539887043,
                                   9983.01831878957],  # by Denton Gentry
                                  [2022, -10.83392888804, 128.22955413422, 277.35434684505, 9649.41539887043,
                                   10044.16537096170],  # by Denton Gentry
                                  [2023, -15.42565265504, 162.29052945112, 312.02364020068, 9649.41539887043,
                                   10108.30391586720],  # by Denton Gentry
                                  [2024, -21.16001735945, 200.35867833472, 346.69293355631, 9649.41539887043,
                                   10175.30699340200],  # by Denton Gentry
                                  [2025, -28.16398310543, 242.43400078501, 381.36222691194, 9649.41539887043,
                                   10245.04764346200],  # by Denton Gentry
                                  [2026, -36.56450999713, 288.51649680199, 416.03152026757, 9649.41539887043,
                                   10317.39890594290],  # by Denton Gentry
                                  [2027, -46.48855813871, 338.60616638567, 450.70081362320, 9649.41539887043,
                                   10392.23382074060],  # by Denton Gentry
                                  [2028, -58.06308763433, 392.70300953605, 485.37010697883, 9649.41539887043,
                                   10469.42542775100],  # by Denton Gentry
                                  [2029, -71.41505858814, 450.80702625312, 520.03940033446, 9649.41539887043,
                                   10548.84676686990],  # by Denton Gentry
                                  [2030, -86.67143110431, 512.91821653688, 554.70869369010, 9649.41539887043,
                                   10630.37087799310],  # by Denton Gentry
                                  [2031, -103.95916528698, 579.03658038734, 589.37798704573, 9649.41539887043,
                                   10713.87080101650],  # by Denton Gentry
                                  [2032, -123.40522124031, 649.16211780449, 624.04728040136, 9649.41539887043,
                                   10799.21957583600],  # by Denton Gentry
                                  [2033, -145.13655906847, 723.29482878833, 658.71657375699, 9649.41539887043,
                                   10886.29024234730],  # by Denton Gentry
                                  [2034, -169.28013887560, 801.43471333887, 693.38586711262, 9649.41539887043,
                                   10974.95584044630],  # by Denton Gentry
                                  [2035, -195.96292076586, 883.58177145611, 728.05516046825, 9649.41539887043,
                                   11065.08941002890],  # by Denton Gentry
                                  [2036, -225.31186484342, 969.73600314004, 762.72445382388, 9649.41539887043,
                                   11156.56399099090],  # by Denton Gentry
                                  [2037, -257.45393121243, 1059.89740839066, 797.39374717951, 9649.41539887043,
                                   11249.25262322820],  # by Denton Gentry
                                  [2038, -292.51607997703, 1154.06598720798, 832.06304053514, 9649.41539887043,
                                   11343.02834663650],  # by Denton Gentry
                                  [2039, -330.62527124140, 1252.24173959199, 866.73233389077, 9649.41539887043,
                                   11437.76420111180],  # by Denton Gentry
                                  [2040, -371.90846510969, 1354.42466554270, 901.40162724641, 9649.41539887043,
                                   11533.33322654980],  # by Denton Gentry
                                  [2041, -416.49262168605, 1460.61476506010, 936.07092060204, 9649.41539887043,
                                   11629.60846284650],  # by Denton Gentry
                                  [2042, -464.50470107464, 1570.81203814419, 970.74021395767, 9649.41539887043,
                                   11726.46294989770],  # by Denton Gentry
                                  [2043, -516.07166337962, 1685.01648479498, 1005.40950731330, 9649.41539887043,
                                   11823.76972759910],  # by Denton Gentry
                                  [2044, -571.32046870514, 1803.22810501247, 1040.07880066893, 9649.41539887043,
                                   11921.40183584670],  # by Denton Gentry
                                  [2045, -630.37807715537, 1925.44689879664, 1074.74809402456, 9649.41539887043,
                                   12019.23231453630],  # by Denton Gentry
                                  [2046, -693.37144883445, 2051.67286614752, 1109.41738738019, 9649.41539887043,
                                   12117.13420356370],  # by Denton Gentry
                                  [2047, -760.42754384655, 2181.90600706508, 1144.08668073582, 9649.41539887043,
                                   12214.98054282480],  # by Denton Gentry
                                  [2048, -831.67332229581, 2316.14632154934, 1178.75597409145, 9649.41539887043,
                                   12312.64437221540],  # by Denton Gentry
                                  [2049, -907.23574428641, 2454.39380960030, 1213.42526744708, 9649.41539887043,
                                   12409.99873163140],  # by Denton Gentry
                                  [2050, -987.24176992249, 2596.64847121795, 1248.09456080271, 9649.41539887043,
                                   12506.91666096860],  # by Denton Gentry
                                  [2051, -1071.81835930821, 2742.91030640229, 1282.76385415835, 9649.41539887043,
                                   12603.27120012290],  # by Denton Gentry
                                  [2052, -1161.09247254773, 2893.17931515333, 1317.43314751398, 9649.41539887043,
                                   12698.93538899000],  # by Denton Gentry
                                  [2053, -1255.19106974520, 3047.45549747107, 1352.10244086961, 9649.41539887043,
                                   12793.78226746590],  # by Denton Gentry
                                  [2054, -1354.24111100478, 3205.73885335549, 1386.77173422524, 9649.41539887043,
                                   12887.68487544640],  # by Denton Gentry
                                  [2055, -1458.36955643064, 3368.02938280662, 1421.44102758087, 9649.41539887043,
                                   12980.51625282730],  # by Denton Gentry
                                  [2056, -1567.70336612691, 3534.32708582443, 1456.11032093650, 9649.41539887043,
                                   13072.14943950450],  # by Denton Gentry
                                  [2057, -1682.36950019777, 3704.63196240894, 1490.77961429213, 9649.41539887043,
                                   13162.45747537370],  # by Denton Gentry
                                  [2058, -1802.49491874737, 3878.94401256015, 1525.44890764776, 9649.41539887043,
                                   13251.31340033100],  # by Denton Gentry
                                  [2059, -1928.20658187986, 4057.26323627805, 1560.11820100339, 9649.41539887043,
                                   13338.59025427200],  # by Denton Gentry
                                  [2060, -2059.63144969940, 4239.58963356264, 1594.78749435902, 9649.41539887043,
                                   13424.16107709270]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!CV168:CX214  # by Denton Gentry
exponential_trend_oecd90_list = [['Year', 'coeff', 'e^x', 'adoption'],  # by Denton Gentry
                                 [2014, 9513.45039364756, 1.00000000000, 9513.45039364756],  # by Denton Gentry
                                 [2015, 9513.45039364756, 1.00750584135, 9584.85684295519],  # by Denton Gentry
                                 [2016, 9513.45039364756, 1.01506802035, 9656.79925774241],  # by Denton Gentry
                                 [2017, 9513.45039364756, 1.02268695986, 9729.28166088106],  # by Denton Gentry
                                 [2018, 9513.45039364756, 1.03036308593, 9802.30810543805],  # by Denton Gentry
                                 [2019, 9513.45039364756, 1.03809682778, 9875.88267490195],  # by Denton Gentry
                                 [2020, 9513.45039364756, 1.04588861787, 9950.00948341134],  # by Denton Gentry
                                 [2021, 9513.45039364756, 1.05373889190, 10024.69267598490],  # by Denton Gentry
                                 [2022, 9513.45039364756, 1.06164808885, 10099.93642875310],  # by Denton Gentry
                                 [2023, 9513.45039364756, 1.06961665097, 10175.74494919190],  # by Denton Gentry
                                 [2024, 9513.45039364756, 1.07764502385, 10252.12247635770],  # by Denton Gentry
                                 [2025, 9513.45039364756, 1.08573365643, 10329.07328112490],  # by Denton Gentry
                                 [2026, 9513.45039364756, 1.09388300100, 10406.60166642410],  # by Denton Gentry
                                 [2027, 9513.45039364756, 1.10209351325, 10484.71196748320],  # by Denton Gentry
                                 [2028, 9513.45039364756, 1.11036565231, 10563.40855206950],  # by Denton Gentry
                                 [2029, 9513.45039364756, 1.11869988073, 10642.69582073410],  # by Denton Gentry
                                 [2030, 9513.45039364756, 1.12709666455, 10722.57820705820],  # by Denton Gentry
                                 [2031, 9513.45039364756, 1.13555647330, 10803.06017790030],  # by Denton Gentry
                                 [2032, 9513.45039364756, 1.14407978003, 10884.14623364670],  # by Denton Gentry
                                 [2033, 9513.45039364756, 1.15266706134, 10965.84090846300],  # by Denton Gentry
                                 [2034, 9513.45039364756, 1.16131879743, 11048.14877054730],  # by Denton Gentry
                                 [2035, 9513.45039364756, 1.17003547207, 11131.07442238580],  # by Denton Gentry
                                 [2036, 9513.45039364756, 1.17881757270, 11214.62250101060],  # by Denton Gentry
                                 [2037, 9513.45039364756, 1.18766559037, 11298.79767825840],  # by Denton Gentry
                                 [2038, 9513.45039364756, 1.19658001987, 11383.60466103180],  # by Denton Gentry
                                 [2039, 9513.45039364756, 1.20556135965, 11469.04819156290],  # by Denton Gentry
                                 [2040, 9513.45039364756, 1.21461011195, 11555.13304767830],  # by Denton Gentry
                                 [2041, 9513.45039364756, 1.22372678275, 11641.86404306590],  # by Denton Gentry
                                 [2042, 9513.45039364756, 1.23291188183, 11729.24602754470],  # by Denton Gentry
                                 [2043, 9513.45039364756, 1.24216592281, 11817.28388733550],  # by Denton Gentry
                                 [2044, 9513.45039364756, 1.25148942315, 11905.98254533430],  # by Denton Gentry
                                 [2045, 9513.45039364756, 1.26088290421, 11995.34696138770],  # by Denton Gentry
                                 [2046, 9513.45039364756, 1.27034689124, 12085.38213256990],  # by Denton Gentry
                                 [2047, 9513.45039364756, 1.27988191346, 12176.09309346260],  # by Denton Gentry
                                 [2048, 9513.45039364756, 1.28948850405, 12267.48491643610],  # by Denton Gentry
                                 [2049, 9513.45039364756, 1.29916720018, 12359.56271193320],  # by Denton Gentry
                                 [2050, 9513.45039364756, 1.30891854306, 12452.33162875470],  # by Denton Gentry
                                 [2051, 9513.45039364756, 1.31874307798, 12545.79685434780],  # by Denton Gentry
                                 [2052, 9513.45039364756, 1.32864135430, 12639.96361509550],  # by Denton Gentry
                                 [2053, 9513.45039364756, 1.33861392551, 12734.83717660940],  # by Denton Gentry
                                 [2054, 9513.45039364756, 1.34866134926, 12830.42284402400],  # by Denton Gentry
                                 [2055, 9513.45039364756, 1.35878418738, 12926.72596229320],  # by Denton Gentry
                                 [2056, 9513.45039364756, 1.36898300591, 13023.75191648920],  # by Denton Gentry
                                 [2057, 9513.45039364756, 1.37925837516, 13121.50613210390],  # by Denton Gentry
                                 [2058, 9513.45039364756, 1.38961086970, 13219.99407535180],  # by Denton Gentry
                                 [2059, 9513.45039364756, 1.40004106842, 13319.22125347630],  # by Denton Gentry
                                 [2060, 9513.45039364756, 1.41054955456, 13419.19321505700]]  # by Denton Gentry
# by Denton Gentry
# SolarHotWater 'TAM Data'!BS50:BV96  # by Denton Gentry
linear_trend_solarhotwater_list = [['Year', 'x', 'constant', 'adoption'],  # by Denton Gentry
                                   [2014, 0.0, 6057.054434, 6057.054434],  # by Denton Gentry
                                   [2015, 55.3449026, 6057.054434, 6112.399337],  # by Denton Gentry
                                   [2016, 110.6898052, 6057.054434, 6167.744239],  # by Denton Gentry
                                   [2017, 166.0347078, 6057.054434, 6223.089142],  # by Denton Gentry
                                   [2018, 221.3796104, 6057.054434, 6278.434044],  # by Denton Gentry
                                   [2019, 276.724513, 6057.054434, 6333.778947],  # by Denton Gentry
                                   [2020, 332.0694156, 6057.054434, 6389.12385],  # by Denton Gentry
                                   [2021, 387.4143182, 6057.054434, 6444.468752],  # by Denton Gentry
                                   [2022, 442.7592208, 6057.054434, 6499.813655],  # by Denton Gentry
                                   [2023, 498.1041234, 6057.054434, 6555.158557],  # by Denton Gentry
                                   [2024, 553.449026, 6057.054434, 6610.50346],  # by Denton Gentry
                                   [2025, 608.7939286, 6057.054434, 6665.848363],  # by Denton Gentry
                                   [2026, 664.1388312, 6057.054434, 6721.193265],  # by Denton Gentry
                                   [2027, 719.4837338, 6057.054434, 6776.538168],  # by Denton Gentry
                                   [2028, 774.8286364, 6057.054434, 6831.88307],  # by Denton Gentry
                                   [2029, 830.173539, 6057.054434, 6887.227973],  # by Denton Gentry
                                   [2030, 885.5184416, 6057.054434, 6942.572876],  # by Denton Gentry
                                   [2031, 940.8633442, 6057.054434, 6997.917778],  # by Denton Gentry
                                   [2032, 996.2082469, 6057.054434, 7053.262681],  # by Denton Gentry
                                   [2033, 1051.553149, 6057.054434, 7108.607583],  # by Denton Gentry
                                   [2034, 1106.898052, 6057.054434, 7163.952486],  # by Denton Gentry
                                   [2035, 1162.242955, 6057.054434, 7219.297389],  # by Denton Gentry
                                   [2036, 1217.587857, 6057.054434, 7274.642291],  # by Denton Gentry
                                   [2037, 1272.93276, 6057.054434, 7329.987194],  # by Denton Gentry
                                   [2038, 1328.277662, 6057.054434, 7385.332096],  # by Denton Gentry
                                   [2039, 1383.622565, 6057.054434, 7440.676999],  # by Denton Gentry
                                   [2040, 1438.967468, 6057.054434, 7496.021902],  # by Denton Gentry
                                   [2041, 1494.31237, 6057.054434, 7551.366804],  # by Denton Gentry
                                   [2042, 1549.657273, 6057.054434, 7606.711707],  # by Denton Gentry
                                   [2043, 1605.002175, 6057.054434, 7662.056609],  # by Denton Gentry
                                   [2044, 1660.347078, 6057.054434, 7717.401512],  # by Denton Gentry
                                   [2045, 1715.691981, 6057.054434, 7772.746415],  # by Denton Gentry
                                   [2046, 1771.036883, 6057.054434, 7828.091317],  # by Denton Gentry
                                   [2047, 1826.381786, 6057.054434, 7883.43622],  # by Denton Gentry
                                   [2048, 1881.726688, 6057.054434, 7938.781122],  # by Denton Gentry
                                   [2049, 1937.071591, 6057.054434, 7994.126025],  # by Denton Gentry
                                   [2050, 1992.416494, 6057.054434, 8049.470928],  # by Denton Gentry
                                   [2051, 2047.761396, 6057.054434, 8104.81583],  # by Denton Gentry
                                   [2052, 2103.106299, 6057.054434, 8160.160733],  # by Denton Gentry
                                   [2053, 2158.451202, 6057.054434, 8215.505635],  # by Denton Gentry
                                   [2054, 2213.796104, 6057.054434, 8270.850538],  # by Denton Gentry
                                   [2055, 2269.141007, 6057.054434, 8326.195441],  # by Denton Gentry
                                   [2056, 2324.485909, 6057.054434, 8381.540343],  # by Denton Gentry
                                   [2057, 2379.830812, 6057.054434, 8436.885246],  # by Denton Gentry
                                   [2058, 2435.175715, 6057.054434, 8492.230148],  # by Denton Gentry
                                   [2059, 2490.520617, 6057.054434, 8547.575051],  # by Denton Gentry
                                   [2060, 2545.86552, 6057.054434, 8602.919954]]  # by Denton Gentry
# by Denton Gentry
# BuildingAutomation 'TAM Data'!DV479:DW525  # by Denton Gentry
global_trend_buildingautomation_list = [['Year', 'China'],  # by Denton Gentry
                                        [2014, 12830.4000000000], [2015, 14733.5554883180],  # by Denton Gentry
                                        [2016, 15199.3049071829], [2017, 15633.3576109881],  # by Denton Gentry
                                        [2018, 16036.7510169021], [2019, 16410.5225420934],  # by Denton Gentry
                                        [2020, 16755.7096037305], [2021, 17073.3496189820],  # by Denton Gentry
                                        [2022, 17364.4800050164], [2023, 17630.1381790023],  # by Denton Gentry
                                        [2024, 17871.3615581081], [2025, 18089.1875595025],  # by Denton Gentry
                                        [2026, 18284.6536003538], [2027, 18458.7970978308],  # by Denton Gentry
                                        [2028, 18612.6554691019], [2029, 18747.2661313356],  # by Denton Gentry
                                        [2030, 18863.6665017005], [2031, 18962.8939973650],  # by Denton Gentry
                                        [2032, 19045.9860354978], [2033, 19113.9800332674],  # by Denton Gentry
                                        [2034, 19167.9134078423], [2035, 19208.8235763910],  # by Denton Gentry
                                        [2036, 19237.7479560821], [2037, 19255.7239640841],  # by Denton Gentry
                                        [2038, 19263.7890175655], [2039, 19262.9805336949],  # by Denton Gentry
                                        [2040, 19254.3359296408], [2041, 19238.8926225717],  # by Denton Gentry
                                        [2042, 19217.6880296562], [2043, 19191.7595680627],  # by Denton Gentry
                                        [2044, 19162.1446549599], [2045, 19129.8807075163],  # by Denton Gentry
                                        [2046, 19096.0051429003], [2047, 19061.5553782806],  # by Denton Gentry
                                        [2048, 19027.5688308256], [2049, 18995.0829177039],  # by Denton Gentry
                                        [2050, 18965.1350560840], [2051, 18938.7626631345],  # by Denton Gentry
                                        [2052, 18917.0031560239], [2053, 18900.8939519207],  # by Denton Gentry
                                        [2054, 18891.4724679934], [2055, 18889.7761214106],  # by Denton Gentry
                                        [2056, 18896.8423293409], [2057, 18913.7085089527],  # by Denton Gentry
                                        [2058, 18941.4120774146], [2059, 18980.9904518950],  # by Denton Gentry
                                        [2060, 19033.4810495627]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!V45:Y94 with source_until_2014='ALL SOURCES',  # by Denton Gentry
# source_after_2014='ALL SOURCES', low_sd=1.0, high_sd=1.0, and  # by Denton Gentry
# B29:B30 set to 'Y' to include regional data in the Min/Max/SD  # by Denton Gentry
forecast_min_max_sd_global_with_regional_list = [['Year', 'Min', 'Max', 'S.D'],  # by Denton Gentry
                                                 [2012, 21534.0000000000, 21534.0000000000, 0.0000000000000],
                                                 # by Denton Gentry
                                                 [2013, 22203.0000000000, 22203.0000000000, 0.0000000000000],
                                                 # by Denton Gentry
                                                 [2014, 22548.2990000000, 23152.7006896004, 146.30235489010],
                                                 # by Denton Gentry
                                                 [2015, 22429.7218661374, 27024.4702803023, 1229.4812097517],
                                                 # by Denton Gentry
                                                 [2016, 22906.9120870725, 27898.5551476510, 1313.7083543558],
                                                 # by Denton Gentry
                                                 [2017, 23402.1189826181, 28756.9038926822, 1399.4229808300],
                                                 # by Denton Gentry
                                                 [2018, 23915.4346943209, 29600.0618626642, 1485.0583556343],
                                                 # by Denton Gentry
                                                 [2019, 24446.9131013217, 30428.5210440123, 1570.0579563478],
                                                 # by Denton Gentry
                                                 [2020, 24872.2227465960, 31079.0751096977, 1698.7705301479],
                                                 # by Denton Gentry
                                                 [2021, 25564.9101095336, 32043.7221836502, 1738.9957278645],
                                                 # by Denton Gentry
                                                 [2022, 26151.9471241863, 32831.9652426197, 1824.2405634648],
                                                 # by Denton Gentry
                                                 [2023, 26758.2104510594, 33608.5496112893, 1911.1821032367],
                                                 # by Denton Gentry
                                                 [2024, 27384.2156903934, 34374.5606148262, 2000.7871502799],
                                                 # by Denton Gentry
                                                 [2025, 28030.4505798149, 35387.6999838500, 2097.8568983995],
                                                 # by Denton Gentry
                                                 [2026, 28697.2751067092, 36509.4429539791, 2191.6495226549],
                                                 # by Denton Gentry
                                                 [2027, 29385.0165896816, 37640.8370975740, 2294.4946417982],
                                                 # by Denton Gentry
                                                 [2028, 30094.1109044164, 38781.9229190917, 2403.1502675761],
                                                 # by Denton Gentry
                                                 [2029, 30825.0168500741, 39932.7714195675, 2518.1046393711],
                                                 # by Denton Gentry
                                                 [2030, 31766.3945441049, 40974.3184829420, 2581.4439191401],
                                                 # by Denton Gentry
                                                 [2031, 32299.5068596379, 42263.9410630002, 2768.1935416770],
                                                 # by Denton Gentry
                                                 [2032, 32931.8013981080, 43444.2607421208, 2903.6674612074],
                                                 # by Denton Gentry
                                                 [2033, 33426.4411921675, 44634.3965746784, 3046.1592407450],
                                                 # by Denton Gentry
                                                 [2034, 33922.5178230747, 45834.3363612893, 3195.6273544302],
                                                 # by Denton Gentry
                                                 [2035, 34466.7932946091, 47044.0626050110, 3352.5609800156],
                                                 # by Denton Gentry
                                                 [2036, 34920.3984310243, 48263.5461195901, 3515.1083306803],
                                                 # by Denton Gentry
                                                 [2037, 35422.8480172506, 49492.7579940144, 3684.8795026053],
                                                 # by Denton Gentry
                                                 [2038, 35928.0981905913, 50731.6730222579, 3861.1862263112],
                                                 # by Denton Gentry
                                                 [2039, 36436.5078668097, 51980.2620438816, 4043.9471377832],
                                                 # by Denton Gentry
                                                 [2040, 36891.0448422666, 53318.6971171473, 4324.7818354847],
                                                 # by Denton Gentry
                                                 [2041, 37464.1331710322, 54506.2433903478, 4428.7240742755],
                                                 # by Denton Gentry
                                                 [2042, 37983.9405169630, 55783.4594497884, 4630.8307303323],
                                                 # by Denton Gentry
                                                 [2043, 38508.0727719431, 57094.9669759492, 4839.5910660176],
                                                 # by Denton Gentry
                                                 [2044, 39036.7373902378, 58748.1022577474, 5055.2372494559],
                                                 # by Denton Gentry
                                                 [2045, 39594.4131995284, 60413.9802624210, 5277.8473717880],
                                                 # by Denton Gentry
                                                 [2046, 40108.5551602081, 62090.5251778409, 5508.6030344729],
                                                 # by Denton Gentry
                                                 [2047, 40652.2151900036, 63775.6700592455, 5747.2975640531],
                                                 # by Denton Gentry
                                                 [2048, 41201.3634882315, 65467.2986092187, 5994.8296543826],
                                                 # by Denton Gentry
                                                 [2049, 41756.2294713394, 67163.2756420720, 6251.9614236051],
                                                 # by Denton Gentry
                                                 [2050, 42313.5981963481, 68762.6925241243, 6490.7704906617],
                                                 # by Denton Gentry
                                                 [2051, 42884.0535147214, 70559.7151101345, 6798.6511380875],
                                                 # by Denton Gentry
                                                 [2052, 43457.5033566593, 72255.9098041119, 7090.3117712789],
                                                 # by Denton Gentry
                                                 [2053, 44037.5093840040, 73947.6764771113, 7395.7459288353],
                                                 # by Denton Gentry
                                                 [2054, 44624.1517999176, 75632.5738268464, 7716.2430712700],
                                                 # by Denton Gentry
                                                 [2055, 45217.5639224199, 77308.2350196979, 8053.1968389723],
                                                 # by Denton Gentry
                                                 [2056, 45817.9763708168, 78972.4496857084, 8408.1032496873],
                                                 # by Denton Gentry
                                                 [2057, 46425.7036591602, 80623.1487278456, 8782.5527912472],
                                                 # by Denton Gentry
                                                 [2058, 47041.0741835201, 82258.2878710141, 9178.2098386838],
                                                 # by Denton Gentry
                                                 [2059, 47664.4590182862, 83875.8992336970, 9596.8053376054],
                                                 # by Denton Gentry
                                                 [2060, 48296.2333895397, 85474.0252660105,
                                                  10040.1128681535]]  # by Denton Gentry
# by Denton Gentry
# SolarPVUtil 'TAM Data'!V45:Y94 with source_until_2014='ALL SOURCES',  # by Denton Gentry
# source_after_2014='ALL SOURCES', low_sd=1.0, high_sd=1.0, and  # by Denton Gentry
# B29:B30 set to 'Y' to include regional data in the Low/Med/High  # by Denton Gentry
forecast_low_med_high_global_with_regional_list = [['Year', 'Low', 'Medium', 'High'],  # by Denton Gentry
                                                   [2012, 21534.0000000000, 21534.0000000000, 21534.0000000000],
                                                   # by Denton Gentry
                                                   [2013, 22203.0000000000, 22203.0000000000, 22203.0000000000],
                                                   # by Denton Gentry
                                                   [2014, 22439.7717507099, 22586.0741056000, 22732.3764604902],
                                                   # by Denton Gentry
                                                   [2015, 23057.1944942536, 24286.6757040053, 25516.1569137570],
                                                   # by Denton Gentry
                                                   [2016, 23629.6080795531, 24943.3164339089, 26257.0247882648],
                                                   # by Denton Gentry
                                                   [2017, 24212.2538431068, 25611.6768239368, 27011.0998047667],
                                                   # by Denton Gentry
                                                   [2018, 24806.2938051016, 26291.3521607359, 27776.4105163702],
                                                   # by Denton Gentry
                                                   [2019, 25411.7989931779, 26981.8569495257, 28551.9149058735],
                                                   # by Denton Gentry
                                                   [2020, 26086.8067455227, 27785.5772756706, 29484.3478058185],
                                                   # by Denton Gentry
                                                   [2021, 26654.8364223656, 28393.8321502301, 30132.8278780946],
                                                   # by Denton Gentry
                                                   [2022, 27290.6361417744, 29114.8767052392, 30939.1172687040],
                                                   # by Denton Gentry
                                                   [2023, 27934.6551700813, 29845.8372733180, 31757.0193765547],
                                                   # by Denton Gentry
                                                   [2024, 28585.9363121400, 30586.7234624199, 32587.5106126998],
                                                   # by Denton Gentry
                                                   [2025, 29193.0498073336, 31290.9067057331, 33388.7636041325],
                                                   # by Denton Gentry
                                                   [2026, 29906.4422282025, 32098.0917508574, 34289.7412735123],
                                                   # by Denton Gentry
                                                   [2027, 30573.7787582810, 32868.2734000791, 35162.7680418773],
                                                   # by Denton Gentry
                                                   [2028, 31244.8412263447, 33647.9914939209, 36051.1417614970],
                                                   # by Denton Gentry
                                                   [2029, 31919.0861662805, 34437.1908056516, 36955.2954450227],
                                                   # by Denton Gentry
                                                   [2030, 32550.7998663918, 35132.2437855319, 37713.6877046720],
                                                   # by Denton Gentry
                                                   [2031, 33275.5547802802, 36043.7483219571, 38811.9418636341],
                                                   # by Denton Gentry
                                                   [2032, 33957.2406926830, 36860.9081538904, 39764.5756150978],
                                                   # by Denton Gentry
                                                   [2033, 34641.0418437770, 37687.2010845220, 40733.3603252671],
                                                   # by Denton Gentry
                                                   [2034, 35326.9141697666, 38522.5415241967, 41718.1688786269],
                                                   # by Denton Gentry
                                                   [2035, 36053.5124316464, 39406.0734116619, 42758.6343916775],
                                                   # by Denton Gentry
                                                   [2036, 36704.8670296052, 40219.9753602855, 43735.0836909658],
                                                   # by Denton Gentry
                                                   [2037, 37396.9611700628, 41081.8406726681, 44766.7201752734],
                                                   # by Denton Gentry
                                                   [2038, 38091.1496015438, 41952.3358278550, 45813.5220541662],
                                                   # by Denton Gentry
                                                   [2039, 38787.4173749387, 42831.3645127219, 46875.3116505051],
                                                   # by Denton Gentry
                                                   [2040, 39450.6760316881, 43775.4578671728, 48100.2397026576],
                                                   # by Denton Gentry
                                                   [2041, 40185.8228035845, 44614.5468778600, 49043.2709521356],
                                                   # by Denton Gentry
                                                   [2042, 40887.5709718454, 45518.4017021777, 50149.2324325100],
                                                   # by Denton Gentry
                                                   [2043, 41590.5754668706, 46430.1665328881, 51269.7575989057],
                                                   # by Denton Gentry
                                                   [2044, 42294.3636873738, 47349.6009368297, 52404.8381862856],
                                                   # by Denton Gentry
                                                   [2045, 42983.7523527564, 48261.5997245444, 53539.4470963325],
                                                   # by Denton Gentry
                                                   [2046, 43701.9529543811, 49210.5559888540, 54719.1590233269],
                                                   # by Denton Gentry
                                                   [2047, 44404.3673931139, 50151.6649571670, 55898.9625212200],
                                                   # by Denton Gentry
                                                   [2048, 45104.7347479793, 51099.5644023619, 57094.3940567444],
                                                   # by Denton Gentry
                                                   [2049, 45802.0542243993, 52054.0156480043, 58305.9770716094],
                                                   # by Denton Gentry
                                                   [2050, 46514.2108153444, 53004.9813060061, 59495.7517966678],
                                                   # by Denton Gentry
                                                   [2051, 47182.9788812009, 53981.6300192884, 60780.2811573758],
                                                   # by Denton Gentry
                                                   [2052, 47864.0294708249, 54954.3412421038, 62044.6530133827],
                                                   # by Denton Gentry
                                                   [2053, 48536.7881755584, 55932.5341043937, 63328.2800332290],
                                                   # by Denton Gentry
                                                   [2054, 49199.5412244601, 56915.7842957301, 64632.0273670001],
                                                   # by Denton Gentry
                                                   [2055, 49850.5262645896, 57903.7231035619, 65956.9199425342],
                                                   # by Denton Gentry
                                                   [2056, 50487.9798908098, 58896.0831404971, 67304.1863901844],
                                                   # by Denton Gentry
                                                   [2057, 51110.1445175266, 59892.6973087738, 68675.2501000211],
                                                   # by Denton Gentry
                                                   [2058, 51715.2164082663, 60893.4262469501, 70071.6360856338],
                                                   # by Denton Gentry
                                                   [2059, 52301.3795422541, 61898.1848798595, 71494.9902174649],
                                                   # by Denton Gentry
                                                   [2060, 52866.7706572830, 62906.8835254366,
                                                    72946.9963935901]]  # by Denton Gentry
