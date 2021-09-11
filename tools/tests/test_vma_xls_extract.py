import collections
import pathlib

import numpy as np
import pandas as pd
import pytest
import tools.vma_xls_extract
import openpyxl

thisdir = pathlib.Path(__file__).parents[0]
wb = openpyxl.load_workbook(thisdir.joinpath('silvopasture_vma.xlsx'), data_only=True, keep_links=False)



def test_make_vma_df_template():
    df = tools.vma_xls_extract.make_vma_df_template()
    expected_cols = {'SOURCE ID: Author/Org, Date, Info', 'Link', 'World / Drawdown Region',
                     'Specific Geographic Location', 'Thermal-Moisture Regime',
                     'Source Validation Code', 'Year / Date', 'License Code', 'Raw Data Input',
                     'Original Units', 'Conversion calculation', 'Common Units', 'Weight',
                     'Assumptions', 'Exclude Data?', 'Crop',
                     'Closest Matching Standard Crop (by Revenue/ha)'}
    assert expected_cols == set(df.columns)


def test_single_table():
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    result, _, _ = vma_r.read_single_table('C48', sheetname='Variable Meta-analysis',
                                           fixed_summary=False)
    expected = pd.read_csv(thisdir.joinpath('silvopasture_vma1.csv'))
    expected['Year / Date'] = expected['Year / Date'].astype('object')
    pd.testing.assert_frame_equal(expected, result)


def test_single_table_use_weight():
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    _, uw, _ = vma_r.read_single_table('C48', sheetname='Variable Meta-analysis',
                                       fixed_summary=False)
    assert not uw


@pytest.mark.slow
def test_read_xls_num_dfs():
    """ Check we produce the right amount of tables + discard empty ones """
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    vma_df = vma_r.read_xls()
    assert len(vma_df) == 24
    non_empty_tables = len(vma_df.loc[(vma_df['Filename'] != '')])
    assert non_empty_tables == 11


@pytest.mark.slow
def test_read_xls():
    """ Check some specifc values from Silvopasture """
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    vma_df = vma_r.read_xls()
    unique = vma_df['Title on xls'].unique()
    assert 'SOLUTION Net Profit Margin per Functional Unit per Annum' in unique
    assert 'Sequestration Rates' in unique
    assert 'SOLUTION Energy Efficiency Factor' in unique


@pytest.mark.slow
def test_read_xls_additional_var():
    """ Check the additional var from Silvopasture """
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    vma_df = vma_r.read_xls()
    s = 'Percent silvopasture area to the total grassland area (including potential)'
    assert s in vma_df['Title on xls'].unique()


@pytest.mark.slow
def test_xls_df_dict():
    """ Check that wb is extracted to a dictionary (component of read_xls) """

    vma_r = tools.vma_xls_extract.VMAReader(wb)
    df_dict = vma_r.xls_df_dict()

    # Do some basic type and shape checking
    assert isinstance(df_dict, collections.OrderedDict)
    for key, value in df_dict.items():
        # VMA title
        assert isinstance(key, str)
        # (df, boolean, (float, float, float))
        assert isinstance(value, tuple)
        assert len(value) == 3
        if value[0] is None:
            assert value[1] is False
            assert value[2] == (np.nan, ) * 3
        else:
            assert isinstance(value[0], pd.core.frame.DataFrame)
            assert not value[0].empty
            assert isinstance(value[1], bool)
            assert isinstance(value[2], tuple)
            assert len(value[2]) == 3
            for number in value[2]:
                assert isinstance(number, float)

    # Check an arbitrary column
    assert 'Disturbance Rate' in df_dict.keys()

    # A known number of VMAs are empty in the example xlsx
    assert sum(value[0] is None for value in df_dict.values()) == 13


@pytest.mark.slow
def test_explicit_fixed_summaries():
    """Check that when fixed summaries are requested, they are provided"""
    wb = openpyxl.load_workbook(thisdir.joinpath('solution_xls_extract_RRS_test_A.xlsm'), data_only=True, keep_links=False)
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    tables = vma_r.xls_df_dict(fixed_summary=True)
    (_,_,summary) = tables['CONVENTIONAL First Cost per Implementation Unit'] 
    assert summary == pytest.approx((2010.0317085196398, 3373.5568673016687, 646.5065497376106))


def test_normalize_col_name():
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    assert vma_r.normalize_col_name('Conedition calculation') == 'Conversion calculation'
    assert vma_r.normalize_col_name('Manually Exclude Data?') == 'Exclude Data?'
    assert vma_r.normalize_col_name('Weight by: Production') == 'Weight'


@pytest.mark.slow
def test_rrs():
    wb = openpyxl.load_workbook(thisdir.joinpath('solarpvutil_vma.xlsm'), data_only=True, keep_links=False)
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    vma_df = vma_r.read_xls()
    assert vma_df.loc[1, 'Title on xls'] == 'Current Adoption'


@pytest.mark.slow
def test_large_vma():
    wb = openpyxl.load_workbook(thisdir.joinpath('lg_vma.xlsx'), data_only=True, keep_links=False)
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    tables = vma_r.xls_df_dict()
    assert len(tables) == 26

    # this is one of the large tables
    assert 'CONVENTIONAL Direct Emissions per Functional Unit' in tables.keys()
    (df, _, _) = tables['CONVENTIONAL Direct Emissions per Functional Unit']
    assert (205,14) == df.shape
    assert df.loc[204]['Raw Data Input'] == pytest.approx(24.8)

