from numpy import NaN
from tools import excel_tools as xlt
import pandas as pd
from pathlib import Path

this_dir = Path(__file__).parents[0]

def test_get_from_excel():
    file=Path(this_dir, "excel_fair_results_test.xlsx")
    dat = xlt.get_from_excel(file,"Gtperyr_PDS1", "K7:P8",
    ['A','B','C','D','E','F'])
    expected = pd.DataFrame([
        (1, 1.0, 1.00, 1.00, 1.0, 1.00),
        (2, 1.5, 1.25, 1.75, 1.1, 1.11)
    ], columns=['A','B','C','D','E','F'])
    assert xlt.df_differ(dat,expected,all_zero=False) is False

    dat = xlt.get_from_excel(file,"Gtperyr_PDS1", "K6:P12")
    expected = pd.DataFrame([
        (1, 1.0, 1.00, 1.00, 1.0, 1.00),
        (2, 1.5, 1.25, 1.75, 1.1, 1.11),
        (3, 2.0, 1.50, 2.50, 1.2, 1.22),
        (4, 2.5, 1.75, 3.25, 1.3, 1.33),
        (5, 3.0, 2.00, 4.00, 1.4, 1.44),
        (6, 3.5, 2.25, 4.75, 1.5, 1.55)
    ], columns=['Health and Education','Building Retrofitting',
        'Plant-Rich Diet','Refrigerant Management','Telepresence',
        'Marine Protected Areas'])  
    assert xlt.df_differ(dat,expected,all_zero=False) is False 

def test_rename_column():
    dat = pd.DataFrame([
        (1, 1.0, 1.00, 1.00, 1.0, 1.00),
        (2, 1.5, 1.25, 1.75, 1.1, 1.11)
    ], columns=['A','B','C','D','E','F'])
    modified = xlt.rename_column(dat, 2, 'CC')
    assert list(modified.columns) == ['A','B', 'CC', 'D', 'E', 'F']

def test_rename_all_columns():
    dat = pd.DataFrame([
        (1, 1.0, 1.00, 1.00, 1.0, 1.00),
        (2, 1.5, 1.25, 1.75, 1.1, 1.11)
    ], columns=['A','B','C','D','E','F'])
    modified = xlt.rename_all_columns(dat, ['AA','BB', None, None, None, 'C'])
    expected = pd.DataFrame([
        (1, 1.0, 1.00),
        (2, 1.5, 1.11)
    ], columns=['AA','BB','C'])
    assert modified.equals(expected)

def test_excel_range_from_df():
    dat =  pd.DataFrame([
        ('hello', 1.0, 1.00, '1.00', 1.0, 1.00),
        ('foo', 1.5, 1.25, '1.75', 1.1, 1.11),
        ('2.0', 2.0, 1.50, '2.50', 1.2, 1.22),
        ('oompah', 2.5, 1.75, '3.25', 1.3, 1.33),
        ('foo', 3.0, 2.00, '4.00', 1.4, 1.44),
        ('bar', 3.5, 2.25, '4.75', 1.5, 1.55)
    ])
    received = xlt.excel_range_from_df(dat, "A2:D3", to_numeric=False)
    expected = pd.DataFrame([
        ('foo', 1.5, 1.25, '1.75'),
        ('2.0', 2.0, 1.50, '2.50'),
    ])
    # Note: we cannot use equals operator here, because the index & 
    # column names will differ
    assert xlt.df_differ(received,expected,all_zero=False) is False

    received = xlt.excel_range_from_df(dat, "A1:D6", to_numeric=True)
    expected = pd.DataFrame([
        ('hello', 1.0, 1.00, 1.00),
        ('foo', 1.5, 1.25, 1.75),
        ('2.0', 2.0, 1.50, 2.50),
        ('oompah', 2.5, 1.75, 3.25),
        ('foo', 3.0, 2.00, 4.00),
        ('bar', 3.5, 2.25, 4.75)
    ])
    assert xlt.df_differ(received,expected,all_zero=False) is False


def test_range_shift():
    assert xlt.range_shift("A1:B1",column_shift=2) == "C1:D1"
    assert xlt.range_shift("C20:F40", row_shift=-10) == "C10:F30"
    assert xlt.range_shift("AA10:AP40", row_shift=10, width_shift=-2) == "AA20:AN50"
    assert xlt.range_shift("B10:D12", width_set=4, height_set=10) == "B10:E19"
    assert xlt.range_shift("A1:A20",column_shift=2,width_shift=4) == "C1:G20"


def test_df_differ():
    # We're not going to test the actual numerical approximation stuff here,
    # just the multi-type and pseudo_zero part.

    d1 =  pd.DataFrame([
        ('hello', 1.0, NaN, '1.00', 2, 1.00),
        ('foo', 1.5, 1.25, '1.75', 3, 1.11),
        ('2.0', 2.0, 1.50, '2.50', 5, 1.22),
        ('oompah', 2.5, 1.75, '3.25', 7, 1.33),
        ('foo', 3.0, 2.00, '4.00', 8, 1.44),
        ('bar', 3.5, 2.25, None, 9, 1.55)
    ], columns=['A','B','C','D','E','F'])   

    # changing 4th column to float, and a few other diffs
    d2 =  pd.DataFrame([
        ('hello', 1.0, 0, '1.00', 2.0, 1.00),
        ('foo', 1.5, 1.25, '1.75', 3.1, 1.11),
        ('2.0', NaN, 1.50, '2.50', 5, 1.22),
        ('oomph', 2.5, 1.75, '3.25', 7, 1.33),
        ('foo', 3.0, 2.00, '4.00', 8, 1.44),
        ('bar', 3.5, 2.25, '', 9, 1.55)
    ], columns=['B','C','D','E','F','A'])  # permuted column names

    # Note: we can't do a simple list equality test here because the embedded NaN won't compare true,
    # so take the str() of it.
    # I suppose there is some risk of different versions of Python printing nan differently?
    assert str(xlt.df_differ(d1,d2,all_zero=True)) == "[(1, 4, 3, 3.1), (2, 1, 2.0, nan), (3, 0, 'oompah', 'oomph')]"
    assert str(xlt.df_differ(d1,d2,all_zero=False)) == "[(0, 2, nan, 0.0), (1, 4, 3, 3.1), (2, 1, 2.0, nan), (3, 0, 'oompah', 'oomph'), (5, 3, None, '')]"