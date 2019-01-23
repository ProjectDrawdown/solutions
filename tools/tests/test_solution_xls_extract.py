"""Tests for solution_xls_extract.py"""

import pytest
from tools import solution_xls_extract as sx

def test_convert_sr_float():
  s = "Val:(0.182810601365724) Formula:='Variable Meta-analysis'!G1411"
  assert sx.convert_sr_float(s) == pytest.approx(0.182810601365724)
  assert sx.convert_sr_float('0.1987') == pytest.approx(0.1987)
  assert sx.convert_sr_float('') == pytest.approx(0.0)
  assert sx.convert_sr_float('12') == pytest.approx(12.0)
