"""Tests for vma.py."""

import io
import pathlib
from model import vma
import pytest

basedir = pathlib.Path(__file__).parents[2]
datadir = pathlib.Path(__file__).parents[0].joinpath('data')

def test_vals_from_real_soln():
  """ Values from Silvopasture Variable Meta Analysis """
  f = datadir.joinpath('vma1_silvopasture.csv')
  v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
  result = v.avg_high_low()
  expected = (314.15, 450.0, 178.3)
  assert result == pytest.approx(expected)

def test_source_data():
  s = """Source ID, Raw Data Input , Original Units, Conversion calculation**, Weight
        Check that this text is present, 0%, %, 0, 0
        """
  f = io.StringIO(s)
  v = vma.VMA(filename=f)
  assert 'Check that this text is present' in v.source_data.to_html()

def test_invalid_discards():
  f = io.StringIO("""Source ID, Raw Data Input , Original Units, Conversion calculation**, Weight
        a, 10000, , 
        b, 10000, , 
        c, 10000, , 
        d, 10000, , 
        e, 10000, , 
        f, 10000, , 
        g, 10000, , 
        h, 10000, , 
        i, 10000, , 
        j, 10000, , 
        k, 10000, , 
        l, 10000, , 
        m, 10000, , 
        n, 10000, , 
        o, 10000, , 
        p, 10000000000, , 
        q, 1, , 
    """)
  v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
  result = v.avg_high_low()
  expected = (10000, 10000, 10000)  # The 10,000,000,000 and 1 values should be discarded.
  assert result == pytest.approx(expected)

def test_single_study():
  f = io.StringIO("""Source ID, Raw Data Input , Original Units, Conversion calculation**, Weight
      A, 39%, %, 
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (0.39, 0.39, 0.39)
  assert result == pytest.approx(expected)

def test_missing_columns():
  f = io.StringIO("""Source ID, Raw Data Input , Original Units, Conversion calculation**, Weight
      A, 1000
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (1000, 1000, 1000)
  assert result == pytest.approx(expected)

def test_inverse():
  f = io.StringIO("""Source ID, Raw Data Input , Original Units, Conversion calculation**, Weight
      A, 43%, %, 
      """)
  postprocess = lambda x, y, z: (1.0 - x, 1.0 - y, 1.0 - z)
  v = vma.VMA(filename=f, postprocess=postprocess)
  result = v.avg_high_low()
  expected = (0.57, 0.57, 0.57)
  assert result == pytest.approx(expected)
