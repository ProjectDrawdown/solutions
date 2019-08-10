import pathlib

import pandas as pd
import pytest
import tools.vma_xls_extract
import xlrd

thisdir = pathlib.Path(__file__).parents[0]
wb = xlrd.open_workbook(thisdir.joinpath('silvopasture_vma.xlsx'))


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


def test_read_xls_num_dfs():
    """ Check we produce the right amount of tables + discard empty ones """
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    df_dict = vma_r.read_xls()
    assert len(df_dict) == 24
    num_empty_tables = len([x for (x, _, _) in df_dict.values() if x is None])
    assert num_empty_tables == 13


def test_read_xls():
    """ Check some specifc values from Silvopasture """
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    df_dict = vma_r.read_xls()
    table = df_dict['SOLUTION Net Profit Margin per Functional Unit per Annum'][0]
    assert table.at[5, 'Raw Data Input'] == 416
    table = df_dict['Sequestration Rates'][0]
    assert len(table) == 28
    (table, exclude, summary) = df_dict['SOLUTION Energy Efficiency Factor']
    assert table is None
    assert exclude == False
    assert len(summary) == 3
    assert pd.isna(summary[0])
    assert pd.isna(summary[1])
    assert pd.isna(summary[2])


def test_read_xls_additional_var():
    """ Check the additional var from Silvopasture """
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    df_dict = vma_r.read_xls()
    assert 'Percent silvopasture area to the total grassland area (including potential)' in df_dict


def test_normalize_col_name():
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    assert vma_r.normalize_col_name('Conedition calculation') == 'Conversion calculation'
    assert vma_r.normalize_col_name('Manually Exclude Data?') == 'Exclude Data?'
    assert vma_r.normalize_col_name('Weight by: Production') == 'Weight'


@pytest.mark.slow
def test_rrs():
    wb = xlrd.open_workbook(thisdir.joinpath('solarpvutil_vma.xlsm'))
    vma_r = tools.vma_xls_extract.VMAReader(wb)
    df_dict = vma_r.read_xls(alt_vma=True)
    table = df_dict['Current Adoption'][0]
    assert table.at[0, 'SOURCE ID: Author/Org, Date, Info'] == 'IRENA (2016)_Historical data for solar PV'
    assert table.at[0, 'Assumptions'] == 'Assuming that PV utility represents around 60% of total Solar PV'
    assert table.at[0, 'Exclude Data?'] == True
