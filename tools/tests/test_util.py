from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import openpyxl
from tools import util

thisdir = Path(__file__).parent
wb = openpyxl.load_workbook(thisdir/'silvopasture_vma.xlsx', data_only=True)
ws = wb['Variable Meta-analysis']
df = pd.read_csv(thisdir/'silvopasture_vma.csv',header=None)

def assert_data_equal(expected, result):
    """Assert the values are equal and in the same order, disregarding the indices"""
    assert expected.shape == result.shape, "DataFrame shapes are inconsistent"
    expected = expected.copy()
    expected.columns = result.columns
    expected.index = result.index
    pd.testing.assert_frame_equal(expected, result)

def test_df_excel_range_basic():
    result = util.df_excel_range(df, "R21:T23")
    expected = pd.DataFrame([
        ["Cubic foot (ft3)",7.48052,6.22884],
        ["Litre (l)",0.26417,0.21997],
        ["Cubic meter (m3)",264.17205,219.96925]])
    assert_data_equal(expected, result)

    result = util.df_excel_range(df, "R21:T23", to_numeric=False)
    expected = pd.DataFrame([
        ["Cubic foot (ft3)","7.48052","6.22884"],
        ["Litre (l)","0.26417","0.21997"],
        ["Cubic meter (m3)","264.17205","219.96925"]])
    assert_data_equal(expected, result)

def test_df_excel_range_edge_cases():
    result = util.df_excel_range(df, "R21:T21")
    expected = pd.DataFrame([["Cubic foot (ft3)",7.48052,6.22884]])
    assert_data_equal(expected, result)

    result = util.df_excel_range(df, "S21:S21")
    expected = pd.DataFrame([[7.48052]])
    assert_data_equal(expected, result)

    # merged cell value registers on the first cell of the merged area
    result = util.df_excel_range(df, "C177:E178")
    assert result.iloc[0,1].startswith("Costs are sometimes presented per cow")
    assert np.isnan(result.iloc[0,2])
    assert np.isnan(result.iloc[1,1])

def test_find_in_column():
    assert 48 == util.find_in_column(ws, util.co("D"), "Link")
    assert 48 == util.find_in_column(ws, util.co("D"), "Link", start_row=48)
    assert 84 == util.find_in_column(ws, util.co("D"), "Link", start_row=49)
    assert util.find_in_column(ws, util.co("D"), "Xxxyzzy") is None

def test_find_in_row():
    assert util.co("L") == util.find_in_row(ws, 49, "million hectares")
    assert util.co("L") == util.find_in_row(ws, 49, "million hectares", start_col=util.co("L"))
    assert util.co("N") == util.find_in_row(ws, 49, "million hectares", start_col=util.co("M"))
    assert util.find_in_row(ws, 49, "Xxxyzzy") is None

def test_read_row():
    result = util.read_row(ws, 49, util.co("S"), util.co("V"))
    # Note this test uncovered some oddities in openpyxl behavior: cells which show as
    # #REF, #DIV, etc., in Excel, appear to return values from openpyxl.  Not clear where
    # those values are coming from.
    #expected = [450.0, None, "", "million hectares"]
    #assert expected == result
    assert 450.0 == pytest.approx(result[0])
    assert "million hectares" == result[3]

    result = util.read_row(ws, 70)
    assert ws.max_column == len(result)

def test_read_range():
    result = util.read_range(ws, 117, util.co("C"), 142, util.co("U"))
    assert 142-117+1 == len(result)
    assert util.co("U")-util.co("C") + 1 == len(result[0])
    assert result[0][14] is None
    assert 456.00 == pytest.approx(result[1][16])

# xls, xln and xli are extensively tested in practice by the extractor

def test_convert_bool():
    assert util.convert_bool("Yes")
    assert util.convert_bool(1)
    assert not util.convert_bool(0)
    assert not util.convert_bool("n")
    assert not util.convert_bool("0")
    assert not util.convert_bool(None, accept_empty=True)
    with pytest.raises(Exception):
        util.convert_bool("")
    with pytest.raises(Exception):
        util.convert_bool("No, not really.")


def test_to_filename():
    assert "foo.csv" == util.to_filename("foo")
    assert "foo_bar.txt" == util.to_filename("foo bar", suffix=".txt")
    assert "new_foo_bar_and_more.csv" == util.to_filename("foo bar (and more!)", prefix="new_")
    assert "More_mess_2021.csv" == util.to_filename(" More  -!-  mess -!-  2021!++")
    name = util.to_filename("a very long and wordy name indeed, with lots and lots of characters", maxlen=30)
    assert 30 == len(name)
    assert ".csv" == Path(name).suffix
    name = util.to_filename("another long and wordy name with too many characters", suffix=".longsuffix", prefix="longprefix_")
    assert 35 == len(name)
    assert ".longsuffix" == Path(name).suffix
    assert name.startswith("longprefix_")
    with pytest.raises(Exception):
        util.to_filename("A_boring_name", prefix="longprefix_", suffix=".longsuffix", maxlen=20)


def test_to_unique_filename():
    filenames = []
    newname = util.to_unique_filename("foo",filenames,suffix=".txt")
    assert "foo.txt" == newname
    filenames.append(newname)
    newname = util.to_unique_filename("Foo",filenames,suffix=".txt")
    assert "Foo_1.txt" == newname
    filenames.append(Path(".")/newname)
    newname = util.to_unique_filename("FOO",filenames,suffix=".txt")
    assert "FOO_2.txt" == newname
    filenames.append(newname)

    newname = util.to_unique_filename("bar",filenames)
    assert "bar.csv" == newname
    filenames.append(newname)
    newname = util.to_unique_filename("bar",filenames,suffix=".notcsv")
    assert "bar.notcsv" == newname
    newname = util.to_unique_filename("bar",filenames,prefix="unique_")
    assert "unique_bar.csv" == newname

