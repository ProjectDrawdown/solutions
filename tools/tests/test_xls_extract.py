import pytest
from tools.xls_extract import cell_to_offsets


def test_cell_to_offsets():
    assert cell_to_offsets('A1') == (0, 0)
    assert cell_to_offsets('B10') == (9, 1)
    assert cell_to_offsets('AA1') == (0, 26)
    assert cell_to_offsets('BA1') == (0, 52)