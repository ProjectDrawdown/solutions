"""Tests for vma.py."""

import io
import pathlib
from model import vma
import pandas as pd
import pytest

parentdir = pathlib.Path(__file__).parents[2]

def test_AvgHighLow():
  # values from SolarPVUtil 'Variable Meta-analysis'!C891:O893
  s = """Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
        From "Coal Plant Efficiency" variable, , World, , , Various, , 37.1577551412647%, %, 0.386991480510726
        From "Natural Gas Plant Efficiency variable, , World, , , Various, , 48.2936717783726%, %, 0.218774807856912
        From "Oil Plant Efficiency variable", , OECD90, Japan, , 2005, , 39%, %, 0.047364989821849
        """
  f = io.StringIO(s)
  ahlvma = vma.AvgHighLow(filename=f, low_sd=1.0, high_sd=1.0, use_weight=True)
  result = ahlvma.avg_high_low()
  expected = (0.41021474451, 0.47368454143, 0.34674494760)
  assert result == pytest.approx(expected)
  f = io.StringIO(s)
  ahlvma = vma.AvgHighLow(filename=f, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (0.41483808973, 0.46357489314, 0.36610128632)
  assert result == pytest.approx(expected)
  f = io.StringIO(s)
  ahlvma = vma.AvgHighLow(filename=f, low_sd=2.0, high_sd=3.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (0.41483808973, 0.56104849996, 0.31736448291)
  assert result == pytest.approx(expected)

def test_AvgHighLow_invalid_discards():
  f = io.StringIO("""Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
        a, , , , , , , 10000, , 
        b, , , , , , , 10000, , 
        c, , , , , , , 10000, , 
        d, , , , , , , 10000, , 
        e, , , , , , , 10000, , 
        f, , , , , , , 10000, , 
        g, , , , , , , 10000, , 
        h, , , , , , , 10000, , 
        i, , , , , , , 10000, , 
        j, , , , , , , 10000, , 
        k, , , , , , , 10000, , 
        l, , , , , , , 10000, , 
        m, , , , , , , 10000, , 
        n, , , , , , , 10000, , 
        o, , , , , , , 10000, , 
        p, , , , , , , 10000000000, , 
        q, , , , , , , 1, , 
    """)
  ahlvma = vma.AvgHighLow(filename=f, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (10000, 10000, 10000)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_inflation():
  ahlvma = vma.AvgHighLow(filename=str(parentdir.joinpath(
    'model', 'tests', 'vma_test_conversion_inflation.csv')))
  result = ahlvma.avg_high_low()
  expected = (2010.032, 3373.557, 646.507)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_co2eq():
  ahlvma = vma.AvgHighLow(filename=str(parentdir.joinpath(
    'model', 'tests', 'vma_test_conversion_co2eq.csv')))
  result = ahlvma.avg_high_low()
  expected = (47096.81818181820, 65382.64314055300, 28810.99322308340)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_btu():
  # values from SolarPVUtil 'Variable Meta-analysis' line 978
  f = io.StringIO("""Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
      A, , , , , , , 8251.6363640, Btu/kWh, 
      B, , , , , , , 8251636364.0, Btu/GWh, 
      B, , , , , , , 8251636364000.0, Btu/TWh, 
      """)
  ahlvma = vma.AvgHighLow(filename=f)
  result = ahlvma.avg_high_low()
  expected = (0.41351090614, 0.41351090614, 0.41351090614)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_unknown():
  f = io.StringIO("""Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
      A, , , , , , , 1, unknown_conversion, 
      """)
  with pytest.raises(ValueError):
    _ = vma.AvgHighLow(filename=f)

def test_AvgHighLow_single_study():
  f = io.StringIO("""Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
      A, , , , , , , 39%, %, 
      """)
  ahlvma = vma.AvgHighLow(filename=f)
  result = ahlvma.avg_high_low()
  expected = (0.39, 0.39, 0.39)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_years():
  f = io.StringIO("""Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
      A, , , , , , , 100, years, 
      """)
  ahlvma = vma.AvgHighLow(filename=f)
  result = ahlvma.avg_high_low()
  expected = (100, 100, 100)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_kWhkW():
  f = io.StringIO("""Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
      A, , , , , , , 1000, kWh/kW, 
      """)
  ahlvma = vma.AvgHighLow(filename=f)
  result = ahlvma.avg_high_low()
  expected = (1000, 1000, 1000)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_capacity_factor():
  f = io.StringIO("""Source ID, Link, Region, Specific Geographic Location, Source Validation Code, Year, License Code, Raw Data Input, Original Units, Weight
      A, , , , , , , 50%, Capacity factor (%), 
      B, , , , , , , 0.50, cAPACITY factor (%), 
      """)
  ahlvma = vma.AvgHighLow(filename=f)
  result = ahlvma.avg_high_low()
  expected = (4380, 4380, 4380)
  assert result == pytest.approx(expected)
