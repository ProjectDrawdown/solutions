import pytest
import pathlib
import pandas as pd
from tools.custom_adoption_xls_extract import CustomAdoptionReader

thisdir = pathlib.Path(__file__).parents[0]


def test_single_table():
    ca_r = CustomAdoptionReader(thisdir.joinpath('silvopasture_custom_pds_adoption.xlsx'), 'pds')
    result = ca_r.read_single_scenario('A77')
    expected = pd.read_csv(thisdir.joinpath('silvopasture_scen1.csv'), index_col=0)
    pd.testing.assert_frame_equal(result, expected)


def test_find_table():
    ca_r = CustomAdoptionReader(thisdir.joinpath('silvopasture_custom_pds_adoption.xlsx'), 'pds')
    ca_r._find_tables()
    assert len(ca_r.table_locations) == 6
    assert list(ca_r.table_locations.keys())[
               -1] == 'High growth, linear trend (based on improved pasture area)'


def test_read_xls():
    ca_r = CustomAdoptionReader(thisdir.joinpath('silvopasture_custom_pds_adoption.xlsx'), 'pds')
    d = ca_r.read_xls()
    # Check a few values from Silvopasture
    assert d[list(d.keys())[1]].at[2027, 'World'] == pytest.approx(460.978967144144)
    assert d[list(d.keys())[4]]['Eastern Europe'].isna().all()
