import pathlib
import pandas as pd
import xlrd
from tools.vma_xls_extract import make_vma_df_template, VMAReader

thisdir = pathlib.Path(__file__).parents[0]
wb = xlrd.open_workbook(thisdir.joinpath('silvopasture_vma.xlsx'))


def test_make_vma_df_template():
    df = make_vma_df_template()
    expected_cols = {'SOURCE ID: Author/Org, Date, Info', 'Link', 'World / Drawdown Region',
                     'Specific Geographic Location', 'Thermal-Moisture Regime', 'Source Validation Code', 'Year / Date',
                     'License Code', 'Raw Data Input', 'Original Units', 'Conversion calculation', 'Common Units',
                     'Weight', 'Assumptions', 'Exclude Data?'}
    assert expected_cols == set(df.columns)


def test_single_table():
    vma_r = VMAReader(wb)
    result = vma_r.read_single_table('C48')
    expected = pd.read_csv(thisdir.joinpath('silvopasture_vma1.csv'))
    # integer values for years are causing an unimportant dtype issue in the test
    pd.testing.assert_frame_equal(expected.drop(columns=['Year / Date']), result.drop(columns=['Year / Date']))


def test_read_xls_num_dfs():
    """ Check we produce the right amount of tables + discard empty ones """
    vma_r = VMAReader(wb)
    df_dict = vma_r.read_xls()
    assert len(df_dict) == 24
    num_empty_tables = len([x for _, x in df_dict.items() if x is None])
    assert num_empty_tables == 13


def test_read_xls():
    """ Check some specifc values from Silvopasture """
    vma_r = VMAReader(wb)
    df_dict = vma_r.read_xls()
    table = df_dict['SOLUTION Net Profit Margin per Functional Unit per Annum']
    assert table.at[5, 'Raw Data Input'] == 416
    table = df_dict['Sequestration Rates']
    assert len(table) == 28
    table = df_dict['Energy Efficiency Factor - SOLUTION']
    assert table is None


def test_read_xls_additional_var():
    """ Check the additional var from Silvopasture """
    vma_r = VMAReader(wb)
    df_dict = vma_r.read_xls()
    assert 'Percent silvopasture area to the total grassland area (including potential)' in df_dict