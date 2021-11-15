from pathlib import Path
import pandas as pd
import tools.vma_xls_extract as vxe
import openpyxl
import pytest

thisdir = Path(__file__).parent
wb = openpyxl.load_workbook(thisdir/'silvopasture_vma.xlsx', data_only=True, keep_links=False)
ws = vxe.get_vma_sheet(wb)
vma_data = vxe.extract_vmas(ws)

wb_errors = openpyxl.load_workbook(thisdir/'silvo_error_vma.xlsx',data_only=True, keep_links=False)
ws_errors = vxe.get_vma_sheet(wb_errors)

def find_vma_by_name(d, name):
    for dd in d:
        if dd['name'] == name:
            return dd
    else:
        return None


def test_extract_vmas_right_count():
    """ Check we produce the right number of tables, discarding empty ones"""
    assert len(vma_data) == 11

def test_read_xls():
    """ Check some specifc values from Silvopasture """
    assert find_vma_by_name(vma_data, 'SOLUTION Net Profit Margin per Functional Unit per Annum') is not None
    assert find_vma_by_name(vma_data, 'Sequestration Rates') is not None
    assert find_vma_by_name(vma_data, 'Total Energy Used per SOLUTION functional unit') is None

def test_vma_table_data():
    sr = find_vma_by_name(vma_data, 'Sequestration Rates')
    df = sr['data']
    assert len(df) == 28  # there are 28 rows of data
    assert len(df.columns) == len(vxe.STANDARD_COLUMNS)
    assert df['Exclude Data?'].sum() == 6  # there are six excluded rows
    assert pd.api.types.is_integer_dtype(df['Year / Date'])   # we converted years to ints successfully

def test_vma_table_info():
    ycp = find_vma_by_name(vma_data, 'Yield from CONVENTIONAL Practice')
    assert ycp['use_weight']
    assert not ycp['bound_correction']
    assert ycp['description'].startswith('The SOLAW Report')
    assert ycp['units'] == 'DM tons fodder/ha/yr'

    cnp = find_vma_by_name(vma_data, 'CONVENTIONAL Net Profit Margin per Functional Unit per Annum')
    assert not cnp['use_weight']
    assert cnp['bound_correction']
    assert cnp['description'].startswith("Costs are sometimes presented per cow")
    assert cnp['units'] == 'US$2014/ ha/ yr'

def test_normalize_col_name():
    assert vxe.normalize_col_name('Conedition calculation') == 'Conversion calculation'
    assert vxe.normalize_col_name('Manually Exclude Data?') == 'Exclude Data?'
    assert vxe.normalize_col_name('Weight by: Production') == 'Weight'


def test_error_handling():
    # wrong column start == nothing found
    with pytest.raises(ValueError, match=r"Unable to find any VMA tables on Excel page \[Variable Meta-analysis\]"):
        vxe.extract_vmas(ws_errors, start_column=1)
    
    with pytest.raises(ValueError, match=r"Unable to find 'Exclude Data\?' column of VMA table at 49 .*"):
        vxe.extract_vmas(ws_errors)

    # Note: _does_ match "Manually Exclude" column in VMA at 85.
    
    with pytest.raises(ValueError, match=r"Unable to find end of VMA table at 817 .*"):
        vxe.extract_vmas(ws_errors, start_row=80)

    with pytest.raises(ValueError, match=r"VMA table at 85 missing column\(s\) 'Source Validation Code' .*"):
        vxe.extract_vmas(ws_errors, start_row=80, end_row=816)

    with pytest.raises(ValueError, match=r"Unable to locate 'Use Weight\?' of VMA at 156 .*"):
        vxe.extract_vmas(ws_errors, start_row=115, end_row=816)
    
    with pytest.raises(ValueError, match=r"Unable to locate 'Low Correction\?' of VMA at 228 .*"):
        vxe.extract_vmas(ws_errors, start_row=158, end_row=816)

    with pytest.raises(ValueError, match=r"Unable to find name of VMA at 512 .*"):
        vxe.extract_vmas(ws_errors, start_row=263, end_row=816)

    # check on a few variations that _do_ work
    loc = (118, 3, 138, 20)
    info = vxe.get_vma_table_info(ws_errors, *loc)
    assert 'description' not in info  # but no error occurred
    assert info['bound_correction'] # even though we moved it
    df = vxe.get_vma_table_data(ws_errors, *loc)
    assert 'We don\'t care' not in df.columns # and no error occurred
    assert df['Assumptions'][0] == '(" US$400/ha for planting trees at high density in pastures")' # even tho we moved it
