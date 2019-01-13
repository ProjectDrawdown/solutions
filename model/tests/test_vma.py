"""Tests for vma.py."""

import io
import pathlib
from model import vma
import pandas as pd
import pytest

parentdir = pathlib.Path(__file__).parents[2]

def test_basics():
  # values from SolarPVUtil 'Variable Meta-analysis'!C891:O893
  s = """Source ID, Raw Data Input, Original Units, Weight
        From "Coal Plant Efficiency" variable, 37.1577551412647%, %, 0.386991480510726
        From "Natural Gas Plant Efficiency variable, 48.2936717783726%, %, 0.218774807856912
        From "Oil Plant Efficiency variable", 39%, %, 0.047364989821849
        """
  f = io.StringIO(s)
  v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
  result = v.avg_high_low()
  expected = (0.41021474451, 0.47368454143, 0.34674494760)
  assert result == pytest.approx(expected)
  f = io.StringIO(s)
  v = vma.VMA(filename=f, low_sd=2.0, high_sd=3.0)
  result = v.avg_high_low()
  expected = (0.41021474451, 0.60062413527, 0.28327515067)
  assert result == pytest.approx(expected)

def test_source_data():
  s = """Source ID, Raw Data Input, Original Units, Weight
        Check that this text is present, 0%, %, 0
        """
  f = io.StringIO(s)
  v = vma.VMA(filename=f)
  assert "Check that this text is present" in v.source_data.to_html()

def test_invalid_discards():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
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

def test_conversion_inflation():
  v = vma.VMA(filename=str(parentdir.joinpath(
    'model', 'tests', 'vma_test_conversion_inflation.csv')))
  result = v.avg_high_low()
  expected = (2010.032, 3373.557, 646.507)
  assert result == pytest.approx(expected)

def test_conversion_co2eq():
  v = vma.VMA(filename=str(parentdir.joinpath(
    'model', 'tests', 'vma_test_conversion_co2eq.csv')))
  result = v.avg_high_low()
  expected = (47096.81818181820, 65382.64314055300, 28810.99322308340)
  assert result == pytest.approx(expected)

def test_conversion_btu():
  # values from SolarPVUtil 'Variable Meta-analysis' line 978
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 8251.6363640, Btu/kWh, 
      B, 8251636364.0, Btu/GWh, 
      B, 8251636364000.0, Btu/TWh, 
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (0.41351090614, 0.41351090614, 0.41351090614)
  assert result == pytest.approx(expected)

def test_conversion_unknown():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 1, unknown_conversion, 
      """)
  with pytest.raises(ValueError):
    _ = vma.VMA(filename=f)

def test_single_study():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 39%, %, 
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (0.39, 0.39, 0.39)
  assert result == pytest.approx(expected)

def test_conversion_years():
  s = """Source ID, Raw Data Input, Original Units, Weight
      A, 100, years, 
      """
  substitutions = {
      '@conv_avg_annual_use@': 2,
      '@soln_avg_annual_use@': 3,
      }
  f = io.StringIO(s)
  v = vma.VMA(filename=f, substitutions=substitutions, final_units='conv-TWh/TW')
  result = v.avg_high_low()
  expected = (200, 200, 200)
  assert result == pytest.approx(expected)
  f = io.StringIO(s)
  v = vma.VMA(filename=f, substitutions=substitutions, final_units='soln-TWh/TW')
  result = v.avg_high_low()
  expected = (300, 300, 300)
  assert result == pytest.approx(expected)

def test_conversion_kWhkW():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 1000, kWh/kW, 
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (1000, 1000, 1000)
  assert result == pytest.approx(expected)

def test_conversion_capacity_factor():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 50%, Capacity factor (%), 
      B, 0.50, cAPACITY factor (%), 
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (4380, 4380, 4380)
  assert result == pytest.approx(expected)

def test_conversion_usd_to_dollar_sign():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 100, usd2014/kw, 
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (100, 100, 100)
  assert result == pytest.approx(expected)

def test_substitution():
  substitutions = {
      '@energy_mix_coal@': 0.38699149767,
      '@energy_mix_natural_gas@': 0.21877481756,
      '@energy_mix_oil@': 0.04736499192,
      }
  v = vma.VMA(filename=str(parentdir.joinpath('model', 'tests', 'vma_test_substitution.csv')),
      substitutions=substitutions)
  result = v.avg_high_low()
  expected = (0.41021474451, 0.47368454143, 0.34674494760)
  assert result == pytest.approx(expected)

def test_final_units():
  substitutions = {
      '@soln_avg_annual_use@': 1841.66857142857,
      }
  s = """Source ID, Raw Data Input, Original Units, Weight
      A, 0.0078, US$2004/kWh, 
      B, 9.75, US$2014/MWh, 
      C, 7.3625585324, €2012/MWh, 
      """
  f = io.StringIO(s)
  v = vma.VMA(filename=f, substitutions=substitutions, final_units='US$2014/kW')
  result = v.avg_high_low()
  expected = (17.956268571425, 17.956268571425, 17.956268571425)
  assert result == pytest.approx(expected)
  f = io.StringIO(s)
  v = vma.VMA(filename=f, substitutions=substitutions, final_units='US$2014/kWh')
  result = v.avg_high_low()
  expected = (0.00975, 0.00975, 0.00975)
  assert result == pytest.approx(expected)

def test_extra_columns():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight, Extra1, Extra2, Extra3
      A, 1000, , , extra1, extra2, extra3
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (1000, 1000, 1000)
  assert result == pytest.approx(expected)

def test_missing_columns():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 1000
      """)
  v = vma.VMA(filename=f)
  result = v.avg_high_low()
  expected = (1000, 1000, 1000)
  assert result == pytest.approx(expected)

def test_inverse():
  f = io.StringIO("""Source ID, Raw Data Input, Original Units, Weight
      A, 43%, %, 
      """)
  postprocess = lambda x, y, z: (1.0 - x, 1.0 - y, 1.0 - z)
  v = vma.VMA(filename=f, postprocess=postprocess)
  result = v.avg_high_low()
  expected = (0.57, 0.57, 0.57)
  assert result == pytest.approx(expected)
