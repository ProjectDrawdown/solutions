"""Tests for vma.py."""

from model import vma
import pandas as pd
import pytest

def test_AvgHighLow():
  # values from SolarPVUtil 'Variable Meta-analysis'!C891:O893
  df = pd.DataFrame([
      ['From "Coal Plant Efficiency" variable', '', 'World', '', '', 'Various', '',
        '37.1577551412647%', '%', 8726/22548.30],
      ['From "Natural Gas Plant Efficiency variable', '', 'World', '', '', 'Various', '',
        '48.2936717783726%', '%', 4933/22548.30],
      ['From "Oil Plant Efficiency variable"', '', 'OECD90', 'Japan', '', 2005, '',
        '39%', '%', 1068/22548.30],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=True)
  result = ahlvma.avg_high_low()
  expected = (0.41021474451, 0.47368454143, 0.34674494760)
  assert result == pytest.approx(expected)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (0.41483808973, 0.46357489314, 0.36610128632)
  assert result == pytest.approx(expected)

def test_AvgHighLow_invalid_discards():
  df = pd.DataFrame([
      ["a", "", "", "", "", "", "", 10000, "", ""],
      ["b", "", "", "", "", "", "", 10000, "", ""],
      ["c", "", "", "", "", "", "", 10000, "", ""],
      ["d", "", "", "", "", "", "", 10000, "", ""],
      ["e", "", "", "", "", "", "", 10000, "", ""],
      ["f", "", "", "", "", "", "", 10000, "", ""],
      ["g", "", "", "", "", "", "", 10000, "", ""],
      ["h", "", "", "", "", "", "", 10000, "", ""],
      ["i", "", "", "", "", "", "", 10000, "", ""],
      ["j", "", "", "", "", "", "", 10000, "", ""],
      ["k", "", "", "", "", "", "", 10000, "", ""],
      ["l", "", "", "", "", "", "", 10000, "", ""],
      ["m", "", "", "", "", "", "", 10000, "", ""],
      ["n", "", "", "", "", "", "", 10000, "", ""],
      ["o", "", "", "", "", "", "", 10000, "", ""],
      ["p", "", "", "", "", "", "", 10000000000, "", ""],
      ["q", "", "", "", "", "", "", 1, "", ""],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (10000, 10000, 10000)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_inflation():
  # values from SolarPVUtil 'Variable Meta-analysis'!C85:O106
  df = pd.DataFrame([
      ["A", "", "", "", "", "", "", 380, "US$2010/kW", "0.38699149767%"],
      ["B", "", "", "", "", "", "", 3900, "US$2010/kW", "0.38699149767%"],
      ["C", "", "", "", "", "", "", 550, "US$2010/kW", "0.21877481756%"],
      ["D", "", "", "", "", "", "", 2100, "US$2010/kW", "0.21877481756%"],
      ["E", "", "", "", "", "", "", 3000, "US$2016/kW", "0.38699149767%"],
      ["F", "", "", "", "", "", "", 1000, "US$2016/kW", "0.21877481756%"],
      ["G", "", "", "", "", "", "", 1300, "US$2016/kW", "0.21877481756%"],
      ["H", "", "", "", "", "", "", 500, "US$2016/kW", "0.04736499192%"],
      ["I", "", "", "", "", "", "", 800, "US$2016/kW", "0.04736499192%"],
      ["J", "", "", "", "", "", "", 461, "uS$2010/Kw", "0.04736499192%"],
      ["K", "", "", "", "", "", "", 700000, "€2012/MW", "0.21877481756%"],
      ["L", "", "", "", "", "", "", 1400000, "€2012/MW", "0.38699149767%"],
      ["M", "", "", "", "", "", "", 700000, "€2012/MW", "0.04736499192%"],
      ["N", "", "", "", "", "", "", 750000, "€2012/mw", "0.04736499192%"],
      ["O", "", "", "", "", "", "", 627, "us$2015/kw", "0.21877481756%"],
      ["P", "", "", "", "", "", "", 1289, "US$2015/kW", "0.21877481756%"],
      ["Q", "", "", "", "", "", "", 813, "US$2015/kW", "0.38699149767%"],
      ["R", "", "", "", "", "", "", 3067, "US$2015/kW", "0.38699149767%"],
      ["S", "", "", "", "", "", "", 917, "US$2012/kW", "0.21877481756%"],
      ["T", "", "", "", "", "", "", 4440, "US$2012/kW", "0.38699149767%"],
      ["U", "", "", "", "", "", "", 2040, "€2011/kW", "0.38699149767%"],
      ["V", "", "", "", "", "", "", 1350, "€2011/kW", "0.21877481756%"],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=True)
  result = ahlvma.avg_high_low()
  expected = (2010.032, 3373.557, 646.507)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_co2eq():
  # values from SolarPVUtil 'Variable Meta-analysis'!C744:O766
  df = pd.DataFrame([
      #["A", "", "", "", "", "", "", 41.00, 'g-CO2eq/kWh', ""],
      ["B", "", "", "", "", "", "", 60.00, 'g-CO2eq/kWh', ""],
      ["C", "", "", "", "", "", "", 26.00, 'g-CO2eq/kWh', ""],
      ["D", "", "", "", "", "", "", 0.02, 'kg-CO2eq/kWh', ""],
      ["E", "", "", "", "", "", "", 0.081, 'kg-CO2eq/kWh', ""],
      ["F", "", "", "", "", "", "", 31, 'g-CO2eq/kWh', ""],
      ["G", "", "", "", "", "", "", 27, 'g-CO2eq/kWh', ""],
      ["H", "", "", "", "", "", "", 57, 'g-CO2eq/kWh', ""],
      ["I", "", "", "", "", "", "", 38, 'g-CO2eq/kWh', ""],
      ["J", "", "", "", "", "", "", 26, 'g-CO2eq/kWh', ""],
      ["K", "", "", "", "", "", "", 19.5, 'g-CO2eq/kWh', ""],
      ["L", "", "", "", "", "", "", 66.5, 'g-CO2eq/kWh', ""],
      ["M", "", "", "", "", "", "", 66, 'g-CO2eq/kWh', ""],
      ["N", "", "", "", "", "", "", 61, 'g-CO2eq/kWh', ""],
      ["O", "", "", "", "", "", "", 58.8, 'g-CO2eq/kWh', ""],
      ["P", "", "", "", "", "", "", 33, 'g-CO2eq/kWh', ""],
      ["Q", "", "", "", "", "", "", 69, 'g-CO2eq/kWh', ""],
      ["R", "", "", "", "", "", "", 37, 'g-CO2eq/kWh', ""],
      ["S", "", "", "", "", "", "", 65.2, 'g-CO2eq/kWh', ""],
      ["T", "", "", "", "", "", "", 30, 'g-CO2eq/kWh', ""],
      ["U", "", "", "", "", "", "", 60, 'g-CO2eq/kWh', ""],
      ["V", "", "", "", "", "", "", 44, 'g-CO2eq/kWh', ""],
      ["W", "", "", "", "", "", "", 60.13, 'g-CO2eq/kWh', ""],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (47096.81818181820, 65382.64314055300, 28810.99322308340)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_btu():
  # values from SolarPVUtil 'Variable Meta-analysis' line 978
  df = pd.DataFrame([
      ["A", "", "", "", "", "", "", 8251.6363640, 'Btu/kWh', ""],
      ["B", "", "", "", "", "", "", 8251636364.0, 'Btu/GWh', ""],
      ["B", "", "", "", "", "", "", 8251636364000.0, 'Btu/TWh', ""],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (0.41351090614, 0.41351090614, 0.41351090614)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_unknown():
  df = pd.DataFrame([["A", "", "", "", "", "", "", 1, "unknown_conversion", ""],
    ], columns=vma.columns)
  with pytest.raises(ValueError):
    _ = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)

def test_AvgHighLow_single_study():
  df = pd.DataFrame([["A", "", "", "", "", "", "", "39%", "%", ""],],
    columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (0.39, 0.39, 0.39)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_years():
  df = pd.DataFrame([["A", "", "", "", "", "", "", 100, 'years', ""],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (100, 100, 100)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_kWhkW():
  df = pd.DataFrame([["A", "", "", "", "", "", "", 1000, 'kWh/kW', ""],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (1000, 1000, 1000)
  assert result == pytest.approx(expected)

def test_AvgHighLow_conversion_capacity_factor():
  df = pd.DataFrame([
    ["A", "", "", "", "", "", "", '50%', 'Capacity factor (%)', ""],
    ["B", "", "", "", "", "", "", 0.50, 'cAPACITY factor (%)', ""],
    ], columns=vma.columns)
  ahlvma = vma.AvgHighLow(df, low_sd=1.0, high_sd=1.0, use_weight=False)
  result = ahlvma.avg_high_low()
  expected = (4380, 4380, 4380)
  assert result == pytest.approx(expected)
