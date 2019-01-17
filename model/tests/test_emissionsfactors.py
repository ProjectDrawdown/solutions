"""Tests for emissionsfactors.py."""

from model import advanced_controls
from model import emissionsfactors as ef
import pandas as pd
import pytest

def test_CO2Equiv():
  c = ef.CO2Equiv(ef.CO2EQ_SOURCE.AR5_WITH_FEEDBACK)
  assert c.CH4multiplier == 34
  assert c.N2Omultiplier == 298
  c = ef.CO2Equiv(ef.CO2EQ_SOURCE.AR4)
  assert c.CH4multiplier == 25
  assert c.N2Omultiplier == 298
  c = ef.CO2Equiv(ef.CO2EQ_SOURCE.SAR)
  assert c.CH4multiplier == 21
  assert c.N2Omultiplier == 310

def test_string_to_conversion_source():
  assert ef.string_to_conversion_source("AR5 with feedback") == ef.CO2EQ_SOURCE.AR5_WITH_FEEDBACK
  assert ef.string_to_conversion_source("AR4") == ef.CO2EQ_SOURCE.AR4
  assert ef.string_to_conversion_source("Ar4") == ef.CO2EQ_SOURCE.AR4
  assert ef.string_to_conversion_source("SAR") == ef.CO2EQ_SOURCE.SAR
  assert ef.string_to_conversion_source("sar") == ef.CO2EQ_SOURCE.SAR
  with pytest.raises(ValueError):
    ef.string_to_conversion_source("invalid")

def test_string_to_emissions_grid_source():
  assert ef.string_to_emissions_grid_source("meta-analysis") == ef.GRID_SOURCE.META
  assert ef.string_to_emissions_grid_source("MeTa_AnAlYsIs") == ef.GRID_SOURCE.META
  assert ef.string_to_emissions_grid_source("META ANALYSIS") == ef.GRID_SOURCE.META
  assert ef.string_to_emissions_grid_source("IPCC_ONLY") == ef.GRID_SOURCE.IPCC
  assert ef.string_to_emissions_grid_source("ipcc only") == ef.GRID_SOURCE.IPCC
  with pytest.raises(ValueError):
    ef.string_to_conversion_source("invalid")

def test_string_to_emissions_grid_range():
  assert ef.string_to_emissions_grid_range("MEAN") == ef.GRID_RANGE.MEAN
  assert ef.string_to_emissions_grid_range("MEan") == ef.GRID_RANGE.MEAN
  assert ef.string_to_emissions_grid_range("Median") == ef.GRID_RANGE.MEAN
  assert ef.string_to_emissions_grid_range("high") == ef.GRID_RANGE.HIGH
  assert ef.string_to_emissions_grid_range("LOW") == ef.GRID_RANGE.LOW
  with pytest.raises(ValueError):
    ef.string_to_conversion_source("invalid")

def test_ElectricityGenOnGrid_conv_ref_grid_CO2eq_per_KWh():
  ac = advanced_controls.AdvancedControls(emissions_grid_source="ipcc_only", emissions_grid_range="mean")
  eg = ef.ElectricityGenOnGrid(ac=ac)
  table = eg.conv_ref_grid_CO2eq_per_KWh()
  assert table.loc[2025, "OECD90"] == pytest.approx(0.454068989)
  assert table.loc[2020, 'World'] == pytest.approx(0.483415642)
  ac.emissions_grid_range = ef.GRID_RANGE.LOW
  eg = ef.ElectricityGenOnGrid(ac=ac)
  table = eg.conv_ref_grid_CO2eq_per_KWh()
  assert table.loc[2020, 'World'] == pytest.approx(0.416520905)
  ac.emissions_grid_range = ef.GRID_RANGE.HIGH
  eg = ef.ElectricityGenOnGrid(ac=ac)
  table = eg.conv_ref_grid_CO2eq_per_KWh()
  assert table.loc[2020, 'World'] == pytest.approx(0.952177536)
  ac.emissions_grid_source = ef.GRID_SOURCE.META
  ac.emissions_grid_range = ef.GRID_RANGE.MEAN
  eg = ef.ElectricityGenOnGrid(ac=ac)
  table = eg.conv_ref_grid_CO2eq_per_KWh()
  assert table.loc[2020, 'World'] == pytest.approx(0.581083120)
  ac.emissions_grid_range = ef.GRID_RANGE.LOW
  eg = ef.ElectricityGenOnGrid(ac=ac)
  table = eg.conv_ref_grid_CO2eq_per_KWh()
  assert table.loc[2020, 'World'] == pytest.approx(0.446005409)
  ac.emissions_grid_range = ef.GRID_RANGE.HIGH
  eg = ef.ElectricityGenOnGrid(ac=ac)
  table = eg.conv_ref_grid_CO2eq_per_KWh()
  assert table.loc[2020, 'World'] == pytest.approx(0.726403172)

def test_conv_ref_grid_CO2_per_KWh():
  eg = ef.ElectricityGenOnGrid(ac=None)
  table = eg.conv_ref_grid_CO2_per_KWh()
  assert table.loc[2025, "World"] == pytest.approx(0.484512031)
  assert table.loc[2032, "OECD90"] == pytest.approx(0.392126590)
  assert table.loc[2046, "Eastern Europe"] == pytest.approx(0.659977317)
  assert table.loc[2060, "Asia (Sans Japan)"] == pytest.approx(0.385555834)
  assert table.loc[2016, "Middle East and Africa"] == pytest.approx(0.185499981)
  assert table.loc[2027, "Latin America"] == pytest.approx(0.491537631)
  assert table.loc[2034, "China"] == pytest.approx(0.474730313)
  assert table.loc[2041, "India"] == pytest.approx(0.725081980)
  assert table.loc[2020, "EU"] == pytest.approx(0.297016531)
  assert table.loc[2039, "USA"] == pytest.approx(0.594563067)

def test_to_dict():
  ac = advanced_controls.AdvancedControls(emissions_grid_source="ipcc_only",
      emissions_grid_range="mean")
  eg = ef.ElectricityGenOnGrid(ac=ac)
  result = eg.to_dict()
  expected = ['conv_ref_grid_CO2eq_per_KWh', 'conv_ref_grid_CO2_per_KWh']
  for ex in expected:
    assert ex in result
    f = getattr(eg, ex, None)
    if f:
      check = f()
      if isinstance(check, pd.DataFrame):
        pd.testing.assert_frame_equal(result[ex], check, check_exact=False)
      elif isinstance(check, pd.Series):
        pd.testing.assert_series_equal(result[ex], check, check_exact=False)
      else:
        assert result[ex] == pytest.approx(check)
