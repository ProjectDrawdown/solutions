from pathlib import Path
import pandas as pd
import tools.vma_xls_extract as vxe
import openpyxl

thisdir = Path(__file__).parent
wb = openpyxl.load_workbook(thisdir/'silvopasture_vma.xlsx', data_only=True, keep_links=False)
ws = wb[vxe.get_vma_sheet(wb)]
vma_data = vxe.extract_vmas(ws)

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

